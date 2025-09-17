import time, json
from lnmarkets import rest
from decouple import config
from _Telegram_Mensagem import enviarMensagem

options = {"key": config("LNM_KEY"), "secret": config("LNM_SECRET"), "passphrase": config("LNM_PASSPHRASE"), "network": config("LNM_NETWORK")}
lnm = rest.LNMarketsRest(**options)

print("Olá Mestre! Iniciando...")
print("Testando Telegram...")
enviarMensagem("Testando Telegram...")

ultimo_preco = 115_140

while True:

    ####################### ARMAZENAR ORDENS ABERTAS E MONTANTE DISPONIVEL #########################
    try:
        user_data_lnm = lnm.get_user()
        user_data = json.loads(user_data_lnm)

        trades_abertos_lnm = lnm.futures_get_trades({"type": "running"})
        trades_abertos = json.loads(trades_abertos_lnm)

        ################################ PREÇO ATUAL DO BITCOIN ################################

        start = time.time()
        ticker_lnm = lnm.futures_get_ticker()
        ticker = json.loads(ticker_lnm)
        preco_atual = ticker["lastPrice"]
        print(f"Preço atual: {preco_atual} | Tempo: {time.time() - start:.2f}")

    except Exception as erro:
        print(f"RESPOSTA USER LNM: {user_data_lnm}\n RESPOSTA TRADES LNM: {ticker_lnm}\n RESPOSTA TICKER LNM: {ticker_lnm}")
        enviarMensagem(f"RESPOSTA USER LNM: {user_data_lnm}\n RESPOSTA TRADES LNM: {ticker_lnm}\n RESPOSTA TICKER LNM: {ticker_lnm}")

        ################################ ENVIANDO ORDEM DE COMPRA ################################
        preco_limite, variacao = 250_000, 0.007
        quantity, leverage = 123, 10

        if user_data["balance"] > preco_limite and abs(preco_atual - ultimo_preco) >= ultimo_preco * variacao:
            print("Variação Detectada. Enviando Ordem 🫡")
            
            try:
                new_trade_lnm = lnm.futures_new_trade({"type": "m", "side": "b", "quantity": quantity, "leverage": leverage})
                new_trade = json.loads(new_trade_lnm)
                print(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
                enviarMensagem(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
                ultimo_preco = new_trade["price"]

            except Exception as erro:
                print(f"RESPOSTA LNM: {new_trade_lnm}. RESPOSTA NEW_TRADE_JSON: {erro}")
                enviarMensagem(f"RESPOSTA LNM: {new_trade_lnm}. RESPOSTA NEW_TRADE_JSON: {erro}")

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
