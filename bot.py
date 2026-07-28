#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import requests
import time

from flask import Flask, request, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import logging

# ============================================================
# 🤖 بوت استضافة PHP - النسخة المتكاملة (Python)
# 📌 يعمل عبر Webhook على استضافتك (Flask)
# 👤 المطور: @I_Z_E_E
# 🔗 رابط المشروع: https://replit.com/@geniralbrahim15/Bot-PHP
# ============================================================

# 🔧 الإعدادات (عدّل هذه القيم)
BOT_TOKEN = "8854697245:AAEe-IOvigi_9h_fzxxXihmlMi76WTcVfj8"  # ضع توكن بوتك هنا
ADMIN_ID = 7757241009  # ضع معرفك الرقمي هنا
BASE_URL = "https://attached-assets--Brhim.repl.co"  # ضع رابط مشروعك بدون / في النهاية
UPLOAD_DIR = "bots/"  # مجلد حفظ البوتات المرفوعة
# ============================================================

# إنشاء مجلد الرفع إذا لم يكن موجوداً
os.makedirs(UPLOAD_DIR, exist_ok=True)

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# ============================================================
# 📦 دوال مساعدة
# ============================================================

def extract_token(file_path):
    """استخراج التوكن من ملف PHP"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'(\d+:[A-Za-z0-9_-]+)', content)
        return match.group(1) if match else None
    except:
        return None

def bot_api(token, method, data=None):
    """إرسال طلب إلى API تيليجرام"""
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        if data:
            resp = requests.post(url, data=data, timeout=10)
        else:
            resp = requests.get(url, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
        return None

def set_webhook(token, url):
    """تعيين Webhook لبوت"""
    result = bot_api(token, 'setWebhook', {'url': url})
    return result if result and result.get('ok') else None

def delete_webhook(token):
    """حذف Webhook"""
    result = bot_api(token, 'deleteWebhook')
    return result if result and result.get('ok') else None

def get_webhook_info(token):
    """جلب معلومات Webhook"""
    result = bot_api(token, 'getWebhookInfo')
    return result if result and result.get('ok') else None

def get_base_url():
    return BASE_URL.rstrip('/')

def get_bot_url(folder_name):
    return f"{get_base_url()}/{UPLOAD_DIR}{folder_name}/bot.php"

def get_bots_list():
    """جلب قائمة البوتات المرفوعة"""
    bots = []
    if os.path.isdir(UPLOAD_DIR):
        for folder in os.listdir(UPLOAD_DIR):
            folder_path = os.path.join(UPLOAD_DIR, folder)
            if os.path.isdir(folder_path):
                file_path = os.path.join(folder_path, 'bot.php')
                if os.path.isfile(file_path):
                    bots.append({
                        'id': folder,
                        'url': get_bot_url(folder),
                        'token': extract_token(file_path),
                        'size': os.path.getsize(file_path),
                        'time': os.path.getmtime(file_path)
                    })
    return bots

# ============================================================
# 🌐 خادم Flask للـ Webhook
# ============================================================

app = Flask(__name__)

# الصفحة الرئيسية (عند زيارة الرابط)
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>🤖 بوت استضافة PHP</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:50px;background:#0f0f1a;color:#fff;">
        <h1>🤖 بوت استضافة PHP</h1>
        <p>✅ البوت يعمل ويستقبل التحديثات عبر Webhook.</p>
        <p>📌 أرسل ملف <code>.php</code> إلى البوت لرفعه وتشغيله.</p>
        <p>👤 المطور: @I_Z_E_E</p>
        <p>🔗 رابط المشروع: <a href="https://replit.com/@geniralbrahim15/Bot-PHP" target="_blank" style="color:#00d2ff;">Bot-PHP on Replit</a></p>
    </body>
    </html>
    """
    return render_template_string(html)

