import requests
from requests_oauthlib import OAuth1
import time
import json
import logging

"""
class PyTrader sends order to linked account
"""
class PyTrader:
	account = "1234" # account number
	auth = OAuth1('YOUR_APP_KEY',
				  'YOUR_APP_SECRET',
				  'USER_OAUTH_TOKEN', 
				  'USER_OAUTH_TOKEN_SECRET') #API auth

	"""
	link_account sets account number (string) and auth (OAuth1 object)
	"""
	def link_account(self, account, auth):
		self.account = account
		self.auth = auth
		return True
	
	"""
	send_order sends order in fixml string format to broker
	"""
	def send_order(self, order_fixml_string):
		endpoint = "https://api.tradeking.com/v1"
		command = "accounts/{}/orders".format(self.account)
		url = "".join([endpoint,"/",command,".json"])
		start = time.time()
		response = requests.post(url, auth=self.auth, data=order_fixml_string)
		end = time.time()
		self.logger.info("send order:{}:{}".format(end-start,response.content))
		return True

	"""
	get_holdings queries the assets held in the portfolio
	"""
	def get_holdings(self):
		endpoint = "https://api.tradeking.com/v1"
		command = "accounts/{}/holdings".format(self.account)
		url = "".join([endpoint,"/",command,".json"])
		start = time.time()
		response = requests.get(url, auth=self.auth)
		end = time.time()
		self.logger.info("get holdings:{}:{}".format(end-start,response.content))
		data = json.loads(response.content.decode('utf-8'))
		return data["response"]

	"""
	get_qty_in_holdings get the qty in the portfolio for specific symbol
	"""
	def get_qty_in_holdings(self, sym):
		resp = self.get_holdings()
		holdings = resp["accountholdings"]
		for h in holdings:
			if h == "holding" and not h:
				print(holdings[h]["instrument"]["sym"])
				print(holdings[h]["qty"])
				if holdings[h]["instrument"]["sym"] == sym:
					return int(holdings[h]["qty"])
		return 0 # no assets in holdings
	
	"""
	buy_limit sends buy limit order with max_amount money for symbol sym at max_price
	"""
	def buy_limit(self, max_amount, sym, max_price):
		order = OrderTicket()
		order.prepare_buy_limit_order(self.account, max_price, 
									  sym, int(max_amount/max_price))
		self.send_order(order.tostring())
		return True
	
	"""
	sell_stop sends sell stop order for symbol sym at stop_price
	qty = -1 means all
	"""
	def sell_stop(self, sym, stop_price, qty=-1):
		order = OrderTicket()
		if qty < 0:
			qty = self.get_qty_in_holdings(sym)
		if qty == 0: # no assets in holding
			return False
		order.prepare_sell_stop_order(self.account, stop_price, sym, qty)
		self.send_order(order.tostring())
		return True
	
	"""
	sell_limit sends sell limit order for symbol sym at min_price
	qty = -1 means all
	"""
	def sell_limit(self, sym, min_price, qty=-1):
		order = OrderTicket()
		if qty <0:
			qty = self.get_qty_in_holdings(sym)
		if qty == 0: # no assets in holding
			return False
		order.prepare_sell_limit_order(self.account, min_price, sym, qty)
		self.send_order(order.tostring())
		return True

	"""
	get_quote queries last quote for symbol sym
	"""
	def get_quote(self, sym):
		endpoint = "https://api.tradeking.com/v1"
		command = "market/ext/quotes"
		url = "".join([endpoint,"/",command,".json?symbols=",sym])
		start = time.time()
		response = requests.get(url, auth=self.auth)
		end = time.time()
		self.logger.info("get quote:{}:{}".format(end-start,response.content))
		data = json.loads(response.content.decode('utf-8'))
		return data["response"]
	
	"""
	get_server_timestamp queries server timestamp
	"""
	def get_server_timestamp(self):
		endpoint = "https://api.tradeking.com/v1"
		command = "market/clock"
		url = "".join([endpoint,"/",command,".json"])
		start = time.time()
		response = requests.get(url)
		end = time.time()
		self.logger.info("get server timestamp:{}:{}".format(end-start,response.content))
		data = json.loads(response.content.decode('utf-8'))
		return data["response"]
	
	"""
	init with logger
	"""
	def __init__(self, logger=None):
		logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename="pytrader.log")
		self.logger = logger or logging.getLogger(__name__)

		
		

"""
class OrderTicket prepares order in fixml format
"""
class OrderTicket:
	order_fixml = ""
	
	"""
	tostring() returns the order string in fixml format
	"""
	def tostring(self):
		return self.order_fixml
	
	"""
	prepare_buy_limit_order prepares buy limit order in fixml format
	"""
	def prepare_buy_limit_order(self, account, price, sym, qty):
		buy_limit_order = '<?xml version="1.0" encoding="UTF-8"?> \
			<FIXML xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2"> \
				<Order Acct="{}" Side="1" Typ="2" Px="{}" TmInForce="0"> \
					<Instrmt SecTyp="CS" Sym="{}"/> \
					<OrdQty Qty="{}"/> \
				</Order> \
			</FIXML>'.format(account, price, sym, qty)
		self.order_fixml = buy_limit_order
		return True
	
	"""
	prepare_sell_stop_order prepares sell stop order in fixml format 
	"""
	def prepare_sell_stop_order(self, account, price, sym, qty):
		sell_stop_order = '<?xml version="1.0" encoding="UTF-8"?> \
			<FIXML xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2"> \
				<Order Acct="{}" Side="2" Typ="3" StopPx="{}" TmInForce="0"> \
					<Instrmt SecTyp="CS" Sym="{}"/> \
					<OrdQty Qty="{}"/> \
				</Order> \
			</FIXML>'.format(account, price, sym, qty)
		self.order_fixml = sell_stop_order
		return True
	
	"""
	prepare_sell_limit_order prepares sell limit order in fixml format
	"""
	def prepare_sell_limit_order(self, account, price, sym, qty):
		sell_limit_order = '<?xml version="1.0" encoding="UTF-8"?> \
			<FIXML xmlns="http://www.fixprotocol.org/FIXML-5-0-SP2"> \
				<Order Acct="{}" Side="2" Typ="2" Px="{}" TmInForce="0"> \
					<Instrmt SecTyp="CS" Sym="{}"/> \
					<OrdQty Qty="{}"/> \
				</Order> \
			</FIXML>'.format(account, price, sym, qty)
		self.order_fixml = sell_limit_order
		return True
		
if __name__ == '__main__':
	print("pytrader")
	trader = PyTrader()
	resp = trader.get_server_timestamp()
	print(resp["date"])
	
