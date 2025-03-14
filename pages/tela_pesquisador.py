import streamlit as st
from databases.db_connection import create_connection
from tela_inicial import get_user_role, get_user_info, get_credentials
import psycopg2
from datetime import datetime
from decimal import Decimal

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

# Função para registrar o veículo manualmente
def register_vehicle(marca, modelo, ano, preco_base):
    conn = create_connection()
    cursor = conn.cursor()

    # Verifica se a marca já existe antes de tentar inseri-la
    cursor.execute("SELECT id_brand FROM brands_table WHERE name = %s", (marca,))
    id_brand = cursor.fetchone()
    if id_brand is None:
        # Se a marca não existir, cria uma nova
        cursor.execute("INSERT INTO brands_table (name) VALUES (%s)", (marca,))
        conn.commit()
        cursor.execute("SELECT id_brand FROM brands_table WHERE name = %s", (marca,))
        id_brand = cursor.fetchone()
        st.success(f"Marca '{marca}' registrada com sucesso!")
    else:
        st.info(f"A marca '{marca}' já existe.")

    # Verifica se o modelo já existe antes de tentar inseri-lo
    cursor.execute("SELECT id_model FROM models_table WHERE name = %s AND id_brand = %s", (modelo, id_brand[0]))
    id_model = cursor.fetchone()
    if id_model is None:
        # Se o modelo não existir, cria um novo
        cursor.execute("INSERT INTO models_table (name, id_brand) VALUES (%s, %s)", (modelo, id_brand[0]))
        conn.commit()
        cursor.execute("SELECT id_model FROM models_table WHERE name = %s AND id_brand = %s", (modelo, id_brand[0]))
        id_model = cursor.fetchone()
        st.success(f"Modelo '{modelo}' registrado com sucesso!")
    else:
        st.info(f"O modelo '{modelo}' já existe para a marca '{marca}'.")

    # Verifica se o veículo já está registrado (ano/modelo)
    cursor.execute("SELECT id_vehicle FROM vehicles_table WHERE id_model = %s AND year_mod = %s", (id_model[0], ano))
    existing_vehicle = cursor.fetchone()

    if existing_vehicle:
        st.warning(f"O veículo {modelo} {marca} ({ano}) já está registrado no banco de dados.")
    else:
        # Inserir o novo veículo no banco de dados
        try:
            cursor.execute(""" 
                INSERT INTO vehicles_table (id_model, id_brand, year_mod, avg_price) 
                VALUES (%s, %s, %s, %s)
            """, (id_model[0], id_brand[0], ano, preco_base))
            conn.commit()
            st.success(f"Veículo {modelo} {marca} ({ano}) registrado com sucesso!")
        except psycopg2.errors.UniqueViolation:
            st.warning(f"O veículo {modelo} {marca} ({ano}) já existe na base de dados. Não foi possível registrar novamente.")

    cursor.close()
    conn.close()

# Função para recuperar as marcas do banco de dados
def get_brands():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM brands_table")
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

# Função para registrar o preço do veículo
# Função para registrar o preço do veículo
def register_vehicle_price(marca, modelo, loja_id, preco, ano):
    conn = create_connection()
    cursor = conn.cursor()

    # Recupera o ID do modelo
    cursor.execute("SELECT id_model FROM models_table WHERE name = %s", (modelo,))
    id_model = cursor.fetchone()
    if id_model is None:
        st.error(f"Modelo '{modelo}' não encontrado.")
        return

    # Verifique se os dados de preço existem antes de calcular o novo valor
    if avg_price is not None and price_count is not None:
        new_avg_price = (avg_price * price_count + preco) / (price_count + 1)
    else:
    # Se não houver dados anteriores, o novo preço será o preço atual
        new_avg_price = preco

