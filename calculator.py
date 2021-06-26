import QuantLib as ql
from bond import *


def bond_yield(bond: Bond) -> float:
    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    Bond_ql = bond.bond_ql
    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.dayCounter(),
                             ql.CompoundedThenSimple,
                             Bond_ql.frequency())


def bond_yield_if_exercised(bond: BondWithOption) -> float:
    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    Bond_ql = bond.bond_ql_if_exercised
    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.dayCounter(),
                             ql.CompoundedThenSimple,
                             Bond_ql.frequency())


def hpy(bond: Bond, annualized: bool = False) -> float:
    # (sell_dirty + coupon_received) / buy_dirty - 1
    Bond_ql = bond.bond_ql
    buy_date = ql.Date(bond.buy_date, '%Y-%m-%d')
    sell_date = ql.Date(bond.sell_date, '%Y-%m-%d')

    ql.Settings.instance().evaluationDate = buy_date
    buy_dirty = bond.buy_clean_price + Bond_ql.accruedAmount()

    ql.Settings.instance().evaluationDate = sell_date
    sell_dirty = bond.sell_clean_price + Bond_ql.accruedAmount()

    coupon_between = bond.interest_cashflow
    coupon_received = sum(coupon_between)
    if bond.taxFree == '否':
        coupon_received = coupon_received * (1 - bond.taxRate/100.0)
    hpy = (sell_dirty + coupon_received) / buy_dirty - 1
    if not annualized:
        return hpy

    # Annualize hpy
    f = bond.bond_ql.dayCounter().yearFraction
    year_faction = f(buy_date, sell_date)
    hpy_annualized = hpy/year_faction
    return hpy_annualized


def hpy_repo(bond: Bond, annualized: bool = False) -> float:
    # (sell_dirty + coupon_received) / buy_dirty

    Bond_ql = bond.bond_ql
    buy_date = ql.Date(bond.buy_date, '%Y-%m-%d')
    sell_date = ql.Date(bond.sell_date, '%Y-%m-%d')

    ql.Settings.instance().evaluationDate = buy_date
    buy_dirty = bond.buy_clean_price + Bond_ql.accruedAmount()

    ql.Settings.instance().evaluationDate = sell_date
    sell_dirty = bond.sell_clean_price + Bond_ql.accruedAmount()

    coupon_between = bond.interest_cashflow
    coupon_received = sum(coupon_between)

    if bond.taxFree == '否':
        coupon_received = coupon_received * (1 - bond.taxRate/100.0)

    repo_hpy = (sell_dirty - buy_dirty + coupon_received) / buy_dirty
    if not annualized:
        return repo_hpy

    f = bond.bond_ql.dayCounter().yearFraction
    year_faction = f(buy_date, sell_date)
    repo_hpy_annualized = repo_hpy / year_faction
    return repo_hpy_annualized


def get_coupon_received(bond: Bond):
    coupon_between = bond.interest_cashflow
    coupon_received = sum(coupon_between)

    if bond.taxFree == '否':
        coupon_received = coupon_received * (1 - bond.taxRate/100.0)
    return coupon_received
