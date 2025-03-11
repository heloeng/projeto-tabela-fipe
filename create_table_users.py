from db_connection import create_connection

def create_table_usuarios():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Criar o tipo ENUM para o papel do usuário
    cursor.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('gestor', 'pesquisador');
            END IF;
        END $$;
    """)

    # Criar a tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id_usuario SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role user_role NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `users` criada com sucesso!")

if __name__ == "__main__":
    create_table_usuarios()
