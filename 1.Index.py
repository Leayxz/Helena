from lnmarkets import rest
from decouple import config
import time
import json

options = {"key": config("LNM_KEY"),
           "secret": config("LNM_SECRET"),
           "passphrase": config("LNM_PASSPHRASE"),
           "network": config("LNM_NETWORK")}

lnm = rest.LNMarketsRest(**options)

ticker2 = json.loads(lnm.futures_get_ticker())
ultimo_preco = ticker2["lastPrice"]

                         ################## LOOP DA AUTOMAÇÃO ##################
                         
while True:
    ############################## ARMAZENAR ORDENS ABERTAS E MONTANTE DISPONIVEL ##############################
    try:
        ordens_abertas = []

        user = json.loads(lnm.get_user())
        margem_disponivel = user["balance"]
        
        trades_abertas = json.loads(lnm.futures_get_trades({"type": "running"}))
        for ordens in trades_abertas:
            if "id" in ordens and "price" in ordens and "sum_carry_fees" in ordens:
                ordens_abertas.append({"id": ordens["id"], "price": ordens["price"], "sum_carry_fees": ordens["sum_carry_fees"]})

        ################################ PREÇO ATUAL DO BITCOIN ################################
    
        ticker = json.loads(lnm.futures_get_ticker())
        preco_atual = ticker["lastPrice"]
        print("Preço atual:", preco_atual)

        ################################ ENVIANDO ORDEM DE COMPRA ################################

        if margem_disponivel > 100 and ultimo_preco < 100:
            if abs(preco_atual - ultimo_preco) >= ultimo_preco * 0.005:
                print("Variação Detectada. Enviando Ordem 🫡")
                new_trade = lnm.futures_new_trade({"type": "m", "side": "b", "quantity": 11, "leverage": 5})
                print("Ordem Enviada: Compra Efetivada ✅")
                ultimo_preco = preco_atual

        ################################ FECHANDO ORDENS ABERTAS ################################

        for ordem in ordens_abertas:
            taxa_fixa = 0.005 + 0.002
            taxa_funding = ((ordem["sum_carry_fees"] / 100000000) * preco_atual) / ordem["price"]

            if preco_atual >= ordem["price"] * (1 + taxa_fixa + taxa_funding):
                lnm.futures_close({"id": ordem["id"]})
                print("Ordem Fechada: Lucro No Bolso 🤑")

    except Exception as e:
        print("Erro durante loop:", e)

    time.sleep(1)
