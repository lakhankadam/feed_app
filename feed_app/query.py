import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(sql_query, values, type="", fetchtype=""):
    conn = get_db_connection()
    if type == 'select':
        try:
            if fetchtype == "fetchone":
                data = conn.execute(sql_query, values).fetchone()
            else:
                data = conn.execute(sql_query, values).fetchall()
            conn.close()
            return data
        except Exception as e:
            return ""
    elif type == 'join':
        try:
            data = conn.execute(sql_query).fetchall()
            conn.close()
            return data
        except Exception as e:
            return ""
    else:
        try:
            conn.execute(sql_query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(e)
            return False

