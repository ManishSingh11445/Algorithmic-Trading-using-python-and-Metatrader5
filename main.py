
import time
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import pytz
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import MetaTrader5 as mt5

class MT5_Trade:

    def __init__(self):
        self.in_position = None
        self.connect = False

    def get_trade_data(self,symbol, timeframe, utc_from, utc_to):
        if not mt5.initialize():
            print("initialize() failed")
            mt5.shutdown()

        # set time zone to UTC
        timezone = pytz.timezone("Etc/UTC")

        utc_from = datetime(2024, 1, 15,  tzinfo=timezone)
        utc_to = datetime.now()

        # get bars from BTCUSDT H1 within the interval of 2024.01.05 00:00 - 2024.01.06 23:00 in UTC time zone
        rates = mt5.copy_rates_range("EURUSD", mt5.TIMEFRAME_M15, utc_from, utc_to)



        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()

        # create DataFrame out of the obtained data
        rates_frame = pd.DataFrame(rates)


        # convert time in seconds into the 'datetime' format
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        tick_rates = rates_frame[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        # display data
        print("\nDisplay dataframe with data")
        print(tick_rates.head(10))

        tick_rates['ret'] = tick_rates.close.pct_change()
        tick_rates['price'] = tick_rates.open.shift(-1)
        print("\nDisplay dataframe with data")
        print(tick_rates.head(10))

        tick_rates['price'] = tick_rates.open.shift(-1)

        return tick_rates

    def order(symbol, lot, buy=True, id_position = None):


        # Take bid price
        bid_price = mt5.symbol_info_tick(symbol).bid

    def place_order(self, df_rates, symbol):


        import pdb;pdb.set_trace()
        login = 5021915790
        password = "Gp!sG6Ep"
        server = "MetaQuotes-Demo"

        if not self.connect:
            mt5.initialize()
            authorized = mt5.login(login, password, server)
            if authorized:
                print(authorized)
                self.connect = True


        lot = 1.0

        # Take ask price
        ask_price = mt5.symbol_info_tick(symbol).ask

        # Take bid price
        bid_price = mt5.symbol_info_tick(symbol).bid

        deviation = 10 #mt5.getSlippage(symbol)

        filling_mode = mt5.symbol_info(symbol).filling_mode - 1

        if df_rates["ret"].iloc[-1] > 0.0001:
            if not self.in_position:
                tp = ask_price * 1.002
                sl = ask_price * 0.098
                type_trade = mt5.ORDER_TYPE_BUY
                price = ask_price


                # Open the trade
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot,
                    "type": type_trade,
                    "price": price,
                    "deviation": deviation,
                    "sl": sl,
                    "tp": tp,
                    "magic": 234000,
                    "comment": "python script order",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_mode
                }
                # send a trading request

                result = mt5.order_check(request)
                print(result)
                # result = mt5.order_send(request)

            else:
                tp = bid_price * 1.002
                sl = bid_price * 0.098
                type_trade = mt5.ORDER_TYPE_SELL
                price = bid_price

                # Close the trade
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": lot,
                    "type": type_trade,
                    "position": self.in_position,
                    "price": price,
                    "deviation": deviation,
                    "magic": 234000,
                    "comment": "python script order",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": filling_mode
                }

                # send a trading request
                result = mt5.order_check(request)
                #result = mt5.order_send(request)
                result_comment = result.comment
                print(result)


# Driver Code
mt5_obj = MT5_Trade()
while True:
    df_rates = mt5_obj.get_trade_data("EURUSD",mt5.TIMEFRAME_H1,24,3)
    mt5_obj.place_order(df_rates,"EURUSD")
    time.sleep(1)

