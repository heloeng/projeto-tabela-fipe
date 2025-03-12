import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

#Grande bloco para configurar funcionalidade de autenticacao:
#--------INICIO_BLOCO_DE_AUTENTICACAO-----------
# Configurações do Google OAuth
SCOPES = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
REDIRECT_URI = "http://localhost:8501"  # Para testes locais

# Função para configurar o Flow dinamicamente com st.secrets
def create_flow(state=None):
    try:
        google_secrets = st.secrets["google_oauth"]
        st.write("Debug: Secrets carregados com sucesso")
        client_config = {
            "web": {
                "client_id": google_secrets["client_id"],
                "project_id": google_secrets["project_id"],
                "auth_uri": google_secrets["auth_uri"],
                "token_uri": google_secrets["token_uri"],
                "auth_provider_x509_cert_url": google_secrets["auth_provider_x509_cert_url"],
                "client_secret": google_secrets["client_secret"],
                "redirect_uris": google_secrets["redirect_uris"]
            }
        }
        return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=REDIRECT_URI, state=state)
    except Exception as e:
        st.error(f"Erro ao criar Flow: {str(e)}")
        return None

# Gerenciamento de credenciais no session_state
def get_credentials():
    if "credentials" not in st.session_state:
        st.session_state["credentials"] = None
    return st.session_state["credentials"]

def set_credentials(credentials):
    st.session_state["credentials"] = credentials
    st.write("Debug: Credenciais definidas")

# Fluxo de autenticação
def authenticate():
    flow = create_flow()
    if flow:
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true"
        )
        st.session_state["oauth_state"] = state
        st.write(f"Debug: State salvo: {state}")
        st.write(f"Debug: Redirecionando para {authorization_url}")
        st.write(f'<meta http-equiv="refresh" content="0;url={authorization_url}">', unsafe_allow_html=True)

# Processa o callback do OAuth
def process_callback():
    st.write("Debug: Iniciando process_callback")
    if "code" not in st.query_params:
        st.write("Debug: Nenhum code na URL")
        return False
    
    state_from_url = st.query_params.get("state")
    stored_state = st.session_state.get("oauth_state")
    st.write(f"Debug: State da URL: {state_from_url}, State armazenado: {stored_state}")
    
    if not stored_state or state_from_url != stored_state:
        st.error("Estado inválido. Tente fazer login novamente.")
        st.session_state.pop("oauth_state", None)
        return False
    
    try:
        flow = create_flow(state=stored_state)
        if flow:
            flow.fetch_token(code=st.query_params["code"])
            credentials = flow.credentials
            st.write(f"Debug: Token obtido: {credentials.token}")
            set_credentials(credentials)
            st.session_state.pop("oauth_state", None)
            st.query_params.clear()
            st.rerun()
            return True
    except Exception as e:
        st.error(f"Erro ao autenticar: {str(e)}")
        st.session_state.pop("oauth_state", None)
        return False
    return False

# Obtém informações do usuário autenticado
def get_user_info(credentials):
    st.write("Debug: Entrando em get_user_info")
    if not credentials:
        st.write("Debug: Credenciais ausentes")
        return None
    
    st.write(f"Debug: Token de acesso: {credentials.token}")
    st.write(f"Debug: Token expirado? {credentials.expired}")
    
    try:
        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        response.raise_for_status()
        user_info = response.json()
        st.write(f"Debug: Resposta da API: {user_info}")
        return user_info
    except requests.RequestException as e:
        st.error(f"Erro ao obter informações do usuário: {str(e)}")
        st.write(f"Debug: Status da resposta: {e.response.status_code if e.response else 'N/A'}")
        return None
#--------FIM_BLOCO_DE_AUTENTICACAO-----------

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

# Processa o callback no início do script
st.write("Debug: Início do script")
if "code" in st.query_params:
    process_callback()

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial"], key="navegacao_radio")

# Botão de login
st.sidebar.header("Acesso para colaboradores")
credentials = get_credentials()
st.write(f"Debug: Credenciais no início da sidebar: {credentials.token if credentials else 'None'}")

if credentials and not credentials.expired:
    user_info = get_user_info(credentials)
    if user_info:
        st.sidebar.write(f"Bem-vindo(a), {user_info['name']} ({user_info['email']})")
        if st.sidebar.button("Logout"):
            set_credentials(None)
            st.session_state.pop("oauth_state", None)
            st.rerun()
    else:
        st.sidebar.error("Erro ao carregar informações do usuário.")
else:
    if st.sidebar.button(":key: Fazer Login com Google"):
        if not get_credentials():
            authenticate()

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
