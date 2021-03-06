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
        error_messages = ('????????????????????????\n',
                          '???????????????????????????\n',
                          '???????????????????????????\n',
                          '????????????????????????')
        error_string = ''.join(
            (error_messages[i] for i in range(len(error_messages)) if not flags[i]))
        QtWidgets.QMessageBox().about(mainwindow, '????????????', error_string)
        return False
    return True


def get_accrued_interest_type(platform: str, category: str) -> int:
    '''
        (?????????,all) = 0
        (?????????,?????????) = 1
        (?????????,other) = 2
        (?????????,?????????) = 3
        (?????????,?????????) = 4
        (?????????,??????) = 5
    '''
    if platform == '?????????????????????????????????':
        return 0
    elif '???' in platform:
        if '??????' in category:
            return 1
        else:
            return 2
    elif '???' in platform:
        if '??????' in category:
            return 3
        elif '??????' in category:
            return 4
        else:
            return 5
    else:
        return 0
