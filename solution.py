import os
import folium
import requests

# Configurações da API da SPTrans
API_KEY = "9f4d1f2f53b5f131e2552c848ac28a13302a36f3f73cbe57153b381d928bf589"
BASE_URL = "http://api.olhovivo.sptrans.com.br/v2.1"
CODIGO_LINHA_TERMO = "8000"  # Linha escolhida para a atividade

session = requests.Session()

# Faz a autenticação na API
def autenticar():
    url = f"{BASE_URL}/Login/Autenticar?token={API_KEY}"
    res = session.post(url)
    if res.status_code == 200 and res.json() is True:
        print("Autenticado com sucesso!")
        return True
    print("Erro na autenticação. Confere o token aí.")
    return False

# Busca a linha e pega o código interno (cl)
def buscar_linha(termo):
    url = f"{BASE_URL}/Linha/Buscar?termosBusca={termo}"
    res = session.get(url)
    linhas = res.json()
    if linhas:
        l = linhas[0]
        print(f"Linha: {l['lt']} - {l['tp']} / {l['ts']}")
        return l['cl']
    print("Nenhuma linha encontrada.")
    return None

# Pega todas as paradas da linha
def obter_paradas(codigo_linha):
    url = f"{BASE_URL}/Parada/BuscarParadasPorLinha?codigoLinha={codigo_linha}"
    return session.get(url).json()

# Pega as posições atuais dos ônibus
def obter_posicoes(codigo_linha):
    url = f"{BASE_URL}/Posicao/Linha?codigoLinha={codigo_linha}"
    return session.get(url).json().get('vs', [])

def main():
    if not autenticar():
        return

    codigo_linha = buscar_linha(CODIGO_LINHA_TERMO)
    if not codigo_linha:
        return

    paradas = obter_paradas(codigo_linha)
    onibus = obter_posicoes(codigo_linha)

    # Centraliza o mapa na primeira parada ou em São Paulo se vier vazio
    if paradas:
        lat, lon = paradas[0]['py'], paradas[0]['px']
    else:
        lat, lon = -23.550520, -46.633308

    # Mapa configurado com Esri World Street Map (fundo limpo e sem bloqueios)
    mapa = folium.Map(
        location=[lat, lon], 
        zoom_start=13, 
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', 
        attr='Esri'
    )

    # Adiciona as paradas (pins azuis)
    print(f"Adicionando {len(paradas)} paradas...")
    for p in paradas:
        folium.Marker(
            location=[p['py'], p['px']],
            popup=f"Parada: {p.get('np', 'N/A')} (Cód: {p.get('cp', 'N/A')})",
            icon=folium.Icon(color='blue', icon='info-sign', prefix='glyphicon')
        ).add_to(mapa)

    # Adiciona os ônibus em tempo real (pins verdes)
    print(f"Adicionando {len(onibus)} ônibus...")
    for v in onibus:
        prefixo = v.get('p', 'N/A')
        horario = v.get('t', v.get('ta', 'Indisponível'))
        folium.Marker(
            location=[v['py'], v['px']],
            popup=f"Prefixo: {prefixo} - Hora: {horario}",
            icon=folium.Icon(color='green', icon='bus', prefix='fa')
        ).add_to(mapa)

    # Salva o mapa gerado
    mapa.save("mapa_onibus.html")
    print("Pronto! Mapa gerado com sucesso como 'mapa_onibus.html'.")

if __name__ == "__main__":
    main()