import QuantLib as ql
import pandas as pd
from WindPy import *
import numpy as np
import datetime


w.start()
today = datetime.date.today().strftime('%Y-%m-%d')

test = w.wsd("210005.IB", "dailycf,dailycf_int,dailycf_prin", "2021-06-01", "2022-12-01", "ShowBlank=0").Data[1]

print(sum(test))
def get_basic_info(code: str) -> dict:
    # 获取左上部分信息

    info = w.wsd(code, "exch_city,exchange_cn,sec_type", "ED0D", today)
    info2 = w.wss(code, "mktpricetype", "ShowBlank=NA")
    priceType = {'1':'净价','2':'全价','3':'利率','4':'其他'}
    settlement = {'IB': 'T+0', 'SH': 'T+1', 'SZ': 'T+1'}

    basic_info = {'location': info.Data[0][0],
                  'platform': info.Data[1][0],
                  'quote_convention': priceType[info2.Data[0][0]],
                  'category': info.Data[2][0],
                  'settlement': settlement[code[-2:]]}

    return basic_info

def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])
    code_ib = w.wsd(code, "relationCode", "ED0D", today, "exchangeType=NIB").Data[0][0]
    if code_ib != None:
        quote_ib = w.wsq(code_ib, "rt_last_cp,rt_last_dp,rt_last_ytm", "ShowBlank=NA").Data
        quote_ib = [float(i) for i in np.ravel(quote_ib)]
        quote_ib.insert(0, code_ib)
        quote_df['IB'] = pd.Series(quote_ib, index=quote_df.index)

    code_sh = w.wsd(code, "relationCode", "ED0D", today, "exchangeType=SSE").Data[0][0]
    if code_sh != None:
        quote_sh = w.wsq(code_sh, "rt_last_cp,rt_last_dp,rt_last_ytm", "ShowBlank=NA").Data
        quote_sh = [float(i) for i in np.ravel(quote_sh)]
        quote_sh.insert(0, code_sh)
        quote_df['SH'] = pd.Series(quote_sh, index=quote_df.index)

    code_sz = w.wsd(code, "relationCode", "ED0D", today, "exchangeType=SZSE").Data[0][0]
    if code_sz != None:
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

def get_frequency(code: str) -> int:
    return w.wss(code, "interestfrequency").Data[0][0]

def get_accrural_method(code: str) -> str:
    return w.wss(code, "actualbenchmark").Data[0][0]

def convert_accrural_method(accrural_method: str) -> ql.DayCounter:
    dayCount = ql.Thirty365()
    return ql.Thirty365()

def get_settlement(code: str) -> int:
    if code[-2:] != 'IB':
        return 1
    else:
        return 0

def get_tax_info(code: str) -> list:
    tax_info = w.wsd(code, "taxfree, taxrate", "ED0D", today, "").Data
    return [tax_info[0][0], tax_info[1][0]]

def get_embedded_option(code: str) -> (bool, float):
    embeddedopt = w.wss(code, "embeddedopt").Data[0][0]
    clause = w.wss(code, "clauseabbr").Data[0][0]
    redemptionprice = w.wss(code, "redemptionprice").Data[0][0]
    redemptiondate = w.wss(code, "redemptiondate").Data[0][0]
    repurchaseprice = w.wss(code, "repurchaseprice").Data[0][0]
    repurchasedate = w.wss(code, "repurchasedate").Data[0][0]

    if embeddedopt == '否':
        return (False, 100.0)
    elif 'C' in clause:
        return (True, redemptionprice)
    elif 'P' in clause:
        return (True, repurchaseprice)
    else:
        return (True, 100.0)

def get_interest_payment_schedule(code: str, start_date: str, end_date: str) -> list:
    schedule = list(set(w.wsd(code, "nxcupn", start_date, end_date, "").Data[0]))
    schedule.sort()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    return [i for i in schedule if i >= start_date and i < end_date]

def get_interest_cashflow(code: str, start_date: str, end_date: str) -> list:
    return w.wsd(code, "dailycf_int", start_date, end_date, "ShowBlank=0").Data[0]


