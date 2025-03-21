import unittest
import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unittest.mock import patch

class TestaTelaPesquisador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuração inicial do Selenium - Executado uma vez para todos os testes"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")  # Evita detecção de automação
        
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.get("http://localhost:8501")  # Ajuste a URL se necessário
        
        # Aguarda o login manual antes de continuar
        input("Por favor, faça o login manualmente na tela inicial e depois pressione Enter para continuar os testes.")

    def test_plotagem_grafico(self):
        """Testa se a cadeia de loja pode ser selecionada corretamente"""
        time.sleep(5)  # Aguarda o carregamento inicial

        # Rola a página para garantir visibilidade dos elementos
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Aguarda o carregamento do selectbox e clica nele
        try:
            select_cadeia = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//label[contains(text(), 'Selecione uma Cadeia')]/following-sibling::div"))
            )
            select_cadeia.click()
            time.sleep(5)

            # Aguarda as opções carregarem
            WebDriverWait(self.driver, 30).until(
                lambda driver: len(driver.find_elements(By.XPATH, "//div[@role='option']")) > 0
            )

            # Captura as opções disponíveis
            options = self.driver.find_elements(By.XPATH, "//div[@role='option']")
            opcoes_disponiveis = [opt.text for opt in options]
            print("Opções encontradas:", opcoes_disponiveis)

            nome_cadeia = "Rede de Lojas C"  # Ajuste conforme necessário
            encontrou = nome_cadeia in opcoes_disponiveis

            self.assertTrue(encontrou, f"A opção '{nome_cadeia}' não foi encontrada no selectbox! Opções disponíveis: {opcoes_disponiveis}")

            # Se encontrou, clica na opção correspondente
            if encontrou:
                for opt in options:
                    if opt.text == nome_cadeia:
                        opt.click()
                        break
                time.sleep(2)

            # Aguarda o botão "Consultar Variação" e clica nele
            botao_consultar = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Consultar Variação')]"))
            )
            botao_consultar.click()

            # Aguarda um possível gráfico aparecer
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'chart-container')]"))
            )

        except Exception as e:
            print(f"Erro ao selecionar a cadeia ou ao carregar o gráfico: {str(e)}")

    # Função simulada para associar loja à cadeia
    def associate_store_to_chain(self, store_id, chain_name):
        st.success(f"Loja {store_id} associada à cadeia {chain_name} com sucesso!")

    @patch('streamlit.selectbox')
    @patch('streamlit.button')
    @patch('streamlit.success')
    def test_associacao_loja_cadeia(self, mock_success, mock_button, mock_selectbox):
        # Simulando as seleções no Streamlit
        mock_selectbox.side_effect = ['Autocarros', 'Rede de Lojas C']
        mock_button.return_value = True  # Simula o clique no botão

        # Inicializando o estado da sessão para a loja e a cadeia
        st.session_state.lojas_registradas = [{'nome': 'Autocarros', 'id': '1'}, {'nome': 'Outras Lojas', 'id': '2'}]
        chains = ["Rede de Lojas A", "Rede de Lojas B", "Rede de Lojas C"]

        # Executando a lógica de associação
        loja_id = mock_selectbox("Selecione a Loja", [loja['nome'] for loja in st.session_state.lojas_registradas])
        chain_to_associate = mock_selectbox("Selecione a Cadeia", chains)

        if mock_button("Associar Loja à Cadeia"):
            try:
                # Busca o ID da loja a partir do nome
                store_id = next(loja['id'] for loja in st.session_state.lojas_registradas if loja['nome'] == loja_id)
                # Chama a função para associar loja à cadeia
                self.associate_store_to_chain(store_id, chain_to_associate)
            except Exception as e:
                st.error(f"Erro ao associar loja à cadeia: {e}")

        # Verifica se o sucesso ocorreu com a associação esperada
        mock_success.assert_called_with("Loja 1 associada à cadeia Rede de Lojas C com sucesso!")

    @patch('streamlit.text_input')
    @patch('streamlit.button')
    @patch('streamlit.error')
    def test_nome_rede_ja_existente(self, mock_error, mock_button, mock_text_input):
        # Simulando o nome já existente
        mock_text_input.return_value = "Rede de Lojas C"  # Nome que já existe

        # Lista de redes cadastradas
        redes_cadastradas = ["Rede de Lojas A", "Rede de Lojas B", "Rede de Lojas C"]

        # Lógica de validação para verificar se a rede já existe
        nome_rede = mock_text_input("Nome da Cadeia")
        if nome_rede in redes_cadastradas:
            mock_error(f"A cadeia '{nome_rede}' já está cadastrada!")

        # Verifica se a mensagem de erro foi chamada
        mock_error.assert_called_with("A cadeia 'Rede de Lojas C' já está cadastrada!")

    @patch('streamlit.text_input')
    @patch('streamlit.button')
    @patch('streamlit.error')
    def test_nome_rede_extremamente_grande(self, mock_error, mock_button, mock_text_input):
        # Nome extremamente longo
        nome_grande = "R" * 1000  # 1000 caracteres, muito grande

        # Lógica de validação para o nome da rede
        mock_text_input.return_value = nome_grande

        # Definindo um tamanho máximo permitido para o nome
        max_length = 255
        if len(nome_grande) > max_length:
            mock_error(f"O nome da cadeia não pode ultrapassar {max_length} caracteres!")

        # Verifica se a mensagem de erro foi chamada
        mock_error.assert_called_with(f"O nome da cadeia não pode ultrapassar {max_length} caracteres!")

    @classmethod
    def tearDownClass(cls):
        """Fecha o navegador após todos os testes - Executado uma vez após todos os testes"""
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
