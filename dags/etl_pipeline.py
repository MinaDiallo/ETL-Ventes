from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import sys
import os

# Ajouter le répertoire du projet au PYTHONPATH
sys.path.append('/opt/airflow')

# Importer les fonctions des scripts
from scripts.extract import extract_data
from scripts.transform import transform_data
from scripts.load import load_data

# Arguments par défaut pour le DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 1, 1),
}

# Définir le DAG
dag = DAG(
    'sales_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL pour les données de ventes',
    schedule_interval=timedelta(days=1),  # Exécution quotidienne
    catchup=False,
    tags=['sales', 'etl'],
)

# Tâche 1: Vérifier que les données source existent
check_data_task = BashOperator(
    task_id='check_data_exists',
    bash_command='ls -la /opt/airflow/data/sales_data_sample.csv || exit 1',
    dag=dag,
)

# Tâche 2: Extraction des données
def extract_task_function():
    print("Début de l'extraction des données...")
    data = extract_data()
    if data is None:
        raise ValueError("L'extraction a échoué")
    print(f"Extraction réussie. Dimensions du DataFrame: {data.shape}")
    return data.to_json()  # Convertir en JSON pour passer entre les tâches

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_task_function,
    dag=dag,
)

# Tâche 3: Transformation des données
def transform_task_function(ti):
    print("Début de la transformation des données...")
    # Récupérer les données de la tâche précédente
    json_data = ti.xcom_pull(task_ids='extract_data')
    if not json_data:
        raise ValueError("Aucune donnée à transformer")
    
    # Convertir JSON en DataFrame
    import pandas as pd
    data = pd.read_json(json_data)
    
    # Transformer les données
    transformed_data, customer_agg, product_agg, time_agg = transform_data(data)
    
    # Sauvegarder les résultats pour la tâche suivante
    result = {
        'transformed_data': transformed_data.to_json(),
        'customer_agg': customer_agg.to_json(),
        'product_agg': product_agg.to_json(),
        'time_agg': time_agg.to_json()
    }
    
    return result

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_task_function,
    dag=dag,
)

# Tâche 4: Chargement des données dans PostgreSQL
def load_task_function(ti):
    print("Début du chargement des données...")
    # Récupérer les données transformées
    result = ti.xcom_pull(task_ids='transform_data')
    if not result:
        raise ValueError("Aucune donnée à charger")
    
    # Convertir JSON en DataFrames
    import pandas as pd
    transformed_data = pd.read_json(result['transformed_data'])
    customer_agg = pd.read_json(result['customer_agg'])
    product_agg = pd.read_json(result['product_agg'])
    time_agg = pd.read_json(result['time_agg'])
    
    # Charger les données dans PostgreSQL
    success = load_data(transformed_data, customer_agg, product_agg, time_agg)
    
    if not success:
        raise ValueError("Le chargement des données a échoué")
    
    return "Chargement terminé avec succès"

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_task_function,
    dag=dag,
)

# Tâche 5: Vérifier le chargement des données
check_load_task = PostgresOperator(
    task_id='check_data_loaded',
    postgres_conn_id='postgres_default',
    sql="""
    SELECT 
        (SELECT COUNT(*) FROM sales_data) as sales_count,
        (SELECT COUNT(*) FROM customer_aggregations) as customer_count,
        (SELECT COUNT(*) FROM product_aggregations) as product_count,
        (SELECT COUNT(*) FROM time_aggregations) as time_count;
    """,
    dag=dag,
)

# Définir les dépendances entre les tâches
check_data_task >> extract_task >> transform_task >> load_task >> check_load_task