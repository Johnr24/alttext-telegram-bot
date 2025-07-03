# Telegram Image Captioning Bot

This bot uses a Hugging Face vision model to generate captions for images sent to it via Telegram. It supports guided captioning, where you can provide a prompt to influence the output.

## Features

-   Generate image captions using state-of-the-art vision models.
-   Guide the caption generation with your own text prompts.
-   Set custom suffixes for captions.
-   Lazy loading of models to conserve resources.
-   Supports gated models from Hugging Face.

## Setup and Installation

### Prerequisites

-   Python 3.8+
-   A Telegram Bot Token. You can get one from [BotFather](https://t.me/botfather).
-   A Hugging Face account and User Access Token (for gated models).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd <repo_directory>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    -   Copy the example environment file:
        ```bash
        cp env.example .env
        ```
    -   Edit the `.env` file with your details.

### Configuration (`.env` file)

-   `TELEGRAM_BOT_TOKEN`: Your token from BotFather.
-   `HF_MODEL_NAME`: The Hugging Face model to use. Defaults to a gated Gemma model.
-   `HF_TOKEN`: Your Hugging Face User Access Token. This is **required** for gated models like Gemma.
    -   You can create a token in your Hugging Face account settings: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
    -   You also need to request access to the gated model on its Hugging Face page. For `google/gemma-3n-E4B-it`, you would visit its page and accept the terms.
-   `USER`: Your name, used in the default polite notice.
-   `ALLOWED_USER_IDS`: A comma-separated list of Telegram user IDs who are allowed to use the bot. If empty, all users are allowed.
-   `SYSTEM_PROMPT`: The system prompt for the model.

### Pre-downloading Gated Models for Docker

To run the bot inside Docker without it needing to download models or authenticate with Hugging Face, you must pre-download the model to a local cache directory that gets mounted into the container.

This is the recommended setup for using gated models with Docker.

1.  **Log in to Hugging Face CLI:**
    ```bash
    huggingface-cli login
    ```
    (This requires `huggingface-hub` which is in `requirements.txt`)

2.  **Create the cache directory:**
    This directory is mapped as a volume in `docker-compose.yml`.
    ```bash
    mkdir -p ./hf_cache
    ```

3.  **Download the model:**
    Replace the `repo-id` with your desired model.
    ```bash
    huggingface-cli download --repo-id google/gemma-3n-E4B-it --cache-dir ./hf_cache
    ```

Now, when you run `docker-compose up`, the bot will find the model files in the mounted volume and won't need to download them.

### Running the Bot

Once configured, you can run the bot with:

```bash
python bot.py
```

## Usage

-   **Send an image:** The bot will generate a caption for it.
-   **Send an image with a caption:** The text you provide will be used to guide the model's caption generation.
-   **/help:** Shows the help message with all commands.
-   **/setsuffix <message>:** Sets a custom suffix for your captions.

## Supported Models

The bot is configured to work with vision-language models like Qwen and Gemma. You can change the model by updating `HF_MODEL_NAME` in your `.env` file. Note that different models may have different performance and resource requirements.
