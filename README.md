# Self-BI BMW (Bayerische Motoren Werke)

Application Streamlit pour analyser les ventes BMW (dataset Kaggle) en langage naturel, avec un agent ReAct (Cohere) et un fallback Pandas. Ce README sert de manuel d’utilisation et peut être inclus dans une archive unique (ZIP/7Z/RAR) avec le code.

## Liens utiles
- Cohere modèles : https://docs.cohere.com/docs/models
- LangChain : https://python.langchain.com/
- Streamlit : https://streamlit.io/
- Kaleido (export Plotly) : https://github.com/plotly/Kaleido

## Prérequis
- Python 3.12+ recommandé
- Dataset brut présent : `data/raw/bareshemotorenwerke.csv`
- (Optionnel) Clé Cohere pour activer l’agent ReAct : `COHERE_API_KEY`

## Installation (avec venv)
```bash
python3 -m venv venv
source venv/bin/activate             # sous Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration (.env)
À créer à la racine du projet :
```
COHERE_API_KEY=your_cohere_api_key   # optionnel si vous n'utilisez que le fallback Pandas
COHERE_MODEL=command-r               # optionnel, valeur par défaut
```

## Préparation des données
Le CSV brut est déjà présent. Générer le CSV nettoyé et la base SQLite :
```bash
./venv/bin/python src/data_Preparation.py
```
Cela produit `data/processed/bmw_cleaned.csv` et `data/processed/bmw_sales.db`.

## Lancer l’application
```bash
./venv/bin/streamlit run app.py
```
Ouvrir l’URL affichée (par défaut http://localhost:8501).

## Usage rapide
1. Saisir une question en français ou anglais dans le champ de saisie.
2. L’agent ReAct (Cohere) répond ; en cas d’échec ou d’absence de clé, le fallback Pandas prend le relais.
3. Le graphique s’affiche ; l’export PNG/PDF est disponible si Kaleido est installé (fichiers générés depuis la figure en mémoire).

## Remarques
- Le dataset n’a pas de colonne pays, seulement la région ; les requêtes par pays sont mappées à la région correspondante (ex : “China” → “Asia”) avec un message explicatif.
- LangSmith est désactivé par défaut pour éviter les erreurs 401.
- Export : nécessite Kaleido (déjà dans `requirements.txt`). Le bouton de téléchargement apparaît dès qu’un graphique est présent.