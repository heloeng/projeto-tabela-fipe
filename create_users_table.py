from db_connection import create_connection

#  Criar a tabela `users_table`
def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Criar ENUM user_role se não existir
    cursor.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('gestor', 'pesquisador');
            END IF;
        END $$;
    """)

    # Criar a tabela users_table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_table (
            id_user SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role user_role NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print(" Tabela `users_table` criada com sucesso!")

#  Inserir Usuário
def insert_user(name, email, role):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users_table (name, email, role) 
        VALUES (%s, %s, %s)
    """, (name, email, role))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Usuário '{name}' inserido com sucesso!")

#  Buscar todos os usuários
def get_users():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users_table;")
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return users

if __name__ == "__main__":
    create_users_table()
