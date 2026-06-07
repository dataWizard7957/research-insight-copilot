export default function InsightCard({
  title,
  summary,
  evidence = [],
  onClick
}) {
  return (
    <div
      onClick={onClick}
      style={{
        border: "1px solid #eee",
        padding: 12,
        marginBottom: 10,
        cursor: "pointer",
        borderRadius: 8,
        background: "#fff"
      }}
    >
      <h4>{title}</h4>

      <p style={{ fontSize: 13, color: "#666" }}>
        {summary}
      </p>

      {/* 👇 ADD THIS */}
      {evidence?.length > 0 && (
        <div style={{ marginTop: 8 }}>
          {evidence.slice(0, 2).map((e, i) => (
            <div key={i} style={{ fontSize: 11, color: "#999" }}>
              chunk: {e.chunk_id} | sentence: {e.sentence_id}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}