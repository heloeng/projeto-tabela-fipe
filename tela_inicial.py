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

# Armazenamento de informações no estado da sessão
if 'precos_registrados' not in st.session_state:
    st.session_state.precos_registrados = {}
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial"], key="navegacao_radio")

if st.sidebar.button("Logout"):
    st.write("Você clicou em Logout!")

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


