---
title: Research Insight Copilot
emoji: 🧠
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
short_description: Turn interview transcripts into evidence-backed insights
---

# Research Insight Copilot

Upload interview transcripts and get themes, pain points and feature requests, each linked to the exact sentences that support it. Then chat with your research, grounded in the transcripts.

**Try it:** open the Upload page and click **Try with sample interviews** to load three short, fictional interviews about an expense-reporting app. Then open **Insights** or **Chat**.

- Your uploads are private to your browser: each visitor gets a separate workspace.
- Data is not kept: it is cleared whenever the Space restarts.
- Built with FastAPI, ChromaDB, MiniLM embeddings (ONNX) and Llama 3.1 on Groq, with a React frontend.

Source code: https://github.com/dataWizard7957/research-insight-copilot
