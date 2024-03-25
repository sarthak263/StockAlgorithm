import os
import toml
import inspect
class _ConfigReader:
    def __init__(self,config_path=None):
        if config_path is None:
            raise ValueError("Config past must be provided. Please specify the path to your configuration file ")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at {config_path}")

        self.config_path = config_path
        self.config = toml.load(self.config_path)
    def _get_caller_module_name(self):
        # Skip frames to find the module name of the actual caller
        frame = inspect.currentframe()
        while frame:
            module = inspect.getmodule(frame)
            if module and module.__name__ != __name__:
                return module.__name__
            frame = frame.f_back
        return None

    def _get_api_key(self):
        caller_name = self._get_caller_module_name()
        if caller_name and caller_name == 'stock_option_strategy._data.alphavantage':
            return self.config["alphavantage"]["api_key"]
        else:
            raise PermissionError("ACCESS DENIED: API_KEY is private!")

    def _get_database_uri(self):
        caller_name = self._get_caller_module_name()
        if caller_name and caller_name == 'stock_option_strategy._data.db_client':
            return self.config["database"]["uri"]
        else:
            raise PermissionError("ACCESS DENIED: Database_uri is private!")

_config_reader : _ConfigReader = None

'''
def config_initialization(config_path=None):
    global _config_reader
    _config_reader = _ConfigReader(config_path)
'''

def get_api_key():
    if _config_reader is not None:
        return _config_reader._get_api_key()
    else:
        raise RuntimeError("ConfigReader not initialized. Please call initialize_config() first.")

def get_database_uri():
    if _config_reader is not None:
        return _config_reader._get_database_uri()
    else:
        raise RuntimeError("ConfigReader not initialized. Please call initialize_config() first.")