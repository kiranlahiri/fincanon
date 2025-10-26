import pandas as pd
import numpy as np
from scipy.optimize import minimize

def calculate_max_drawdown(returns: pd.Series):
    """Calculate maximum drawdown from a returns series."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_sortino_ratio(returns: pd.Series, risk_free_rate=0.0):
    """Calculate Sortino ratio (return / downside deviation)."""
    excess_returns = returns - risk_free_rate
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = downside_returns.std()

    if downside_std == 0 or np.isnan(downside_std):
        return np.nan

    return excess_returns.mean() / downside_std

def calculate_beta(portfolio_returns: pd.Series, market_returns: pd.Series):
    """Calculate portfolio beta vs market (usually SPY)."""
    if len(portfolio_returns) != len(market_returns):
        return np.nan

    covariance = np.cov(portfolio_returns, market_returns)[0][1]
    market_variance = np.var(market_returns)

    if market_variance == 0:
        return np.nan

    return covariance / market_variance

def portfolio_stats(weights, mean_returns, cov_matrix):
    """Calculate portfolio return and volatility for given weights."""
    portfolio_return = np.dot(weights, mean_returns)
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_return, portfolio_vol

def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0):
    """Negative Sharpe ratio for minimization."""
    p_return, p_vol = portfolio_stats(weights, mean_returns, cov_matrix)
    if p_vol == 0:
        return np.inf
    return -(p_return - risk_free_rate) / p_vol

def portfolio_volatility(weights, mean_returns, cov_matrix):
    """Portfolio volatility for minimization."""
    return portfolio_stats(weights, mean_returns, cov_matrix)[1]

def optimize_portfolio(mean_returns, cov_matrix, risk_free_rate=0):
    """
    Find optimal portfolios:
    - Minimum variance portfolio
    - Maximum Sharpe ratio portfolio
    """
    n_assets = len(mean_returns)

    # Constraints: weights sum to 1
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    # Bounds: each weight between 0 and 1 (long-only)
    bounds = tuple((0, 1) for _ in range(n_assets))

    # Initial guess: equal weights
    initial_guess = np.array([1/n_assets] * n_assets)

    # Minimize variance
    min_var_result = minimize(
        portfolio_volatility,
        initial_guess,
        args=(mean_returns, cov_matrix),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    # Maximize Sharpe (minimize negative Sharpe)
    max_sharpe_result = minimize(
        neg_sharpe_ratio,
        initial_guess,
        args=(mean_returns, cov_matrix, risk_free_rate),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    # Calculate stats for optimal portfolios
    min_var_weights = min_var_result.x
    min_var_return, min_var_vol = portfolio_stats(min_var_weights, mean_returns, cov_matrix)

    max_sharpe_weights = max_sharpe_result.x
    max_sharpe_return, max_sharpe_vol = portfolio_stats(max_sharpe_weights, mean_returns, cov_matrix)

    return {
        'min_variance': {
            'weights': min_var_weights.tolist(),
            'return': min_var_return,
            'volatility': min_var_vol,
            'sharpe': (min_var_return - risk_free_rate) / min_var_vol if min_var_vol > 0 else 0
        },
        'max_sharpe': {
            'weights': max_sharpe_weights.tolist(),
            'return': max_sharpe_return,
            'volatility': max_sharpe_vol,
            'sharpe': (max_sharpe_return - risk_free_rate) / max_sharpe_vol if max_sharpe_vol > 0 else 0
        }
    }

def calculate_efficient_frontier(mean_returns, cov_matrix, num_portfolios=20):
    """
    Calculate efficient frontier points.
    Returns portfolios with different target returns.
    """
    n_assets = len(mean_returns)

    # Find min and max possible returns
    min_ret = np.min(mean_returns)
    max_ret = np.max(mean_returns)

    # Generate target returns
    target_returns = np.linspace(min_ret, max_ret, num_portfolios)

    frontier_portfolios = []

    for target_return in target_returns:
        # Constraints: weights sum to 1, and portfolio return equals target
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, mean_returns) - target_return}
        ]

        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        result = minimize(
            portfolio_volatility,
            initial_guess,
            args=(mean_returns, cov_matrix),
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )

        if result.success:
            weights = result.x
            ret, vol = portfolio_stats(weights, mean_returns, cov_matrix)
            frontier_portfolios.append({
                'return': ret,
                'volatility': vol,
                'weights': weights.tolist()
            })

    return frontier_portfolios

def analyze_portfolio(df: pd.DataFrame, weights=None, risk_free_rate=0.04):
    """
    Analyze a portfolio of asset returns.

    Args:
        df (pd.DataFrame): DataFrame with Date index and asset returns as columns.
        weights (list/np.array): Portfolio weights, defaults to equal weighting.
        risk_free_rate (float): Annual risk-free rate (default 0.04 = 4%).

    Returns:
        dict: portfolio and asset-level metrics
    """
    # Ensure datetime index
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    n_assets = df.shape[1]
    asset_names = df.columns.tolist()

    if weights is None:
        weights = np.ones(n_assets) / n_assets
    weights = np.array(weights)

    # Convert annual risk-free rate to daily
    rf_daily = risk_free_rate / 252

    # Basic stats
    mean_returns = df.mean()
    volatilities = df.std()
    covariance_matrix = df.cov()

    # Portfolio stats
    port_return = np.dot(mean_returns, weights)
    port_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
    sharpe = (port_return - rf_daily) / port_vol if port_vol > 0 else np.nan

    # Annualize (assuming ~252 trading days)
    ann_factor = np.sqrt(252)
    ann_return = port_return * 252
    ann_vol = port_vol * ann_factor
    ann_sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else np.nan

    # Calculate portfolio returns series for advanced metrics
    portfolio_returns = df.dot(weights)

    # Time-series data for charts
    # 1. Cumulative portfolio value (start at 100)
    cumulative_returns = (1 + portfolio_returns).cumprod()
    portfolio_value_series = (cumulative_returns * 100).tolist()
    dates_series = df.index.strftime('%Y-%m-%d').tolist()

    # 2. Rolling Sharpe ratio (90-day window)
    rolling_window = 90
    rolling_sharpe_series = []
    if len(portfolio_returns) >= rolling_window:
        for i in range(rolling_window - 1, len(portfolio_returns)):
            window_returns = portfolio_returns.iloc[i - rolling_window + 1:i + 1]
            window_mean = window_returns.mean()
            window_std = window_returns.std()
            if window_std > 0:
                window_sharpe = ((window_mean - rf_daily) / window_std) * np.sqrt(252)
                rolling_sharpe_series.append({
                    'date': dates_series[i],
                    'sharpe': window_sharpe
                })

    # 3. Drawdown series
    running_max = cumulative_returns.expanding().max()
    drawdown_series = ((cumulative_returns - running_max) / running_max * 100).tolist()

    # 4. Asset-level cumulative returns (for asset view)
    asset_cumulative_returns = {}
    for asset in asset_names:
        asset_cumulative = (1 + df[asset]).cumprod()
        asset_cumulative_returns[asset] = (asset_cumulative * 100).tolist()

    # Tier 1: Advanced Risk Metrics
    max_drawdown = calculate_max_drawdown(portfolio_returns)
    sortino_daily = calculate_sortino_ratio(portfolio_returns, rf_daily)
    sortino_annual = calculate_sortino_ratio(portfolio_returns, rf_daily) * np.sqrt(252)

    # Calculate beta vs market (if SPY is in the portfolio, use it as benchmark)
    beta = np.nan
    if 'SPY' in df.columns:
        beta = calculate_beta(portfolio_returns, df['SPY'])

    # Correlation matrix
    correlation_matrix = df.corr()
    correlation_matrix_dict = correlation_matrix.to_dict()

    # Extract top correlations (excluding diagonal)
    top_correlations = []
    for i, asset1 in enumerate(asset_names):
        for j, asset2 in enumerate(asset_names):
            if i < j:  # Only upper triangle to avoid duplicates
                corr = correlation_matrix.loc[asset1, asset2]
                top_correlations.append({
                    'asset1': asset1,
                    'asset2': asset2,
                    'correlation': corr
                })

    # Sort by absolute correlation value (highest first)
    top_correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
    top_5_correlations = top_correlations[:5]  # Keep top 5

    # Diversification ratio: weighted avg volatility / portfolio volatility
    weighted_vols = np.dot(volatilities, weights)
    diversification_ratio = weighted_vols / port_vol if port_vol > 0 else np.nan

    # Tier 2: Portfolio Optimization (pass daily risk-free rate)
    optimal_portfolios = optimize_portfolio(mean_returns, covariance_matrix, rf_daily)
    efficient_frontier = calculate_efficient_frontier(mean_returns, covariance_matrix, num_portfolios=20)

    # Annualize frontier points
    efficient_frontier_annual = []
    for point in efficient_frontier:
        efficient_frontier_annual.append({
            'return': point['return'] * 252,
            'volatility': point['volatility'] * np.sqrt(252),
            'weights': point['weights']
        })

    # Annualize optimal portfolios
    optimal_portfolios_annual = {
        'min_variance': {
            'weights': optimal_portfolios['min_variance']['weights'],
            'return': optimal_portfolios['min_variance']['return'] * 252,
            'volatility': optimal_portfolios['min_variance']['volatility'] * np.sqrt(252),
            'sharpe': optimal_portfolios['min_variance']['sharpe'] * np.sqrt(252)
        },
        'max_sharpe': {
            'weights': optimal_portfolios['max_sharpe']['weights'],
            'return': optimal_portfolios['max_sharpe']['return'] * 252,
            'volatility': optimal_portfolios['max_sharpe']['volatility'] * np.sqrt(252),
            'sharpe': optimal_portfolios['max_sharpe']['sharpe'] * np.sqrt(252)
        }
    }

    # Windowed metrics (quarterly)
    # Calculate metrics for each quarter to show trends
    windowed_metrics = []

    # Group by quarter
    df_with_quarter = df.copy()
    df_with_quarter['quarter'] = df_with_quarter.index.to_period('Q')

    for quarter in df_with_quarter['quarter'].unique():
        quarter_data = df_with_quarter[df_with_quarter['quarter'] == quarter].drop('quarter', axis=1)

        if len(quarter_data) >= 20:  # Need at least 20 days for meaningful stats
            q_mean_returns = quarter_data.mean()
            q_cov = quarter_data.cov()

            q_port_return = np.dot(q_mean_returns, weights)
            q_port_vol = np.sqrt(np.dot(weights.T, np.dot(q_cov, weights)))

            # Annualize
            q_ann_return = q_port_return * 252
            q_ann_vol = q_port_vol * np.sqrt(252)
            q_ann_sharpe = (q_ann_return - risk_free_rate) / q_ann_vol if q_ann_vol > 0 else None

            windowed_metrics.append({
                'quarter': str(quarter),
                'return': q_ann_return,
                'volatility': q_ann_vol,
                'sharpe': q_ann_sharpe,
                'days': len(quarter_data)
            })

    # Asset-level metrics
    # Per-asset contribution to portfolio return
    asset_return_contributions = (mean_returns * weights * 252).to_dict()

    # Per-asset contribution to portfolio variance (using marginal contribution)
    # MCR = (Covariance Matrix * weights) / portfolio_variance
    marginal_contrib = covariance_matrix.dot(weights) / (port_vol ** 2) if port_vol > 0 else np.zeros(n_assets)
    asset_variance_contributions = (marginal_contrib * weights * 252).tolist()

    # Per-asset Sharpe ratio (individual asset Sharpe, not contribution)
    asset_sharpes = {}
    for asset in asset_names:
        asset_return_annual = mean_returns[asset] * 252
        asset_vol_annual = volatilities[asset] * np.sqrt(252)
        if asset_vol_annual > 0:
            asset_sharpes[asset] = (asset_return_annual - risk_free_rate) / asset_vol_annual
        else:
            asset_sharpes[asset] = None

    # Convert NaN/Inf to None for JSON serialization
    def clean_value(val):
        if isinstance(val, (int, float)):
            if np.isnan(val) or np.isinf(val):
                return None
        return val

    return {
        # Original metrics
        "asset_means": mean_returns.to_dict(),
        "asset_vols": volatilities.to_dict(),
        "portfolio_return_daily": clean_value(port_return),
        "portfolio_vol_daily": clean_value(port_vol),
        "portfolio_sharpe_daily": clean_value(sharpe),
        "portfolio_return_annual": clean_value(ann_return),
        "portfolio_vol_annual": clean_value(ann_vol),
        "portfolio_sharpe_annual": clean_value(ann_sharpe),

        # Tier 1: Advanced Risk Metrics
        "max_drawdown": clean_value(max_drawdown),
        "sortino_ratio_daily": clean_value(sortino_daily),
        "sortino_ratio_annual": clean_value(sortino_annual),
        "beta": clean_value(beta),
        "correlation_matrix": correlation_matrix_dict,
        "top_correlations": [{k: clean_value(v) if k == 'correlation' else v for k, v in corr.items()} for corr in top_5_correlations],
        "diversification_ratio": clean_value(diversification_ratio),

        # Asset-level metrics
        "asset_weights": {asset: weight for asset, weight in zip(asset_names, weights)},
        "asset_return_contributions": {k: clean_value(v) for k, v in asset_return_contributions.items()},
        "asset_variance_contributions": {asset: clean_value(contrib) for asset, contrib in zip(asset_names, asset_variance_contributions)},
        "asset_sharpes": {k: clean_value(v) for k, v in asset_sharpes.items()},

        # Windowed metrics
        "windowed_metrics": [{k: clean_value(v) if k != 'quarter' and k != 'days' else v for k, v in window.items()} for window in windowed_metrics],

        # Time-series data for charts
        "time_series": {
            "dates": dates_series,
            "portfolio_value": [clean_value(v) for v in portfolio_value_series],
            "rolling_sharpe": [{k: clean_value(v) if k != 'date' else v for k, v in point.items()} for point in rolling_sharpe_series],
            "drawdown": [clean_value(v) for v in drawdown_series],
            "asset_values": {asset: [clean_value(v) for v in values] for asset, values in asset_cumulative_returns.items()}
        },

        # Tier 2: Portfolio Optimization
        "optimal_portfolios": optimal_portfolios_annual,
        "efficient_frontier": efficient_frontier_annual,
    }
