# Dicionário com coordenadas de aeroportos do Brasil e extras
airport_coords = {
    "GRU": (-23.4356, -46.4731),
    "CGH": (-23.6261, -46.6561),
    "GIG": (-22.8090, -43.2506),
    "SDU": (-22.9105, -43.1630),
    "CNF": (-19.6244, -43.9714),
    "BSB": (-15.8698, -47.9208),
    "REC": (-8.1264, -34.9234),
    "CWB": (-25.5280, -49.1750),
    "SSA": (-12.9081, -38.3228),
    "FOR": (-3.7766, -38.5321),
    "POA": (-29.9939, -51.1711),
    "BEL": (-1.3792, -48.4760),
    "MAO": (-3.0386, -60.0497),
    "VCP": (-23.0076, -47.1340),
    "NAT": (-5.9111, -35.2750),
    "VIX": (-20.2584, -40.2863),
    "CGB": (-15.6015, -56.0970),
    "JFK": (40.6413, -73.7781)
}

# Função para obter a região a partir do código do aeroporto
def obter_regiao(codigo):
    mapping = {
        'GRU': 'regiao sudeste',
        'CGH': 'regiao sudeste',
        'GIG': 'regiao sudeste',
        'SDU': 'regiao sudeste',
        'CNF': 'regiao sudeste',
        'BSB': 'regiao centro-oeste',
        'REC': 'regiao nordeste',
        'CWB': 'regiao sul',
        'SSA': 'regiao nordeste',
        'FOR': 'regiao nordeste',
        'POA': 'regiao sul',
        'BEL': 'regiao norte',
        'MAO': 'regiao norte',
        'VCP': 'regiao sudeste',
        'NAT': 'regiao nordeste',
        'VIX': 'regiao sudeste',
        'CGB': 'regiao centro-oeste',
        'JFK': 'regiao internacional'
    }
    return mapping.get(codigo, 'regiao desconhecida')
