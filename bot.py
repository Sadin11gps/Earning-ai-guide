# -*- coding: utf-8 -*-
from flask import Flask, request, abort
import telebot
from telebot import types
import sqlite3
import random
import string
from pyTelegramBotCAPTCHA import CaptchaManager
from datetime import datetime
import os

# --- কনফিগারেশন ---
API_TOKEN = os.getenv('BOT_TOKEN', '8059084521:AAGuVxr-6-X0Izld_uOD4nazPqd3yaKQgzo')
ADMIN_IDS = [7702378694, 7475964655]  # দুইজন অ্যাডমিন
ADMIN_PASSWORD = "Rdsvai11"

bot = telebot.TeleBot(API_TOKEN)
captcha_manager = CaptchaManager(API_TOKEN)

app = Flask(__name__)

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
        'admin_send': "📩 Enter User ID to send message:",
        'admin_send_msg': "Enter message for the user:",
        'broadcast_success': "✅ Broadcast sent to {} users!",
        'send_success': "✅ Message sent to user!",
        'user_not_found': "❌ User not found.",
        'user_list_header': "👥 <b>All Users List:</b>\n\n",
        'user_list_format': "🆔 <b>ID:</b> <code>{}</code>\n👤 <b>Name:</b> {} {}\n💰 <b>Balance:</b> \( {:.4f}\n👥 <b>Referrals:</b> {}\n📤 <b>Paid Withdraw:</b> \){:.4f}\n\n",
        'no_users': "📭 No users yet.",
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
        'admin_send': "📩 ইউজার আইডি দিন:",
        'admin_send_msg': "ইউজারের জন্য মেসেজ লিখুন:",
        'broadcast_success': "✅ {} জন ইউজারকে ব্রডকাস্ট পাঠানো হয়েছে!",
        'send_success': "✅ মেসেজ পাঠানো হয়েছে!",
        'user_not_found': "❌ ইউজার পাওয়া যায়নি।",
        'user_list_header': "👥 <b>সব ইউজারের লিস্ট:</b>\n\n",
        'user_list_format': "🆔 <b>ID:</b> <code>{}</code>\n👤 <b>নাম:</b> {} {}\n💰 <b>ব্যালেন্স:</b> \( {:.4f}\n👥 <b>রেফারেল:</b> {}\n📤 <b>পেইড উইথড্র:</b> \){:.4f}\n\n",
        'no_users': "📭 এখনো কোনো ইউজার নেই।",
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
                       pending_task TEXT, language TEXT DEFAULT 'en')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS task_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                       details TEXT, status TEXT, date TEXT, amount REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS withdraw_history 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                       amount REAL, method TEXT, address TEXT, date TEXT, status TEXT DEFAULT 'Pending')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings 
                      (key TEXT PRIMARY KEY, value REAL)''')
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('task_price', 0.1500)")
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN ref_count INTEGER DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN total_ref_earn REAL DEFAULT 0.0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE withdraw_history ADD COLUMN status TEXT DEFAULT 'Pending'")
    except:
        pass 
        
    conn.commit()
    conn.close()

init_db()

# --- জেনারেটর ফাংশন ---
def generate_full_creds():
    first_names = ["Brian", "James", "Robert", "John", "Michael", "William", "David", "Richard", "Joseph", "Thomas"]
    last_names = ["Holloway", "Rasmussen", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    chars = string.ascii_lowercase + string.digits
    password = ''.join(random.choice(chars + string.ascii_uppercase) for _ in range(10))
    email_prefix = ''.join(random.choice(chars) for _ in range(8))
    recovery_prefix = ''.join(random.choice(chars) for _ in range(10))
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    email = f"{email_prefix}{random.choice(chars)}@gmail.com"
    recovery = f"{recovery_prefix}@hotmail.com"
    return f_name, l_name, password, email, recovery

# --- কিবোর্ডস ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('💰 Balance', '📋 Tasks')
    markup.add('📤 Withdraw', '👤 Profile')
    markup.add('📋 History', '🤔 FAQ')
    markup.add('👥 My Referrals', '🌍 Language')
    return markup

def admin_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📝 Task History', '💸 Withdraw History')
    markup.add('💰 Manage Balance', '⚙️ Set Task Price')
    markup.add('📢 Broadcast', '📩 Send Message')
    markup.add('👥 User List', '🏠 Exit Admin')
    return markup

def language_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🇺🇸 English', '🇧🇩 বাংলা')
    markup.add('🔙 Back')
    return markup

def get_task_price():
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    try:
        price = conn.execute("SELECT value FROM settings WHERE key='task_price'").fetchone()[0]
    except:
        price = 0.1500
    conn.close()
    return price

def is_menu_button(text):
    buttons = ['💰 Balance', '📋 Tasks', '📤 Withdraw', '👤 Profile', '📋 History', '🤔 FAQ', '👥 My Referrals', '🌍 Language', '❌ Cancel', '🏠 Exit Admin', 'TRX', '✅ Account registered', '▶️ Start', '🔙 Back', '🇺🇸 English', '🇧🇩 বাংলা', '📢 Broadcast', '📩 Send Message', '📝 Task History', '💸 Withdraw History', '💰 Manage Balance', '⚙️ Set Task Price', '👥 User List']
    return text in buttons

# --- হেল্পার ফাংশন ---
def get_user_lang(user_id):
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else 'en'

# --- /start (CAPTCHA দিয়ে শুরু) ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    captcha_manager.send_new_captcha(bot, message.chat.id, message.from_user)

# --- ল্যাঙ্গুয়েজ চেঞ্জ ---
@bot.message_handler(func=lambda m: m.text in ['🇺🇸 English', '🇧🇩 বাংলা'])
def change_language(message):
    user_id = message.from_user.id
    new_lang = 'en' if message.text == '🇺🇸 English' else 'bn'
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    conn.execute("UPDATE users SET language=? WHERE id=?", (new_lang, user_id))
    conn.commit()
    conn.close()
    texts = LANGUAGES[new_lang]
    bot.send_message(user_id, texts['lang_set'], reply_markup=main_menu())

# --- Language বাটন ---
@bot.message_handler(func=lambda m: m.text == '🌍 Language')
def language_handler(message):
    lang = get_user_lang(message.from_user.idAAG5z--eYoWDpek1XeoY3eyXtdlsOhI0Et4't.send_message(message.from_user.id, texts['language'], reply_markup=language_menu())

# --- অ্যাডমিন লগইন ---
@bot.message_handler(commands=['admin'])
def admin_login(message):
    if message.from_user.id in ADMIN_IDS:
        msg = bot.send_message(message.chat.id, "🔐 Enter Admin Password:")
        bot.register_next_step_handler(msg, verify_admin)
    else:
        bot.send_message(message.chat.id, "❌ You are not authorized.")

def verify_admin(message):
    if message.text == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "✅ Admin Panel Unlocked.", reply_markup=admin_menu())
    else:
        bot.send_message(message.chat.id, "❌ Wrong Password.")

# --- অ্যাডমিনে Broadcast ---
@bot.message_handler(func=lambda m: m.text == '📢 Broadcast' and m.from_user.id in ADMIN_IDS)
def admin_broadcast(message):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    msg = bot.send_message(message.chat.id, texts['admin_broadcast'])
    bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(message):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    if message.text == '🏠 Exit Admin':
        bot.send_message(message.chat.id, "Exited admin panel.", reply_markup=main_menu())
        return

    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    conn.close()

    sent_count = 0
    for user in users:
        try:
            bot.send_message(user[0], message.text)
            sent_count += 1
        except:
            pass

    bot.send_message(message.chat.id, texts['broadcast_success'].format(sent_count), reply_markup=admin_menu())

# --- অ্যাডমিনে Send Message ---
@bot.message_handler(func=lambda m: m.text == '📩 Send Message' and m.from_user.id in ADMIN_IDS)
def admin_send(message):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    msg = bot.send_message(message.chat.id, texts['admin_send'])
    bot.register_next_step_handler(msg, admin_send_user_id)

def admin_send_user_id(message):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    if message.text == '🏠 Exit Admin':
        bot.send_message(message.chat.id, "Exited admin panel.", reply_markup=main_menu())
        return

    try:
        target_id = int(message.text)
        msg = bot.send_message(message.chat.id, texts['admin_send_msg'])
        bot.register_next_step_handler(msg, lambda m: admin_send_final(m, target_id))
    except:
        bot.send_message(message.chat.id, "❌ Invalid User ID.", reply_markup=admin_menu())

def admin_send_final(message, target_id):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    if message.text == '🏠 Exit Admin':
        bot.send_message(message.chat.id, "Exited admin panel.", reply_markup=main_menu())
        return

    try:
        bot.send_message(target_id, message.text)
        bot.send_message(message.chat.id, texts['send_success'], reply_markup=admin_menu())
    except:
        bot.send_message(message.chat.id, texts['user_not_found'], reply_markup=admin_menu())

# --- User List বাটন ---
@bot.message_handler(func=lambda m: m.text == '👥 User List' and m.from_user.id in ADMIN_IDS)
def admin_user_list(message):
    admin_lang = get_user_lang(message.from_user.id)
    texts = LANGUAGES[admin_lang]
    
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, username, balance, ref_count FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        bot.send_message(message.chat.id, texts['no_users'])
        return
    
    text = texts['user_list_header']
    for user in rows:
        u_id, f_name, u_name, bal, ref_count = user
        username_str = f"@{u_name}" if u_name else "N/A"
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        wd_total = conn.execute("SELECT SUM(amount) FROM withdraw_history WHERE user_id=? AND status='Paid'", (u_id,)).fetchone()[0] or 0.0
        conn.close()
        text += texts['user_list_format'].format(u_id, f_name, username_str, bal, ref_count, wd_total)
    
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=admin_menu())

# --- মেইন হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    user_id = message.from_user.id
    text = message.text

    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]

    if text in ['❌ Cancel', '🏠 Exit Admin', '🔙 Back']:
        bot.send_message(user_id, "🏠 Home.", reply_markup=main_menu())
        return

    if text == '👤 Profile':
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        bal = conn.execute("SELECT balance FROM users WHERE id=?", (user_id,)).fetchone()[0]
        wd_res = conn.execute("SELECT SUM(amount) FROM withdraw_history WHERE user_id=? AND status='Paid'", (user_id,)).fetchone()[0]
        wd_total = wd_res if wd_res else 0.0
        conn.close()
        profile_msg = texts['profile'].format(message.from_user.first_name, bal, wd_total)
        bot.send_message(user_id, profile_msg, parse_mode="HTML")
        return

    elif text == '🤔 FAQ':
        faq_msg = "🤔 <b>View help at:</b>\n📄 https://telegra.ph/FAQ----CRAZY-MONEY-BUX-12-25-2"
        bot.send_message(user_id, faq_msg, parse_mode="HTML")
        return

    elif text == '📋 History':
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        rows = conn.execute("SELECT details, status FROM task_history WHERE user_id=? ORDER BY id DESC LIMIT 15", (user_id,)).fetchall()
        conn.close()
        if not rows:
            bot.send_message(user_id, texts['history_empty'])
            return
        history_txt = texts['history_header']
        for r in rows:
            details, status = r
            try:
                gmail = details.split('|')[2].split(': ')[1]
                stat_emoji = "✅" if status == "Approved" else "❌" if status == "Rejected" else "⏳"
                history_txt += f"📧 {gmail}\n📊 Status: {status} {stat_emoji}\n\n"
            except:
                continue
        bot.send_message(user_id, history_txt, parse_mode="HTML")
        return

    elif text == '💰 Balance':
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        bal = conn.execute("SELECT balance FROM users WHERE id=?", (user_id,)).fetchone()[0]
        conn.close()
        bot.send_message(user_id, texts['balance'].format(bal))
        return

    elif text == '📋 Tasks':
        p = get_task_price()
        m = types.ReplyKeyboardMarkup(resize_keyboard=True).row(f'📱 G account (FAST CHECK) (${p:.4f})').row('❌ Cancel')
        bot.send_message(user_id, texts['tasks'], reply_markup=m)
        return

    elif '📱 G account' in text:
        m = types.ReplyKeyboardMarkup(resize_keyboard=True).add('▶️ Start').add('❌ Cancel')
        bot.send_message(user_id, texts['task_desc'], reply_markup=m)
        return

    elif text == '▶️ Start':
        fn, ln, p, e, rec = generate_full_creds()
        pending_data = f"FN: {fn}|LN: {ln}|E: {e}|P: {p}|REC: {rec}"
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        conn.execute("UPDATE users SET pending_task=? WHERE id=?", (pending_data, user_id))
        conn.commit()
        conn.close()
        main_msg = f"First name: <code>{fn}</code>\nLast name: <code>{ln}</code>\nPassword: <code>{p}</code>\nEmail: <code>{e}</code>\nRecovery email: <code>{rec}</code>\n\n⚠️ IMPORTANT: MANDATORY add this recovery email to account settings after registration!"
        bot.send_message(user_id, main_msg, parse_mode="HTML")
        m = types.ReplyKeyboardMarkup(resize_keyboard=True).add('✅ Account registered').add('❌ Cancel')
        bot.send_message(user_id, texts['start_task'], reply_markup=m)
        return

    elif text == '✅ Account registered':
        price = get_task_price()
        fn_user = message.from_user.first_name
        u_name = f"@{message.from_user.username}" if message.from_user.username else "N/A"
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        cursor = conn.cursor()
        res = cursor.execute("SELECT pending_task FROM users WHERE id=?", (user_id,)).fetchone()
        if res and res[0]:
            creds = res[0]
            parts = creds.split('|')
            gmail = parts[2].split(': ')[1]
            password = parts[3].split(': ')[1]
            recovery = parts[4].split(': ')[1]
            date_n = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO task_history (user_id, details, status, date, amount) VALUES (?, ?, 'Pending', ?, ?)", (user_id, creds, date_n, price))
            tid = cursor.lastrowid

            cursor.execute("UPDATE users SET pending_task = NULL WHERE id=?", (user_id,))
            
            conn.commit()
            conn.close()

            bot.send_message(user_id, texts['submitted'], reply_markup=main_menu())

            admin_msg = f"🔔 <b>New Task Submission</b>\n\n👤 <b>User ID:</b> <code>{user_id}</code>\n👤 <b>Name:</b> {fn_user}\n👤 <b>Username:</b> {u_name}\n\n      🔰<b>Task Information</b>🔰\n\n📧 <b>Gmail:</b> <code>{gmail}</code>\n🔑 <b>Pass:</b> <code>{password}</code>\n🔄 <b>Recovery:</b> <code>{recovery}</code>"
            adm_m = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Approve", callback_data=f"app_{user_id}_{tid}"), types.InlineKeyboardButton("Reject", callback_data=f"rej_{user_id}_{tid}"))
            for admin_id in ADMIN_IDS:
                try:
                    bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=adm_m)
                except:
                    pass
        else:
            bot.send_message(user_id, "❌ No pending task found.")
        return

    elif text == '👥 My Referrals':
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        res = conn.execute("SELECT ref_count, total_ref_earn FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        ref_count = res[0] if res else 0
        ref_earn = res[1] if res else 0.0
        r_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(user_id, texts['referrals'].format(ref_count, ref_earn, r_link))
        return

    elif text == '📤 Withdraw':
        m = types.ReplyKeyboardMarkup(resize_keyboard=True).add('TRX').add('❌ Cancel')
        bot.send_message(user_id, texts['withdraw'], reply_markup=m)
        return

    elif text == 'TRX':
        msg = bot.send_message(user_id, texts['enter_amount'])
        bot.register_next_step_handler(msg, process_withdraw_amount)
        return

    elif user_id in ADMIN_IDS:
        if text == '📝 Task History':
            conn = sqlite3.connect('socialbux.db', check_same_thread=False)
            query = "SELECT task_history.id, task_history.user_id, task_history.details, users.first_name, users.username FROM task_history JOIN users ON task_history.user_id = users.id WHERE task_history.status = 'Pending' LIMIT 10"
            rows = conn.execute(query).fetchall()
            conn.close()
            if not rows:
                bot.send_message(user_id, texts['no_pending_tasks'])
                return
            for r in rows:
                try:
                    tid, uid, details, name, uname = r
                    parts = details.split('|')
                    gmail = parts[2].split(': ')[1]
                    password = parts[3].split(': ')[1]
                    recovery = parts[4].split(': ')[1]
                    hist_msg = f"🔔 <b>New Task Submission</b>\n\n👤 <b>User ID:</b> <code>{uid}</code>\n👤 <b>Name:</b> {name}\n\n      🔰<b>Task Information</b>🔰\n\n📧 <b>Gmail:</b> <code>{gmail}</code>\n🔑 <b>Pass:</b> <code>{password}</code>\n🔄 <b>Recovery:</b> <code>{recovery}</code>"
                    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Approve", callback_data=f"app_{uid}_{tid}"), types.InlineKeyboardButton("Reject", callback_data=f"rej_{uid}_{tid}"))
                    bot.send_message(user_id, hist_msg, parse_mode="HTML", reply_markup=markup)
                except:
                    continue
            return
        
        elif text == '💸 Withdraw History':
            conn = sqlite3.connect('socialbux.db', check_same_thread=False)
            query = "SELECT w.id, w.user_id, w.amount, w.address, u.username, u.first_name FROM withdraw_history w JOIN users u ON w.user_id = u.id WHERE w.status = 'Pending'"
            rows = conn.execute(query).fetchall()
            conn.close()
            
            if not rows:
                bot.send_message(user_id, texts['no_pending_withdraw'])
                return

            for row in rows:
                wid, uid, amount, address, username, firstname = row
                uname = f"@{username}" if username else "N/A"
                
                msg_text = f"💸 <b>Withdraw Request</b>\n\n👤 <b>User:</b> {firstname} ({uname})\n🆔 <b>ID:</b> <code>{uid}</code>\n💰 <b>Amount:</b> ${amount}\n🏦 <b>Method:</b> TRX\n📫 <b>Address:</b> <code>{address}</code>"
                
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"wapp_{uid}_{wid}"),
                           types.InlineKeyboardButton("❌ Reject", callback_data=f"wrej_{uid}_{wid}"))
                bot.send_message(user_id, msg_text, parse_mode="HTML", reply_markup=markup)
            return

        elif text == '⚙️ Set Task Price':
            msg = bot.send_message(user_id, "🔢 Enter new task price (e.g., 0.15):")
            bot.register_next_step_handler(msg, admin_set_price_step)
            return

        elif text == '💰 Manage Balance':
            msg = bot.send_message(user_id, "Enter User ID:")
            bot.register_next_step_handler(msg, admin_balance_id_step)
            return

# --- সাব ফাংশনসমূহ ---
def process_withdraw_amount(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]
    if is_menu_button(message.text):
        handle_all(message)
        return
    try:
        amount = float(message.text)
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        bal = conn.execute("SELECT balance FROM users WHERE id=?", (user_id,)).fetchone()[0]
        conn.close()
        if bal < amount:
            bot.send_message(user_id, texts['insufficient'])
            return
        msg = bot.send_message(user_id, texts['enter_address'])
        bot.register_next_step_handler(msg, lambda m: process_withdraw_address(m, amount))
    except:
        bot.send_message(user_id, "⚠️ Invalid amount.")

def process_withdraw_address(message, amount):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = LANGUAGES[lang]
    if is_menu_button(message.text):
        handle_all(message)
        return
    address = message.text
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect('socialbux.db', check_same_thread=False)
    conn.execute("UPDATE users SET balance = balance - ? WHERE id=?", (amount, user_id))
    conn.execute("INSERT INTO withdraw_history (user_id, amount, method, address, date, status) VALUES (?, ?, 'TRX', ?, ?, 'Pending')", (user_id, amount, address, date_now))
    conn.commit()
    conn.close()
    
    try:
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, f"🔔 New Withdraw Request from ID: {user_id}\nAmount: ${amount}")
    except:
        pass
    
    bot.send_message(user_id, texts['withdrawn'], reply_markup=main_menu())

def admin_balance_id_step(message):
    t_id = message.text
    msg = bot.send_message(message.chat.id, "Enter Amount:")
    bot.register_next_step_handler(msg, lambda m: admin_balance_save_step(m, t_id))

def admin_balance_save_step(message, t_id):
    try:
        amt = float(message.text)
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        conn.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amt, t_id))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "✅ Success.")
    except:
        bot.send_message(message.chat.id, "Error.")

def admin_set_price_step(message):
    try:
        new_price = float(message.text)
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('task_price', ?)", (new_price,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"✅ Task price updated to ${new_price:.4f}", reply_markup=admin_menu())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid number. Please enter a valid amount.", reply_markup=admin_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    captcha = captcha_manager.update_captcha(bot, call)
    if captcha:
        if captcha.solved:
            user_id = call.from_user.id
            lang = get_user_lang(user_id)
            texts = LANGUAGES[lang]
            conn = sqlite3.connect('socialbux.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (id, first_name, username, language) VALUES (?, ?, ?, ?)", 
                               (user_id, call.from_user.first_name, call.from_user.username, 'en'))
                conn.commit()
            conn.close()
            bot.send_message(user_id, texts['welcome'], reply_markup=main_menu())
            captcha_manager.delete_captcha(bot, captcha)
        else:
            bot.answer_callback_query(call.id, "Wrong! Try again.", show_alert=True)
        return

    try:
        data = call.data.split('_')
        act, uid, tid = data[0], int(data[1]), int(data[2])
        conn = sqlite3.connect('socialbux.db', check_same_thread=False)
        cursor = conn.cursor()
        
        if act == 'app':
            cursor.execute("SELECT amount FROM task_history WHERE id=?", (tid,))
            res = cursor.fetchone()
            if res:
                amt = res[0]
                cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amt, uid))
                cursor.execute("UPDATE task_history SET status='Approved' WHERE id=?", (tid,))
                cursor.execute("SELECT referred_by FROM users WHERE id=?", (uid,))
                ref_row = cursor.fetchone()
                if ref_row and ref_row[0]:
                    ref = ref_row[0]
                    cursor.execute("UPDATE users SET balance = balance + ?, total_ref_earn = total_ref_earn + ? WHERE id=?", (amt*0.2, amt*0.2, ref))
                conn.commit()
                bot.send_message(uid, f"✅ Task Approved! ${amt} added.")
                bot.edit_message_text(f"✅ Approved Task for User {uid}", call.message.chat.id, call.message.message_id)
        
        elif act == 'rej':
            cursor.execute("UPDATE task_history SET status='Rejected' WHERE id=?", (tid,))
            conn.commit()
            bot.send_message(uid, "❌ Task Rejected.")
            bot.edit_message_text(f"❌ Rejected Task for User {uid}", call.message.chat.id, call.message.message_id)

        elif act == 'wapp':
            cursor.execute("UPDATE withdraw_history SET status='Paid' WHERE id=?", (tid,))
            conn.commit()
            bot.send_message(uid, "✅ Your withdrawal has been paid!")
            bot.edit_message_text(f"✅ Withdraw Paid for User {uid}", call.message.chat.id, call.message.message_id)
        
        elif act == 'wrej':
            cursor.execute("SELECT amount FROM withdraw_history WHERE id=?", (tid,))
            row = cursor.fetchone()
            if row:
                amt = row[0]
                cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amt, uid))
                cursor.execute("UPDATE withdraw_history SET status='Rejected' WHERE id=?", (tid,))
                conn.commit()
                bot.send_message(uid, f"❌ Withdrawal Rejected. ${amt} refunded to balance.")
                bot.edit_message_text(f"❌ Withdraw Rejected for User {uid}", call.message.chat.id, call.message.message_id)

        conn.close()
    except Exception as e:
        print("Error in callback:", e)

print("🤖 Gmail Factory Bot is Running - Final Version with CAPTCHA!")

# --- Webhook routes ---
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
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
