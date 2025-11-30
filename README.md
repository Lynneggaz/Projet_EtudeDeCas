# Self-BI BMW (Bayerische Motoren Werke)

Application Streamlit pour interroger les ventes BMW (dataset Kaggle) en langage naturel avec un agent ReAct (Cohere) et un fallback Pandas.

## Prérequis
- Python 3.12+ recommandé
- Accès local au dataset déjà présent dans `data/raw/bareshemotorenwerke.csv`
- (Optionnel) Clé Cohere pour activer l’agent ReAct : `COHERE_API_KEY`

## Installation (avec venv)
```bash
python3 -m venv venv
source venv/bin/activate             # sous Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration
Créer un fichier `.env` à la racine avec, au minimum :
```
COHERE_API_KEY=your_cohere_api_key   # optionnel si vous n'utilisez que le fallback Pandas
COHERE_MODEL=command-r               # optionnel, valeur par défaut
```

## Préparation des données
Le CSV brut est déjà présent. Pour générer les fichiers nettoyés et la base SQLite :
```bash
./venv/bin/python src/data_Preparation.py
```
Cela crée `data/processed/bmw_cleaned.csv` et `data/processed/bmw_sales.db`.

## Lancer l’application
```bash
./venv/bin/streamlit run app.py
```
Ouvrir ensuite l’URL affichée (par défaut http://localhost:8501).

## Notes d’usage
- L’agent ReAct nécessite une clé Cohere. En cas d’échec ou d’absence de clé, le fallback Pandas s’active automatiquement.
- Les exports PNG/PDF utilisent Kaleido (déjà dans `requirements.txt`). Le fichier est généré dans `exports/`.
- Le dataset n’a pas de granularité par pays ; certaines questions “pays” sont mappées vers la région correspondante (ex: “China” → “Asia”) pour fournir un graphique.
