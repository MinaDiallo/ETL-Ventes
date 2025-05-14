Documentation Technique - Projet Automatisation ETL pour TPE/PME
Table des matières
Architecture du système
Base de données PostgreSQL
Pipeline ETL avec Apache Airflow
Processus d'extraction des données
Processus de transformation des données
Processus de chargement des données
Environnement Docker
Maintenance et dépannage
Architecture du système
Le système d'automatisation ETL pour TPE/PME est construit autour de trois composants principaux :

PostgreSQL : Base de données relationnelle pour le stockage des données transformées
Apache Airflow : Orchestrateur de workflows pour l'automatisation des tâches ETL
Scripts Python : Modules d'extraction, transformation et chargement des données
L'architecture suit un modèle de microservices conteneurisés avec Docker, permettant un déploiement facile et une maintenance simplifiée.

Base de données PostgreSQL
Schéma relationnel
La base de données sales_db comprend cinq tables principales organisées selon le modèle relationnel suivant :

Structure des tables
Le schéma de la base de données est défini dans le fichier sql/01-initdb.sql :

sales_data : Table principale contenant les données détaillées de ventes

Clé primaire : id (auto-incrémenté)
Colonnes principales : order_number, quantity, unit_price, order_date, product_code, customer_name
Colonnes dérivées : line_total, sales, margin, margin_percentage
Dimensions temporelles : order_year, order_month, order_day, order_quarter, order_day_of_week
customer_aggregations : Agrégations par client

Clé primaire : id (auto-incrémenté)
Métriques : total_orders, total_sales, total_quantity
Temporalité : first_order, last_order, customer_lifetime_days
product_aggregations : Agrégations par produit

Clé primaire : id (auto-incrémenté)
Métriques : total_quantity, total_revenue, order_count, customer_count
time_aggregations : Agrégations temporelles

Clé primaire : id (auto-incrémenté)
Dimensions : year, month
Métriques : total_sales, order_count, customer_count, quantity
etl_metadata : Métadonnées du processus ETL

Clé primaire : id (auto-incrémenté)
Informations : load_timestamp, rows_loaded, source
Indexation
Pour optimiser les performances des requêtes, plusieurs index ont été créés :

idx_sales_order_number sur sales_data(order_number)
idx_sales_product_code sur sales_data(product_code)
idx_sales_customer_name sur sales_data(customer_name)
idx_sales_order_date sur sales_data(order_date)
Connexion à la base de données
La connexion à PostgreSQL est configurée dans le fichier docker-compose.yml avec les paramètres suivants :

Hôte : postgres
Port : 5432
Base de données : sales_db
Utilisateur : postgres
Mot de passe : postgres
Pipeline ETL avec Apache Airflow
Structure du DAG
Le pipeline ETL est défini dans le fichier dags/etl_pipeline.py sous forme d'un DAG (Directed Acyclic Graph) Airflow nommé sales_etl_pipeline.

Le DAG est configuré pour s'exécuter quotidiennement (schedule_interval=timedelta(days=1)) et comprend cinq tâches principales :

check_data_task : Vérifie l'existence des fichiers source
extract_task : Extrait les données du fichier CSV
transform_task : Transforme et nettoie les données
load_task : Charge les données dans PostgreSQL
check_load_task : Vérifie que les données ont été correctement chargées
Les dépendances entre les tâches sont définies comme suit :

check_data_task >> extract_task >> transform_task >> load_task >> check_load_task



Configuration d'Airflow
Airflow est configuré dans le fichier docker-compose.yml avec les paramètres suivants :

Exécuteur : LocalExecutor
Connexion à la base de données : postgresql+psycopg2://postgres:postgres@postgres/airflow_db
Clé Fernet : jbw24LzqsD2dGCgfakDvzeZDGTLaKr3zpMjyvxNqSME=
Connexion PostgreSQL : postgresql://postgres:postgres@postgres:5432/sales_db
Processus d'extraction des données
Le processus d'extraction est implémenté dans le fichier scripts/extract.py et comprend les étapes suivantes :

Localisation du fichier source : Recherche du fichier CSV dans le répertoire data/
Détection de l'encodage : Tentative de lecture avec différents encodages (latin-1, ISO-8859-1, cp1252, utf-8-sig, utf-16)
Détection automatique du séparateur : Utilisation de l'option sep=None avec le moteur Python
Chargement des données : Lecture du fichier CSV dans un DataFrame pandas
Particularités techniques :

