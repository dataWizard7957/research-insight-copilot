import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Insights({ onJumpToSentence }) {
  const [data, setData] = useState(null);
  const [activeTheme, setActiveTheme] = useState(null);

  // FIX 1: followups should NEVER be null
  const [followups, setFollowups] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [followupLoading, setFollowupLoading] = useState(false);

  // ==================================================
  // LOAD INSIGHTS
  // ==================================================
  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(false);

      const res = await api.get("/insights/");
      setData(res.data);

    } catch (err) {
      console.log("Insights load error:", err);
      setError(true);
      setData(null);

    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // OPEN THEME + FOLLOWUPS
  // ==================================================
  const openTheme = async (theme) => {
    setActiveTheme(theme);
    setFollowups([]);
    setFollowupLoading(true);

    try {
      const res = await api.post("/insights/followups", {
        theme: theme.name,
      });

    console.log("FOLLOWUPS API RESPONSE:", res.data);
      const raw = res.data;
      const questions =
        raw?.questions?.questions ||
        raw?.questions ||
        [];

      setFollowups(Array.isArray(questions) ? questions : []);

    } catch (err) {
      console.log("Followup error:", err);
      setFollowups([]);

    } finally {
      setFollowupLoading(false);
    }
  };

  // ==================================================
  // JUMP TO TRANSCRIPT
  // ==================================================
  const jumpToEvidence = (evidence) => {
    if (!onJumpToSentence) return;

    // FIX 3: consistent payload (NO transcript_id needed)
    onJumpToSentence({
      chunk_id: evidence.chunk_id,
      sentence_id: evidence.sentence_id,
    });
  };

  // ==================================================
  // STATES
  // ==================================================
  if (loading) {
    return <div style={{ padding: 20 }}>Loading insights...</div>;
  }

  if (error || !data) {
    return (
      <div style={{ padding: 20, color: "red" }}>
        <h3>⚠️ Failed to load insights</h3>
        <p>Check backend /insights API</p>
        <button onClick={loadInsights}>Retry</button>
      </div>
    );
  }

  // ==================================================
  // UI
  // ==================================================
  return (
    <div style={{ display: "flex", height: "100%" }}>

      {/* LEFT PANEL */}
      <div style={{ flex: 1, padding: 20, overflowY: "auto" }}>
        <h2>📊 Insights Dashboard</h2>

        <h3>Executive Summary</h3>
        <p>{data.executive_summary}</p>

        {/* THEMES */}
        <h3>Top Themes</h3>

        {(data.top_themes ?? []).map((theme) => (
          <div
            key={theme.name}
            onClick={() => openTheme(theme)}
            style={{
              border: "1px solid #ddd",
              padding: 12,
              marginBottom: 10,
              cursor: "pointer",
              borderRadius: 8,
              background: "#fff",
            }}
          >
            <h4>{theme.name}</h4>
            <p style={{ fontSize: 13, color: "#666" }}>
              {theme.summary}
            </p>
            <small style={{ color: "gray" }}>
              Click to explore →
            </small>
          </div>
        ))}

        <h3>Pain Points</h3>
        <ul>
          {(data.pain_points ?? []).map((p, i) => (
            <li key={i}>{p}</li>
          ))}
        </ul>

        <h3>Feature Requests</h3>
        <ul>
          {(data.feature_requests ?? []).map((f, i) => (
            <li key={i}>{f}</li>
          ))}
        </ul>
      </div>

      {/* RIGHT DRAWER */}
      {activeTheme && (
        <div
          style={{
            width: 420,
            borderLeft: "1px solid #ddd",
            padding: 16,
            background: "#fafafa",
            overflowY: "auto",
          }}
        >
          <button
            onClick={() => setActiveTheme(null)}
            style={{
              marginBottom: 10,
              padding: "6px 10px",
              border: "1px solid #ccc",
              borderRadius: 6,
            }}
          >
            ✕ Close
          </button>

          <h3>🧠 {activeTheme.name}</h3>
          <p>{activeTheme.summary}</p>
       
          {/* FOLLOWUPS */}

          <h4>🔥 Follow-up Questions</h4>

          {followupLoading && <p>Generating questions...</p>}

          {!followupLoading &&  followups && followups.length === 0 && (
            <p>No follow-ups generated.</p>
          )}

          {followups?.map((q, i) => (
            <div
              key={i}
              style={{
                padding: 8,
                border: "1px solid #eee",
                marginBottom: 8,
                borderRadius: 6,
                background: "#fff",
                cursor: "pointer",
              }}
            >
              {q}
            </div>
          ))}
       
          {/* EVIDENCE */}
          <h4 style={{ marginTop: 20 }}>📌 Evidence</h4>

          {(activeTheme.evidence ?? []).map((evidence, i) => (
            <blockquote
              key={i}
              onClick={() => jumpToEvidence(evidence)}
              style={{
                borderLeft: "3px solid #2563eb",
                padding: 10,
                marginBottom: 10,
                fontSize: 14,
                color: "#444",
                cursor: "pointer",
                background: "#fff",
                borderRadius: 6,
              }}
            >
              {evidence.text}

              {/* FIX 4: cleaner label (you can later inject filename from backend) */}
              <div style={{ fontSize: 12, color: "#999", marginTop: 6 }}>
                📄 {evidence.filename || "unknown file"} • Chunk {evidence.chunk_id} • Sentence {evidence.sentence_id}
              </div>
              

              <div style={{ fontSize: 12, color: "#666", marginTop: 6 }}>
                Click to view source →
              </div>
            </blockquote>
          ))}
        </div>
      )}
    </div>
  );
}