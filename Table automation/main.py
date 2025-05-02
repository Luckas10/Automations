from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Iniciar navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Abrir sistema
url = input("🔗 Informe a URL do sistema: ").strip()
driver.get(url)

print("\n➡️ Faça login manualmente e vá até a página com a tabela.")

while True:
    iniciar = input("\n⏳ Quando estiver pronto e na tabela desejada, digite '1'. Para sair, digite 'sair': ")
    if iniciar.strip().lower() == "sair":
        print("👋 Encerrando script. O navegador continuará aberto.")
        break
    if iniciar.strip() != "1":
        print("⚠️ Entrada inválida.")
        continue

    # Entrada dos anos (permitindo deixar em branco)
    ano_min_input = input("📅 Informe o ANO MÍNIMO (pressione Enter para ignorar): ").strip()
    ano_max_input = input("📅 Informe o ANO MÁXIMO (pressione Enter para ignorar): ").strip()

    try:
        ano_min = int(ano_min_input) if ano_min_input else None
        ano_max = int(ano_max_input) if ano_max_input else None
        total_paginas = int(input("📄 Quantas páginas essa tabela possui? "))
    except ValueError:
        print("❌ Entrada inválida.")
        continue

    try:
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        print("\n==============================")
        print("✅ Tabela detectada. Iniciando verificação...")
        print("==============================\n")

        pagina_atual = 1
        while pagina_atual <= total_paginas:
            print(f"\n🔁 Verificando página {pagina_atual} de {total_paginas}...")

            linhas = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            for linha in linhas:
                colunas = linha.find_elements(By.TAG_NAME, "td")
                if len(colunas) >= 5:
                    texto_coluna = colunas[3].text.strip()
                    try:
                        ano = int(texto_coluna.split()[0])

                        # Verifica os filtros de ano
                        if (ano_min is not None and ano < ano_min) or \
                           (ano_max is not None and ano > ano_max):
                            checkbox = colunas[0].find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                            if checkbox.is_selected():
                                driver.execute_script("arguments[0].click();", checkbox)
                                print(f"🛑 Desmarcado veículo do ano {ano}")
                    except ValueError:
                        print(f"⚠️ Coluna não contém ano válido: '{texto_coluna}'")
                    except Exception as e:
                        print(f"⚠️ Erro ao clicar no checkbox: {e}")
                        continue

            if pagina_atual == total_paginas:
                print("\n✅ Última página verificada.")
                break

            # Mudar de página pelo número
            try:
                proxima_pagina = str(pagina_atual + 1)
                botao = driver.find_element(By.XPATH, f"//button[normalize-space(text())='{proxima_pagina}']")
                driver.execute_script("arguments[0].click();", botao)
                print(f"➡️ Avançando para página {proxima_pagina}")
                pagina_atual += 1
                time.sleep(0.3)
            except:
                try:
                    proximo = driver.find_element(By.XPATH, "//button[normalize-space(text())='>']")
                    driver.execute_script("arguments[0].click();", proximo)
                    print("➡️ Avançando com botão '>' como alternativa.")
                    pagina_atual += 1
                    time.sleep(0.3)
                except Exception as e:
                    print(f"❌ Não foi possível avançar para próxima página: {e}")
                    break

        print("\n==============================")
        print("✅ Verificação concluída nesta tabela.")
        print("==============================")

    except Exception as erro:
        print(f"\n❌ Erro durante execução: {erro}")

print("\n🔍 Script encerrado. Verifique tudo no navegador.")
