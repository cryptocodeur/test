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


def prompt(text: str) -> str:
    """Wrapper around input() to simplify testing/mocking if needed."""
    return input(text)


def run_interactive_assistant(templates: Dict[str, dict]) -> str:
    """Guide the user step-by-step to create a report without CLI knowledge."""
    if not templates:
        raise SystemExit("Aucun modèle disponible dans templates.json.")

    print(
        "Assistant de génération de compte-rendu\n"
        "---------------------------------------\n"
        "Ce mode vous guide pas à pas. Appuyez sur Entrée pour accepter les propositions.\n"
    )

    ordered_templates = list(templates.items())
    for idx, (key, template) in enumerate(ordered_templates, start=1):
        title = template.get("title", key)
        description = template.get("description")
        extra = f" — {description}" if description else ""
        print(f"{idx}. {title} ({key}){extra}")

    selected_template: dict | None = None
    template_key: str | None = None
    while selected_template is None:
        choice = prompt(
            "\nTapez le numéro du modèle souhaité ou son identifiant (ex: 1 ou veines_membres_inferieurs) : "
        ).strip()
        if not choice:
            print("Veuillez sélectionner un modèle.")
            continue

        # Accept numeric selection
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(ordered_templates):
                template_key, selected_template = ordered_templates[idx]
                break
            print("Numéro invalide, merci d'essayer à nouveau.")
            continue

        # Accept template identifier
        choice_lower = choice.lower()
        for key, template in ordered_templates:
            if key.lower() == choice_lower:
                template_key, selected_template = key, template
                break
        if selected_template is None:
            print("Identifiant de modèle inconnu, recommencez.")

    assert selected_template is not None and template_key is not None

    print(f"\nVous avez choisi : {selected_template.get('title', template_key)}\n")

    header = {
        "Patient": prompt("Nom du patient (laisser vide pour ne pas l'afficher) : ").strip(),
        "Date": prompt(
            "Date de l'examen (format JJ/MM/AAAA, Entrée pour aujourd'hui) : "
        ).strip()
        or dt.date.today().strftime("%d/%m/%Y"),
        "Médecin": prompt("Nom du médecin (Entrée pour laisser vide) : ").strip(),
        "Structure": prompt("Nom de la structure (Entrée pour laisser vide) : ").strip(),
    }

    overrides: Dict[str, str] = {}
    sections = selected_template.get("sections", [])
    if sections:
        print(
            "\nNous allons parcourir les sections du compte-rendu."
            " Appuyez sur Entrée pour conserver la proposition." 
        )
    for section in sections:
        name = section.get("name", "Section")
        default_text = section.get("default", "").strip()
        print("\n" + name)
        print("-" * len(name))
        if default_text:
            print(default_text)
        else:
            print("(aucun texte proposé)")
        answer = prompt(
            "Votre texte (ou Entrée pour conserver la proposition ci-dessus) : "
        ).strip()
        if answer:
            overrides[name.lower()] = answer

    report = build_report(selected_template, overrides=overrides, header=header)
    print("\nCompte-rendu généré :\n")
    print(report)

    save_choice = prompt("Enregistrer dans un fichier texte ? (o/N) : ").strip().lower()
    if save_choice == "o":
        default_filename = f"rapport_{template_key}_{dt.date.today().isoformat()}.txt"
        path_input = prompt(
            f"Nom du fichier (Entrée pour {default_filename}) : "
        ).strip()
        filename = path_input or default_filename
        output_path = Path(filename).expanduser()
        output_path.write_text(report, encoding="utf-8")
        print(f"Fichier enregistré dans {output_path.resolve()}")

    return report


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

    subparsers.add_parser(
        "assistant",
        help=(
            "Mode guidé interactif (idéal si vous n'êtes pas à l'aise avec la ligne de commande)"
        ),
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

    if args.command == "assistant":
        result = run_interactive_assistant(templates)
        return result

    parser.print_help()
    return ""


if __name__ == "__main__":
    main()
