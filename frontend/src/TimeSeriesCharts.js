import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function TimeSeriesCharts({ timeSeries }) {
  const [view, setView] = useState('portfolio'); // 'portfolio' or 'assets'

  if (!timeSeries || !timeSeries.dates || timeSeries.dates.length === 0) {
    return null;
  }

  // Prepare data for portfolio value chart
  const portfolioValueData = timeSeries.dates.map((date, idx) => ({
    date: date,
    value: timeSeries.portfolio_value[idx]
  }));

  // Prepare data for asset values chart
  const assetValueData = timeSeries.dates.map((date, idx) => {
    const dataPoint = { date };
    if (timeSeries.asset_values) {
      Object.keys(timeSeries.asset_values).forEach(asset => {
        dataPoint[asset] = timeSeries.asset_values[asset][idx];
      });
    }
    return dataPoint;
  });

  // Colors for different assets
  const assetColors = {
    'AAPL': '#A2AAAD',
    'GOOGL': '#4285F4',
    'META': '#0668E1',
    'MSFT': '#F25022',
    'NVDA': '#76B900',
    'SPY': '#FFB900'
  };

  // Prepare data for rolling Sharpe chart
  const rollingSharpeData = timeSeries.rolling_sharpe.map(point => ({
    date: point.date,
    sharpe: point.sharpe
  }));

  // Prepare data for drawdown chart
  const drawdownData = timeSeries.dates.map((date, idx) => ({
    date: date,
    drawdown: timeSeries.drawdown[idx]
  }));

  // Custom tick formatter to show fewer dates
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}/${date.getFullYear().toString().slice(2)}`;
  };

  // Sample data to show fewer x-axis labels
  const tickInterval = Math.floor(timeSeries.dates.length / 6);

  return (
    <div className="time-series-container">
      <h2>Portfolio Performance Over Time</h2>

      {/* Toggle between Portfolio and Asset View */}
      <div className="view-toggle">
        <button
          className={view === 'portfolio' ? 'active' : ''}
          onClick={() => setView('portfolio')}
        >
          Portfolio View
        </button>
        <button
          className={view === 'assets' ? 'active' : ''}
          onClick={() => setView('assets')}
        >
          Asset View
        </button>
      </div>

      {/* Portfolio Value Chart */}
      {view === 'portfolio' && (
        <div className="chart-container">
          <h3>Cumulative Portfolio Value</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={portfolioValueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                interval={tickInterval}
              />
              <YAxis
                label={{ value: 'Value (Start = 100)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                labelFormatter={(label) => `Date: ${label}`}
                formatter={(value) => [`${value.toFixed(2)}`, 'Portfolio Value']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#3498db"
                strokeWidth={2}
                dot={false}
                name="Portfolio Value"
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="chart-description">
            Starting with 100, this shows your portfolio's weighted growth over time.
          </p>
        </div>
      )}

      {/* Asset Value Chart */}
      {view === 'assets' && timeSeries.asset_values && (
        <div className="chart-container">
          <h3>Individual Asset Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={assetValueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                interval={tickInterval}
              />
              <YAxis
                label={{ value: 'Value (Start = 100)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                labelFormatter={(label) => `Date: ${label}`}
                formatter={(value, name) => [`${value.toFixed(2)}`, name]}
              />
              <Legend />
              {Object.keys(timeSeries.asset_values).map((asset, idx) => (
                <Line
                  key={asset}
                  type="monotone"
                  dataKey={asset}
                  stroke={assetColors[asset] || `hsl(${idx * 60}, 70%, 50%)`}
                  strokeWidth={2}
                  dot={false}
                  name={asset}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <p className="chart-description">
            Shows each asset's growth independently (unweighted). Compare to see which assets drove your returns.
          </p>
        </div>
      )}

      {/* Rolling Sharpe Chart */}
      {rollingSharpeData.length > 0 && (
        <div className="chart-container">
          <h3>Rolling 90-Day Sharpe Ratio</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={rollingSharpeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                interval={Math.floor(rollingSharpeData.length / 6)}
              />
              <YAxis
                label={{ value: 'Sharpe Ratio', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                labelFormatter={(label) => `Date: ${label}`}
                formatter={(value) => [`${value.toFixed(2)}`, 'Sharpe Ratio']}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="sharpe"
                stroke="#e74c3c"
                strokeWidth={2}
                dot={false}
                name="Rolling Sharpe"
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="chart-description">
            Shows risk-adjusted performance over rolling 90-day windows. Higher is better.
          </p>
        </div>
      )}

      {/* Drawdown Chart */}
      <div className="chart-container">
        <h3>Drawdown from Peak</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={drawdownData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              interval={tickInterval}
            />
            <YAxis
              label={{ value: 'Drawdown (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              labelFormatter={(label) => `Date: ${label}`}
              formatter={(value) => [`${value.toFixed(2)}%`, 'Drawdown']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="drawdown"
              stroke="#9b59b6"
              strokeWidth={2}
              dot={false}
              name="Drawdown"
              fill="#9b59b6"
            />
          </LineChart>
        </ResponsiveContainer>
        <p className="chart-description">
          Shows portfolio decline from previous peak. 0% means at new high, negative values show losses from peak.
        </p>
      </div>
    </div>
  );
}

export default TimeSeriesCharts;
