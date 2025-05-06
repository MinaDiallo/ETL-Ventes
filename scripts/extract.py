import pandas as pd
import os
from datetime import datetime

def extract_data():
    """
    Fonction pour extraire les données du fichier CSV et les préparer pour l'analyse
    """
    # Définir le chemin vers le fichier de données
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  
    data_file = os.path.join(project_root, 'data', 'sales_data_sample.csv')
    
    # Vérifier si le fichier existe
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Le fichier {data_file} n'existe pas")
    
    # Charger les données
    encodings = ['latin-1', 'ISO-8859-1', 'cp1252', 'utf-8-sig', 'utf-16']
    df = None
    
    for encoding in encodings:
        try:
            print(f"Tentative de chargement avec l'encodage {encoding}...")
            # Essayer de détecter automatiquement le séparateur
            df = pd.read_csv(data_file, encoding=encoding, sep=None, engine='python')
            print(f"Succès avec l'encodage {encoding}!")
            
            break
        except Exception as e:
            print(f"Échec avec l'encodage {encoding}: {e}")
    
    if df is None:
        raise Exception("Impossible de charger le fichier avec les encodages testés")
    return df
  
#Todo remove
def main():
    """
    Fonction principale
    """
    print("Début de l'extraction des données...")
    data = extract_data()
    
    if data is not None:
        # Ici, vous pouvez ajouter d'autres traitements sur les données
        # Par exemple, des analyses statistiques, des visualisations, etc.
        print("Extraction terminée avec succès.")
        
    else:
        print("L'extraction a échoué.")

if __name__ == "__main__":
    main()