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
- Start the `ollama-app` service on port 11434.
- Start the Streamlit `app` service on port 8501.
- Automatically pull the default model (`gemma:2b`) after the Ollama service is healthy.

**Note**: The initial model download may take some time depending on your internet connection.

### Step 3: Verify the Services are Running

```bash
# Check if all containers are running and healthy
docker compose ps
```

You should see the `streamlit-app`, `ollama-app`, and `ollama-pull-models` containers running. The `ollama-app` container should show a "healthy" status.

### Step 4: Access the Chatbot

Open your web browser and navigate to:
```
http://localhost:8501
```

You should see the AI chatbot interface!

## Key Configuration

You can customize the application by creating a `.env` file in the project root.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama-app:11434` | The URL for the Ollama service inside the Docker network. |
| `OLLAMA_MODEL` | `gemma:2b` | The default model to use for the chat. |

## Troubleshooting

### How to View Logs

```bash
# View live logs for a specific service (e.g., the app)
docker compose logs -f streamlit-app

# View logs for the Ollama service
docker compose logs -f ollama-app
```

### Common Issues

- **Connection Error**: If the app can't connect to Ollama, check the logs for `streamlit-app`. Ensure `ollama-app` is running and healthy (`docker compose ps`).
- **Model Not Found**: Check the logs for `ollama-pull-models` to confirm the model was downloaded. You can also run `docker compose exec ollama-app ollama list` to see available models.

Enjoy your local AI chatbot! 🚀

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