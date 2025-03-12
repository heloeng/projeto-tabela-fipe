import streamlit as st
from create_research_table import insert_research, get_research

st.title("Gerenciamento de Pesquisas")

#  Formulário para Inserção de Pesquisas
with st.form("Inserir Pesquisa"):
    assigned_date = st.date_input("Data de Atribuição")
    completion_date = st.date_input("Data de Conclusão (opcional)", None)
    user_id = st.number_input("ID do Pesquisador", min_value=1, step=1)
    store_id = st.number_input("ID da Loja", min_value=1, step=1)

    submitted = st.form_submit_button("Adicionar Pesquisa")
    if submitted:
        insert_research(assigned_date, completion_date, user_id, store_id)
        st.success(" Pesquisa cadastrada com sucesso!")

#  Listar Pesquisas Existentes
st.subheader("Pesquisas Cadastradas")
researches = get_research()
for research in researches:
    st.write(f" **Pesquisa {research[0]}** -  {research[1]} |  Loja ID {research[4]} | 👤 Pesquisador ID {research[3]}")
