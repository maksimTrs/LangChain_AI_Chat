# LangChain AI Chat Framework - Complete Setup Guide

This guide provides step-by-step instructions to set up and run the AI chatbot framework from scratch.

## Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.11+** (Download from [python.org](https://python.org))
- **Docker Desktop** (Download from [docker.com](https://docker.com))
- **Git** (Download from [git-scm.com](https://git-scm.com))

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd LangChain_AI_Chat
```

### Step 2: Create Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env
```

**Optional**: Edit the `.env` file to customize settings:
```bash
# Default configuration (you can modify these)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:30b-a3b-q4_K_M
CHAT_MEMORY_SIZE=10
STREAMLIT_SERVER_PORT=8501
```

### Step 3: Start Ollama Service with Docker

```bash
# Start Ollama in Docker (this will also pull the configured models)
docker-compose up -d
```

This command will:
- Start the Ollama service on port 11434
- Automatically pull the following models:
  - `qwen3:30b-a3b-q4_K_M` (30B parameter model, quantized)
  - `gemma3:12b-it-qat` (12B parameter instruction-tuned model)
  - `nomic-embed-text` (embedding model)

**Note**: Model downloading may take 10-30 minutes depending on your internet speed.

### Step 4: Verify Ollama is Running

```bash
# Check if containers are running
docker ps

# Check Ollama service health
curl http://localhost:11434/api/tags
```

You should see the downloaded models listed in the response.

### Step 5: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### Step 6: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 7: Run the Application

```bash
# Start the Streamlit web interface
streamlit run main.py
```

### Step 8: Access the Chatbot

Open your web browser and navigate to:
```
http://localhost:8501
```

You should see the AI chatbot interface!

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen3:30b-a3b-q4_K_M` | Model to use for chat |
| `CHAT_MEMORY_SIZE` | `10` | Number of messages to remember |
| `STREAMLIT_SERVER_PORT` | `8501` | Web interface port |

### Switching Models

1. Edit the `.env` file and change the `OLLAMA_MODEL` value to one of the available models:
   - `qwen3:30b-a3b-q4_K_M`
   - `gemma3:12b-it-qat`

2. Restart the Streamlit application:
   ```bash
   # Stop the current application (Ctrl+C)
   # Then restart it
   streamlit run main.py
   ```

### Adding New Models

To add more models, edit the `docker-compose.yml` file and add additional pull commands in the `ollama-pull-models` service:

```yaml
# Pull large language models
OLLAMA_HOST=ollama:11434 ollama pull qwen3:30b-a3b-q4_K_M
OLLAMA_HOST=ollama:11434 ollama pull gemma3:12b-it-qat
OLLAMA_HOST=ollama:11434 ollama pull your-new-model  # Add this line
```

Then restart Docker Compose:
```bash
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused Error
**Problem**: Cannot connect to Ollama service

**Solution**:
```bash
# Check if Docker containers are running
docker ps

# If not running, start them
docker-compose up -d

# Check Ollama logs
docker logs ollama
```

#### 2. Model Not Found Error
**Problem**: Selected model is not available

**Solution**:
```bash
# Check available models
curl http://localhost:11434/api/tags

# Or check Docker logs for model pulling status
docker logs ollama-pull-llama
```

#### 3. Out of Memory Error
**Problem**: System runs out of memory when loading large models

**Solution**: Enable RAM optimization in `docker-compose.yml`:
```yaml
environment:
  # Uncomment these lines:
  - OLLAMA_FLASH_ATTENTION=true
  - OLLAMA_KV_CACHE_TYPE=f16
  - OLLAMA_MAX_LOADED_MODELS=1
```

#### 4. Port Already in Use
**Problem**: Port 8501 or 11434 is already in use

**Solution**: Change ports in `.env` file:
```bash
STREAMLIT_SERVER_PORT=8502  # Change to different port
```

### Viewing Logs

```bash
# Ollama service logs
docker logs ollama

# Model pulling logs
docker logs ollama-pull-llama

# Streamlit logs are visible in the terminal where you run the app
```

## Performance Tips

1. **For better performance with limited RAM**: Uncomment the environment variables in `docker-compose.yml`
2. **For faster responses**: Use smaller models like `gemma3:12b-it-qat` instead of `qwen3:30b-a3b-q4_K_M`
3. **For better quality**: Use larger models but ensure you have sufficient RAM (16GB+ recommended)

## Project Structure

```
LangChain_AI_Chat/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── chatbot.py         # Core chatbot logic with LangChain
│   ├── memory_manager.py  # Conversation memory management
│   └── config.py          # Configuration management
├── docker-compose.yml     # Ollama Docker service configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment configuration
├── main.py               # Streamlit web interface
├── README.md             # Project documentation
└── SETUP_GUIDE.md        # This setup guide
```

## Next Steps

Once you have the chatbot running:

1. **Experiment with different models** to find the best balance of speed and quality for your use case
2. **Adjust memory settings** in the `.env` file to control conversation context length
3. **Explore the code** in the `app/` directory to understand how LangChain integrates with Ollama
4. **Customize the Streamlit interface** in `main.py` to add new features

## Support

If you encounter issues not covered in this guide:

1. Check the Docker and Streamlit logs for error messages
2. Ensure all prerequisites are properly installed
3. Verify that your system meets the hardware requirements for the selected models
4. Try using a smaller model if you're experiencing memory issues

Enjoy your local AI chatbot! 🚀