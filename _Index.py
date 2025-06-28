from lnmarkets import rest
from decouple import config
from _Telegram_Mensagem import enviarMensagem
import time
import json

options = {"key": config("LNM_KEY"),
           "secret": config("LNM_SECRET"),
           "passphrase": config("LNM_PASSPHRASE"),
           "network": config("LNM_NETWORK")}

lnm = rest.LNMarketsRest(**options)

print("Olá Mestre! Iniciando...")
print("Testando Telegram...")
enviarMensagem("Testando Telegram...")

ultimo_preco = 107000

while True:
    ############################## ARMAZENAR ORDENS ABERTAS E MONTANTE DISPONIVEL ##############################
    try:
        user = json.loads(lnm.get_user())
        trades_abertos = json.loads(lnm.futures_get_trades({"type": "running"}))

        ################################ PREÇO ATUAL DO BITCOIN ################################

        start = time.time()
        ticker = json.loads(lnm.futures_get_ticker())
        preco_atual = ticker["lastPrice"]
        print(f"Preço atual: {preco_atual} | Tempo: {time.time() - start:.2f}")

        ################################ ENVIANDO ORDEM DE COMPRA ################################

        if user["balance"] > 400000 and abs(preco_atual - ultimo_preco) >= 600:
            print("Variação Detectada. Enviando Ordem 🫡")
            new_trade = json.loads(lnm.futures_new_trade({"type": "m", "side": "b", "quantity": 30, "leverage": 10}))
            print(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
            enviarMensagem(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
            ultimo_preco = new_trade["price"]

        ################################ FECHANDO ORDENS ABERTAS ################################

        for ordem in trades_abertos:
            lucro_taxa = 0.005 + 0.002
            taxa_funding = ((ordem["sum_carry_fees"] / 100000000) * preco_atual) / ordem["price"]

            if preco_atual > ordem["price"] * (1 + lucro_taxa + taxa_funding):
                new_close = json.loads(lnm.futures_close({"id": ordem["id"]}))
                lucro_liquido = new_close['pl'] - (new_close['opening_fee'] + new_close['closing_fee'] + new_close['sum_carry_fees'])
                print(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")
                enviarMensagem(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")

        ################################ INJETANDO MARGEM NAS OPERAÇÕES ################################

        for ordem in trades_abertos:
            if preco_atual < ordem["liquidation"] * 1.02:
                lnm.futures_add_margin({'amount': int(ordem["margin"] / 3), 'id': ordem["id"]})
                print("PERIGO: Injetando Margem ⚠️")
                enviarMensagem("PERIGO: Injetando Margem ⚠️")

    except Exception as erro:
        print("Erro durante loop:", erro)

    time.sleep(0.8)
