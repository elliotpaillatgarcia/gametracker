"""Point d'entrée du pipeline ETL complet"""
from src.extract import extract
from src.transform import transform_players, transform_scores
from src.load import load_players, load_scores
from src.database import database_connection

def main():
    # Extraction
    df_players = extract('data/raw/Players.csv')
    df_scores = extract('data/raw/Scores.csv')

    # Transformation
    df_players_clean = transform_players(df_players)
    valid_player_ids = set(df_players_clean['player_id'])
    df_scores_clean = transform_scores(df_scores, valid_player_ids)

    # Chargement
    with database_connection() as conn:
        load_players(df_players_clean, conn)  # Charger les joueurs d'abord
        load_scores(df_scores_clean, conn)    # Puis les scores (clé étrangère)

if __name__ == "__main__":
    main()
