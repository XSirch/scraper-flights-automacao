import asyncio
from datetime import date, timedelta
import pandas as pd
import re

from playwright.async_api import async_playwright

# Função para coletar os voos de UM dia específico
async def scrape_day(page, origin, destination, flight_date):
    print(f"[DEBUG] Iniciando o scraping para a data: {flight_date}")
    url = (
        "https://www.google.com/travel/flights?hl=pt-BR&gl=BR&trip=oneway&q="
        f"Flights%20to%20{destination}%20from%20{origin}%20on%20{flight_date}"
    )
    print(f"[INFO] Acessando: {url}")
    print("[DEBUG] Iniciando o carregamento da página...")
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    print("[DEBUG] Página carregada.")

    selector = "li.pIav2d"
    print("[DEBUG] Buscando pelo seletor dos cartões de voo...")
    try:
        await page.wait_for_selector(selector, timeout=5000)
    except:
        print(f"[WARN] Não encontrei nenhum voo na data {flight_date}.")
        return None

    flight_cards = await page.query_selector_all(selector)
    print(f"[DEBUG] Encontrados {len(flight_cards)} cartões de voo.")

    if not flight_cards:
        print(f"[WARN] Nenhum cartão de voo encontrado em {flight_date}.")
        return None

    cheapest_flight_info = None
    cheapest_price = float("inf")

    for index, card in enumerate(flight_cards):
        if index >= 5:  # Limitar a 10 cartões
            break
        print(f"[DEBUG] Processando cartão {index + 1} de {len(flight_cards)}")
        try:
            departure_span = page.locator("span[aria-label*='Horário de partida']").first
            departure_time = (await departure_span.inner_text()) if departure_span else "N/A"

            price_el = await card.query_selector("div.YMlIz FpEdX jLMuyc span")
            if not price_el:
                price_locator = page.locator("span[aria-label*='Reais brasileiros']").first
                await price_locator.wait_for()
                raw_price_text = await price_locator.inner_text()
                price_el = page.locator(f"span:has-text('{raw_price_text}')").first
                
            
            raw_price = await price_el.inner_text() if price_el else "N/A"
            print(f"[DEBUG] Horário de partida: {departure_time}, Preço bruto: {raw_price}")

            price_numeric = float("inf")
            if "R$" in raw_price:
                only_digits = "".join(ch for ch in raw_price if ch.isdigit())
                if only_digits:
                    price_numeric = float(only_digits)
            only_digits = re.sub(r"\D", "", raw_price)  # ex.: "2250"
            price_numeric = float(only_digits) if only_digits else float("inf")

            airline_el = await card.query_selector("div.sSHqwe.tPgKwe.ogfYpf span")
            airline = (await airline_el.inner_text()) if airline_el else "N/A"

            if price_numeric < cheapest_price:
                cheapest_price = price_numeric
                cheapest_flight_info = {
                    "data_voo": flight_date,
                    "dia_semana": "",
                    "horario_partida": departure_time,
                    "companhia": airline,
                    "preco": cheapest_price,
                }
        except Exception as e:
            print(f"[DEBUG] Erro ao parsear um cartão: {e}")
            continue

        print(f"[DEBUG] Voo mais barato encontrado: {cheapest_flight_info}")
    return cheapest_flight_info


async def scrape_range(origin, destination, days_ahead=60):
    today = date.today()
    all_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        for i in range(days_ahead + 1):
            target_date = today + timedelta(days=i)
            flight_date_str = target_date.strftime("%Y-%m-%d")
            print(f"[DEBUG] Processando a data: {flight_date_str}")

            flight_info = await scrape_day(page, origin, destination, flight_date_str)
            if flight_info:
                flight_info["dia_semana"] = target_date.strftime("%A")
                all_data.append(flight_info)
                print(f"[DEBUG] Voo encontrado para {flight_date_str}: {flight_info}")
            else:
                print(f"[DEBUG] Nenhum voo encontrado para {flight_date_str}.")

            await page.wait_for_timeout(2000)

        await browser.close()

    print(f"[DEBUG] Total de voos encontrados: {len(all_data)}")
    return all_data


async def main():
    origin = "CGH"
    destination = "SDU"
    days_ahead = 1

    print(f"[INFO] Iniciando coleta de {origin} para {destination} em até {days_ahead} dias...")

    results = await scrape_range(origin, destination, days_ahead)
    print(f"[INFO] Coleta finalizada. {len(results)} dias encontrados com voos.")

    if results:
        df = pd.DataFrame(results)
        print(f"[DEBUG] Dados coletados: {df.head()}")
        df.to_csv("voos_proximos_60_dias.csv", index=False, encoding="utf-8-sig")
        print("[INFO] Dados salvos em 'voos_proximos_60_dias.csv'.")
    else:
        print("[WARN] Não foi encontrado nenhum voo (ou todos falharam).")

if __name__ == "__main__":
    asyncio.run(main())
