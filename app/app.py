import os
import sys
import logging
import threading

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QRadioButton, \
    QPushButton, QTextEdit, QGridLayout, QStatusBar, QFileDialog, QListWidget, QMessageBox
from stock_option_strategy._utils.enums import TimeFrame
from stock_option_strategy._cli import initialize_config

# Setup logging to log into 'stock_app.log' file with the specified format
logging.basicConfig(filename='stock_app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('numexpr').setLevel(logging.WARNING)
class CustomEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, callback):
        super().__init__(CustomEvent.EVENT_TYPE)
        self.callback = callback

# Business Logic Handler
class StockAlgorithm:
    def get_stock_details(self, ticker, prob, timeframe, is_diff):
        from stock_option_strategy._data.iron_condor import IronCondor

        try:
            if timeframe == "Weekly":
                Ic = IronCondor(ticker, TimeFrame.WEEKLY.get_enum(), prob=prob)
            else:
                Ic = IronCondor(ticker, TimeFrame.MONTHLY.get_enum(), prob=prob)

            if not is_diff:
                return Ic.get_same_width_option_price()
            else:
                return Ic.get_different_width_option_price()
        except ValueError as e:
            print(e)
            return {}

    def save_predictions(self, filename, data):
        # Save the prediction data to a file
        with open(filename, 'w') as f:
            f.write(data)


# GUI Class
def show_error_message(message):
    error_dialog = QMessageBox()
    error_dialog.setWindowTitle("Error")
    error_dialog.setText(message)
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.exec_()

