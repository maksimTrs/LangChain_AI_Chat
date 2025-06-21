# AI Chatbot with LangChain + Ollama + Streamlit

A complete AI chatbot solution featuring:
- 🦜 **LangChain** for conversation management
- 🦙 **Ollama** for local LLM inference (via Docker)
- 🎨 **Stable Diffusion** for local image generation (GPU/CPU support)
- 🗄️ **SQLite Database** for persistent conversation storage
- 🧠 **Memory Management** for conversation context per session
- 🐳 **Docker** for easy deployment with GPU profiles
- ⚡ **Streamlit** for a beautiful web interface

## 🏗️ Project Structure

```
LangChain_AI_Chat/
├── app/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── memory_manager.py
│   ├── image_generator.py      # Image generation logic
│   └── config.py
├── data/
│   ├── chathistory.db          # SQLite database (auto-created)
│   └── generated_images/       # Generated images storage
├── static/
│   └── style.css
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
├── SETUP_GUIDE.md
├── IMAGE_GENERATION_GUIDE.md   # Image generation documentation
└── setup_image_generation.py   # Image setup validation
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

**For GPU users (RTX 4090, RTX 3060, etc.):**
```bash
docker-compose --profile gpu up --build
```

**For CPU-only users:**
```bash
docker-compose up --build
```

This will build the Streamlit application image and start all services in the correct order.

3. **Ollama models:**
The `docker-compose.yml` is configured to automatically pull the default models (`gemma:2b`, `llama3.2:1b`). The model pulling service will wait until the Ollama service is healthy before starting.

4. **Access the chatbot:**
   - Open http://localhost:8501 in your browser.
   - Use chat for conversations
   - Use commands like "generate image of a sunset" for image creation

## 🔧 Configuration

### Environment Variables

You can customize the application by creating a `.env` file in the root of the project. We provide a `.env.example` file with all available options:

```bash
# Copy the example file and customize it
cp .env.example .env
```

The `.env.example` file includes all configurable options with descriptions. Main settings include:

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

### Image Generation Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_MODEL` | `runwayml/stable-diffusion-v1-5` | Hugging Face model ID for image generation. |
| `IMAGE_HEIGHT` | `512` | Generated image height in pixels. |
| `IMAGE_WIDTH` | `512` | Generated image width in pixels. |
| `IMAGE_STEPS` | `20` | Number of inference steps (higher = better quality). |
| `IMAGE_GUIDANCE_SCALE` | `7.5` | How closely to follow the prompt (1-20). |
| `IMAGE_OUTPUT_DIR` | `./data/generated_images` | Directory to save generated images. |
| `IMAGE_AUTO_LOAD` | `true` | Automatically load image model on startup. |

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

## 🎨 Image Generation Features

The chatbot includes local image generation powered by Stable Diffusion:

### Supported Commands
- `generate image of [description]`
- `create picture of [description]` 
- `draw [description]`
- `illustrate [description]`

### Key Features
- **Local Generation**: No external APIs required
- **GPU Acceleration**: Automatic GPU detection and optimization
- **Memory Management**: Smart memory handling for GPU/CPU
- **Download Support**: Download generated images
- **Chat Integration**: Images appear directly in chat history
- **Persistent Storage**: Images saved to `./data/generated_images/`

### Performance
- **GPU (RTX 4090)**: ~2-5 seconds per image
- **GPU (RTX 3060)**: ~5-15 seconds per image  
- **CPU**: 2-10 minutes per image (not recommended)

### Requirements
- **GPU Mode**: NVIDIA GPU with 4GB+ VRAM
- **CPU Mode**: 8GB+ system RAM (very slow)
- **Storage**: 5GB+ for model downloads

> 📖 **Detailed Guide**: See [IMAGE_GENERATION_GUIDE.md](IMAGE_GENERATION_GUIDE.md) for complete setup instructions.

## 🐳 Docker Services

### Ollama Service (`ollama-app`)
- **Image**: `ollama/ollama:latest`
- **Port**: `11434`
- **Volume**: Persistent model storage.
- **Health Check**: Ensures the service is fully running before dependent services start.

### App Service (`app` / `app-gpu`)
- **Build**: From the `Dockerfile` in the root directory.
- **Port**: `8501`
- **Volumes**: 
  - `./data:/app/data` for database and image persistence
  - `huggingface_cache:/root/.cache/huggingface` for model caching
- **Profiles**: 
  - `app` (CPU profile): Default, no GPU acceleration
  - `app-gpu` (GPU profile): NVIDIA GPU acceleration enabled
- **Dependencies**: Waits for the `ollama-app` service to be healthy.

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
│    (UI Logic)   │    │  (Chat Logic)   │    │ (gemma:2b,etc.)│
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

### Chat Features
- **Real-time Chat**: Instant responses with typing indicators
- **Image Generation**: Generate images directly in chat
- **Memory Controls**: Clear conversation, restart bot
- **Download Support**: Download generated images

### Sidebar Controls
- **Model Selection**: Switch between available LLM models
- **Response Style**: Choose complexity level (Beginner/Expert/PhD)
- **Image Generation**: Load/unload image models, GPU memory management
- **Model Information**: View current model and settings
- **Conversation Summary**: Statistics and message count

### Technical Features
- **Responsive Design**: Works on desktop and mobile
- **Session Management**: Independent conversations per user
- **Persistent Storage**: Chat history and images survive restarts
- **GPU Monitoring**: Real-time GPU memory usage (GPU mode)

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
