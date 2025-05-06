import pandas as pd
import os
import psycopg2
from sqlalchemy import create_engine, text
import time
from datetime import datetime

def load_data(df, customer_agg, product_agg, time_agg):
    """
    Fonction pour charger les données transformées dans une base de données PostgreSQL
    Les tables sont déjà créées par initdb.sql
    """
    if df is None or customer_agg is None or product_agg is None or time_agg is None:
        raise ValueError("Tous les DataFrames doivent être fournis pour le chargement")
    
    print("Début du chargement des données dans PostgreSQL...")
    
    # Paramètres de connexion à la base de données
    db_params = {
        'host': os.environ.get('DB_HOST', 'postgres'),
        'port': os.environ.get('DB_PORT', '5432'),
        'database': os.environ.get('DB_NAME', 'sales_db'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres')
    }
    
    # Attendre que PostgreSQL soit prêt
    max_retries = 10
    retry_interval = 5  # secondes
    
    for i in range(max_retries):
        try:
            # Tester la connexion
            conn = psycopg2.connect(
                host=db_params['host'],
                port=db_params['port'],
                dbname=db_params['database'],
                user=db_params['user'],
                password=db_params['password']
            )
            conn.close()
            print("Connexion à PostgreSQL établie avec succès.")
            break
        except Exception as e:
            print(f"Tentative {i+1}/{max_retries} - Impossible de se connecter à PostgreSQL: {e}")
            if i < max_retries - 1:
                print(f"Nouvelle tentative dans {retry_interval} secondes...")
                time.sleep(retry_interval)
            else:
                raise Exception("Impossible de se connecter à la base de données après plusieurs tentatives.")
    
    # Créer une connexion SQLAlchemy pour pandas to_sql
    engine_url = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(engine_url)
    
    print(df.columns)
    print(customer_agg.columns)
    print(product_agg.columns)
    print(time_agg.columns)
    
    try:
            
        # Vider les tables existantes avant d'insérer les nouvelles données
        # Utiliser text() pour créer un objet SQL exécutable
        with engine.connect() as connection:
            # Méthode 1 : Utiliser text() (pour SQLAlchemy 1.4+)
            connection.execute(text("TRUNCATE TABLE sales_data, customer_aggregations, product_aggregations, time_aggregations RESTART IDENTITY CASCADE"))
            # Ou méthode 2 : Exécuter chaque table séparément
            # connection.execute(text("TRUNCATE TABLE sales_data RESTART IDENTITY CASCADE"))
            # connection.execute(text("TRUNCATE TABLE customer_aggregations RESTART IDENTITY CASCADE"))
            # connection.execute(text("TRUNCATE TABLE product_aggregations RESTART IDENTITY CASCADE"))
            # connection.execute(text("TRUNCATE TABLE time_aggregations RESTART IDENTITY CASCADE"))
            connection.commit()  # Important : commit les changements
            print("Tables vidées avec succès.")
        
        # Charger les données principales
        print(f"Chargement de la table sales_data ({len(df)} lignes)...")
        df.to_sql('sales_data', engine, if_exists='append', index=False, 
                  method='multi', chunksize=1000)
        
        # Charger les agrégations
        print(f"Chargement de la table customer_aggregations ({len(customer_agg)} lignes)...")
        customer_agg.to_sql('customer_aggregations', engine, if_exists='append', 
                           index=False, method='multi', chunksize=1000)
        
        print(f"Chargement de la table product_aggregations ({len(product_agg)} lignes)...")
        product_agg.to_sql('product_aggregations', engine, if_exists='append', 
                          index=False, method='multi', chunksize=1000)
        
        print(f"Chargement de la table time_aggregations ({len(time_agg)} lignes)...")
        time_agg.to_sql('time_aggregations', engine, if_exists='append', 
                       index=False, method='multi', chunksize=1000)
        
        # Ajouter une entrée dans la table de métadonnées
        metadata_df = pd.DataFrame({
            'load_timestamp': [datetime.now()],
            'rows_loaded': [len(df)],
            'source': ['ETL Pipeline']
        })
        metadata_df.to_sql('etl_metadata', engine, if_exists='append', index=False)
        
        print("Chargement des données terminé avec succès.")
        return True
        
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return False

def main():
    """
    Fonction principale pour les tests autonomes
    """
    
if __name__ == "__main__":
    main()