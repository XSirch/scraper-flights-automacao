import json
import sys
import asyncio
import datetime
import math
from pesquisa_voos import search_flights
from db_pg import init_db, salva_resultados_em_db

def carregar_parametros(json_file="params_flights.json"):
    """
    Carrega os parâmetros de busca de voos a partir de um arquivo JSON.
    Exemplo de estrutura do JSON:
    [
      {
         "origem": "GRU",
         "destino": "JFK",
         "data": "2025-03-25"
      },
      {
         "origem": "SDU",
         "destino": "CGH",
         "data": "2025-03-30"
      }
    ]
    """
    with open(json_file, "r", encoding="utf-8") as f:
        parametros = json.load(f)
    return parametros

def carregar_regioes(json_file="regioes.json"):
    """
    Carrega o mapeamento de aeroportos para regiões a partir de um arquivo JSON.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        regioes = json.load(f)
    return regioes

def carregar_airport_coords(json_file="airport_coords.json"):
    """
    Carrega as coordenadas (latitude e longitude) dos aeroportos a partir de um arquivo JSON.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        coords = json.load(f)
    return coords

def haversine(coord1, coord2):
    """
    Calcula a distância (em km) entre duas coordenadas (latitude, longitude) usando a fórmula de Haversine.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Raio da Terra em km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def tratar_preco(preco_valor):
    """
    Converte o valor do preço para um número (float).
    Se o valor já for numérico, retorna-o diretamente.
    Se for uma string, remove 'R$', espaços e formata a vírgula para ponto.
    Se não puder converter, retorna None.
    """
    if preco_valor is None:
        return None

    # Se já for um número, retorna-o
    if isinstance(preco_valor, (int, float)):
        return preco_valor

    # Converte para string, caso não seja
    preco_str = str(preco_valor)
    if "unavailable" in preco_str.lower():
        print("indisponivel")
        return None

    # Remove "R$" e espaços
    preco_limpo = preco_str.replace("R$", "").strip()
    # Remove separadores de milhar e substitui vírgula por ponto
    preco_limpo = preco_limpo.replace(".", "").replace(",", ".")
    try:
        return float(preco_limpo)
    except ValueError:
        print("Erro de tratamento de valor")
        return None

def buscar_voo(origem, destino, data_str, regioes, airport_coords):
    """
    Realiza a busca de voos para a data informada e retorna o voo mais barato.
    Obtém a região de origem a partir do arquivo de mapeamento e calcula a distância entre
    os aeroportos caso as coordenadas estejam disponíveis.
    """
    search_date = datetime.date.today()
    try:
        result = search_flights(data_str, origem, destino)
    except Exception as e:
        print(f"Erro ao buscar voos para {data_str} ({origem} -> {destino}): {e}")
        return None

    if hasattr(result, "flights") and result.flights:
        # Seleciona o voo mais barato
        sorted_flights = sorted(result.flights, key=lambda f: f.price)
        flight = sorted_flights[0]
        flight_date = datetime.datetime.strptime(data_str, '%Y-%m-%d').date()
        hora_busca = datetime.datetime.now()
        # Obtém a região do aeroporto de origem
        regiao_origem = regioes.get(origem, "N/A")
        # Calcula a distância se as coordenadas estiverem disponíveis
        if origem in airport_coords and destino in airport_coords:
            distancia = haversine(airport_coords[origem], airport_coords[destino])
            distancia_str = str(round(distancia, 2))
        else:
            distancia_str = "N/A"
        preco_tratado = tratar_preco(getattr(flight, "price", ""))
        trecho = f"{origem} x {destino}"
        voo_info = {
            "TRECHO": trecho,
            "data_voo": data_str,
            "melhor_voo": "Sim",  # Como selecionamos o mais barato, marcamos como "Sim"
            "hora_partida": getattr(flight, "departure", ""),
            "hora_chegada": getattr(flight, "arrival", ""),
            "preco": preco_tratado,
            "companhia": flight.name,
            "dia_semana_voo": flight_date.strftime("%A"),
            "data_busca": search_date.strftime("%Y-%m-%d"),
            "horario_busca": hora_busca.strftime("%H:%M:%S"),
            "dia_semana_busca": search_date.strftime("%A"),
            "regiao_origem": regiao_origem,
            "distancia_km": distancia_str
        }
        print(f"[DEBUG] Voo encontrado: {voo_info}")
        return voo_info
    else:
        print(f"Nenhum voo encontrado para {data_str} ({origem} -> {destino}).")
        return None

def tarefa_automatizada():
    """
    Função principal que:
      - Inicializa o banco de dados.
      - Carrega os parâmetros de busca de voos, o mapeamento de regiões e as coordenadas dos aeroportos.
      - Para cada conjunto de parâmetros, busca o voo mais barato do dia.
      - Salva os resultados no banco de dados.
    """
    init_db()  # Inicializa o banco e cria as tabelas, se necessário
    print("[INFO] Banco de dados inicializado.")
    parametros = carregar_parametros()
    regioes = carregar_regioes()
    airport_coords = carregar_airport_coords()
    todos_resultados = []

    for param in parametros:
        origem = param.get("origem")
        destino = param.get("destino")
        data_str = param.get("data")
        print(f"Executando busca para {origem} -> {destino} na data {data_str}")
        resultado = buscar_voo(origem, destino, data_str, regioes, airport_coords)
        if resultado:
            todos_resultados.append(resultado)

    if todos_resultados:
        salva_resultados_em_db(todos_resultados)
        print(f"Total de {len(todos_resultados)} registros salvos no banco de dados.")
    else:
        print("Nenhum resultado obtido para salvar.")

if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    tarefa_automatizada()
