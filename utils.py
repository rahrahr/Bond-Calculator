import QuantLib as ql
import pandas as pd
# from WindPy import *
import time
import numpy as np

# w.start()
# today = time.strftime("%Y-%m-%d", time.localtime(time.time()))


def get_basic_info(code: str) -> dict:
    # 获取左上部分信息

    # info = w.wsd(code, "exch_city,exchange_cn,sec_type,settlementmethod",
    #              "ED0D", today, "PriceAdj=CP")
    # info = np.ravel(info.Data)
    basic_info = {'location': info[0],
                  'platform': info[1],
                  'quote_convention': '',
                  'category': info[2],
                  'settlement': ''}

    return basic_info


def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])

    # quote_ib = w.wsd(code, "trade_code,cleanprice,dirtyprice,ytm_b", "ED0D", today,
    #                  "returnType=1;TradingCalendar=NIB")
    # quote_df['IB'] = pd.Series(np.ravel(quote_ib.Data), index=quote_df.index)

    # quote_sh = w.wsd(code, "trade_code,cleanprice,dirtyprice,ytm_b", "ED0D", today,
    #                  "returnType=1;TradingCalendar=SHFE")
    # quote_df['SH'] = pd.Series(np.ravel(quote_sh.Data), index=quote_df.index)
    # quote_sz = w.wsd(code, "trade_code,cleanprice,dirtyprice,ytm_b", "ED0D", today,
    #                  "returnType=1;TradingCalendar=SZSE")
    # quote_df['SZ'] = pd.Series(np.ravel(quote_sz.Data), index=quote_df.index)

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
