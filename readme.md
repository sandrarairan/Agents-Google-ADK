# 🧠 Multi-Tool Agent with Google ADK

This quickstart guide walks you through setting up a **multi-tool conversational agent** using the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/get-started/quickstart/#run-your-agent). You will learn how to:

- ✅ Install the ADK in a Python environment
- 🛠️ Set up a basic agent with multiple tools
- 💻 Run your agent locally in terminal or via the browser-based dev UI

> **Note**: This setup assumes you have a local IDE (e.g., VS Code, PyCharm) and either Python 3.9+ or Java 17+ installed.

---

## 🚀 1. Environment Setup & ADK Installation

### 🐍 Python (recommended)

1. **Create and activate a virtual environment**:

```bash
# Create
python -m venv .venv

# Activate
# macOS/Linux:
source .venv/bin/activate
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1

2. Install the ADK package:

pip install google-adk

3.  Create Your Agent Project

parent_folder/
└── multi_tool_agent/
    ├── __init__.py
    ├── agent.py
    └── .env


