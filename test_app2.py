import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get("http://localhost:8501")
time.sleep(3)

# Validando o título da página
expected_title = "Histórico de Cotações"
actual_title = driver.title

auth_button = driver.find_element(By.ID,"stBaseButton-secondary")
auth_button.click
time.sleep(3)

assert actual_title == expected_title, "Title should be 'Histórico de Cotações', but its:"


    # Validando campo 'Fist Name'

    # first_name_field = driver.find_element(By.ID,"firstName")
    # first_name_field.send_keys("João Marcelo Carneiro Dantas")



# @pytest.fixture(scope="session")
# def driver():
#     # Start the Streamlit application as a separate process
#     app_process = subprocess.Popen(
#         ["streamlit", "run", "tela_inicial.py"]
#         )

#     driver = webdriver.Chrome()
#     driver.implicitly_wait(3)

#     yield driver

#     driver.quit()

#     # Stop the Streamlit application process after the test
#     app_process.terminate()
#     app_process.wait()