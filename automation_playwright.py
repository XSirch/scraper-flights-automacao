import json
import asyncio
import datetime
import math
from zoneinfo import ZoneInfo

from db_pg import init_db, salva_resultados_em_db
from pesquisa_voos_playwright import scrape_day
from playwright.async_api import async_playwright

def carregar_parametros(json_file="params_flights.json"):
    """
    Carrega os parâmetros de busca de voos a partir de um arquivo JSON.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_regioes(json_file="regioes.json"):
    """
    Carrega o mapeamento de aeroportos para regiões a partir de um arquivo JSON.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def carregar_airport_coords(json_file="airport_coords.json"):
    """
    Carrega as coordenadas (latitude e longitude) dos aeroportos a partir de um arquivo JSON.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def haversine(coord1, coord2):
    """
    Calcula a distância (em km) entre duas coordenadas (latitude, longitude)
    usando a fórmula de Haversine.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Raio da Terra em km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def tratar_preco(preco_valor):
    """
    Converte o valor do preço para um número (int).
    Se o valor já for numérico, retorna-o diretamente.
    Se for uma string, remove 'R$', espaços e formata a vírgula para ponto.
    Se não puder converter, retorna None.
    """
    if preco_valor is None:
        return None
    if isinstance(preco_valor, (int, float)):
        return preco_valor

    preco_str = str(preco_valor)
    if "unavailable" in preco_str.lower():
        return None

    preco_limpo = preco_str.replace("R$", "").strip()
    preco_limpo = preco_limpo.replace(".", "").replace(",", ".")
    try:
        return int(preco_limpo)
    except ValueError:
        return None

def validar_voo_info(voo_info):
    """
    Verifica se todos os campos do voo estão presentes e são válidos.
    Considera inválido se algum campo for None, uma string vazia, "0" ou "N/A".
    """
    for key, value in voo_info.items():
        if value is None or (isinstance(value, str) and value.strip() in ["", "0", "N/A"]):
            return False
    return True

async def buscar_voo_playwright(origin, destination, flight_date, regioes, airport_coords, browser):
    """
    Tenta realizar a busca do voo via Playwright, repetindo a busca até 3 vezes
    caso não obtenha um resultado válido.
    """
    max_attempts = 3
    attempt = 0
    flight_info = None
    while attempt < max_attempts:
        try:
            page = await browser.new_page()
            flight_info = await scrape_day(page, origin, destination, flight_date)
        except Exception as e:
            print(f"[ERROR] Erro ao buscar voos para {flight_date} ({origin} -> {destination}) na tentativa {attempt+1}: {e}")
        finally:
            try:
                await page.close()
            except Exception as e:
                print("[WARN] Erro ao fechar a página:", e)
        if flight_info:
            break
        else:
            print(f"[WARN] Tentativa {attempt+1} - Nenhum voo encontrado para {flight_date} ({origin} -> {destination}).")
        attempt += 1
    return flight_info

async def processar_parametro(param, regioes, airport_coords, browser):
    """
    Processa um parâmetro de busca:
      - Realiza a busca do voo utilizando Playwright.
      - Completa as informações do voo com os dados adicionais necessários.
    """
    origin = param.get("origem")
    destination = param.get("destino")
    flight_date = param.get("data")
    print(f"[INFO] Processando voo: {origin} -> {destination} em {flight_date}")
    
    flight = await buscar_voo_playwright(origin, destination, flight_date, regioes, airport_coords, browser)
    if not flight:
        print(f"[ERROR] Não foi possível obter um voo válido para {origin} -> {destination} em {flight_date}.")
        return None

    flight_date_obj = datetime.datetime.strptime(flight_date, "%Y-%m-%d").date()
    agora_br = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
    trecho = f"{origin} x {destination}"
    regiao_origem = regioes.get(origin, "N/A")
    if origin in airport_coords and destination in airport_coords:
        distancia = haversine(airport_coords[origin], airport_coords[destination])
        distancia_str = str(round(distancia, 2))
    else:
        distancia_str = "N/A"
    preco_tratado = tratar_preco(flight.get("preco"))

    # Monta o dicionário com todos os campos exigidos para a tabela
    voo_info = {
        "TRECHO": trecho,
        "data_voo": flight_date,
        "hora_partida": flight.get("horario_partida", "N/A"),
        "hora_chegada": flight.get("horario_chegada", "N/A"),  # Dado não obtido via Playwright
        "preco": preco_tratado,
        "companhia": flight.get("companhia", "N/A"),
        "dia_semana_voo": flight_date_obj.strftime("%A"),
        "data_busca": agora_br.strftime("%Y-%m-%d"),
        "horario_busca": agora_br.strftime("%H:%M:%S"),
        "dia_semana_busca": agora_br.strftime("%A"),
        "regiao_origem": regiao_origem,
        "distancia_km": distancia_str
    }
    print(f"[DEBUG] Voo encontrado: {voo_info}")
    if validar_voo_info(voo_info):
        return voo_info
    else:
        print("[WARN] Voo com parâmetros inválidos.")
        return None

async def tarefa_automatizada():
    """
    Função principal que:
      - Inicializa o banco de dados.
      - Carrega os parâmetros, as regiões e as coordenadas dos aeroportos.
      - Realiza as buscas de voos de forma assíncrona utilizando Playwright.
      - Salva os resultados no banco de dados.
    """
    init_db()
    print("[INFO] Banco de dados inicializado.")
    parametros = carregar_parametros()
    regioes = carregar_regioes()
    airport_coords = carregar_airport_coords()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = []
        for param in parametros:
            tasks.append(processar_parametro(param, regioes, airport_coords, browser))
        resultados = await asyncio.gather(*tasks)
        await browser.close()

    # Filtra os resultados válidos (não None)
    resultados_validos = [r for r in resultados if r is not None]
    if resultados_validos:
        salva_resultados_em_db(resultados_validos)
        print(f"[INFO] Total de {len(resultados_validos)} registros salvos no banco de dados.")
    else:
        print("[WARN] Nenhum resultado obtido para salvar.")

if __name__ == "__main__":
    asyncio.run(tarefa_automatizada())
