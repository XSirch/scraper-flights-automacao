import os
import psycopg2
import csv
from dotenv import load_dotenv

def get_connection():
    """
    Obtém a conexão com o banco de dados PostgreSQL usando a variável de ambiente DATABASE_URL.
    """
    # Se não estiver no GitHub Actions, tente carregar as variáveis do .env
    if os.getenv("GITHUB_ACTIONS") != "true":
        from dotenv import load_dotenv
        load_dotenv()
    USER = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    DBNAME = os.getenv("DBNAME")
    # Para debug, podemos imprimir (ou registrar) se as variáveis estão sendo capturadas (não imprima senhas em produção!)
    print("Tentando conectar com:")
    print("USER:", USER)
    print("HOST:", HOST)
    print("PORT:", PORT)
    print("DBNAME:", DBNAME)
    
    try:
        conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
        sslmode='require'
    )
        print("Connection successful!")
        return conn
    except:
        print("Connection failed!")

'''    # Create a cursor to execute SQL queries
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise Exception("A variável de ambiente DATABASE_URL não está definida!")
    conn = psycopg2.connect(db_url)
    return conn'''

def init_db():
    """
    Inicializa o banco de dados e cria a tabela 'resultados' se ela não existir.
    Agora inclui a coluna TRECHO.
    """
    conn = get_connection()
    cur = conn.cursor()
    print("Verificando/criando a tabela 'resultados'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id SERIAL PRIMARY KEY,
            TRECHO TEXT,
            data_voo TEXT,
            melhor_voo TEXT,
            hora_partida TEXT,
            hora_chegada TEXT,
            preco REAL,
            companhia TEXT,
            dia_semana_voo TEXT,
            data_busca TEXT,
            horario_busca TEXT,
            dia_semana_busca TEXT,
            regiao_origem TEXT,
            distancia_km TEXT
        )
    """)
    conn.commit()
    print("Tabela 'resultados' verificada/criada com sucesso.")
    cur.close()
    conn.close()

def salva_resultados_em_db(resultados):
    """
    Salva uma lista de resultados no banco de dados PostgreSQL.
    Evita a inserção de registros duplicados verificando se já existe um registro com os mesmos dados.
    Agora inclui a coluna TRECHO.
    """
    conn = get_connection()
    cur = conn.cursor()
    for r in resultados:
        print("Verificando duplicidade para o registro:")
        print(r)
        cur.execute("""
            SELECT COUNT(*) FROM resultados 
            WHERE TRECHO = %s AND data_voo = %s AND melhor_voo = %s AND hora_partida = %s AND hora_chegada = %s 
                  AND preco = %s AND companhia = %s AND dia_semana_voo = %s 
                  AND data_busca = %s AND horario_busca = %s AND dia_semana_busca = %s 
                  AND regiao_origem = %s AND distancia_km = %s
        """, (
            r.get("TRECHO"),
            r.get("data_voo"), 
            r.get("melhor_voo"), 
            r.get("hora_partida"), 
            r.get("hora_chegada"), 
            r.get("preco"),
            r.get("companhia"), 
            r.get("dia_semana_voo"), 
            r.get("data_busca"), 
            r.get("horario_busca"),
            r.get("dia_semana_busca"),
            r.get("regiao_origem"), 
            r.get("distancia_km")
        ))
        exists = cur.fetchone()[0]
        print("Resultado da verificação (número de registros existentes):", exists)
        if exists == 0:
            print("Inserindo registro:")
            print(r)
            cur.execute("""
                INSERT INTO resultados 
                (TRECHO, data_voo, melhor_voo, hora_partida, hora_chegada, preco, companhia, dia_semana_voo, 
                 data_busca, horario_busca, dia_semana_busca, regiao_origem, distancia_km)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                r.get("TRECHO"),
                r.get("data_voo"), 
                r.get("melhor_voo"), 
                r.get("hora_partida"), 
                r.get("hora_chegada"), 
                r.get("preco"),
                r.get("companhia"), 
                r.get("dia_semana_voo"), 
                r.get("data_busca"), 
                r.get("horario_busca"),
                r.get("dia_semana_busca"),
                r.get("regiao_origem"), 
                r.get("distancia_km")
            ))
            print("Registro inserido com sucesso.")
        else:
            print("Registro já cadastrado:", r)
    conn.commit()
    print("Todos os registros foram processados e commit realizado.")
    cur.close()
    conn.close()

def export_db_to_csv(csv_filename):
    """
    Exporta todos os registros da tabela 'resultados' para um arquivo CSV.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resultados")
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(headers)
        csv_writer.writerows(rows)
    
    return csv_filename

def get_all_results():
    """
    Retorna todos os registros da tabela 'resultados' como uma lista de dicionários.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resultados")
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    results = [dict(zip(headers, row)) for row in rows]
    return results
