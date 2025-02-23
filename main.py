from pyscript import fetch

response = await fetch(
#    "https://examples.pyscriptapps.com/api-proxy-tutorial/api/proxies/status-check",
    "https://api.nbp.pl/api/exchangerates/rates/A/USD/2020-06-29/",
    method="GET"
).json()


print(response)
