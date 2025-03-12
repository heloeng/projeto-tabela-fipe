import streamlit as st
from create_stores_table import insert_store, get_stores

#  Título da Aplicação
st.title("Gerenciamento de Lojas")

#  Formulário para Inserção de Lojas
with st.form("Inserir Loja"):
    name = st.text_input("Nome da Loja")
    city = st.text_input("Cidade")
    state = st.text_input("Estado")
    street = st.text_input("Rua")
    neighborhood = st.text_input("Bairro")
    number = st.text_input("Número")
    zip_code = st.text_input("CEP")

    submitted = st.form_submit_button("Salvar Loja")
    if submitted:
        insert_store(name, city, state, street, neighborhood, number, zip_code)
        st.success(f" Loja '{name}' salva com sucesso!")


#  Listar Lojas Existentes
st.subheader("Lojas Cadastradas")
stores = get_stores()
for store in stores:
    st.write(f" **{store[1]}** -  {store[2]}, {store[3]}")
