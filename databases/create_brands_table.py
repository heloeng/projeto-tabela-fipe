from databases.db_connection import create_connection

def create_brands_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Criando a tabela brands_table se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brands_table (
            id_brand SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)

    # Inserindo as marcas pré-estabelecidas
    cursor.execute("""
        INSERT INTO brands_table (name)
        VALUES
            ('Chevrolet'),
            ('Ford'),
            ('Toyota'),
            ('Honda')
        ON CONFLICT (name) DO NOTHING
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `brands_table` criada com sucesso!")

if __name__ == "__main__":
    create_brands_table()
