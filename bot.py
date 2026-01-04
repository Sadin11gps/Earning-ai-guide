# -*- coding: utf-8 -*-
from flask import Flask, request, abort
import telebot
from telebot import types
import sqlite3
import random
import string
from datetime import datetime
import time
import os

# --- কনফিগারেশন ---
API_TOKEN = os.getenv('BOT_TOKEN', '8059084521:AAGuVxr-6-X0Izld_uOD4nazPqd3yaKQgzo')
ADMIN_IDS = [7702378694, 7475964655]  # দুইজন অ্যাডমিন
ADMIN_PASSWORD = "Rdsvai11"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- CAPTCHA / Anti-Spam RAM ---
pending_captcha = {}       # user_id -> {"answer": int, "expire": timestamp}
verified_users = set()     # user_id who passed captcha

# --- ল্যাঙ্গুয়েজ ডিকশনারি ---
LANGUAGES = {
    'en': {
        'welcome': "👋 Welcome!\n\nℹ️ This bot helps you earn money by doing simple tasks.\n\nBy using this Bot, you automatically agree to the Terms of Use.👉 https://telegra.ph/FAQ----CRAZY-MONEY-BUX-12-25-2",
        'balance': "💰 Your balance: ${:.4f}",
        'tasks': "👇 Please select a task:",
        'task_desc': "⏳ Review time: 74 min ⏳\n\n📋 Task: 📱 G account (FAST CHECK)\n\n📄 Description: 🔐 MANDATORY!\nYou must use only the email and password provided by the Telegram bot to register.",
        'start_task': "👉 Press the button to confirm registration or cancel the task:",
        'submitted': "✅ Submitted for review!",
        'referrals': "👥 Referrals: {}\n💰 Earned: ${:.4f}\n🔗 Link: {}",
        'withdraw': "📤 Choose method:",
        'insufficient': "❌ Insufficient balance!",
        'enter_amount': "🔢 Min $1.50\n📤 Enter Amount:",
        'enter_address': "📤 Enter TRX Address:",
        'withdrawn': "✅ Withdrawal submitted!",
        'profile': "👤 <b>{}</b>\n\n💰 <b>Total Balance:</b> \( {:.4f}\n📤 <b>Total Withdraw:</b> \){:.4f}\n🔒 <b>Account:</b> Active✅",
        'history_empty': "📭 You haven't completed any tasks yet.",
        'history_header': "📋 <b>Your Task History:</b>\n\n",
        'language': "🌍 Choose language:",
        'lang_set': "✅ Language set to English!",
        'no_pending_tasks': "📭 No pending tasks.",
        'no_pending_withdraw': "📭 No pending withdrawals.",
        'admin_broadcast': "📢 Enter message to broadcast to all users:",
        'admin_send': "Enter User ID to send message:",
        'admin_send_msg': "Enter message for the user:",
        'broadcast_success': "✅ Broadcast sent to {} users!",
        'send_success': "✅ Message sent to user!",
        'user_not_found': "❌ User not found.",
        'user_list_header': "👥 <b>All Users List:</b>\n\n",
        'user_list_format': "🆔 <b>ID:</b> <code>{}</code>\n👤 <b>Name:</b> {} {}\n💰 <b>Balance:</b> \( {:.4f}\n👥 <b>Referrals:</b> {}\n📤 <b>Paid Withdraw:</b> \){:.4f}\n\n",
        'no_users': "📭 No users yet.",
        'captcha_prompt': "🧮 Solve this to continue:\n{} = ?\n⏱ You have 120 seconds.",
        'captcha_success': "✅ Verification successful!",
        'captcha_fail': "❌ Wrong answer, try again ({}/3)",
        'captcha_block': "⛔ Too many wrong answers! Blocked for 5 minutes.",
        'captcha_timeout': "⛔ Time expired. Send /start again.",
        'captcha_block_msg': "⛔ Blocked due to multiple wrong attempts.\n⏱ Try again in {} seconds."
    },
    'bn': {
        'welcome': "👋 স্বাগতম!\n\nℹ️ এই বটে সিম্পল টাস্ক করে ডলার আর্ন করুন।\n\nবট ব্যবহার করে আপনি অটোম্যাটিক টার্মস অ্যাগ্রি করছেন।👉 https://telegra.ph/FAQ----CRAZY-MONEY-BUX-12-25-2",
        'balance': "💰 আপনার ব্যালেন্স: ${:.4f}",
        'tasks': "👇 একটা টাস্ক সিলেক্ট করুন:",
        'task_desc': "⏳ রিভিউ টাইম: ৭৪ মিনিট ⏳\n\n📋 টাস্ক: 📱 G account (FAST CHECK)\n\n📄 বর্ণনা: 🔐 অবশ্যই বট দেওয়া ইমেইল ও পাসওয়ার্ড দিয়ে রেজিস্টার করতে হবে।",
        'start_task': "👉 রেজিস্ট্রেশন কনফার্ম করুন বা ক্যানসেল করুন:",
        'submitted': "✅ রিভিউয়ের জন্য সাবমিট করা হয়েছে!",
        'referrals': "👥 রেফারেল: {}\n💰 আর্ন: ${:.4f}\n🔗 লিঙ্ক: {}",
        'withdraw': "📤 পেমেন্ট মেথড সিলেক্ট করুন:",
        'insufficient': "❌ ব্যালেন্স যথেষ্ট নয়!",
        'enter_amount': "🔢 মিনিমাম $1.50\n📤 অ্যামাউন্ট দিন:",
        'enter_address': "📤 TRX অ্যাড্রেস দিন:",
        'withdrawn': "✅ উইথড্র রিকোয়েস্ট করা হয়েছে!",
        'profile': "👤 <b>{}</b>\n\n💰 <b>টোটাল ব্যালেন্স:</b> \( {:.4f}\n📤 <b>টোটাল উইথড্র:</b> \){:.4f}\n🔒 <b>অ্যাকাউন্ট:</b> অ্যাকটিভ✅",
        'history_empty': "📭 আপনি এখনো কোনো টাস্ক করেননি।",
        'history_header': "📋 <b>আপনার টাস্ক হিস্ট্রি:</b>\n\n",
        'language': "🌍 ভাষা সিলেক্ট করুন:",
        'lang_set': "✅ ভাষা বাংলায় সেট করা হয়েছে!",
        'no_pending_tasks': "📭 কোনো পেন্ডিং টাস্ক নেই।",
        'no_pending_withdraw': "📭 কোনো পেন্ডিং উইথড্র নেই।",
        'admin_broadcast': "📢 সবাইকে মেসেজ পাঠানোর জন্য মেসেজ লিখুন:",
        'admin_send': "ইউজার আইডি দিন:",
        'admin_send_msg': "ইউজারের জন্য মেসেজ লিখুন:",
        'broadcast_success': "✅ {} জন ইউজারকে ব্রডকাস্ট পাঠানো হয়েছে!",
        'send_success': "✅ মেসেজ পাঠানো হয়েছে!",
        'user_not_found': "❌ ইউজার পাওয়া যায়নি।",
        'user_list_header': "👥 <b>সব ইউজারের লিস্ট:</b>\n\n",
        'user_list_format': "🆔 <b>ID:</b> <code>{}</code>\n👤 <b>নাম:</b> {} {}\n💰 <b>ব্যালেন্স:</b> \( {:.4f}\n👥 <b>রেফারেল:</b> {}\n📤 <b>পেইড উইথড্র:</b> \){:.4f}\n\n",
        'no_users': "📭 এখনো কোনো ইউজার নেই।",
        'captcha_prompt': "🧮 যাচাই করার জন্য সমাধান করুন:\n{} = ?\n⏱ আপনার কাছে 120 সেকেন্ড আছে।",
        'captcha_success': "✅ যাচাইকরণ সফল!",
        'captcha_fail': "❌ ভুল উত্তর, আবার চেষ্টা করো ({}/3)",
        'captcha_block': "⛔ অনেক ভুল উত্তর! ৫ মিনিটের জন্য block করা হয়েছে।",
        'captcha_timeout': "⛔ সময় শেষ। আবার /start দিন।",
        'captcha_block_msg': "⛔ অনেক ভুল উত্তর।\n⏱ {} সেকেন্ড পরে আবার চেষ্টা করুন।"
    }
}

