import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from utils.preprocess import clean_and_prepare_data
from rag.retriever import get_faiss_retriever
from rag.generator import generate_ticket_triage, AutomatedTicketAnalysis

app = FastAPI(title="MSP Corp AI Ticket Automation Engine", version="1.0")

# Global placeholder for the active vector database retriever
retriever_instance = None


class TicketRequest(BaseModel):
    ticket: str


@app.get("/", response_class=HTMLResponse)
def ticket_triage_site():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MSP Corp Ticket Automation</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --text: #16202a;
      --muted: #607080;
      --line: #d8e0ea;
      --accent: #1f7a6d;
      --accent-dark: #155f55;
      --danger: #a83434;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 32px 0;
    }
    header {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 22px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 30px;
      line-height: 1.2;
      letter-spacing: 0;
    }
    p {
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }
    .status {
      min-width: max-content;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 8px;
      padding: 10px 12px;
      color: var(--muted);
      font-size: 14px;
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(320px, 420px);
      gap: 18px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    label {
      display: block;
      margin-bottom: 10px;
      font-weight: 700;
    }
    textarea {
      width: 100%;
      min-height: 330px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      color: var(--text);
      font: 15px/1.5 Arial, Helvetica, sans-serif;
    }
    textarea:focus {
      border-color: var(--accent);
      outline: 3px solid rgba(31, 122, 109, 0.16);
    }
    .actions {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 14px;
    }
    button {
      border: 0;
      border-radius: 8px;
      background: var(--accent);
      color: white;
      padding: 11px 16px;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    button:disabled {
      cursor: wait;
      opacity: 0.72;
    }
    .hint {
      font-size: 14px;
      color: var(--muted);
    }
    .result h2 {
      margin: 0 0 14px;
      font-size: 20px;
      letter-spacing: 0;
    }
    .empty {
      color: var(--muted);
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 20px;
      line-height: 1.5;
    }
    .field {
      border-top: 1px solid var(--line);
      padding: 13px 0;
    }
    .field:first-of-type { border-top: 0; padding-top: 0; }
    .name {
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    .value {
      line-height: 1.5;
      overflow-wrap: anywhere;
    }
    ul {
      margin: 6px 0 0;
      padding-left: 20px;
    }
    li { margin: 6px 0; }
    .error {
      color: var(--danger);
      font-weight: 700;
    }
    @media (max-width: 820px) {
      header, .layout { display: block; }
      .status { margin-top: 14px; }
      .result { margin-top: 18px; }
      textarea { min-height: 260px; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>MSP Corp Ticket Automation</h1>
        <p>Paste an IT support ticket and generate the triage output.</p>
      </div>
      <div class="status" id="status">Ready</div>
    </header>

    <div class="layout">
      <section>
        <form id="ticketForm">
          <label for="ticket">Incoming ticket</label>
          <textarea id="ticket" name="ticket" required placeholder="Example: User cannot access shared HR documents after moving teams..."></textarea>
          <div class="actions">
            <button id="submitBtn" type="submit">Analyze Ticket</button>
            <span class="hint">The first request can take a little longer while the model responds.</span>
          </div>
        </form>
      </section>

      <section class="result">
        <h2>Analysis Result</h2>
        <div id="result" class="empty">No ticket analyzed yet.</div>
      </section>
    </div>
  </main>

  <script>
    const form = document.getElementById("ticketForm");
    const ticket = document.getElementById("ticket");
    const result = document.getElementById("result");
    const statusBox = document.getElementById("status");
    const submitBtn = document.getElementById("submitBtn");

    const labels = {
      ticket_summary: "Ticket Summary",
      predicted_category: "Predicted Category",
      priority: "Priority",
      root_cause: "Root Cause",
      recommended_resolution: "Recommended Resolution",
      technician_action: "Technician Action",
      estimated_resolution_time: "Estimated Resolution Time"
    };

    function renderValue(value) {
      if (Array.isArray(value)) {
        return "<ul>" + value.map(item => `<li>${escapeHtml(item)}</li>`).join("") + "</ul>";
      }
      return `<div class="value">${escapeHtml(String(value ?? ""))}</div>`;
    }

    function escapeHtml(value) {
      return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    form.addEventListener("submit", async event => {
      event.preventDefault();
      const text = ticket.value.trim();
      if (!text) return;

      submitBtn.disabled = true;
      statusBox.textContent = "Analyzing...";
      result.className = "empty";
      result.textContent = "Running retrieval and AI triage.";

      try {
        const response = await fetch("/predict-ticket", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ticket: text })
        });

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "The server could not process this ticket.");
        }

        result.className = "";
        result.innerHTML = Object.entries(labels).map(([key, label]) => `
          <div class="field">
            <div class="name">${label}</div>
            ${renderValue(data[key])}
          </div>
        `).join("");
        statusBox.textContent = "Complete";
      } catch (error) {
        result.className = "empty error";
        result.textContent = error.message;
        statusBox.textContent = "Error";
      } finally {
        submitBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.on_event("startup")
def startup_event():
    global retriever_instance
    # Updated to the requested absolute Windows path
    csv_file_path = "C:\\LLM_RAG_TICKET\\data\\IT_Service_Tickets.csv"

    print("========== INITIALIZING SYSTEM TIMELINE ==========")
    if not os.path.exists(csv_file_path):
        print(f"CRITICAL ERROR: High-volume ticket file not found at {csv_file_path}!")
        return

    try:
        # Preprocess data and initialize retriever instance
        df = clean_and_prepare_data(csv_file_path)
        retriever_instance = get_faiss_retriever(df, k=3)
        print("========== ENGINE SUCCESSFULLY RUNNING ==========")
    except Exception as e:
        print(f"Initialization Failed: {str(e)}")


@app.post("/predict-ticket", response_model=AutomatedTicketAnalysis)
def process_ticket(payload: TicketRequest):
    global retriever_instance
    if retriever_instance is None:
        raise HTTPException(status_code=503, detail="Vector Database Retriever Engine is not initialized yet.")

    try:
        analysis_report = generate_ticket_triage(payload.ticket, retriever_instance)
        return analysis_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Orchestration Error: {str(e)}")
