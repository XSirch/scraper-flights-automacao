import streamlit as st
import datetime
import pandas as pd
import math
import sys
import asyncio
import concurrent.futures
from pesquisa_voos import search_flights
from airports import airport_coords, obter_regiao
from db import init_db, salva_resultados_em_db, salva_historico_em_db, busca_resultados, busca_historico
from historico_precos import scrape 

# Inicializa o banco de dados ao iniciar o app, garantindo que os dados persistam
init_db()

if "resultados" not in st.session_state:
    st.session_state["resultados"] = None

def haversine(coord1, coord2):
    # Fórmula de Haversine para calcular a distância (em km) entre duas coordenadas
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

def fetch_voos_por_data(date_str, origem, destino, search_date, num_results):
    resultados = []
    try:
        result = search_flights(date_str, origem, destino)
    except Exception as e:
        if "no token provided" in str(e).lower():
            st.error("Token não fornecido. Por favor, forneça um token para continuar.")
            return []
        else:
            raise e
    if result.flights:
        # Ordena os voos pelo preço e seleciona os melhores conforme o número solicitado
        sorted_flights = sorted(result.flights, key=lambda f: f.price)
        melhores_voos = sorted_flights[:num_results]
        flight_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        for flight in melhores_voos:
            voo_info = {
                "data_voo": date_str,
                "melhor_voo": "Sim" if flight.is_best else "Não",
                "hora_partida": getattr(flight, "departure", ""),
                "hora_chegada": getattr(flight, "arrival", ""),
                "preco": flight.price,
                "companhia": flight.name,
                "dia_semana_voo": flight_date.strftime("%A"),
                "dia_semana_busca": search_date.strftime("%A")
            }
            if origem in airport_coords and destino in airport_coords:
                distancia = haversine(airport_coords[origem], airport_coords[destino])
                voo_info["distancia_km"] = str(round(distancia, 2))
            else:
                voo_info["distancia_km"] = "N/A"
            resultados.append(voo_info)
    return resultados

