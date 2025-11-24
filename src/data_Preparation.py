import pandas as pd 
import sqlite3 
import os 
#fonction de nettoyage des données
RAW_PATH= '../data/raw/bmw_data.csv'
CLEANED_PATH= '../data/processed/bmw_data_clean.csv'
#chemin de la bdd 
DB_PATH= './data/processed/bmw_sales.db'






def infer_category(model):
    """Infère la catégorie à partir du model (simple règle pour matcher le cahier)."""
    model = str(model).upper()
    if 'X' in model:
        return 'SUV'
    elif 'SERIES' in model:
        return 'Sedan'
    elif 'I' in model:
        return 'Electric'
    else:
        return 'Unknown'

def clean_dataset():
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(f"Fichier raw manquant : {RAW_PATH}. Téléchargez-le depuis Kaggle.")
    
    df = pd.read_csv(RAW_PATH)
    
    df.columns = df.columns.str.strip().str.lower()
    
    actual_cols = ['model', 'year', 'region', 'color', 'fuel_type', 'transmission', 'engine_size_l', 'mileage_km', 'price_usd', 'sales_volume', 'sales_classification']
    if not all(col in df.columns for col in actual_cols):
        raise ValueError("Colonnes inattendues dans le CSV. Vérifiez le dataset Kaggle. Colonnes trouvées : " + str(list(df.columns)))
    
    df = df.dropna(subset=['year', 'sales_volume'])  
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')  
    df['sales_volume'] = pd.to_numeric(df['sales_volume'].astype(str).str.replace(',', ''), errors='coerce').astype('Int64')
    df['mileage_km'] = pd.to_numeric(df['mileage_km'], errors='coerce').astype('Int64')
    df['price_usd'] = pd.to_numeric(df['price_usd'], errors='coerce').astype('Int64')
    df['engine_size_l'] = pd.to_numeric(df['engine_size_l'], errors='coerce')
    df['region'] = df['region'].str.strip().str.title()  
    df['model'] = df['model'].str.strip().str.upper()  
    df['color'] = df['color'].str.strip().str.title()
    df['transmission'] = df['transmission'].str.strip().str.title()
    df['sales_classification'] = df['sales_classification'].str.strip().str.title()
    df['fuel_type'] = df['fuel_type'].str.strip().str.capitalize()  
    
    df.fillna({'color': 'Unknown', 'transmission': 'Unknown', 'sales_classification': 'Unknown', 'engine_size_l': 0, 'mileage_km': 0, 'price_usd': 0}, inplace=True)
    
    powertrain_map = {
        'Petrol': 'GASOLINE',
        'Diesel': 'DIESEL',
        'Hybrid': 'PHEV',
        'Electric': 'BEV'
    }
    df['powertrain'] = df['fuel_type'].map(powertrain_map).fillna('UNKNOWN')
    
    df['country'] = 'Unknown'  
    df['category'] = df['model'].apply(infer_category)  
    
    df = df.rename(columns={'sales_volume': 'sales'})
    
    expected_cols = ['year', 'country', 'region', 'model', 'category', 'powertrain', 'sales']
    df = df[expected_cols]
    
    os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)
    df.to_csv(CLEANED_PATH, index=False)
    print(f"CSV nettoyé sauvegardé : {CLEANED_PATH} ({len(df)} lignes)")
    
    return df

def create_sqlite_db(df):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        year INTEGER,
        country TEXT,
        region TEXT,
        model TEXT,
        category TEXT,
        powertrain TEXT,
        sales INTEGER
    )
    ''')
    
    df.to_sql('sales', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    print(f"Base SQLite créée : {DB_PATH} (table 'sales')")

if __name__ == "__main__":
    df_cleaned = clean_dataset()
    create_sqlite_db(df_cleaned)