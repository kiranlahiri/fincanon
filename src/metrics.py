import pandas as pd
import numpy as np

def analyze_portfolio(df: pd.DataFrame, weights=None, risk_free_rate=0.0):
    """
    Analyze a portfolio of asset returns.
    
    Args:
        df (pd.DataFrame): DataFrame with Date index and asset returns as columns.
        weights (list/np.array): Portfolio weights, defaults to equal weighting.
        risk_free_rate (float): Daily risk-free rate (0.0 default).
    
    Returns:
        dict: portfolio and asset-level metrics
    """
    # Ensure datetime index
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    n_assets = df.shape[1]
    if weights is None:
        weights = np.ones(n_assets) / n_assets
    weights = np.array(weights)

    # Basic stats
    mean_returns = df.mean()
    volatilities = df.std()
    covariance_matrix = df.cov()

    # Portfolio stats
    port_return = np.dot(mean_returns, weights)
    port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
    sharpe = (port_return - risk_free_rate) / port_vol if port_vol > 0 else np.nan

    # Annualize (assuming ~252 trading days)
    ann_factor = np.sqrt(252)
    ann_return = port_return * 252
    ann_vol = port_vol * ann_factor
    ann_sharpe = (ann_return - risk_free_rate*252) / ann_vol if ann_vol > 0 else np.nan

    return {
        "asset_means": mean_returns.to_dict(),
        "asset_vols": volatilities.to_dict(),
        "portfolio_return_daily": port_return,
        "portfolio_vol_daily": port_vol,
        "portfolio_sharpe_daily": sharpe,
        "portfolio_return_annual": ann_return,
        "portfolio_vol_annual": ann_vol,
        "portfolio_sharpe_annual": ann_sharpe,
    }
