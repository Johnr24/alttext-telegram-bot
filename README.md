# Telegram Ollama Image Captioning Bot

This bot connects to a running [Ollama](https://ollama.com/) instance to generate captions for images sent via Telegram. It supports guided captioning and custom suffixes.

## Features

-   Generate image captions using any multimodal model supported by Ollama (e.g., `llava`, `moondream`).
-   Guide the caption generation with your own text prompts.
-   Set custom suffixes for captions.
-   Lightweight bot: the heavy lifting of model inference is handled by a separate Ollama instance.

## How It Works

The bot is a simple Python application that listens for messages on Telegram. When a user sends an image, the bot:
1.  Encodes the image into base64.
2.  Sends the image and any user-provided prompt to the Ollama API.
3.  Receives the generated text from the model.
4.  Extracts the caption from the response.
5.  Sends the formatted caption back to the user in the Telegram chat.

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   A running [Ollama](https://ollama.com/) instance.
-   A multimodal model pulled in Ollama (e.g., `ollama run llava`).
-   A Telegram Bot Token. You can get one from [BotFather](https://t.me/botfather).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd <repo_directory>
    ```
2. **Build with Docker Compose:**
3. b
### Configuration (`.env` file)

-   `TELEGRAM_BOT_TOKEN`: Your token from BotFather.
-   `OLLAMA_HOST`: The full URL of your Ollama instance's API. Defaults to `http://localhost:11434`.
-   `OLLAMA_MODEL`: The name of the multimodal model you have in Ollama (e.g., `llava`, `moondream`).
-   `USER`: Your name, used in the default polite notice. 
    -   You can set your own notice in /setpolitenotice in the app
-   `ALLOWED_USER_IDS`: A comma-separated list of Telegram user IDs who are allowed to use the bot. If empty, all users are allowed.
-   `SYSTEM_PROMPT`: A custom system prompt for the model. If not set, a default prompt is used.
-   `OLLAMA_NUM_PREDICT`: (Optional) Sets the maximum number of tokens for the model's response. For example, `OLLAMA_NUM_PREDICT=512`.

### Running the Bot

1.  **Start your Ollama instance.** Make sure it's running and accessible from where you'll run the bot.

2.  **Pull a model (if you haven't already):**
    ```bash
    ollama pull llava
    ```

3.  **Run the bot:**
    ```bash
    python bot.py
    ```

## Usage

-   **Send an image:** The bot will generate a caption for it.
-   **Send an image with a caption:** The text you provide will be used to guide the model's caption generation.
-   **/help:** Shows the help message with all commands.
-   **/setpolitenotice <message>:** Sets a custom suffix for your captions. Use the command without a message to remove it.

## Docker

You can also run this bot inside a Docker container. The `docker-compose.yml` file is configured to build and run the bot's container.

The main consideration is ensuring the bot container can communicate with your Ollama instance.

### Connecting to Ollama on the Host

If you are running Ollama directly on your host machine, you can make it accessible to the Docker container by setting `OLLAMA_HOST` in your `.env` file.

-   **On Linux:** Use `http://172.17.0.1:11434` (the default Docker bridge network gateway).
-   **On macOS or Windows:** Use `http://host.docker.internal:11434`.

After setting the `OLLAMA_HOST`, you can run the bot with:
```bash
docker-compose up --build
```
