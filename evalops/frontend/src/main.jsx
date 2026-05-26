import React from "react";
import { createRoot } from "react-dom/client";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const metricLabel = "RAGAS String Presence";

function App() {
  const [runs, setRuns] = React.useState([]);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    let ignore = false;

    async function loadRecentRuns() {
      try {
        const response = await fetch(`${API_BASE_URL}/evaluations/runs/recent?status=completed&limit=20`);
        if (!response.ok) {
          throw new Error(`request failed with status ${response.status}`);
        }
        const payload = await response.json();
        if (!ignore) {
          setRuns(payload.runs || []);
        }
      } catch (fetchError) {
        if (!ignore) {
          setError(fetchError instanceof Error ? fetchError.message : "unknown error");
        }
      }
    }

    loadRecentRuns();
    return () => {
      ignore = true;
    };
  }, []);

  const ragasSeries = runs
    .filter((run) => run.result && run.result.ragas_string_presence !== null && run.result.ragas_string_presence !== undefined)
    .slice()
    .reverse()
    .map((run, index) => ({
      run: index + 1,
      value: run.result.ragas_string_presence
    }));

  return (
    <main style={{ fontFamily: "Segoe UI", padding: 24 }}>
      <h1>EvalOps Observability Dashboard</h1>
      <p>Recent completed evaluations with one real RAGAS metric.</p>
      {error ? <p style={{ color: "#b00020" }}>API error: {error}</p> : null}

      <div style={{ display: "flex", gap: 32, flexWrap: "wrap", alignItems: "flex-start" }}>
        <LineChart width={540} height={280} data={ragasSeries}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="run" />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#1f4d8f" strokeWidth={3} name={metricLabel} />
        </LineChart>

        <section>
          <h2 style={{ marginTop: 0 }}>Latest Completed Runs</h2>
          {runs.length === 0 ? (
            <p>No completed runs yet.</p>
          ) : (
            <table cellPadding="8" style={{ borderCollapse: "collapse", minWidth: 420 }}>
              <thead>
                <tr>
                  <th align="left">Run ID</th>
                  <th align="left">Evaluator</th>
                  <th align="left">String Presence</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.job_id}>
                    <td>{run.run_id}</td>
                    <td>{run.evaluator}</td>
                    <td>{run.result?.ragas_string_presence ?? "n/a"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
