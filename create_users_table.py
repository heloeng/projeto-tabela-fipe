from db_connection import create_connection

def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                CREATE TYPE user_role AS ENUM ('gestor', 'pesquisador');
            END IF;
        END $$;
    """)

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
    print("Tabela `users_table` criada com sucesso!")

if __name__ == "__main__":
    create_users_table()
