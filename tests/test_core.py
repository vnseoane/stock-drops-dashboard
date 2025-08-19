import pandas as pd
from app.core.returns import to_period_returns, ReturnConfig, count_threshold_breaches, max_red_streak
from app.core.drawdown import compute_drawdown, max_drawdown


def _toy_prices():
    idx = pd.date_range('2020-01-31', periods=6, freq='M')
    px = pd.Series([100, 105, 80, 81, 79, 90], index=idx, name='Adj Close')
    return pd.DataFrame(px)


def test_to_period_returns():
    df = _toy_prices()
    ret = to_period_returns(df, ReturnConfig("M"))
    assert 'ret' in ret.columns


def test_threshold_breaches():
    df = _toy_prices()
    ret = to_period_returns(df, ReturnConfig("M"))
    c = count_threshold_breaches(ret, -0.10)
    assert c >= 1


def test_red_streak():
    df = _toy_prices()
    ret = to_period_returns(df, ReturnConfig("M"))
    streak = max_red_streak(ret)
    assert isinstance(streak, int)


def test_drawdown():
    df = _toy_prices()
    dd = compute_drawdown(df['Adj Close'])
    assert dd['dd'].min() <= 0
    assert isinstance(max_drawdown(dd), float)
