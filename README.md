# Assistant Doppler

Cet outil fournit une aide pour générer des comptes-rendus d'échographie Doppler en moins d'une minute à partir de modèles préremplis. Les modèles proposés couvrent les examens artériels et veineux les plus fréquents, mais ils peuvent être adaptés très facilement.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation rapide

Lister les modèles disponibles :

```bash
python -m doppler_reports.cli list
```

Générer un compte-rendu type pour un examen artériel des membres inférieurs, en personnalisant le patient et la conclusion :

```bash
python -m doppler_reports.cli generate arteres_membres_inferieurs \
  --patient "M. Dupont" \
  --medecin "Dr Martin" \
  --set "Conclusion=Sténose fémorale superficielle droite à 60% traitée par angioplastie le jour même."
```

Le texte est affiché directement dans le terminal et peut être copié-collé dans votre dossier patient ou un modèle Word. Chaque section peut être surchargée à l'aide de `--set`. Le nom de section peut être fourni tel qu'affiché (`"Conclusion"`) ou en minuscules (`"conclusion"`).

## Mode assisté (recommandé si vous n'êtes pas à l'aise avec l'informatique)

1. **Installer Python** :
   - Rendez-vous sur [python.org/downloads](https://www.python.org/downloads/) et téléchargez la dernière version stable (cochez « Add python.exe to PATH » lors de l'installation sous Windows).
2. **Télécharger le projet** : cliquez sur le bouton « Code » puis « Download ZIP » sur la page GitHub, puis décompressez l'archive dans un dossier facile à retrouver (par exemple `Documents/AssistantDoppler`).
3. **Ouvrir un terminal dans ce dossier** :
   - Sous **Windows** : dans l'explorateur, faites un clic droit dans le dossier vide tout en maintenant la touche `Shift`, puis choisissez « Ouvrir la fenêtre PowerShell ici ».
   - Sous **macOS** : ouvrez l'application Terminal puis tapez `cd `, glissez-déposez le dossier et appuyez sur Entrée.
4. **Créer l'environnement** (à faire la première fois uniquement) :

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Lancer l'assistant guidé** :

   ```bash
   python -m doppler_reports.cli assistant
   ```

   Le programme vous posera simplement des questions (type d'examen, nom du patient, conclusion…) et générera le compte-rendu prêt à copier/coller. Vous pouvez également enregistrer le texte dans un fichier `.txt` si vous le souhaitez.

## Personnalisation

Les modèles sont définis dans `doppler_reports/templates.json`. Chaque section comporte un texte par défaut que vous pouvez modifier pour intégrer vos tournures habituelles, des items à cocher ou des lignes vides à compléter. L'ajout d'un nouveau modèle se fait en dupliquant une entrée et en modifiant son contenu.

## Pourquoi cet outil ?

- **Rapidité** : partir d'une base solide pour saisir votre compte-rendu en quelques secondes.
- **Standardisation** : harmoniser les conclusions et sections clés pour toute l'équipe.
- **Traçabilité** : conserver des segments explorés et mesures hémodynamiques structurées.
