import os
import sys
import pandas as pd

# Ajouter le répertoire scripts au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Importer les fonctions des scripts
from extract import extract_data
from transform import transform_data
from load import load_data

def run_pipeline():
    """
    Exécute le pipeline ETL complet
    """
    print("=== DÉBUT DU PIPELINE ETL ===")
    
    # Étape 1 : Extraction
    print("\n=== ÉTAPE 1 : EXTRACTION ===")
    try:
        data = extract_data()
        if data is None:
            print("L'extraction a échoué. Arrêt du pipeline.")
            return
        print("Extraction réussie.")
    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return
    
    # Étape 2 : Transformation
    print("\n=== ÉTAPE 2 : TRANSFORMATION ===")
    try:
        transformed_data, customer_agg, product_agg, time_agg = transform_data(data)
        print("Transformation réussie.")
        print(f"Dimensions du DataFrame principal : {transformed_data.shape}")
        print(f"Dimensions des agrégations des clients : {customer_agg.shape}")
        print(f"Dimensions des agrégations des produits : {product_agg.shape}")
        print(f"Dimensions des agrégations temporelles : {time_agg.shape}")
        print(transformed_data.head())
        print(customer_agg.head())
        print(product_agg.head())
        print(time_agg.head())
    except Exception as e:
        print(f"Erreur lors de la transformation : {e}")
        return
    
    # Étape 3 : Chargement (à implémenter)
    print("\n=== ÉTAPE 3 : CHARGEMENT ===")
    
    try:
        success = load_data(transformed_data, customer_agg, product_agg, time_agg)
        if success:
            print("Chargement réussi dans PostgreSQL.")
        else:
            print("Le chargement a échoué.")
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return

if __name__ == "__main__":
    run_pipeline()