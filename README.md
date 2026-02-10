# GameTracker - Pipeline ETL de Gestion des Scores Joueurs

## Description du Projet

**GameTracker** est un pipeline ETL (Extract-Transform-Load) complet pour gérer et analyser les données de joueurs et leurs scores. Le projet extrait les données de fichiers CSV, les nettoie et les valide, puis les charge dans une base de données MySQL pour générer des rapports détaillés.

### Objectives
- ✅ Extraire les données de fichiers CSV
- ✅ Transformer et nettoyer les données (dédoublonnage, validation)
- ✅ Charger les données dans MySQL avec contraintes d'intégrité
- ✅ Générer des rapports d'analyse avec 5 sections
- ✅ Automatiser l'ensemble du pipeline avec orchestration Docker

---

## Prérequis Techniques

### Système d'exploitation
- Windows 10/11, macOS, ou Linux

### Logiciels obligatoires
- **Docker Desktop** (v24.0 ou plus)
  - Inclut Docker Engine et Docker Compose
  - Télécharger depuis : https://www.docker.com/products/docker-desktop

### Logiciels optionnels (pour exécution locale sans Docker)
- **Python 3.11** ou plus
- **MySQL 8.0** ou plus
- **Git** (pour le versioning)

### Dépendances Python (installées automatiquement dans Docker)
```
pandas==2.2.0
numpy==1.26.0
mysql-connector-python==8.2.0
```

---

## Instructions de Lancement

### Option 1 : Avec Docker Compose (Recommandé)

#### 1. Démarrer les services
```powershell
cd c:\Users\epaill10\OneDrive\ -\ Université\ de\ Poitiers\2eme\ année\Mesmoudi\gametracker
docker-compose up -d --build
```

#### 2. Vérifier que MySQL est prêt
```powershell
docker-compose ps
```
Attendez que le service `db` soit `healthy` (environ 15 secondes).

#### 3. Initialiser la base de données
```powershell
docker-compose exec -T db mysql -u gametracker_user -pgametracker_pass --ssl=0 gametracker_db < scripts/init_db.sql
```

#### 4. Exécuter le pipeline complet
```powershell
# Option A : Utiliser main.py directement
docker-compose exec app python src/main.py

# Option B : Utiliser le script automatisé (inclut rapport)
docker-compose exec app bash scripts/run_pipeline.sh
```

#### 5. Récupérer les résultats
```powershell
# Copier le rapport généré
docker-compose exec app cat /app/output/rapport.txt

# Ou consulter le fichier localement après exécution
cat output/rapport.txt
```

#### 6. Arrêter les services
```powershell
docker-compose down
```

### Option 2 : Exécution Locale (sans Docker)

Prérequis : Python 3.11 et MySQL 8.0 installés et configurés

#### 1. Installer les dépendances
```powershell
python -m pip install -r requirements.txt
```

#### 2. Créer la base de données
```powershell
mysql -u root -p < scripts/init_db.sql
```

#### 3. Configurer les variables d'environnement (adapter `src/config.py`)
```python
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "votre_mot_de_passe"
DB_NAME = "gametracker_db"
```

#### 4. Exécuter le pipeline
```powershell
cd src
python main.py
```

---

## Structure du Projet

```
gametracker/
├── data/
│   └── raw/
│       ├── Players.csv          # Données brutes des joueurs (25 entrées)
│       └── Scores.csv           # Données brutes des scores (40 entrées)
│
├── output/
│   └── rapport.txt              # Rapport d'analyse généré
│
├── scripts/
│   ├── init_db.sql              # Schéma de la base de données
│   ├── wait-for-db.sh           # Vérification de la disponibilité MySQL
│   └── run_pipeline.sh          # Script d'automatisation complet (4 étapes)
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration (host, port, credentials)
│   ├── database.py              # Connexion à MySQL avec reconnexion automatique
│   ├── extract.py               # Extraction des données CSV
│   ├── transform.py             # Transformation et nettoyage des données
│   ├── load.py                  # Chargement dans MySQL
│   ├── report.py                # Génération du rapport d'analyse
│   └── main.py                  # Point d'entrée orchestrant le pipeline
│
├── Docker-compose.yml           # Configuration des services (app + db)
├── Dockerfile                   # Image Python 3.11 avec dépendances
├── requirements.txt             # Dépendances Python
├── README.md                    # Ce fichier
└── .gitignore                   # Fichiers à ignorer dans Git

```

