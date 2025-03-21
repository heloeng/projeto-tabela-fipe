from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

class TesteInterface:

    def setup_method(self):
        self.driver = webdriver.Chrome()

    def test_same_date(self):
        # Configuração do WebDriver (no exemplo, estou usando o Chrome)
        driver = self.driver

        try:
            # Abre a página do Streamlit
            driver.get("http://localhost:8501")

            # Aguarda a página carregar
            time.sleep(2)

            # Localiza o menu lateral e clica na opção "Cotação Dólar"
            sidebar = driver.find_element(By.CSS_SELECTOR, ".stSidebar")
            cotacao_dolar_option = driver.find_element(By.CSS_SELECTOR, "div.st-c2.st-b0.st-b1.st-b2.st-b3.st-c3.st-bf.st-bg.st-c4")
            cotacao_dolar_option.click()

            # Aguarda a página carregar
            time.sleep(5)

            dropdown_marca = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha uma marca']"))
            )

            # Clica no dropdown para abrir as opções
            dropdown_marca.click()

            # Aguarda as opções do dropdown carregarem
            time.sleep(1)

            # Localiza a opção "Toyota" no dropdown
            opcao_toyota = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Toyota')]"))
            )

            # Clica na opção "Toyota"
            opcao_toyota.click()

            # Aguarda a seleção ser aplicada e o carregamento dos modelos
            time.sleep(1)

            # Seleciona o modelo
            dropdown_modelo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha um modelo']"))
            )

            # Clica no dropdown para abrir as opções
            dropdown_modelo.click()

            # Aguarda as opções do dropdown carregarem
            time.sleep(1)

            opcao_corolla = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Corolla')]"))
            )

            # Clica na opção "Toyota"
            opcao_corolla.click()

            # Aguarda a seleção ser aplicada e o carregamento dos modelos
            time.sleep(1)

            dropdown_ano_modelo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha um ano/modelo']"))
            )

            # Clica no dropdown para abrir as opções
            dropdown_ano_modelo.click()

            # Aguarda as opções do dropdown carregarem
            time.sleep(1)

            opcao_flex = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '2019 Flex')]"))
            )

            # Clica na opção "2019 Flex"
            opcao_flex.click()

            # Aguarda a seleção ser aplicada e o carregamento dos modelos
            time.sleep(1)

            botao_pesquisar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[.//p[text()="Pesquisar"]]'))
            )

            botao_pesquisar.click()

            time.sleep(5)

            grafico = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nsewdrag drag"))
            )

            grafico.click()

            time.sleep(2)

            assert qtd == 1, "Deveria ser apresentado gráfico com um ponto."

        finally:
            # Fecha o navegador
            driver.quit()

    # def test_valid_period(self):
    #     # Configuração do WebDriver (no exemplo, estou usando o Chrome)
    #     driver = self.driver

    #     try:
    #         # Abre a página do Streamlit
    #         driver.get("http://localhost:8501")

    #         # Aguarda a página carregar
    #         time.sleep(2)

    #         # Localiza o menu lateral e clica na opção "Cotação Dólar"
    #         sidebar = driver.find_element(By.CSS_SELECTOR, ".stSidebar")
    #         cotacao_dolar_option = driver.find_element(By.CSS_SELECTOR, "div.st-c2.st-b0.st-b1.st-b2.st-b3.st-c3.st-bf.st-bg.st-c4")
    #         cotacao_dolar_option.click()

    #         # Aguarda a página carregar
    #         time.sleep(5)

    #         dropdown_marca = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha uma marca']"))
    #         )

    #         # Clica no dropdown para abrir as opções
    #         dropdown_marca.click()

    #         # Aguarda as opções do dropdown carregarem
    #         time.sleep(1)

    #         # Localiza a opção "Toyota" no dropdown
    #         opcao_toyota = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Toyota')]"))
    #         )

    #         # Clica na opção "Toyota"
    #         opcao_toyota.click()

    #         # Aguarda a seleção ser aplicada e o carregamento dos modelos
    #         time.sleep(1)

    #         # Seleciona o modelo
    #         dropdown_modelo = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha um modelo']"))
    #         )

    #         # Clica no dropdown para abrir as opções
    #         dropdown_modelo.click()

    #         # Aguarda as opções do dropdown carregarem
    #         time.sleep(1)

    #         opcao_corolla = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Corolla')]"))
    #         )

    #         # Clica na opção "Toyota"
    #         opcao_corolla.click()

    #         # Aguarda a seleção ser aplicada e o carregamento dos modelos
    #         time.sleep(1)

    #         dropdown_ano_modelo = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='Escolha um ano/modelo']"))
    #         )

    #         # Clica no dropdown para abrir as opções
    #         dropdown_ano_modelo.click()

    #         # Aguarda as opções do dropdown carregarem
    #         time.sleep(1)

    #         opcao_flex = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '2019 Flex')]"))
    #         )

    #         # Clica na opção "2019 Flex"
    #         opcao_flex.click()

    #         # Aguarda a seleção ser aplicada e o carregamento dos modelos
    #         time.sleep(1)

    #         dropdown_mes_inicio = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='Janeiro']"))
    #         )

    #         dropdown_mes_inicio.click()

    #         mes_inicio = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Maio')]"))
    #         )

    #         mes_inicio.click()

    #         dropdown_mes_fim = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='Janeiro']"))
    #         )

    #         dropdown_mes_fim.click()

    #         mes_fim = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Abril')]"))
    #         )

    #         mes_fim.click()

    #         time.sleep(1)

    #         dropdown_ano_inicio = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='2020']"))
    #         )

    #         dropdown_ano_inicio.click()

    #         ano_inicio = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '2024')]"))
    #         )

    #         ano_inicio.click()

    #         time.sleep(1)

    #         dropdown_ano_fim = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[text()='2020']"))
    #         )

    #         dropdown_ano_fim.click()

    #         ano_fim = WebDriverWait(driver, 5).until(
    #             EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '2025')]"))
    #         )

    #         ano_fim.click()

    #         botao_pesquisar = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, '//button[.//p[text()="Pesquisar"]]'))
    #         )

    #         botao_pesquisar.click()

    #         time.sleep(1)

    #         alerta = WebDriverWait(driver, 20).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, "div.st-emotion-cache-1rsyhoq.e1nzilvr5 p"))
    #         )
    #         result = alerta.text
    #         print(result)

    #         time.sleep(2)

    #         assert result == "O período selecionado é inválido!", "Mensagem deveria informar que o período selecionado é inválido."

    #     finally:
    #         # Fecha o navegador
    #         driver.quit()