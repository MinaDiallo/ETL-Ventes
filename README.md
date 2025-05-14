# Automatisation ETL pour TPE/PME

## Description du Projet

Ce projet implémente un pipeline ETL (Extract, Transform, Load) automatisé conçu pour les Très Petites, Petites et Moyennes Entreprises (TPE/PME). Il permet d'extraire des données de ventes depuis des fichiers CSV, de les transformer pour obtenir des insights métier, et de les charger dans une base de données PostgreSQL pour analyse et visualisation.

L'objectif principal est de fournir aux TPE/PME un outil simple mais puissant pour :
- Automatiser le traitement des données de ventes
- Générer des analyses clients, produits et temporelles
- Centraliser les données dans une base structurée
- Faciliter la prise de décision basée sur les données

## Captures d'écran des visualisations

### Vue d'ensemble des performances de ventes

![Vue d'ensemble des ventes](./docs/images/dashboard_overview.png)
*Tableau de bord principal montrant les KPIs de ventes et les tendances temporelles*

### Analyse client et segmentation

![Analyse client](./docs/images/customer_analysis.png)
*Segmentation des clients et analyse de la valeur client à vie (CLV)*

### Performance des produits

![Performance produit](./docs/images/product_performance.png)
*Analyse détaillée des performances par produit et catégorie*

### Structure de la base de données

![Schéma de la base de données](./docs/images/database_schema.png)
*Modèle relationnel des données de ventes dans PostgreSQL*

## Technologies Utilisées

- **Python 3.9** : Langage principal pour le traitement des données
- **Pandas** : Manipulation et transformation des données
- **PostgreSQL 14** : Base de données relationnelle
- **Apache Airflow 2.6.3** : Orchestration et automatisation des workflows
- **Docker & Docker Compose** : Conteneurisation et déploiement simplifié
- **Power BI** : Visualisation et tableaux de bord interactifs
- **Git** : Gestion de version

## Architecture du Système

Le système est composé de trois services principaux, tous orchestrés via Docker Compose :
- **PostgreSQL** : Stockage des données transformées et métadonnées Airflow
- **Airflow Webserver** : Interface utilisateur pour gérer et surveiller les pipelines
- **Airflow Scheduler** : Exécution planifiée des tâches ETL

## Installation

### Prérequis
- Docker et Docker Compose installés sur votre machine
- Git pour cloner le dépôt
- Power BI Desktop pour la visualisation (Windows uniquement)

### Étapes d'installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/MinaDiallo/Sales-ETL-Pipeline
   ```

2. Naviguez vers le répertoire du projet :
   ```bash
   cd Automatisation_TB_PME
   ```

3. Lancez les conteneurs avec Docker Compose :
   ```bash
   docker-compose up -d
   ```

4. Initialisez la base de données Airflow (première exécution uniquement) :
   ```bash
   docker-compose exec airflow-webserver airflow db init
   ```
   ou
   ```bash
   docker-compose run airflow-webserver airflow db init
   ```

5. Créez un utilisateur admin pour Airflow :
   ```bash
   docker-compose exec airflow-webserver airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```

## Guide d'Utilisation

### Structure des Données
Placez vos fichiers de données dans le répertoire `./data`. Le pipeline est configuré pour traiter le fichier `sales_data_sample.csv` par défaut.

### Exécution du Pipeline ETL
1. Accédez à l'interface Airflow via votre navigateur à l'adresse : http://localhost:8080
2. Connectez-vous avec les identifiants créés précédemment (admin/admin par défaut)
3. Activez le DAG "sales_etl_pipeline" en cliquant sur le bouton d'activation
4. Déclenchez une exécution manuelle ou attendez l'exécution planifiée quotidienne

### Étapes du Pipeline
Le pipeline ETL exécute les étapes suivantes :
1. Vérification des données source : S'assure que les fichiers nécessaires existent
2. Extraction : Lit les données depuis le fichier CSV source
3. Transformation : Nettoie les données et crée des agrégations par client, produit et période
4. Chargement : Insère les données transformées dans la base PostgreSQL
5. Vérification : Confirme que les données ont été correctement chargées

### Accès aux Données
Les données transformées sont stockées dans la base PostgreSQL et peuvent être consultées via :
```bash
docker-compose exec postgres psql -U postgres -d sales_db
```

Tables disponibles :
- `sales_data` : Données de ventes détaillées
- `customer_aggregations` : Analyses par client
- `product_aggregations` : Analyses par produit
- `time_aggregations` : Analyses temporelles

## Visualisation des Données avec Power BI

### Configuration de la connexion
1. Ouvrez Power BI Desktop
2. Cliquez sur "Obtenir les données" > "Base de données" > "PostgreSQL"
3. Entrez les informations de connexion :
   - Serveur : localhost
   - Base de données : sales_db
   - Utilisateur : postgres
   - Mot de passe : postgres
   - Port : 5432

### Tableaux de bord
Le projet inclut plusieurs tableaux de bord Power BI préconfigurés :

#### Vue d'ensemble des ventes
- Tendances des ventes sur la période
- Répartition par catégorie de produit
- Performance par région

#### Analyse client
- Segmentation des clients
- Valeur client à vie (CLV)
- Fréquence d'achat

#### Performance produit
- Produits les plus vendus
- Marges par ligne de produit
- Analyse des retours

## Structure du Projet
```
Automatisation_TB_PME/
├── dags/                  # DAGs Airflow
│   └── etl_pipeline.py    # Définition du pipeline ETL
├── scripts/               # Scripts Python pour ETL
│   ├── extract.py         # Fonctions d'extraction
│   ├── transform.py       # Fonctions de transformation
│   └── load.py            # Fonctions de chargement
├── data/                  # Données source et transformées
├── docs/                  # Capture et documentation technique
├── sql/                   # Scripts SQL d'initialisation
├── power_bi/              # Fichiers Power BI (.pbix)
├── docs/
│   └── images/            # Captures d'écran des visualisations
├── docker-compose.yml     # Configuration des services
├── Dockerfile             # Image Docker personnalisée
└── README.md              # Documentation
```

## Développement et Extension

Pour étendre ce projet :
- Ajoutez de nouvelles sources de données dans `scripts/extract.py`
- Créez des transformations supplémentaires dans `scripts/transform.py`
- Modifiez les schémas de base de données dans `sql/`
- Ajoutez de nouveaux DAGs dans le répertoire `dags/`
- Créez des visualisations Power BI supplémentaires basées sur vos besoins spécifiques

## Dépannage

### Problèmes courants
- **Airflow ne démarre pas** : Vérifiez les logs avec `docker-compose logs airflow-webserver`
- **Échec d'extraction** : Assurez-vous que le fichier CSV est présent dans le répertoire `./data`
- **Erreurs de connexion PostgreSQL** : Vérifiez que le service PostgreSQL est en cours d'exécution
- **Power BI ne se connecte pas** : Assurez-vous que le port 5432 est correctement exposé et accessible

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Forker le projet
- Créer une branche pour votre fonctionnalité
- Soumettre une pull request

## Licence

Ce projet est sous licence V0
## Contact

Aminata DIALLO - amitad.diallo@gmail.com

Lien du projet : https://github.com/MinaDiallo/Sales-ETL-Pipeline