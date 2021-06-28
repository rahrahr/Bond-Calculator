import re
import traceback

from PyQt5 import QtWidgets, uic

import calculator
from bond import *
import misc

if sys.platform == 'darwin':
    from utils_test import *
else:
    from utils import *


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("mainwindow.ui", self)
        self.pushButton_basicinfo.clicked.connect(self.getBasicInfo)
        self.pushButton_quote.clicked.connect(self.getQuote)
        self.pushButton_clear.clicked.connect(self.clearHPY)
        self.pushButton_hpy.clicked.connect(self.getHPY)
        self.pushButton_repo_hpy.clicked.connect(self.getRepoHPY)
        self.pushButton_clear_yield.clicked.connect(self.clearYield)
        self.pushButton_yield.clicked.connect(self.getYield)
        self.ib_settlement.valueChanged.connect(self.change_settlement)
        self.code_text.textChanged.connect(
            lambda _: self.sell_code.setText(self.code_text.text()))

    def getBasicInfo(self):
        bond_code = self.code_text.text()
        flag1 = re.match(r'^\d{6,}\.(IB|SZ|SH)$', bond_code) is None
        if flag1:
            QtWidgets.QMessageBox.about(self, "错误信息", '债券代码格式错误')
            return

        basic_info = get_basic_info(bond_code)
        self.location.setText(basic_info['location'])
        self.platform.setText(basic_info['platform'])
        self.quote_convention.setText(basic_info['quote_convention'])
        self.category.setText(basic_info['category'])
        self.settlement.setText(basic_info['settlement'])

        # The following fills out the bottom-right part of the GUI related to option.
        option = get_embedded_option(bond_code)
        if option[0]:
            self.has_option.setChecked(True)
            self.strike_price.setText('{:.4f}'.format(option[1]))

    def change_settlement(self):
        bond_code = self.code_text.text()
        flag1 = re.match(r'^\d{6,}\.(IB|SZ|SH)$', bond_code) is None
        if flag1:
            return
        if bond_code[-2:] == 'IB':
            self.settlement.setText(
                'T+{}'.format(int(self.ib_settlement.text())))

    def getQuote(self):
        bond_code = self.code_text.text()
        flag1 = re.match(r'^\d{6,}\.(IB|SZ|SH)$', bond_code) is None
        if flag1:
            QtWidgets.QMessageBox.about(self, "错误信息", '债券代码格式错误')

        quote_df = get_quote(bond_code)
        self.code_ib.setText(str(quote_df.loc['code', 'IB']))
        self.code_sh.setText(str(quote_df.loc['code', 'SH']))
        self.code_sz.setText(str(quote_df.loc['code', 'SZ']))

        self.clean_price_ib.setText(
            '{:.4f}'.format(quote_df.loc['clean', 'IB']))
        self.clean_price_sh.setText(
            '{:.4f}'.format(quote_df.loc['clean', 'SH']))
        self.clean_price_sz.setText(
            '{:.4f}'.format(quote_df.loc['clean', 'SZ']))

        self.full_price_ib.setText('{:.4f}'.format(quote_df.loc['full', 'IB']))
        self.full_price_sh.setText('{:.4f}'.format(quote_df.loc['full', 'SH']))
        self.full_price_sz.setText('{:.4f}'.format(quote_df.loc['full', 'SZ']))

        self.yield_ib.setText('{:.4f}'.format(quote_df.loc['yield', 'IB']))
        self.yield_sh.setText('{:.4f}'.format(quote_df.loc['yield', 'SH']))
        self.yield_sz.setText('{:.4f}'.format(quote_df.loc['yield', 'SZ']))

    def clearHPY(self):
        for LineEditor in self.HPY.findChildren(QtWidgets.QLineEdit):
            LineEditor.clear()

        for QDateEdit in self.HPY.findChildren(QtWidgets.QDateEdit):
            QDateEdit.setDate(QtWidgets.QDateEdit().date())

    def getHPY(self):
        # read all the data from input part of UI
        bond_code = self.code_text.text()
        buy_clean_price = self.buy_clean_price_text.text()
        buy_date = self.buy_date_text.text().replace('/', '-')
        sell_clean_price = self.sell_clean_price_text.text()
        sell_date = self.sell_date_text.text().replace('/', '-')
        sell_code = self.sell_code.text()
        ib_settlement = int(self.ib_settlement.text())

        if not misc.sanity_check_all(self, bond_code, sell_code,
                                     buy_clean_price,
                                     sell_clean_price):
            return

        try:
            bond = misc.create_bond_(bond_code, buy_date, sell_date,
                                     buy_clean_price, sell_clean_price,
                                     ib_settlement, self.platform.text(), self.category.text())

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        hpy = calculator.hpy(bond, cross_exchange=(bond_code != sell_code))
        hpy_annualized = calculator.hpy(
            bond, annualized=True, cross_exchange=(bond_code != sell_code))
        coupon_received = calculator.get_coupon_received(bond)

        self.hpy_text.setText('{:.4f}'.format(hpy * 100))
        self.hpy_annualized_text.setText('{:.4f}'.format(hpy_annualized * 100))
        self.coupon_received.setText('{:.2f}'.format(coupon_received))

    def getRepoHPY(self):
        # read all the data from input part of UI
        bond_code = self.code_text.text()
        buy_clean_price = self.buy_clean_price_text.text()
        buy_date = self.buy_date_text.text().replace('/', '-')
        sell_clean_price = self.sell_clean_price_text.text()
        sell_date = self.sell_date_text.text().replace('/', '-')
        sell_code = self.sell_code.text()
        ib_settlement = int(self.ib_settlement.text())

        if not misc.sanity_check_all(self, bond_code, sell_code,
                                     buy_clean_price,
                                     sell_clean_price):
            return

        try:
            bond = misc.create_bond_(bond_code, buy_date, sell_date,
                                     buy_clean_price, sell_clean_price,
                                     ib_settlement, self.platform.text(),
                                     self.category.text())

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        repo_hpy = calculator.repo_hpy(
            bond, cross_exchange=(bond_code != sell_code))

        repo_hpy_annualized = calculator.repo_hpy(
            bond, annualized=True, cross_exchange=(bond_code != sell_code))  # TODO

        coupon_received = calculator.get_coupon_received(bond)

        self.hpy_text.setText('{:.4f}'.format(repo_hpy * 100))
        self.hpy_annualized_text.setText(
            '{:.4f}'.format(repo_hpy_annualized * 100))
        self.coupon_received.setText('{:.4f}'.format(coupon_received))

    def clearYield(self):
        for LineEditor in self.Yield_calculation.findChildren(QtWidgets.QLineEdit):
            LineEditor.clear()

        for QDateEdit in self.Yield_calculation.findChildren(QtWidgets.QDateEdit):
            QDateEdit.setDate(QtWidgets.QDateEdit().date())

        for QCheckBox in self.Yield_calculation.findChildren(QtWidgets.QCheckBox):
            QCheckBox.setChecked(False)

    def getYield(self):
        # read all the data from input part of UI
        bond_code = self.code_text.text()
        buy_clean_price = self.clean.text()
        buy_date = self.buy_date_text_2.text().replace('/', '-')
        sell_clean_price = '100'  # Not actually used
        sell_date = '2000-01-01'  # Not actually used
        sell_code = '111111.IB'  # Not actually used
        ib_settlement = int(self.ib_settlement.text())
        has_option = self.has_option.isChecked()

        if not misc.sanity_check_all(self, bond_code, sell_code,
                                     buy_clean_price,
                                     sell_clean_price):
            return

        try:
            bond = misc.create_bond_(bond_code, buy_date, sell_date,
                                     buy_clean_price, sell_clean_price, ib_settlement, 
                                     self.platform.text(), self.category.text())

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        buy_yield = calculator.bond_yield(bond)
        self.yield_at_buy.setText('{:.4f}'.format(buy_yield * 100))
        self.accrued.setText('{:.4f}'.format(bond.bond_ql.accruedAmount()))
        self.full.setText('{:.4f}'.format(
            bond.bond_ql.accruedAmount() + float(buy_clean_price)))

        if has_option:
            buy_yield_if_exercised = calculator.bond_yield_if_exercised(bond)
            self.yield_if_exercised.setText(
                '{:.4f}'.format(buy_yield_if_exercised * 100))
