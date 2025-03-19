import streamlit as st
from databases.db_connection import create_connection
from tela_inicial import get_user_role, get_user_info, get_credentials
import psycopg2
from datetime import datetime
from decimal import Decimal
import re
import pandas as pd

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
def register_vehicle_price(usuario, loja, modelo, ano, preco):
    conn = create_connection()
    cursor = conn.cursor()

    # # Recupera o ID do modelo
    # cursor.execute("SELECT id_model FROM models_table WHERE name = %s", (modelo,))
    # id_model = cursor.fetchone()
    # if id_model is None:
    #     st.error(f"Modelo '{modelo}' não encontrado.")
    #     return


# Agora, faça o update com o novo registro
    cursor.execute("""
    INSERT INTO register_table(id_user, id_store, id_vehicle, year_man, price)
    VALUES (
    (SELECT id_user FROM users_table WHERE  email = %s LIMIT 1),
    (SELECT id_store FROM stores_table WHERE  name = %s),
    (SELECT id_vehicle FROM vehicles_table WHERE  year_mod = %s),
    %s,
    %s
    )
""", (usuario, loja, modelo, ano, preco))



    conn.commit()
    cursor.close()
    conn.close()

    #return inserted_reg is not None

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

# Função para buscar principais dados da tabela regiser_table
def get_register_data_by_plate():
    with create_connection() as conn:
        query = """
            SELECT r.plate, r.price, r.reg_date, s.name AS store_name
            FROM register_table r
            JOIN stores_table s ON r.id_store = s.id_store
            ORDER BY r.reg_date
        """
        df = pd.read_sql(query, conn)
    return df

