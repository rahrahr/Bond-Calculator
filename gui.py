import re
import traceback

from PyQt5 import QtWidgets, uic

import calculator
from bond import Bond
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

    def getBasicInfo(self):
        bond_code = self.code_text.text()
        flag1 = re.match(r'^\d{6}\.(IB|SZ|SH)$', bond_code) is None
        if flag1:
            QtWidgets.QMessageBox.about(self, "错误信息", '债券代码格式错误')

        basic_info = get_basic_info(bond_code)
        self.location.setText(basic_info['location'])
        self.platform.setText(basic_info['platform'])
        self.quote_convention.setText(basic_info['quote_convention'])
        self.category.setText(basic_info['category'])
        self.settlement.setText(basic_info['settlement'])

        # The following fills out the bottom-right part of the GUI related to option.
        option = get_embedded_option(code)
        if option[0]:
            self.has_option.setChecked(True)
            self.strike_price.setText('{:.4f'.format(option[1]))
            
    def getQuote(self):
        bond_code = self.code_text.text()
        flag1 = re.match(r'^\d{6}\.(IB|SZ|SH)$', bond_code) is None
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
        ib_settlement = int(self.ibsettlement.text())

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
                        float(buy_clean_price),
                        float(sell_clean_price))

            if bond_code[-2:] =='IB' and ib_settlement != 0:
                bond.settlement = ib_settlement
                bond.bond_ql = bond.create_bond_ql()

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        hpy = calculator.hpy(bond)
        hpy_annualized = calculator.hpy(bond, annualized=True)  # TODO
        coupon_received = calculator.get_coupon_received(bond)

        self.hpy_text.setText('{:.4f}'.format(hpy))
        self.hpy_annualized_text.setText('{:.4f}'.format(hpy_annualized))
        self.coupon_received.setText('{:.4f}'.format(coupon_received))

    def getRepoHPY(self):
        # read all the data from input part of UI
        bond_code = self.code_text.text()
        buy_clean_price = self.buy_clean_price_text.text()
        buy_date = self.buy_date_text.text().replace('/', '-')
        sell_clean_price = self.sell_clean_price_text.text()
        sell_date = self.sell_date_text.text().replace('/', '-')
        ib_settlement = int(self.ibsettlement.text())

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
                        float(buy_clean_price),
                        float(sell_clean_price))
            if bond_code[-2:] == 'IB' and ib_settlement != 0:
                bond.settlement = ib_settlement
                bond.bond_ql = bond.create_bond_ql()

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        repo_hpy = calculator.repo_hpy(bond)
        repo_hpy_annualized = calculator.repo_hpy(
            bond, annualized=True)  # TODO
        coupon_received = calculator.get_coupon_received(bond)

        self.hpy_text.setText('{:.4f}'.format(repo_hpy))
        self.hpy_annualized_text.setText('{:.4f}'.format(repo_hpy_annualized))
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
        sell_clean_price = 100  # Not actually used
        sell_date = '2000-01-01'  # Not actually used
        ib_settlement = int(self.ibsettlement.text())

        # do sanity check
        flag1 = re.match(r'^\d{6}\.(IB|SZ|SH)$', bond_code) is not None
        flag2 = buy_clean_price.replace('.', '', 1).isdigit()
        flags = (flag1, flag2)

        if not all(flags):
            error_messages = ('债券代码格式错误\n',
                              '买入净价不为浮点数\n')
            error_string = ''.join(
                (error_messages[i] for i in range(2) if not flags[i]))
            QtWidgets.QMessageBox.about(self, "错误信息", error_string)
            return

        try:
            bond = Bond(bond_code,
                        buy_date,
                        sell_date,
                        float(buy_clean_price),
                        float(sell_clean_price))
            if bond_code[-2:] == 'IB' and ib_settlement != 0:
                bond.settlement = ib_settlement
                bond.bond_ql = bond.create_bond_ql()

        except Exception:
            QtWidgets.QMessageBox.about(self, "错误信息", traceback.format_exc())
            return

        buy_yield = calculator.bond_yield(bond)
        self.yield_at_buy.setText('{:.4f}'.format(buy_yield))
        self.accrued.setText('{:.4f}'.format(bond.bond_ql.accruedAmount()))
        self.full.setText('{:.4f}'.format(
            bond.bond_ql.accruedAmount() + buy_clean_price))
