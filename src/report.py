"""Génération de rapports depuis la base de données"""
from datetime import datetime


def generate_report(conn, output_path: str = '/app/output/rapport.txt') -> None:
    """Génère un rapport complet et l'écrit dans un fichier.
    
    Args:
        conn: Connexion MySQL.
        output_path: Chemin vers le fichier de sortie.
    """
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Statistiques générales
        cursor.execute("SELECT COUNT(*) as total FROM players")
        total_players = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM scores")
        total_scores = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT game) as total FROM scores")
        total_games = cursor.fetchone()['total']
        
        # 2. Top 5 meilleurs scores
        cursor.execute("""
            SELECT p.username, s.game, s.score
            FROM scores s
            JOIN players p ON s.player_id = p.player_id
            ORDER BY s.score DESC
            LIMIT 5
        """)
        top_scores = cursor.fetchall()
        
        # 3. Score moyen par jeu
        cursor.execute("""
            SELECT game, AVG(score) as avg_score
            FROM scores
            GROUP BY game
            ORDER BY avg_score DESC
        """)
        avg_by_game = cursor.fetchall()
        
        # 4. Répartition des joueurs par pays
        cursor.execute("""
            SELECT country, COUNT(*) as count
            FROM players
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
        """)
        players_by_country = cursor.fetchall()
        
        # 5. Répartition des sessions par plateforme
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM scores
            WHERE platform IS NOT NULL
            GROUP BY platform
            ORDER BY count DESC
        """)
        sessions_by_platform = cursor.fetchall()
        
        # Générer le rapport
        report = []
        report.append("="*60)
        report.append("GAMETRACKER - Rapport de synthese")
        report.append(f"Genere le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*60)
        report.append("")
        
        # Statistiques générales
        report.append("--- Statistiques generales ---")
        report.append(f"Nombre de joueurs : {total_players}")
        report.append(f"Nombre de scores : {total_scores}")
        report.append(f"Nombre de jeux : {total_games}")
        report.append("")
        
        # Top 5 scores
        report.append("--- Top 5 des meilleurs scores ---")
        for i, score in enumerate(top_scores, 1):
            report.append(f"{i}. {score['username']} | {score['game']} | {score['score']}")
        report.append("")
        
        # Score moyen par jeu
        report.append("--- Score moyen par jeu ---")
        for game in avg_by_game:
            report.append(f"{game['game']} : {game['avg_score']:.1f}")
        report.append("")
        
        # Joueurs par pays
        report.append("--- Joueurs par pays ---")
        for country in players_by_country:
            report.append(f"{country['country']} : {country['count']}")
        report.append("")
        
        # Sessions par plateforme
        report.append("--- Sessions par plateforme ---")
        for platform in sessions_by_platform:
            report.append(f"{platform['platform']} : {platform['count']}")
        report.append("")
        
        report.append("="*60)
        
        # Écrire le fichier
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"Rapport généré: {output_path}")
        
    finally:
        cursor.close()
 
