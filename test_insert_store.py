from db_connection import create_connection

def insert_store(name, city, state, street, neighborhood, number, zip_code):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO stores_table (name, city, state, street, neighborhood, number, zip_code) 
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (name, city, state, street, neighborhood, number, zip_code))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loja {name} inserida com sucesso!")

if __name__ == "__main__":
    insert_store(
        "Loja Centro 1",
        "Rio de Janeiro",
        "RJ",
        "Avenida Atlântica",
        "Copacabana",
        "13",
        "01234-000"
    )
