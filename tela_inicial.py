import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
from databases.db_connection import create_connection
from databases.create_saved_queries_table import save_daily_query, save_period_query, save_graph_query, get_last_saved_queries
import psycopg2
from datetime import datetime
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
import main

# Configurações do Google OAuth
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
REDIRECT_URI = "http://localhost:8501"
CLIENT_SECRETS_FILE = "client_secret.json"

# Verifica se o arquivo client_secret.json existe
if not os.path.exists(CLIENT_SECRETS_FILE):
    st.error(f"Arquivo {CLIENT_SECRETS_FILE} não encontrado. Por favor, coloque-o no diretório do projeto.")
    st.stop()

# Gerenciamento de credenciais no session_state
def get_credentials():
    if "credentials" not in st.session_state:
        st.session_state["credentials"] = None
    return st.session_state["credentials"]

def set_credentials(credentials):
    st.session_state["credentials"] = credentials

# Função para recuperar as lojas do banco de dados
def get_lojas():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id_store, name, street, number, neighborhood, city, state, cep
    FROM stores_table
    """)
    lojas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{
        'id': loja[0],
        'nome': loja[1],
        'rua': loja[2],
        'numero': loja[3],
        'bairro': loja[4],
        'cidade': loja[5],
        'estado': loja[6],
        'cep': loja[7]
    } for loja in lojas]

# Função para recuperar as brands do banco de dados
def get_brands():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT INITCAP(TRIM(LOWER(name))) FROM brands_table
    """)  # Usando INITCAP para garantir que a primeira letra seja maiúscula
    brands = cursor.fetchall()
    cursor.close()
    conn.close()
    return [brand[0] for brand in brands]


# Função para recuperar os modelos de uma marca
def get_models_by_brand(brand_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT models_table.name 
        FROM models_table
        JOIN brands_table ON models_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s
    """, (brand_name,))
    models = cursor.fetchall()
    cursor.close()
    conn.close()
    return [model[0] for model in models] if models else []

# Função para recuperar os anos/modelos de um veículo
def get_years_by_model(brand_name, model_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT year_mod 
        FROM vehicles_table
        JOIN models_table ON vehicles_table.id_model = models_table.id_model
        JOIN brands_table ON vehicles_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s AND models_table.name = %s
    """, (brand_name, model_name))
    years = cursor.fetchall()
    cursor.close()
    conn.close()
    return [year[0] for year in years] if years else []

# Função para listar  o preço médio do veículo "hoje"
def get_vehicle_price_avg(brand_name, model_name, year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT avg_price
        FROM vehicles_table
        JOIN models_table ON vehicles_table.id_model = models_table.id_model
        JOIN brands_table ON vehicles_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s AND models_table.name = %s AND vehicles_table.year_mod = %s
    """, (brand_name, model_name, year))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]#, result[1]  # Average price and count of records
    return None, 0

# Função para listar o preço médio do veículo "período de tempo"
def get_vehicle_price_avg_period(brand_name, model_name, year, start_date, end_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price) 
        FROM register_table
        JOIN vehicles_table ON register_table.id_vehicle = vehicles_table.id_vehicle
        JOIN models_table ON vehicles_table.id_model = models_table.id_model
        JOIN brands_table ON vehicles_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s 
          AND models_table.name = %s 
          AND vehicles_table.year_mod = %s
          AND register_table.reg_date BETWEEN %s AND %s
    """, (brand_name, model_name, year, start_date, end_date))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result[0] if result else None


