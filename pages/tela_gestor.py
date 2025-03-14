import streamlit as st
import requests
import psycopg2
from databases.db_connection import create_connection
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
        SELECT DISTINCT year_mod 
        FROM vehicles_table
        JOIN models_table ON vehicles_table.id_model = models_table.id_model
        JOIN brands_table ON models_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s AND models_table.name = %s
        ORDER BY year_mod DESC
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
    SELECT AVG(avg_price), COUNT(*)
    FROM vehicles_table
    JOIN models_table ON vehicles_table.id_model = models_table.id_model
    JOIN brands_table ON models_table.id_brand = brands_table.id_brand
    WHERE brands_table.name = %s AND models_table.name = %s AND vehicles_table.year_mod = %s
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
def insert_pesquisador(name, email, role):
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users_table (name, email, role) 
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING id_user -- Retorna o ID do usuário se a inserção ocorreu
    """, (name, email, role))

    inserted = cursor.fetchone()
    
    conn.commit()
    cursor.close()
    conn.close()

    return inserted is not None

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

# Tela Inicial
if page == "Tela Inicial":
    st.title("Consulta de Preços de Veículos")
    st.subheader("Preencha os campos abaixo e clique em 'Pesquisar'")

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

    # Quando uma marca ou modelo for selecionado, carrega os anos/modelos disponíveis
    if modelo_selecionado or marca_selecionada != "Escolha uma marca":
        anos_modelos = get_years_by_model(marca_selecionada, modelo_selecionado)
        if anos_modelos:  # Verifica se há anos/modelos disponíveis
            ano_modelo_selecionado = st.selectbox("Ano/Modelo", ["Escolha um ano/modelo"] + anos_modelos, key="ano_modelo_selecionado")
        else:
            ano_modelo_selecionado = None  # Caso não haja anos/modelos, o campo é ocultado
    else:
        ano_modelo_selecionado = None  # Caso nem marca nem modelo tenha sido selecionado

    # Adiciona o botão "Pesquisar"
    if st.button("Pesquisar"):
        # Verifica se todos os campos foram preenchidos
        if marca_selecionada != "Escolha uma marca" and modelo_selecionado and ano_modelo_selecionado:
            # Chama a função para calcular o preço médio
            preco_medio, count = get_vehicle_price_avg(marca_selecionada, modelo_selecionado, ano_modelo_selecionado)
            if preco_medio:
                # Exibe o preço médio do veículo
                st.write(f"Preço médio para {marca_selecionada} {modelo_selecionado} {ano_modelo_selecionado}: R$ {preco_medio:,.2f} ({count} registros)")
            else:
                st.warning("Não há registros suficientes para calcular o preço médio.")
        else:
            st.warning("Por favor, selecione todos os campos antes de pesquisar.")

# Área do Gestor
elif page == "Área do Gestor":
    st.title("Área do Gestor")
    
    # Cadastro de Pesquisador
    st.subheader("Cadastrar Usuário")
    nome_pesquisador = st.text_input("Nome do Pesquisador", key="nome_pesquisador")
    email_pesquisador = st.text_input("E-mail do Pesquisador", key="email_pesquisador")
    role_usuario = st.selectbox("Permissão", ["gestor", "pesquisador"], key="role_usuario")
     
    # Exibindo o botão de cadastro
    if st.button("Cadastrar Usuário"):
        if insert_pesquisador(nome_pesquisador, email_pesquisador, role_usuario):
            st.session_state.pesquisadores.append((nome_pesquisador, email_pesquisador, role_usuario))
            st.write(f"Usuário {nome_pesquisador} ({email_pesquisador}) cadastrado com sucesso como {role_usuario}.")
        else:
            st.warning(f"O usuário com o e-mail {email_pesquisador} já existe no sistema.")
    
    # Cadastro de Loja
    st.subheader("Cadastrar Loja")
    nome_loja = st.text_input("Nome da Loja", key="nome_loja")
    rua_loja = st.text_input("Rua", key="rua_loja")
    bairro_loja = st.text_input("Bairro", key="bairro_loja")
    numero_loja = st.text_input("Número", key="numero_loja")
    cidade_loja = st.text_input("Cidade", key="cidade_loja")
    estado_loja = st.selectbox("Estado", sorted(estados_dict.keys()), key="estado_loja")
    cep_loja = st.text_input("CEP", key="cep_loja")

    # Exibindo o botão de cadastro
    if st.button("Cadastrar Loja"):
        insert_loja(nome_loja, rua_loja, bairro_loja, numero_loja, cidade_loja, estado_loja, cep_loja)
        st.write(f"Loja {nome_loja} cadastrada com sucesso.")
    
    # Atribuição de Pesquisador a Loja
    gestores = get_pesquisadores()  # Supondo que a função `get_pesquisadores` também retorne os gestores
    gestor_selecionado = st.selectbox("Escolha o Gestor", ["Escolha o gestor"] + [gestor[0] for gestor in gestores])
    pesquisador_selecionado = st.selectbox("Escolha o Pesquisador", ["Escolha o pesquisador"] + [pesquisador[0] for pesquisador in st.session_state.pesquisadores])
    loja_selecionada = st.selectbox("Escolha a Loja", ["Escolha a loja"] + st.session_state.lojas_registradas)

    # Função para atribuir um pesquisador a uma loja
    def assign_researcher_to_store(pesquisador_nome, loja_nome, gestor_nome):
        conn = create_connection()
        cursor = conn.cursor()

        # Verificar se o gestor está no banco de dados
        cursor.execute("""
            SELECT id_user FROM users_table WHERE name = %s AND role = 'gestor'
        """, (gestor_nome,))
        gestor_id = cursor.fetchone()

        # Se o gestor existe, atribuir pesquisador à loja
        if gestor_id:
            cursor.execute("""
                SELECT id_user FROM users_table WHERE name = %s AND role = 'gestor'
            """, (gestor_nome,))
            conn.commit()
            st.write(f"Pesquisador(a) {pesquisador_nome} foi atribuído à Loja {loja_nome} pelo(a) Gestor(a) {gestor_nome}.")
        
        # Exibe o botão para atribuir pesquisador à loja
    if st.button("Atribuir Pesquisador à Loja"):
        if pesquisador_selecionado != "Escolha o pesquisador" and loja_selecionada != "Escolha a loja" and gestor_selecionado != "Escolha o gestor":
            assign_researcher_to_store(pesquisador_selecionado, loja_selecionada, gestor_selecionado)
        else:
            st.warning("Por favor, selecione um pesquisador, uma loja e um gestor.")













