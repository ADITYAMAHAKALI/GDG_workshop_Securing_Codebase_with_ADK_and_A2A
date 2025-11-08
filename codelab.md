summary: Securing Your Codebase with ADK, A2A & Gemini (45 min)
id: gdg-secure-codebase-adk-a2a-45
categories: AI, Security, Backend
tags: gemini, adk, a2a, python, streamlit, gitingest
status: Draft
authors: Aditya Mahakali ( [LinkedIn](https://www.linkedin.com/in/aditya-mahakali-b81758168/))
Feedback Link: https://github.com/GDG-Bangalore/GDG_workshop_Securing_Codebase_with_ADK_and_A2A/issues

# Securing Your Codebase with ADK, A2A & Gemini (45 min)

<!-- ------------------------ -->
## 1. Overview

Duration: 5

In this codelab you will spin up a **3-agent GitHub security scanner** using:

- **Google Agent Development Kit (ADK)** – define agents
- **Agent2Agent (A2A)** – expose them as HTTP services
- **Gemini** – analyze code & configs
- **gitingest** – ingest GitHub repos without manual cloning
- **Streamlit** – simple web UI

The pipeline:

1. **Scanner Agent** → ingests a GitHub repo (`gitingest`)
2. **Analyzer Agent** → uses Gemini to find security issues
3. **Reporter Agent** → turns findings into Markdown
4. **Orchestrator / Streamlit** → glues everything and shows the report

You’ll:

- Run all three agents locally
- Trigger a scan from CLI
- Trigger a scan from a Streamlit UI

---

<!-- ------------------------ -->
## 2. Prerequisites & Repo Setup

Duration: 10

### 2.1. What you need

- **Python** 3.10 or higher (3.11 / 3.12 recommended)
- **Git** installed
- A **Gemini API key** (organizer may provide or ask you to create one)

### 2.2. Get a Gemini API key

If you don’t already have one:

1. Go to `https://ai.google.dev`
2. Sign in with your Google account
3. Create an API key
4. Copy it (you’ll paste it into `.env`)

### 2.3. Clone the workshop repo

In a terminal:

```bash
git clone https://github.com/GDG-Bangalore/GDG_workshop_Securing_Codebase_with_ADK_and_A2A.git
cd GDG_workshop_Securing_Codebase_with_ADK_and_A2A
````

You should see:

```text
.
├── orchestrator.py
├── streamlit_app.py
├── agents/
├── utils/
├── reports/
└── .env.example
```

---

<!-- ------------------------ -->

## 3. Virtualenv & Dependencies

Duration: 5

To keep things clean, use a virtual environment.

### 3.1. Create venv

```bash
python3 -m venv venv
```

### 3.2. Activate venv

**macOS / Linux:**

```bash
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

Make sure you see `(venv)` at the start of your terminal prompt.

### 3.3. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

If install fails, double-check you’re using Python 3.10+.

---

<!-- ------------------------ -->

## 4. Configure `.env` (Gemini & GitHub)

Duration: 5

The project uses `python-dotenv`, so config lives in `.env`.

### 4.1. Copy example env

```bash
cp .env.example .env
```

### 4.2. Edit `.env`

Open `.env` and set your key:

```env
GOOGLE_API_KEY="YOUR_REAL_GEMINI_API_KEY"
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Optional: only if you want to scan private repos
GITHUB_TOKEN=""
```

* `GOOGLE_API_KEY` is required for Gemini calls
* `GITHUB_TOKEN` is optional and used by `gitingest` for private repos

Save the file.

---

<!-- ------------------------ -->

## 5. Run the Three Agents

Duration: 10

You’ll run each agent on its own port using `uvicorn`.

Open **three terminals** (or tabs). In each:

* `cd` into the project root
* Activate the `venv` (`source venv/bin/activate` or `.\venv\Scripts\Activate.ps1`)

### 5.1. Scanner Agent (port 8001)

**Terminal 1:**

```bash
uvicorn agents.scanner_agent:a2a_app --port 8001 --reload
```

This agent:

* Accepts a GitHub URL
* Calls `gitingest`
* Returns a **RepoDigest JSON** (summary, tree, content)

### 5.2. Analyzer Agent (port 8002)

**Terminal 2:**

```bash
uvicorn agents.analyzer_agent:a2a_app --port 8002 --reload
```

This agent:

* Accepts the RepoDigest JSON
* Uses **Gemini Pro** to look for security issues
* Returns a **vulnerability report JSON**

### 5.3. Reporter Agent (port 8003)

**Terminal 3:**

```bash
uvicorn agents.reporter_agent:a2a_app --port 8003 --reload
```

This agent:

* Accepts the vulnerability JSON
* Uses **Gemini Flash** to output a **Markdown report**

> If any agent crashes:
>
> * Check `.env` has a valid `GOOGLE_API_KEY`
> * Check `pip install -r requirements.txt` completed successfully

---

<!-- ------------------------ -->

## 6. Run a Scan via Orchestrator (CLI)

Duration: 7

Now you’ll use the orchestrator to chain the three agents.

### 6.1. Start a CLI scan

Open **Terminal 4**, activate `venv`, and run:

```bash
python orchestrator.py --url https://github.com/ADITYAMAHAKALI/gdg-vuln-sample-repo
```

What happens:

1. Orchestrator discovers the three agents via A2A
2. Sends the repo URL to **Scanner**
3. Sends scanner output to **Analyzer**
4. Sends analyzer output to **Reporter**
5. Prints the Markdown report in the terminal
6. Saves it under `reports/` as a `.md` file

### 6.2. Verify the report

List the `reports` directory:

```bash
ls reports
```

You should see a file like:

```text
https_github.com_ADITYAMAHAKALI_gdg-vuln-sample-repo.md
```

Open it in your editor / viewer to quickly inspect the findings.

---

<!-- ------------------------ -->

## 7. Run the Streamlit Web UI

Duration: 5

Now let’s use the same orchestrator from a simple web UI.

### 7.1. Start Streamlit

In **Terminal 5** (or reuse Terminal 4), with `venv` active:

```bash
streamlit run streamlit_app.py
```

You’ll see an address like:

```text
Local URL: http://localhost:8501
```

Open it in your browser.

### 7.2. Use the UI

1. Confirm that all agents are still running on:

   * 8001 → scanner
   * 8002 → analyzer
   * 8003 → reporter
2. In the Streamlit UI:

   * Paste a GitHub repo URL, e.g.:

     ```text
     https://github.com/ADITYAMAHAKALI/gdg-vuln-sample-repo
     ```

   * Click **Run Scan**
3. Wait for the spinner to finish
4. Read the Markdown report directly in the browser
5. Click **Download** to save the report as `.md`

If you see an error in Streamlit:

* Ensure the agents are running
* Ensure `.env` is correctly set with `GOOGLE_API_KEY`

---

<!-- ------------------------ -->

## 8. Quick Code Walkthrough

Duration: 5

If you have a few minutes left, here’s what to highlight.

### 8.1. Scanner Agent

File: `agents/scanner_agent.py`

* Wraps `gitingest_repo(repo_url)`
* ADK `Agent` with a `scan_repo` tool
* Instruction forces the agent to:

  * Call the tool exactly once
  * Return only the JSON

### 8.2. Analyzer Agent

File: `agents/analyzer_agent.py`

* Configures `google.generativeai` with your key
* Uses `gemini-2.5-pro`
* System prompt describes:

  * What patterns to treat as risky (secrets, unsafe HTTP, etc.)
  * How to structure the JSON (`repo_summary`, `findings[]`)

### 8.3. Reporter Agent

File: `agents/reporter_agent.py`

* Based on the vulnerability JSON, produces Markdown
* Uses emojis for severity
* Outputs developer-friendly sections

### 8.4. Orchestrator

File: `orchestrator.py`

* Uses `A2ACardResolver` to discover agents
* Uses a shared HTTP client for performance
* Chains:

  ```python
  repo_digest = await _send_text_message(scanner, repo_url)
  vuln_json   = await _send_text_message(analyzer, repo_digest)
  report_md   = await _send_text_message(reporter, vuln_json)
  ```

---

<!-- ------------------------ -->

## 9. Where to Go Next

Duration: 3

You now have a working **multi-agent security scanner**:

* Agents defined with **ADK**
* Interoperability via **A2A**
* Security analysis via **Gemini**
* CLI + **Streamlit** front-ends

Some ideas to extend after the workshop:

* Run scans automatically in **CI/CD** and post results as PR comments
* Add a **Secrets-only agent** or **Dependency-focused agent**
* Re-implement one agent in **another language** (Go, Java) and still talk via A2A
* Customize prompts to reflect your org’s own security policies

You’re done. Save the repo, keep your `.env` safe, and feel free to adapt this pipeline for your own projects.

```