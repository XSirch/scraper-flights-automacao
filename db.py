import sqlite3
import csv

def init_db():
    """
    Inicializa o banco de dados e cria a tabela 'resultados' se ela não existir.
    """
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS resultados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_voo TEXT,
                        melhor_voo TEXT,
                        hora_partida TEXT,
                        hora_chegada TEXT,
                        preco REAL,
                        companhia TEXT,
                        dia_semana_voo TEXT,
                        data_busca TEXT,
                        horario_busca TEXT,
                        regiao_origem TEXT,
                        distancia_km TEXT
                    )""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TRECHO TEXT,
            DATA TEXT,
            DADOS TEXT
        )
    """)
    conn.commit()
    conn.close()

def salva_resultados_em_db(resultados):
    """
    Salva uma lista de resultados no banco de dados.
    Evita a inserção de registros duplicados verificando se já existe um registro com os mesmos dados.
    """
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    for r in resultados:
        # Verifica se já existe um registro com os mesmos dados (exceto o id)
        cur.execute("""
            SELECT COUNT(*) FROM resultados 
            WHERE data_voo = ? AND melhor_voo = ? AND hora_partida = ? AND hora_chegada = ? 
                  AND preco = ? AND companhia = ? AND dia_semana_voo = ? 
                  AND data_busca = ? AND horario_busca = ? AND regiao_origem = ? 
                  AND distancia_km = ?
        """, (r.get("data_voo"), r.get("melhor_voo"), r.get("hora_partida"), r.get("hora_chegada"), r.get("preco"),
              r.get("companhia"), r.get("dia_semana_voo"), r.get("data_busca"), r.get("horario_busca"),
              r.get("regiao_origem"), r.get("distancia_km")))
        exists = cur.fetchone()[0]
        if exists == 0:
            print(f"Resultado já cadastrado: {r}")
            cur.execute("""INSERT INTO resultados 
                            (data_voo, melhor_voo, hora_partida, hora_chegada, preco, companhia, dia_semana_voo, 
                             data_busca, horario_busca, regiao_origem, distancia_km)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (r.get("data_voo"), r.get("melhor_voo"), r.get("hora_partida"), r.get("hora_chegada"), r.get("preco"),
                         r.get("companhia"), r.get("dia_semana_voo"), r.get("data_busca"), r.get("horario_busca"),
                         r.get("regiao_origem"), r.get("distancia_km")))
    conn.commit()
    conn.close()

def salva_historico_em_db(historico):
    """
    Salva o histórico de preços no banco de dados.
    """
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    # Obtém as colunas do DataFrame passado como parâmetro
    columns = historico.columns.tolist()
    placeholders = ", ".join(["?"] * len(columns))
    # Envolve os nomes das colunas em aspas duplas para evitar problemas com nomes que possam ser números ou palavras reservadas
    quoted_columns = ", ".join([f'"{col}"' for col in columns])
    sql_insert = f"INSERT INTO historico ({quoted_columns}) VALUES ({placeholders})"
    cur.execute(sql_insert, tuple(historico.iloc[0]))
    conn.commit()
    conn.close()

def export_db_to_csv(csv_filename):
    """
    Exporta todos os registros da tabela 'resultados' para um arquivo CSV.
    O csv_filename é o nome do arquivo CSV de destino.
    Retorna o nome do arquivo CSV criado.
    """
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM resultados")
    rows = cur.fetchall()
    headers = [description[0] for description in cur.description]
    conn.close()
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(headers)
        csv_writer.writerows(rows)
        
    return csv_filename

def busca_resultados():
    """Retorna todos os registros da tabela 'resultados' como uma lista de dicionários."""
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM resultados")
    rows = cur.fetchall()
    headers = [description[0] for description in cur.description]
    conn.close()
    results = [dict(zip(headers, row)) for row in rows]
    return results

def busca_historico():
    """Retorna todos os registros da tabela 'historico' como uma lista de dicionários."""
    conn = sqlite3.connect('resultados.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM historico")
    rows = cur.fetchall()
    headers = [description[0] for description in cur.description]
    conn.close()
    results = [dict(zip(headers, row)) for row in rows]
    return results