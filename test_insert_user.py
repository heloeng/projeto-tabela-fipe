from db_connection import create_connection

def insert_user(name, email, role):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users_table (name, email, role) 
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (name, email, role))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Usuário {name} inserido com sucesso!")

if __name__ == "__main__":
    insert_user("Heloiza Mendes", "heloiza@email.com", "pesquisador")
    insert_user("Vitor Trevisan", "vitortnocente@gmail.com", "pesquisador")
