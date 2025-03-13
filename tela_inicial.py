import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os
from db_connection import create_connection
import psycopg2
from datetime import datetime

# Configurações do Google OAuth
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
REDIRECT_URI = "http://localhost:8501"
CLIENT_SECRETS_FILE = "client_secret.json"

# Função para recuperar as lojas do banco de dados
def get_lojas():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name, street, number, neighborhood, city, state, cep 
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

# Função para recuperar as marcas do banco de dados
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

# Função para calcular o preço médio do veículo
def get_vehicle_price_avg(brand_name, model_name, year):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(price), COUNT(*) 
        FROM vehicle_prices_table
        JOIN models_table ON vehicle_prices_table.id_model = models_table.id_model
        JOIN brands_table ON models_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s AND models_table.name = %s AND vehicle_prices_table.year_mod = %s
    """, (brand_name, model_name, year))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0], result[1]  # Average price and count of records
    return None, 0

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
        conn = db_connection.create_connection()
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

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial"], key="navegacao_radio")

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
        else:
            st.sidebar.write(f"Usuário sem permissões")

        if st.sidebar.button("Logout"):
            st.session_state["credentials"] = None
            st.session_state.pop("state", None)
            st.rerun()
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
            avg_price, count = get_vehicle_price_avg(marca_selecionada, modelo_selecionado, ano_selecionado)
            if avg_price is None:
                avg_price = 0.0  # Se não houver preço médio, exibe 0,00

            st.write(f"**Preço Médio do {marca_selecionada} - {modelo_selecionado} ({ano_selecionado}):** R$ {avg_price:.2f} (calculado a partir de {count} registros).")
        else:
            st.warning("Por favor, selecione uma marca, um modelo e um ano/modelo.")
