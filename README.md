# AI Chatbot with LangChain + Ollama + Streamlit

A complete AI chatbot solution featuring:
- 🦜 **LangChain** for conversation management
- 🦙 **Ollama** for local LLM inference (via Docker)
- 🗄️ **SQLite Database** for persistent conversation storage
- 🧠 **Memory Management** for conversation context per session
- 🐳 **Docker** for easy deployment
- ⚡ **Streamlit** for a beautiful web interface

## 🏗️ Project Structure

```
LangChain_AI_Chat/
├── app/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── memory_manager.py
│   └── config.py
├── data/
│   └── chathistory.db          # SQLite database (auto-created)
├── static/
│   └── style.css
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
└── SETUP_GUIDE.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Setup Instructions

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd LangChain_AI_Chat
```

2. **Start the services:**
```bash
docker compose up -d --build
```
This will build the Streamlit application image and start all services in the correct order.

3. **Ollama models:**
The `docker-compose.yml` is configured to automatically pull the default model (`gemma:2b`). The model pulling service will wait until the Ollama service is healthy before starting.

4. **Access the chatbot:**
   - Open http://localhost:8501 in your browser.

## 🔧 Configuration

### Environment Variables

You can customize the application by creating a `.env` file in the root of the project (e.g. add https://smith.langchain.com/ connection to log your LLM chat messages info).

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama-app:11434` | **(Important)** The URL for the Ollama service within the Docker network. |
| `OLLAMA_MODEL` | `gemma:2b` | The default model to use. |
| `OLLAMA_TEMPERATURE` | `0.7` | The temperature for the LLM. |
| `OLLAMA_TOP_P` | `0.9` | The top_p for the LLM. |
| `OLLAMA_NUM_PREDICT` | `512` | The number of tokens to predict. |
| `CHAT_MEMORY_SIZE` | `10` | Number of messages to remember in a session. |
| `DATABASE_URL` | `sqlite+aiosqlite:///data/chathistory.db` | SQLite database connection string. |
| `DATABASE_TABLE_NAME` | `message_store` | Database table name for storing messages. |
| `STREAMLIT_SERVER_PORT` | `8501` | Web interface port. |

### Available Models

The default model is `gemma:2b`. You can change the model by setting the `OLLAMA_MODEL` environment variable in your `.env` file. Make sure the model is available in your Ollama instance. You can add more models to be pulled at startup by editing the `command` in the `ollama-pull-models` service in `docker-compose.yml`.

## 🧠 Memory Management

The chatbot uses a dual-layer memory system for optimal performance:
- **Session-based Memory**: Each user session has its own independent conversation history.
- **SQLite Database**: Conversations are persistently stored in `data/chathistory.db` and survive application restarts.
- **Configurable Size**: The number of messages to remember is configurable via the `CHAT_MEMORY_SIZE` environment variable.
- **Automatic Creation**: The database file is automatically created when you start your first conversation.

### Database Persistence

The SQLite database is mapped to your host machine via Docker volumes:
- **Location**: `./data/chathistory.db` on your host machine
- **Table**: `message_store` (configurable via `DATABASE_TABLE_NAME`)
- **Schema**: Stores session IDs, message content, timestamps, and metadata
- **Backup**: You can backup conversations by copying the `data/chathistory.db` file

## 🐳 Docker Services

### Ollama Service (`ollama-app`)
- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Volume**: Persistent model storage.
- **Health Check**: Ensures the service is fully running before dependent services start.

### App Service (`app`)
- **Build**: From the `Dockerfile` in the root directory.
- **Port**: `8501`
- **Volume**: `./data:/app/data` for database persistence
- **Dependencies**: Waits for the `ollama-pull-models` service to complete successfully.

### Ollama Pull Models Service (`ollama-pull-models`)
- **Image**: `ollama/ollama:latest`
- **Function**: Pulls the default Ollama model at startup, after the `ollama-app` service is healthy.

## 🛠️ Development

### Project Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Streamlit     │    │    LangChain     │    │     Ollama     │
│  (Frontend)     │◄──►│ (Orchestration)  │◄──►│  (LLM Server)  │
└─────────────────┘    └──────────────────┘    └────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
│     main.py     │    │   chatbot.py    │    │  Local Models  │
│    (UI Logic)   │    │  (Chat Logic)   │    │  (gemma:2b, etc.)│
└─────────────────┘    └─────────────────┘    └────────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
│  Session State  │    │ Memory Manager  │    │ SQLite Database│
│ (In-memory per  │    │ (Manages memory │    │ (Persistent    │
│     session)    │    │   for LangChain)│    │   Storage)     │
└─────────────────┘    └─────────────────┘    └────────────────┘
```

### Key Components

1. **OllamaChatbot** (`app/chatbot.py`)
   - Core chatbot logic.
   - Integrates with LangChain and Ollama.
   - Manages model switching.

2. **ChatMemoryManager** (`app/memory_manager.py`)
   - Manages the conversation buffer for LangChain.
   - Handles SQLite database operations for persistent storage.
   - Manages async/sync compatibility for database operations.

3. **Config** (`app/config.py`)
   - Handles application configuration from environment variables.
   - Validates the configuration at startup.

4. **Streamlit Interface** (`main.py`)
   - Renders the web UI.
   - Manages user sessions and chat history.
   - Handles user input and displays the chatbot's response.

## 🎛️ Web Interface Features

- **Real-time Chat**: Instant responses with typing indicators
- **Memory Controls**: Clear conversation, restart bot
- **Model Information**: View current model and settings
- **Conversation Summary**: Statistics and message count
- **Responsive Design**: Works on desktop and mobile

## 🔍 Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check the logs of the app service to see connection errors
   docker compose logs streamlit-app
   
   # Restart the Ollama service
   docker compose restart ollama-app
   ```

2. **Model Not Found**
   ```bash
   # Check the logs of the model pulling service
   docker compose logs ollama-pull-models
   
   # Manually pull a model if needed
   docker compose exec ollama-app ollama pull <model-name>
   
   # List available models
   docker compose exec ollama-app ollama list
   ```

3. **Port Conflicts**
   ```bash
   # Check what's using the ports
   # On Linux/Mac
   sudo lsof -i :8501
   sudo lsof -i :11434
   
   # On Windows
   netstat -aon | findstr ":8501"
   netstat -aon | findstr ":11434"
   
   # Modify ports in docker-compose.yml if needed
   ```

4. **Database Issues**
   ```bash
   # Check if database file exists
   ls -la data/chathistory.db
   
   # Check database permissions (Linux/Mac)
   ls -la data/
   
   # Reset database (removes all conversation history)
   rm data/chathistory.db
   docker-compose restart streamlit-app
   
   # Check database content (requires sqlite3)
   sqlite3 data/chathistory.db "SELECT * FROM message_store LIMIT 5;"
   ```

5. **Memory/Context Issues**
   ```bash
   # Clear conversation via web interface
   # Click "🗑️ Clear Conversation" button
   
   # Or restart the application
   docker-compose restart streamlit-app
   ```

### Logs and Debugging

```bash
# View logs for all services in real-time
docker compose logs -f

# View logs for a specific service
docker compose logs -f ollama-app
docker compose logs -f streamlit-app

# Check the status of all services
docker compose ps
```
