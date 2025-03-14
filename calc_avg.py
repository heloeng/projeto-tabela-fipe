import psycopg2
from datetime import datetime, timedelta
from databases.db_connection import create_connection

def update_avg_price():
    # Configuração da conexão com o banco de dados
    conn = create_connection()
    cur = conn.cursor()
    
    # Obtendo a data do dia anterior
    today = datetime.now().date()
    yesterday = (datetime.now() - timedelta(days=1)).date()
    hour = datetime.now().hour   # the current hour
    minute = datetime.now().minute # the current minute
    minutes = str(minute).zfill(2)
    
    print('Função para cálculo da média de preços executada por último em',today, f'às {hour}:{minutes}' )

    
    # Consulta para calcular a média de price por id_vehicle para registros do dia anterior
    cur.execute("""
        SELECT id_vehicle, AVG(price) AS avg_price
        FROM register_table
        WHERE reg_date = %s
        GROUP BY id_vehicle
    """, (yesterday,))
    
    avg_prices = cur.fetchall()
    
    # Atualizando a tabela vehicles_table com os valores calculados
    for id_vehicle, avg_price in avg_prices:
        cur.execute("""
            UPDATE vehicles_table
            SET avg_price = %s, calc_date = %s
            WHERE id_vehicle = %s
        """, (avg_price, today, id_vehicle))
    
    # Commit das alterações e fechamento da conexão
    conn.commit()
    cur.close()
    conn.close()



if __name__ == "__main__":
    update_avg_price()