class StockAlgorithm_GUI(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iron Condor Option Strategy")
        self.setGeometry(100, 100, 600, 400)
        self.generateCounter = 0

        self.stock_algorithm = StockAlgorithm()  # Business logic handler

        # Initialize UI components
        self.init_input_elements()
        self.init_output_elements()
        self.init_ui()
    def customEvent(self, a0: 'QEvent') -> None:
        if a0.type() == CustomEvent.EVENT_TYPE:
            a0.callback()

    def init_ui(self):
        layout = QVBoxLayout()
        grid = QGridLayout()

        self.add_input_elements_to_grid(grid)
        self.add_output_elements_to_grid(grid)

        layout.addLayout(grid)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def init_input_elements(self):
        self.lbl_ticker = QLabel("Stock Ticker:")
        self.edit_ticker = QLineEdit()
        self.btn_add_ticker = QPushButton("Add Ticker")
        self.btn_add_ticker.clicked.connect(self.add_ticker_to_list)
        self.list_tickers = QListWidget()
        self.list_tickers.addItems(["AAPL","NFLX","MSFT","MRK","DIS","PEP","V","UNH","LLY","WMT","CAT","JNJ","CSCO"])

        self.lbl_prob = QLabel("Probability of Success:")
        self.combo_prob = QComboBox()
        self.combo_prob.addItems(["50%", "60%", "70%", "80%", "90%"])

        self.lbl_timeframe = QLabel("Timeframe (days):")
        self.data_combo = QComboBox()
        self.data_combo.addItems(["Weekly", "Monthly"])
        self.data_combo.currentIndexChanged.connect(self.handle_data_combo_change)

        self.radio_sameWidth = QRadioButton("Same Width")
        self.radio_sameWidth.setChecked(True)
        self.radio_differentWidth = QRadioButton("Different Width")

    def init_output_elements(self):
        self.btn_generate = QPushButton("Predict Data")
        self.btn_generate.clicked.connect(self.generate_predictions)
        self.btn_save = QPushButton("Save to File")
        self.btn_save.clicked.connect(self.save_to_file)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.statusBar = QStatusBar()

    def add_input_elements_to_grid(self, grid):
        grid.addWidget(self.lbl_ticker, 0, 0)
        grid.addWidget(self.edit_ticker, 0, 1)
        grid.addWidget(self.btn_add_ticker, 0, 2)
        grid.addWidget(self.list_tickers, 1, 0, 1, 3)
        grid.addWidget(self.lbl_prob, 2, 0)
        grid.addWidget(self.combo_prob, 2, 1)
        grid.addWidget(self.lbl_timeframe, 3, 0)
        grid.addWidget(self.data_combo, 3, 1)
        grid.addWidget(self.radio_sameWidth, 4, 0)
        grid.addWidget(self.radio_differentWidth, 4, 1)

    def add_output_elements_to_grid(self, grid):
        grid.addWidget(self.btn_generate, 5, 0, 1, 2)
        grid.addWidget(self.btn_save, 6, 0, 1, 2)

    def add_ticker_to_list(self):
        ticker = self.edit_ticker.text()
        if ticker:
            self.list_tickers.addItem(ticker)
            self.edit_ticker.clear()

    def handle_data_combo_change(self):
        index = self.data_combo.currentIndex()
        self.radio_sameWidth.setEnabled(index == 0)
        self.radio_differentWidth.setChecked(index == 1)

    def generate_predictions(self):
        self.generateCounter += 1
        ticker = self.list_tickers.currentItem().text()
        prob = self.combo_prob.currentText()
        timeframe = self.data_combo.currentText()

        # Perform long-running tasks in a thread to keep GUI responsive
        threading.Thread(target=self.threaded_prediction, args=(ticker, prob, timeframe)).start()

    def threaded_prediction(self, ticker, prob, timeframe):

        try:
            Stock_data = self.stock_algorithm.get_stock_details(ticker, prob, timeframe, self.radio_differentWidth.isEnabled())
            if Stock_data:
                # Make sure to update the GUI from the main thread
                QApplication.postEvent(self, CustomEvent(lambda: self.printTextOutput(Stock_data)))
            else:
                QApplication.postEvent(self, CustomEvent(
                    lambda: show_error_message("Ticker not found. Please try another ticker")))
        except Exception as e:
            QApplication.postEvent(self, CustomEvent(
                lambda: show_error_message("An error occurred while generating predictions.")))
            logging.exception("Error generating predictions: %s", e)

    def printTextOutput(self, stock_data):
        self.result_box.append(f"{self.generateCounter}. Stock Prediction")
        for idx, (hdr, std) in enumerate(stock_data.items(), start=1):
            self.result_box.append(f"       {idx}. {hdr}: {std}")

    def save_to_file(self):
        try:
            # Open a file dialog and get the name of the file to save to
            filename, _ = QFileDialog.getSaveFileName(self, "Save results", "", "Text Files (*.txt);;All Files (*)")

            if filename:
                # If a file was selected, open it and write the text of the result_box to it
                self.stock_algorithm.save_predictions(filename,self.result_box.toPlainText())

                # Show a success message in the status bar
                self.statusBar.showMessage(f"Results saved to {filename}.")
                logging.info(f"Results saved to {filename}.")
        except Exception as e:
            logging.exception("Failed to save file: %s",e)
            QMessageBox.critical(self,"Save Failed",f"An error occurred while saving the file: {e}")

    # Custom Event to handle thread-safe GUI updates

class StockApp:
    def __init__(self):
        initialize_config(r"config.toml")
        self.app = QApplication(sys.argv)
        self.window = StockAlgorithm_GUI()

    def start(self):
        self.window.show()
        sys.exit(self.app.exec_())


# Function to run the GUI
def show_gui():
    try:
        app = StockApp()
        app.start()
    except Exception as e:
        logging.exception("An unexpected error occurred in the GUI application.")
        error_message = f"Sorry, the application encountered an unexpected error: {e}"
        error_details = f"Please check the 'stock_app.log' file for more details. Error: {str(e)}"

        # Show a user-friendly message via a QMessageBox
        show_error_message(error_details+error_message)
        # Exit the application with a non-zero exit code to indicate an error
        sys.exit(1)


# Run the application if this file is executed
if __name__ == "__main__":
    show_gui()