import streamlit as st
from databases.create_users_table import insert_user, get_users

st.title("Gerenciamento de Usuários")

#  Formulário para Inserção de Usuários
with st.form("Inserir Usuário"):
    name = st.text_input("Nome do Usuário")
    email = st.text_input("Email")
    role = st.selectbox("Papel", ["gestor", "pesquisador"])

    submitted = st.form_submit_button("Adicionar Usuário")
    if submitted:
        insert_user(name, email, role)
        st.success(f"Usuário '{name}' cadastrado com sucesso!")

#  Listar Usuários Existentes
st.subheader("Usuários Cadastrados")
users = get_users()
for user in users:
    st.write(f" **{user[1]}** -  {user[2]} |  {user[3]}")
