import sys
import traceback
from datetime import date
import requests
from stock_option_strategy.config._settings import get_api_key
from stock_option_strategy._utils.enums import *
from typing import List
import numpy as np
from scipy.stats import zscore

class AlphaData:
    curr_year = str(date.today().year)

    def __init__(self, data_enum: StockEnum, symbol):

        self.price_stack = []
        self.data = {}
        self.symbol = symbol
        self.data_enum = data_enum
        self.json_object = requests.get(f'https://www.alphavantage.co/query?function={self.data_enum.api_name}&outputsize=full&symbol={symbol}&apikey={get_api_key()}').json()

    #region adds all the necessary _data of a stock ticker from all the years
    def addData(self):
        try:
            temp_year = self.curr_year
            self.data = {"_id": self.symbol,
                         self.symbol:
                             {
                                temp_year:
                                    {
                                        self.data_enum.duration: {},
                                        "WidthData": {"positiveWidth": [], "negativeWidth": [], "avgPosWidth": 0,
                                                      "avgNegWidth": 0, "MaxPosWidth": 0, "MaxNegWidth": 0},
                                        "PercentWidthData": {"positivePC": [], "negativePC": [], "avgPosPC": 0, "avgNegPC": 0,
                                                             "MaxPosPC": 0, "MaxNegPC": 0}
                                    }
                            }

                         }
            for key, value in self.json_object[self.data_enum.data_name].items():

                year = key.split("-")[0]
                price = float(value['5. adjusted close'])

                if year not in self.data[self.symbol]:

                    self.__calcData(temp_year)
                    self.data[self.symbol][year] = {self.data_enum.duration: {},
                                                    "WidthData": {"positiveWidth": [], "negativeWidth": [],
                                                                  "avgPosWidth": 0, "avgNegWidth": 0, "MaxPosWidth": 0,
                                                                  "MaxNegWidth": 0},
                                                    "PercentWidthData": {"positivePC": [], "negativePC": [],
                                                                         "avgPosPC": 0, "avgNegPC": 0, "MaxPosPC": 0,
                                                                         "MaxNegPC": 0}
                                                    }

                    temp_year = year

                self.data[self.symbol][year][self.data_enum.duration][key] = price
                self.__addPrice(price, year)

            self.__add_prob_data()
        except Exception as e:
            print(traceback.format_exc())
            print(f"Exception: {e}")
            sys.exit(-1)

        return self.data

    #endregion

    #region Helper Methods to add to the database
    def __addPrice(self, val, year):
        try:
            if len(self.price_stack) < 2:
                self.price_stack.append(val)

            if len(self.price_stack) == 2:
                prev_price = self.price_stack.pop()
                curr_price = self.price_stack.pop()

                width = curr_price - prev_price
                perChange = self.__percentChange(prev_price, curr_price)
                if width < 0:
                    self.data[self.symbol][year]["WidthData"]["negativeWidth"].append(width)
                    self.data[self.symbol][year]["PercentWidthData"]["negativePC"].append(perChange)

                else:
                    self.data[self.symbol][year]["WidthData"]["positiveWidth"].append(width)
                    self.data[self.symbol][year]["PercentWidthData"]["positivePC"].append(perChange)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Exception: {e}")
            sys.exit(-1)

    def __calcData(self, curr_year):

        try:
            #calculate avg Positive and Negative Width
            self.data[self.symbol][curr_year]["WidthData"]["avgPosWidth"]  = self.__getAvg(self.data[self.symbol][curr_year]["WidthData"]["positiveWidth"])
            self.data[self.symbol][curr_year]["WidthData"]["avgNegWidth"]  = self.__getAvg(self.data[self.symbol][curr_year]["WidthData"]["negativeWidth"])

            #calculate max and min Width
            self.data[self.symbol][curr_year]["WidthData"]["MaxPosWidth"]  = max(self.data[self.symbol][curr_year]["WidthData"]["positiveWidth"],default=0)
            self.data[self.symbol][curr_year]["WidthData"]["MaxNegWidth"]  = min(self.data[self.symbol][curr_year]["WidthData"]["negativeWidth"],default=0)

            #calculate avg Percentage Change
            self.data[self.symbol][curr_year]["PercentWidthData"]["avgNegPC"]  = self.__getAvg(self.data[self.symbol][curr_year]["PercentWidthData"]["negativePC"])
            self.data[self.symbol][curr_year]["PercentWidthData"]["avgPosPC"]  = self.__getAvg(self.data[self.symbol][curr_year]["PercentWidthData"]["positivePC"])

            #calculate max and min Percentage Change
            self.data[self.symbol][curr_year]["PercentWidthData"]["MaxPosPC"]  = max(self.data[self.symbol][curr_year]["PercentWidthData"]["positivePC"],default=0)
            self.data[self.symbol][curr_year]["PercentWidthData"]["MaxNegPC"]  = min(self.data[self.symbol][curr_year]["PercentWidthData"]["negativePC"],default=0)

        except Exception as e:
            print(traceback.format_exc())
            print(f"Exception: {e}")
            sys.exit(-1)
    #endregion

    def __addProbKeys(self):
        self.data[self.symbol].setdefault("Probabilities", {})
        self.data[self.symbol]["Probabilities"].setdefault("Call", {})
        self.data[self.symbol]["Probabilities"].setdefault("Put", {})

    def __add_prob_data(self):
        temp_posProb_PC = []
        temp_negProb_PC = []
        db_keys = list(self.data[self.symbol].keys())[1:]
        for year in db_keys:
            try:
                temp_posProb_PC.extend(self.data[self.symbol][year]["PercentWidthData"]["positivePC"])
                temp_negProb_PC.extend(self.data[self.symbol][year]["PercentWidthData"]["negativePC"])
            except Exception as e:
                print(e)

        updated_without_outliers_POS = self.__remove_outliers_zscore(temp_posProb_PC)
        updated_without_outliers_NEG = self.__remove_outliers_zscore(temp_negProb_PC)

        self.__addProbKeys()
        listOf_Probs = [50,60,70,80,90,99]
        for probs in listOf_Probs:
            self.data[self.symbol]["Probabilities"]["Call"].setdefault(f"{probs}%", None)
            self.data[self.symbol]["Probabilities"]["Put"].setdefault(f"{probs}%", None)
            self.data[self.symbol]["Probabilities"]["Call"][f"{probs}%"] = self.__calc_positive_prob(updated_without_outliers_POS, probs)
            self.data[self.symbol]["Probabilities"]["Put"][f"{probs}%"] = self.__calc_negative_prob(updated_without_outliers_NEG, probs)

        self.data[self.symbol]["Probabilities"]["Call"].setdefault("OverallAvgPosPC", None)
        self.data[self.symbol]["Probabilities"]["Put"].setdefault("OverallAvgNegPC", None)

        self.data[self.symbol]["Probabilities"]["Call"]["OverallAvgPosPC"] = self.__getAvg(updated_without_outliers_POS)
        self.data[self.symbol]["Probabilities"]["Put"]["OverallAvgNegPC"] = self.__getAvg(updated_without_outliers_NEG)

    @staticmethod
    #region helper methods to calculate _data
    def __percentChange(t0, t1):
        if t0==0:
            return 0
        return round(((t1-t0)/t0) * 100,2)

    @staticmethod
    def __getAvg(data):
        if len(data) == 0:
            return 0
        return round(sum(data)/len(data),2)

    @staticmethod
    def __calc_negative_prob(percentData, percentage):
        percentData.sort(reverse=True)
        # Calculate the index corresponding to the given percentage
        index = int(len(percentData) * (percentage / 100))

        # Get the number at the calculated index
        return percentData[index]

    @staticmethod
    def __calc_positive_prob(percentData, percentage):
        # Sort the _data in ascending order
        percentData.sort()
        if percentage == 100:
            return percentData[-1]
        # Calculate the index corresponding to the given percentage
        index = int(len(percentData) * (percentage / 100))

        # Get the number at the calculated index
        return percentData[index]

    #endregion

    @staticmethod
    def __remove_outliers_zscore(Pdata, threshold=3) -> List:
        # Convert the list of floats to a NumPy array
        temp_data = np.array(Pdata)

        # Calculate the z-scores for each element in the array
        z_scores = zscore(temp_data)

        # Identify the indices of the outliers based on the threshold
        outlier_indices = np.where(np.abs(z_scores) > threshold)

        # Remove the outliers from the _data array
        data_without_outliers = np.delete(temp_data, outlier_indices)

        return sorted(list(data_without_outliers))

