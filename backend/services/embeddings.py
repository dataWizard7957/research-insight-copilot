"""
Sentence embeddings with all-MiniLM-L6-v2, run through ONNX Runtime
(ChromaDB's built-in embedder). Same model as sentence-transformers, without
PyTorch, so the backend installs in ~100 MB and starts quickly.
"""
import os
from functools import cached_property

import numpy as np

from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

# ONNX Runtime sizes its thread pool to the host's CPU count, not the
# container's share of it. On small cloud plans (e.g. Render free) that can
# exhaust memory, so use a fixed, small number of threads.
THREADS = int(os.getenv("EMBED_THREADS", "1"))


class _MiniLM(ONNXMiniLM_L6_V2):
    @cached_property
    def tokenizer(self):
        # Chroma pads every input to 256 tokens; interview sentences are ~20.
        # Pad each batch only to its longest input instead. Mean pooling
        # ignores padding, so the vectors are the same, about 10x faster.
        tok = self.Tokenizer.from_file(os.path.join(self.DOWNLOAD_PATH, self.EXTRACTED_FOLDER_NAME, "tokenizer.json"))
        tok.enable_truncation(max_length=256)
        tok.enable_padding(pad_id=0, pad_token="[PAD]")
        return tok

    def _forward(self, documents, batch_size: int = 32):
        out = []
        for i in range(0, len(documents), batch_size):
            encoded = self.tokenizer.encode_batch(documents[i : i + batch_size])
            ids = np.array([e.ids for e in encoded], dtype=np.int64)
            mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
            hidden = self.model.run(None, {
                "input_ids": ids,
                "attention_mask": mask,
                "token_type_ids": np.zeros_like(ids),
            })[0]
            m = mask[..., None].astype(hidden.dtype)
            pooled = (hidden * m).sum(1) / np.clip(m.sum(1), 1e-9, None)
            out.append(self._normalize(pooled).astype(np.float32))
        return np.concatenate(out)

    @cached_property
    def model(self):
        so = self.ort.SessionOptions()
        so.log_severity_level = 3
        so.intra_op_num_threads = THREADS
        so.inter_op_num_threads = 1
        so.graph_optimization_level = self.ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        return self.ort.InferenceSession(
            os.path.join(self.DOWNLOAD_PATH, self.EXTRACTED_FOLDER_NAME, "model.onnx"),
            providers=["CPUExecutionProvider"],
            sess_options=so,
        )


_embed = _MiniLM()


def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    return [[float(x) for x in v] for v in _embed(texts)]


def get_embedding(text: str) -> list[float]:
    return get_embeddings([text])[0]
