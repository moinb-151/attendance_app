import os
import sys
import django
from decouple import config

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance.settings")
django.setup()

import requests
import uuid
from datetime import datetime
from decouple import config
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = config("BOT_TOKEN")
API_URL = config("API_BASE_URL")  # Adjust this URL as needed


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = """👋 Welcome to the Attendance Log Bot!

This bot helps you and your team log daily attendance with ease.

📌 Here's what you can do:

/register username <value> - Register yourself (4-digit ID is auto-assigned)
/log <username> <field> <value> [date] - Log your time for arrival, lunch_start, lunch_end, or departure
Example: /log alice arrival 09:00  
Example: /log alice lunch_start 13:00 17-06-25

/ulog <log_id> <field> <value> - Log your time for arrival, lunch_start, lunch_end, or departure
Example: /ulog 2 arrival 09:00  
Example: /ulog 2 lunch_start 13:00 

📁 To get your logs:

/export <username> <start_date> <end_date>  
Example: /export moin 15-06-25 21-06-25

ℹ️ Dates should be in DD-MM-YY format. If no date is provided, today's date will be used.

Let’s get started!"""
    await update.message.reply_text(message.strip())


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /register <field> <value>")
            return

        field = context.args[0]
        value = context.args[1]

        data = {field: value}
        res = requests.post(f"{API_URL}user/register/", json=data)

        try:
            res_data = res.json()
        except Exception as e:
            print("Raw Response Text:", res.text)
            raise ValueError(f"Error: {e}")

        if res.status_code == 201:
            message = f"✅ User registered successfully!\n\n👤 User: {res_data['username']} (ID: {res_data['user_id']})"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"❌ Failed to register user: {res.json()}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Example: /log john arrival 09:00 20-06-25
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage: /log <username> <field> <value> [date (dd-mm-yy)]"
            )
            return

        username = context.args[0]
        field = context.args[1]  # arrival, departure, lunch_start, lunch_end
        value = context.args[2]
        date = (
            context.args[3]
            if len(context.args) >= 4
            else datetime.now().strftime("%d-%m-%y")
        )

        data = {"username": username, field: value, "date": date}

        res = requests.post(f"{API_URL}add-log/", json=data)

        try:
            response_data = res.json()
        except Exception as e:
            print("Raw Response Text:", res.text)
            raise ValueError(f"Error: {e}")

        if res.status_code == 201:
            res_data = res.json()
            user = res_data["user"]
            message = f"""✅ Log added successfully!

📅 Date: {res_data['date']}
👤 User: {user['username']} (ID: {user['user_id']})

⏰ Attendance Summary:
• ID: {res_data['id']}
• Arrival: {res_data.get('arrival', 'Not logged')}
• Lunch Start: {res_data.get('lunch_start', 'Not logged')}
• Lunch End: {res_data.get('lunch_end', 'Not logged')}
• Departure: {res_data.get('departure', 'Not logged')}"""

            await update.message.reply_text(message.strip())
        else:
            await update.message.reply_text(f"❌ Failed to add log: {res.json()}")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def ulog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 3:
            await update.message.reply_text("Usage: /ulog <log-id> <field> <value>")
            return
        log_id = int(context.args[0])
        field = context.args[1]
        value = context.args[2]
        data = {field: value}
        res = requests.patch(f"{API_URL}update-log/{log_id}/", json=data)

        try:
            res_data = res.json()
        except Exception as e:
            print("Raw Response Text:", res.text)
            raise ValueError(f"Error: {e}")

        if res.status_code == 200:
            user = res_data["user"]

            message = f"""✅ Log updated successfully!

📅 Date: {res_data['date']}
👤 User: {user['username']} (ID: {user['user_id']})

⏰ Attendance Summary:
• ID: {res_data['id']}
• Arrival: {res_data.get('arrival', 'Not logged')}
• Lunch Start: {res_data.get('lunch_start', 'Not logged')}
• Lunch End: {res_data.get('lunch_end', 'Not logged')}
• Departure: {res_data.get('departure', 'Not logged')}"""

            await update.message.reply_text(message.strip())
        else:
            await update.message.reply_text(f"❌ Failed to update log: {res.json()}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage: /export <username> <start_date> <end_date> (dd-mm-yy)"
            )
            return

        username, start_date, end_date = context.args

        data = {
            "username": username,
            "start_date": start_date,
            "end_date": end_date,
        }

        res = requests.get(f"{API_URL}export-csv/", params=data)

        if res.status_code == 200:
            unique_id = str(uuid.uuid4())[:5]
            file_path = f"{unique_id}_{username}_attendance.csv"

            with open(file_path, "wb") as f:
                f.write(res.content)

            with open(file_path, "rb") as f:
                await update.message.reply_document(document=f)
        else:
            await update.message.reply_text(f"❌ Failed to export logs: {res.json()}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    """Simple synchronous main function"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("log", log))
    app.add_handler(CommandHandler("ulog", ulog))
    app.add_handler(CommandHandler("export", export_handler))
    app.add_handler(CommandHandler("register", register))

    print("🤖 Bot is running...")

    # Run the bot - this will handle the event loop internally
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖 Bot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
