from dataclasses import dataclass
import QuantLib as ql


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
        self.issue_date: str = self.get_issue_date(code)  # YYYY-MM-DD
        self.maturity_date: str = self.get_maturity_date(code)  # YYYY-MM-DD
        self.coupon_rate: float = self.get_coupon_rate(code)
        self.tenor: int = self.get_tenor(code)  # 6M, 3M, etc
        self.accrual_method: str = self.get_accrural_method(code)

        self.bond_ql = self.create_bond_ql()  # 创建QuantLib Bond类

    @staticmethod
    def get_issue_date(code: str) -> float:
        pass

    @staticmethod
    def get_coupon_rate(code: str) -> float:
        pass

    @staticmethod
    def get_maturity_date(code: str) -> str:
        pass

    @staticmethod
    def get_tenor(code: str) -> int:
        pass

    @staticmethod
    def get_accrural_method(code: str) -> float:
        pass

    @staticmethod
    def convert_accrural_method(accrural_method: str) -> ql.DayCounter:
        pass

    def create_bond_ql(self) -> ql.FixedRateBond:
        issue_date = ql.Date(self.issue_date, '%Y-%m-%d')
        maturity = ql.Date(self.maturity_date, '%Y-%m-%d')
        tenor = ql.Period(self.tenor, ql.Months)
        daycount_convention = self.convert_accrural_method(
            self.accrural_method)

        Bond_ql = ql.FixedRateBond(0,
                                   ql.China(),
                                   100,
                                   issue_date,
                                   maturity,
                                   tenor,
                                   [bond.coupon],
                                   daycount_convention)

        return Bond_ql
