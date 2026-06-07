import { useState } from "react";
import { Routes, Route, Link } from "react-router-dom";

import Upload from "./pages/Upload";
import Chat from "./pages/Chat";
import Insights from "./pages/Insights";
import TranscriptBox from "./components/TranscriptBox";

export default function App() {
  const [selectedSentence, setSelectedSentence] = useState(null);

  const [highlightedSentenceId, setHighlightedSentenceId] = useState(null);

  const [refreshTranscripts, setRefreshTranscripts] = useState(0);

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily: "Arial",
      }}
    >
      {/* SIDEBAR */}
      <div style={sidebarStyle}>
        <h3>🧠 Research Copilot</h3>

        <Link style={linkStyle} to="/">
          📤 Upload
        </Link>

        <Link style={linkStyle} to="/chat">
          💬 Chat
        </Link>

        <Link style={linkStyle} to="/insights">
          📊 Insights
        </Link>
      </div>

      {/* SPLIT PANE */}
      <div style={{ display: "flex", flex: 1 }}>
        {/* LEFT: TRANSCRIPTS */}
        <div style={leftPane}>
          <TranscriptBox
            onSelectQuote={setSelectedSentence}
            highlighted={highlightedSentenceId}
            refreshTrigger={refreshTranscripts}
          />
        </div>

        {/* RIGHT: ROUTES */}
        <div style={rightPane}>
          <Routes>
            <Route
              path="/"
              element={
                <Upload
                  setRefreshTranscripts={setRefreshTranscripts}
                />
              }
            />

            <Route
              path="/chat"
              element={<Chat selectedSentence={selectedSentence} />}
            />

            <Route
              path="/insights"
              element={
                <Insights
                  onJumpToSentence={(payload) =>
                    setHighlightedSentenceId({
                      chunk_id: payload.chunk_id,
                      sentence_id: payload.sentence_id,
                    })
                  }
                />
              }
            />
          </Routes>
        </div>
      </div>
    </div>
  );
}

const sidebarStyle = {
  width: 220,
  borderRight: "1px solid #ddd",
  padding: 20,
  display: "flex",
  flexDirection: "column",
  gap: 12,
  background: "#fafafa",
};

const leftPane = {
  width: "40%",
  borderRight: "1px solid #eee",
  overflowY: "auto",
  padding: 10,
};

const rightPane = {
  flex: 1,
  overflowY: "auto",
  padding: 20,
};

const linkStyle = {
  textDecoration: "none",
  color: "#333",
  padding: "8px 10px",
  borderRadius: 6,
  background: "#fff",
  border: "1px solid #eee",
};