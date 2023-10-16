from misc import ProcessingQueue, exec, exec_interval
from config.config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH, ACCT_NUM
from td.client import TDClient

class BaseTradingBot:
    def __init__(self, symbol):
        self.client = TDClient(client_id = CONSUMER_KEY, redirect_uri= REDIRECT_URI, account_number = ACCT_NUM, credentials_path = JSON_PATH)
        self.client.login
        self.sym = symbol
        self.datastore = ProcessingQueue(60)

    def run(self):
        exec_interval(self.get_price, 5)

    def get_price(self):
        print(self.client.get_quotes([self.sym])[self.sym]['lastPrice'])


bot = BaseTradingBot('AMD')
bot.run()