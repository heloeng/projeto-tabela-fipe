from databases.db_connection import create_connection

def create_register_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Criando a tabela register_table se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS register_table (
            id_register SERIAL PRIMARY KEY,
            id_user INTEGER NOT NULL,
            id_store INTEGER NOT NULL,
            id_vehicle INTEGER NOT NULL,
            plate TEXT NOT NULL,
            year_man INTEGER NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            reg_date DATE NOT NULL DEFAULT CURRENT_DATE,
            CONSTRAINT fk_user FOREIGN KEY (id_user) REFERENCES users_table(id_user) ON DELETE CASCADE,
            CONSTRAINT fk_store FOREIGN KEY (id_store) REFERENCES stores_table(id_store) ON DELETE CASCADE,
            CONSTRAINT fk_vehicle FOREIGN KEY (id_vehicle) REFERENCES vehicles_table(id_vehicle) ON DELETE CASCADE
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `register_table` criada com sucesso!")

if __name__ == "__main__":
    create_register_table()