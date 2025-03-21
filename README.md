# Flight Search Automation

## Visão Geral

Este projeto tem como objetivo automatizar a busca por voos e o monitoramento de preços, integrando diversas funcionalidades para facilitar a obtenção e o armazenamento de informações relevantes. As principais funções do projeto incluem:

- **Busca de Voos:** Consulta voos utilizando dois métodos:
  - **Fast Flights:** Busca via API/módulo `pesquisa_voos`, utilizada no script `automation.py`.
  - **Playwright:** Busca assíncrona via scraping com o Playwright, utilizada no script `automation_playwright.py`, que agora utiliza o fuso horário oficial do Brasil para os dados de data/hora.
- **Cálculo de Distâncias:** Utiliza a fórmula de Haversine para calcular a distância (em km) entre aeroportos, com base nas coordenadas disponíveis.
- **Persistência de Dados:** Armazena os resultados das buscas em um banco de dados PostgreSQL, otimizando a inserção com multithreading (utilizando `ThreadPoolExecutor` no módulo `db_pg.py`) e evitando duplicidade de registros.
- **Scraping de Histórico de Preços:** Utiliza o Playwright para extrair dados de histórico de preços de voos a partir do Google Flights e gera um arquivo CSV com os resultados.
- **Mapeamento de Regiões:** Disponibiliza dados de mapeamento dos aeroportos para suas respectivas regiões (ex.: Sudeste, Sul, Nordeste).

## Funcionalidades

- **Busca Automatizada de Voos (Fast Flights):**  
  Consulta os voos com base em parâmetros definidos em `params_flights.json`, seleciona o voo mais barato e processa os dados, calculando a distância entre os aeroportos e registrando as informações retornadas.

- **Busca de Voos com Playwright:**  
  Realiza a busca de voos de forma assíncrona através do Playwright (em `automation_playwright.py`), utilizando:
  - **Fuso Horário Oficial do Brasil:** Os campos de data e hora da busca (`data_busca`, `horario_busca` e `dia_semana_busca`) são definidos conforme o fuso `America/Sao_Paulo`.
  - **Remoção da Coluna "melhor_voo":** Essa coluna foi removida dos resultados para simplificar a estrutura dos dados.

- **Otimização na Persistência de Dados:**  
  O módulo `db_pg.py` foi atualizado para realizar a inserção dos registros no banco de dados de forma otimizada, utilizando multithreading com `ThreadPoolExecutor`. Essa abordagem acelera o processo de inserção, principalmente em cenários com um grande número de registros, verificando duplicidades e realizando as operações de forma concorrente.

- **Scraping de Histórico de Preços:**  
  Utiliza o Playwright para acessar o Google Flights, expandir gráficos de histórico de preços, extrair informações relevantes e salvar os dados em um arquivo CSV (`historico_precos.csv`).

- **Mapeamento e Coordenadas:**  
  Utiliza os arquivos `regioes.json` e `airport_coords.json` para fornecer informações complementares sobre os aeroportos, como a região a que pertencem e suas coordenadas geográficas.

## Estrutura de Arquivos

- **`airport_coords.json`**  
  Contém um dicionário JSON com os códigos dos aeroportos e suas respectivas coordenadas (latitude e longitude).

- **`regioes.json`**  
  Mapeia os códigos dos aeroportos para suas respectivas regiões (ex.: "GRU": "Sudeste").

- **`params_flights.json`** (deve ser criado pelo usuário)  
  Arquivo JSON contendo os parâmetros para as buscas de voos. Exemplo:
  ```json
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
  ```

- **`automation.py`**  
  Script principal que utiliza o módulo `pesquisa_voos` para buscar voos via Fast Flights, processa os dados (incluindo cálculo de distâncias) e armazena os resultados no banco de dados.

- **`automation_playwright.py`**  
  Script alternativo que realiza a busca de voos utilizando o Playwright. Implementa a obtenção dos dados de data e hora de busca com o fuso horário oficial do Brasil e remove a coluna "melhor_voo" dos registros.

- **`db_pg.py`**  
  Módulo responsável pela conexão e operações com o banco de dados PostgreSQL. Agora inclui uma otimização na inserção dos resultados usando multithreading para acelerar as operações de gravação e verificação de duplicidade.

