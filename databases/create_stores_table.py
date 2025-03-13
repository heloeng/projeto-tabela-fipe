import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis do ambiente (.env)
load_dotenv()

#  Criar conexão com o banco
def create_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

#  Criar a tabela `stores_table`
def create_stores_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores_table (
            id_store SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            street TEXT,
            neighborhood TEXT,
            number TEXT,             
            city TEXT NOT NULL,
            state TEXT NOT NULL,           
            cep TEXT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `stores_table` criada com sucesso!")

#  Inserir Loja
def insert_store(name, street, neighborhood, number, city, state, cep):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO stores_table (name, street, neighborhood, number, city, state, cep)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (name, street, neighborhood, number, city, state, cep))
    
    conn.commit()
    cursor.close()
    conn.close()

#  Buscar todas as lojas
def get_stores():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stores_table;")
    stores = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return stores

if __name__ == "__main__":
    create_stores_table()