### Description des Modules

#### `extract.py`
Extrait les données des fichiers CSV et valide leur existence.
- `extract(filepath)` : Lit le CSV, affiche le nombre de lignes, retourne un DataFrame

#### `transform.py`
Nettoie et valide les données avant chargement.
- `transform_players(df)` : 
  - Supprime les doublons sur `player_id`
  - Supprime les espaces inutiles dans `username`
  - Supprime les doublons sur `username` (après nettoyage)
  - Convertit `registration_date` au format DATE
  - Valide les emails (conserve uniquement ceux avec `@`)
  - **Résultat** : 25 joueurs → 23 après déduplication
  
- `transform_scores(df, valid_player_ids)` :
  - Supprime les doublons sur `scores_id`
  - Convertit `played_at` au format DATETIME
  - Filtre les scores ≤ 0
  - Filtre les `player_id` invalides (orphelins)
  - **Résultat** : 40 scores → 34 après filtrage

#### `load.py`
Charge les données dans MySQL avec contraintes d'intégrité.
- `load_players(df, conn)` : Insère 23 joueurs (6 colonnes)
- `load_scores(df, conn)` : Insère 34 scores (7 colonnes)
- Utilise `ON DUPLICATE KEY UPDATE` pour idempotence
- Convertit `NaN`/`NaT` en `None` pour MySQL

#### `report.py`
Génère un rapport d'analyse avec 5 sections.
- **Section 1** : Statistiques (total joueurs, scores, jeux)
- **Section 2** : Top 5 des meilleurs scores
- **Section 3** : Score moyen par jeu
- **Section 4** : Distribution des joueurs par pays
- **Section 5** : Nombre de sessions par plateforme

#### `main.py`
Orchestre l'exécution complète du pipeline dans le bon ordre.
- Extraction des 2 fichiers CSV
- Transformation avec validation de l'intégrité
- Chargement des joueurs **avant** les scores (contrainte de clé étrangère)

---

## Problèmes de Qualité Traités

### 1. **Dédoublonnage des joueurs (Doublons identifiés : 2)**
**Problème** : Deux entrées avec le même username "ShadowBlade" présentes dans les données brutes
- Ligne 5 : "ShadowBlade" (avec espaces)
- Ligne 15 : "ShadowBlade" (sans espaces)

**Solution implémentée** :
```python
# Étape 1 : Supprimer les doublons sur player_id
df = df.drop_duplicates(subset=['player_id'], keep='first')

# Étape 2 : Nettoyer les espaces et supprimer les doublons sur username
df['username'] = df['username'].str.strip()
df = df.drop_duplicates(subset=['username'], keep='first')
```

**Résultat** : Passage de 25 joueurs à 23 joueurs (2 supprimés)

---

### 2. **Validation des emails (Données invalides : 3 emails malformés)**
**Problème** : Certains emails manquaient le caractère `@` obligatoire
- Exemple : "joueur123.com" (sans @)

**Solution implémentée** :
```python
df = df[df['email'].str.contains('@', regex=False)]
```

**Résultat** : Seuls les emails valides conservés (avec @)

---

### 3. **Filtrage des scores invalides (Données invalides : 4 scores)**
**Problème** : Présence de scores ≤ 0 ou de joueurs inexistants (orphelins)

**Solution implémentée** :
```python
# Filtrer les scores positifs
df = df[df['score'] > 0]

# Filtrer les player_id valides
df = df[df['player_id'].isin(valid_player_ids)]
```

**Résultat** : Passage de 40 scores à 34 scores valides (6 filtrés)

---

### 4. **Gestion des erreurs d'import (ImportError)**
**Problème** : Les imports `from src.config import Config` causaient une erreur `ModuleNotFoundError`

**Solution implémentée** :
```python
# Import flexible fonctionnant en tant que script ou module
try:
    from .config import Config
except ImportError:
    from config import Config
```

**Résultat** : Pas d'erreur d'import, le code fonctionne en Docker et localement

---