Gestion robuste des erreurs d'encodage
Détection automatique du format CSV
Vérification de l'existence du fichier source
Processus de transformation des données
Le processus de transformation est implémenté dans le fichier scripts/transform.py et comprend les étapes suivantes :

Standardisation des noms de colonnes : Conversion en minuscules et remplacement des espaces par des underscores
Correction des types de données : Conversion des dates, nombres et textes au format approprié
Gestion des valeurs manquantes : Stratégies différenciées selon les colonnes (médiane pour les valeurs numériques, "Unknown" pour les catégories)
Création de colonnes dérivées : Calcul de métriques comme sales, margin, margin_percentage
Détection et gestion des valeurs aberrantes : Utilisation de la méthode IQR (écart interquartile)
Création d'agrégations : Génération de tables d'agrégation par client, produit et période
Agrégations principales :

Par client : Nombre de commandes, ventes totales, quantité totale, première et dernière commande, durée de vie client
Par produit : Quantité totale, revenu total, nombre de commandes, nombre de clients
Temporelle : Ventes totales, nombre de commandes, nombre de clients, quantité par année et mois
Processus de chargement des données
Le processus de chargement est implémenté dans le fichier scripts/load.py et comprend les étapes suivantes :

Connexion à PostgreSQL : Établissement d'une connexion avec gestion des tentatives en cas d'échec
Nettoyage des tables existantes : Troncature des tables avant insertion des nouvelles données
Chargement par lots : Utilisation de la méthode to_sql de pandas avec chunksize=1000 pour optimiser les performances
Enregistrement des métadonnées : Ajout d'une entrée dans la table etl_metadata avec horodatage et nombre de lignes chargées
Optimisations techniques :

Chargement par lots pour gérer les grands volumes de données
Gestion des tentatives de connexion avec délai d'attente
Utilisation de transactions pour garantir l'intégrité des données
Environnement Docker
L'environnement est défini dans les fichiers docker-compose.yml et Dockerfile.

Services Docker
postgres : Base de données PostgreSQL

Image : postgres:14
Volumes :
postgres_data:/var/lib/postgresql/data (persistance)
./sql:/docker-entrypoint-initdb.d (scripts d'initialisation)
Ports : 5432:5432
airflow-webserver : Interface utilisateur Airflow

Image : apache/airflow:2.6.3
Volumes :
./dags:/opt/airflow/dags
./scripts:/opt/airflow/scripts
./data:/opt/airflow/data
./logs:/opt/airflow/logs
Ports : 8080:8080
airflow-scheduler : Planificateur Airflow

Image : apache/airflow:2.6.3
Volumes identiques au webserver
Image Docker personnalisée
Le Dockerfile définit une image Python 3.9 avec les dépendances nécessaires :

Installation des packages système pour psycopg2 (gcc, libpq-dev)
Installation des dépendances Python depuis requirements.txt
Configuration du répertoire de travail /app
Maintenance et dépannage
Surveillance du pipeline
Le pipeline peut être surveillé via l'interface web d'Airflow à l'adresse http://localhost:8080.

Les logs détaillés sont disponibles dans :

Interface Airflow : Onglet "Logs" de chaque tâche
Système de fichiers : Répertoire ./logs monté dans les conteneurs Airflow
Vérification de l'intégrité des données
La tâche check_load_task exécute la requête SQL suivante pour vérifier l'intégrité des données chargées :

SELECT 
    (SELECT COUNT(*) FROM sales_data) as sales_count,
    (SELECT COUNT(*) FROM customer_aggregations) as customer_count,
    (SELECT COUNT(*) FROM product_aggregations) as product_count,
    (SELECT COUNT(*) FROM time_aggregations) as time_count;



Problèmes courants et solutions
Échec de la tâche d'extraction :

Vérifier l'existence du fichier CSV dans /opt/airflow/data/
Vérifier l'encodage du fichier source
Échec de la tâche de transformation :

Examiner les logs pour identifier les colonnes problématiques
Vérifier la structure du fichier source
Échec de la tâche de chargement :

Vérifier la connexion à PostgreSQL
Vérifier les permissions de l'utilisateur PostgreSQL
Examiner les contraintes de schéma
Problèmes de performance :

Optimiser les index de la base de données
Ajuster le paramètre chunksize dans la fonction de chargement
Augmenter les ressources allouées aux conteneurs Docker
Cette documentation technique fournit une vue d'ensemble complète de l'architecture et du fonctionnement du système d'automatisation ETL pour TPE/PME. Elle peut être complétée par des diagrammes spécifiques et des exemples de code pour faciliter la compréhension et la maintenance du système.