def app():
    st.title("Buscador de Voos")
    page = st.sidebar.radio("Selecione a página", ["Buscar Voos", "Histórico de Preços", "Database"])
    
    if page == "Histórico de Preços":
        # --- Seção para disparar o scraper e gerar o CSV ---
        st.subheader("Gerar Histórico de Preços")

        # O usuário deve informar o trecho no formato "ORIGEM x DESTINO" (ex.: "SDU x CGH")
        origem = st.selectbox("Código do aeroporto de origem", options=list(airport_coords.keys()), index=list(airport_coords.keys()).index("GRU"))
        destino = st.selectbox("Código do aeroporto de destino", options=list(airport_coords.keys()), index=list(airport_coords.keys()).index("JFK"))
        flight_date_input = st.date_input("Data do Voo para Scraping", value=datetime.date.today(), key="scrape_date")
        
        if st.button("Gerar Histórico de Preços", key="gerar_historico"):
            try:
                # Divide o trecho para extrair origem e destino
                if sys.platform.startswith("win"):
                    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                    flight_date_str = flight_date_input.strftime("%Y-%m-%d")
                    print(origem, destino, flight_date_str)
                    # Executa a função de scraping de forma síncrona utilizando asyncio.run       
                    asyncio.run(scrape(origem, destino, flight_date_str))
                    st.success("Histórico de preços gerado com sucesso! Confira abaixo os dados carregados.")
            except Exception as e:
                st.error(f"Erro ao gerar histórico: {e}")
        
        # --- Seção para carregar os dados do scraper ---
        st.subheader("Resultado da busca")
        try:
            df_precos = pd.read_csv("historico_precos.csv")
            st.write("Dados carregados do arquivo historico_precos.csv:")
            st.dataframe(df_precos)
        except Exception as e:
            st.error("Erro ao carregar o arquivo historico_precos.csv. Certifique-se de que o arquivo foi gerado.")
            st.stop()
        
        # --- Seção para processar os dados e gerar o DataFrame pivotado ---
        st.subheader("Processar Histórico de Preços")
        # Entrada para o trecho (caso o usuário queira confirmar ou alterar)
        trecho = f"{origem} x {destino}"
        if st.button("Gerar DataFrame", key="gerar_dataframe"):
            data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Converte os valores da coluna "Tempo" para uppercase
            df_precos["Tempo"] = df_precos["Tempo"].str.upper()
            # Remove o símbolo "R$" e espaços em branco
            df_precos["Preço"] = df_precos["Preço"].str.replace("R$", "", regex=False).str.strip()
            # Cria um dicionário mapeando cada tempo para seu respectivo preço (caso haja duplicatas, pega o primeiro)
            price_dict = df_precos.groupby("Tempo")["Preço"].first().to_dict()
            
            # Define a ordem das colunas: inicia com HOJE e depois ordena os demais pelo número extraído
            ordered_times = []
            if "HOJE" in price_dict:
                ordered_times.append("HOJE")
            import re
            others = []
            for key in price_dict.keys():
                if key != "HOJE":
                    m = re.search(r'(\d+)', key)
                    if m:
                        others.append((int(m.group(1)), key))
            others.sort(key=lambda x: x[0])
            ordered_times.extend([key for _, key in others])
            
            # Cria o dicionário final com a estrutura desejada
            final_row = {"TRECHO": trecho, "DATA": data_hora}
            for col in ordered_times:
                final_row[col] = price_dict.get(col)
            
            # Cria o DataFrame final com uma única linha
            df_historico_final = pd.DataFrame([final_row])
            st.session_state["df_historico"] = df_historico_final
            st.write("DataFrame Gerado:")
            st.dataframe(df_historico_final)
        
        # --- Seção para salvar o DataFrame processado em uma nova tabela no banco ---
        if "df_historico" in st.session_state:
            if st.button("Salvar DataFrame no Banco", key="salvar_dataframe"):
                try:
                    salva_historico_em_db(st.session_state["df_historico"])
                except Exception as e:
                    st.error(f"Erro ao salvar o DataFrame no banco: {e}")              
                st.success("DataFrame salvo no banco de dados com sucesso!")
        st.stop()
    
    if page == "Database":
        st.subheader("Database")
        # --- Seção para carregar os dados do banco --- 
        try:
            resultado = busca_resultados()
            historico = busca_historico()
            st.write("Dados carregados do banco de dados:")
            st.subheader("Resultados")
            st.dataframe(resultado)
            st.subheader("Histórico de Preços")
            st.dataframe(historico)
        except Exception as e:    
            st.error(f"Erro ao carregar os dados do banco: {e}")        
        st.stop()
    # --- Página de busca de voos ---
    st.sidebar.header("Filtros de Busca")
    with st.sidebar.expander("Explicação das Siglas dos Aeroportos"):
        st.write("As siglas representam os códigos IATA dos aeroportos. Exemplos:")
        st.write("- GRU: Aeroporto Internacional de São Paulo/Guarulhos")
        st.write("- JFK: Aeroporto Internacional John F. Kennedy")
        st.write("- Outros aeroportos possuem siglas padrão conforme IATA.")
    
    start_date = st.date_input("Data de início", datetime.date.today())
    end_date = st.date_input("Data de fim", datetime.date.today() + datetime.timedelta(days=30))
    origem = st.selectbox("Código do aeroporto de origem", options=list(airport_coords.keys()), index=list(airport_coords.keys()).index("GRU"))
    destino = st.selectbox("Código do aeroporto de destino", options=list(airport_coords.keys()), index=list(airport_coords.keys()).index("JFK"))
    
    # Widget para o usuário escolher quantos resultados deseja por data
    num_results = st.number_input("Número de resultados por data", min_value=1, max_value=10, value=3, step=1)
    
    if st.button("Buscar voos"):
        search_date = datetime.date.today()
        total_days = (end_date - start_date).days + 1
        datas = [(start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(total_days)]
        
        progress_bar = st.progress(0)
        resultados = []
        completed = 0
        
        # Busca de voos em paralelo usando multithreading, passando o parâmetro num_results
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_date = {
                executor.submit(fetch_voos_por_data, data, origem, destino, search_date, num_results): data 
                for data in datas
            }
            for future in concurrent.futures.as_completed(future_to_date):
                resultados.extend(future.result())
                completed += 1
                progress_bar.progress(completed / total_days)
        
        if resultados:
            now = datetime.datetime.now()
            for r in resultados:
                r["data_busca"] = search_date.strftime("%Y-%m-%d")
                r["horario_busca"] = now.strftime("%H:%M:%S")
                r["regiao_origem"] = obter_regiao(origem)
            resultados = sorted(resultados, key=lambda x: x["data_voo"])
            st.session_state["resultados"] = resultados
            df = pd.DataFrame(resultados)
            st.dataframe(df)
            
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Exportar para CSV", data=csv, file_name="resultados.csv", mime="text/csv")
        else:
            st.error("Nenhum voo encontrado para os parâmetros informados.")
    
    # Botão para salvar os resultados (exibido sempre que houver dados na sessão)
    if st.session_state["resultados"]:
        if st.button("Salvar no Banco", key="save_button"):
            try:
                salva_resultados_em_db(st.session_state["resultados"])
                st.success(f"Resultados salvos no banco de dados com sucesso! ({len(st.session_state['resultados'])} registros)")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    
    with st.expander("Banco de Dados Atualizado"):
        registros = busca_resultados()
        if registros:
            st.dataframe(pd.DataFrame(registros))
        else:
            st.write("Banco de dados está vazio.")

if __name__ == "__main__":
    app()
