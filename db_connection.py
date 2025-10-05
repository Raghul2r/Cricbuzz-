import pyodbc

def get_connection():
    DB_CONFIG = {
        'server': r'DESKTOP-A0TP13D\SQLEXPRESS',
        'database': 'cricbuzz',
        'driver': '{ODBC Driver 17 for SQL Server}'
    }

    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        "Trusted_Connection=yes;"
    )

    return pyodbc.connect(conn_str)
