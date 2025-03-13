from databases.db_connection import create_connection

def create_vehicles_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Criando a tabela vehicles_table se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles_table (
            id_vehicle SERIAL PRIMARY KEY,
            year_mod TEXT UNIQUE NOT NULL,
            id_model INTEGER NOT NULL,
            id_brand INTEGER NOT NULL,
            calc_date DATE NOT NULL DEFAULT CURRENT_DATE,
            avg_price NUMERIC(10, 2) NOT NULL,
            CONSTRAINT fk_model FOREIGN KEY (id_model) REFERENCES models_table(id_model) ON DELETE CASCADE,
            CONSTRAINT fk_brand FOREIGN KEY (id_brand) REFERENCES brands_table(id_brand) ON DELETE CASCADE
        );
    """)

    # Inserindo os modelos pré-estabelecidos
    vehicles = [
        ('2020 Gasolina','Onix','Chevrolet', '2025-03-10', 50000.00),
        ('2021 Gasolina','Cruze','Chevrolet', '2025-03-12', 75251.32),
        ('2019 Flex','Corolla','Toyota', '2025-03-12', 75000.00),
        ('2020 Flex','Corolla','Toyota', '2025-03-12', 81652.78),
        ('2020 Gasolina','Corolla','Toyota', '2025-02-28', 79852.34),
        ('2019 Álcool','CR-V','Honda', '2025-03-11', 62003.75)
    ]

    for year_mod, model_name, brand_name, calc_date, avg_price in vehicles:
        cursor.execute("""
            INSERT INTO vehicles_table (year_mod, id_model, id_brand, calc_date, avg_price)
            VALUES (%s,
            (SELECT id_model FROM models_table WHERE name = %s),            
            (SELECT id_brand FROM brands_table WHERE name = %s),
            %s, %s)
            ON CONFLICT DO NOTHING;
        """, (year_mod, model_name,brand_name, calc_date, avg_price))

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `vehicles_table` criada com sucesso!")

if __name__ == "__main__":
    create_vehicles_table()