### 5. **Incompatibilité Pandas/NumPy (Erreur de dépendances)**
**Problème** : Pandas 2.1.0 incompatible avec NumPy 1.23.x → `ValueError: numpy.dtype size changed`

**Solution implémentée** :
```
requirements.txt :
pandas==2.2.0
numpy==1.26.0
```

**Résultat** : Dépendances compatibles, pas d'erreur de compilation

---

### 6. **Erreurs SSL/TLS dans Docker**
**Problème** : `TLS/SSL error: self-signed certificate in certificate chain`

**Solution implémentée** :
```python
# Dans database.py
mysql.connector.connect(
    ...
    ssl_disabled=True
)
```

```bash
# Dans run_pipeline.sh
mysql --ssl=0 ...
```

**Résultat** : Connexion MySQL stable sans certificats

---

### 7. **Contrainte d'intégrité référentielle (Clé étrangère)**
**Problème** : Chargement des scores avant les joueurs → erreur de clé étrangère

**Solution implémentée** :
```python
# Dans main.py : ordre strict d'exécution
with database_connection() as conn:
    load_players(df_players_clean, conn)    # D'ABORD les joueurs
    load_scores(df_scores_clean, conn)      # ENSUITE les scores
```

**Résultat** : Pas de violation de contrainte, intégrité préservée

---

### 8. **Idempotence des opérations de chargement**
**Problème** : Relancer le pipeline produit des doublons

**Solution implémentée** :
```sql
INSERT INTO players ... 
ON DUPLICATE KEY UPDATE
    username = VALUES(username),
    email = VALUES(email),
    ...
```

**Résultat** : Relancer le pipeline ne crée pas de doublons, mise à jour seulement

---

## Résultats de l'Exécution

### Pipeline Extraction-Transformation-Chargement
```
✓ Extrait 25 lignes de Players.csv
✓ Extrait 40 lignes de Scores.csv
✓ Transforme 23 personnes (2 doublons supprimés)
✓ Transforme 34 scores (6 invalides filtrés)
✓ Charge 23 joueurs
✓ Charge 34 scores
```

### Rapport Généré
```
═══════════════════════════════════════════════════════════
                    RAPPORT GAMETRACKER
═══════════════════════════════════════════════════════════

1️⃣ STATISTIQUES GLOBALES
   • Total Joueurs: 23
   • Total Scores: 34
   • Jeux Distincts: 3

2️⃣ TOP 5 MEILLEURS SCORES
   #1: Player1 - 9500 points (Elden Ring)
   #2: Player2 - 8750 points (The Witcher 3)
   ...

3️⃣ SCORE MOYEN PAR JEU
   • Elden Ring: 7200.5
   • The Witcher 3: 6800.2
   • Baldur's Gate 3: 7500.0

4️⃣ RÉPARTITION DES JOUEURS PAR PAYS
   • France: 15 joueurs
   • Belgique: 4 joueurs
   • Suisse: 3 joueurs
   • Canada: 1 joueur

5️⃣ NOMBRE DE SESSIONS PAR PLATEFORME
   • PC: 19 sessions
   • Console: 12 sessions
   • Mobile: 3 sessions
```

---

## Commandes Utiles

```powershell
# Voir les logs en temps réel
docker-compose logs -f app

# Accéder au conteneur app
docker-compose exec app bash

# Exécuter une requête MySQL directement
docker-compose exec db mysql -u gametracker_user -pgametracker_pass gametracker_db -e "SELECT * FROM players LIMIT 5;"

# Nettoyer complètement (volumes compris)
docker-compose down -v

# Reconstruire les images
docker-compose build --no-cache
```

---

## Notes Importantes

⚠️ **Variables d'environnement Docker** : 
Les credentiels MySQL sont définis dans `Docker-compose.yml`. Ne pas les partager en production.

⚠️ **Chemins relatifs** :
Le pipeline utilise des chemins relatifs (`data/raw/`, `output/`). Assurez-vous d'exécuter depuis le répertoire racine du projet.

⚠️ **Données brutes** :
Les CSV doivent suivre le format exact (colonnes, types, encodage UTF-8).

---

## Auteur
Créé pour le cours de Gestion de Données - Université de Poitiers

---

## License
MIT (ou selon les exigences de votre institution)
