# Digital Twin

An AI chatbot that acts as your personal "digital twin" — it answers questions from website visitors about your career, background, skills, and public GitHub projects, in your voice. Built with [Gradio](https://www.gradio.app/) and the OpenAI API.

## How it works

The twin is a chat interface backed by an LLM (`gpt-5.4-mini`) that is grounded with:
- Your **LinkedIn profile** (parsed from a PDF at startup)
- A short **summary** of who you are (`summary.txt`)
- **Live GitHub data** — the model can call tools to list your public repos or fetch a specific repo's details and README on demand, so it never has to guess or invent project details

If it can't answer something, it records the question (via [Pushover](https://pushover.net/)) instead of making up an answer. It can also capture a visitor's email if they want to get in touch.

## Features

- 💬 Conversational chat UI (Gradio `ChatInterface`) with a custom dark/light theme
- 🧠 Answers grounded in your real LinkedIn profile and bio, not hallucinated
- 🔧 Tool calling for:
  - `list_github_repos` — lists your public repositories
  - `get_github_repo` — fetches a specific repo's details + README
  - `record_user_details` — captures a visitor's contact info
  - `record_unknown_question` — logs questions the twin couldn't answer
- 📱 Push notifications on new leads / unanswered questions via Pushover
- ☁️ Ready to deploy on [Hugging Face Spaces](https://huggingface.co/spaces) (metadata already included)

## Project structure

```
Digital-Twin/
└── twin/
    ├── app.py              # Gradio app entry point + chat loop
    ├── context.py          # Builds the system prompt from LinkedIn PDF + summary.txt
    ├── tools.py            # Tool definitions: GitHub lookups, Pushover notifications
    ├── styles.py            # Custom CSS/JS for the chat UI
    ├── requirements.txt
    ├── linkedin.pdf         # Your exported LinkedIn profile (used for context)
    ├── summary.txt          # Short written bio used for context
    └── README.md            # Hugging Face Spaces config
```

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/rajesh0411/Digital-Twin.git
cd Digital-Twin/twin
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your own content

Replace `linkedin.pdf` and `summary.txt` with your own exported LinkedIn PDF and a short bio — these are what the model uses to represent you.

### 4. Configure environment variables

Create a `.env` file inside `twin/`:

```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_USERNAME=your_github_username
PUSHOVER_TOKEN=your_pushover_app_token
PUSHOVER_USER=your_pushover_user_key
```

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Auth for the OpenAI API (chat + tool calls) |
| `GITHUB_USERNAME` | Yes | Which GitHub account the twin looks up when asked about projects |
| `PUSHOVER_TOKEN` / `PUSHOVER_USER` | Optional | Enables push notifications for new leads/unanswered questions. Leave unset to disable. |

### 5. Run it

```bash
python app.py
```

Gradio will start a local server (and print a shareable link) where you can chat with your twin.

## Deploying

`twin/README.md` includes Hugging Face Spaces front matter (`sdk: gradio`), so the `twin/` folder can be pushed directly to a Hugging Face Space and it will run as-is — just make sure to set the environment variables above as **Space secrets**.

## Tech stack

- [Gradio](https://www.gradio.org/) — chat UI
- [OpenAI Python SDK](https://github.com/openai/openai-python) — LLM + tool calling
- [pypdf](https://pypi.org/project/pypdf/) — parsing the LinkedIn PDF
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable loading
- [Requests](https://requests.readthedocs.io/) — GitHub API + Pushover calls

## License

No license has been added yet — consider adding one (e.g. MIT) if you want others to reuse this code.
