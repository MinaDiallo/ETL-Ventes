
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
