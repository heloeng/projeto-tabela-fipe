from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import cv2
import numpy as np
import time


class TesteInterface:

    def setup_method(self):
        self.driver = webdriver.Chrome()

    def test_graph(self):
        # Configuração do WebDriver (no exemplo, estou usando o Chrome)
        driver = self.driver
        driver.get("http://localhost:8501")

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

        time.sleep(2)

        botao_pesquisar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[.//p[text()="Pesquisar"]]'))
        )

        botao_pesquisar.click()

        time.sleep(10)

        # Capturar o screenshot do gráfico
        graph_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nsewdrag"))
        )
        graph_element.screenshot("graph.png")

        driver.quit()

        # Processar a imagem para detectar pontos
        image = cv2.imread("graph.png")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)

        #Remover ruídos
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Detectar contornos
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar contornos para detectar pontos
        min_radius = 2  # Ajuste conforme necessário
        max_radius = 10
        point_count = 0
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            if min_radius < radius < max_radius:
                point_count += 1

        assert point_count == 1, "O gráfico deveria apresentar mais de 1 ponto."
