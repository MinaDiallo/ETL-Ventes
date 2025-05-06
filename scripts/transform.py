import pandas as pd
import numpy as np
import os
from datetime import datetime

def transform_data(df=None):
    """
    Fonction pour transformer les données de ventes
    - Nettoie les données
    - Gère les valeurs manquantes
    - Corrige les types de données
    - Renomme les colonnes 
    - Crée des agrégations utiles pour l'analyse
    """
    if df is None:
      raise Exception("Pas de DataFrame fourni pour la transformation.")

    print("Début de la transformation des données...")
    print(f"Dimensions initiales: {df.shape}")
    
    # 1. Renommer les colonnes pour plus de clarté 
    # Standardiser les noms de colonnes (tout en minuscules, espaces remplacés par des underscores)
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # Mapper les noms de colonnes spécifiques
    column_mapping = {
        'ordernumber': 'order_number',
        'quantityordered': 'quantity',
        'priceeach': 'unit_price',
        'orderlinenumber': 'line_number',
        'orderdate': 'order_date',
        'qtr_id': 'quarter',
        'month_id': 'month',
        'year_id': 'year',
        'productline': 'product_line',
        'msrp': 'suggested_retail_price',
        'productcode': 'product_code',
        'customername': 'customer_name',
        'addressline1': 'address_line1',
        'addressline2': 'address_line2',
        'postalcode': 'postal_code',
        'contactlastname': 'contact_last_name',
        'contactfirstname': 'contact_first_name',
        'dealsize': 'deal_size'
    }
    df = df.rename(columns=column_mapping)
    
    # 2. Vérifier et corriger les types de données
    
    # Convertir les dates
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        # Extraire des composants de date utiles pour l'analyse
        df['order_year'] = df['order_date'].dt.year
        df['order_month'] = df['order_date'].dt.month
        df['order_day'] = df['order_date'].dt.day
        df['order_quarter'] = df['order_date'].dt.quarter
        df['order_day_of_week'] = df['order_date'].dt.dayofweek
    
    # Convertir les colonnes numériques
    numeric_columns = ['quantity', 'unit_price', 'suggested_retail_price']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 3. Gestion des valeurs manquantes
    
    # Afficher le nombre de valeurs manquantes par colonne
    missing_values = df.isnull().sum()
    print("\nValeurs manquantes par colonne:")
    print(missing_values[missing_values > 0])
    
    # Stratégies de gestion des valeurs manquantes
    # a) Pour les colonnes numériques importantes, remplacer par la médiane
    for col in ['quantity', 'unit_price']:
        if col in df.columns and df[col].isnull().sum() > 0:
            median_value = df[col].median()
            df[col] = df[col].fillna(median_value)
            print(f"Valeurs manquantes dans {col} remplacées par la médiane: {median_value}")
    
    # b) Pour les colonnes catégorielles, remplacer par "Unknown"
    categorical_columns = ['product_line', 'product_code', 'customer_name', 'city', 'state', 'country', 'deal_size']
    for col in categorical_columns:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col] = df[col].fillna("Unknown")
            print(f"Valeurs manquantes dans {col} remplacées par 'Unknown'")
    
    # c) Pour les dates, supprimer les lignes dont date est null car critique
    if 'order_date' in df.columns and df['order_date'].isnull().sum() > 0:
        rows_before = len(df)
        df = df.dropna(subset=['order_date'])
        rows_after = len(df)
        print(f"Suppression de {rows_before - rows_after} lignes avec dates manquantes")
    
    # Convertir les colonnes numériques
    numeric_columns = ['unit_price', 'suggested_retail_price']  
    integer_columns = ['quantity']  

    # Convertir les colonnes à virgule flottante
    for col in numeric_columns:
      if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Convertir les colonnes entières
    for col in integer_columns:
      if col in df.columns:
          # D'abord convertir en float pour gérer les valeurs NaN, puis en int
          df[col] = pd.to_numeric(df[col], errors='coerce')
          # Remplacer les NaN par 0 ou une autre valeur appropriée avant la conversion en int
          df[col] = df[col].fillna(0).astype(int)
          print(f"Colonne {col} convertie en entier")
    
    # 4. Création de nouvelles colonnes utiles pour l'analyse
    
    # Calculer le montant total par ligne de commande
    if 'quantity' in df.columns and 'unit_price' in df.columns:
        df['line_total'] = df['quantity'] * df['unit_price']
        print("Colonne 'line_total' créée (quantity * unit_price)")
    
    # Calculer la marge par produit
    if 'unit_price' in df.columns and 'suggested_retail_price' in df.columns:
        df['margin'] = df['unit_price'] - df['suggested_retail_price']
        df['margin_percentage'] = (df['margin'] / df['suggested_retail_price']) * 100
        print("Colonnes 'margin' et 'margin_percentage' créées")
    
    # 5. Détection et gestion des valeurs aberrantes
    
    # Exemple pour la quantité et le prix unitaire
    for col in ['unit_price']:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Identifier les valeurs aberrantes
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            print(f"\nNombre de valeurs aberrantes dans {col}: {len(outliers)}")
            
            # Plafonner les valeurs aberrantes
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
    
            print(f"Valeurs aberrantes dans {col} plafonnées entre {lower_bound} et {upper_bound}")
    
    
    # 6. Créer des agrégations utiles pour l'analyse
    
    # Créer un DataFrame d'agrégation par client
    # MODIFICATION: Utiliser reset_index() et renommer les colonnes manuellement
    customer_agg = df.groupby('customer_name').agg({
    'order_number': pd.Series.nunique,
    'line_total': 'sum',
    'quantity': 'sum',
    'order_date': ['min', 'max']
    }).reset_index()

    # Renommer les colonnes
    customer_agg.columns = ['customer_name', 'total_orders', 'total_sales', 'total_quantity', 'first_order', 'last_order']

    # Calculer la durée entre la première et la dernière commande
    customer_agg['customer_lifetime_days'] = (customer_agg['last_order'] - customer_agg['first_order']).dt.days

    # Créer un DataFrame d'agrégation par produit - CORRECTION
    product_columns = {
        'quantity': 'total_quantity',
        'line_total': 'total_revenue',
        'order_number': 'order_count',
        'customer_name': 'customer_count'
    }

    product_agg = pd.DataFrame()
    product_agg['product_code'] = df['product_code'].unique()

    for col, new_name in product_columns.items():
        if col == 'order_number' or col == 'customer_name':
            # Pour les colonnes qui nécessitent nunique
            temp_df = df.groupby('product_code')[col].nunique().reset_index()
            temp_df.columns = ['product_code', new_name]
        else:
            # Pour les colonnes qui nécessitent sum
            temp_df = df.groupby('product_code')[col].sum().reset_index()
            temp_df.columns = ['product_code', new_name]
    
    # Fusionner avec product_agg
    product_agg = product_agg.merge(temp_df, on='product_code', how='left')

    # Créer un DataFrame d'agrégation temporelle (par mois) - CORRECTION
    time_columns = {
        'line_total': 'total_sales',
        'order_number': 'order_count',
        'customer_name': 'customer_count',
        'quantity': 'total_quantity'
    }

    # Créer d'abord un DataFrame avec les combinaisons uniques de year et month
    time_agg = df[['year', 'month']].drop_duplicates().reset_index(drop=True)

    for col, new_name in time_columns.items():
        if col == 'order_number' or col == 'customer_name':
            # Pour les colonnes qui nécessitent nunique
            temp_df = df.groupby(['year', 'month'])[col].nunique().reset_index()
            temp_df.columns = ['year', 'month', new_name]
        else:
            # Pour les colonnes qui nécessitent sum
            temp_df = df.groupby(['year', 'month'])[col].sum().reset_index()
            temp_df.columns = ['year', 'month', new_name]
    
    # Fusionner avec time_agg
    time_agg = time_agg.merge(temp_df, on=['year', 'month'], how='left')
    
    # 7. Sauvegarder les données transformées
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(current_dir), 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder le DataFrame principal
    df.to_csv(os.path.join(output_dir, 'transformed_sales_data.csv'), index=False, encoding='utf-8-sig')
    print(f"\nDonnées transformées sauvegardées. Dimensions finales: {df.shape}")
    
    # Sauvegarder les agrégations
    customer_agg.to_csv(os.path.join(output_dir, 'customer_aggregations.csv'), index=False, encoding='utf-8-sig')
    product_agg.to_csv(os.path.join(output_dir, 'product_aggregations.csv'), index=False, encoding='utf-8-sig')
    time_agg.to_csv(os.path.join(output_dir, 'time_aggregations.csv'), index=False, encoding='utf-8-sig')
    print("Fichiers d'agrégation sauvegardés.")
    
    # Vérifier qu'il n'y a pas de colonnes avec suffixes _m999
    all_columns = list(df.columns) + list(customer_agg.columns) + list(product_agg.columns) + list(time_agg.columns)
    problematic_columns = [col for col in all_columns if '_m' in col and col.split('_m')[-1].isdigit()]
    if problematic_columns:
        print(f"ATTENTION: Des colonnes avec suffixes _mXXX ont été détectées: {problematic_columns}")
    else:
        print("Aucune colonne avec suffixe _mXXX détectée. Transformation réussie.")
    
    return df, customer_agg, product_agg, time_agg

def main():
    """
    Fonction principale
    """
    try:
        df, customer_agg, product_agg, time_agg = transform_data()
        print("Transformation terminée avec succès.")
        
        # Afficher quelques statistiques utiles
        print("\nAperçu des statistiques:")
        print(f"Nombre total de commandes: {df['order_number'].nunique()}")
        print(f"Nombre total de clients: {df['customer_name'].nunique()}")
        print(f"Période couverte: {df['order_date'].min()} à {df['order_date'].max()}")
        print(f"Chiffre d'affaires total: {df['line_total'].sum():.2f}")
        
        # Top 5 des clients
        top_customers = customer_agg.sort_values('total_sales', ascending=False).head(5)
        print("\nTop 5 des clients:")
        print(top_customers[['customer_name', 'total_sales', 'total_orders']])
        
        # Top 5 des produits
        top_products = product_agg.sort_values('total_revenue', ascending=False).head(5)
        print("\nTop 5 des produits:")
        print(top_products[['product_code', 'total_revenue', 'total_quantity']])
        
    except Exception as e:
        print(f"Erreur lors de la transformation: {e}")

if __name__ == "__main__":
    main()