# Using Local Models with 01Agent

This guide explains how to set up and use local large language models (LLMs) with 01Agent via Ollama and LM Studio.

## Ollama

### 1. Install Ollama

First, you need to install Ollama on your system. Follow the instructions on the official Ollama website:

[https://ollama.com/download](https://ollama.com/download)

### 2. Pull a Model

Once Ollama is installed, you can pull a model. For example, to pull the Llama 2 model, open your terminal and run:

```bash
ollama pull llama2
```

You can find a list of available models on the Ollama models page: [https://ollama.com/library](https://ollama.com/library)

### 3. Configure 01Agent to Use Ollama

To use Ollama with 01Agent, you need to configure your backend's `.env` file.

1.  **Ensure Ollama Server is Running**: Make sure the Ollama server is running in the background. It usually starts automatically after installation.
2.  **Set `OLLAMA_URL`**: In your `backend/.env` file (or `backend/.env.example` if you're setting it up for the first time), ensure `OLLAMA_URL` is set to the correct address of your Ollama server. The default is usually `http://127.0.0.1:11434`.

    ```dotenv
    OLLAMA_URL=http://127.0.0.1:11434
    ```

3.  **Configure Agents to Use Ollama**: For each agent you want to use with Ollama, set its `_AGENT_MODEL_TYPE` to `ollama` and its `_AGENT_MODEL_ID` to the name of the model you pulled (e.g., `llama2`).

    For example, to use Llama 2 for the `CLASSIFIER_AGENT`:

    ```dotenv
    CLASSIFIER_AGENT_MODEL_TYPE=ollama
    CLASSIFIER_AGENT_MODEL_ID=llama2
    ```

    Repeat this for any other agents (e.g., `TITLE_AGENT`, `SUGGESTOR_AGENT`, `PLANNER_AGENT`, `COMPUTER_USE_AGENT`, `SUMMARIZER_AGENT`) that you wish to power with Ollama.

## LM Studio

### 1. Install LM Studio

Download and install LM Studio from their official website:

[https://lmstudio.ai/](https://lmstudio.ai/)

### 2. Download and Load a Model

Inside LM Studio, you can browse and download various models. Once downloaded, load the model you wish to use into the server.

### 3. Start the Local Server

In LM Studio, navigate to the "Local Server" tab and click "Start Server". By default, it runs on `http://localhost:1234`.

### 4. Configure 01Agent to Use LM Studio

To use LM Studio with 01Agent, you need to configure your backend's `.env` file.

1.  **Set `OPENAI_API_BASE`**: In your `backend/.env` file, set `OPENAI_API_BASE` to the address of your LM Studio server's OpenAI-compatible API endpoint. The default is usually `http://localhost:1234/v1`.

    ```dotenv
    OPENAI_API_BASE=http://localhost:1234/v1
    ```

2.  **Set `OPENAI_API_KEY`**: LM Studio does not require an API key, but the `ChatOpenAI` client expects one. You can set `OPENAI_API_KEY` to any non-empty string (e.g., `sk-lmstudio`).

    ```dotenv
    OPENAI_API_KEY=sk-lmstudio
    ```

3.  **Configure Agents to Use OpenAI**: For each agent you want to use with LM Studio, set its `_AGENT_MODEL_TYPE` to `openai` and its `_AGENT_MODEL_ID` to the model name you are using in LM Studio (e.g., `gemma-2b-it`).

    For example, to use a model from LM Studio for the `CLASSIFIER_AGENT`:

    ```dotenv
    CLASSIFIER_AGENT_MODEL_TYPE=openai
    CLASSIFIER_AGENT_MODEL_ID=gemma-2b-it
    ```

    Repeat this for any other agents that you wish to power with LM Studio.

After making these changes, restart your 01Agent backend for the new configuration to take effect.
