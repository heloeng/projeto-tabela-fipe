import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import os

# Configurações do Google OAuth
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
REDIRECT_URI = "http://localhost:8501"
CLIENT_SECRETS_FILE = "client_secret.json"

# Verifica se o arquivo client_secret.json existe
if not os.path.exists(CLIENT_SECRETS_FILE):
    st.error(f"Arquivo {CLIENT_SECRETS_FILE} não encontrado. Por favor, coloque-o no diretório do projeto.")
    st.stop()

# Gerenciamento de credenciais no session_state
def get_credentials():
    if "credentials" not in st.session_state:
        st.session_state["credentials"] = None
    return st.session_state["credentials"]

def set_credentials(credentials):
    st.session_state["credentials"] = credentials

# Fluxo de autenticação
def authenticate():
    if not get_credentials():
        try:
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            authorization_url, state = flow.authorization_url(
                access_type="offline",
                include_granted_scopes="true",
                prompt="consent"
            )
            st.session_state["state"] = state
            st.write("Redirecionando para o login do Google...")
            st.write(
                f'<meta http-equiv="refresh" content="1;url={authorization_url}">',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Erro ao iniciar autenticação: {str(e)}")

# Processa o callback do OAuth
def process_callback():
    if "code" not in st.query_params:
        return False
    
    state_from_url = st.query_params.get("state")
    stored_state = st.session_state.get("state")
    
    if not stored_state:
        st.warning("State não encontrado. Usando state da URL como fallback.")
        stored_state = state_from_url
        st.session_state["state"] = stored_state
    
    if state_from_url != stored_state:
        st.error("Estado inválido ou ausente. Tente fazer login novamente.")
        st.session_state.pop("state", None)
        return False
    
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=stored_state
        )
        flow.fetch_token(code=st.query_params["code"])
        credentials = flow.credentials
        set_credentials(credentials)
        st.session_state.pop("state", None)
        st.query_params.clear()
        st.rerun()
        return True
    except Exception as e:
        st.error(f"Erro ao processar o callback: {str(e)}")
        st.session_state.pop("state", None)
        return False

# Obtém informações do usuário autenticado
def get_user_info(credentials):
    if not credentials:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao obter informações do usuário: {str(e)}")
        return None

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
if "code" in st.query_params:
    process_callback()

# Sidebar
st.sidebar.title("Menu")
page = st.sidebar.radio("Navegação", ["Tela Inicial"], key="navegacao_radio")

# Autenticação na sidebar
st.sidebar.header("Acesso para colaboradores")
credentials = get_credentials()

if credentials and not credentials.expired:
    user_info = get_user_info(credentials)
    if user_info:
        st.sidebar.write(f"Bem-vindo(a), {user_info['name']} ({user_info['email']})")
        if st.sidebar.button("Logout"):
            st.session_state["credentials"] = None
            st.session_state.pop("state", None)
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
        if chave_veiculo in st.session_state.precos_registrados:
            lojas_precos = st.session_state.precos_registrados[chave_veiculo]
            total_preco = sum(preco for loja, precos in lojas_precos.items() for preco in precos)
            total_registros = sum(len(precos) for loja, precos in lojas_precos.items())
            if total_registros > 0:
                preco_medio = total_preco / total_registros
                st.write(f"**Preço Médio do {chave_veiculo}:** R$ {preco_medio:.2f}")
            else:
                st.write("**Nenhum preço registrado para este veículo ainda.**")
        else:
            st.write("**Nenhum preço registrado para este veículo ainda.**")