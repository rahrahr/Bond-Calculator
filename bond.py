from dataclasses import dataclass
import sys
import QuantLib as ql
from copy import deepcopy
if sys.platform == 'darwin':
    from utils_test import *
else:
    from utils import *


@dataclass
class Bond:
    def __init__(self,
                 code: str,
                 buy_date: str,
                 sell_date: str,
                 buy_clean_price: float,
                 sell_clean_price: float):
        self.code: str = code
        self.buy_date: str = buy_date  # YYYY-MM-DD
        self.buy_clean_price: float = buy_clean_price
        self.sell_date: str = sell_date  # YYYY-MM-DD
        self.sell_clean_price: float = sell_clean_price

        # The following fields require WindPy to acquire.
        self.bond_type: str = get_interest_type(code)
        self.face_value: float = get_face_value(code)
        self.issue_date: str = get_issue_date(code)  # YYYY-MM-DD
        self.maturity_date: str = get_maturity_date(code)  # YYYY-MM-DD
        self.tenor: ql.Period = ql.Period(get_frequency(code))  # 6M, 3M, etc
        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(
            code)  # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)
        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]
        self.coupon_rate: list = get_coupon_rate(
            code, self.issue_date, self.maturity_date)

        self.bond_ql = self.create_bond_ql()

    def create_bond_ql(self) -> ql.FixedRateBond:
        effectiveDate = ql.Date(self.issue_date, '%Y-%m-%d')
        terminationDate = ql.Date(self.maturity_date, '%Y-%m-%d')
        tenor = self.tenor
        calendar = ql.China(ql.China.IB)
        businessConvention = ql.Following
        dateGeneration = ql.DateGeneration.Forward
        monthEnd = False
        schedule = ql.Schedule(effectiveDate, terminationDate, tenor, calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   self.face_value,
                                   schedule,
                                   [i/100.0 for i in self.coupon_rate],
                                   daycount_convention)
        return Bond_ql

    def get_accrued_amount(self, date: str) -> float:
        '''
        (银行间,all) = 0
        (深交所,附息债) = 1
        (深交所,贴现式国债) = 2
        (中债登,all) = 3
        (中证登,all) = 4
        (上交所,all) = 5
        '''
        date = ql.Date(date, '%Y-%m-%d')
        # TODO: 不同交易所应计利息计算规则
        if self.accrued_interest_type == 0:
            ql.Settings.instance().evaluationDate = date
            return self.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 1:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            b = deepcopy(self.bond_ql)
            b.dayCounter = ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
            return b.accruedAmount()

        elif self.accrued_interest_type == 2:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            return self.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 3:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            return self.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 4:
            ql.Settings.instance().evaluationDate = date
            b = deepcopy(self.bond_ql)
            b.dayCounter = ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
            return b.accruedAmount()

        elif self.accrued_interest_type == 5:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            return self.bond_ql.accruedAmount()

        else:
            ql.Settings.instance().evaluationDate = date
            return self.bond_ql.accruedAmount()

    def get_dirty_price(self, date: str, clean_price: float) -> float:
        return clean_price + self.get_accrued_amount(date)

    def get_coupon_received(self):
        # coupon_between = bond.interest_cashflow
        Bond_ql = self.bond_ql
        buy_date = ql.Date(self.buy_date, '%Y-%m-%d')
        sell_date = ql.Date(self.sell_date, '%Y-%m-%d')
        coupon_between = [c.amount() for c in self.bond_ql.cashflows()
                          if buy_date < c.date() <= sell_date]
        coupon_received = sum(coupon_between)
        if self.taxFree == '否':
            coupon_received = coupon_received * (1 - self.taxRate / 100.0)
        return coupon_received


@dataclass
class SCP(Bond):
    def __init__(self,
                 code: str,
                 buy_date: str,
                 sell_date: str,
                 buy_clean_price: float,
                 sell_clean_price: float):
        self.code: str = code
        self.buy_date: str = buy_date  # YYYY-MM-DD
        self.buy_clean_price: float = buy_clean_price
        self.sell_date: str = sell_date  # YYYY-MM-DD
        self.sell_clean_price: float = sell_clean_price

        # The following fields require WindPy to acquire.
        self.issue_date: str = get_issue_date(code)  # YYYY-MM-DD
        self.maturity_date: str = get_maturity_date(code)  # YYYY-MM-DD
        self.face_value = get_face_value(code)
        try:
            self.coupon_rate: float = get_coupon_rate(
                code, self.issue_date, self.maturity_date)
        except:
            self.coupon_rate: float = 0

        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(code)
        self.tenor: ql.Period = ql.Period(get_frequency(code))
        # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)

        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

    def create_bond_ql(self) -> ql.FixedRateBond:
        effectiveDate = ql.Date(self.issue_date, '%Y-%m-%d')
        terminationDate = ql.Date(self.maturity_date, '%Y-%m-%d')
        tenor = 1
        calendar = ql.China(ql.China.IB)
        businessConvention = ql.Following
        dateGeneration = ql.DateGeneration.Forward
        monthEnd = False
        schedule = ql.Schedule(effectiveDate, terminationDate, ql.Period(tenor), calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   self.face_value,
                                   schedule,
                                   [i/100.0 for i in self.coupon_rate],
                                   daycount_convention)
        return Bond_ql


@dataclass
class BondWithOption(Bond):
    # 含权债，不管是回售还是赎回都是提前终止然后收到一笔钱？
    def __init__(self,
                 code: str,
                 buy_date: str,
                 sell_date: str,
                 buy_clean_price: float,
                 sell_clean_price: float):

        super(BondWithOption, self).__init__(code, buy_date,
                                             sell_date,
                                             buy_clean_price,
                                             sell_clean_price)

        self.option_strike = get_embedded_option(code)[1]
        self.option_marturity = get_embedded_option_maturity(code)
        self.bond_ql_if_exercised = self.create_bond_ql_if_exercised()

    def create_bond_ql_if_exercised(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        option_marturity = ql.Date(self.option_marturity, '%Y-%m-%d')
        tenor = self.tenor
        calendar = ql.China(ql.China.IB)
        businessConvention = ql.Following
        dateGeneration = ql.DateGeneration.Backward
        monthEnd = False
        schedule = ql.Schedule(issue_date, option_marturity, tenor, calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter
        face_value = self.option_strike

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   self.face_value,
                                   schedule,
                                   [i / face_value for i in self.coupon_rate],
                                   daycount_convention)
        return Bond_ql
