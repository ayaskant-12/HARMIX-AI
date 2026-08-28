# HARMIX AI
**AI-Powered Performance Engineering & JMeter Scripting**

HARMIX AI is an enterprise-grade SaaS platform designed to revolutionize performance engineering. By uploading a standard HAR (HTTP Archive) file, HARMIX automatically parses endpoints, detects authentication mechanisms, recommends correlation parameters, and leverages a local LLM (Ollama) to generate runnable Apache JMeter (`.jmx`) scripts and Executive PDF reports.

## Features
*   **Automated HAR Parsing:** Extracts requests, headers, response times, and payloads.
*   **API Inventory & Rule Engine:** Evaluates performance best practices (e.g., detecting missing cache managers, large payloads).
*   **Auth & Correlation Engines:** Auto-detects Bearer tokens, Session IDs, and JWTs, generating JSONPath extractors automatically.
*   **Offline AI Integration:** Uses local LLMs via Ollama (`tinyllama`, `llama3`, `qwen`) for secure, on-premise AI analysis.
*   **JMX & PDF Generation:** Instantly outputs runnable JMeter Test Plans and C-Suite ready PDF reports.
*   **Context-Aware Chat:** Converse directly with your HAR file to ask specific architectural or testing questions.

## Folder Structure
```text
HarmixAI/
├── frontend/
│   ├── index.html        # Main SPA interface
│   ├── css/style.css     # Glassmorphism UI styles
│   └── js/app.js         # Modular vanilla JS logic
├── backend/
│   ├── app/
│   │   ├── main.py       # FastAPI router and core app
│   │   ├── database/     # SQLite + SQLAlchemy models
│   │   ├── parser/       # HAR JSON extraction logic
│   │   ├── services/     # Rule, Auth, and Correlation Engines
│   │   ├── ai/           # Ollama LLM client integration
│   │   ├── generator/    # JMX XML Builder
│   │   └── reports/      # FPDF2 Report Generator
├── uploads/              # Raw uploaded HAR files
├── generated/            # Output JMeter (.jmx) files
├── reports/              # Output PDF files
├── database/             # SQLite DB store
├── requirements.txt      # Python dependencies
└── README.md