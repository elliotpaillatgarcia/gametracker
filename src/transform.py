import pandas as pd


def transform_players(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme et nettoie les donnees des personnes.
    Args:
        df: DataFrame brut des personnes.
    Returns:
        DataFrame nettoye.
    """
    df = df.copy()

    # Supprimer les doublons sur player_id
    df = df.drop_duplicates(subset=['player_id'], keep='first')
    # Nettoyer les espaces des usernames
    df['username'] = df['username'].str.strip()
    # Supprimer les doublons sur username (après strip)
    df = df.drop_duplicates(subset=['username'], keep='first')
    # Convertir les dates
    df['registration_date'] = pd.to_datetime(df['registration_date'], errors='coerce')
    # Remplacer NaT par None pour MySQL
    df['registration_date'] = df['registration_date'].where(df['registration_date'].notna(), None)
    # Nettoyer les emails invalides
    df['email'] = df['email'].where(df['email'].str.contains('@', na=False), None)
    print(f"Transforme {len(df)} personnes")
    return df

def transform_scores(df: pd.DataFrame, valid_player_ids: set) -> pd.DataFrame:
    """Transforme et nettoie les donnees des scores.
    Args:
        df: DataFrame brut des scores.
        valid_player_ids: Set des player_ids valides.
    Returns:
        DataFrame nettoye.
    """
    df = df.copy()

    # Supprimer les doublons sur score_id
    df = df.drop_duplicates(subset=['score_id'])
    # Convertir les dates
    df['played_at'] = pd.to_datetime(df['played_at'], errors='coerce')
    # Convertir les scores en numériques
    df['score'] = pd.to_numeric(df['score'], errors='coerce')
    # Supprimer les scores négatifs ou nuls
    df = df[df['score'] > 0]
    # Supprimer les scores dont le player_id n'est pas valide
    df = df[df['player_id'].isin(valid_player_ids)]
    print(f"Transforme {len(df)} scores")
    return df