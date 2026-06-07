import { useState, useRef, useEffect } from "react";

export default function Chat({ selectedSentence }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // selected transcript citations
  const [selectedSources, setSelectedSources] = useState([]);

  const abortRef = useRef(null);

  // When user clicks a sentence in TranscriptBox
  useEffect(() => {
    if (!selectedSentence) return;

    setQuestion(
      `Explain this: "${selectedSentence.text}"`
    );

    setSelectedSources([
      {
        filename: selectedSentence.filename,
        transcript_id:selectedSentence.transcript_id,
        chunk_id: selectedSentence.chunk_id,
        sentence_id:selectedSentence.sentence_id,
      },
    ]);
  }, [selectedSentence]);

  const askQuestion = async () => {
    if (!question.trim()) return;

    // cancel previous stream
    if (abortRef.current) {
      abortRef.current.abort();
    }

    const controller = new AbortController();
    abortRef.current = controller;

    const currentQuestion = question;
    const currentSources = [...selectedSources];

    // add user + placeholder bot message
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: currentQuestion,
        sources: currentSources,
      },
      {
        role: "bot",
        text: "",
        streaming: true,
      },
    ]);

    setQuestion("");
    setSelectedSources([]);
    setLoading(true);

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/chat/stream",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            question: currentQuestion,
            sources: currentSources,
          }),
          signal: controller.signal,
        }
      );

      if (!res.ok) {
        throw new Error(
          `Request failed (${res.status})`
        );
      }

      const reader =
        res.body.getReader();
      const decoder =
        new TextDecoder();

      let fullText = "";

      while (true) {
        const { value, done } =
          await reader.read();

        if (done) break;

        fullText += decoder.decode(
          value,
          {
            stream: true,
          }
        );

        setMessages((prev) => {
          const copy = [...prev];

          copy[copy.length - 1] = {
            role: "bot",
            text: fullText,
            streaming: true,
          };

          return copy;
        });
      }

      // mark stream complete
      setMessages((prev) => {
        const copy = [...prev];

        copy[copy.length - 1] = {
          ...copy[copy.length - 1],
          streaming: false,
        };

        return copy;
      });
    } catch (err) {
      if (err.name === "AbortError") {
        return;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text:
            "⚠️ Error: Failed to fetch response",
          streaming: false,
        },
      ]);
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  return (
    <div
      style={{
        width: "100%",
        maxWidth: 1100,
        margin: "0 auto",
      }}
    >
      <h2>💬 Research Chat</h2>

      {/* ACTIVE SOURCE */}
      {selectedSources.length > 0 && (
        <div
          style={{
            marginBottom: 10,
            padding: 8,
            background: "#fff7cc",
            border:
              "1px solid #f0d000",
            borderRadius: 6,
            fontSize: 13,
          }}
        >
          📄 Using selected transcript
          sentence
        </div>
      )}

      {/* CHAT WINDOW */}
      <div
        style={{
          border: "1px solid #ddd",
          padding: 12,
          height: 500,
          overflowY: "auto",
          borderRadius: 8,
          background: "#fafafa",
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              marginBottom: 16,
            }}
          >
            <b
              style={{
                color:
                  m.role === "user"
                    ? "#2563eb"
                    : "#16a34a",
              }}
            >
              {m.role === "user"
                ? "You"
                : "AI"}
            </b>

            <div
              style={{
                marginTop: 4,
                whiteSpace:
                  "pre-wrap",
              }}
            >
              {m.text}
              {m.streaming && (
                <span> ▍</span>
              )}
            </div>

            {/* source metadata */}
            {m.role === "user" &&
              m.sources?.length >
                0 && (
                <div
                  style={{
                    marginTop: 6,
                    fontSize: 12,
                    color: "#666",
                  }}
                >
                  <strong>
                    Source:
                  </strong>

                  {m.sources.map(
                    (s) => (
                      <div
                        key={`${s.chunk_id}-${s.sentence_id}`}
                      >
                       📄{s.filename || "Interview"} • Chunk {s.chunk_id} • Sentence {s.sentence_id}
                      </div>
                    )
                  )}
                </div>
              )}
          </div>
        ))}
      </div>

      {/* INPUT */}
      <div
        style={{
          marginTop: 12,
          display: "flex",
          gap: 8,
        }}
      >
        <input
          value={question}
          onChange={(e) =>
            setQuestion(
              e.target.value
            )
          }
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              askQuestion();
            }
          }}
          placeholder="Ask research question..."
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 6,
            border:
              "1px solid #ccc",
          }}
        />

        <button
          onClick={askQuestion}
          disabled={loading}
          style={{
            padding:
              "10px 16px",
            borderRadius: 6,
            border: "none",
            cursor: "pointer",
            background: loading
              ? "#555"
              : "#111",
            color: "#fff",
          }}
        >
          {loading
            ? "Thinking..."
            : "Send"}
        </button>
      </div>
    </div>
  );
}