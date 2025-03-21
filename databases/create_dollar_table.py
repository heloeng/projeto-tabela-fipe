from databases.db_connection import create_connection
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Função para obter as cotações do dólar em um período específico
def get_dollar_rates(start_date, end_date):
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial='{start_date}',dataFinalCotacao='{end_date}')?$format=json"
    response = requests.get(url)
    data = response.json()
    return data['value']

# Função para calcular a média mensal das cotações
def calculate_monthly_averages(start_year, end_year):
    monthly_averages = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            end_date = datetime.today() - timedelta(days=1)
            #end_date = datetime.today() - relativedelta(months=1)
            rates = get_dollar_rates(start_date.strftime('%m-%d-%Y'), end_date.strftime('%m-%d-%Y'))
            if rates:
                avg_rate = sum((float(rate['cotacaoCompra']) + float(rate['cotacaoVenda'])) / 2 for rate in rates) / len(rates)
                monthly_averages.append((year, month, avg_rate))
    return monthly_averages

def should_update_dollar_table(cursor):
    # Verificar se a tabela está vazia
    cursor.execute("""
        SELECT COUNT(*) FROM dollar_table;
    """)
    count = cursor.fetchone()[0]

    if count == 0:
        return True

    #Verificar se já há dados para o mês atual
    current_year = datetime.today().year
    current_month = str(datetime.now().month)

    cursor.execute("""
        SELECT 1 FROM dollar_table WHERE year = %s AND month = %s;
    """, (current_year, current_month))

    exists = cursor.fetchone()

    return exists is None

def create_dollar_table():
    conn = create_connection()
    cursor = conn.cursor()

    # Criando a tabela dollar_table se ela não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dollar_table (
            id_monthyear SERIAL PRIMARY KEY,
            month TEXT NOT NULL,
            year INTEGER NOT NULL,
            dollar NUMERIC(10, 4) NOT NULL,
            CONSTRAINT unique_date UNIQUE (month, year)
        );
    """)

    if should_update_dollar_table(cursor):
        print("Atualizando a tabela 'dollar_table'...")
        monthly_averages = calculate_monthly_averages(2020, 2025)

        for year, month, avg_rate in monthly_averages:
            cursor.execute("""
                INSERT INTO dollar_table (year, month, dollar)
                VALUES (%s, %s, %s)
                ON CONFLICT (year, month) DO UPDATE
                SET dollar = EXCLUDED.dollar;
            """, (year, month, avg_rate))

        conn.commit()
        print("Tabela 'dollar_table' atualizada com sucesso!")
    else:
        print("Nenhuma atualização necessária para a 'dollar_table'.")

    cursor.close()
    conn.close()
    print("Tabela `dollar_table` criada com sucesso!")

if __name__ == "__main__":
    create_dollar_table()