def get_register_data_by_vehicle(brand_name, model_name, year):
    with create_connection() as conn:
        query = """
            SELECT r.plate, r.year_man, r.price, r.reg_date, s.name AS store_name
            FROM register_table r
            JOIN stores_table s ON r.id_store = s.id_store
            JOIN vehicles_table v ON r.id_vehicle = v.id_vehicle
            JOIN models_table m ON v.id_model = m.id_model
            JOIN brands_table b ON m.id_brand = b.id_brand
            WHERE b.name = %s AND m.name = %s AND v.year_mod = %s
            ORDER BY r.reg_date
        """
        df = pd.read_sql(query, conn, params=(brand_name, model_name, year))
    return df
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
                st.write(f"Preço médio para {marca_selecionada} {modelo_selecionado} {ano_modelo_selecionado}: R$ {preco_medio:,.2f}.")# ({count} registros)")
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
            ano_fab = st.number_input("Ano de Fabricação", min_value=0, step=1, format="%d")
            preco = st.number_input("Preço", min_value=0.0, format="%.2f")

            if st.button("Registrar Preço"):
                # Agora, a variável loja_selecionada é comparada corretamente com loja['nome']
                loja_id = next(loja['id'] for loja in st.session_state.lojas_registradas if loja['nome'] == loja_selecionada)
                register_vehicle_price(user_info['email'], loja_selecionada, ano_selecionado, ano_fab, preco)
                st.success(f"Preço do veículo cadastrado com sucesso!")
                #else:
                    #st.write(f"Erro ao cadastrar o preço.")
                #usuario, loja, modelo, ano, preco

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
    st.title("Histórico de cotações")
    st.subheader("Consulta de histórico de cotações por veículo.")

    # Checkbox para alternar entre pesquisa por placa ou marca-modelo-ano
    toggle_plate_search= st.checkbox("Pesquisar carro por placa", key="pesquisar_por_placa", help="Habilite para pesquisar um carro epecífico através da placa. Deixe sem marcar caso queira pesquisar pelo arranjo marca-modelo-ano")

    # Inicializar variáveis no session_state se ainda não existirem
    if 'search_params' not in st.session_state:
        st.session_state.search_params = {
            'marca': None,
            'modelo': None,
            'ano': None,
            'placa': None,
            'toggle_plate_search': False
        }
    
    if not toggle_plate_search:
        # Pesquisa por marca-modelo-ano
        marcas = get_brands()
        marca_selecionada = st.selectbox("Marca", ["Escolha uma marca"] + marcas, key="marca_selecionada")

        if marca_selecionada != "Escolha uma marca":
            modelos = get_models_by_brand(marca_selecionada)
            if modelos:
                modelo_selecionado = st.selectbox("Modelo", ["Escolha um modelo"] + modelos, key="modelo_selecionado")
            else:
                st.warning("Não há modelos disponíveis para a marca selecionada.")
                modelo_selecionado = None
        else:
            modelo_selecionado = None

        if modelo_selecionado and modelo_selecionado != "Escolha um modelo":
            anos_modelos = get_years_by_model(marca_selecionada, modelo_selecionado)
            if anos_modelos:
                ano_modelo_selecionado = st.selectbox("Ano/Modelo", ["Escolha um ano/modelo"] + anos_modelos, key="ano_modelo_selecionado")
            else:
                ano_modelo_selecionado = None
        else:
            ano_modelo_selecionado = None

        placa_selecionada = None
    else:
        # Pesquisa por placa
        placa_selecionada = st.text_input(
            "Placa do veículo (ex.: ABC1234 ou ABC1D34)",
            max_chars=7,
            key="placa_selecionada"
        )
        marca_selecionada = None
        modelo_selecionado = None
        ano_modelo_selecionado = None

    # Botão "Pesquisar" para salvar os parâmetros no session_state
    if st.button("Pesquisar"):
        if toggle_plate_search:
            if placa_selecionada and len(placa_selecionada.strip()) > 0:
                placa_selecionada = placa_selecionada.upper()
                if len(placa_selecionada) != 7:
                    st.warning("A placa deve ter exatamente 7 caracteres (ex.: ABC1234 ou ABC1D23).")
                elif not re.match(r'^([A-Z]{3}\d{4}|[A-Z]{3}\d[A-Z]\d{2})$', placa_selecionada):
                    st.warning("A placa deve seguir o padrão tradicional (ex.: ABC1234) ou Mercosul (ex.: ABC1D23).")
                else:
                    st.session_state.search_params = {
                        'marca': None,
                        'modelo': None,
                        'ano': None,
                        'placa': placa_selecionada,
                        'toggle_plate_search': True
                    }
            else:
                st.warning("Por favor, informe uma placa válida.")
        else:
            if marca_selecionada != "Escolha uma marca" and modelo_selecionado and modelo_selecionado != "Escolha um modelo" and ano_modelo_selecionado and ano_modelo_selecionado != "Escolha um ano/modelo":
                st.session_state.search_params = {
                    'marca': marca_selecionada,
                    'modelo': modelo_selecionado,
                    'ano': ano_modelo_selecionado,
                    'placa': None,
                    'toggle_plate_search': False
                }
            else:
                st.warning("Por favor, selecione todos os campos antes de pesquisar.")

    # Renderizar o gráfico com base nos parâmetros salvos no session_state
    if st.session_state.search_params['toggle_plate_search']:
        st.subheader("Histórico de Preços por placa e loja")
        df = get_register_data_by_plate()
        if not df.empty:
            df = df[df['plate'] == st.session_state.search_params['placa']]  # Filtrar pela placa salva
            if not df.empty:
                available_stores = sorted(df['store_name'].unique())
                filtered_stores = st.multiselect("Filtrar por Loja", available_stores, default=available_stores, key="filter_stores_plate")
                if filtered_stores:
                    df = df[df['store_name'].isin(filtered_stores)]
                df_pivot = df.pivot_table(index='reg_date', columns='store_name', values='price', aggfunc='mean')
                df_pivot = df_pivot.fillna(method='ffill')
                df_pivot.index.name = "Data de Registro"

                st.write("Foram encontradas um total de ", len(df), " consultas para a seleção. De ", df.iloc[0, 2], " a ", df.iloc[-1, 2])
                st.line_chart(df_pivot, use_container_width=True)
                st.write("Dados exibidos no gráfico:")
                st.dataframe(df)
            else:
                st.warning(f"Nenhum dado disponível para a placa {st.session_state.search_params['placa']}.")
        else:
            st.warning("Nenhum dado disponível para exibição no gráfico.")
    elif (st.session_state.search_params['marca'] and 
          st.session_state.search_params['modelo'] and 
          st.session_state.search_params['ano']):
        st.subheader("Histórico de Preços por Loja")
        df = get_register_data_by_vehicle(
            st.session_state.search_params['marca'],
            st.session_state.search_params['modelo'],
            st.session_state.search_params['ano']
        )
        if not df.empty:
            available_stores = sorted(df['store_name'].unique())
            filtered_stores = st.multiselect("Filtrar por Loja", available_stores, default=available_stores, key="filter_stores_vehicle")
            if filtered_stores:
                df = df[df['store_name'].isin(filtered_stores)]
            available_plates = sorted(df['plate'].unique())
            filtered_plates = st.multiselect("Filtrar por Placa", available_plates, default=available_plates, key="filter_plates_vehicle")
            if filtered_plates:
                df = df[df['plate'].isin(filtered_plates)]
            df_pivot = df.pivot_table(index='reg_date', columns='store_name', values='price', aggfunc='mean')
            df_pivot = df_pivot.fillna(method='ffill')
            st.line_chart(df_pivot, use_container_width=True)
            st.write(f"Dados do gráfico para {st.session_state.search_params['marca']} {st.session_state.search_params['modelo']} {st.session_state.search_params['ano']}:")
            st.dataframe(df_pivot)
        else:
            st.warning(f"Nenhum dado disponível para {st.session_state.search_params['marca']} {st.session_state.search_params['modelo']} {st.session_state.search_params['ano']}.")
    else:
        st.info("Por favor, clique em 'Pesquisar' para exibir o gráfico.")

    # Botão para limpar pesquisa
    if st.button("Limpar Pesquisa :wastebasket:"):
        st.session_state.search_params = {
        'marca': None,
        'modelo': None,
        'ano': None,
        'placa': None,
        'toggle_plate_search': False
    }

    
# P3 - Samuel
if page == "P3 - Samuel":
    st.title("P3 - Samuel")
    st.subheader("Testes")
    
# P4 - Sofia
if page == "P4 - Sofia":
    st.title("P4 - Sofia")
    st.subheader("Testes")
    
# P5 - Vitor
if page == "P5 - Vitor":
    st.title("P5 - Vitor")
    st.subheader("Testes")
