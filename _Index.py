import time, json
from lnmarkets import rest
from decouple import config
from _Telegram_Mensagem import enviarMensagem

options = {"key": config("LNM_KEY"), "secret": config("LNM_SECRET"), "passphrase": config("LNM_PASSPHRASE"), "network": config("LNM_NETWORK")}
lnm = rest.LNMarketsRest(**options)

print("Olá Mestre! Iniciando...")
print("Testando Telegram...")
enviarMensagem("Testando Telegram...")

ultimo_preco = 115_900

while True:
    try:
        ####################### ARMAZENAR ORDENS ABERTAS E MONTANTE DISPONIVEL #########################

        user_data = json.loads(lnm.get_user())
        trades_abertos = json.loads(lnm.futures_get_trades({"type": "running"}))

        ################################ PREÇO ATUAL DO BITCOIN ################################

        start = time.time()
        ticker = json.loads(lnm.futures_get_ticker())
        preco_atual = ticker["lastPrice"]
        print(f"Preço atual: {preco_atual} | Tempo: {time.time() - start:.2f}")

        ################################ ENVIANDO ORDEM DE COMPRA ################################

        preco_limite, variacao = 250_000, 0.007
        quantity, leverage = 123, 10

        if user_data["balance"] > preco_limite and abs(preco_atual - ultimo_preco) >= ultimo_preco * variacao:

            print("Variação Detectada. Enviando Ordem 🫡")
            new_trade = json.loads(lnm.futures_new_trade({"type": "m", "side": "b", "quantity": quantity, "leverage": leverage}))
            print(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
            enviarMensagem(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
            ultimo_preco = new_trade["price"]

        ################################ FECHANDO ORDENS ABERTAS ################################

        for ordem in trades_abertos:
            lucro, taxa = 0.005, 0.002
            taxa_funding = ((ordem["sum_carry_fees"] / 100000000) * preco_atual) / ordem["quantity"]

            if preco_atual > ordem["price"] * (1 + lucro + taxa + taxa_funding):
                new_close = json.loads(lnm.futures_close({"id": ordem["id"]}))
                lucro_liquido = new_close['pl'] - (new_close['opening_fee'] + new_close['closing_fee'] + new_close['sum_carry_fees'])
                print(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")
                enviarMensagem(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")

        ################################ INJETANDO MARGEM NAS OPERAÇÕES ################################

        protecao = 1.02

        for ordem in trades_abertos:
            if preco_atual < ordem["liquidation"] * protecao:
                lnm.futures_add_margin({'amount': int(ordem["margin"] / 3), 'id': ordem["id"]})
                print("PERIGO: Injetando Margem ⚠️")
                enviarMensagem("PERIGO: Injetando Margem ⚠️")

        time.sleep(1.5)

    except Exception as erro:
        print(f"❌ ERRO: {erro}")
