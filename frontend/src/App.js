import React, { useState } from "react";
import "./App.css";
import EfficientFrontierChart from "./EfficientFrontierChart";
import TimeSeriesCharts from "./TimeSeriesCharts";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

      const data = await res.json();
      setMetrics(data);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Something went wrong. Check console.");
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) {
      alert("Please enter a question");
      return;
    }

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      // Build the request payload
      const payload = { question };

      // If portfolio metrics are available, include them
      if (metrics) {
        payload.portfolio_metrics = metrics;
      }

      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

      const data = await res.json();
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (err) {
      console.error("Query failed:", err);
      alert("Failed to get answer. Make sure the backend is running and papers are ingested.");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="app-container">
    <h1>FinCanon</h1>

    <h2>Upload Portfolio</h2>
    <input type="file" onChange={handleFileChange} />
    <button onClick={handleUpload}>Analyze</button>

    {metrics && (
  <div className="metrics-section">
    <h2>Portfolio Metrics</h2>

    <h3>Performance</h3>
    <ul>
      <li>Annual Return: {metrics.portfolio_return_annual ? (metrics.portfolio_return_annual * 100).toFixed(2) + '%' : 'N/A'}</li>
      <li>Annual Volatility: {metrics.portfolio_vol_annual ? (metrics.portfolio_vol_annual * 100).toFixed(2) + '%' : 'N/A'}</li>
      <li>Sharpe Ratio: {metrics.portfolio_sharpe_annual ? metrics.portfolio_sharpe_annual.toFixed(3) : 'N/A'}</li>
      <li>Sortino Ratio: {metrics.sortino_ratio_annual ? metrics.sortino_ratio_annual.toFixed(3) : 'N/A'}</li>
    </ul>

    <h3>Risk Metrics</h3>
    <ul>
      <li>Maximum Drawdown: {metrics.max_drawdown ? (metrics.max_drawdown * 100).toFixed(2) + '%' : 'N/A'}</li>
      <li>Diversification Ratio: {metrics.diversification_ratio ? metrics.diversification_ratio.toFixed(3) : 'N/A'}</li>
      {metrics.beta && <li>Beta vs SPY: {metrics.beta.toFixed(3)}</li>}
    </ul>

    <h3>Asset-Level Breakdown</h3>
    <table className="asset-table">
      <thead>
        <tr>
          <th>Asset</th>
          <th>Weight</th>
          <th>Return Contrib.</th>
          <th>Asset Sharpe</th>
        </tr>
      </thead>
      <tbody>
        {metrics.asset_weights && Object.entries(metrics.asset_weights)
          .sort((a, b) => b[1] - a[1])
          .map(([asset, weight]) => (
          <tr key={asset}>
            <td><strong>{asset}</strong></td>
            <td>{(weight * 100).toFixed(1)}%</td>
            <td>{metrics.asset_return_contributions[asset] ? (metrics.asset_return_contributions[asset] * 100).toFixed(2) + '%' : 'N/A'}</td>
            <td>{metrics.asset_sharpes[asset] ? metrics.asset_sharpes[asset].toFixed(2) : 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>

    {metrics.top_correlations && metrics.top_correlations.length > 0 && (
      <>
        <h3>Top Asset Correlations</h3>
        <ul>
          {metrics.top_correlations.slice(0, 5).map((corr, idx) => (
            <li key={idx}>
              {corr.asset1} ↔ {corr.asset2}: {corr.correlation.toFixed(2)}
            </li>
          ))}
        </ul>
      </>
    )}

    {metrics.windowed_metrics && metrics.windowed_metrics.length > 0 && (
      <>
        <h3>Quarterly Performance Trend</h3>
        <table className="quarterly-table">
          <thead>
            <tr>
              <th>Quarter</th>
              <th>Return</th>
              <th>Volatility</th>
              <th>Sharpe</th>
            </tr>
          </thead>
          <tbody>
            {metrics.windowed_metrics.slice(-6).map((window, idx) => (
              <tr key={idx}>
                <td>{window.quarter}</td>
                <td>{window.return ? (window.return * 100).toFixed(1) + '%' : 'N/A'}</td>
                <td>{window.volatility ? (window.volatility * 100).toFixed(1) + '%' : 'N/A'}</td>
                <td style={{
                  color: window.sharpe > 1.5 ? 'green' : window.sharpe < 0 ? 'red' : 'inherit'
                }}>
                  {window.sharpe ? window.sharpe.toFixed(2) : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </>
    )}

    {metrics.optimal_portfolios && (
      <>
        <h3>Optimal Portfolios</h3>

        <div className="optimal-portfolio">
          <h4>🔹 Minimum Variance Portfolio</h4>
          <ul>
            <li>Return: {(metrics.optimal_portfolios.min_variance.return * 100).toFixed(2)}%</li>
            <li>Volatility: {(metrics.optimal_portfolios.min_variance.volatility * 100).toFixed(2)}%</li>
            <li>Sharpe: {metrics.optimal_portfolios.min_variance.sharpe.toFixed(3)}</li>
          </ul>
          <details>
            <summary>View Weights</summary>
            <ul>
              {metrics.optimal_portfolios.min_variance.weights.map((weight, idx) => {
                const assetName = Object.keys(metrics.asset_means)[idx];
                return weight > 0.01 ? (
                  <li key={idx}>{assetName}: {(weight * 100).toFixed(1)}%</li>
                ) : null;
              })}
            </ul>
          </details>
        </div>

        <div className="optimal-portfolio">
          <h4>🔹 Maximum Sharpe Portfolio</h4>
          <ul>
            <li>Return: {(metrics.optimal_portfolios.max_sharpe.return * 100).toFixed(2)}%</li>
            <li>Volatility: {(metrics.optimal_portfolios.max_sharpe.volatility * 100).toFixed(2)}%</li>
            <li>Sharpe: {metrics.optimal_portfolios.max_sharpe.sharpe.toFixed(3)}</li>
          </ul>
          <details>
            <summary>View Weights</summary>
            <ul>
              {metrics.optimal_portfolios.max_sharpe.weights.map((weight, idx) => {
                const assetName = Object.keys(metrics.asset_means)[idx];
                return weight > 0.01 ? (
                  <li key={idx}>{assetName}: {(weight * 100).toFixed(1)}%</li>
                ) : null;
              })}
            </ul>
          </details>
        </div>
      </>
    )}
  </div>
)}

    {/* Efficient Frontier Chart */}
    {metrics && metrics.efficient_frontier && (
      <EfficientFrontierChart metrics={metrics} />
    )}

    {/* Time Series Charts */}
    {metrics && metrics.time_series && (
      <TimeSeriesCharts timeSeries={metrics.time_series} />
    )}

    <h2>Ask a Question</h2>
    {metrics && (
      <p className="portfolio-indicator">
        ✓ Portfolio data loaded - answers will be personalized to your portfolio
      </p>
    )}
    <input
      type="text"
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      placeholder={metrics
        ? "e.g., How does my Sharpe ratio compare to theory?"
        : "e.g., What is portfolio diversification?"}
    />
    <button onClick={handleAsk} disabled={loading}>
      {loading ? "Thinking..." : "Ask"}
    </button>

    {answer && (
      <div className="answer-section">
        <h2>Answer</h2>
        <p>{answer}</p>

        {sources.length > 0 && (
          <div className="sources-section">
            <h3>Sources</h3>
            {sources.map((source, idx) => (
              <div key={idx} className="source-item">
                <strong>
                  {source.metadata.title} (Page {source.metadata.page})
                </strong>
                <p>{source.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    )}
  </div>
);
}

export default App;
