import requests 
from typing import Final
from telegram import Update 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
import logging
import openai 
import re

# Constants
TOKEN: Final = '7658799183:AAFdhDnLtU-UQXQDIGChcxN7_Z93p5F97XA'
BOT_USERNAME: Final = '@xxLIGHTxx_BOT'
OPENAI_API_KEY: Final = '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'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Function to interact with OpenAI
async def get_openai_response(prompt: str) -> str:
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process your request at the moment."

# Function to solve math problems locally
def solve_math_locally(expression: str) -> str:
    try:
        # Remove any unwanted characters
        sanitized_expression = re.sub(r'[^0-9+\-*/().^ ]', '', expression)
        # Replace ^ with ** for Python exponentiation
        sanitized_expression = sanitized_expression.replace('^', '**')
        result = eval(sanitized_expression)
        return f"The answer is: {result}"
    except Exception as e:
        logger.error(f"Error solving math locally: {e}")
        return "Sorry, I couldn't solve this math problem."

# Function to handle text responses
def handle_responses(text: str) -> str:
    processed = text.lower()

    responses = {
        'hello': 'Hey there! How can I assist you today?',
        'hi': 'Hi! How’s it going?',
        'how are you': 'I’m just a bot, but I’m doing great! How about you?',
        'who created you?': 'I was created by Chaitanya & Rachita to assist with various tasks.',
        'piece of wisdom': 'FOCUS! What you focus on grows.',
        'tell me a joke': 'Why don’t skeletons fight each other? They don’t have the guts!',
        'what is your name?': 'My name is LightBot, your friendly assistant.',
        'thank you': 'You’re welcome! Let me know if there’s anything else I can help with.',
        'goodbye': 'Goodbye! Have a wonderful day!',
        'tell me a fact': 'Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!',
        'why is the sky blue?': 'The sky appears blue because molecules in the air scatter blue light from the sun more than they scatter red light.',
        'what is the meaning of life?': 'The meaning of life is subjective, but many believe it’s about love, learning, and making the world a better place.',
        'i am bored': 'Why not try something new today? Learn a skill, read a book, or ask me to tell you a joke!',
        'do you like humans?': 'Of course! Humans are amazing, and I’m here to make life easier for you.',
        'what is the weather?': 'I can’t check real-time weather directly, but you can ask me for weather-related websites!',
        'do you dream?': 'As a bot, I don’t dream, but if I did, it’d probably be about helping people more efficiently!',
        'do you have feelings?': 'I don’t have feelings, but I’m programmed to understand and respond to yours.',
        'what is your favorite color?': 'I’d say it’s blue—like the sky and the ocean!',
        'do you believe in magic?': 'Technology is like magic that works in the real world!',
        'can you sing?': 'I can’t sing, but I can tell you a song lyric: "Don’t stop believin’!" 🎶',
        'do you know any riddles?': 'Sure! Here’s one: What has keys but can’t open locks? A piano!',
        'tell me a quote': '“The only way to do great work is to love what you do.” — Steve Jobs',
        'i need motivation': 'You can do anything you set your mind to. Start small, but start today!',
        'do you know any trivia?': 'Here’s a fun fact: A group of flamingos is called a "flamboyance."',
        'are you real?': 'I exist in the digital world, so I’m real in my own way!',
        'can you dance?': 'I can’t dance, but I bet you’d be great at it!',
        'tell me a fun fact': 'Sure! Did you know that bananas are berries, but strawberries aren’t?',
        'are you alive?': 'Not quite. I’m just a very smart program!',
        'why is water wet?': 'Water feels wet because it activates sensory neurons in your skin when in contact.',
        'can you help me?': 'I’ll do my best! Tell me what you need help with.',
        'are you smart?': 'I’m as smart as the data and code that power me!',
        'why are we here?': 'That’s one of life’s biggest questions. Perhaps to explore, love, and create!',
        'what is a black hole?': 'A black hole is a region of space where gravity is so strong that not even light can escape.',
        'capital of india': 'New Delhi',
        'capital of france':'Paris',
        'christmas is celebrated on':'25 December',
        'What is the meaning of Life':'The meaning of life is to create your own purpose and find joy in the journey'
        'Who was the first person to walk on the moon?: Neil Armstrong'
        'Which is the longest river in the world?:The Nile River'
        'Which planet is known as the "Red Planet"?:Mars'
    }

    # Loop through the predefined responses
    for key, value in responses.items():
        if key in processed:
            return value

    # Detect math problems
    if any(char.isdigit() for char in text) and any(op in text for op in "+-*/^="):
        return "math_problem"

    # Explicitly return None for unrecognized inputs
    return None

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.chat.id
    message_type = update.message.chat.type

    logger.info(f"Message from User({user_id}) in {message_type} chat: {text}")

    if message_type == 'group' and BOT_USERNAME in text:
        text = text.replace(BOT_USERNAME, '').strip()

    response = handle_responses(text)

    if response == "math_problem":
        response = solve_math_locally(text)
    elif response is None:
        try:
            response = await get_openai_response(text)
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            response = "Sorry, I couldn't process your request at the moment."

    await update.message.reply_text(response)

# Error handling
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, I am LightBot! I can help you with various tasks lightning fast.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Use /start to begin. Mention me in groups to get my attention!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command placeholder.')

async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('The name "Python" comes from the British comedy television show Monty Python Flying Circus.')

async def formula1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('(a + b)^2 = a^2 + 2ab + b^2.')

async def formula2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('(a - b)^2 = a^2 - 2ab + b^2')

# Main function
def main():
    logger.info('Starting bot...')

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('fact', fact_command))
    app.add_handler(CommandHandler('formula_1', formula1_command))
    app.add_handler(CommandHandler('formula_2', formula2_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    logger.info('Bot is polling...')
    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
