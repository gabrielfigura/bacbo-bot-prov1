import requests
from bs4 import BeautifulSoup
import time
import telegram
import os

# Token e chat_id do Telegram
TOKEN = "8163319902:AAHE9LZ984JCIc-Lezl4WXR2FsGHPEFTxRQ"
CHAT_ID = "-1002597090660"
bot = telegram.Bot(token=TOKEN)

# Histórico das últimas jogadas
historico = []

# Função para obter os dados da página
def obter_resultados():
    url = "https://casinoscores.com/es/bac-bo/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        resultados = soup.select(".dice-box .dice-red, .dice-box .dice-blue")
        pares = []
        for i in range(0, len(resultados), 2):
            dado1 = int(resultados[i].text.strip())
            dado2 = int(resultados[i+1].text.strip())
            soma1, soma2 = dado1, dado2
            if soma1 > soma2:
                pares.append("🔴")  # Banker
            elif soma2 > soma1:
                pares.append("🔵")  # Player
            else:
                pares.append("🟡")  # TIE
        return pares
    except Exception as e:
        print("Erro ao obter resultados:", e)
        return []

# Lógica para calcular confiança com base em padrão
def calcular_confianca(padrao):
    if padrao == "surf":
        return 95
    elif padrao in ["3:1", "3:2"]:
        return 88
    elif padrao == "2:2":
        return 83
    elif padrao == "alternancia":
        return 80
    else:
        return 75

# Lógica para detectar padrões
def analisar_padroes(historico):
    if len(historico) < 8:
        return None

    ultimos = historico[-8:]

    # Padrão 3:1
    if ultimos[-4:] == ["🔵", "🔵", "🔵", "🔴"] or ultimos[-4:] == ["🔴", "🔴", "🔴", "🔵"]:
        return "alerta_3:1"

    # Confirmação padrão 3:1
    if historico[-8:] == ["🔵", "🔵", "🔵", "🔴", "🔵", "🔵", "🔵", "🔴"]:
        return "3:1"

    # Padrão 3:2
    if historico[-5:] in [["🔵", "🔵", "🔵", "🔴", "🔴"], ["🔴", "🔴", "🔴", "🔵", "🔵"]]:
        return "3:2"

    # Alternância
    if historico[-6:] in [
        ["🔵", "🔴", "🔵", "🔴", "🔵", "🔴"],
        ["🔴", "🔵", "🔴", "🔵", "🔴", "🔵"]
    ]:
        return "alternancia"

    # Surf
    if historico[-6:] == ["🔵"] * 6 or historico[-6:] == ["🔴"] * 6:
        return "surf"

    # Padrão 2:2 com repetição e inversão
    if historico[-8:] == ["🔵", "🔵", "🔴", "🔴", "🔵", "🔵", "🔴", "🔴"]:
        return "2:2"

    return None

# Enviar mensagem para o Telegram
def enviar_mensagem(texto):
    try:
        bot.send_message(chat_id=CHAT_ID, text=texto)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

# Loop principal
def main():
    global historico
    enviado_3_1 = False
    while True:
        resultados = obter_resultados()
        if resultados and resultados != historico:
            for r in resultados:
                if r not in historico:
                    historico.append(r)
            if len(historico) > 100:
                historico = historico[-100:]

            padrao = analisar_padroes(historico)
            if padrao == "alerta_3:1" and not enviado_3_1:
                enviar_mensagem("⚠️ Padrão 3:1 se formando...")
                enviado_3_1 = True
            elif padrao == "3:1":
                enviar_mensagem("🎲 Padrão 3:1 confirmado!")
                enviar_mensagem(f"""
🎯 Novo sinal Bac Bo ao vivo:
Entrada: {historico[-1]*3}
Protege o TIE🟡
Validade: 1 minuto
Confiança: {calcular_confianca('3:1')}%
""")
                enviado_3_1 = False
            elif padrao:
                tipo = historico[-1]
                enviar_mensagem(f"""
🎲 Padrão {padrao} detectado!

🎯 Entrada: {tipo*3}
Protege o TIE🟡
Validade: 1 minuto
Confiança: {calcular_confianca(padrao)}%
""")
        time.sleep(5)

if __name__ == "__main__":
    main()
