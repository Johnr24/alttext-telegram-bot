import logging
import os
from io import BytesIO

import torch
from dotenv import load_dotenv
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoModelForCausalLM, AutoProcessor

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "microsoft/Florence-2-base")  # Default to Florence-2 base model
USER = os.getenv("USER", "the user")  # Default to 'john' if USER is not set
ALLOWED_USER_IDS_STR = os.getenv("ALLOWED_USER_IDS")
ALLOWED_USER_IDS = [int(uid.strip()) for uid in ALLOWED_USER_IDS_STR.split(',')] if ALLOWED_USER_IDS_STR else []
FLORENCE2_TASK_PROMPT = os.getenv("FLORENCE2_TASK_PROMPT", "<DETAILED_CAPTION>")

# --- Model Lazy Loading ---
# Global variables to hold the model and processor. They are loaded on demand.
model = None
processor = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model_and_processor():
    """Loads the model and processor into memory if they are not already loaded."""
    global model, processor
    if model is None or processor is None:
        logger.info(f"Loading model: {HF_MODEL_NAME}")
        try:
            # For Florence-2 models, we use AutoModelForCausalLM and AutoProcessor.
            # trust_remote_code=True is required for Florence-2.
            model = AutoModelForCausalLM.from_pretrained(HF_MODEL_NAME, trust_remote_code=True)
            processor = AutoProcessor.from_pretrained(HF_MODEL_NAME, trust_remote_code=True)
            model.to(device)
            logger.info(f"Model loaded successfully on {device}.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Reset to None so we can try again later
            model = None
            processor = None
            raise  # Re-raise the exception to be caught by the caller

def unload_model_and_processor():
    """Unloads the model and processor from memory to free up resources."""
    global model, processor
    if model is not None or processor is not None:
        logger.info("Unloading model from memory.")
        del model
        del processor
        model = None
        processor = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Model unloaded successfully.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        logger.warning(f"Unauthorized access attempt by user_id: {user_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this bot."
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm an image captioning bot. Send me an image, and I'll tell you what I see."
    )

def generate_caption(image: Image.Image) -> str:
    """Generates a caption for the given image using Florence-2 model."""
    logger.info("Generating caption for image.")

    # This function is now specifically for Florence-2 models.
    if "florence" not in HF_MODEL_NAME.lower():
        logger.warning("This caption generation function is designed for Florence-2 models. The current model is not a Florence-2 model.")
        return "This bot is configured for Florence-2 models. The current model is not a Florence-2 model."

    try:
        load_model_and_processor()

        # Use the task prompt from environment variables
        task_prompt = FLORENCE2_TASK_PROMPT
        
        # The processor for Florence-2 handles both text and image.
        inputs = processor(text=task_prompt, images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate caption
        max_new_tokens = 256  # Increased for more detailed captions
        num_beams = 4
        gen_kwargs = {"max_new_tokens": max_new_tokens, "num_beams": num_beams}

        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            **gen_kwargs
        )

        # The processor has a special post-processing step.
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        
        # The post_process_generation function cleans up the output.
        parsed_answer = processor.post_process_generation(
            generated_text, 
            task=task_prompt, 
            image_size=(image.width, image.height)
        )

        caption = parsed_answer.get(task_prompt, "Could not generate caption.")
        
        logger.info(f"Generated caption: '{caption}'")
        return caption
    finally:
        unload_model_and_processor()

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming photos and generates a caption."""
    user_id = update.effective_user.id
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        logger.warning(f"Unauthorized access attempt by user_id: {user_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you are not authorized to use this bot."
        )
        return

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
        await context.bot.send_message(chat_id=chat_id, text=f"{caption}\n\nPolite Notice: this caption is generated by a locally hosted AI model on an ARM Mac Mini, not by an online service or a data center. It may not be accurate or reliable. {USER} uses this method of alt text generation, because they have dyslexia and find writing alt-text mentally taxing")
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
