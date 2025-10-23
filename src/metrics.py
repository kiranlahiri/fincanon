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

    # Calculate portfolio returns series for advanced metrics
    portfolio_returns = df.dot(weights)

    # Tier 1: Advanced Risk Metrics
    max_drawdown = calculate_max_drawdown(portfolio_returns)
    sortino_daily = calculate_sortino_ratio(portfolio_returns, risk_free_rate)
    sortino_annual = calculate_sortino_ratio(portfolio_returns, risk_free_rate) * np.sqrt(252)

    # Calculate beta vs market (if SPY is in the portfolio, use it as benchmark)
    beta = np.nan
    if 'SPY' in df.columns:
        beta = calculate_beta(portfolio_returns, df['SPY'])

    # Correlation matrix
    correlation_matrix = df.corr().to_dict()

    # Diversification ratio: weighted avg volatility / portfolio volatility
    weighted_vols = np.dot(volatilities, weights)
    diversification_ratio = weighted_vols / port_vol if port_vol > 0 else np.nan

    # Tier 2: Portfolio Optimization
    optimal_portfolios = optimize_portfolio(mean_returns, covariance_matrix, risk_free_rate)
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
        "correlation_matrix": correlation_matrix,
        "diversification_ratio": clean_value(diversification_ratio),

        # Tier 2: Portfolio Optimization
        "optimal_portfolios": optimal_portfolios_annual,
        "efficient_frontier": efficient_frontier_annual,
    }
