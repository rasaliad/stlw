import fdb
from contextlib import contextmanager
from app.core.config import settings

class FirebirdConnection:
    def __init__(self):
        self.connection_params = {
            'host': settings.FIREBIRD_HOST,
            'port': settings.FIREBIRD_PORT,
            'database': settings.FIREBIRD_DATABASE,
            'user': settings.FIREBIRD_USER,
            'password': settings.FIREBIRD_PASSWORD,
            'charset': 'UTF8'
        }
 
    @contextmanager
    def get_connection(self):
        connection = None
        try:
            connection = fdb.connect(**self.connection_params)
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: tuple = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
            finally:
                cursor.close()

db = FirebirdConnection()