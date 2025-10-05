"""Command-line helper to compose Doppler ultrasound reports quickly."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

TEMPLATE_PATH = Path(__file__).with_name("templates.json")


def load_templates(path: Path = TEMPLATE_PATH) -> Dict[str, dict]:
    """Load JSON templates file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("templates", {})


def list_templates(templates: Dict[str, dict]) -> List[Tuple[str, str]]:
    """Return template id and title."""
    return [(key, value.get("title", "")) for key, value in templates.items()]


def build_report(
    template: dict,
    overrides: Dict[str, str],
    header: Dict[str, str],
) -> str:
    """Build the full textual report."""
    lines: List[str] = []
    metadata = template.get("metadata", {})

    title = template.get("title")
    if title:
        lines.append(title.upper())
        lines.append("=" * len(title))
        lines.append("")

    if header:
        header_lines = [f"{key}: {value}" for key, value in header.items() if value]
        if header_lines:
            lines.extend(header_lines)
            lines.append("")

    description = template.get("description")
    if description:
        lines.append(description.strip())
        lines.append("")

    examens = metadata.get("examens_cibles")
    if examens:
        lines.append("Segments explorés :")
        for segment in examens:
            lines.append(f"  - {segment}")
        lines.append("")

    for section in template.get("sections", []):
        name = section.get("name", "Section")
        default_text = section.get("default", "").strip()
        value = overrides.get(name.lower(), overrides.get(name, default_text))
        lines.append(name)
        lines.append("-" * len(name))
        lines.append(value.strip() if value else "")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def parse_override_arguments(values: Iterable[str]) -> Dict[str, str]:
    """Parse key=value pairs from CLI arguments."""
    parsed: Dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Invalid override '{item}'. Expected format section=value"
            )
        key, value = item.split("=", 1)
        parsed[key.strip().lower()] = value.strip()
    return parsed


def main(argv: Iterable[str] | None = None) -> str:
    parser = argparse.ArgumentParser(
        description=(
            "Compose rapidement des comptes-rendus d'échographie Doppler "
            "en partant de modèles éditables."
        )
    )

    subparsers = parser.add_subparsers(dest="command")

    parser_list = subparsers.add_parser("list", help="Afficher les modèles disponibles")

    parser_generate = subparsers.add_parser(
        "generate", help="Générer un compte-rendu à partir d'un modèle"
    )
    parser_generate.add_argument("template_id", help="Identifiant du modèle")
    parser_generate.add_argument(
        "--set",
        metavar="SECTION=TEXTE",
        dest="overrides",
        action="append",
        default=[],
        help=(
            "Remplacer le contenu d'une section. Le nom de la section peut être "
            "celui affiché ou en minuscules. Exemple: --set 'Conclusion=Pas de sténose.'"
        ),
    )
    parser_generate.add_argument(
        "--patient",
        help="Identité du patient à afficher dans l'en-tête",
    )
    parser_generate.add_argument(
        "--date",
        help="Date de l'examen (défaut: aujourd'hui)",
    )
    parser_generate.add_argument(
        "--medecin",
        help="Nom du médecin réalisant l'examen",
    )
    parser_generate.add_argument(
        "--structure",
        help="Nom de la structure ou cabinet",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    templates = load_templates()

    if args.command == "list":
        output_lines = ["Modèles disponibles :"]
        for key, title in list_templates(templates):
            output_lines.append(f"- {key}: {title}")
        result = "\n".join(output_lines)
        print(result)
        return result

    if args.command == "generate":
        template_id = args.template_id
        template = templates.get(template_id)
        if not template:
            available = ", ".join(templates.keys()) or "aucun modèle"
            raise SystemExit(
                f"Modèle '{template_id}' introuvable. Modèles disponibles: {available}."
            )

        overrides = parse_override_arguments(args.overrides)
        header = {
            "Patient": args.patient or "",
            "Date": args.date or dt.date.today().strftime("%d/%m/%Y"),
            "Médecin": args.medecin or "",
            "Structure": args.structure or "",
        }
        report = build_report(template, overrides=overrides, header=header)
        print(report)
        return report

    parser.print_help()
    return ""


if __name__ == "__main__":
    main()
