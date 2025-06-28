import logging
import os
from io import BytesIO

import torch
from dotenv import load_dotenv
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "nlpconnect/vit-gpt2-image-captioning")

# --- AI Model Loading ---
logger.info(f"Loading model: {HF_MODEL_NAME}")
model = None
try:
    model = VisionEncoderDecoderModel.from_pretrained(HF_MODEL_NAME)
    feature_extractor = ViTImageProcessor.from_pretrained(HF_MODEL_NAME)
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    logger.info(f"Model loaded successfully on {device}.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    # Exit if model fails to load
    exit()
# --- End AI Model Loading ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm an image captioning bot. Send me an image, and I'll tell you what I see."
    )

def generate_caption(image: Image.Image) -> str:
    """Generates a caption for the given image."""
    logger.info("Generating caption for image.")
    
    # The model `microsoft/florence2-base` requires a different processing pipeline.
    # This implementation is for ViT-GPT2 style models.
    if "florence" in HF_MODEL_NAME.lower():
        # Using a different model family like Florence-2 would require a different
        # implementation for processing and generation.
        return "The selected model (`microsoft/florence2-base`) is not directly compatible with this bot's current implementation. Please use a ViT-GPT2-like model."

    max_length = 16
    num_beams = 4
    gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

    pixel_values = feature_extractor(images=[image], return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    output_ids = model.generate(pixel_values, **gen_kwargs)

    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    
    logger.info(f"Generated caption: '{preds[0]}'")
    return preds[0]

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming photos and generates a caption."""
    chat_id = update.effective_chat.id
    logger.info(f"Received image from chat_id: {chat_id}")

    await context.bot.send_message(chat_id=chat_id, text="Processing your image...")

    # Get the largest photo sent
    photo_file = await update.message.photo[-1].get_file()
    
    # Download the photo into a BytesIO object
    file_bytes = await photo_file.download_as_bytearray()
    image_stream = BytesIO(file_bytes)
    
    try:
        image = Image.open(image_stream).convert("RGB")
        caption = generate_caption(image)
        await context.bot.send_message(chat_id=chat_id, text=f"Caption: {caption}")
    except Exception as e:
        logger.error(f"An error occurred while processing the image: {e}")
        await context.bot.send_message(chat_id=chat_id, text="Sorry, I couldn't process that image.")


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found. Please create a .env file and add it.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    logger.info("Bot is running. Press Ctrl-C to stop.")
    application.run_polling()


if __name__ == '__main__':
    main()
