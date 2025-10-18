import React, { useState } from "react";
import "./App.css";

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
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
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
    <ul>
      <li>Annual Return: {metrics.portfolio_return_annual.toFixed(4)}</li>
      <li>Annual Volatility: {metrics.portfolio_vol_annual.toFixed(4)}</li>
      <li>Annual Sharpe: {metrics.portfolio_sharpe_annual.toFixed(4)}</li>
    </ul>

    <h3>Asset Means</h3>
    <ul>
      {Object.entries(metrics.asset_means).map(([asset, value]) => (
        <li key={asset}>
          {asset}: {value.toFixed(4)}
        </li>
      ))}
    </ul>

    <h3>Asset Volatilities</h3>
    <ul>
      {Object.entries(metrics.asset_vols).map(([asset, value]) => (
        <li key={asset}>
          {asset}: {value.toFixed(4)}
        </li>
      ))}
    </ul>
  </div>
)}


    <h2>Ask a Question</h2>
    <input
      type="text"
      value={question}
      onChange={(e) => setQuestion(e.target.value)}
      placeholder="e.g., What is portfolio diversification?"
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
