import streamlit as st
from databases.db_connection import create_connection
from tela_inicial import get_user_role
from tela_inicial import get_user_info
from tela_inicial import get_credentials
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import psycopg2
from datetime import datetime

# Função para recuperar as cadeias de lojas
def get_chains():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_chain, chain_name FROM store_chains_table")
    chains = cursor.fetchall()
    cursor.close()
    conn.close()
    return [chain[1] for chain in chains]

# Função para associar loja a cadeia
def associate_store_to_chain(store_id, chain_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_chain FROM store_chains_table WHERE chain_name = %s", (chain_name,))
    chain_id = cursor.fetchone()
    
    if chain_id is None:
        st.error(f"Cadeia de loja '{chain_name}' não encontrada.")
        return
    
    # Verificando se a loja já está associada à cadeia
    cursor.execute("SELECT * FROM store_chains_table WHERE store_id = %s AND chain_name = %s", (store_id, chain_name))
    if cursor.fetchone():
        st.warning(f"A loja '{store_id}' já está associada à cadeia '{chain_name}'.")
        return
    
    cursor.execute("INSERT INTO store_chains_table (store_id, chain_name) VALUES (%s, %s)", (store_id, chain_name))
    conn.commit()
    cursor.close()
    conn.close()
    st.success(f"Loja associada à cadeia '{chain_name}' com sucesso!")
    
    # Função para exibir a variação do preço médio mensal
def get_price_variation_by_month(chain_name, start_date, end_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT v.avg_price, v.calc_date
    FROM vehicles_table v
    JOIN stores_table s ON v.store_id = s.id_store
    LEFT JOIN store_chains_table sc ON s.id_store = sc.store_id
    WHERE sc.chain_name = %s
    AND v.calc_date BETWEEN %s AND %s
    ORDER BY v.calc_date;
""", (chain_name, start_date, end_date))
    
    prices = cursor.fetchall()
    cursor.close()
    conn.close()
    return prices

# Função para mostrar o gráfico de variação de preços com linha conectando os pontos
def show_price_variation_graph(prices):
    if not prices:
        st.warning("Não há dados de preço para o intervalo selecionado.")
        return
    
    # Criação do DataFrame com preços e datas
    df = pd.DataFrame(prices, columns=["price", "date"])
    df['date'] = pd.to_datetime(df['date'])  # Garantir que as datas sejam do tipo datetime
    df.sort_values(by='date', inplace=True)  # Garantir que os dados estão ordenados por data

    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plotando a linha conectando os pontos com preço
    ax.plot(df['date'], df['price'], marker='o', linestyle='-', color='b', label="Variação de Preço")

    # Título e rótulos
    ax.set_title('Variação de Cotação de Preço', fontsize=16)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Preço Médio (R$)', fontsize=12)
    
    # Formatação do eixo X para mostrar mês/ano
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    # Rótulos do eixo X
    plt.xticks(rotation=45)

    # Legenda
    ax.legend()

    # Exibição do gráfico
    st.pyplot(fig)

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
def register_vehicle_price(marca, modelo, loja_id, preco, ano):
    conn = create_connection()
    cursor = conn.cursor()

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

# Função para calcular o preço médio do veículo
def get_vehicle_price_avg(brand_name, model_name):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(price), COUNT(*) 
        FROM vehicle_prices_table
        JOIN models_table ON vehicle_prices_table.id_model = models_table.id_model
        JOIN brands_table ON models_table.id_brand = brands_table.id_brand
        WHERE brands_table.name = %s AND models_table.name = %s
    """, (brand_name, model_name))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and result[0] is not None:
        return result[0], result[1]  # Preço médio, contagem de registros
    return None, 0  # Caso não haja dados

# Armazenamento de informações no estado da sessão
if 'lojas_registradas' not in st.session_state:
    st.session_state.lojas_registradas = get_lojas()  # Carrega as lojas do banco de dados

st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Área do Pesquisador", "Registrar Veículo", "P1 - Heloiza", "P2 - João Marcelo", "P3 - Samuel", "P4 - Sofia", "P5 - Vitor"], key="navegacao_radio")

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
            avg_price, count = get_vehicle_price_avg(marca_selecionada, modelo_selecionado)
            if avg_price is None:
                avg_price = 0.0  # Se não houver preços registrados, o valor será 0
            st.write(f"O preço médio para {chave_veiculo} é R${avg_price:.2f}, com {count} registros.")

        else:
            st.warning("Por favor, preencha todos os campos para realizar a pesquisa.")

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
            
# P1- Heloiza
if page == "P1 - Heloiza":
    st.title("P1 - Heloiza")
    st.subheader("Testes")
    
# P2 - João Marcelo
if page == "P2 - João Marcelo":
    st.title("P2 - João Marcelo")
    st.subheader("Testes")
    
# P3 - Samuel
if page == "P3 - Samuel":
    st.title("P3 - Samuel")
    st.subheader("Testes")

    # Consulta Gráfica da Variação de Cotação Média Mensal
    st.header("Consulta Gráfica de Variação de Preço")

    # Selecione a cadeia de loja
    chains = list(set(get_chains()))  # Remover duplicatas
    selected_chain = st.selectbox("Selecione uma Cadeia de Loja", ["Escolha uma cadeia"] + chains)

    if selected_chain != "Escolha uma cadeia":
        # Selecione o período
        start_date = st.date_input("Data Inicial", min_value=datetime(2000, 1, 1))
        end_date = st.date_input("Data Final", min_value=datetime(2000, 1, 1))

        if start_date and end_date and start_date <= end_date:
            if st.button("Consultar Variação"):
                prices = get_price_variation_by_month(selected_chain, start_date, end_date)
                show_price_variation_graph(prices)
        else:
            st.warning("Selecione um período válido.")

    # Cadastro de Cadeia de Loja
    st.header("Cadastro de Cadeia de Loja")
    chain_name = st.text_input("Nome da Cadeia de Loja")
    
    if st.button("Cadastrar Cadeia"):
        if chain_name:
            try:
                conn = create_connection()
                cursor = conn.cursor()

                # Buscar o maior id_store para gerar o próximo
                cursor.execute("SELECT MAX(id_store) FROM stores_table")
                max_id = cursor.fetchone()[0]
                new_store_id = max_id + 1 if max_id is not None else 1

                # Adicionar um nome fictício para a loja, caso não tenha dados
                store_name = "Loja " + str(new_store_id)
                store_city = "Cidade Fictícia"
                store_state = "Estado Fictício"

                # Inserir dados na tabela stores_table (incluindo nome da loja)
                cursor.execute("""
                    INSERT INTO stores_table (id_store, name, city, state)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id_store) DO NOTHING
                """, (new_store_id, store_name, store_city, store_state))

                # Inserir a cadeia de loja na tabela store_chains_table
                cursor.execute("""
                    INSERT INTO store_chains_table (store_id, chain_name)
                    VALUES (%s, %s)
                """, (new_store_id, chain_name))

                # Confirmar a transação no banco de dados
                conn.commit()

                cursor.close()
                conn.close()

                st.success(f"Cadeia de loja '{chain_name}' cadastrada com sucesso!")
            except Exception as e:
                # Reverter transações em caso de erro
                conn.rollback()
                st.error(f"Erro ao cadastrar a cadeia de loja: {str(e)}")
        else:
            st.warning("Preencha o nome da cadeia.")

    # Associação de loja a cadeia
    st.header("Associação de Loja a Cadeia")
    
    # Verifica se há lojas registradas em st.session_state
    if 'lojas_registradas' in st.session_state:
        loja_id = st.selectbox("Selecione a Loja", list(set([loja['nome'] for loja in st.session_state.lojas_registradas])) )  # Remover duplicatas
        chain_to_associate = st.selectbox("Selecione a Cadeia", chains)

        if st.button("Associar Loja à Cadeia"):
            try:
                # Busca o ID da loja a partir do nome
                store_id = next(loja['id'] for loja in st.session_state.lojas_registradas if loja['nome'] == loja_id)
                # Chama a função para associar loja à cadeia
                associate_store_to_chain(store_id, chain_to_associate)
            except Exception as e:
                st.error(f"Erro ao associar loja à cadeia: {e}")
    else:
        st.warning("Não há lojas registradas para associar.")
    
# P4 - Sofia
if page == "P4 - Sofia":
    st.title("P4 - Sofia")
    st.subheader("Testes")
    
# P5 - Vitor
if page == "P5 - Vitor":
    st.title("P5 - Vitor")
    st.subheader("Testes")
