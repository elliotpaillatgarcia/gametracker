#!/bin/bash
# Script de lancement du pipeline ETL
set -e

echo "Attente de la base de donnees..."
./scripts/wait-for-db.sh

echo "Initialisation des tables..."
mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" --skip-ssl < scripts/init_db.sql

echo "Execution du pipeline ETL..."
python -m src.main

echo "Generation du rapport..."
python3 << 'EOF'
import sys
sys.path.insert(0, './src')
from database import database_connection
from report import generate_report
with database_connection() as conn:
    generate_report(conn)
EOF

echo "Termine!"

