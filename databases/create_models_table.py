from databases.db_connection import create_connection

def create_models_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Criando a tabela models_table se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models_table (
            id_model SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            id_brand INTEGER NOT NULL,
            CONSTRAINT fk_brand FOREIGN KEY (id_brand) REFERENCES brands_table(id_brand) ON DELETE CASCADE
        );
    """)

    # Inserindo os modelos pré-estabelecidos
    models = [
        ('Onix','Chevrolet'),
        ('Cruze','Chevrolet'),
        ('Tracker','Chevrolet'),
        ('S10','Chevrolet'),
        ('Ka','Ford'),
        ('Fiesta','Ford'),
        ('Focus','Ford'),
        ('Ranger','Ford'),
        ('Corolla','Toyota'),
        ('Etios','Toyota'),
        ('Hilux','Toyota'),
        ('Yaris','Toyota'),
        ('Civic','Honda'),
        ('Fit','Honda'),
        ('HR-V','Honda'),
        ('CR-V','Honda')
    ]

    for model_name, brand_name in models:
        cursor.execute("""
            INSERT INTO models_table (name, id_brand)
            VALUES (%s, (SELECT id_brand FROM brands_table WHERE name = %s))
            ON CONFLICT (name) DO NOTHING;
        """, (model_name,brand_name))

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `models_table` criada com sucesso!")

if __name__ == "__main__":
    create_models_table()
