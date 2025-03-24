from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

def test_graph():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)
    
    try:
        driver.get("http://localhost:8501")
        time.sleep(3)

        # 1) Clicar em "Gráfico Mensal"
        graph_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='stMarkdownContainer']//p[contains(text(), 'Gráfico Mensal')]")))
        graph_menu.click()
        time.sleep(3)  # Dar tempo para o Streamlit trocar de tela

        # 2) Selecionar a marca "Hyundai"
        brand_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='stSelectbox'][.//p[text()='Marca']]//div[@data-baseweb='select']//input")))
        brand_input.click()
        time.sleep(1)
        brand_input.send_keys("Hyundai")
        time.sleep(1)
        brand_input.send_keys(Keys.ENTER)
        print("Selecionada a marca Hyundai com sucesso!")
        time.sleep(3)

        # 3) Selecionar "IONIQ 5" no campo Modelo
        model_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='stSelectbox'][.//p[text()='Modelo']]//div[@data-baseweb='select']//input")))
        model_input.click()
        time.sleep(1)
        model_input.send_keys("IONIQ 5")
        time.sleep(1)
        model_input.send_keys(Keys.ENTER)
        time.sleep(3)
        print("Selecionado Hyundai (Marca) e IONIQ 5 (Modelo).")

        # 4) Selecionar o campo "Ano/Modelo" (ex.: 2025)
        year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='stSelectbox'][.//p[text()='Ano/Modelo']]//div[@data-baseweb='select']//input")))
        year_input.click()
        time.sleep(1)
        year_input.send_keys("2025")
        time.sleep(1)
        year_input.send_keys(Keys.ENTER)

        # 5) Localizar o campo date_input para "Selecione o Período"
        date_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stDateInput'][.//p[text()='Selecione o Período']]")))
        
        # 6) Localizar o elemento <input> dentro do container de datas
        input_field = date_container.find_element(By.XPATH, ".//input[@data-testid='stDateInputField']")

        # 7) Clicar para focar e digitar o intervalo
        input_field.click()
        time.sleep(1)
        input_field.clear()
        time.sleep(1)
        input_field.send_keys("01/01/2025 – 17/03/2025")
        time.sleep(1)
        input_field.send_keys(Keys.ENTER)
        time.sleep(2)

        # Pressiona Enter para confirmar
        input_field.send_keys(Keys.ENTER)
        time.sleep(2)

        print("Intervalo '01/01/2025 – 17/03/2025' digitado com sucesso.")

        # 8) Aguardar e clicar no botão "Gerar Gráfico"
        button_generate = wait.until(EC.element_to_be_clickable((By.XPATH, "//button//*[contains(text(), 'Gerar Gráfico')]")))
        button_generate.click()
        time.sleep(2)
        print("Cliquei no botão 'Gerar Gráfico'.")

        # 9) Aguardar o gráfico ser exibido
        graph_img = wait.until(EC.presence_of_element_located((By.XPATH, "//img[contains(@src, 'data:image/png')]")))
        print("Gráfico exibido com sucesso.")

      

    except Exception as e:
        print(f"Erro no teste: {e}")

    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    test_graph()
