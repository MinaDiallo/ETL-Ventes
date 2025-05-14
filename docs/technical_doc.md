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

### Configuration d'Airflow

Airflow est configuré dans le fichier `docker-compose.yml` avec les paramètres suivants :

- **Exécuteur** : `LocalExecutor`
- **Connexion à la base de données** : `postgresql+psycopg2://postgres:postgres@postgres/airflow_db`
- **Clé Fernet** : `jbw24LzqsD2dGCgfakDvzeZDGTLaKr3zpMjyvxNqSME=`
- **Connexion PostgreSQL** : `postgresql://postgres:postgres@postgres:5432/sales_db`

---

## Processus d'extraction des données

Le processus d'extraction est implémenté dans le fichier `scripts/extract.py` et comprend les étapes suivantes :

- **Localisation du fichier source** : Recherche du fichier CSV dans le répertoire `data/`
- **Détection de l'encodage** : Tentative de lecture avec différents encodages (`latin-1`, `ISO-8859-1`, `cp1252`, `utf-8-sig`, `utf-16`)
- **Détection automatique du séparateur** : Utilisation de l'option `sep=None` avec le moteur `python`
- **Chargement des données** : Lecture du fichier CSV dans un DataFrame `pandas`

**Particularités techniques :**

- Gestion robuste des erreurs d'encodage
- Détection automatique du format CSV
- Vérification de l'existence du fichier source

---

## Processus de transformation des données

Le processus de transformation est implémenté dans le fichier `scripts/transform.py` et comprend les étapes suivantes :

- Standardisation des noms de colonnes
- Correction des types de données
- Gestion des valeurs manquantes
- Création de colonnes dérivées
- Détection et gestion des valeurs aberrantes
- Création d’agrégations

**Agrégations principales :**

- **Par client** : Nombre de commandes, ventes totales, quantité totale, première et dernière commande, durée de vie client
- **Par produit** : Quantité totale, revenu total, nombre de commandes, nombre de clients
- **Temporelle** : Ventes totales, nombre de commandes, nombre de clients, quantité par année et mois

---

## Processus de chargement des données

Le processus de chargement est implémenté dans le fichier `scripts/load.py` et comprend les étapes suivantes :

- Connexion à PostgreSQL
- Nettoyage des tables existantes
- Chargement par lots
- Enregistrement des métadonnées

**Optimisations techniques :**

- Chargement par lots pour gérer les grands volumes de données
- Gestion des tentatives de connexion avec délai d'attente
- Utilisation de transactions pour garantir l'intégrité des données

---

## Environnement Docker

L’environnement est défini dans les fichiers `docker-compose.yml` et `Dockerfile`.

### Services Docker

#### postgres

- **Image** : `postgres:14`
- **Volumes** :
  - `postgres_data:/var/lib/postgresql/data`
  - `./sql:/docker-entrypoint-initdb.d`
- **Ports** : `5432:5432`

#### airflow-webserver

- **Image** : `apache/airflow:2.6.3`
- **Volumes** :
  - `./dags:/opt/airflow/dags`
  - `./scripts:/opt/airflow/scripts`
  - `./data:/opt/airflow/data`
  - `./logs:/opt/airflow/logs`
- **Ports** : `8080:8080`

#### airflow-scheduler

- Même image et volumes que `airflow-webserver`

### Image Docker personnalisée

Le `Dockerfile` définit une image Python 3.9 avec les dépendances nécessaires :

- Installation des packages système pour `psycopg2`
- Installation des dépendances Python depuis `requirements.txt`
- Configuration du répertoire de travail `/app`

---

## Maintenance et dépannage

### Surveillance du pipeline

Le pipeline peut être surveillé via l’interface web Airflow à l’adresse `http://localhost:8080`.

**Logs détaillés disponibles dans :**

- Interface Airflow (onglet "Logs")
- Répertoire `./logs`

### Vérification de l’intégrité des données

La tâche `check_load_task` exécute la requête SQL suivante :

```sql
SELECT
  (SELECT COUNT(*) FROM sales_data) as sales_count,
  (SELECT COUNT(*) FROM customer_aggregations) as customer_count,
  (SELECT COUNT(*) FROM product_aggregations) as product_count,
  (SELECT COUNT(*) FROM time_aggregations) as time_count;
```

---

### Problèmes courants et solutions

- **Échec de l'extraction** :
  - Vérifier le fichier CSV dans `/opt/airflow/data/`
  - Vérifier l'encodage

- **Échec de la transformation** :
  - Examiner les logs
  - Vérifier la structure du fichier source

- **Échec du chargement** :
  - Vérifier la connexion PostgreSQL
  - Vérifier les permissions
  - Examiner les contraintes de schéma

- **Problèmes de performance** :
  - Optimiser les index
  - Ajuster `chunksize`
  - Allouer plus de ressources Docker

---

## Conclusion

Cette documentation technique fournit une vue d'ensemble complète de l'architecture et du fonctionnement du système d'automatisation ETL pour les ventes.
