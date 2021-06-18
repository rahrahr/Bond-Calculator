import QuantLib as ql
from bond import Bond


def bond_yield(bond: Bond) -> float:

    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')

    Bond_ql = bond.bond_ql

    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.DayCounter(),
                             ql.Compounded,
                             Bond_ql.frequency())


def hpy(bond: Bond) -> float:
    # (dirty_sell + interest_received) / dirty_buy
    pass