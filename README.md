# AI Chatbot with LangChain + Ollama + Memory

A complete AI chatbot solution featuring:
- 🦜 **LangChain** for conversation management
- 🦙 **Ollama** for local LLM inference (via Docker)
- 🧠 **Persistent Memory** for conversation context
- 🐳 **Docker** for Ollama deployment
- ⚡ **Streamlit** for beautiful web interface

## 🏗️ Project Structure

```
ai-chatbot/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── chatbot.py         # Core chatbot logic
│   ├── memory_manager.py  # Conversation memory management
│   └── config.py          # Configuration management
├── docker-compose.yml     # Ollama Docker service configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── main.py             # Streamlit web interface
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup Instructions

1. **Clone and setup:**
```bash
git clone <your-repo-url>
cd ai-chatbot
cp .env.example .env
```

2. **Start Ollama in Docker:**
```bash
docker-compose up -d
```

3. **Ollama models:**
```bash
# Models will be automatically pulled as configured in docker-compose.yml
# Currently configured models:
# - qwen3:30b-a3b-q4_K_M
# - gemma3:12b-it-qat
```

4. **Setup Python virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

5. **Install dependencies:**
```bash
pip install -r requirements.txt
```

6. **Configure environment:**
```bash
# Edit .env file with your settings
# Make sure OLLAMA_BASE_URL points to your Docker container
# Default: OLLAMA_BASE_URL=http://localhost:11434
```

7. **Run the application:**
```bash
streamlit run main.py
```

8. **Access the chatbot:**
   - Open http://localhost:8501 in your browser

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama2` | Model to use |
| `CHAT_MEMORY_SIZE` | `10` | Number of messages to remember |
| `STREAMLIT_SERVER_PORT` | `8501` | Web interface port |

### Available Models

Popular Ollama models configured in this project:
- `qwen3:30b-a3b-q4_K_M` - Qwen 3 30B model (quantized)
- `gemma3:12b-it-qat` - Gemma 3 12B instruction-tuned model (quantized)

You can add more models by updating the docker-compose.yml file.
- `mistral` - Fast and efficient
- `neural-chat` - Conversational AI

To switch models:
```bash
docker exec -it ollama-server ollama pull <model-name>
# Update OLLAMA_MODEL in .env
# Restart the Streamlit application locally
```

## 🧠 Memory Management

The chatbot features sophisticated memory management:

- **Conversation Buffer**: Keeps last N messages in memory
- **Persistent Storage**: Saves chat history to JSON files
- **Session Management**: Separate conversations per session
- **Memory Summary**: View conversation statistics

### Memory Files
- Location: `./data/` (Docker) or project root (local)
- Format: `chat_history_{session_id}.json`
- Auto-saved after each interaction

## 🎛️ Web Interface Features

- **Real-time Chat**: Instant responses with typing indicators
- **Memory Controls**: Clear conversation, restart bot
- **Model Information**: View current model and settings
- **Conversation Summary**: Statistics and message count
- **Responsive Design**: Works on desktop and mobile

## 🐳 Docker Services

### Ollama Service
- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Volume**: Persistent model storage
- **Health Check**: API endpoint monitoring

### Local Python Application
- **Port**: `8501` (Streamlit)
- **Dependencies**: Connects to Ollama Docker service
- **Storage**: Local file system for chat history

## 🛠️ Development

### Project Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   LangChain     │    │     Ollama      │
│  (Frontend)     │◄──►│  (Orchestration)│◄──►│   (LLM Server)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  main.py        │    │  chatbot.py     │    │  Local Models   │
│  (UI Logic)     │    │  (Chat Logic)   │    │  (llama2, etc.) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Session State  │    │ Memory Manager  │
│  (Temp Storage) │    │ (Persistent)    │
└─────────────────┘    └─────────────────┘
```

### Key Components

1. **OllamaChatbot** (`app/chatbot.py`)
   - Main chatbot logic
   - LangChain integration
   - Model management

2. **ChatMemoryManager** (`app/memory_manager.py`)
   - Conversation persistence
   - Memory buffer management
   - Session handling

3. **Config** (`app/config.py`)
   - Environment configuration
   - Validation logic

4. **Streamlit Interface** (`main.py`)
   - Web UI components
   - User interaction handling
   - Real-time updates

### Adding New Features

1. **Custom Prompts**: Modify the system prompt in `chatbot.py`
2. **New Models**: Add model configurations in `config.py`
3. **UI Components**: Extend the Streamlit interface in `main.py`
4. **Memory Types**: Implement new memory strategies in `memory_manager.py`

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