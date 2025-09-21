import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
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
    const res = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>FinCanon</h1>

      <h2>Upload Portfolio</h2>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Analyze
      </button>

      {/* ✅ Render metrics in tables */}
      {metrics && (
        <div style={{ marginTop: "20px" }}>
          <h2>Portfolio Metrics</h2>
          <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
            <tbody>
              <tr>
                <td><strong>Annual Return</strong></td>
                <td>{metrics.portfolio_return_annual.toFixed(4)}</td>
              </tr>
              <tr>
                <td><strong>Annual Volatility</strong></td>
                <td>{metrics.portfolio_vol_annual.toFixed(4)}</td>
              </tr>
              <tr>
                <td><strong>Annual Sharpe</strong></td>
                <td>{metrics.portfolio_sharpe_annual.toFixed(4)}</td>
              </tr>
            </tbody>
          </table>

          <h3 style={{ marginTop: "20px" }}>Asset Means</h3>
          <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Asset</th>
                <th>Mean Return</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(metrics.asset_means).map(([asset, value]) => (
                <tr key={asset}>
                  <td>{asset}</td>
                  <td>{value.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3 style={{ marginTop: "20px" }}>Asset Volatilities</h3>
          <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Asset</th>
                <th>Volatility</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(metrics.asset_vols).map(([asset, value]) => (
                <tr key={asset}>
                  <td>{asset}</td>
                  <td>{value.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <h2 style={{ marginTop: "30px" }}>Ask a Question</h2>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: "300px", marginRight: "10px" }}
      />
      <button onClick={handleAsk}>Ask</button>

      <h2>Answer</h2>
      <p>{answer}</p>
    </div>
  );
}

export default App;
