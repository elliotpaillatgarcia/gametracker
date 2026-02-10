#!/bin/bash

set -e  # Arrêter à la première erreur

echo "======================================================"
echo "GAMETRACKER - Pipeline automatisé"
echo "======================================================"
echo ""

# 1. Attendre la base de données
echo "1️⃣  Attente de la base de données..."
bash /app/scripts/wait-for-db.sh
echo "✅ Base de données prête"
echo ""

# 2. Initialisation des tables
echo "2️⃣  Initialisation des tables..."
mysql --ssl=0 -h db -u gametracker_user -pgametracker_pass gametracker_db < /app/scripts/init_db.sql
echo "✅ Tables initialisées"
echo ""

# 3. Exécution du pipeline ETL
echo "3️⃣  Exécution du pipeline ETL..."
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/app/src')

import mysql.connector
from extract import extract
from transform import transform_players, transform_scores
from load import load_players, load_scores

# Connexion
conn = mysql.connector.connect(
    host='db',
    user='gametracker_user',
    password='gametracker_pass',
    database='gametracker_db',
    ssl_disabled=True
)

# Extract
print("   - Extraction...")
df_p = extract('/app/data/raw/Players.csv')
df_s = extract('/app/data/raw/Scores.csv')

# Transform
print("   - Transformation...")
df_p_t = transform_players(df_p)
valid_ids = set(df_p_t['player_id'])
df_s_t = transform_scores(df_s, valid_ids)

# Load
print("   - Chargement...")
load_players(df_p_t, conn)
load_scores(df_s_t, conn)
conn.commit()

conn.close()
print("✅ Pipeline ETL terminé")
PYTHON_SCRIPT
echo ""

# 4. Génération du rapport
echo "4️⃣  Génération du rapport..."
python3 << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '/app/src')

import mysql.connector
from report import generate_report

conn = mysql.connector.connect(
    host='db',
    user='gametracker_user',
    password='gametracker_pass',
    database='gametracker_db',
    ssl_disabled=True
)

generate_report(conn)

with open('/app/output/rapport.txt', 'r') as f:
    print(f.read())

conn.close()
PYTHON_SCRIPT
echo ""

echo "======================================================"
echo "✅ Pipeline complètement automatisé et exécuté !"
echo "======================================================"
