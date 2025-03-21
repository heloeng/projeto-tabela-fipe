from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import cv2
import numpy as np
import time

# Configurar o Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executar sem abrir a janela do navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Acessar a página que contém o gráfico
driver.get("http://localhost:8501")
time.sleep(5)  # Esperar o carregamento

# Capturar o screenshot do gráfico
graph_element = driver.find_element(By.XPATH, "XPATH_DO_GRAFICO")
graph_element.screenshot("graph.png")

driver.quit()

# Processar a imagem para detectar pontos
image = cv2.imread("graph.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)

# Detectar contornos
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filtrar contornos para detectar pontos
min_radius = 3  # Ajuste conforme necessário
max_radius = 10
point_count = 0
for contour in contours:
    (x, y), radius = cv2.minEnclosingCircle(contour)
    if min_radius < radius < max_radius:
        point_count += 1

print(f"Número de pontos detectados: {point_count}")
