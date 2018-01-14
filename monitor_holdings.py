from pytrader import PyTrader
from requests_oauthlib import OAuth1
import logging
import time
import yaml

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="monitor.log")
    logger = logging.getLogger(__name__)
    trader = PyTrader(logger)

    # account config
    with open('account.yaml') as f:
        acct_cfg = yaml.load(f)
    account = acct_cfg["account"]
    auth = OAuth1(acct_cfg["auth"]["app_key"], acct_cfg["auth"]["app_secret"],
                  acct_cfg["auth"]["token"], acct_cfg["auth"]["token_secret"])
    trader.link_account(account, auth)

    while(True):
        print(time.time())
        resp = trader.get_holdings()
        holdings = resp["accountholdings"]
        for h in holdings:
            if h == "holding" and not h:
                print("{} {}".format(holdings[h]["instrument"]["sym"],holdings[h]["qty"]))
        time.sleep(1)
