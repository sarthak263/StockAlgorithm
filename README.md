# StockAlgorithm

StockAlgorithm is a Python library designed to provide strategies, tools, and insights for stock trading, specifically focusing on the Iron Condor strategy. The library includes a variety of features such as data fetching, database management, strategy implementation, and a graphical user interface for ease of use.

## Features

- **Data Fetching**: Retrieve stock data using AlphaVantage API.
- **Database Management**: Store and manage stock data in a local database.
- **Iron Condor Strategy**: Implement the Iron Condor trading strategy, providing predictions and insights.
- **Graphical User Interface**: A user-friendly GUI for interacting with the library and fetching predictions.

## Installation

To install StockAlgorithm, you can use pip:

```bash
pip install stockalgorithm
```
## Configuration

Before you can use the StockAlgorithm library, you need to configure it with your AlphaVantage API key. Follow these steps to set it up:

1. **Create a Config Folder**: In your project directory, create a folder named `config`.
2. **Add Config File**: Inside the `config` folder, create a file named `config.toml`.
3. **Add Your API Key**: Open `config.toml` and add your AlphaVantage API key in the following format:

    ```toml
    [alphavantage]
    api_key = "your_api_key_here"
   
    [database]
    uri = "mongodb://localhost:27017/MyStockDB"
    ```

    Make sure to replace "your_api_key_here" with your actual API key.
## Reading Configuration
There are three ways this application will read the config file.
1. Setting environmental variable "STOCK_OPTION_STRATEGY_CONFIG"
2. Having the config.toml file in the same directory as your application directory. Easiest way.
3. Providing the path of the config file when calling the initialize_config("config.toml file path")

## Usage

# Run Iron Condor prediction
```
from stock_option_strategy import initialize_config, predict
initialize_config()
res = predict(ticker, "Monthly", "70%") or
res = predict_multiple_stocks([["AAPL", "Monthly", "70%"],["DIS", "Monthly", "70%"]])
```
## Contributing

Contributions to StockAlgorithm are welcome and appreciated. Whether it's reporting bugs, suggesting enhancements, or helping with code, all contributions help improve the library.

To contribute:

1. **Report Bugs**: Open an issue on our [GitHub repository](https://github.com/sarthak263/StockAlgorithm/issues) and label it as a bug.
2. **Suggest Enhancements**: Have an idea to make StockAlgorithm better? Open an issue and label it as an enhancement.
3. **Contribute Code**: Fork the repository, make your changes, and submit a pull request.

Please make sure to update tests as appropriate and follow the code of conduct.

## License

StockAlgorithm is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
