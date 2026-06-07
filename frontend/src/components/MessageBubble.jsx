export default function MessageBubble({ role, text, sources = [] }) {
  const scrollToChunk = (chunkId) => {
    const el = document.getElementById(chunkId);

    if (!el) return;

    el.classList.add("highlight");

    el.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });

    setTimeout(() => {
      el.classList.remove("highlight");
    }, 1500);
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignSelf: role === "user" ? "flex-end" : "flex-start",
        background: role === "user" ? "#dff1ff" : "#f5f5f5",
        padding: 10,
        margin: 6,
        borderRadius: 10,
        maxWidth: "70%",
      }}
    >
      <div>{text}</div>

      {/* SOURCE CHUNKS (click → scroll transcript) */}
      {sources?.length > 0 && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 12, color: "#666" }}>Sources:</div>

          {sources.map((s, i) => (
            <button
              key={i}
              onClick={() => scrollToChunk(s.chunk_id)}
              style={{
                fontSize: 12,
                marginRight: 6,
                marginTop: 4,
                cursor: "pointer",
              }}
            >
              📄 {s.transcript} #{s.chunk_id}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}