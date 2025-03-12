from db_connection import create_connection

#  Criar a tabela `research_table`
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

#  Inserir Pesquisa
def insert_research(assigned_date, completion_date, user_id, store_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO research_table (assigned_date, completion_date, user_id, store_id)
        VALUES (%s, %s, %s, %s)
    """, (assigned_date, completion_date, user_id, store_id))
    
    conn.commit()
    cursor.close()
    conn.close()

#  Buscar todas as pesquisas
def get_research():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM research_table;")
    researches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return researches

if __name__ == "__main__":
    create_research_table()
