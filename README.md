Segue abaixo o conteúdo completo do arquivo README.md que inclui todo o conteúdo da resposta:

```markdown
# Flight Search Automation

## Visão Geral

Este projeto tem como objetivo automatizar a busca por voos e o monitoramento de preços, integrando diferentes funcionalidades:
- **Busca de Voos:** Lê parâmetros de busca de um arquivo JSON, consulta o voo mais barato para cada rota (utilizando uma função externa `search_flights`), calcula a distância entre aeroportos e processa os dados retornados.
- **Armazenamento em Banco de Dados:** Salva os resultados da busca em um banco de dados PostgreSQL, evitando duplicidade de registros.
- **Scraping de Histórico de Preços:** Utiliza o Playwright para extrair dados de histórico de preços de voos a partir do Google Flights e gera um arquivo CSV com os resultados.
- **Informações de Aeroportos:** Disponibiliza dados sobre coordenadas de aeroportos e mapeamento de regiões.

## Funcionalidades

- **Busca Automatizada de Voos:** Consulta os voos com base em parâmetros definidos em um arquivo `params_flights.json` e seleciona o voo mais barato.
- **Cálculo de Distâncias:** Utiliza a fórmula de Haversine para calcular a distância (em km) entre dois aeroportos, caso suas coordenadas estejam disponíveis.
- **Persistência de Dados:** Salva os resultados das buscas em um banco PostgreSQL, realizando verificação para evitar inserção de registros duplicados.
- **Scraping de Histórico de Preços:** Realiza scraping de gráficos de histórico de preços no Google Flights, extraindo informações relevantes e exportando os dados para CSV.
- **Mapeamento de Regiões:** Fornece um mapeamento dos aeroportos para suas respectivas regiões (ex.: Sudeste, Sul, Nordeste).

## Estrutura de Arquivos

- **`airport_coords.json`**  
  Contém um dicionário JSON com os códigos dos aeroportos e suas respectivas coordenadas (latitude e longitude).

- **`airports.py`**  
  Define um dicionário com as coordenadas dos aeroportos e a função `obter_regiao(codigo)`, que retorna a região associada ao código do aeroporto.

- **`automation.py`**  
  Script principal que:
  - Carrega os parâmetros de busca a partir do arquivo `params_flights.json` (arquivo a ser criado).
  - Carrega o mapeamento de regiões (`regioes.json`) e as coordenadas dos aeroportos (`airport_coords.json`).
  - Realiza a busca do voo mais barato para cada conjunto de parâmetros.
  - Calcula a distância entre os aeroportos utilizando a fórmula de Haversine.
  - Registra os resultados no banco de dados PostgreSQL utilizando funções do módulo `db_postgres.py`.

- **`db_postgres.py`**  
  Módulo responsável pela conexão com o banco PostgreSQL e operações como:
  - Inicialização do banco de dados e criação da tabela `resultados` (caso não exista).
  - Inserção dos registros de resultados, com verificação para evitar duplicidade.
  - Exportação dos dados para um arquivo CSV.
  - Recuperação de todos os registros da tabela.

- **`historico_precos.py`**  
  Script que realiza scraping de histórico de preços no Google Flights utilizando o Playwright, extraindo informações dos gráficos de preço e salvando os dados em um arquivo CSV.

- **`regioes.json`**  
  Contém um mapeamento em JSON dos códigos dos aeroportos para suas respectivas regiões (ex.: "GRU": "Sudeste").

- **`params_flights.json`** (não incluso – deve ser criado)  
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

## Pré-requisitos

- **Python 3.8+**
- **PostgreSQL:** Certifique-se de ter um banco de dados PostgreSQL instalado e configurado.
- **Variáveis de Ambiente:** O acesso ao banco de dados é feito por meio de variáveis de ambiente (veja a seção de [Configuração](#configuração)).
- **Dependências do Projeto:** As bibliotecas necessárias incluem:
  - `psycopg2`
  - `python-dotenv`
  - `pandas`
  - `playwright`

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
   Em seguida, instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instale os Navegadores do Playwright:**
   Após instalar o pacote do Playwright, execute:
   ```bash
   playwright install
   ```

## Configuração

### Variáveis de Ambiente

Configure a conexão com o banco de dados PostgreSQL através de um arquivo `.env` na raiz do projeto. Exemplo de conteúdo:
```
user=seu_usuario_db
password=sua_senha_db
host=seu_host_db
port=porta_db
dbname=nome_do_banco
```

### Parâmetros de Busca de Voos

Crie o arquivo `params_flights.json` na raiz do projeto com os parâmetros de busca. Exemplo:
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

### Outros Arquivos de Configuração

- **`regioes.json`:** Mapeia os códigos dos aeroportos para suas respectivas regiões.
- **`airport_coords.json`:** Contém as coordenadas dos aeroportos.

Certifique-se de que estes arquivos estejam presentes e formatados corretamente.

## Uso

### Executando a Busca Automatizada de Voos

Para iniciar o processo de busca de voos e salvar os resultados no banco de dados, execute:
```bash
python automation.py
```
O script realizará as seguintes ações:
- Inicializará o banco de dados (criando a tabela `resultados` se necessário).
- Carregará os parâmetros de busca, as regiões e as coordenadas dos aeroportos.
- Realizará a busca do voo mais barato para cada conjunto de parâmetros.
- Calculará a distância entre os aeroportos e processará os dados retornados.
- Inserirá os resultados no banco de dados, evitando registros duplicados.

### Executando o Scraping de Histórico de Preços

Para coletar dados históricos de preços de voos a partir do Google Flights e gerar um CSV, execute:
```bash
python historico_precos.py
```
O script fará o seguinte:
- Construirá a URL de busca para o Google Flights com base nos parâmetros informados.
- Usará o Playwright para abrir a página, expandir o gráfico de histórico de preços e extrair os dados relevantes.
- Salvará os dados extraídos em um arquivo CSV chamado `historico_precos.csv`.

### Operações com o Banco de Dados

O módulo `db_postgres.py` fornece funções para:
- **Inicializar o banco de dados:** `init_db()`
- **Salvar resultados:** `salva_resultados_em_db(resultados)` (verifica duplicidades antes da inserção)
- **Exportar dados para CSV:** `export_db_to_csv(csv_filename)`
- **Recuperar todos os registros:** `get_all_results()`

Você pode importar e utilizar essas funções em outros scripts conforme necessário.

## Solução de Problemas

- **Erros de Conexão com o Banco de Dados:**  
  Verifique se as variáveis de ambiente estão definidas corretamente e se o servidor PostgreSQL está em execução.

- **Problemas com o Playwright:**  
  Certifique-se de que os navegadores necessários foram instalados com `playwright install` e que a versão do Playwright é compatível.

- **Módulo `pesquisa_voos`:**  
  O script `automation.py` importa a função `search_flights` do módulo `pesquisa_voos`. Garanta que este módulo esteja disponível e implementado corretamente no seu ambiente.

## Contribuição

Contribuições são bem-vindas! Caso deseje contribuir:
1. Faça um fork do repositório.
2. Crie uma branch para a sua feature ou correção de bug.
3. Envie um pull request com suas alterações.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Agradecimentos

- [Playwright](https://playwright.dev/) para automação de navegador.
- [psycopg2](https://www.psycopg.org/) para integração com PostgreSQL.
- [python-dotenv](https://pypi.org/project/python-dotenv/) para gerenciamento de variáveis de ambiente.
```
