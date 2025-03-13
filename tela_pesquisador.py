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

# Configuração do email do pesquisador (exemplo fictício, pode ser alterado conforme necessidade)
if 'pesquisador_email' not in st.session_state:
    st.session_state.pesquisador_email = "pesquisador1@exemplo.com"  # Defina o email do pesquisador

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial", "Pesquisador"], key="navegacao_radio")

# Botão de logout (sem funcionalidade)
if st.sidebar.button("Logout"):
    # st.session_state["credentials"] = None
    # st.session_state.pop("state", None)
    # st.rerun()
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

# Tela do Pesquisador
elif page == "Pesquisador":
    st.title("Área do Pesquisador")
    st.subheader("Registro de Preços")
    
    # Exibir as lojas atribuídas ao pesquisador e o gestor responsável
    pesquisador_email = st.session_state.pesquisador_email  # Usando o email do pesquisador do session_state
    
    # Exibir as lojas atribuídas
    if pesquisador_email in st.session_state.pesquisadores_lojas:
        lojas_atribuidas = st.session_state.pesquisadores_lojas[pesquisador_email]
        st.write(f"**Lojas Atribuídas a {pesquisador_email}:** {', '.join(lojas_atribuidas)}")
        
        # Exibir o gestor responsável
        if pesquisador_email in st.session_state.gestores_associacoes:
            gestores = st.session_state.gestores_associacoes[pesquisador_email]
            st.write(f"**Gestores Responsáveis:** {', '.join(gestores)}")
        else:
            st.write("**Nenhum gestor atribuído ainda.**")
    else:
        st.write("**Nenhuma loja atribuída ainda.**")
    
    # Seleção de marca, modelo e ano para o pesquisador
    marca_selecionada = st.selectbox("Escolha uma marca", ["Escolha uma marca"] + list(veiculos.keys()), key="marca_selecionada_pesquisador", index=0)
    modelo_selecionado = st.selectbox("Escolha um modelo", ["Escolha um modelo"] + veiculos.get(marca_selecionada, []), key="modelo_selecionado_pesquisador", index=0)
    ano_selecionado = st.selectbox("Escolha um ano", ["Escolha um ano", "2019", "2020", "2021", "2022", "2023", "2024"], key="ano_selecionado_pesquisador", index=0)
    
    # Seleção de loja apenas entre as lojas atribuídas ao pesquisador
    if pesquisador_email in st.session_state.pesquisadores_lojas:
        lojas_disponiveis = st.session_state.pesquisadores_lojas[pesquisador_email]
    else:
        lojas_disponiveis = []
    
    loja_selecionada = st.selectbox("Escolha uma loja", ["Escolha uma loja"] + lojas_disponiveis, key="loja_selecionada", index=0)
    
    # Registrar preço
    preco = st.number_input("Preço do veículo", min_value=0.0, format="%.2f")
    
    # Registrar o preço se houver valores preenchidos
    if st.button("Registrar Preço"):
        chave_veiculo = f"{marca_selecionada} - {modelo_selecionado} - {ano_selecionado}"
        
        if chave_veiculo not in st.session_state.precos_registrados:
            st.session_state.precos_registrados[chave_veiculo] = {}
        
        # Adicionar preço à loja selecionada
        if loja_selecionada != "Escolha uma loja" and preco > 0:
            if loja_selecionada not in st.session_state.precos_registrados[chave_veiculo]:
                st.session_state.precos_registrados[chave_veiculo][loja_selecionada] = []
            
            st.session_state.precos_registrados[chave_veiculo][loja_selecionada].append(preco)
            st.success(f"Preço de R$ {preco:.2f} registrado para o veículo {chave_veiculo} na loja {loja_selecionada}.")
            
            # Resetar todos os campos para o placeholder após registrar
            marca_selecionada = "Escolha uma marca"
            modelo_selecionado = "Escolha um modelo"
            ano_selecionado = "Escolha um ano"
            loja_selecionada = "Escolha uma loja"
        else:
            st.warning("Por favor, escolha uma loja válida e insira um preço válido.")
