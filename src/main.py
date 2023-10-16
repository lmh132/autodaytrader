from models import BaseTradingBot

params = {
    'symbol' : 'PFE', #symbol of the equity you want to trade.
    'amount' : 10, #amount of shares moved per trade.
    'takeprofit' : 0.04, #target profit per trade.
    'stoploss' : -100 #maximum loss bot can incur before aborting. Use a negative number.
}

bot = BaseTradingBot(params)

if __name__ == '__main__':
    bot.run()