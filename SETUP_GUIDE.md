# LangChain AI Chat Framework - Complete Setup Guide

This guide provides step-by-step instructions to set up and run the AI chatbot framework.

## Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.9+** (Download from [python.org](https://python.org))
- **Docker Desktop** (Download from [docker.com](https://docker.com))
- **Git** (Download from [git-scm.com](https://git-scm.com))

## Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd LangChain_AI_Chat
```

### Step 2: Start the Application with Docker

```bash
# Build the application image and start all services
docker compose up -d --build
```

This command will:
- Build the Docker image for the Streamlit application.
- Start the Ollama service on port 11434.
- Start the Streamlit app service on port 8501.
- Automatically pull the default model: `gemma:2b`.

**Note**: The initial model download may take some time depending on your internet connection.

### Step 3: Verify the Services are Running

```bash
# Check if containers are running
docker ps

# Check Ollama service health and available models
curl http://localhost:11434/api/tags
```

You should see the `streamlit-app`, `ollama`, and `ollama-pull-models` containers running. The curl command should list the `gemma:2b` model.

### Step 4: Access the Chatbot

Open your web browser and navigate to:
```
http://localhost:8501
```

You should see the AI chatbot interface!

## Configuration Options

### Environment Variables

You can customize the application by creating a `.env` file in the project root.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama server URL (for Docker). Use `http://localhost:11434` for local dev. |
| `OLLAMA_MODEL` | `gemma:2b` | The default model to use. |
| `OLLAMA_TEMPERATURE` | `0.7` | The temperature for the LLM. |
| `OLLAMA_TOP_P` | `0.9` | The top_p for the LLM. |
| `OLLAMA_NUM_PREDICT` | `512` | The number of tokens to predict. |
| `CHAT_MEMORY_SIZE` | `10` | Number of messages to remember in a session. |
| `STREAMLIT_SERVER_PORT` | `8501` | Web interface port. |

### Switching Models

You can switch the model at runtime from the sidebar in the application. To change the default model, set the `OLLAMA_MODEL` environment variable in your `.env` file.

### Adding New Models

To add more models to be pulled at startup, edit the `docker-compose.yml` file and add additional pull commands in the `ollama-pull-models` service:

```yaml
command:
  - "-c"
  - |
    # ...
    OLLAMA_HOST=ollama:11434 ollama pull gemma:2b
    OLLAMA_HOST=ollama:11434 ollama pull your-new-model # Add this line
```

Then restart Docker Compose:
```bash
docker compose down
docker compose up -d --build
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused Error
**Problem**: The Streamlit app cannot connect to the Ollama service.

**Solution**:
- Ensure the Docker containers are running: `docker ps`.
- Check the logs of the Streamlit app: `docker logs streamlit-app`.
- Verify the `OLLAMA_BASE_URL` is set correctly for your environment.

#### 2. Model Not Found Error
**Problem**: Selected model is not available in Ollama.

**Solution**:
- Check available models: `curl http://localhost:11434/api/tags`.
- Check the logs for the model pulling service: `docker logs ollama-pull-models`.

#### 3. Out of Memory Error
**Problem**: System runs out of memory when loading large models.

**Solution**: Enable RAM optimization by uncommenting the environment variables in the `ollama` service in `docker-compose.yml`.

#### 4. Port Already in Use
**Problem**: Port 8501 or 11434 is already in use.

**Solution**: Change the port mappings in `docker-compose.yml`. For example, change `"8501:8501"` to `"8502:8501"`.

### Viewing Logs

```bash
# Streamlit app logs
docker logs streamlit-app

# Ollama service logs
docker logs ollama

# Model pulling logs
docker logs ollama-pull-models
```

## Project Structure

```
LangChain_AI_Chat/
├── app/
│   ├── __init__.py
│   ├── chatbot.py
│   ├── memory_manager.py
│   └── config.py
├── static/
│   └── style.css
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py
├── README.md
└── SETUP_GUIDE.md
```

## Next Steps

Once you have the chatbot running:

1. **Experiment with different models** from the sidebar.
2. **Adjust memory settings** in a `.env` file to control conversation context length.
3. **Explore the code** in the `app/` directory to understand the application logic.
4. **Customize the Streamlit interface** in `main.py` to add new features.

Enjoy your local AI chatbot! 🚀