# --- ডাটাবেস সেটআপ ---
def init_db():
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, 
                       balance REAL DEFAULT 0.0, referred_by INTEGER, 
                       ref_count INTEGER DEFAULT 0, total_ref_earn REAL DEFAULT 0.0,
                       pending_task TEXT, language TEXT DEFAULT 'en',
                       captcha_tries INTEGER DEFAULT 0, captcha_block_until REAL DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS task_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                       details TEXT, status TEXT, date TEXT, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS withdraw_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                       amount REAL, method TEXT, address TEXT, date TEXT, status TEXT DEFAULT 'Pending')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings 
                      (key TEXT PRIMARY KEY, value REAL)''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('task_price', 0.1500)")
    conn.commit()
    conn.close()

init_db()

# --- CAPTCHA Generator ---
def generate_math_captcha(user_id):
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(['+', '-', '*'])
    question = f"{a} {op} {b}"
    answer = eval(question)
    expire = time.time() + 120  # 120 seconds
    return question, answer, expire

# --- Helper Functions ---
def get_user_lang(user_id):
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 'en'

def start_cmd(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]
    bot.send_message(user_id, texts['welcome'])

# --- /start with CAPTCHA ---
@bot.message_handler(commands=['start'])
def start_captcha(message):
    user_id = message.from_user.id
    now = time.time()
    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]

    if user_id in ADMIN_IDS:
        start_cmd(message)
        return

    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    row = cursor.execute("SELECT captcha_tries, captcha_block_until FROM users WHERE id=?", (user_id,)).fetchone()
    tries, block_until = row if row else (0, 0)

    if block_until and now < block_until:
        remaining = int(block_until - now)
        bot.send_message(user_id, texts['captcha_block_msg'].format(remaining))
        conn.close()
        return

    q, ans, exp = generate_math_captcha(user_id)
    pending_captcha[user_id] = {"answer": ans, "expire": exp}
    bot.send_message(user_id, texts['captcha_prompt'].format(q))
    conn.close()

