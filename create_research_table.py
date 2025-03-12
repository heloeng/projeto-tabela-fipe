from db_connection import create_connection

def create_research_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_table (
            id_campaign SERIAL PRIMARY KEY,
            assigned_date DATE NOT NULL,
            completion_date DATE,
            user_id INTEGER REFERENCES users_table(id_user) ON DELETE CASCADE,
            store_id INTEGER REFERENCES stores_table(id_store) ON DELETE CASCADE
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `research_table` criada com sucesso!")

if __name__ == "__main__":
    create_research_table()
