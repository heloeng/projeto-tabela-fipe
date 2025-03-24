import psycopg2
import os
from dotenv import load_dotenv
from databases.db_connection import create_connection



def create_store_chains_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_chains_table (
            id_chain SERIAL PRIMARY KEY,
            chain_name VARCHAR(255) NOT NULL,
            store_id INTEGER NOT NULL,
            FOREIGN KEY (store_id) REFERENCES stores_table(id_store)
        );
        """)
        conn.commit()
        print("Tabela 'store_chains_table' criada com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar a tabela: {e}")
    finally:
        cursor.close()
        conn.close()