# Agora, faça o update com o novo valor de new_avg_price
    cursor.execute("""
    UPDATE vehicles_table v
    SET v.avg_price = %s, v.preco = %s
    FROM stores_table s
    WHERE v.id_model = %s 
      AND v.year_mod = %s 
      AND s.id_store = %s
      AND s.id_store = v.id_store
""", (new_avg_price, preco, id_model[0], ano, loja_id))

    existing_price_data = cursor.fetchone()  # Obtemos o preço médio e a quantidade de registros

    if existing_price_data and existing_price_data[0] is not None:
        avg_price = existing_price_data[0]
        price_count = existing_price_data[1]

        # Calculando o novo preço médio
        new_avg_price = (Decimal(avg_price) * Decimal(price_count) + Decimal(preco)) / (Decimal(price_count) + 1)

        # Atualiza o preço médio na tabela vehicles_table
        cursor.execute("""
        UPDATE vehicles_table
        SET avg_price = %s, preco = %s
        WHERE id_model = %s AND year_mod = %s AND store_id = %s  -- Ajuste conforme necessário
        """, (new_avg_price, preco, id_model[0], ano, loja_id))

        conn.commit()
        st.success(f"Preço atualizado! Nova média de preço para {modelo} ({ano}): R$ {new_avg_price:.2f}")
    else:
        # Se não houver preços registrados, insere o novo preço como o primeiro preço
        cursor.execute("""
        INSERT INTO vehicles_table (id_model, year_mod, preco, avg_price, store_id)  -- Ajuste conforme necessário
        VALUES (%s, %s, %s, %s, %s)
        """, (id_model[0], ano, preco, preco, loja_id))

        conn.commit()
        st.success(f"Preço registrado! Preço de {modelo} ({ano}): {preco:.2f}")

    cursor.close()
    conn.close()

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

# Armazenamento de informações no estado da sessão
if 'lojas_registradas' not in st.session_state:
    st.session_state.lojas_registradas = get_lojas()  # Carrega as lojas do banco de dados

st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Área do Pesquisador", "Registrar Veículo"], key="navegacao_radio_P")

st.sidebar.header("Acesso para colaboradores")
credentials = get_credentials()

if credentials and not credentials.expired:
    user_info = get_user_info(credentials)
    if user_info:
        user_email = user_info['email']
        user_role = get_user_role(user_email)

        st.sidebar.write(f"Bem-vindo(a), {user_info['name']} ({user_email})")
        if user_role:
            st.sidebar.markdown(f"Logado como **{user_role}**")
            if user_role != "pesquisador":
                st.switch_page("tela_inicial.py")
                st.error("Acesso negado: Apenas pesquisadores podem acessar esta página.")
        else:
            st.sidebar.write(f"Usuário sem permissões")
            st.switch_page("tela_inicial.py")

        if st.sidebar.button("Logout"):
            st.session_state["credentials"] = None
            st.session_state.pop("state", None)
            st.switch_page("tela_inicial.py")
else:
    st.switch_page("tela_inicial.py")
    st.error("Você precisa estar logado como pesquisador para acessar esta página.")

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

# Área do Pesquisador
if page == "Área do Pesquisador":
    st.title("Área do Pesquisador")
    st.subheader("Registro de Preços dos Veículos")

    # Escolher marca, modelo e ano
    marcas = get_brands()
    marca_selecionada = st.selectbox("Marca", marcas)

    if marca_selecionada:
        modelos = get_models_by_brand(marca_selecionada)
        modelo_selecionado = st.selectbox("Modelo", modelos)

        if modelo_selecionado:
            ano_modelo = get_years_by_model(marca_selecionada, modelo_selecionado)
            ano_selecionado = st.selectbox("Ano/Modelo", ano_modelo)

            lojas = [loja['nome'] for loja in st.session_state.lojas_registradas]
            loja_selecionada = st.selectbox("Loja", lojas)
            preco = st.number_input("Preço", min_value=0.0, format="%.2f")

            if st.button("Registrar Preço"):
                # Agora, a variável loja_selecionada é comparada corretamente com loja['nome']
                loja_id = next(loja['id'] for loja in st.session_state.lojas_registradas if loja['nome'] == loja_selecionada)
                register_vehicle_price(marca_selecionada, modelo_selecionado, loja_id, preco, ano_selecionado)

# Tela para registrar veículos
if page == "Registrar Veículo":
    st.title("Registrar Novo Veículo")

    marca = st.text_input("Marca")
    modelo = st.text_input("Modelo")
    ano = st.text_input("Ano/Modelo")
    preco_base = st.number_input("Preço Base", min_value=0.0, format="%.2f")

    if st.button("Registrar Veículo"):
        if marca and modelo and ano and preco_base:
            register_vehicle(marca, modelo, ano, preco_base)
        else:
            st.warning("Preencha todos os campos para registrar um novo veículo.")
