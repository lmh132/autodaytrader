from misc import ProcessingQueue, exec, exec_interval, Transactions, Trends
from datetime import datetime
from config.config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH, ACCT_NUM
from td.client import TDClient

class BaseTradingBot:
    def __init__(self, params):
        #print(params)
        self.client = TDClient(client_id = CONSUMER_KEY, redirect_uri= REDIRECT_URI, account_number = ACCT_NUM, credentials_path = JSON_PATH)
        self.client.login

        self.sym = params['symbol']
        self.amt = params['amount']
        self.tp = params['takeprofit']
        self.sl = params['stoploss']

        self.datastore = ProcessingQueue(1029)
        self.positions = 0
        self.currentprice = 0
        self.trend = Trends.RANGING
        self.orderID = None
        self.cont = False

        self.prevVar1 = 0 #previous slow HMA calculation
        self.prevVar2 = 0 #previous fast HMA calculation
        self.prevVar3 = Trends.RANGING #previous trend

    def run(self):
        while self.getTime() < 34200:
            print("awaiting market opening...")
        exec_interval(self.update, 5, self.cont)

    def update(self):
        self.currentprice = self.client.get_quotes([self.sym])[self.sym]['lastPrice']
        self.datastore.add(self.currentprice)
        self.positions = self.get_positions()
        self.cont = (self.get_profitloss() > self.sl) and (self.getTime() < 57600)
        if self.datastore.is_full():
            self.algorithm()
        else:
            print("collecting data...")

    def getTime(self):
        h = int(datetime.now().strftime("%H"))
        m = int(datetime.now().strftime("%M"))
        s = int(datetime.now().strftime("%S"))
        return 3600*h + 60*m + s
    
    def algorithm(self):
        hmaSlow = self.datastore.get_hma(sp = 30)
        hmaFast = self.datastore.get_hma(sp = 8, length = 57)
        hmaSlowSlope = hmaSlow - self.prevVar1
        hmaFastSlope = hmaFast - self.prevVar2

        match hmaSlowSlope*hmaFastSlope > 0:
            case True:
                self.trend = Trends.RALLY
            case False:
                self.trend = Trends.PULLBACK

        if self.prevVar3 == Trends.PULLBACK and self.trend == Trends.RALLY:
            if hmaSlowSlope > 0:
                self.make_transaction(Transactions.BUY, self.amt)
                self.orderID = self.make_limit(Transactions.SELL, self.amt, round(self.currentprice+self.tp, 2))
            elif hmaSlowSlope < 0:
                self.make_transaction(Transactions.SELL_SHORT, self.amt)
                self.orderID = self.make_limit(Transactions.BUY_TO_COVER, self.amt, round(self.currentprice-self.tp, 2))
        elif self.prevVar3 == Trends.RALLY and self.trend == Trends.PULLBACK:
            self.flatten()


        self.prevVar1 = hmaSlow
        self.prevVar2 = hmaFast
        self.prevVar3 = self.trend

    @exec
    def get_positions(self):
        orderList = self.client.get_accounts(fields=['positions'])[0]['securitiesAccount']['positions']
        for order in orderList:
            if order['instrument']['symbol'] == self.sym:
                return order['longQuantity'] - order['shortQuantity']
        return 0

    @exec
    def get_profitloss(self):
        if self.client.get_accounts(fields=['positions']) != None:
            orderList = self.client.get_accounts(fields=['positions'])[0]['securitiesAccount']['positions']
            for order in orderList:
                if order['instrument']['symbol'] == self.sym:
                    return int(order['currentDayProfitLoss'])
        return 0

    @exec
    def make_transaction(self, type, amt):
        order = {'orderType' : 'MARKET',
                        'session' : 'NORMAL',
                        'duration' : 'DAY',
                        'orderStrategyType' : 'SINGLE',
                        'orderLegCollection' : [{
                            'instruction' : type.name,
                            'quantity' : amt,
                            'instrument' : {
                                'symbol' : self.sym,
                                'assetType' : 'EQUITY'
                            }
                        }]}
        
        return self.client.place_order(ACCT_NUM, order)['order_id']

    @exec
    def make_limit(self, type, amt, limit):
        order = {
                    "orderType": "LIMIT",
                    "session": "NORMAL",
                    "duration": "DAY",
                    "price": limit,
                    "orderStrategyType": "SINGLE",
                    "orderLegCollection": [
                        {
                            "instruction": type.name,
                            "quantity": amt,
                            "instrument": {
                                "assetType": "EQUITY",
                                "symbol": self.sym
                            }
                        }
                    ]
                }
        return self.client.place_order(ACCT_NUM, order)['order_id']
        
    @exec
    def flatten(self):
        self.shares = self.get_positions()
        if self.shares > 0:
            self.client.cancel_order(ACCT_NUM, self.orderID)
            self.make_transaction(Transactions.SELL, self.shares)
        elif self.shares < 0:
            self.client.cancel_order(ACCT_NUM, self.orderID)
            self.make_transaction(Transactions.BUY_TO_COVER, abs(self.shares))
