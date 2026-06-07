import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function TranscriptBox({
  onSelectQuote,
  highlighted,
  refreshTrigger,
}) {
  const [chunks, setChunks] = useState([]);
  const [selected, setSelected] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  // ==================================================
  // LOAD TRANSCRIPTS
  // ==================================================
  useEffect(() => {
    loadTranscripts();
  }, [refreshTrigger]);

  const loadTranscripts = async () => {
    try {
      setLoading(true);
      setError(false);

      const res = await api.get("/transcripts/");

      const payload = res.data?.data ?? res.data;

      setChunks(Array.isArray(payload) ? payload : []);
    } catch (err) {
      console.error("Transcript fetch error:", err);
      setError(true);
      setChunks([]);
    } finally {
      setLoading(false);
    }
  };

  // ==================================================
  // EXTERNAL HIGHLIGHT (Insights → Transcript sync)
  // ==================================================
  useEffect(() => {
    if (!highlighted) return;

    const { chunk_id, sentence_id } = highlighted || {};

    if (chunk_id === undefined || sentence_id === undefined) return;

    setSelected({ chunk_id, sentence_id });

    const el = document.getElementById(
      `sentence-${chunk_id}-${sentence_id}`
    );

    if (!el) return;

    setTimeout(() => {
      el.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 100);
  }, [highlighted]);

  // ==================================================
  // CLICK SENTENCE
  // ==================================================
  const handleSentenceClick = (sentence, chunk) => {
    const payload = {
      text: sentence.text,
      filename: chunk.filename,
      transcript_id: chunk.transcript_id,
      chunk_id: chunk.chunk_id,
      sentence_id: sentence.sentence_id,
    };

    setSelected({
      chunk_id: chunk.chunk_id,
      sentence_id: sentence.sentence_id,
    });

    onSelectQuote?.(payload);
  };

  // ==================================================
  // LOADING STATE
  // ==================================================
  if (loading) {
    return <div style={styles.center}>Loading transcripts...</div>;
  }

  // ==================================================
  // ERROR STATE
  // ==================================================
  if (error) {
    return (
      <div style={styles.center}>
        <h3>⚠️ Failed to load transcripts</h3>
        <button onClick={loadTranscripts}>Retry</button>
      </div>
    );
  }

  // ==================================================
  // EMPTY STATE
  // ==================================================
  if (!chunks.length) {
    return (
      <div style={styles.center}>
        <h3>📄 No transcripts yet</h3>
        <p>Upload a file to start your research session.</p>
      </div>
    );
  }

  // ==================================================
  // UI
  // ==================================================
  
return (
  <div>
    <h3 style={{ marginBottom: 10 }}>📄 Transcripts</h3>

    {chunks.map((chunk) => (
      <div
        key={`${chunk.transcript_id}-${chunk.chunk_id}`}
        style={styles.chunk}
      >
        <div style={{ lineHeight: 1.8 }}>
          {chunk.sentences?.map((sentence) => {
            const isActive =
              selected?.chunk_id === chunk.chunk_id &&
              selected?.sentence_id === sentence.sentence_id;

            return (
              <span
                key={`${chunk.chunk_id}-${sentence.sentence_id}`}
                id={`sentence-${chunk.chunk_id}-${sentence.sentence_id}`}
                onClick={() =>
                  handleSentenceClick(sentence, chunk)
                }
                style={{
                  ...styles.sentence,
                  ...(isActive ? styles.highlight : {}),
                }}
              >
                {sentence.text}{" "}
              </span>
            );
          })}
        </div>
      </div>
    ))}
  </div>
);
}


// ==================================================
// STYLES
// ==================================================
const styles = {
  chunk: {
    padding: 12,
    borderBottom: "1px solid #eee",
  },

  sentence: {
    cursor: "pointer",
    padding: "2px 4px",
    borderRadius: 4,
    transition: "background 0.15s ease",
  },

  highlight: {
    background: "#fff3b0",
    fontWeight: 600,
    outline: "2px solid #f59e0b",
  },

  center: {
    padding: 30,
    textAlign: "center",
    color: "#666",
  },
};