- **`historico_precos.py`**  
  Script que realiza o scraping de histórico de preços no Google Flights e gera um arquivo CSV com os resultados.

- **`pesquisa_voos.py`**  
  Módulo que implementa a busca de voos utilizando a API/método do pacote `fast-flights`.

- **`pesquisa_voos_playwright.py`**  
  Módulo que realiza o scraping de voos com o Playwright de forma assíncrona.

## Pré-requisitos

- **Python 3.8+**
- **PostgreSQL:** Certifique-se de ter um banco de dados PostgreSQL instalado e configurado.
- **Variáveis de Ambiente:** O acesso ao banco de dados é feito por meio de variáveis de ambiente (veja a seção de [Configuração](#configuração)).
- **Dependências do Projeto:**  
  As bibliotecas necessárias incluem:
  - `psycopg2`
  - `python-dotenv`
  - `pandas`
  - `playwright`
  - `fast-flights` (ou dependência similar para busca de voos)

## Instalação

1. **Clone o Repositório:**
   ```bash
   git clone https://github.com/XSirch/scraper-flights-automacao
   cd scraper-flights-automacao
   ```

2. **Crie e Ative um Ambiente Virtual (Opcional, mas recomendado):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instale os Navegadores do Playwright:**
   ```bash
   playwright install
   ```

## Configuração

### Variáveis de Ambiente

Configure a conexão com o banco de dados PostgreSQL através de um arquivo `.env` na raiz do projeto. Exemplo:
```
user=seu_usuario_db
password=sua_senha_db
host=seu_host_db
port=porta_db
dbname=nome_do_banco
```

### Parâmetros de Busca de Voos

Crie o arquivo `params_flights.json` com os parâmetros de busca de voos conforme o exemplo acima.

## Uso

### Executando a Busca Automatizada de Voos (Fast Flights)

Para iniciar o processo de busca de voos utilizando o método Fast Flights e salvar os resultados no banco de dados, execute:
```bash
python automation.py
```
O script realizará as seguintes ações:
- Inicializará o banco de dados (criando a tabela `resultados2` se necessário).
- Carregará os parâmetros de busca, as regiões e as coordenadas dos aeroportos.
- Buscará o voo mais barato para cada conjunto de parâmetros, calculará as distâncias e processará os dados.
- Inserirá os resultados no banco de dados, evitando registros duplicados.

### Executando a Busca de Voos com Playwright

Para utilizar o método assíncrono baseado no Playwright, execute:
```bash
python automation_playwright.py
```
As principais diferenças deste método são:
- Utiliza o Playwright para scraping dos dados de voos.
- Define os campos de data e hora da busca com o fuso horário oficial do Brasil (`America/Sao_Paulo`).
- Não inclui a coluna "melhor_voo" nos registros.

### Executando o Scraping de Histórico de Preços

Para coletar dados históricos de preços de voos a partir do Google Flights e gerar um CSV, execute:
```bash
python historico_precos.py
```
O script realizará o scraping dos gráficos de histórico de preços e salvará os dados em `historico_precos.csv`.

## Operações com o Banco de Dados

O módulo `db_pg.py` fornece as seguintes funções:
- **Inicializar o banco de dados:** `init_db()`  
  Cria a tabela `resultados2` se não existir.
- **Salvar resultados:** `salva_resultados_em_db(resultados)`  
  Insere os registros no banco de dados de forma otimizada com multithreading, evitando duplicidades.
- **Exportar dados para CSV:** `export_db_to_csv(csv_filename)`
- **Recuperar todos os registros:** `get_all_results()`

## Contribuição

Contribuições são bem-vindas! Caso deseje contribuir:
1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção de bug.
3. Envie um pull request com suas alterações.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Agradecimentos

- [fast-flights](https://github.com/AWeirdDev/flights) pelo módulo de busca de voos.
- [Playwright](https://playwright.dev/) pela automação de navegador.
- [psycopg2](https://www.psycopg.org/) para a integração com PostgreSQL.
- [python-dotenv](https://pypi.org/project/python-dotenv/) para gerenciamento de variáveis de ambiente.
