import QuantLib as ql
import pandas as pd
from WindPy import *
import numpy as np
import datetime

w.start()
today = datetime.date.today().strftime('%Y-%m-%d')


def get_basic_info(code: str) -> dict:
    # 获取左上部分信息

    info = w.wss(
        code, "exch_city,exchange_cn,windl2type,mktpricetype", "ShowBlank=NA")
    priceType = {'1': '净价', '2': '全价', '3': '利率', '4': '其他'}
    settlement = {'IB': 'T+0', 'SH': 'T+1', 'SZ': 'T+1'}

    basic_info = {'location': info.Data[0][0],
                  'platform': info.Data[1][0],
                  'quote_convention': priceType[info.Data[3][0]],
                  'category': info.Data[2][0],
                  'settlement': settlement[code[-2:]]}

    return basic_info


def get_full_name(code: str) -> str:
    return ''


def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])
    code_ib = w.wss(code, "relationCode", "exchangeType=NIB").Data[0][0]
    if code_ib != None:
        quote_ib = w.wsq(
            code_ib, "rt_last_cp,rt_last_dp,rt_last_ytm", "ShowBlank=NA").Data
        quote_ib = [float(i) for i in np.ravel(quote_ib)]
        quote_ib.insert(0, code_ib)
        quote_df['IB'] = pd.Series(quote_ib, index=quote_df.index)

    code_sh = w.wss(code, "relationCode", "exchangeType=SSE").Data[0][0]
    if code_sh != None:
        quote_sh = w.wsq(
            code_sh, "rt_last_cp,rt_last_dp,rt_last_ytm", "ShowBlank=NA").Data
        quote_sh = [float(i) for i in np.ravel(quote_sh)]
        quote_sh.insert(0, code_sh)
        quote_df['SH'] = pd.Series(quote_sh, index=quote_df.index)

    code_sz = w.wss(code, "relationCode", "exchangeType=SZSE").Data[0][0]
    if code_sz != None:
        quote_sz = w.wsq(code_sz, "rt_last_cp,rt_last_dp,rt_last_ytm").Data
        quote_sz = [float(i) for i in np.ravel(quote_sz)]
        quote_sz.insert(0, code_sz)
        quote_df['SZ'] = pd.Series(quote_sz, index=quote_df.index)

    return quote_df


def get_interest_type(code: str) -> str:
    return w.wss(code, "interesttype").Data[0][0]


def get_face_value(code: str) -> float:
    if w.wss(code, "par").Data[0][0] != None:
        return w.wss(code, "par").Data[0][0]
    else:
        return 100.0


def get_issue_date(code: str) -> float:
    return w.wss(code, "carrydate").Data[0][0].strftime('%Y-%m-%d')


def get_coupon_rate(code: str, start_date: str, end_date: str) -> list:
    coupon_rate = w.wsd(code, "couponrate3", start_date,
                        end_date, "ShowBlank=0").Data[0]
    if coupon_rate != None:
        return coupon_rate
    else:
        return [0.0]


def get_maturity_date(code: str) -> str:
    return w.wss(code, "carryenddate").Data[0][0].strftime('%Y-%m-%d')


def get_frequency(code: str) -> int:
    if w.wss(code, "interestfrequency").Data[0][0] != None:
        return w.wss(code, "interestfrequency").Data[0][0]
    else:  # 零息票券
        return 0


def get_accrural_method(code: str) -> str:
    return w.wss(code, "actualbenchmark").Data[0][0]


def convert_accrural_method(code: str) -> ql.DayCounter:
    if get_accrural_method(code) == 'ACT/ACT':
        return ql.ActualActual()
    elif get_accrural_method(code) == 'A/365F':
        return ql.Thirty365()
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


def get_redemption(code: str) -> (bool, float, str):
    embeddedopt = w.wss(code, "embeddedopt").Data[0][0]
    clause = w.wss(code, "clauseabbr").Data[0][0]
    redemptionprice = w.wss(code, "redemptionprice").Data[0][0]
    redemptiondate = w.wss(code, "redemptiondate").Data[0][0]

    if 'C' in clause:
        return (True, redemptionprice, redemptiondate)
    else:
        return (False, 100.0, '2021-12-31')


def get_repurchase(code: str) -> (bool, float):
    embeddedopt = w.wss(code, "embeddedopt").Data[0][0]
    clause = w.wss(code, "clauseabbr").Data[0][0]
    repurchaseprice = w.wss(code, "repurchaseprice").Data[0][0]
    repurchasedate = w.wss(code, "repurchasedate").Data[0][0]

    if 'P' in clause:
        return (True, repurchaseprice, repurchasedate)
    else:
        return (True, 100.0, '2021-12-31')


def get_embedded_option_maturity(code: str) -> str:
    return '2021-12-31'


def get_extendable(code: str) -> bool:
    # 是否可延期
    return False


def is_amortized(code: str) -> bool:
    return w.wss(code, "prepayportion", "serial=1").Data[0][0] == None


def is_discounted(code: str) -> bool:
    return '贴现' in w.wss(code, "coupon")


def get_notionals(code: str, face_value: float) -> list:
    prepayment = []
    calendar = ql.China(ql.China.IB)

    for i in range(1, 10):
        prepayment_data = w.wss(
            code, "prepaymentdate,prepayportion", "serial="+str(i)).Data
        if prepayment_data[0][0] > datetime.datetime(2000, 1, 1, 0, 0):
            date = ql.Date(prepayment_data[0][0].strftime(
                '%Y-%m-%d'), '%Y-%m-%d')
            date = calendar.adjust(date, ql.Following)
            payment = face_value * prepayment_data[1][0] / 100.0
            prepayment.append((date, payment))

    effectiveDate = ql.Date(get_issue_date(code), '%Y-%m-%d')
    terminationDate = ql.Date(get_maturity_date(code), '%Y-%m-%d')
    tenor = ql.Period(get_frequency(code))
    businessConvention = ql.Following
    dateGeneration = ql.DateGeneration.Forward
    monthEnd = False
    schedule = ql.Schedule(effectiveDate, terminationDate, tenor, calendar, businessConvention,
                           businessConvention, dateGeneration, monthEnd)

    notionals_map = {k: face_value for k in list(schedule)}
    remain_notionals = face_value
    for i in prepayment:
        date = i[0]
        prepayment_amount = i[1]
        for key in notionals_map.keys():
            if key >= date:
                notionals_map[key] = remain_notionals - prepayment_amount
        remain_notionals = remain_notionals - prepayment_amount

    return list(notionals_map.values())


def get_issue_price(code: str) -> float:
    return w.wss(code, "coupon,issue_issueprice")

# notionals = get_notionals("101655025.IB", 100.0)#list(notionals_map.values())#[100,100,100,50]
#bond = ql.AmortizingFixedRateBond(0, notionals[0], notionals[1], [0.0358], ql.Thirty360())
# bond.cashflows()
#print([c.amount() for c in bond.cashflows()])
#print([c.date() for c in bond.cashflows()])
