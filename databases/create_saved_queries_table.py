from databases.db_connection import create_connection
import json

def create_saved_queries_table():
    """Cria a tabela saved_queries_table no banco de dados."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_queries_table (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year_mod TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            avg_price_data JSONB NOT NULL,  -- 🔹 JSONB aceita diferentes formatos
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela `saved_queries_table` criada/atualizada com sucesso!")


#Função para salvar uma consulta de Média Diária no banco de dados.
def save_daily_query(user_email, brand, model, year_mod, date, avg_price):
    conn = create_connection()
    cursor = conn.cursor()

    avg_price_data = {date[:7]: avg_price} 

    cursor.execute("""
        INSERT INTO saved_queries_table (user_email, brand, model, year_mod, start_date, end_date, avg_price_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_email, brand, model, year_mod, date, date, json.dumps(avg_price_data)))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Consulta de média diária salva para {user_email}, preço: R$ {avg_price:.2f}")

# Função para salvar pesquisa por período no banco de dados.
def save_period_query(user_email, brand, model, year_mod, start_date, end_date, avg_price):
    conn = create_connection()
    cursor = conn.cursor()

    avg_price_data = {"media": avg_price, "periodo": f"{start_date} a {end_date}"}  

    cursor.execute("""
        INSERT INTO saved_queries_table (user_email, brand, model, year_mod, start_date, end_date, avg_price_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_email, brand, model, year_mod, start_date, end_date, json.dumps(avg_price_data)))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Consulta por período salva para {user_email}, média: R$ {avg_price:.2f}")

# Função para salvar uma consulta de Gráfico Mensal no banco de dados
def save_graph_query(user_email, brand, model, year_mod, start_date, end_date, avg_price_data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO saved_queries_table (user_email, brand, model, year_mod, start_date, end_date, avg_price_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (user_email, brand, model, year_mod, start_date, end_date, json.dumps(avg_price_data)))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Consulta de gráfico salva para {user_email}")


#Função para consultar as ultimas pesquias
def get_last_saved_queries(user_email, limit=15):
    """Recupera as últimas consultas salvas por um usuário."""
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT brand, model, year_mod, start_date, end_date, avg_price_data, created_at
        FROM saved_queries_table
        WHERE user_email = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_email, limit))

    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results
