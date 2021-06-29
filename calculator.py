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


def bond_yield_if_extended(bond: BondWithOption) -> float:
    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    Bond_ql = bond.bond_ql_if_exercised
    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.dayCounter(),
                             ql.CompoundedThenSimple,
                             Bond_ql.frequency())


def get_coupon_received(bond: Bond):
    return bond.get_coupon_received()


def hpy(bond: Bond, annualized: bool = False, cross_exchange=False) -> float:
    # (sell_dirty + coupon_received) / buy_dirty - 1
    buy_dirty = bond.get_dirty_price(bond.buy_date, bond.buy_clean_price)
    sell_dirty = bond.get_dirty_price(bond.sell_date, bond.sell_clean_price)
    coupon_received = bond.get_coupon_received()

    # 转托管费用
    fees = 0
    if cross_exchange:
        fees = 0.005

    hpy = (sell_dirty + coupon_received - fees) / buy_dirty - 1
    if not annualized:
        return hpy

    # Annualize hpy
    f = bond.bond_ql.dayCounter().yearFraction
    year_faction = f(buy_date, sell_date)
    hpy_annualized = hpy/year_faction
    return hpy_annualized


def hpy_repo(bond: Bond, annualized: bool = False, cross_exchange=False) -> float:
    # (sell_dirty + coupon_received) / buy_dirty
    buy_dirty = bond.get_dirty_price(bond.buy_date, bond.buy_clean_price)
    sell_dirty = bond.get_dirty_price(bond.sell_date, bond.sell_clean_price)
    coupon_received = bond.get_coupon_received()

    # 转托管费用
    fees = 0
    if cross_exchange:
        fees = 0.005

    repo_hpy = (sell_dirty - buy_dirty + coupon_received - fees) / buy_dirty
    if not annualized:
        return repo_hpy

    f = bond.bond_ql.dayCounter().yearFraction
    year_faction = f(buy_date, sell_date)
    repo_hpy_annualized = repo_hpy / year_faction
    return repo_hpy_annualized
