import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


driver = webdriver.Chrome()
driver.get("http://localhost:8501")
time.sleep(1)

#-------------------Search without parameters (plate mode OFF)-----------------------
# Condições: 
# Usuário é pesquisador, e deve estar com a tela de pesquisador aberta. O reste refere-se ao arquivo tela_pesquisador_no_auth.py
# Teste: Realizar pesquisa com o modo "pesquisar por placa" ativado, a placa informada está contida no banco de dados.

option_to_select = "Consulta histórico de cotações" 
radio_selection = driver.find_elements(By.CSS_SELECTOR, "div[role='radiogroup'] label") # Seleciona o radio, não pela key, mas pela classe de objeto.
for button in radio_selection:
    if option_to_select in button.text:
        button.click()
        break

time.sleep(2)

checkbox = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".st-key-pesquisar_por_placa input[type='checkbox']"))
    )   
driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
driver.execute_script("arguments[0].click();", checkbox) # Forçando o clique com JavaScript

plate_input = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-placa_selecionada input[type= 'text']"))
)
plate_input.clear()
plate_input.send_keys("XYZ0123")
plate_input.send_keys(Keys.ENTER)

time.sleep(2)

search_research_history = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-search_tracking button"))
)
driver.execute_script("arguments[0].scrollIntoView(true);", search_research_history)
search_research_history.click()


time.sleep(4)
driver.quit()