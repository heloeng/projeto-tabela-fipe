import streamlit as st
import requests
from db_connection import create_connection
from datetime import datetime

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
    
    return [model[0] for model in models]

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

# Função para registrar uma nova marca no banco de dados
def insert_brand(brand_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO brands_table (name) 
        SELECT %s 
        WHERE NOT EXISTS (SELECT 1 FROM brands_table WHERE name = %s)
    """, (brand_name, brand_name))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função para inserir um novo modelo
def insert_model(model_name, brand_name):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO models_table (name, id_brand)
        SELECT %s, id_brand FROM brands_table WHERE name = %s
        ON CONFLICT (name, id_brand) DO NOTHING
    """, (model_name, brand_name))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função para recuperar as lojas do banco de dados
def get_lojas():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM stores_table")
    lojas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [loja[0] for loja in lojas]

# Função para recuperar os pesquisadores do banco de dados
def get_pesquisadores():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, email FROM users_table")
    pesquisadores = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [(pesquisador[0], pesquisador[1]) for pesquisador in pesquisadores]

# Função para adicionar um novo pesquisador
def insert_pesquisador(name, email):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users_table (name, email) 
        VALUES (%s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (name, email))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função para adicionar uma nova loja
def insert_loja(name, street, neighborhood, number, city, state, cep):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO stores_table (name, street, neighborhood, number, city, state, cep)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (name, street, neighborhood, number, city, state, cep))
    
    conn.commit()
    cursor.close()
    conn.close()

# Dados do estado e cidade
estados = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados").json()
estados_dict = {estado["sigla"]: estado["id"] for estado in estados}

# Armazenamento de informações no estado da sessão
if 'precos_registrados' not in st.session_state:
    st.session_state.precos_registrados = {}
if 'pesquisadores_lojas' not in st.session_state:
    st.session_state.pesquisadores_lojas = []  
if 'lojas_registradas' not in st.session_state:
    st.session_state.lojas_registradas = get_lojas()  # Carrega as lojas do banco de dados
if 'pesquisadores' not in st.session_state:
    st.session_state.pesquisadores = get_pesquisadores()  # Carrega os pesquisadores do banco de dados

st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Área do Gestor"], key="navegacao_radio")

if st.sidebar.button("Logout"):
    st.write("Você clicou em Logout!")

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

elif page == "Área do Gestor":
    st.title("Área do Gestor")
    
    # Cadastro de Pesquisador
    st.subheader("Cadastrar Pesquisador")
    nome_pesquisador = st.text_input("Nome do Pesquisador", key="nome_pesquisador")
    email_pesquisador = st.text_input("E-mail do Pesquisador", key="email_pesquisador")
    
    if st.button("Cadastrar Pesquisador"):
        if nome_pesquisador and email_pesquisador:
            if email_pesquisador not in [pesquisador[1] for pesquisador in st.session_state.pesquisadores]:
                insert_pesquisador(nome_pesquisador, email_pesquisador)
                st.session_state.pesquisadores.append((nome_pesquisador, email_pesquisador))
                st.success(f"Pesquisador {nome_pesquisador} cadastrado com sucesso!")
            else:
                st.error(f"Pesquisador com e-mail {email_pesquisador} já cadastrado.")
        else:
            st.error("Por favor, insira o nome e e-mail válidos para o pesquisador.")
    
    # Exibir lista de pesquisadores cadastrados
    st.subheader("Pesquisadores Cadastrados")
    if st.session_state.pesquisadores:
        for pesquisador in st.session_state.pesquisadores:
            st.write(f"{pesquisador[0]} - {pesquisador[1]}")
    else:
        st.write("Nenhum pesquisador cadastrado.")

        # Função para adicionar um novo gestor
def insert_gestor(name, email):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users_table (name, email, role) 
        VALUES (%s, %s, 'Gestor')
        ON CONFLICT (email) DO NOTHING
    """, (name, email))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função para adicionar gestor ao banco de dados
def insert_gestor(name, email):
    conn = create_connection()
    cursor = conn.cursor()
    
    role = 'gestor'  # Papel do gestor
    
    cursor.execute("""
        INSERT INTO users_table (name, email, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (name, email, role))
    
    conn.commit()
    cursor.close()
    conn.close()

# Inicializar a lista de gestores no session_state, se ainda não existir
if 'gestores' not in st.session_state:
    st.session_state.gestores = []

# Cadastro de Gestor
st.subheader("Cadastrar Gestor")
nome_gestor = st.text_input("Nome do Gestor", key="nome_gestor")
email_gestor = st.text_input("E-mail do Gestor", key="email_gestor")

if st.button("Cadastrar Gestor"):
    if nome_gestor and email_gestor:
        # Verificar se o e-mail já está na lista de gestores cadastrados
        if email_gestor not in [gestor[1] for gestor in st.session_state.gestores]:
            insert_gestor(nome_gestor, email_gestor)
            st.session_state.gestores.append((nome_gestor, email_gestor))  # Adiciona o novo gestor à lista
            st.success(f"Gestor {nome_gestor} cadastrado com sucesso!")
        else:
            st.error(f"Gestor com e-mail {email_gestor} já cadastrado.")
    else:
        st.error("Por favor, insira o nome e e-mail válidos para o gestor.")

# Exibir lista de gestores cadastrados
st.subheader("Gestores Cadastrados")
if st.session_state.gestores:
    for gestor in st.session_state.gestores:
        st.write(f"{gestor[0]} - {gestor[1]}")
else:
    st.write("Nenhum gestor cadastrado.")
    
    # Cadastro de Loja
    st.subheader("Cadastrar Loja")
    nome_loja = st.text_input("Nome da Loja", key="nome_loja")
    rua_loja = st.text_input("Rua", key="rua_loja")
    bairro_loja = st.text_input("Bairro", key="bairro_loja")
    numero_loja = st.text_input("Número", key="numero_loja")
    cidade_loja = st.text_input("Cidade", key="cidade_loja")
    estado_loja = st.selectbox("Estado", ["Escolha um estado"] + list(estados_dict.keys()), key="estado_loja")
    cep_loja = st.text_input("CEP", key="cep_loja")

    if st.button("Cadastrar Loja"):
        if nome_loja and rua_loja and bairro_loja and numero_loja and cidade_loja and estado_loja != "Escolha um estado" and cep_loja:
            insert_loja(nome_loja, rua_loja, bairro_loja, numero_loja, cidade_loja, estado_loja, cep_loja)
            st.session_state.lojas_registradas.append(nome_loja)
            st.success(f"Loja {nome_loja} cadastrada com sucesso!")
        else:
            st.error("Por favor, insira todos os dados da loja.")

    # Exibir lista de lojas cadastradas
    st.subheader("Lojas Cadastradas")
    if st.session_state.lojas_registradas:
        for loja in st.session_state.lojas_registradas:
            st.write(loja)
    else:
        st.write("Nenhuma loja cadastrada.")