#Função para listar o preço médio do veículo(marcar, modelo e ano) "período de tempo" separado por mês/ano
def get_vehicle_price_avg_graph(vehicle_id, start_date, end_date):
    """Consulta a média de preços por mês/ano para um veículo específico dentro de um intervalo e gera dados para o gráfico"""
    conn = create_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            DATE_TRUNC('month', register_table.reg_date) AS mes_ano,
            AVG(register_table.price) AS preco_medio
        FROM register_table
        WHERE register_table.id_vehicle = %s
          AND register_table.reg_date BETWEEN %s AND %s
        GROUP BY mes_ano
        ORDER BY mes_ano;
    """

    cursor.execute(query, (vehicle_id, start_date, end_date))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results  # Retorna uma lista de tuplas [(mes_ano, preco_medio), ...]

#Função para buscar id do veículo para gerar o gráfico
def get_vehicle_id_for_graph(brand, model, year):
    """Busca o ID do veículo com base na marca, modelo e ano para gerar o gráfico"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_vehicle FROM vehicles_table
        JOIN models_table ON vehicles_table.id_model = models_table.id_model
        JOIN brands_table ON vehicles_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s 
          AND models_table.name = %s 
          AND vehicles_table.year_mod = %s
    """, (brand, model, year))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result[0] if result else None


# Função para registrar o preço do veículo
def register_vehicle_price(marca, modelo, loja_id, preco, ano):
    conn = create_connection()
    cursor = conn.cursor()

    # Verifica se a marca já existe no banco de dados
    cursor.execute("SELECT id_brand FROM brands_table WHERE name = %s", (marca,))
    existing_brand = cursor.fetchone()

    # Se a marca não existir, insira uma nova marca
    if not existing_brand:
        cursor.execute("INSERT INTO brands_table (name) VALUES (%s) RETURNING id_brand", (marca,))
        id_brand = cursor.fetchone()[0]
    else:
        id_brand = existing_brand[0]

    # Recupera o ID do modelo
    cursor.execute("SELECT id_model FROM models_table WHERE name = %s", (modelo,))
    id_model = cursor.fetchone()
    if id_model is None:
        st.error(f"Modelo '{modelo}' não encontrado.")
        return

    # Verifica se já existe um preço registrado para esse modelo/ano/loja
    cursor.execute("""
        SELECT id_vehicle_price FROM vehicle_prices_table
        WHERE id_model = %s AND year_mod = %s AND id_store = %s
    """, (id_model[0], ano, loja_id))
    existing_price = cursor.fetchone()

    if existing_price:
        st.warning(f"Preço para {modelo} ({ano}) já registrado nesta loja.")
    else:
        # Inserir o novo preço no banco de dados
        cursor.execute("""
            INSERT INTO vehicle_prices_table (id_model, year_mod, id_store, price)
            VALUES (%s, %s, %s, %s)
        """, (id_model[0], ano, loja_id, preco))

        conn.commit()
        st.success(f"Preço de {modelo} ({ano}) registrado com sucesso na loja!")

    cursor.close()
    conn.close()

# Armazenamento de informações no estado da sessão
if 'lojas_registradas' not in st.session_state:
    st.session_state.lojas_registradas = get_lojas()  # Carrega as lojas do banco de dados

#------INICIO BLOCO DE AUTENTICAÇÃO-----

# Fluxo de autenticação
def authenticate():
    if not get_credentials():
        try:
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            authorization_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent"
            )
            st.session_state["state"] = state
            st.write("Redirecionando para o login do Google...")
            st.write(
                f'<meta http-equiv="refresh" content="1;url={authorization_url}">',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Erro ao iniciar autenticação: {str(e)}")

    
# Consulta o role do usuário na tabela users_table usando db_connection
def get_user_role(email):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users_table WHERE email = %s", (email,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Erro ao consultar o banco de dados: {str(e)}")
        return None

# Processa o callback do OAuth
def process_callback():
    if "code" not in st.query_params:
        return False
    
    state_from_url = st.query_params.get("state")
    stored_state = st.session_state.get("state")
    
    if not stored_state:
        st.warning("State não encontrado. Usando state da URL como fallback.")
        stored_state = state_from_url
        st.session_state["state"] = stored_state
    
    if state_from_url != stored_state:
        st.error("Estado inválido ou ausente. Tente fazer login novamente.")
        st.session_state.pop("state", None)
        return False
    
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=stored_state
        )
        flow.fetch_token(code=st.query_params["code"])
        credentials = flow.credentials
        set_credentials(credentials)
        st.session_state.pop("state", None)
        st.query_params.clear()
        st.rerun()
        return True
    except Exception as e:
        st.error(f"Erro ao processar o callback: {str(e)}")
        st.session_state.pop("state", None)
        return False

# Obtém informações do usuário autenticado
def get_user_info(credentials):
    if not credentials:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao obter informações do usuário: {str(e)}")
        return None
    
#------FIM BLOCO DE AUTENTICAÇÃO-----

# Processa o callback no início do script
if "code" in st.query_params:
    process_callback()

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Consulta por período", "Gráfico Mensal"], key="navegacao_radio_I")

# Autenticação na sidebar
st.sidebar.header("Acesso para colaboradores")
credentials = get_credentials()

if credentials and not credentials.expired:
    user_info = get_user_info(credentials)
    if user_info:
        user_email = user_info['email']
        user_role = get_user_role(user_email) #Consulta da role do usuário na tabela user_table

        st.sidebar.write(f"Bem-vindo(a), {user_info['name']} ({user_email})")
        if user_role:
            st.sidebar.markdown(f"Logado como **{user_role}**")
            # Redirecionamento para tela_pesquisador.py se o role for "pesquisador" ou tela_gestor.py se o role for "gestor" 
            if user_role == "pesquisador":
                st.switch_page("pages/tela_pesquisador.py")
            elif user_role == "gestor":
                st.switch_page("pages/tela_gestor.py")
        else:
            st.sidebar.write(f"Usuário sem permissões")

        if st.sidebar.button("Logout"):
            st.session_state["credentials"] = None
            st.session_state.pop("state", None)
            st.switch_page("tela_inicial.py")
    else:
        st.sidebar.error("Erro ao carregar informações do usuário.")
else:
    if st.sidebar.button(":key: Fazer Login com Google"):
        if not get_credentials():
            authenticate()



# Tela Inicial
if page == "Tela Inicial":
    st.title("Consulta de Preços de Veículos")
    st.subheader("Preencha os campos abaixo")

    # Recupera as marcas diretamente do banco
    marcas = get_brands()
    marca_selecionada = st.selectbox("Marca", ["Escolha uma marca"] + marcas, key="marca_selecionada")

    # Quando a marca for selecionada, carrega os modelos dessa marca
    if marca_selecionada != "Escolha uma marca":
        modelos = get_models_by_brand(marca_selecionada)
        if modelos:  # Verifica se existem modelos para a marca selecionada
            modelo_selecionado = st.selectbox("Modelo", ["Escolha um modelo"] + modelos, key="modelo_selecionado")
        else:
            st.warning("Não há modelos disponíveis para a marca selecionada.")  # Aviso caso não haja modelos
            modelo_selecionado = None  # Caso não haja modelos, o campo é ocultado
    else:
        modelo_selecionado = None  # Caso nenhum modelo tenha sido selecionado

    # Lista de "Ano/Modelo" a ser exibida de acordo com o modelo
    if modelo_selecionado and marca_selecionada:
        ano_modelo = get_years_by_model(marca_selecionada, modelo_selecionado)
    else:
        ano_modelo = []
    ano_selecionado = st.selectbox("Ano/Modelo", ["Escolha um ano/modelo"] + ano_modelo, key="ano_selecionado_inicial")

    # Verifica se todos os campos foram selecionados corretamente
    if st.button("Pesquisar"):
        if modelo_selecionado and marca_selecionada and ano_selecionado:
            chave_veiculo = f"{marca_selecionada} - {modelo_selecionado} ({ano_selecionado})"

            # Exibe o preço médio do veículo
            avg_price = get_vehicle_price_avg(marca_selecionada, modelo_selecionado, ano_selecionado)
            if avg_price is None:
                avg_price = 0.0  # Se não houver preço médio, exibe 0,00

            st.write(f"**Preço Médio do {marca_selecionada} - {modelo_selecionado} ({ano_selecionado}):** R$ {avg_price:.2f}.")# (calculado a partir de {count} registros).")
        else:
            st.warning("Por favor, selecione uma marca, um modelo e um ano/modelo.")



if page == "Consulta por período":
    st.title("Consulta de Preços de Veículos")
    st.subheader("Preencha os campos abaixo")

    # Recupera as marcas diretamente do banco
    brands = get_brands()
    selected_brand_period = st.selectbox("Marca", ["Escolha uma marca"] + brands, key="selected_brand_period")

    # Inicializa as variáveis antes do uso para evitar erros
    select_model_period = None  
    selected_year_period = None

    # Quando a marca for selecionada, carrega os modelos dessa marca
    if selected_brand_period != "Escolha uma marca":
        modelos = get_models_by_brand(selected_brand_period)
        if modelos:  
            select_model_period = st.selectbox("Modelo", ["Escolha um modelo"] + modelos, key="select_model_period")
        else:
            st.warning("Não há modelos disponíveis para a marca selecionada.")  

    # Lista de "Ano/Modelo" a ser exibida de acordo com o modelo
    if select_model_period:
        year_model_period = get_years_by_model(selected_brand_period, select_model_period)
    else:
        year_model_period = []
    
    selected_year_period = st.selectbox("Ano/Modelo", ["Escolha um ano/modelo"] + year_model_period, key="selected_year_period")

    # Adicionando apenas o seletor de período de tempo
    st.subheader("Selecionar Período")

    # Seletor de datas corrigido
    period = st.date_input(
        "Selecione o Período",
        [date.today().replace(day=1), date.today()],  # Define um intervalo padrão
        format="DD/MM/YYYY"
    )

    # Garante que data_inicial e data_final sejam sempre válidas
    if isinstance(period, tuple) or isinstance(period, list):  # Caso o usuário selecione duas datas
        if len(period) == 2:
            start_date_period, end_date_period = period
        elif len(period) == 1:  # Se apenas uma data for escolhida
            start_date_period, end_date_period = period[0], period[0]
    else:
        start_date_period, end_date_period = None, None  # Nenhuma data válida foi selecionada

    if start_date_period and end_date_period:
        st.write(f"**Período selecionado:** {start_date_period} até {end_date_period}")
    
    
    # Inicializa avg_price para evitar erro caso o usuário tente salvar antes de pesquisar
    avg_price = None  

    

    if st.button("Pesquisar"):
        if select_model_period and selected_brand_period and selected_year_period:
            chave_veiculo = f"{selected_brand_period} - {select_model_period} ({selected_year_period})"
            
            avg_price = get_vehicle_price_avg_period(
                selected_brand_period, select_model_period, selected_year_period, 
                start_date_period, end_date_period
            )

            if avg_price is None:
                st.warning("Não há registros para este período.")
                avg_price = 0.0 

            # Armazena o preço médio na sessão do Streamlit
            st.session_state.avg_price = avg_price  

            st.write(f"**Preço Médio do {selected_brand_period} - {select_model_period} ({selected_year_period}):** R$ {avg_price:.2f}")
        else:
            st.warning("Por favor, selecione uma marca, um modelo e um ano/modelo.")



        # Campo para salvar consulta (key diferente)
    user_email = st.text_input("Digite seu e-mail para salvar a consulta:", key="user_email_periodo_salvar")

    if st.button("Salvar Consulta"):
        avg_price = st.session_state.get("avg_price", None)  

        if avg_price is None:
            st.warning("Você precisa primeiro pesquisar o preço antes de salvar.")
        elif not user_email:
            st.warning("Por favor, insira um e-mail para salvar a consulta.")
        else:
            save_period_query(user_email, selected_brand_period, select_model_period,
                            selected_year_period, str(start_date_period), str(end_date_period), float(avg_price))  
            
            st.success(f"Consulta salva com sucesso para {user_email}!")

    #Campo separado para consultar pesquisas salvas (key diferente)
    user_email_query = st.text_input("Digite seu e-mail para visualizar suas últimas consultas:", key="user_email_periodo_consultar")

    
    if st.button("Carregar Últimas Consultas"):
        if user_email_query:
            consultas = get_last_saved_queries(user_email_query)

            if consultas:
                dados_tabela = []

                for consulta in consultas:
                    marca, modelo, ano, start_date, end_date, avg_price_data, created_at = consulta
                    
                    # Converte JSON de preços médios para dicionário se necessário
                    avg_price_data = json.loads(avg_price_data) if isinstance(avg_price_data, str) else avg_price_data

                    # 🔹 Verifica se a consulta é de período (média única) ou de gráfico (múltiplos valores)
                    if "média" in avg_price_data:
                        avg_price_str = f"R$ {float(avg_price_data['média']):,.2f}"
                    else:
                        avg_price_str = ", ".join([f"{mes}: R$ {float(valor):,.2f}" for mes, valor in avg_price_data.items() if isinstance(valor, (int, float))])

                    # Adiciona os dados na tabela
                    dados_tabela.append({
                        "Veículo": f"{marca} {modelo} ({ano})",
                        "Período": f"{start_date} até {end_date}",
                        "Preço Médio": avg_price_str,
                        "Salva em": created_at.strftime('%d/%m/%Y %H:%M')
                    })

                # Converte a lista em um DataFrame do Pandas
                df_consultas = pd.DataFrame(dados_tabela)

                # Exibe os dados formatados como tabela no Streamlit
                st.dataframe(df_consultas)

            else:
                st.warning("Nenhuma consulta encontrada para esse e-mail.")
        else:
            st.warning("Por favor, insira um e-mail para buscar as consultas.")


if page == "Gráfico Mensal":
    st.title("Consulta de Preços de Veículos")
    st.subheader("Preencha os campos abaixo")

    # Recupera as brands diretamente do banco
    brands = get_brands()
    selected_brand_graph = st.selectbox("Marca", ["Escolha uma marca"] + brands, key="selected_brand_graph")

    # Inicializa as variáveis antes do uso para evitar erros
    selected_model_graph = None  
    selected_year_graph = None

    # Quando a marca for selecionada, carrega os modelos dessa marca
    if selected_brand_graph != "Escolha uma marca":
        models = get_models_by_brand(selected_brand_graph)
        if models:  
            selected_model_graph = st.selectbox("Modelo", ["Escolha um modelo"] + models, key="selected_model_graph")
        else:
            st.warning("Não há modelos disponíveis para a marca selecionada.")  

    # Lista de "Ano/Modelo" a ser exibida de acordo com o modelo
    if selected_model_graph:
        selected_year_graph = get_years_by_model(selected_brand_graph, selected_model_graph)
    else:
        selected_year_graph = []
    
    selected_year_graph = st.selectbox("Ano/Modelo", ["Escolha um ano/modelo"] + selected_year_graph, key="selected_year_graph")

    # Adicionando apenas o seletor de período de tempo
    st.subheader("Selecionar Período")

    # Seletor de datas corrigido
    period = st.date_input(
        "Selecione o Período",
        [date.today().replace(day=1), date.today()],  # Define um intervalo padrão
        format="DD/MM/YYYY"
    )

    if isinstance(period, (tuple, list)) and len(period) == 2:
        start_date_period, end_date_period = period
    elif isinstance(period, (tuple, list)) and len(period) == 1:
        start_date_period, end_date_period = period[0], period[0]
    else:
        start_date_period, end_date_period = None, None

    if start_date_period and end_date_period:
        st.write(f"**Período selecionado:** {start_date_period} até {end_date_period}")
        

    if "grafico_gerado" not in st.session_state:
        st.session_state.grafico_gerado = False
    
    if st.button("Gerar Gráfico"):
        if selected_model_graph and selected_brand_graph and selected_year_graph:
            chave_veiculo = f"{selected_brand_graph} - {selected_model_graph} ({selected_year_graph})"
            vehicle_id = get_vehicle_id_for_graph(selected_brand_graph, selected_model_graph, selected_year_graph)
            if vehicle_id:
                data = get_vehicle_price_avg_graph(vehicle_id, start_date_period, end_date_period)
                if data:
                    df = pd.DataFrame(data, columns=["Data", "Preço Médio"])
                    st.session_state.df = df  
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.scatter(df["Data"], df["Preço Médio"], color='b', label="Preço Médio")
                    ax.set_xticks(df["Data"])
                    ax.set_xticklabels(df["Data"].dt.strftime('%b/%Y'), rotation=45)
                    ax.set_xlabel("Mês/Ano")
                    ax.set_ylabel("Preço Médio (R$)")
                    ax.set_title(f"Variação de Preço do {chave_veiculo} por Mês")
                    ax.grid(True)
                    st.pyplot(fig)
                    st.session_state.grafico_gerado = True
                else:
                    st.warning("Não há registros para este período.")
            else:
                st.warning("Erro!!")
        else:
            st.warning("Por favor, selecione uma marca, um modelo e um ano/modelo.")
    
    
    user_email = st.text_input("Digite seu e-mail para salvar a consulta:", key="user_email")

    if st.button("Salvar Consulta"):

        if "df" in st.session_state and st.session_state.df is not None:
            df = st.session_state.df  
            if user_email:
                # Converte os valores de 'Decimal' para 'float' para evitar erro ao salvar no JSON
                avg_price_data = {row["Data"].strftime("%Y-%m"): float(row["Preço Médio"]) for _, row in df.iterrows()}
                
                # Chama a função que salva no banco de dados
                save_graph_query(user_email, selected_brand_graph, selected_model_graph,
                                selected_year_graph, str(start_date_period), str(end_date_period), avg_price_data)
                
                st.success(f"Consulta salva com sucesso para {user_email}!")
            else:
                st.warning("Por favor, insira um e-mail para salvar a consulta.")
        else:
            st.warning("Você precisa gerar o gráfico antes de salvar a consulta.")



    st.subheader("Consultar Últimas Pesquisas Salvas")

    user_email_query = st.text_input("Digite seu e-mail para visualizar suas últimas consultas:", key="user_email_query")

    if st.button("Carregar Últimas Consultas"):
        if user_email_query:
            queries = get_last_saved_queries(user_email_query)

            if queries:
                table_data = []

                for query in queries:
                    marca, modelo, ano, start_date, end_date, avg_price_data, created_at = query
                    
                    # Converte JSON de preços médios para dicionário se necessário
                    avg_price_data = json.loads(avg_price_data) if isinstance(avg_price_data, str) else avg_price_data

                    # Verifica se a consulta é de período (média única) ou de gráfico (múltiplos valores)
                    if "média" in avg_price_data:
                        avg_price_str = f"R$ {float(avg_price_data['média']):,.2f}"
                    else:
                        avg_price_str = ", ".join([f"{mes}: R$ {float(valor):,.2f}" for mes, valor in avg_price_data.items() if isinstance(valor, (int, float))])

                    # Adiciona os dados na tabela
                    table_data.append({
                        "Veículo": f"{marca} {modelo} ({ano})",
                        "Período": f"{start_date} até {end_date}",
                        "Preço Médio": avg_price_str,
                        "Salva em": created_at.strftime('%d/%m/%Y %H:%M')
                    })

                # Converte a lista em um DataFrame do Pandas
                df_queries = pd.DataFrame(table_data)

                # Exibe os dados formatados como tabela no Streamlit
                st.dataframe(df_queries)

            else:
                st.warning("Nenhuma consulta encontrada para esse e-mail.")
        else:
            st.warning("Por favor, insira um e-mail para buscar as consultas.")