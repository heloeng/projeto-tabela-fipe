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

if 'pesquisadores_cadastrados' not in st.session_state:
    st.session_state.pesquisadores_cadastrados = []  # Lista de pesquisadores cadastrados

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Gestor"], key="navegacao_radio")

# Botão de logout (sem funcionalidade)
if st.sidebar.button("Logout"):
    st.write("Você clicou em Logout!")  # Esse botão não faz nada por enquanto, apenas visual.

# Tela Inicial (usuário)
if page == "Tela Inicial":
    st.title("Consulta de Preços de Veículos")
    st.subheader("Consulta de Preços Médios")
    
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

# Tela do Gestor
elif page == "Gestor":
    st.title("Área do Gestor")
    st.subheader("Atribuição de Pesquisadores a Lojas")
    
    # Cadastro de um novo pesquisador (email)
    novo_pesquisador_email = st.text_input("Cadastrar um novo pesquisador (e-mail)", key="novo_pesquisador_email")
    
    # Botão para cadastrar pesquisador
    if st.button("Cadastrar Pesquisador"):
        if novo_pesquisador_email and "@" in novo_pesquisador_email:
            # Adiciona o e-mail do pesquisador à lista
            st.session_state.pesquisadores_cadastrados.append(novo_pesquisador_email)
            st.success(f"Pesquisador {novo_pesquisador_email} cadastrado com sucesso!")
        else:
            st.warning("Por favor, insira um e-mail válido.")

    # Seleção do pesquisador
    pesquisador = st.selectbox("Escolha um pesquisador", ["Escolha um pesquisador"] + st.session_state.pesquisadores_cadastrados, key="pesquisador_gestor")
    
    # Seleção de loja
    loja = st.selectbox("Escolha uma loja", ["Escolha uma loja", "Loja A", "Loja B", "Loja C"], key="loja_gestor")
    
    # Atribuir pesquisador à loja
    if st.button("Atribuir Loja ao Pesquisador"):
        if pesquisador != "Escolha um pesquisador" and loja != "Escolha uma loja":
            if pesquisador not in st.session_state.pesquisadores_lojas:
                st.session_state.pesquisadores_lojas[pesquisador] = []
            
            # Adiciona a loja ao pesquisador
            if loja not in st.session_state.pesquisadores_lojas[pesquisador]:
                st.session_state.pesquisadores_lojas[pesquisador].append(loja)
                st.success(f"Pesquisador {pesquisador} foi atribuído à loja {loja}.")
            else:
                st.warning(f"O pesquisador {pesquisador} já está atribuído à loja {loja}.")
        else:
            st.warning("Por favor, escolha um pesquisador e uma loja válidos.")
    
    # Exibição dos pesquisadores e suas lojas atribuídas
    st.subheader("Pesquisadores e Lojas Atribuídas")
    for pesquisador, lojas in st.session_state.pesquisadores_lojas.items():
        st.write(f"**{pesquisador}** - Lojas: {', '.join(lojas)}")
