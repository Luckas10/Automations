from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import time
import re

# === CONFIGURAÇÃO ===
BASE_DIR = r"D:\\Dataset Carro"
TEMPO_ESPERA = 20

# === INICIAR NAVEGADOR ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

url = input("🔗 Informe a URL do sistema: ").strip()
driver.get(url)

print("➡️ Faça login manualmente e vá até a tela com o calendário de vistorias.")
input("⏳ Quando estiver pronto, pressione Enter para continuar...")

# coleta links de vistorias de carro
WebDriverWait(driver, TEMPO_ESPERA).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "a.fc-daygrid-event"))
)
vistoria_links = driver.find_elements(By.CSS_SELECTOR, "a.fc-daygrid-event")
carros = []
for link in vistoria_links:
    try:
        texto = link.find_element(By.CLASS_NAME, "fc-event-main").text.strip().lower()
        if "carro" in texto:
            carros.append(link.get_attribute("href"))
    except:
        continue

total = len(carros)
print(f"\n🚗 {total} vistorias de carro encontradas. Vou processar **todas**.")

def selecionar_exibir_50():
    seletor = WebDriverWait(driver, TEMPO_ESPERA).until(
        EC.presence_of_element_located((
            By.XPATH, "//label[contains(., 'Exibir')]/select"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView();", seletor)
    time.sleep(1)
    seletor.find_element(By.XPATH, ".//option[text()='50']").click()
    time.sleep(3)

def baixar_imagens_tabela_atual():
    # espera o container DataTables aparecer
    WebDriverWait(driver, TEMPO_ESPERA).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.dataTables_scrollBody"))
    )

    # força o scroll até o fim para renderizar todas as linhas
    scroll_body = driver.find_element(By.CSS_SELECTOR, "div.dataTables_scrollBody")
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_body)
    time.sleep(3.5)  # dá tempo de renderizar as linhas

    # coleta todas as linhas
    linhas = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr")

    # extrai descrição e src em lista estática
    itens = []
    for doc in linhas:
        try:
            tds = doc.find_elements(By.TAG_NAME, "td")
            descricao = next(
                (td.text.strip() for td in tds
                 if td.text.strip() and not td.find_elements(By.TAG_NAME, "img")),
                "SemDescricao"
            )
            descricao = re.sub(r'[\\/:*?"<>|]', '', descricao)

            img = doc.find_element(By.TAG_NAME, "img")
            src = img.get_attribute("src")
            itens.append((descricao, src))
        except:
            continue

    # baixa cada imagem sem mexer mais no Selenium
    for descricao, src in itens:
        try:
            pasta = os.path.join(BASE_DIR, descricao)
            os.makedirs(pasta, exist_ok=True)
            nome_arquivo = os.path.basename(src.split("?", 1)[0])
            caminho = os.path.join(pasta, nome_arquivo)

            resp = requests.get(src, timeout=15)
            resp.raise_for_status()
            with open(caminho, "wb") as f:
                f.write(resp.content)
            print(f"✅ Imagem salva em: {caminho}")
        except requests.HTTPError as he:
            if he.response.status_code == 404:
                print(f"⚠️ Imagem não encontrada (404): {src} — pulando esta imagem.")
            else:
                print(f"⚠️ Erro HTTP ao baixar {src}: {he}")
        except Exception as e:
            print(f"⚠️ Erro ao baixar {src}: {e}")

# === LOOP PRINCIPAL (todas as vistorias) ===
for idx, vistoria_url in enumerate(carros, start=1):
    print(f"\n➡️ [{idx}/{total}] Acessando vistoria: {vistoria_url}")
    try:
        driver.get(vistoria_url)
        time.sleep(2)

        # abre aba Documentos
        aba = WebDriverWait(driver, TEMPO_ESPERA).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@class,'nav-link') and contains(text(),'Documentos')]"
            ))
        )
        driver.execute_script("arguments[0].click();", aba)
        time.sleep(3)

        print("📊 Alterando exibição para 50 registros...")
        selecionar_exibir_50()

        print("📄 Baixando todas as imagens desta vistoria...")
        baixar_imagens_tabela_atual()

    except Exception as e:
        msg = str(e).lower()
        if "404" in msg:
            print(f"⚠️ Vistoria retornou 404 — pulando para a próxima.")
        else:
            print(f"❌ Erro ao processar vistoria #{idx}: {e}")
        continue

print("\n🎯 Processo finalizado para todas as vistorias encontradas.")
input("💛 Pressione Enter para fechar o navegador...")
driver.quit()