# نقطة استقبال التحديثات من تيليجرام (سيتم تعيينها كـ Webhook للبوت الأساسي)
@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال التحديثات من تيليجرام ومعالجتها"""
    update_data = request.get_json()
    if not update_data:
        return 'OK', 200
    
    # معالجة التحديثات يدوياً
    process_update(update_data)
    return 'OK', 200

# ============================================================
# 📥 معالج التحديثات يدوياً (محاكاة لدوال PHP)
# ============================================================

def process_update(update_data):
    """معالجة التحديثات الواردة من تيليجرام"""
    if 'message' in update_data:
        message = update_data['message']
        chat_id = message['chat']['id']
        from_id = message['from']['id']
        text = message.get('text', '')
        document = message.get('document')
        
        # أمر /start
        if text == '/start':
            keyboard = [
                [{'text': '📤 رفع بوت', 'callback_data': 'upload'}],
                [{'text': '📋 بوتاتي', 'callback_data': 'my_bots'}],
                [{'text': 'ℹ️ تعليمات', 'callback_data': 'help'}]
            ]
            if from_id == ADMIN_ID:
                keyboard.append([{'text': '⚙️ لوحة التحكم', 'callback_data': 'admin'}])
            send_message(chat_id, 
                         "🤖 **بوت استضافة PHP**\nمرحباً! أرسل ملف `.php` لرفعه وتشغيله.\n\nاختر أحد الخيارات:",
                         reply_markup=inline_keyboard(keyboard))
        
        elif text == '/help':
            send_message(chat_id,
                         "📖 **تعليمات البوت**\n\n1️⃣ أرسل ملف `.php` وسيتم رفعه على الاستضافة.\n2️⃣ بعد الرفع، سيظهر لك رابط البوت وأزرار التحكم.\n3️⃣ يمكنك تشغيل/إيقاف/حذف البوتات المرفوعة.\n\n👤 المطور: @I_Z_E_E")
        
        elif text == '/admin' and from_id == ADMIN_ID:
            bots = get_bots_list()
            count = len(bots)
            send_message(chat_id,
                         f"⚙️ **لوحة التحكم**\n📦 عدد البوتات المرفوعة: {count}",
                         reply_markup=inline_keyboard([
                             [{'text': '📊 الإحصائيات', 'callback_data': 'stats'}],
                             [{'text': '🗑 مسح الكل', 'callback_data': 'reset'}],
                             [{'text': '🔙 رجوع', 'callback_data': 'back'}]
                         ]))
        
        # معالجة رفع الملفات
        if document and document.get('file_name', '').endswith('.php'):
            file_id = document['file_id']
            file_name = document['file_name']
            
            # تحميل الملف
            file_info = bot_api(BOT_TOKEN, 'getFile', {'file_id': file_id})
            if not file_info or not file_info.get('ok'):
                send_message(chat_id, "❌ فشل تحميل الملف.")
                return
            file_path = file_info['result']['file_path']
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            
            try:
                file_content = requests.get(file_url, timeout=20).content
            except:
                send_message(chat_id, "❌ فشل قراءة الملف.")
                return
            
            # حفظ الملف
            folder_name = f"bot_{int(time.time()*1000)}"
            folder_path = os.path.join(UPLOAD_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            file_save_path = os.path.join(folder_path, 'bot.php')
            with open(file_save_path, 'wb') as f:
                f.write(file_content)
            
            token = extract_token(file_save_path)
            bot_url = get_bot_url(folder_name)
            
            msg = "✅ **تم رفع البوت!**\n\n"
            msg += f"🔗 **الرابط:** `{bot_url}`\n"
            msg += f"📁 **المجلد:** `{folder_name}`\n"
            if token:
                msg += f"🆔 **التوكن:** `{token}`\n\n"
                msg += "اضغط على '▶️ تشغيل' لتفعيل البوت."
            else:
                msg += "⚠️ **لم يتم العثور على توكن.**\nتأكد من وجود توكن صالح في الملف."
            
            keyboard = [
                [{'text': '▶️ تشغيل', 'callback_data': f"start_{folder_name}"}],
                [{'text': '⏹ إيقاف', 'callback_data': f"stop_{folder_name}"}],
                [{'text': '🗑 حذف', 'callback_data': f"delete_{folder_name}"}],
                [{'text': '🔙 رجوع', 'callback_data': 'back'}]
            ]
            send_message(chat_id, msg, reply_markup=inline_keyboard(keyboard))
    
    elif 'callback_query' in update_data:
        callback = update_data['callback_query']
        chat_id = callback['message']['chat']['id']
        message_id = callback['message']['message_id']
        data = callback['data']
        from_id = callback['from']['id']
        
        # معالجة الأزرار (نفس المنطق السابق)
        if data == 'back':
            keyboard = [
                [{'text': '📤 رفع بوت', 'callback_data': 'upload'}],
                [{'text': '📋 بوتاتي', 'callback_data': 'my_bots'}],
                [{'text': 'ℹ️ تعليمات', 'callback_data': 'help'}]
            ]
            if from_id == ADMIN_ID:
                keyboard.append([{'text': '⚙️ لوحة التحكم', 'callback_data': 'admin'}])
            edit_message(chat_id, message_id,
                         "🤖 **بوت استضافة PHP**\nاختر أحد الخيارات:",
                         reply_markup=inline_keyboard(keyboard))
        
        elif data == 'upload':
            edit_message(chat_id, message_id,
                         "📤 أرسل ملف `.php` لرفعه.",
                         reply_markup=inline_keyboard([
                             [{'text': '🔙 رجوع', 'callback_data': 'back'}]
                         ]))
        
        elif data == 'my_bots':
            bots = get_bots_list()
            if not bots:
                edit_message(chat_id, message_id,
                             "📭 **لا توجد بوتات مرفوعة.**",
                             reply_markup=inline_keyboard([
                                 [{'text': '📤 رفع بوت', 'callback_data': 'upload'}],
                                 [{'text': '🔙 رجوع', 'callback_data': 'back'}]
                             ]))
            else:
                text = "📋 **بوتاتي المرفوعة:**\n\n"
                for bot in bots:
                    status = '🟢 يعمل'
                    if bot['token']:
                        info = get_webhook_info(bot['token'])
                        if info and info.get('ok') and info['result'].get('url'):
                            if info['result']['url'] != bot['url']:
                                status = '🔴 متوقف'
                        else:
                            status = '🔴 متوقف'
                    else:
                        status = '⚠️ بدون توكن'
                    text += f"📁 `{bot['id']}` — {status}\n"
                    text += f"🔗 `{bot['url']}`\n\n"
                keyboard = []
                for bot in bots:
                    keyboard.append([{'text': f"📁 {bot['id']}", 'callback_data': f"detail_{bot['id']}"}])
                keyboard.append([{'text': '🔙 رجوع', 'callback_data': 'back'}])
                edit_message(chat_id, message_id, text, reply_markup=inline_keyboard(keyboard))
        
        elif data == 'help':
            edit_message(chat_id, message_id,
                         "📖 **تعليمات البوت**\n\n1️⃣ أرسل ملف `.php` لرفعه.\n2️⃣ استخدم الأزرار للتحكم.\n3️⃣ يمكنك تشغيل/إيقاف/حذف البوتات.\n\n👤 المطور: @I_Z_E_E",
                         reply_markup=inline_keyboard([
                             [{'text': '🔙 رجوع', 'callback_data': 'back'}]
                         ]))
        
        elif data == 'admin' and from_id == ADMIN_ID:
            bots = get_bots_list()
            edit_message(chat_id, message_id,
                         f"⚙️ **لوحة التحكم**\n📦 عدد البوتات: {len(bots)}",
                         reply_markup=inline_keyboard([
                             [{'text': '📊 الإحصائيات', 'callback_data': 'stats'}],
                             [{'text': '🗑 مسح الكل', 'callback_data': 'reset'}],
                             [{'text': '🔙 رجوع', 'callback_data': 'back'}]
                         ]))
        
        elif data == 'stats' and from_id == ADMIN_ID:
            bots = get_bots_list()
            total = len(bots)
            running = 0
            for bot in bots:
                if bot['token']:
                    info = get_webhook_info(bot['token'])
                    if info and info.get('ok') and info['result'].get('url') and info['result']['url'] == bot['url']:
                        running += 1
            edit_message(chat_id, message_id,
                         f"📊 **الإحصائيات**\n📦 الكل: {total}\n🟢 يعمل: {running}\n🔴 متوقف: {total - running}",
                         reply_markup=inline_keyboard([
                             [{'text': '🔙 رجوع', 'callback_data': 'admin'}]
                         ]))
        
        elif data == 'reset' and from_id == ADMIN_ID:
            bots = get_bots_list()
            for bot in bots:
                folder_path = os.path.join(UPLOAD_DIR, bot['id'])
                if os.path.isdir(folder_path):
                    for f in os.listdir(folder_path):
                        os.remove(os.path.join(folder_path, f))
                    os.rmdir(folder_path)
            edit_message(chat_id, message_id,
                         "🗑 تم حذف جميع البوتات.",
                         reply_markup=inline_keyboard([
                             [{'text': '🔙 رجوع', 'callback_data': 'admin'}]
                         ]))
        
        elif data.startswith('detail_'):
            folder_name = data.replace('detail_', '')
            file_path = os.path.join(UPLOAD_DIR, folder_name, 'bot.php')
            if not os.path.isfile(file_path):
                edit_message(chat_id, message_id,
                             "❌ البوت غير موجود.",
                             reply_markup=inline_keyboard([
                                 [{'text': '🔙 رجوع', 'callback_data': 'my_bots'}]
                             ]))
                return
            token = extract_token(file_path)
            bot_url = get_bot_url(folder_name)
            status = 'غير معروف'
            if token:
                info = get_webhook_info(token)
                if info and info.get('ok') and info['result'].get('url'):
                    status = '🟢 يعمل' if info['result']['url'] == bot_url else '🔴 متوقف'
                else:
                    status = '🔴 متوقف'
            else:
                status = '⚠️ بدون توكن'
            text = f"📁 **{folder_name}**\n🔗 `{bot_url}`\n🆔 " + (f"`{token}`" if token else "⚠️ لا يوجد توكن") + f"\n📊 الحالة: {status}"
            keyboard = [
                [{'text': '▶️ تشغيل', 'callback_data': f"start_{folder_name}"}],
                [{'text': '⏹ إيقاف', 'callback_data': f"stop_{folder_name}"}],
                [{'text': '🗑 حذف', 'callback_data': f"delete_{folder_name}"}],
                [{'text': '🔙 رجوع', 'callback_data': 'my_bots'}]
            ]
            edit_message(chat_id, message_id, text, reply_markup=inline_keyboard(keyboard))
        
        elif data.startswith('start_'):
            folder_name = data.replace('start_', '')
            file_path = os.path.join(UPLOAD_DIR, folder_name, 'bot.php')
            if not os.path.isfile(file_path):
                answer_callback(callback['id'], "❌ غير موجود", show_alert=True)
                return
            token = extract_token(file_path)
            if not token:
                answer_callback(callback['id'], "❌ لا يوجد توكن", show_alert=True)
                return
            bot_url = get_bot_url(folder_name)
            result = set_webhook(token, bot_url)
            if result and result.get('ok'):
                answer_callback(callback['id'], "✅ تم التشغيل", show_alert=True)
                edit_message(chat_id, message_id,
                             f"✅ تم تشغيل `{folder_name}`",
                             reply_markup=inline_keyboard([
                                 [{'text': '🔙 رجوع', 'callback_data': f"detail_{folder_name}"}]
                             ]))
            else:
                answer_callback(callback['id'], "❌ فشل التشغيل", show_alert=True)
        
        elif data.startswith('stop_'):
            folder_name = data.replace('stop_', '')
            file_path = os.path.join(UPLOAD_DIR, folder_name, 'bot.php')
            if not os.path.isfile(file_path):
                answer_callback(callback['id'], "❌ غير موجود", show_alert=True)
                return
            token = extract_token(file_path)
            if not token:
                answer_callback(callback['id'], "❌ لا يوجد توكن", show_alert=True)
                return
            result = delete_webhook(token)
            if result and result.get('ok'):
                answer_callback(callback['id'], "⏹ تم الإيقاف", show_alert=True)
                edit_message(chat_id, message_id,
                             f"⏹ تم إيقاف `{folder_name}`",
                             reply_markup=inline_keyboard([
                                 [{'text': '🔙 رجوع', 'callback_data': f"detail_{folder_name}"}]
                             ]))
            else:
                answer_callback(callback['id'], "❌ فشل الإيقاف", show_alert=True)
        
        elif data.startswith('delete_'):
            folder_name = data.replace('delete_', '')
            folder_path = os.path.join(UPLOAD_DIR, folder_name)
            if not os.path.isdir(folder_path):
                answer_callback(callback['id'], "❌ غير موجود", show_alert=True)
                return
            for f in os.listdir(folder_path):
                os.remove(os.path.join(folder_path, f))
            os.rmdir(folder_path)
            answer_callback(callback['id'], "🗑 تم الحذف", show_alert=True)
            edit_message(chat_id, message_id,
                         f"🗑 تم حذف `{folder_name}`",
                         reply_markup=inline_keyboard([
                             [{'text': '🔙 رجوع', 'callback_data': 'my_bots'}]
                         ]))
        else:
            answer_callback(callback['id'], "❌ خيار غير معروف", show_alert=True)

# ============================================================
# 📤 دوال مساعدة لإرسال الرسائل وتعديلها
# ============================================================

def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    """إرسال رسالة عبر API"""
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    bot_api(BOT_TOKEN, 'sendMessage', data)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode='Markdown'):
    """تعديل رسالة موجودة"""
    data = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': parse_mode}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    bot_api(BOT_TOKEN, 'editMessageText', data)

def answer_callback(callback_id, text, show_alert=False):
    """الرد على استعلام الزر"""
    data = {'callback_query_id': callback_id, 'text': text, 'show_alert': show_alert}
    bot_api(BOT_TOKEN, 'answerCallbackQuery', data)

def inline_keyboard(buttons):
    """تحويل قائمة الأزرار إلى هيكل inline_keyboard"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            keyboard_row.append(btn)
        keyboard.append(keyboard_row)
    return {'inline_keyboard': keyboard}

# ============================================================
# 🚀 تشغيل البوت (Webhook أو Polling)
# ============================================================

if __name__ == '__main__':
    # تعيين Webhook للبوت الأساسي
    webhook_url = f"{BASE_URL}/webhook"
    result = set_webhook(BOT_TOKEN, webhook_url)
    if result and result.get('ok'):
        print(f"✅ تم تعيين Webhook: {webhook_url}")
    else:
        print("⚠️ فشل تعيين Webhook. سيتم استخدام Polling.")
        from telegram.ext import Application
        app = Application.builder().token(BOT_TOKEN).build()
        app.run_polling()
    
    # تشغيل خادم Flask
    app.run(host='0.0.0.0', port=8080)