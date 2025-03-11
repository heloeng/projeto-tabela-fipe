from db_connection import create_connection

def insert_user(nome, email, role):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (nome, email, role) 
        VALUES (%s, %s, %s);
    """, (nome, email, role))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Usuário {nome} inserido com sucesso!")

if __name__ == "__main__":
    insert_user("Paulo Souza ", "paulo@email.com", "pesquisador")


# testar no usuario  SELECT *FROM users;