import QuantLib as ql
import pandas as pd
import datetime

data_1 = pd.read_excel('data0625.xlsx', index_col=0)
data_accrued = pd.read_excel('data0625.xlsx', index_col=0)


def get_basic_info(code: str) -> dict:
    basic_info = {'location': '0',
                  'platform': '0',
                  'quote_convention': '0',
                  'category': '0',
                  'settlement': '0'}
    return basic_info


def get_interest_type(code: str) -> str:
    return '固定利率'


def get_quote(code: str) -> pd.DataFrame:
    quote_df = pd.DataFrame(None, index=['code', 'clean', 'full', 'yield'],
                            columns=['IB', 'SH', 'SZ'])
    return quote_df


def get_issue_date(code: str) -> float:
    return data_1.loc[code, '起息日期'].date().strftime('%Y-%m-%d')


def get_coupon_rate(code: str) -> float:
    return data_1.loc[code, '票面利率(当期)\n[单位] %']


def get_maturity_date(code: str) -> str:
    return data_1.loc[code, '到期日期'].date().strftime('%Y-%m-%d')


def get_frequency(code: str) -> int:
    return int(data_1.loc[code, '每年付息次数'])


def get_accrural_method(code: str) -> str:
    return "test"


def convert_accrural_method(accrural_method: str) -> ql.DayCounter:
    return ql.ActualActual()


def get_settlement(code: str) -> int:
    if code[-2:] != 'IB':
        return 1
    else:
        return 0


def get_tax_info(code: str) -> tuple:
    tax_info = data_1.loc[code, ['是否免税', '税率\n[单位] %']]
    return (tax_info.iloc[0], tax_info.iloc[1])


def get_embedded_option(code: str) -> (bool, float):
    embeddedopt = data_1.loc[code, [
        '是否含权债', '特殊条款', '赎回日', '赎回价格', '回售日', '回售价格']]

    if embeddedopt.loc['是否含权债'] == '否':
        return (False, 100.0)
    elif '赎回' in embeddedopt.loc['特殊条款']:
        return (True, embeddedopt.loc['赎回价格'])
    elif '回售' in embeddedopt.loc['特殊条款']:
        return (True, embeddedopt.loc['回售价格'])
    else:
        return (True, 100.0)


def get_embedded_option_maturity(code: str) -> str:
    if not get_embedded_option(code)[0]:
        return
    else:
        repo_date = data_1.loc[code, '回售日']
        redeem_date = data_1.loc[code, '赎回日']
        if not pd.isnull(repo_date):
            return repo_date
        elif not pd.isnull(redeem_date):
            return redeem_date
        else:
            raise Exception('不属于回售/赎回')


def get_extendable(code: str) -> bool:
    return True
