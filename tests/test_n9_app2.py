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

brand_selector = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-marca_selecionada_trkng input"))
)
brand_selector.click()

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stSelectboxVirtualDropdown']"))
)

selected_brand = WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[role='option']"))
)
for brand in selected_brand:
    if "Toyota" in brand.text:
        brand.click()
        break

model_selector = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-modelo_selecionado_trkng input"))
)
model_selector.click()

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stSelectboxVirtualDropdown']"))
)

selected_model = WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[role='option']"))
)

time.sleep(1)

for model in selected_model:
    if "Corolla" in model.text:
        model.click()
        break

year_selector = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-ano_modelo_selecionado_trkng input"))
)
year_selector.click()

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stSelectboxVirtualDropdown']"))
)

selected_year = WebDriverWait(driver, 5).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[role='option']"))
)

time.sleep(1)

for year in selected_year:
    if "2019 Flex" in year.text:
        year.click()
        break

time.sleep(2)

search_research_history = WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".st-key-search_tracking button"))
)
driver.execute_script("arguments[0].scrollIntoView(true);", search_research_history)
search_research_history.click()


time.sleep(4)
driver.quit()