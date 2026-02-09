import pandas as pd


def load_players(df: pd.DataFrame, conn) -> int:
    """Charge les joueurs dans la base de donnees.
    Args:
        df: DataFrame des joueurs.
        conn: Connexion MySQL.
    Returns:
        Nombre de lignes inserees.
    """
    cursor = conn.cursor()
    query = """
    INSERT INTO players
    (player_id, username, email, registration_date)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        username = VALUES(username),
        email = VALUES(email),
        registration_date = VALUES(registration_date)
    """
    count = 0
    for _, row in df.iterrows():
        values = (
            int(row['player_id']),
            row['username'],
            row['email'] if pd.notna(row['email']) else None,
            row['registration_date'].strftime('%Y-%m-%d') if pd.notna(row['registration_date']) else None
        )
        cursor.execute(query, values)
        count += 1

    print(f"Charge {count} joueurs")
    return count


def load_scores(df: pd.DataFrame, conn) -> int:
    """Charge les scores dans la base de donnees.
    Args:
        df: DataFrame des scores.
        conn: Connexion MySQL.
    Returns:
        Nombre de lignes inserees.
    """
    cursor = conn.cursor()
    query = """
    INSERT INTO scores
    (score_id, player_id, score, played_at)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        score = VALUES(score),
        played_at = VALUES(played_at)
    """
    count = 0
    for _, row in df.iterrows():
        values = (
            int(row['score_id']),
            int(row['player_id']),
            float(row['score']) if pd.notna(row['score']) else None,
            row['played_at'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['played_at']) else None
        )
        cursor.execute(query, values)
        count += 1

    print(f"Charge {count} scores")
    return count