# --- CAPTCHA Answer Handler ---
@bot.message_handler(func=lambda m: m.from_user.id in pending_captcha)
def handle_captcha(message):
    user_id = message.from_user.id
    now = time.time()
    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]
    data = pending_captcha.get(user_id)

    if not data:
        return

    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    row = cursor.execute("SELECT captcha_tries, captcha_block_until FROM users WHERE id=?", (user_id,)).fetchone()
    tries, block_until = row if row else (0, 0)

    if now > data["expire"]:
        del pending_captcha[user_id]
        bot.send_message(user_id, texts['captcha_timeout'])
        conn.close()
        return

    if message.text.isdigit() and int(message.text) == data["answer"]:
        verified_users.add(user_id)
        del pending_captcha[user_id]
        cursor.execute("UPDATE users SET captcha_tries=0, captcha_block_until=0 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(user_id, texts['captcha_success'])
        start_cmd(message)
    else:
        tries += 1
        if tries >= 3:
            block_until = now + 300
            cursor.execute("UPDATE users SET captcha_tries=?, captcha_block_until=? WHERE id=?", (tries, block_until, user_id))
            del pending_captcha[user_id]
            bot.send_message(user_id, texts['captcha_block'])
        else:
            cursor.execute("UPDATE users SET captcha_tries=? WHERE id=?", (tries, user_id))
            bot.send_message(user_id, texts['captcha_fail'].format(tries))
        conn.commit()
        conn.close()

# --- Webhook Routes ---
@app.route('/' + API_TOKEN, methods=['POST'])
def get_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        abort(403)

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == '__main__':
    print("🤖 Gmail Factory Bot with CAPTCHA & Anti-Spam Running!")
    app.run(host='0.0.0.0', AAG5z--eYoWDpek1XeoY3eyXtdlsOhI0Et4'4'4'
