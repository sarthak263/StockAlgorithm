import traceback

import stock_option_strategy.config as conf
import os
def initialize_config(config_path: str=None):
    """
       Initializes the application configuration by searching for the configuration file in several locations.

       Parameters:
       - config_path (str, optional): The path to the configuration file. If not provided, the function will look
         for the configuration file in the environment variable "STOCK_OPTION_STRATEGY_CONFIG", current working directory,
          "config.toml" and user's home directory "~/.config/stock_option_strategy/config.toml".

       Raises:
       - FileNotFoundError: If the configuration file cannot be found in any of the searched locations.
    """
    if config_path is None:
        #os environment variable
        env_config_path = os.environ.get('STOCK_OPTION_STRATEGY_CONFIG')
        if env_config_path:
            config_path = env_config_path

        if config_path is None:
            # Check if config.toml exists in the current working directory
            cwd_config_path = os.path.join(os.getcwd(), 'config.toml')
            if os.path.isfile(cwd_config_path):
                config_path = cwd_config_path
            else:
                # 2. Check in the user's home directory
                home_config_path = os.path.expanduser('~/.config/stock_option_strategy/config.toml')
                if os.path.isfile(home_config_path):
                    config_path = home_config_path

        if config_path is None:
            raise FileNotFoundError("Configuration file not found. Please provide a valid path to your configuration file.")

    conf._settings._config_reader = conf._settings._ConfigReader(config_path)


def predict_multiple_stocks(stock_list: list):
    """
        Predicts the option prices for multiple stocks using the Iron Condor strategy based on given parameters for each stock.

        Parameters:
        - stock_list (list): A list of lists, where each inner list contains parameters for a single stock prediction:
          ['Ticker', 'Timeframe', 'Probability'].

        Returns:
        - list: A list of dictionaries with the prediction results or error messages for each stock.
    """
    predictions = []

    # Loop through each set of stock parameters in the list
    for stock_params in stock_list:
        if len(stock_params) != 3:
            # Handle incorrect parameter count
            predictions.append(
                {"Error": "Invalid number of parameters provided. Expected ['Ticker', 'Timeframe', 'Probability']."})
            continue

        ticker, timeframe, probability = stock_params

        # Call the existing predict function with the current set of parameters
        try:
            result = predict(ticker, timeframe, probability)
            # Assuming predict() now returns a dictionary or an error message string
            if isinstance(result, str):
                predictions.append({"Ticker": ticker, "Error": result})
            else:
                predictions.append(result)
        except Exception as e:
            # Catch any unexpected errors during prediction
            predictions.append({"Ticker": ticker, "Error": f"An error occurred during prediction: {str(e)}"})

    return predictions

def predict(ticker: str, timeframe: str="MONTHLY", probability: str="70%"):
    """
        Predicts the option prices using the Iron Condor strategy for a given stock ticker, timeframe, and probability.

        Parameters:
        - ticker (str): The stock ticker symbol.
        - timeframe (str): The prediction timeframe, either 'MONTHLY' or 'WEEKLY'.
        - probability (str): The probability as a percentage, e.g., '70%'.

        Returns:
        - str: A message with the prediction result or an error message.

        Raises:
        - RuntimeError: If the configuration is not initialized.
        - ValueError: For invalid timeframe or probability format.
    """

    def validate_timeframe(tf: str) -> bool:
        """
        Validates the given timeframe.

        Parameters:
        - timeframe (str): The timeframe to validate.

        Returns:
        - bool: True if the timeframe is valid, False otherwise.
        """
        return tf.upper() in ["MONTHLY", "WEEKLY"]

    def validate_probability(prob: str) -> bool:
        """
        Validates the given probability format.

        Parameters:
        - probability (str): The probability to validate.

        Returns:
        - bool: True if the probability format is valid, False otherwise.
        """
        return prob.endswith("%") or not prob[:-1].isdigit()

    if conf._settings._config_reader is None:
        raise RuntimeError("Configuration not initialized. Please call initialize_config() first.")

    from stock_option_strategy._data.iron_condor import IronCondor, TimeFrame
    # Validate timeframe
    if timeframe.upper() not in ["MONTHLY", "WEEKLY"]:
        return "Invalid timeframe. Please enter either 'Monthly' or 'Weekly'."

    # Validate probability format
    if not validate_probability(probability):
        return "Invalid probability format. Please enter the probability as a percentage, e.g., '70%'."

    try:
        ticker = ticker.upper()
        iron_condor = IronCondor(ticker, TimeFrame[timeframe.upper()].get_enum(), prob=probability)
        return iron_condor.get_different_width_option_price()
    except KeyError:
        return f"Invalid timeframe or probability. Please enter 'Monthly' or 'Weekly' as the timeframe. and probability format is 70%. {traceback.format_exc()}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
if __name__ == "__main__":
        pass