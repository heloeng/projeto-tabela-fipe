from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configuração automática do WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Abrir o Google
driver.get("https://www.google.com")

# Fechar o navegador após 5 segundos
import time
time.sleep(5)
driver.quit()
