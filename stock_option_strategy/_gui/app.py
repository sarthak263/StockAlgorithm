from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QRadioButton, \
    QPushButton, QTextEdit, QGridLayout, QStatusBar, QFileDialog, QListWidget
import sys
from stock_option_strategy._data.iron_condor import IronCondor
from stock_option_strategy._utils.enums import TimeFrame


class StockAlgorithm_GUI(QWidget):
    """
        Main window class for the StockAlgorithm application.
    """
    def __init__(self):
        """
            Initializes the GUI, sets up the layout and widgets.
        """
        super().__init__()
        #self.stockHeader = ["Symbol", "Last Updated Date", "Predicated Option Put", "Last Updated Price", "Predicated Option Call", "Call width %","Put Width %"]
        self.setWindowTitle("Iron Condor Option Strategy")
        self.setGeometry(100, 100, 600, 400)
        self.generateCounter = 0
        # Setup UI
        self.init_input_elements()
        self.init_output_elements()
        self._init_ui()


    def _init_ui(self):
        layout = QVBoxLayout(self)
        grid = QGridLayout(self)

        self.add_input_elements_to_grid(grid)
        self.add_output_elements_to_grid(grid)

        layout.addLayout(grid)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def init_ticker_elements(self):
        self.lbl_ticker = QLabel("Stock Ticker:")
        self.combo_ticker = QComboBox()
        self.edit_ticker = QLineEdit()
        self.btn_add_ticker = QPushButton("Add Ticker")
        self.btn_add_ticker.clicked.connect(self.add_ticker_to_list)
        self.list_tickers = QListWidget()
        self.combo_ticker.addItems(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])  # Example tickers

    def init_prob_elements(self):
        self.lbl_prob = QLabel("Probability of Success:")
        self.combo_prob = QComboBox()
        self.combo_prob.addItems(["50%", "60%", "70%", "80%", "90%"])

    def init_timeframe_elements(self):
        self.lbl_timeframe = QLabel("Timeframe (days):")
        self.data_combo = QComboBox()
        self.data_combo.addItems(["Weekly", "Monthly"])
        self.data_combo.currentIndexChanged.connect(self.handle_data_combo_change)

        self.radio_differentWidth = QRadioButton("Different Width")
        self.radio_sameWidth = QRadioButton("Same Width")
        self.radio_sameWidth.setChecked(True)

    def init_output_elements(self):
        self.btn_generate = QPushButton("Predict Data")
        self.btn_generate.clicked.connect(self.generate_predictions)
        self.btn_save = QPushButton("Save to File")
        self.btn_save.clicked.connect(self.save_to_file)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.statusBar = QStatusBar()

    def init_input_elements(self):
        self.lbl_ticker = QLabel("Stock Ticker:")
        self.edit_ticker = QLineEdit()
        self.btn_add_ticker = QPushButton("Add Ticker")
        self.btn_add_ticker.clicked.connect(self.add_ticker_to_list)

        self.list_tickers = QListWidget()

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


    def add_ticker_elements_to_grid(self, grid):
        grid.addWidget(self.lbl_ticker, 0, 0)
        grid.addWidget(self.combo_ticker, 0, 1)


    def add_ticker_to_list(self):
        ticker = self.edit_ticker.text()
        if ticker:  # make sure ticker is not empty
            self.list_tickers.addItem(ticker)
            self.edit_ticker.clear()  # clear the line edit for next input

    def add_prob_elements_to_grid(self, grid):
        grid.addWidget(self.lbl_prob, 1, 0)
        grid.addWidget(self.combo_prob, 1, 1)

    def add_timeframe_elements_to_grid(self, grid):
        grid.addWidget(self.lbl_timeframe, 2, 0)
        grid.addWidget(self.data_combo, 2, 1)
        grid.addWidget(self.radio_differentWidth, 3, 0)
        grid.addWidget(self.radio_sameWidth, 3, 1)

    def add_output_elements_to_grid(self, grid):
        grid.addWidget(self.btn_generate, 5, 0, 1, 2)
        grid.addWidget(self.btn_save, 6, 0, 1, 2)

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

    def handle_data_combo_change(self):
        # Get the selected index of the data_combo
        index = self.data_combo.currentIndex()

        # Enable or disable the radio buttons based on the selected index
        if index == 0:  # Weekly
            self.radio_sameWidth.setEnabled(True)
            self.radio_differentWidth.setEnabled(True)
        elif index == 1:  # Monthly
            self.radio_sameWidth.setEnabled(False)
            self.radio_differentWidth.setEnabled(True)

            # If the same width radio button is disabled, set the different width radio button as checked
            if not self.radio_sameWidth.isEnabled():
                self.radio_differentWidth.setChecked(True)

    def generate_predictions(self):
        self.generateCounter+=1
        Stock_data = self.getStockDetails()
        self.printTextOutput(Stock_data)

        # Clear the status bar and show a message indicating the operation was successful
        self.statusBar.clearMessage()
        self.statusBar.showMessage("Predictions generated successfully.")

    def printTextOutput(self, stock_data):

        self.result_box.append(f"{self.generateCounter}. Stock Prediction")
        for idx, (hdr,std) in enumerate(stock_data.items(), start=1):
            self.result_box.append(f"       {idx}. {hdr}: {std}")

    def save_to_file(self):
        # Open a file dialog and get the name of the file to save to
        filename, _ = QFileDialog.getSaveFileName(self, "Save results", "", "Text Files (*.txt);;All Files (*)")

        if filename:
            # If a file was selected, open it and write the text of the result_box to it
            with open(filename, 'w') as f:
                f.write(self.result_box.toPlainText())

            # Show a success message in the status bar
            self.statusBar.showMessage(f"Results saved to {filename}.")

    def getStockDetails(self):
        ticker = self.list_tickers.currentItem().text()
        prob = self.combo_prob.currentText()
        timeframe = self.data_combo.currentText()

        if timeframe == "Weekly":
            Ic = IronCondor(ticker,TimeFrame.WEEKLY.get_enum(),prob=prob)
        else:
            Ic = IronCondor(ticker, TimeFrame.MONTHLY.get_enum(), prob=prob)

        if self.radio_sameWidth.isEnabled():
            return Ic.get_same_width_option_price()
        else:
            return Ic.get_different_width_option_price()


class StockApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = StockAlgorithm_GUI()
    def start(self):
        self.window.show()
        sys.exit((self.app.exec_()))


def show_gui():
    try:
        app = StockApp()
        app.start()
    except Exception as e:
        raise e