import streamlit as st

# Dados das marcas e modelos
veiculos = {
    "Chevrolet": ["Onix", "Cruze", "Tracker", "S10"],
    "Ford": ["Ka", "Fiesta", "Focus", "Ranger"],
    "Toyota": ["Corolla", "Etios", "Hilux", "Yaris"],
    "Honda": ["Civic", "Fit", "HR-V", "CR-V"]
}

# Armazenar os preços registrados pelos pesquisadores e as lojas associadas
if 'precos_registrados' not in st.session_state:
    st.session_state.precos_registrados = {}

if 'pesquisadores_lojas' not in st.session_state:
    st.session_state.pesquisadores_lojas = {}

if 'gestores_associacoes' not in st.session_state:
    st.session_state.gestores_associacoes = {}

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial"], key="navegacao_radio")

# Botão de login (sem funcionalidade)
if st.sidebar.button("Fazer Login com Google"):
    st.write("Você clicou em 'Fazer Login com Google'. (Sem funcionalidade no momento)")

# Tela Inicial (usuário)
if page == "Tela Inicial":
    st.title("Bem-vindo à Consulta de Preços de Veículos")
    st.subheader("Consulte os preços médios dos veículos nas lojas")

    # Filtros com placeholders
    marca_selecionada = st.selectbox("Escolha uma marca", ["Escolha uma marca"] + list(veiculos.keys()), key="marca_selecionada")
    modelo_selecionado = st.selectbox("Escolha um modelo", ["Escolha um modelo"] + veiculos.get(marca_selecionada, []), key="modelo_selecionado")
    ano_selecionado = st.selectbox("Escolha um ano", ["Escolha um ano", "2019", "2020", "2021", "2022", "2023", "2024"], key="ano_selecionado")
    
    # Chave para identificar o veículo completo
    chave_veiculo = f"{marca_selecionada} - {modelo_selecionado} - {ano_selecionado}"
    
    # Botão de pesquisa
    if st.button("Pesquisar"):
        # Exibir o preço médio se houverem preços registrados
        if chave_veiculo in st.session_state.precos_registrados:
            lojas_precos = st.session_state.precos_registrados[chave_veiculo]
            total_preco = sum([preco for loja, precos in lojas_precos.items() for preco in precos])  # Soma de todos os preços
            total_registros = sum([len(precos) for loja, precos in lojas_precos.items()])  # Total de registros
            
            if total_registros > 0:
                preco_medio = total_preco / total_registros  # Preço médio
                st.write(f"**Preço Médio do {chave_veiculo}:** R$ {preco_medio:.2f}")
            else:
                st.write("**Nenhum preço registrado para este veículo ainda.**")
        else:
            st.write("**Nenhum preço registrado para este veículo ainda.**")
