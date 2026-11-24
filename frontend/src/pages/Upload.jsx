import { useState } from "react";
import { api } from "../api/client";

const errorText = (err, fallback) => err?.response?.data?.detail || fallback;

export default function Upload({ setRefreshTranscripts }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = () => setRefreshTranscripts?.((prev) => prev + 1);

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setBusy(true);
      setStatus("Uploading...");
      const res = await api.post("/upload/", formData);
      setStatus(`Uploaded ${res.data.filename} (${res.data.chunks_created} chunks)`);
      refresh();
    } catch (err) {
      setStatus(`Upload failed: ${errorText(err, "is the backend running?")}`);
    } finally {
      setBusy(false);
    }
  };

  const loadSamples = async () => {
    try {
      setBusy(true);
      setStatus("Loading sample interviews...");
      const res = await api.post("/upload/sample");
      setStatus(
        res.data.loaded.length
          ? `${res.data.message}. Open Insights or Chat to explore them.`
          : "Sample interviews are already loaded. Open Insights or Chat to explore them."
      );
      refresh();
    } catch (err) {
      setStatus(`Could not load samples: ${errorText(err, "is the backend running?")}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <h2>📄 Upload Transcript</h2>

      <div style={sampleBox}>
        <p style={{ margin: "0 0 10px" }}>
          No transcripts handy? Try three short, fictional interviews about an expense-reporting app.
        </p>
        <button onClick={loadSamples} disabled={busy}>
          Try with sample interviews
        </button>
      </div>

      <input
        type="file"
        accept=".txt,.md,text/plain,text/markdown"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={uploadFile} disabled={busy || !file}>Upload</button>

      <p>{status}</p>

      <p style={note}>
        Plain-text transcripts (.txt or .md, up to 300 KB). Your uploads are private to this browser.
      </p>
    </div>
  );
}

const sampleBox = {
  border: "1px solid #eee",
  background: "#fafafa",
  borderRadius: 8,
  padding: 14,
  margin: "12px 0 20px",
};

const note = { color: "#777", fontSize: 13 };
