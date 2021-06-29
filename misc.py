from bond import *
from PyQt5 import QtWidgets
import re


def create_bond_(bond_code,
                 buy_date,
                 sell_date,
                 buy_clean_price,
                 sell_clean_price,
                 ib_settlement,
                 platform,
                 category):

    bond = Bond(bond_code,
                buy_date,
                sell_date,
                float(buy_clean_price),
                float(sell_clean_price))
                
    if ql.Date(bond.maturity_date, '%Y-%m-%d') - ql.Date(bond.issue_date, '%Y-%m-%d') <= 365:
        bond = SCP(bond_code,
                   buy_date,
                   sell_date,
                   float(buy_clean_price),
                   float(sell_clean_price))

        # if bond_code[-2:] == 'IB' and ib_settlement != 0:
        bond.settlement = ib_settlement
        bond.accrued_interest_type = get_accrued_interest_type(
            platform, category)
        bond.bond_ql = bond.create_bond_ql()

    elif not get_embedded_option(bond_code)[0]:
        bond = Bond(bond_code,
                    buy_date,
                    sell_date,
                    float(buy_clean_price),
                    float(sell_clean_price))

        # if bond_code[-2:] == 'IB' and ib_settlement != 0:
        bond.settlement = ib_settlement
        bond.accrued_interest_type = get_accrued_interest_type(
            platform, category)
        bond.bond_ql = bond.create_bond_ql()
    else:
        bond = BondWithOption(bond_code,
                              buy_date,
                              sell_date,
                              float(buy_clean_price),
                              float(sell_clean_price))

        # if bond_code[-2:] == 'IB' and ib_settlement != 0:
        bond.settlement = ib_settlement
        bond.accrued_interest_type = get_accrued_interest_type(
            platform, category)
        bond.bond_ql = bond.create_bond_ql()
        bond.bond_ql_if_exercised = bond.create_bond_ql_if_exercised()
    return bond


def sanity_check_all(mainwindow, bond_code, sell_code, buy_clean_price, sell_clean_price) -> None:
    flag1 = re.match(r'^\d{6,}\.(IB|SZ|SH)$', bond_code) is not None
    flag2 = buy_clean_price.replace('.', '', 1).isdigit()
    flag3 = sell_clean_price.replace('.', '', 1).isdigit()
    flag4 = re.match(r'^\d{6,}\.(IB|SZ|SH)$', sell_code) is not None
    flags = (flag1, flag2, flag3, flag4)

    if not all(flags):
        error_messages = ('债券代码格式错误\n',
                          '买入净价不为浮点数\n',
                          '卖出净价不为浮点数\n',
                          '卖出代码格式错误')
        error_string = ''.join(
            (error_messages[i] for i in range(len(error_messages)) if not flags[i]))
        QtWidgets.QMessageBox().about(mainwindow, '错误信息', error_string)
        return False
    return True


def get_accrued_interest_type(platform: str, category: str) -> int:
    '''
    (银行间,all) = 0
    (深交所,附息债) = 1
    (深交所,贴现式国债) = 2
    (中债登,all) = 3 
    (中证登,all) = 4
    (上交所,all) = 5
    '''
    if platform == '全国银行间同业拆借中心':
        return 0
    elif platform == '深交所':
        if category == '贴现式国债':
            return 2
        else:
            return 1
    elif platform == '中债登':
        return 3
    elif platform == '中证登':
        return 4
    elif platform == '上交所':
        return 5
    else:
        return 0
