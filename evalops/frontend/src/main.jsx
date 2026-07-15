import React from "react";
import { createRoot } from "react-dom/client";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
const metricLabel = "RAGAS String Presence";

function useRecentRuns(status = "completed", limit = 20) {
  const [runs, setRuns] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState("");

  const fetchRuns = React.useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_BASE_URL}/evaluations/runs/recent?status=${status}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`request failed with status ${response.status}`);
      }
      const payload = await response.json();
      setRuns(payload.runs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }, [status, limit]);

  React.useEffect(() => {
    fetchRuns();
    const interval = setInterval(fetchRuns, 5000); // Auto-refresh every 5s
    return () => clearInterval(interval);
  }, [fetchRuns]);

  return { runs, loading, error, refetch: fetchRuns };
}

function App() {
  const [activeTab, setActiveTab] = React.useState("dashboard");
  const [evalForm, setEvalForm] = React.useState({
    run_id: "",
    question: "",
    answer: "",
    context: "",
    ground_truth: ""
  });
  const [submitError, setSubmitError] = React.useState("");
  const [submitSuccess, setSubmitSuccess] = React.useState("");

  const { runs, loading, error, refetch } = useRecentRuns("completed", 20);

  const handleFormChange = (e) => {
    setEvalForm({ ...evalForm, [e.target.name]: e.target.value });
  };

  const handleSubmitEval = async (e) => {
    e.preventDefault();
    setSubmitError("");
    setSubmitSuccess("");

    try {
      const response = await fetch(`${API_BASE_URL}/evaluations/rag/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(evalForm)
      });

      if (!response.ok) {
        throw new Error(`failed to enqueue evaluation: ${response.status}`);
      }

      const result = await response.json();
      setSubmitSuccess(`Evaluation queued: ${result.job_id}`);
      setEvalForm({ run_id: "", question: "", answer: "", context: "", ground_truth: "" });
      setTimeout(() => refetch(), 1000);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "unknown error");
    }
  };

  const ragasSeries = runs
    .filter((run) => run.result?.ragas_string_presence !== null && run.result?.ragas_string_presence !== undefined)
    .slice()
    .reverse()
    .map((run, index) => ({
      run: index + 1,
      value: run.result.ragas_string_presence,
      runId: run.run_id
    }));

  return (
    <main style={{ fontFamily: "Segoe UI", padding: 24, maxWidth: 1200 }}>
      <header style={{ marginBottom: 32 }}>
        <h1>EvalOps Dashboard</h1>
        <p>AI evaluation, observability, and reliability scoring</p>
      </header>

      <div style={{ display: "flex", gap: 16, marginBottom: 24, borderBottom: "1px solid #ddd", paddingBottom: 12 }}>
        <button
          onClick={() => setActiveTab("dashboard")}
          style={{
            background: activeTab === "dashboard" ? "#1f4d8f" : "transparent",
            color: activeTab === "dashboard" ? "white" : "inherit",
            border: "none",
            padding: "8px 16px",
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 500
          }}
        >
          Dashboard
        </button>
        <button
          onClick={() => setActiveTab("submit")}
          style={{
            background: activeTab === "submit" ? "#1f4d8f" : "transparent",
            color: activeTab === "submit" ? "white" : "inherit",
            border: "none",
            padding: "8px 16px",
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 500
          }}
        >
          Submit Evaluation
        </button>
      </div>

      {activeTab === "dashboard" && (
        <div style={{ display: "flex", gap: 32, flexWrap: "wrap", alignItems: "flex-start" }}>
          {loading ? (
            <p>Loading...</p>
          ) : error ? (
            <p style={{ color: "#b00020" }}>Error: {error}</p>
          ) : (
            <>
              <div>
                <h2 style={{ marginTop: 0 }}>Quality Trend</h2>
                {ragasSeries.length === 0 ? (
                  <p>No completed evaluations yet.</p>
                ) : (
                  <LineChart width={540} height={280} data={ragasSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="run" />
                    <YAxis domain={[0, 1]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="value" stroke="#1f4d8f" strokeWidth={3} name={metricLabel} />
                  </LineChart>
                )}
              </div>

              <section>
                <h2 style={{ marginTop: 0 }}>Latest Completed Evaluations</h2>
                {runs.length === 0 ? (
                  <p>No completed runs yet.</p>
                ) : (
                  <table cellPadding="8" style={{ borderCollapse: "collapse", minWidth: 420 }}>
                    <thead>
                      <tr>
                        <th align="left">Run ID</th>
                        <th align="left">Evaluator</th>
                        <th align="left">String Presence</th>
                        <th align="left">Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {runs.map((run) => (
                        <tr key={run.job_id} style={{ borderBottom: "1px solid #eee" }}>
                          <td>{run.run_id}</td>
                          <td>{run.evaluator}</td>
                          <td>{run.result?.ragas_string_presence?.toFixed(3) ?? "n/a"}</td>
                          <td style={{ fontSize: 12, color: "#666" }}>
                            {new Date(run.created_at).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </section>
            </>
          )}
        </div>
      )}

      {activeTab === "submit" && (
        <div style={{ maxWidth: 600 }}>
          <h2>Enqueue RAG Evaluation</h2>
          <form onSubmit={handleSubmitEval} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {submitSuccess && <p style={{ color: "#2e7d32", background: "#e8f5e9", padding: 12, borderRadius: 4 }}>{submitSuccess}</p>}
            {submitError && <p style={{ color: "#b00020", background: "#ffebee", padding: 12, borderRadius: 4 }}>Error: {submitError}</p>}

            <div>
              <label>Run ID</label>
              <input
                type="text"
                name="run_id"
                value={evalForm.run_id}
                onChange={handleFormChange}
                placeholder="e.g., run-2024-001"
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box" }}
                required
              />
            </div>

            <div>
              <label>Question</label>
              <textarea
                name="question"
                value={evalForm.question}
                onChange={handleFormChange}
                placeholder="User's question"
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box", minHeight: 60 }}
                required
              />
            </div>

            <div>
              <label>Answer</label>
              <textarea
                name="answer"
                value={evalForm.answer}
                onChange={handleFormChange}
                placeholder="Generated answer"
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box", minHeight: 60 }}
                required
              />
            </div>

            <div>
              <label>Context</label>
              <textarea
                name="context"
                value={evalForm.context}
                onChange={handleFormChange}
                placeholder="Retrieved context chunks"
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box", minHeight: 60 }}
              />
            </div>

            <div>
              <label>Ground Truth (optional)</label>
              <textarea
                name="ground_truth"
                value={evalForm.ground_truth}
                onChange={handleFormChange}
                placeholder="Expected answer"
                style={{ width: "100%", padding: 8, borderRadius: 4, border: "1px solid #ccc", boxSizing: "border-box", minHeight: 60 }}
              />
            </div>

            <button
              type="submit"
              style={{
                background: "#1f4d8f",
                color: "white",
                border: "none",
                padding: "10px 16px",
                borderRadius: 4,
                cursor: "pointer",
                fontSize: 14,
                fontWeight: 500
              }}
            >
              Submit Evaluation
            </button>
          </form>
        </div>
      )}

      <footer style={{ marginTop: 48, paddingTop: 24, borderTop: "1px solid #eee", fontSize: 12, color: "#666" }}>
        <p>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Docs</a>
          {" · "}
          <a href="http://localhost:9090" target="_blank" rel="noopener noreferrer">Prometheus</a>
          {" · "}
          <a href="http://localhost:3000" target="_blank" rel="noopener noreferrer">Grafana</a>
        </p>
      </footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
