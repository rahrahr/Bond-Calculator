import QuantLib as ql
import pandas as pd
from WindPy import *
import numpy as np
import datetime

w.start()
today = datetime.date.today().strftime('%Y-%m-%d')


def get_basic_info(code: str) -> dict:
    # 获取左上部分信息

    info = w.wsd(code, "exch_city,exchange_cn,sec_type", "ED0D", today)
    info2 = w.wss(code, "mktpricetype", "ShowBlank=NA")
    priceType = {'1': '净价', '2': '全价', '3': '利率', '4': '其他'}

    #info2 = w.wss(code, "coupon").Data[0][0]
    basic_info = {'location': info.Data[0][0],
                  'platform': info.Data[1][0],
                  'quote_convention': priceType[info2.Data[0][0]],
                  'category': info.Data[2][0],
                  'settlement': ''}

    return basic_info


def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])
    code_ib = w.wsd(code, "relationCode", "ED0D", today,
                    "exchangeType=NIB").Data[0][0]
    quote_ib = w.wsq(code_ib, "rt_last_cp,rt_last_dp,rt_last_ytm").Data
    quote_ib = [float(i) for i in np.ravel(quote_ib)]
    quote_ib.insert(0, code_ib)
    quote_df['IB'] = pd.Series(quote_ib, index=quote_df.index)

    code_sh = w.wsd(code, "relationCode", "ED0D", today,
                    "exchangeType=SSE").Data[0][0]
    quote_sh = w.wsq(code_sh, "rt_last_cp,rt_last_dp,rt_last_ytm").Data
    quote_sh = [float(i) for i in np.ravel(quote_sh)]
    quote_sh.insert(0, code_sh)
    quote_df['SH'] = pd.Series(quote_sh, index=quote_df.index)

    code_sz = w.wsd(code, "relationCode", "ED0D", today,
                    "exchangeType=SZSE").Data[0][0]
    quote_sz = w.wsq(code_sz, "rt_last_cp,rt_last_dp,rt_last_ytm").Data
    quote_sz = [float(i) for i in np.ravel(quote_sz)]
    quote_sz.insert(0, code_sz)
    quote_df['SZ'] = pd.Series(quote_sz, index=quote_df.index)

    return quote_df


def get_issue_date(code: str) -> float:
    return w.wss(code, "carrydate").Data[0][0].strftime('%Y-%m-%d')


def get_coupon_rate(code: str) -> float:
    return w.wss(code, "couponrate2").Data[0][0]


def get_maturity_date(code: str) -> str:
    return w.wss(code, "carryenddate").Data[0][0].strftime('%Y-%m-%d')


def get_tenor(code: str) -> int:
    return int(12/w.wss(code, "interestfrequency").Data[0][0])


def get_accrural_method(code: str) -> str:
    #w.wss(code, "actualbenchmark").Data[0][0]
    return "test"


def convert_accrural_method(accrural_method: str) -> ql.DayCounter:
    dayCount = ql.Thirty360()
    return ql.Thirty360()


def get_settlement(code: str) -> int:
    if code[-2:] != 'IB':
        return 1
    else:
        return 0


def get_tax_info(code: str) -> list:
    tax_info = w.wsd(code, "taxfree, taxrate", "ED0D", today, "").Data
    return [tax_info[0][0], tax_info[1][0]]


def get_embedded_option(code: str) -> (bool, float):
    return (False, 100)
