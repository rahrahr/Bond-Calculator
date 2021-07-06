import QuantLib as ql
from bond import *


def bond_yield(bond: Bond) -> float:
    if hasattr(bond, 'isDiscounted') and bond.isDiscounted:
        ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
        Bond_ql = bond.bond_ql
        return Bond_ql.bondYield(bond.get_dirty_price(bond.buy_date, bond.buy_clean_price),
                                Bond_ql.dayCounter(),
                                ql.CompoundedThenSimple,
                                Bond_ql.frequency())

    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    Bond_ql = bond.bond_ql
    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.dayCounter(),
                             ql.CompoundedThenSimple,
                             Bond_ql.frequency())


def bond_yield_if_exercised(bond: BondWithOption) -> float:
    if hasattr(bond, 'isDiscounted') and bond.isDiscounted:
        ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
        Bond_ql = bond.bond_ql
        return Bond_ql.bondYield(bond.get_dirty_price(bond.buy_date, bond.buy_clean_price),
                                 Bond_ql.dayCounter(),
                                 ql.CompoundedThenSimple,
                                 Bond_ql.frequency())
                                 
    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    Bond_ql = bond.bond_ql_if_exercised
    return Bond_ql.bondYield(bond.buy_clean_price,
                             Bond_ql.dayCounter(),
                             ql.CompoundedThenSimple,
                             Bond_ql.frequency())


def bond_yield_if_extended(bond: BondWithOption) -> float:
    ql.Settings.instance().evaluationDate = ql.Date(bond.buy_date, '%Y-%m-%d')
    effectiveDate = ql.Date(bond.issue_date, '%Y-%m-%d')
    terminationDate = ql.Date(
        '2199-{}'.format(bond.issue_date[-5:]), '%Y-%m-%d')
    tenor = bond.tenor
    calendar = ql.China(ql.China.IB)
    businessConvention = ql.Following
    dateGeneration = ql.DateGeneration.Forward
    monthEnd = False
    schedule = ql.Schedule(effectiveDate, terminationDate, tenor, calendar, businessConvention,
                           businessConvention, dateGeneration, monthEnd)
    daycount_convention = bond.day_counter

    Bond_ql = ql.FixedRateBond(bond.settlement,
                               100,
                               schedule,
                               [i / 100 for i in bond.coupon_rate],
                               daycount_convention)

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
    year_faction = f(ql.Date(bond.buy_date, '%Y-%m-%d'),
                     ql.Date(bond.sell_date, '%Y-%m-%d'))
    hpy_annualized = hpy/year_faction
    return hpy_annualized


def repo_hpy(bond: Bond, annualized: bool = False, cross_exchange=False) -> float:
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
    year_faction = f(ql.Date(bond.buy_date, '%Y-%m-%d'),
                     ql.Date(bond.sell_date, '%Y-%m-%d'))
    repo_hpy_annualized = repo_hpy / year_faction
    return repo_hpy_annualized
