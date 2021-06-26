from dataclasses import dataclass
import sys
import QuantLib as ql
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
        self.issue_date: str = get_issue_date(code)  # YYYY-MM-DD
        self.maturity_date: str = get_maturity_date(code)  # YYYY-MM-DD
        self.coupon_rate: float = get_coupon_rate(code)
        self.tenor: ql.Period = ql.Period(get_frequency(code))  # 6M, 3M, etc
        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(
            self.accrural_method)

        # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)

        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

    def create_bond_ql(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        maturity = ql.Date(self.maturity_date, '%Y-%m-%d')
        tenor = self.tenor
        calendar = ql.NullCalendar()
        businessConvention = ql.Unadjusted
        dateGeneration = ql.DateGeneration.Backward
        monthEnd = False
        schedule = ql.Schedule(issue_date, maturity, tenor, calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   100,
                                   schedule,
                                   [self.coupon_rate/100.0],
                                   daycount_convention)

        return Bond_ql


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

        try:
            self.coupon_rate: float = get_coupon_rate(code)
        except:
            self.coupon_rate: float = 0

        self.accrural_method: str = get_accrural_method(code)
        self.day_counter: ql.DayCounter = convert_accrural_method(
            self.accrural_method)

        # 0 or 1 (correspond to T+0 or T+1)
        self.settlement: str = get_settlement(code)

        self.taxFree: str = get_tax_info(code)[0]
        self.taxRate: float = get_tax_info(code)[1]

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

    def create_bond_ql(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        maturity = ql.Date(self.maturity_date, '%Y-%m-%d')
        calendar = ql.NullCalendar()
        businessConvention = ql.Unadjusted
        dateGeneration = ql.DateGeneration.Backward
        monthEnd = False
        schedule = ql.Schedule(issue_date, maturity, ql.Period(1), calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   100,
                                   schedule,
                                   [self.coupon_rate/100.0],
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
        calendar = ql.NullCalendar()
        businessConvention = ql.Unadjusted
        dateGeneration = ql.DateGeneration.Backward
        monthEnd = False
        schedule = ql.Schedule(issue_date, option_marturity, tenor, calendar, businessConvention,
                               businessConvention, dateGeneration, monthEnd)
        daycount_convention = self.day_counter
        face_value = self.option_strike

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   face_value,
                                   schedule,
                                   # 行权时，债券相当于票面利率coupon_rate / face_value，到期时间是行权时间的债券
                                   [self.coupon_rate / face_value],
                                   daycount_convention)

        return Bond_ql
