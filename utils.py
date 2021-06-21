import QuantLib as ql
import pandas as pd


def get_basic_info(code: str) -> dict:
    # 获取左上部分信息
    basic_info = {'location': '',
                  'platform': '',
                  'quote_convention': '',
                  'category': '',
                  'settlement': ''}
    # TODO
    return basic_info


def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])
    # TODO
    return quote_df


def get_issue_date(code: str) -> float:
    pass


def get_coupon_rate(code: str) -> float:
    pass


def get_maturity_date(code: str) -> str:
    pass


def get_tenor(code: str) -> int:
    pass


def get_accrural_method(code: str) -> float:
    pass


def convert_accrural_method(accrural_method: str) -> ql.DayCounter:
    pass
