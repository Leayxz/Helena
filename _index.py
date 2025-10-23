import time, json, requests
from lnmarkets import rest
from decouple import config
from _telegram import enviarMensagem

options = {"key": config("LNM_KEY"), "secret": config("LNM_SECRET"), "passphrase": config("LNM_PASSPHRASE"), "network": config("LNM_NETWORK")}
lnm = rest.LNMarketsRest(**options)

print("🫡 Olá Mestre! Iniciando...")
print("🫡 Testando Telegram...")
enviarMensagem("🫡 Testando Telegram...")

ultima_ath = 126_200
ultimo_preco = 108_000

while True:
      try:
            # SALDO E ORDENS ABERTAS
            resposta_user = lnm.get_user()
            resposta_trades = lnm.futures_get_trades({"type": "running"})
            if 'balance' not in resposta_user or 'liquidation' not in resposta_trades: print(f"🚫 Resposta Inválida User: {resposta_user}\n🚫 Resposta Inválida Trades: {resposta_trades}"); enviarMensagem(f"🚫 Resposta Inválida Ln Markets: {resposta_user}\n🚫 Resposta Inválida Ln Markets: {resposta_trades}"); time.sleep(3); continue
            user_data = json.loads(resposta_user)
            trades_abertos = json.loads(resposta_trades)

            # PREÇO ATUAL LNM OU PRECO ATUAL BYBIT
            try:
                  start = time.time()
                  resposta = requests.get("https://api.lnmarkets.com/v2/futures/ticker", params = {"symbol": "BTCUSD"})
                  if resposta.status_code != 200: print(f"🚫 Erro Preço Ln Markets: {resposta}"); enviarMensagem(f"🚫 Erro Preço Ln Markets: {resposta}")
                  preco_atual = resposta.json()['lastPrice']
                  print(f"🟦 Preço Atual Ln Markets: {preco_atual} | Tempo: {time.time() - start:.2f}")
                  print(f"💵 Saldo Atual 7lpg5d9v1vk: {user_data['balance']}")

            except:
                  start = time.time()
                  resposta = requests.get("https://api.bybit.com/v5/market/tickers", params = {"category": "spot", "symbol": "BTCUSDT"})
                  if resposta.status_code != 200: print(f"🚫 Erro Preço Bybit: {resposta}"); enviarMensagem(f"🚫 Erro Preço Bybit: {resposta}"); continue
                  preco_atual = float(resposta.json()['result']['list'][0]['lastPrice'])
                  print(f"🟧 Preço Atual Bybit: {preco_atual} | Tempo: {time.time() - start:.2f}")
                  print(f"💵 Saldo Atual 7lpg5d9v1vk: {user_data['balance']}")

            # ATUALIZA ATH
            if ultima_ath < preco_atual:
                  ultima_ath = preco_atual

            # ENVIANDO ORDEM DE COMPRA
            percentual_queda = ((ultima_ath - preco_atual) / ultima_ath) * 100
            preco_limite, variacao = 250_000, 0.007
            margin, leverage = 12200, 10

            if user_data['balance'] > preco_limite and abs(preco_atual - ultimo_preco) >= ultimo_preco * variacao:

                  resposta_new_trade = lnm.futures_new_trade({"type": "m", "side": "b", "margin": margin, "leverage": leverage})

                  if 'price' in resposta_new_trade:
                        new_trade = json.loads(resposta_new_trade)
                        print(f"🔻 Distância ATH: {percentual_queda:.2f}%\nCompra Realizada ✅\nPreço De Compra: ${new_trade['price']} 🎯")
                        enviarMensagem(f"🔻 Distância ATH: {percentual_queda:.2f}%\nCompra Realizada ✅\nPreço De Compra: ${new_trade['price']} 🎯")
                        ultimo_preco = new_trade['price']
                  else:
                        print(f"🚫 Ordem Não Enviada: {resposta_new_trade}")
                        enviarMensagem(f"🚫 Ordem Não Enviada: {resposta_new_trade}")
                        time.sleep(3)

            # FECHANDO ORDENS ABERTAS
            for ordem in trades_abertos:
                  lucro, taxa = 0.005, 0.002
                  taxa_funding = ((ordem['sum_carry_fees'] / 100000000) * preco_atual) / ordem['quantity']

                  if preco_atual > ordem['price'] * (1 + lucro + taxa + taxa_funding):

                        resposta_close = lnm.futures_close({"id": ordem["id"]})

                        if 'opening_fee' in resposta_close:
                              new_close = json.loads(resposta_close)
                              lucro_liquido = new_close['pl'] - (new_close['opening_fee'] + new_close['closing_fee'] + new_close['sum_carry_fees'])
                              print(f"🤑 Ordem Fechada!\n💰 Lucro Obtido: 丰 {lucro_liquido}")
                              enviarMensagem(f"🤑 Ordem Fechada!\n💰 Lucro Obtido: 丰 {lucro_liquido}")
                        else:
                              print(f"🚫 Ordem Não Encerrada: {resposta_close}")
                              enviarMensagem(f"🚫 Ordem Não Encerrada: {resposta_close}")
                              time.sleep(3)

            # INJETANDO MARGEM NAS OPERAÇÕES
            protecao = 1.02

            for ordem in trades_abertos:
                  if preco_atual < ordem["liquidation"] * protecao:

                        resposta_injecao_ordem = lnm.futures_add_margin({'amount': int(ordem['margin'] / 3), 'id': ordem['id']})

                        if 'id' in resposta_injecao_ordem:
                              print(f"⚠️ Injetando Margem: {ordem['id']}")
                              enviarMensagem(f"⚠️ Injetando Margem")

                        else:
                              print(f"🚫 Margem Não Injetada: {ordem['id']} | {resposta_injecao_ordem} | Timestamp: {time.time()}")
                              enviarMensagem(f"🚫 Margem Não Injetada: {resposta_injecao_ordem}")

            time.sleep(1.5)

      except Exception as erro:
            print(f"❌ ALGO NÃO FOI TRATADO: {erro}")

# MUDANDO ABERTURA DE ORDEM DE DOLAR PRA SATS PRA EVITAR AUMENTO CONFORME O PREÇO DESCE
# O SDK NAO PERMITE CONSULTAR A RESPOSTA DA REQUISICAO