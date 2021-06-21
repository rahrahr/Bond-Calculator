from dataclasses import dataclass

import QuantLib as ql

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
        self.tenor: int = get_tenor(code)  # 6M, 3M, etc
        self.accrual_method: str = get_accrural_method(code)
        self.settlement: str = get_settlement(code) # 0 or 1 (correspond to T+0 or T+1)

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

    def create_bond_ql(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        maturity = ql.Date(self.maturity_date, '%Y-%m-%d')
        tenor = ql.Period(self.tenor, ql.Months)
        daycount_convention = self.convert_accrural_method(
            self.accrural_method)

        Bond_ql = ql.FixedRateBond(self.settlement,
                                   ql.China(),
                                   100,
                                   issue_date,
                                   maturity,
                                   tenor,
                                   [bond.coupon],
                                   daycount_convention)

        return Bond_ql
