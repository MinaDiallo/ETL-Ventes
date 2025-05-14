# Documentation Technique - Projet Automatisation ETL pour TPE/PME

## Table des matières
1. [Architecture du système](#architecture-du-système)
2. [Base de données PostgreSQL](#base-de-données-postgresql)
3. [Pipeline ETL avec Apache Airflow](#pipeline-etl-avec-apache-airflow)
4. [Processus d'extraction des données](#processus-dextraction-des-données)
5. [Processus de transformation des données](#processus-de-transformation-des-données)
6. [Processus de chargement des données](#processus-de-chargement-des-données)
7. [Environnement Docker](#environnement-docker)
8. [Maintenance et dépannage](#maintenance-et-dépannage)

---

## Architecture du système

Le système d'automatisation ETL pour TPE/PME est construit autour de trois composants principaux :

- **PostgreSQL** : Base de données relationnelle pour le stockage des données transformées.
- **Apache Airflow** : Orchestrateur de workflows pour l'automatisation des tâches ETL.
- **Scripts Python** : Modules d'extraction, de transformation et de chargement des données.

L'architecture suit un modèle de microservices conteneurisés avec Docker, permettant un déploiement facile et une maintenance simplifiée.

---

## Base de données PostgreSQL

### Schéma relationnel

La base de données `sales_db` comprend cinq tables principales organisées selon le modèle relationnel suivant :

### Structure des tables

Définie dans le fichier `sql/01-initdb.sql` :

- **sales_data** : Table principale contenant les données détaillées de ventes.
  - Clé primaire : `id` (auto-incrémenté)
  - Colonnes principales : `order_number`, `quantity`, `unit_price`, `order_date`, `product_code`, `customer_name`
  - Colonnes dérivées : `line_total`, `sales`, `margin`, `margin_percentage`
  - Dimensions temporelles : `order_year`, `order_month`, `order_day`, `order_quarter`, `order_day_of_week`

- **customer_aggregations** : Agrégations par client.
  - Clé primaire : `id`
  - Métriques : `total_orders`, `total_sales`, `total_quantity`
  - Temporalité : `first_order`, `last_order`, `customer_lifetime_days`

- **product_aggregations** : Agrégations par produit.
  - Clé primaire : `id`
  - Métriques : `total_quantity`, `total_revenue`, `order_count`, `customer_count`

- **time_aggregations** : Agrégations temporelles.
  - Clé primaire : `id`
  - Dimensions : `year`, `month`
  - Métriques : `total_sales`, `order_count`, `customer_count`, `quantity`

- **etl_metadata** : Métadonnées du processus ETL.
  - Clé primaire : `id`
  - Informations : `load_timestamp`, `rows_loaded`, `source`

### Indexation

Pour optimiser les performances des requêtes, plusieurs index ont été créés :

- `idx_sales_order_number` sur `sales_data(order_number)`
- `idx_sales_product_code` sur `sales_data(product_code)`
- `idx_sales_customer_name` sur `sales_data(customer_name)`
- `idx_sales_order_date` sur `sales_data(order_date)`

### Connexion à la base de données

La connexion PostgreSQL est définie dans `docker-compose.yml` :

- **Hôte** : `postgres`
- **Port** : `5432`
- **Base de données** : `sales_db`
- **Utilisateur** : `postgres`
- **Mot de passe** : `postgres`

![Diagramme de Classe](./images/Diag-classe.png)
*Diagramme de Classe*
---

## Pipeline ETL avec Apache Airflow

### Structure du DAG

Le pipeline est défini dans le fichier `dags/etl_pipeline.py` sous la forme d’un DAG nommé `sales_etl_pipeline`.

- **Fréquence** : quotidienne (`schedule_interval=timedelta(days=1)`)
- **Tâches principales** :
  1. `check_data_task` : Vérifie l'existence des fichiers source.
  2. `extract_task` : Extrait les données du fichier CSV.
  3. `transform_task` : Transforme et nettoie les données.
  4. `load_task` : Charge les données dans PostgreSQL.
  5. `check_load_task` : Vérifie que les données ont été correctement chargées.

```python
check_data_task >> extract_task >> transform_task >> load_task >> check_load_task
```

### Configuration d'Airflow

Paramètres dans `docker-compose.yml` :

- **Exécuteur** : `LocalExecutor`
- **Connexion DB** : `postgresql+psycopg2://postgres:postgres@postgres/airflow_db`
- **Clé Fernet** : `jbw24LzqsD2dGCgfakDvzeZDGTLaKr3zpMjyvxNqSME=`
- **Connexion PostgreSQL** : `postgresql://postgres:postgres@postgres:5432/sales_db`

---

## Processus d'extraction des données

Implémenté dans `scripts/extract.py` :

- Recherche du fichier dans `data/`
- Détection de l’encodage (`latin-1`, `ISO-8859-1`, `cp1252`, `utf-8-sig`, `utf-16`)
- Détection automatique du séparateur (`sep=None`)
- Chargement dans un `DataFrame` pandas

### Particularités techniques :
- Gestion robuste des erreurs d'encodage
- Détection automatique du format CSV
- Vérification de l’existence du fichier source

---

## Processus de transformation des données

Implémenté dans `scripts/transform.py` :

- Standardisation des noms de colonnes
- Correction des types de données
- Gestion des valeurs manquantes (médiane ou "Unknown")
- Création de colonnes dérivées (`sales`, `margin`, etc.)
- Détection et traitement des valeurs aberrantes (IQR)
- Création des tables d'agrégations

### Agrégations principales :
- **Client** : commandes, ventes, quantité, durée de vie client
- **Produit** : quantités, revenus, commandes, clients
- **Temporelle** : ventes, commandes, clients par année et mois

---

## Processus de chargement des données

Implémenté dans `scripts/load.py` :

- Connexion PostgreSQL avec gestion des tentatives
- Troncature des tables avant chargement
- Chargement par lots (`to_sql(chunksize=1000)`)
- Enregistrement des métadonnées (`etl_metadata`)

### Optimisations techniques :
- Chargement par lots pour gros volumes
- Transactions PostgreSQL
- Attente et retries sur la connexion

---

## Environnement Docker

Défini dans `docker-compose.yml` et `Dockerfile`.

### Services Docker

- **postgres** :
  - Image : `postgres:14`
  - Volumes :
    - `postgres_data:/var/lib/postgresql/data`
    - `./sql:/docker-entrypoint-initdb.d`
  - Ports : `5432:5432`

- **airflow-webserver** :
  - Image : `apache/airflow:2.6.3`
  - Volumes :
    - `./dags:/opt/airflow/dags`
    - `./scripts:/opt/airflow/scripts`
    - `./data:/opt/airflow/data`
    - `./logs:/opt/airflow/logs`
  - Ports : `8080:8080`

- **airflow-scheduler** :
  - Image : `apache/airflow:2.6.3`
  - Volumes identiques au webserver

### Image Docker personnalisée

- Basée sur Python 3.9

### Installation :
- Packages système (`gcc`, `libpq-dev`)
- Dépendances Python via `requirements.txt`
- Répertoire de travail : `/app`

---

## Maintenance et dépannage

### Surveillance du pipeline

- Interface web : [http://localhost:8080](http://localhost:8080)
- Logs :
  - Airflow : onglet "Logs"
  - Système de fichiers : `./logs`

### Vérification de l'intégrité des données

Requête SQL exécutée par `check_load_task` :

```sql
SELECT
  (SELECT COUNT(*) FROM sales_data) AS sales_count,
  (SELECT COUNT(*) FROM customer_aggregations) AS customer_count,
  (SELECT COUNT(*) FROM product_aggregations) AS product_count,
  (SELECT COUNT(*) FROM time_aggregations) AS time_count;
```

### Problèmes courants et solutions

- **Échec extraction** :
  - Vérifier existence du fichier dans `/opt/airflow/data/`
  - Vérifier encodage du fichier

- **Échec transformation** :
  - Examiner les logs
  - Vérifier structure du fichier source

- **Échec chargement** :
  - Vérifier connexion PostgreSQL
  - Vérifier permissions et contraintes

- **Problèmes de performance** :
  - Optimiser les index
  - Ajuster `chunksize`
  - Augmenter les ressources Docker
