from utils.db_connection import get_connection

class PlayerStatsDB:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM top_run_scorers")
        columns = [column[0] for column in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def get_next_id(self):
        players = self.fetch_all()
        return max(player['player_id'] for player in players) + 1 if players else 1

    def add_player(self, player_id, name, matches, innings, runs, average):
        self.cursor.execute("""
            INSERT INTO top_run_scorers (player_id, player_name, matches, innings, runs, average)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (player_id, name, matches, innings, runs, average))
        self.conn.commit()

    def update_player(self, player_id, name, matches, innings, runs, average):
        self.cursor.execute("""
            UPDATE top_run_scorers
            SET player_name=?, matches=?, innings=?, runs=?, average=?
            WHERE player_id=?
        """, (name, matches, innings, runs, average, player_id))
        self.conn.commit()

    def delete_player(self, player_id):
        self.cursor.execute("DELETE FROM top_run_scorers WHERE player_id=?", (player_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
