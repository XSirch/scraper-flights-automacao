import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def scrape(origin: str, destination: str, flight_date: str, output_file: str = "historico_precos.csv"):
    """
    Realiza uma busca one-way no Google Flights utilizando os parâmetros:
      - origin: código ou nome do aeroporto de origem.
      - destination: código ou nome do aeroporto de destino.
      - flight_date: data do voo (no formato AAAA-MM-DD).

    O script acessa a URL de busca, clica no botão para expandir o gráfico de histórico
    de preços, aguarda o carregamento dos dados, extrai informações de tempo e preço dos
    elementos do gráfico e, por fim, salva os resultados em um arquivo CSV.
    """
    # Monta a URL da busca
    url = (
        "https://www.google.com/travel/flights?hl=pt-BR&gl=BR&trip=oneway&q="
        f"Flights%20to%20{destination}%20from%20{origin}%20on%20{flight_date}"
    )
    print(f"[DEBUG] URL construída: {url}")

    # XPath do botão que expande o gráfico de histórico de preços
    expand_button_xpath = (
        '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/'
        'div[2]/div[2]/div/div/div/div/div[1]/div[4]/button'
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Acessa a página e aguarda o carregamento completo (networkidle)
        await page.goto(url)
        print("[DEBUG] Página acessada. Aguardando carregamento (networkidle)...")
        await page.wait_for_load_state("networkidle")

        # Rola a página para disparar o carregamento de elementos dinâmicos
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # Tenta localizar e clicar no botão que expande o gráfico
        try:
            button_locator = page.locator(f"xpath={expand_button_xpath}")
            await button_locator.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            await button_locator.click(timeout=20000)
            print("[DEBUG] Botão de expandir gráfico clicado.")
        except Exception as e:
            print(f"[DEBUG] Erro ao clicar no botão: {e}")

        # Aguarda alguns segundos para que o gráfico seja carregado
        await page.wait_for_timeout(5000)
        try:
            await page.wait_for_selector("g[aria-label*=' - ']", timeout=20000)
            print("[DEBUG] Gráfico carregado.")
        except Exception as e:
            print(f"[DEBUG] Erro ao aguardar o gráfico: {e}")
            await browser.close()
            return

        # Extrai os elementos do gráfico que contêm a informação de tempo e preço
        elements = await page.query_selector_all("g[aria-label*=' - ']")
        print(f"[DEBUG] Número de elementos encontrados: {len(elements)}")

        # Processa os dados extraídos
        data = []
        for elem in elements:
            aria_label = await elem.get_attribute("aria-label")
            if aria_label and " - " in aria_label:
                # Divide a string no formato "Tempo - Preço"
                time_info, price_info = [part.strip() for part in aria_label.split(" - ", 1)]
                data.append({"Tempo": time_info, "Preço": price_info})

        await browser.close()

        # Salva os dados extraídos em um arquivo CSV, se houver informações
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
            print(f"[DEBUG] Dados coletados e salvos em '{output_file}'.")
        else:
            print("[DEBUG] Nenhum dado encontrado no gráfico.")

async def main():
    # Exemplo de parâmetros:
    origin = "REC"         # Aeroporto de Congonhas
    destination = "GIG"    # Santos Dumont
    flight_date = "2025-03-19"
    await scrape(origin, destination, flight_date)

if __name__ == "__main__":
    asyncio.run(main())
