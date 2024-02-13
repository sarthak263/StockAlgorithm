import datetime
from stock_option_strategy._data.alphavantage import AlphaData
from .db_client import MongoClientWrapper
# noinspection PyProtectedMember
from stock_option_strategy._utils.enums import StockEnum #noinspection PyProtectedMember
class StockDB:

    today_date = datetime.date.today()

    def __init__(self, db_client : MongoClientWrapper , data_enum: StockEnum):
        self.db : db_client = db_client.db
        self.data_enum = data_enum
        self.curr_db = self.db[data_enum.collection_name]

    def isExist(self, symbol):
        return self.curr_db.count_documents({"_id": symbol}, limit=1) != 0

    def insertData(self,symbol):
        try:
            if not self.isExist(symbol):

                val = AlphaData(self.data_enum, symbol).addData()
                self.curr_db.insert_one(val)
        except Exception as e:
            print(f"An error occurred while inserting data for {symbol}: {str(e)}")

    def updateData(self, symbol):
        try:
            filter_data = {"_id": symbol}
            val = AlphaData(self.data_enum, symbol).addData()
            self.curr_db.update_one(filter_data, {"$set": val})
        except Exception as e:
            print(f"An error occurred while updating data for {symbol}: {str(e)}")
    def getData(self, symbol):
        try:
            self.insertData(symbol)
            return self.curr_db.find_one({"_id": symbol}, projection={"_id": 0, symbol: 1})[symbol]
        except Exception as e:
            print(f"An error occurred while retrieving data for {symbol}: {str(e)}")
            return None

    def delete_all(self):
        print("Deleting all the _data")
        self.curr_db.delete_many({})
