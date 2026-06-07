import { useState } from "react";
import { api } from "../api/client";

export default function Upload({ setRefreshTranscripts }) { // ✅ ADDED PROP
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const uploadFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");

      const res = await api.post("/upload/", formData);

      setStatus(
        `Uploaded: ${res.data.transcript_id} (${res.data.chunks_created} chunks)`
      );

      // ✅ TRIGGER REFRESH AFTER SUCCESS
      setRefreshTranscripts?.((prev) => prev + 1);

    } catch (err) {
      setStatus("Upload failed");
    }
  };

  return (
    <div>
      <h2>📄 Upload Transcript</h2>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={uploadFile}>Upload</button>

      <p>{status}</p>
    </div>
  );
}