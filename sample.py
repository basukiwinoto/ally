"""
sample code using pytrader
"""
from pytrader import PyTrader

trader = PyTrader()

"""
get market time
"""
resp = trader.get_server_timestamp()
print(resp["date"])

"""
get last quote - account.yaml should look like this below

account : your_account_number
auth :
    app_key : your_app_key
    app_secret : your_app_secret
    token : your_token
    token_secret : your_token_secret
"""
import yaml
from requests_oauthlib import OAuth1


with open('account.yaml') as f:
	acct_cfg = yaml.load(f)
account = acct_cfg["account"]
auth = OAuth1(acct_cfg["auth"]["app_key"], acct_cfg["auth"]["app_secret"],
              acct_cfg["auth"]["token"], acct_cfg["auth"]["token_secret"])
trader.link_account(account, auth)

sym = "AAPL"
resp = trader.get_quote(sym)
last = float(resp["quotes"]["quote"]["last"])
print("{} {}".format(sym,last))

