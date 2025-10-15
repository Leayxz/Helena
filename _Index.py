import time, json, requests
from lnmarkets import rest
from decouple import config
from _telegram import enviarMensagem

options = {"key": config("LNM_KEY"), "secret": config("LNM_SECRET"), "passphrase": config("LNM_PASSPHRASE"), "network": config("LNM_NETWORK")}
lnm = rest.LNMarketsRest(**options)

print("Olá Mestre! Iniciando...")
print("Testando Telegram...")
enviarMensagem("Testando Telegram...")

ultima_ath = 126_200
ultimo_preco = 110_619

while True:
      try:
            # BUSCA UMA VEZ ORDENS ABERTAS E MONTANTE ARMAZENAR ORDENS ABERTAS E MONTANTE DISPONIVEL
            user_data = json.loads(lnm.get_user())
            trades_abertos = json.loads(lnm.futures_get_trades({"type": "running"}))

            # PREÇO ATUAL LNM OU PRECO ATUAL BYBIT
            try:
                  start = time.time()
                  preco_atual = requests.get("https://api.lnmarkets.com/v2/futures/ticker", params = {"symbol": "BTCUSD"}).json()['lastPrice']
                  print(f"🟦 Preço Atual Ln Markets: {preco_atual} | Tempo: {time.time() - start:.2f}")
                  print(f"Saldo Atual: {user_data['balance']}")
            
            except ValueError as erro:
                  print(erro)

            except:
                  url = "https://api.bybit.com/v5/market/tickers"
                  params = {"category": "spot", "symbol": "BTCUSDT"} # Spot??
                  ticker = requests.get(url, params = params).json()['result']['list'][0]
                  preco_atual = float(ticker['lastPrice'])
                  print(f"🟧 Preço Atual Bybit: {preco_atual} | Tempo: {time.time() - start:.2f}")

            # ATUALIZA ATH
            if ultima_ath < preco_atual:
                  ultima_ath = preco_atual

            # ENVIANDO ORDEM DE COMPRA
            percentual_queda = ((ultima_ath - ultimo_preco) / ultima_ath) * 100
            preco_limite, variacao = 250_000, 0.007
            margin, leverage = 24400, 10

            if user_data['balance'] > preco_limite and abs(preco_atual - ultimo_preco) >= ultimo_preco * variacao:

                  print("Variação Detectada. Enviando Ordem 🫡")
                  new_trade = json.loads(lnm.futures_new_trade({"type": "m", "side": "b", "margin": margin, "leverage": leverage}))
                  print(f"Ordem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
                  enviarMensagem(f"🔻 Distância ATH: {percentual_queda:.2f}%\nOrdem Enviada: Compra Efetivada ✅\nPreço De Compra: {new_trade['price']} 🎯")
                  ultimo_preco = new_trade["price"]

            # FECHANDO ORDENS ABERTAS
            for ordem in trades_abertos:
                  lucro, taxa = 0.005, 0.002
                  taxa_funding = ((ordem["sum_carry_fees"] / 100000000) * preco_atual) / ordem["quantity"]

                  if preco_atual > ordem["price"] * (1 + lucro + taxa + taxa_funding):
                        new_close = json.loads(lnm.futures_close({"id": ordem["id"]}))
                        lucro_liquido = new_close['pl'] - (new_close['opening_fee'] + new_close['closing_fee'] + new_close['sum_carry_fees'])
                        print(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")
                        enviarMensagem(f"Ordem Fechada: Lucro no Bolso 🤑\nLucro Obtido: {lucro_liquido} 💰")

            # INJETANDO MARGEM NAS OPERAÇÕES
            protecao = 1.02

            for ordem in trades_abertos:
                  if preco_atual < ordem["liquidation"] * protecao:
                        lnm.futures_add_margin({'amount': int(ordem["margin"] / 3), 'id': ordem["id"]})
                        print("PERIGO: Injetando Margem ⚠️")
                        enviarMensagem("PERIGO: Injetando Margem ⚠️")

            time.sleep(1.5)

      except ValueError as erro:
            print(f'❌ Erro: {erro}')
            enviarMensagem(f"❌ ERRO: {erro}")

      except Exception as erro:
            print(f"❌ ERRO: {erro}")

# MUDANDO ABERTURA DE DOLAR PRA SATS PRA EVITAR AUMENTO CONFORME O PREÇO DESCE
