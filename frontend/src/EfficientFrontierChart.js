import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts';

const EfficientFrontierChart = ({ metrics }) => {
  if (!metrics || !metrics.efficient_frontier || !metrics.optimal_portfolios) {
    return null;
  }

  // Prepare data for the chart
  const frontierData = metrics.efficient_frontier.map(point => ({
    volatility: point.volatility * 100,  // Convert to percentage
    return: point.return * 100,
    type: 'frontier'
  }));

  // Current portfolio point
  const currentPortfolio = {
    volatility: metrics.portfolio_vol_annual * 100,
    return: metrics.portfolio_return_annual * 100,
    name: 'Current Portfolio'
  };

  // Optimal portfolios
  const minVariance = {
    volatility: metrics.optimal_portfolios.min_variance.volatility * 100,
    return: metrics.optimal_portfolios.min_variance.return * 100,
    name: 'Min Variance'
  };

  const maxSharpe = {
    volatility: metrics.optimal_portfolios.max_sharpe.volatility * 100,
    return: metrics.optimal_portfolios.max_sharpe.return * 100,
    name: 'Max Sharpe'
  };

  // Individual assets
  const assetData = Object.keys(metrics.asset_means).map(asset => ({
    volatility: metrics.asset_vols[asset] * Math.sqrt(252) * 100,
    return: metrics.asset_means[asset] * 252 * 100,
    name: asset,
    type: 'asset'
  }));

  return (
    <div className="chart-container">
      <h3>Efficient Frontier</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="volatility"
            name="Volatility"
            unit="%"
            label={{ value: 'Volatility (Annual %)', position: 'insideBottom', offset: -10 }}
          />
          <YAxis
            type="number"
            dataKey="return"
            name="Return"
            unit="%"
            label={{ value: 'Return (Annual %)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            cursor={{ strokeDasharray: '3 3' }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div style={{
                    backgroundColor: 'white',
                    padding: '10px',
                    border: '1px solid #ccc',
                    borderRadius: '5px'
                  }}>
                    <p style={{ margin: 0, fontWeight: 'bold' }}>{data.name || 'Frontier Point'}</p>
                    <p style={{ margin: '5px 0 0 0' }}>Return: {data.return.toFixed(2)}%</p>
                    <p style={{ margin: '5px 0 0 0' }}>Volatility: {data.volatility.toFixed(2)}%</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />

          {/* Efficient Frontier Line */}
          <Scatter
            name="Efficient Frontier"
            data={frontierData}
            fill="#3498db"
            line={{ stroke: '#3498db', strokeWidth: 2 }}
            lineType="monotone"
          />

          {/* Individual Assets */}
          <Scatter
            name="Individual Assets"
            data={assetData}
            fill="#95a5a6"
            shape="circle"
          />

          {/* Current Portfolio */}
          <Scatter
            name="Current Portfolio"
            data={[currentPortfolio]}
            fill="#e74c3c"
            shape="diamond"
          />

          {/* Min Variance Portfolio */}
          <Scatter
            name="Min Variance"
            data={[minVariance]}
            fill="#27ae60"
            shape="triangle"
          />

          {/* Max Sharpe Portfolio */}
          <Scatter
            name="Max Sharpe"
            data={[maxSharpe]}
            fill="#f39c12"
            shape="star"
          />
        </ScatterChart>
      </ResponsiveContainer>

      <div className="chart-legend-text">
        <p><strong>How to read this chart:</strong></p>
        <ul>
          <li><strong>Blue Line:</strong> Efficient Frontier - optimal portfolios</li>
          <li><strong>Red Diamond:</strong> Your current portfolio</li>
          <li><strong>Orange Star:</strong> Maximum Sharpe ratio portfolio (best risk-adjusted)</li>
          <li><strong>Green Triangle:</strong> Minimum variance portfolio (lowest risk)</li>
          <li><strong>Gray Dots:</strong> Individual assets</li>
        </ul>
      </div>
    </div>
  );
};

export default EfficientFrontierChart;
