from db_connection import create_connection

def create_stores_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores_table (
            id_store SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            street TEXT,
            neighborhood TEXT,
            number TEXT,
            zip_code TEXT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `stores_table` criada com sucesso!")

if __name__ == "__main__":
    create_stores_table()
