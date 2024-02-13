import traceback

from stock_option_strategy._strategies.iron_base import IronOptionStrategyBase

from stock_option_strategy._data.db_client import DB_Client
from stock_option_strategy._utils.enums import StockEnum, TimeFrame
import datetime
import yfinance as yf

class IronCondor(IronOptionStrategyBase):

    def __init__(self, symbol, data_enum: StockEnum, prob="60%"):
        from stock_option_strategy._data.stock_db import StockDB
        """
            Initializes the IronCondor strategy.

            Args:
                symbol (str): The stock symbol for which the strategy is applied.
                data_enum (enum): An enumeration type representing the source of _data.
                prob (str): A string representing the probability level for the strategy, default is "60%".

            Attributes:
                today (datetime.date): The current date adjusted to the last trading day.
                symbol (str): The stock symbol.
                data_enum (enum): The _data enumeration type.
                prob (str): The probability level for the strategy.
                stock_db (StockDB): An instance of StockDB to interact with the stock database.
                _db: The database client used for interacting with the database.
        """

        self.today = datetime.date.today() - datetime.timedelta(days=1)
        self.symbol = symbol
        if self.__check_ticker_exists():
            self.data_enum = data_enum
            self.prob = prob
            self.stock_db = StockDB(DB_Client, data_enum)
            self._db = self.stock_db.getData(self.symbol)
            #self.curr_price = yf.Ticker(symbol).info.get('currentPrice')
            self.curr_price = round(yf.Ticker(self.symbol).get_fast_info.last_price,2)

            if self.__is_update_required():
                self.stock_db.updateData(self.symbol)
                self._db = self.stock_db.getData(self.symbol)
        else:
            raise ValueError(f"The ticker {self.symbol} does not exist. Please try another ticker")

    def __check_ticker_exists(self):
        stock_info = yf.Ticker(self.symbol)
        hist_data = stock_info.history(period="1d")
        if hist_data.empty:
            return False
        else:
            return True

    def __calcProb(self, data, maxValue, flag):
        if len(data) == 0:
            return 0
        if flag:
            count = sum(1 for d in data if d < maxValue)
        else:
            count = sum(1 for d in data if d > maxValue)
        return count / len(data) * 100

    def __is_update_required(self):
        _,recentData = self.__getCurrentPrice()
        if recentData is None:
            return True
        recentData = datetime.datetime.strptime(recentData, "%Y-%m-%d").date()
        if recentData == self.today:
            #no updates necessary
            return False
        else:
            #updates required
            return True

    def __getCurrentPrice(self):
        curr_year = str(datetime.date.today().year)
        try:
            return (next(iter(self._db[curr_year][self.data_enum.duration].values())),
                    next(iter(self._db[curr_year][self.data_enum.duration].keys())))
        except Exception as e:
            #need to update can't find the current values and keys
            return None,None

    def get_same_width_option_price(self) -> dict[str:str]:
        """
            Calculates the option price for the Iron Condor strategy with legs of the same width.

            Returns:
                float: The calculated option price.
        """

        posPC = self._db["Probabilities"]["Call"][self.prob]
        negPC = self._db["Probabilities"]["Put"][self.prob]
        last_updated_price, last_updated_date = self.__getCurrentPrice()

        if self.curr_price:
            last_updated_price = self.curr_price

        if negPC > posPC:
            Option_call = round(((last_updated_price * negPC) / 100) + last_updated_price)
            Option_put = round(last_updated_price - ((last_updated_price * negPC) / 100))
        else:
            Option_call = round(((last_updated_price * posPC) / 100) + last_updated_price)
            Option_put = round(last_updated_price - ((last_updated_price * posPC) / 100))

        result = {
            "Symbol": self.symbol,
            "Last Updated Date": last_updated_date,
            "Predicted Option Put": f"${Option_put}",
            "Last Updated Price": f"${last_updated_price}",
            "Predicted Option Call": f"${Option_call}",
            "Call Width %": f"{posPC}%",
            "Put Width %": f"{negPC}%",
            "Probability of Success": self.prob
        }
        #return [self.symbol,last_updated_date, f"${Option_put}", f"${last_updated_price}", f"${Option_call}", f"{posPC}%", f"{negPC}%", self.prob]
        return result

    def get_different_width_option_price(self) -> dict[str:str]:
        """
            Calculates the option price for the Iron Condor strategy with legs of different widths.

            Returns:
                float: The calculated option price.
        """

        posPC = self._db["Probabilities"]["Call"][self.prob]
        negPC = self._db["Probabilities"]["Put"][self.prob]
        last_updated_price, last_updated_date = self.__getCurrentPrice()

        if self.curr_price:
            last_updated_price = self.curr_price

        Option_put = round(last_updated_price + ((last_updated_price * negPC) / 100))
        Option_call = round(((last_updated_price * posPC) / 100) + last_updated_price)

        #return [self.symbol,last_updated_date, f"${Option_put}", f"${last_updated_price}", f"${Option_call}", f"{posPC}%", f"{negPC}%",  self.prob]

        result = {
        "Symbol": self.symbol,
        "Last Updated Date": last_updated_date,
        "Predicted Option Put": f"${Option_put}",
        "Last Updated Price": f"${last_updated_price}",
        "Predicted Option Call": f"${Option_call}",
        "Call Width %": f"{posPC}%",
        "Put Width %": f"{negPC}%",
        "Probability of Success": self.prob
        }

        return result