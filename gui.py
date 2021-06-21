from PyQt5 import QtWidgets, uic
import traceback
import re
from bond import Bond
import calculator
class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("mainwindow.ui", self)
        self.pushButton.clicked.connect(self.printButtonPressed)

    def printButtonPressed(self):
        # read all the data from input part of UI
        bond_code = self.code_text.text()
        buy_clean_price = self.buy_clean_price_text.text()
        buy_date = self.buy_date_text.text().replace('/', '-')
        sell_clean_price = self.sell_clean_price_text.text()
        sell_date = self.sell_date_text.text().replace('/', '-')

        # do sanity check
        flag1 = re.match(r'^\d{6}\.(IB|SZ|SH)$', bond_code) is not None
        flag2 = buy_clean_price.replace('.', '', 1).isdigit()
        flag3 = sell_clean_price.replace('.', '', 1).isdigit()
        flags = (flag1, flag2, flag3)

        if not all(flags):
            error_messages = ('债券代码格式错误\n',
                              '买入净价不为浮点数\n',
                              '卖出净价不为浮点数')
            error_string = ''.join(
                (error_messages[i] for i in range(3) if not flags[i]))
            QtWidgets.QMessageBox.about(self, "错误信息", error_string)
            return

        try:
            bond = Bond(bond_code,
                        buy_date,
                        sell_date,
                        buy_clean_price,
                        sell_clean_price)
        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        yield_at_buy = calculator.bond_yield(bond)
        hpy = calculator.hpy(bond)
        hpy_annualized = None # TODO

        self.yield_text.setText(str(yield_at_buy))
        self.hpy_text.setText(str(hpy))
        self.hpy_annualized_text.setText(str(hpy_annualized))
