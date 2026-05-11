from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from dotenv import load_dotenv
import time
import os
import glob

load_dotenv()

USUARIO = os.getenv("NEPPO_USUARIO")
SENHA = os.getenv("NEPPO_SENHA")
NEPPO_URL = os.getenv("NEPPO_URL")
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")

data_atual = datetime.now().strftime("%d/%m/%Y")
data_atual_formatada = datetime.now().strftime("%d%m%Y")

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
})

def limpar_arquivos_anteriores(prefixo):
    padrao = os.path.join(DOWNLOAD_PATH, f"{prefixo}*")
    for arquivo in glob.glob(padrao):
        try:
            os.remove(arquivo)
        except Exception as e:
            print(f"Erro ao remover {arquivo}: {e}")

def aguardar_e_renomear(novo_prefixo):
    def aguardar_download(pasta, timeout=30):
        for _ in range(timeout):
            arquivos = os.listdir(pasta)
            if arquivos and not any(a.endswith(".crdownload") for a in arquivos):
                return arquivos
            time.sleep(1)
        return []

    limpar_arquivos_anteriores(novo_prefixo)
    arquivos = aguardar_download(DOWNLOAD_PATH)

    if arquivos:
        arquivos_completos = [os.path.join(DOWNLOAD_PATH, a) for a in arquivos]
        mais_recente = max(arquivos_completos, key=os.path.getctime)
        _, ext = os.path.splitext(mais_recente)
        novo_nome = f"{novo_prefixo}{data_atual_formatada}{ext}"
        novo_caminho = os.path.join(DOWNLOAD_PATH, novo_nome)
        if os.path.exists(novo_caminho):
            os.remove(novo_caminho)
        os.rename(mais_recente, novo_caminho)
        print(f"Arquivo salvo: {novo_nome}")
    else:
        print("Nenhum arquivo encontrado para renomear.")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

try:
    driver.get(f"{NEPPO_URL}/chat/#/login")
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[6]/tm2-auth-component/div[1]/div[2]/div/div[4]/form/div/div[2]/div[1]/input"))).send_keys(USUARIO)
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[6]/tm2-auth-component/div[1]/div[2]/div/div[4]/form/div/div[2]/div[2]/input"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-auth-component/div[1]/div[2]/div/div[4]/form/div/div[4]/div[1]/button"))).click()
    time.sleep(5)

    if "dashboard" in driver.current_url:
        print("Login realizado com sucesso.")

        driver.get(f"{NEPPO_URL}/chat/#/report/sessionHistory")
        time.sleep(5)

        campo_data_inicial = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-session-history-component/div[2]/div/div[2]/div[2]/div/div/div/input")))
        driver.execute_script("arguments[0].value = '';", campo_data_inicial)
        campo_data_inicial.send_keys(data_atual)

        campo_data_final = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-session-history-component/div[2]/div/div[2]/div[3]/div/div/div/input")))
        driver.execute_script("arguments[0].value = '';", campo_data_final)
        campo_data_final.send_keys(data_atual)

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-session-history-component/div[2]/div/div[6]/button"))).click()
        time.sleep(5)

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-session-history-component/div[2]/div/a"))).click()
        time.sleep(10)

        aguardar_e_renomear("atendimentos")

        driver.get(f"{NEPPO_URL}/chat/#/report/statusDirectMessage")
        time.sleep(5)

        campo_data_inicial = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-status-direct-message-component/div[2]/div[1]/div[2]/div[2]/div[1]/div/div/input")))
        driver.execute_script("arguments[0].value = '';", campo_data_inicial)
        campo_data_inicial.send_keys(data_atual)

        campo_data_final = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-status-direct-message-component/div[2]/div[1]/div[2]/div[3]/div/div/div/input")))
        driver.execute_script("arguments[0].value = '';", campo_data_final)
        campo_data_final.send_keys(data_atual)

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-status-direct-message-component/div[2]/div[1]/div[5]/button"))).click()
        time.sleep(5)

        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[6]/tm2-status-direct-message-component/div[2]/div[1]/a"))).click()
        time.sleep(10)

        aguardar_e_renomear("envios")

        print(f"Downloads concluídos para: {data_atual}")

    else:
        print("Falha no login.")

except Exception as e:
    print(f"Erro: {str(e)}")

finally:
    driver.quit()