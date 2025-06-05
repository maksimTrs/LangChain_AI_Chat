# AI Chatbot with LangChain + Ollama + Streamlit

A complete AI chatbot solution featuring:
- 🦜 **LangChain** for conversation management
- 🦙 **Ollama** for local LLM inference (via Docker)
- 🧠 **In-memory** for conversation context per session
- 🐳 **Docker** for easy deployment
- ⚡ **Streamlit** for a beautiful web interface

## 🏗️ Project Structure

```
ai-chatbot/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── chatbot.py         # Core chatbot logic
│   ├── memory_manager.py  # Conversation memory management
│   └── config.py          # Configuration management
├── static/
│   └── style.css          # Custom CSS for the web interface
├── Dockerfile              # Dockerfile for the Streamlit application
├── docker-compose.yml     # Docker services configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── main.py             # Streamlit web interface
└── README.md           # This file
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
cd ai-chatbot
```

2. **Start the services:**
```bash
docker compose up -d --build
```
This will build the Streamlit application image and start all the services.

3. **Ollama models:**
The `docker-compose.yml` is configured to automatically pull the default model (`gemma:2b`).

4. **Access the chatbot:**
   - Open http://localhost:8501 in your browser.

## 🔧 Configuration

### Environment Variables

You can customize the application by creating a `.env` file in the root of the project.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL. When running with Docker, this is `http://ollama:11434`. |
| `OLLAMA_MODEL` | `gemma:2b` | The default model to use. |
| `OLLAMA_TEMPERATURE` | `0.7` | The temperature for the LLM. |
| `OLLAMA_TOP_P` | `0.9` | The top_p for the LLM. |
| `OLLAMA_NUM_PREDICT` | `512` | The number of tokens to predict. |
| `CHAT_MEMORY_SIZE` | `10` | Number of messages to remember in a session. |
| `STREAMLIT_SERVER_PORT` | `8501` | Web interface port. |

### Available Models

The default model is `gemma:2b`. You can change the model by setting the `OLLAMA_MODEL` environment variable. Make sure the model is available in your Ollama instance. You can add more models to be pulled at startup by editing the `command` in the `ollama-pull-models` service in `docker-compose.yml`.

## 🧠 Memory Management

The chatbot uses Streamlit's session state to manage conversation history.
- **Session-based Memory**: Each user session has its own independent conversation history.
- **In-memory**: The history is stored in memory and is not persisted across application restarts.
- **Configurable Size**: The number of messages to remember is configurable via the `CHAT_MEMORY_SIZE` environment variable.

## 🐳 Docker Services

### Ollama Service
- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Volume**: Persistent model storage.
- **Health Check**: Ensures the service is running before the app starts.

### App Service
- **Build**: From the `Dockerfile` in the root directory.
- **Port**: `8501`
- **Dependencies**: Depends on the `ollama` and `ollama-pull-models` services.

### Ollama Pull Models Service
- **Image**: `ollama/ollama:latest`
- **Function**: Pulls the default Ollama model at startup.

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
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│  Session State  │    │ Memory Manager  │
│ (In-memory per  │    │ (Manages memory │
│     session)    │    │   for LangChain)│
└─────────────────┘    └─────────────────┘
```

### Key Components

1. **OllamaChatbot** (`app/chatbot.py`)
   - Core chatbot logic.
   - Integrates with LangChain and Ollama.
   - Manages model switching.

2. **ChatMemoryManager** (`app/memory_manager.py`)
   - Manages the conversation buffer for LangChain.

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
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama service
   docker-compose restart ollama
   ```

2. **Model Not Found**
   ```bash
   # Pull the model
   docker exec -it ollama-server ollama pull llama2
   
   # List available models
   docker exec -it ollama-server ollama list
   ```

3. **Memory Issues**
   ```bash
   # Clear chat history
   rm -f chat_history_*.json
   
   # Or use the web interface "Clear Conversation" button
   ```

4. **Port Conflicts**
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :8501
   netstat -tulpn | grep :11434
   
   # Modify ports in docker-compose.yml if needed
   ```

### Logs and Debugging

```bash
# View Ollama Docker logs
docker-compose logs -f

# View Ollama service logs
docker-compose logs -f ollama

# Check Docker service health
docker-compose ps

# View Streamlit logs
# These will be visible in the terminal where you run the Streamlit app
```

## 📊 Performance Tips

1. **Model Selection**:
   - Use smaller models (7B) for faster responses
   - Use larger models (13B+) for better quality

2. **Memory Management**:
   - Reduce `CHAT_MEMORY_SIZE` for faster processing
   - Increase for better context retention

3. **Hardware Requirements**:
   - Minimum: 8GB RAM, 4 CPU cores
   - Recommended: 16GB RAM, 8 CPU cores
   - GPU: Optional but significantly faster

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - For the amazing framework
- [Ollama](https://ollama.ai/) - For local LLM serving
- [Streamlit](https://streamlit.io/) - For the beautiful web interface
- [Meta](https://ai.meta.com/llama/) - For the Llama models

---

**Happy Chatting! 🤖💬**