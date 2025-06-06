from lnmarkets import rest
from decouple import config
import json

options = {"key": config("LNM_KEY"),
           "secret": config("LNM_SECRET"),
           "passphrase": config("LNM_PASSPHRASE"),
           "network": config("LNM_NETWORK")}

lnm = rest.LNMarketsRest(**options)

ticker2 = json.loads(lnm.futures_get_ticker())
print(ticker2)