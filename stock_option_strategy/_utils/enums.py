from enum import Enum, auto
from typing import NamedTuple

class StockEnum(NamedTuple):
    """
        Represents various properties of a stock.
    """
    api_name: str
    data_name: str
    collection_name: str
    duration: str

class TimeFrame(Enum):
    """
        Enumeration representing different time frames for stock _data.
    """
    MONTHLY = auto()
    WEEKLY = auto()
    DAILY = auto()

    def get_enum(self) -> StockEnum:
        """
            Returns a StockEnum instance corresponding to the time frame.

            Returns:
                StockEnum: The StockEnum instance corresponding to the time frame.
        """
        if self == TimeFrame.MONTHLY:
            return StockEnum("TIME_SERIES_MONTHLY_ADJUSTED", "Monthly Adjusted Time Series", "StockData_Monthly","MONTHLY")
        elif self == TimeFrame.WEEKLY:
            return StockEnum("TIME_SERIES_WEEKLY_ADJUSTED", "Weekly Adjusted Time Series", "StockData_Weekly","WEEKLY")
        elif self == TimeFrame.DAILY:
            return StockEnum("TIME_SERIES_DAILY_ADJUSTED", "Daily", "StockData_Daily","DAILY")
