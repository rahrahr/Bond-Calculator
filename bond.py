from dataclasses import dataclass
import sys
import QuantLib as ql
from copy import copy
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
        try:
            self.face_value: float = get_face_value(code)
        except:
            self.face_value: float = 100.0
        self.issue_date: str = get_issue_date(code)  # YYYY-MM-DD
        self.maturity_date: str = get_maturity_date(code)  # YYYY-MM-DD
        self.tenor: ql.Period = ql.Period(get_frequency(code))  # 6M, 3M, etc
        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(
            code)  # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)
        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]
        try:
            self.coupon_rate: list = get_coupon_rate(
                code, self.issue_date, self.maturity_date)
        except:
            self.coupon_rate: list = [0.0]
        self.isAmortized: bool = is_amortized(code)
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

        if self.isAmortized == True:
            Bond_ql = ql.AmortizingFixedRateBond(self.settlement,
                                                 get_notionals(
                                                     self.code, self.face_value),
                                                 schedule,
                                                 [i/100.0 for i in self.coupon_rate],
                                                 daycount_convention)
        else:
            Bond_ql = ql.FixedRateBond(self.settlement,
                                       self.face_value,
                                       schedule,
                                       [i/100.0 for i in self.coupon_rate],
                                       daycount_convention)
        return Bond_ql

    def get_accrued_amount(self, date: str) -> float:
        '''
        (银行间,all) = 0
        (深交所,贴现债) = 1
        (深交所,other) = 2
        (上交所,贴现债) = 3
        (上交所,私募债) = 4
        (上交所,其他) = 5
        '''
        date = ql.Date(date, '%Y-%m-%d')
        if self.settlement == 0:
            ql.Settings.instance().evaluationDate = date
            b = copy(self)
            b.dayCounter = ql.ActualActual(ql.ActualActual.ISMA)
            b.bond_ql = b.create_bond_ql()
            return b.bond_ql.accruedAmount()

        if self.accrued_interest_type == 0:
            ql.Settings.instance().evaluationDate = date
            b = copy(self)
            b.dayCounter = ql.ActualActual(ql.ActualActual.ISMA)
            b.bond_ql = b.create_bond_ql()
            return b.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 1:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            return self.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 2:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            b = copy(self)
            # b.dayCounter = ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
            b.dayCounter = ql.ActualActual(ql.ActualActual.ISMA)
            b.bond_ql = b.create_bond_ql()
            return b.accruedAmount()

        elif self.accrued_interest_type == 3:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            return self.bond_ql.accruedAmount()

        elif self.accrued_interest_type == 4:
            ql.Settings.instance().evaluationDate = date
            b = copy(self)
            # b.dayCounter = ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
            b.dayCounter = ql.ActualActual(ql.ActualActual.ISMA)
            b.bond_ql = b.create_bond_ql()
            return b.accruedAmount()

        elif self.accrued_interest_type == 5:
            ql.Settings.instance().evaluationDate = date - ql.Period('1D')
            b = copy(self)
            # b.dayCounter = ql.Actual365Fixed(ql.Actual365Fixed.NoLeap)
            b.dayCounter = ql.ActualActual(ql.ActualActual.ISMA)
            b.bond_ql = b.create_bond_ql()
            return b.accruedAmount()

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
        self.face_value: float = get_face_value(code)
        self.isAmortized: bool = False
        self.isDiscounted: bool = is_discounted(code)

        if self.isDiscounted:
            self.issue_price = get_issue_price(code)
            self.coupon_rate: float = [0]
        else:
            try:
                self.coupon_rate: float = get_coupon_rate(
                    code, self.issue_date, self.maturity_date)
            except:
                self.coupon_rate: float = [0]

        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(code)
        self.tenor: ql.Period = ql.Period(get_frequency(code))
        # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)

        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

        if get_embedded_option(code)[0]:
            self.option_strike = get_embedded_option(code)[1]
            self.option_marturity = get_embedded_option_maturity(code)
            self.bond_ql_if_exercised = self.create_bond_ql_if_exercised()

    def get_accrued_amount(self, date:str) -> float:
        if not self.isDiscounted:
            return super(SCP, self).get_accrued_amount(date)
        else:
            x = ql.Date(date, '%Y-%m-%d') - \
                 ql.Date(self.issue_date, '%Y-%m-%d')
            y = ql.Date(self.maturity_date, '%Y-%m-%d') - \
                ql.Date(self.issue_date, '%Y-%m-%d')
            return (100 - self.issue_price) * (x / y)

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

    def create_bond_ql_if_exercised(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        option_marturity = ql.Date(self.option_marturity, '%Y-%m-%d')
        tenor = 1
        calendar = ql.China(ql.China.IB)
        businessConvention = ql.Following
        dateGeneration = ql.DateGeneration.Forward
        monthEnd = False
        schedule = ql.Schedule(issue_date, option_marturity, ql.Period(tenor), calendar,
                               businessConvention, businessConvention,
                               dateGeneration, monthEnd)

        daycount_convention = self.day_counter
        face_value = self.option_strike

        if self.isAmortized == True:
            Bond_ql = ql.AmortizingFixedRateBond(self.settlement,
                                                 get_notionals(
                                                     self.code, self.face_value),
                                                 schedule,
                                                 [i / face_value for i in self.coupon_rate],
                                                 daycount_convention)
        else:
            Bond_ql = ql.FixedRateBond(self.settlement,
                                       self.face_value,
                                       schedule,
                                       [i / face_value for i in self.coupon_rate],
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
        dateGeneration = ql.DateGeneration.Forward
        monthEnd = False
        schedule = ql.Schedule(issue_date, option_marturity, tenor, calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter
        face_value = self.option_strike

        if self.isAmortized == True:
            Bond_ql = ql.AmortizingFixedRateBond(self.settlement,
                                                 get_notionals(
                                                     self.code, self.face_value),
                                                 schedule,
                                                 [i / face_value for i in self.coupon_rate],
                                                 daycount_convention)
        else:
            Bond_ql = ql.FixedRateBond(self.settlement,
                                       self.face_value,
                                       schedule,
                                       [i / face_value for i in self.coupon_rate],
                                       daycount_convention)
        return Bond_ql
