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
    # (sell_dirty + coupon_received) / buy_dirty

    Bond_ql = bond.bond_ql
    buy_date = ql.Date(bond.buy_date, '%Y-%m-%d')
    sell_date = ql.Date(bond.sell_date, '%Y-%m-%d')

    ql.Settings.instance().evaluationDate = buy_date
    buy_dirty = bond.buy_clean_price + Bond_ql.accruedAmount()

    ql.Settings.instance().evaluationDate = sell_date
    sell_dirty = bond.sell_clean_price + Bond_ql.accruedAmount()

    coupon_between = [c.amount() for c in Bond_ql.cashflows()
                      if buy_date < c.date() <= sell_date]
    coupon_received = sum(coupon_between)

    return (sell_dirty + coupon_received) / buy_dirty
