<?php
// ============================================================
// 🤖 بوت استضافة PHP (محسّن)
// 📌 يعمل على أي استضافة PHP (بما فيها InfinityFree)
// 👤 المطور: @I_Z_E_E
// ============================================================

// ============================================================
// 🔧 الإعدادات (عدّل هذه القيم)
// ============================================================
$BOT_TOKEN = "8743950401:AAENgy8-8kVzP4oR3UWRD_Y33Dzy59qX3ew";
$ADMIN_ID = 7757241009;
$BASE_URL = "https://astidafaphp.wuaze.com"; // رابط استضافتك (بدون /)
$UPLOAD_DIR = "bots/";
// ============================================================

// إنشاء مجلد الرفع
if (!is_dir($UPLOAD_DIR)) mkdir($UPLOAD_DIR, 0777, true);

// ============================================================
// 📦 دوال مساعدة
// ============================================================

function bot_api($method, $data = [], $token = null) {
    global $BOT_TOKEN;
    $token = $token ?? $BOT_TOKEN;
    $url = "https://api.telegram.org/bot{$token}/{$method}";
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    $res = curl_exec($ch);
    curl_close($ch);
    return json_decode($res, true);
}

function send_message($chat_id, $text, $reply_markup = null) {
    $data = ['chat_id' => $chat_id, 'text' => $text, 'parse_mode' => 'Markdown'];
    if ($reply_markup) $data['reply_markup'] = json_encode($reply_markup);
    return bot_api('sendMessage', $data);
}

function edit_message($chat_id, $message_id, $text, $reply_markup = null) {
    $data = ['chat_id' => $chat_id, 'message_id' => $message_id, 'text' => $text, 'parse_mode' => 'Markdown'];
    if ($reply_markup) $data['reply_markup'] = json_encode($reply_markup);
    return bot_api('editMessageText', $data);
}

function answer_callback($callback_id, $text, $show_alert = false) {
    return bot_api('answerCallbackQuery', ['callback_query_id' => $callback_id, 'text' => $text, 'show_alert' => $show_alert]);
}

function extract_token($content) {
    if (preg_match('/\b(\d{6,12}:[A-Za-z0-9_-]{20,})\b/', $content, $matches)) return $matches[1];
    return null;
}

function set_webhook($token, $url) {
    $result = bot_api('setWebhook', ['url' => $url], $token);
    return $result && $result['ok'];
}

function delete_webhook($token) {
    $result = bot_api('deleteWebhook', [], $token);
    return $result && $result['ok'];
}

function get_bot_url($folder_name) {
    global $BASE_URL, $UPLOAD_DIR;
    return rtrim($BASE_URL, '/') . '/' . rtrim($UPLOAD_DIR, '/') . '/' . $folder_name . '/bot.php';
}

function get_bots_list() {
    global $UPLOAD_DIR;
    $bots = [];
    if (is_dir($UPLOAD_DIR)) {
        foreach (scandir($UPLOAD_DIR) as $folder) {
            if ($folder != '.' && $folder != '..' && is_dir($UPLOAD_DIR . '/' . $folder)) {
                $file_path = $UPLOAD_DIR . '/' . $folder . '/bot.php';
                if (file_exists($file_path)) {
                    $content = file_get_contents($file_path);
                    $bots[] = [
                        'id' => $folder,
                        'url' => get_bot_url($folder),
                        'token' => extract_token($content),
                        'size' => filesize($file_path),
                        'time' => filemtime($file_path)
                    ];
                }
            }
        }
    }
    return $bots;
}

function is_admin($user_id) {
    global $ADMIN_ID;
    return $user_id == $ADMIN_ID;
}

function inline_keyboard($buttons) {
    return ['inline_keyboard' => $buttons];
}

// ============================================================
// 📥 معالج التحديثات
// ============================================================

$update = json_decode(file_get_contents('php://input'), true);
if (!$update) {
    echo "✅ بوت PHP يعمل!";
    exit;
}

$message = $update['message'] ?? null;
$callback = $update['callback_query'] ?? null;

if ($message) {
    $chat_id = $message['chat']['id'];
    $user_id = $message['from']['id'];
    $text = $message['text'] ?? '';
    $document = $message['document'] ?? null;
    $first_name = $message['from']['first_name'] ?? 'مستخدم';
    
    // ===== أمر /start =====
    if ($text == '/start') {
        $keyboard = [
            [['text' => '📤 رفع بوت', 'callback_data' => 'upload']],
            [['text' => '📋 بوتاتي', 'callback_data' => 'my_bots']],
            [['text' => 'ℹ️ تعليمات', 'callback_data' => 'help']]
        ];
        if (is_admin($user_id)) {
            $keyboard[] = [['text' => '⚙️ لوحة التحكم', 'callback_data' => 'admin']];
        }
        send_message($chat_id, "🤖 **بوت استضافة PHP**\nمرحباً $first_name!\nأرسل ملف `.php` لرفعه.", inline_keyboard($keyboard));
        exit;
    }
    
    // ===== أمر /help =====
    if ($text == '/help') {
        send_message($chat_id, "📖 **التعليمات**\n1. أرسل ملف `.php`.\n2. استخدم الأزرار لتشغيله.\n3. يمكنك حذف البوتات.");
        exit;
    }
    
    // ===== رفع ملف =====
    if ($document && pathinfo($document['file_name'], PATHINFO_EXTENSION) == 'php') {
        $file_id = $document['file_id'];
        $file_name = $document['file_name'];
        
        // تحميل الملف
        $file_info = bot_api('getFile', ['file_id' => $file_id]);
        if (!$file_info || !$file_info['ok']) {
            send_message($chat_id, "❌ فشل تحميل الملف.");
            exit;
        }
        $file_path = $file_info['result']['file_path'];
        $file_url = "https://api.telegram.org/file/bot{$BOT_TOKEN}/{$file_path}";
        $file_content = file_get_contents($file_url);
        if (!$file_content) {
            send_message($chat_id, "❌ فشل قراءة الملف.");
            exit;
        }
        
        // حفظ الملف
        $folder_name = 'bot_' . time() . '_' . bin2hex(random_bytes(4));
        $folder_path = $UPLOAD_DIR . '/' . $folder_name;
        mkdir($folder_path, 0777, true);
        file_put_contents($folder_path . '/bot.php', $file_content);
        
        // استخراج التوكن
        $token = extract_token($file_content);
        $bot_url = get_bot_url($folder_name);
        
        $msg = "✅ **تم رفع البوت!**\n";
        $msg .= "📁 `{$folder_name}`\n";
        $msg .= "🔗 `{$bot_url}`\n";
        $msg .= $token ? "🆔 تم العثور على توكن.\n" : "⚠️ لم يتم العثور على توكن.\n";
        $msg .= "\nاستخدم الأزرار للتحكم.";
        
        $keyboard = [
            [['text' => '▶️ تشغيل', 'callback_data' => "start_{$folder_name}"]],
            [['text' => '⏹ إيقاف', 'callback_data' => "stop_{$folder_name}"]],
            [['text' => '🗑 حذف', 'callback_data' => "delete_{$folder_name}"]],
            [['text' => '🔙 رجوع', 'callback_data' => 'back']]
        ];
        send_message($chat_id, $msg, inline_keyboard($keyboard));
        exit;
    }
}

// ===== معالج الأزرار =====
if ($callback) {
    $chat_id = $callback['message']['chat']['id'];
    $message_id = $callback['message']['message_id'];
    $data = $callback['data'];
    $user_id = $callback['from']['id'];
    $callback_id = $callback['id'];
    
    // زر رجوع
    if ($data == 'back') {
        $keyboard = [
            [['text' => '📤 رفع بوت', 'callback_data' => 'upload']],
            [['text' => '📋 بوتاتي', 'callback_data' => 'my_bots']],
            [['text' => 'ℹ️ تعليمات', 'callback_data' => 'help']]
        ];
        if (is_admin($user_id)) $keyboard[] = [['text' => '⚙️ لوحة التحكم', 'callback_data' => 'admin']];
        edit_message($chat_id, $message_id, "🤖 **بوت استضافة PHP**\nاختر أحد الخيارات:", inline_keyboard($keyboard));
        exit;
    }
    
    // زر رفع
    if ($data == 'upload') {
        edit_message($chat_id, $message_id, "📤 أرسل ملف `.php` لرفعه.", inline_keyboard([
            [['text' => '🔙 رجوع', 'callback_data' => 'back']]
        ]));
        exit;
    }
    
    // زر قائمة البوتات
    if ($data == 'my_bots') {
        $bots = get_bots_list();
        if (empty($bots)) {
            edit_message($chat_id, $message_id, "📭 لا توجد بوتات مرفوعة.", inline_keyboard([
                [['text' => '📤 رفع بوت', 'callback_data' => 'upload']],
                [['text' => '🔙 رجوع', 'callback_data' => 'back']]
            ]));
            exit;
        }
        $text = "📋 **بوتاتك المرفوعة:**\n\n";
        foreach ($bots as $bot) {
            $status = '🟢 يعمل';
            if ($bot['token']) {
                $info = bot_api('getWebhookInfo', [], $bot['token']);
                if ($info && $info['ok'] && isset($info['result']['url']) && $info['result']['url'] == $bot['url']) {
                    $status = '🟢 يعمل';
                } else {
                    $status = '🔴 متوقف';
                }
            } else {
                $status = '⚠️ بدون توكن';
            }
            $text .= "📁 `{$bot['id']}` — {$status}\n";
            $text .= "🔗 `{$bot['url']}`\n\n";
        }
        $keyboard = [];
        foreach ($bots as $bot) {
            $keyboard[] = [['text' => "📁 {$bot['id']}", 'callback_data' => "detail_{$bot['id']}"]];
        }
        $keyboard[] = [['text' => '🔙 رجوع', 'callback_data' => 'back']];
        edit_message($chat_id, $message_id, $text, inline_keyboard($keyboard));
        exit;
    }
    
    // زر التعليمات
    if ($data == 'help') {
        edit_message($chat_id, $message_id, "📖 **التعليمات**\n1. أرسل ملف `.php`.\n2. استخدم الأزرار لتشغيله.\n3. يمكنك حذف البوتات.", inline_keyboard([
            [['text' => '🔙 رجوع', 'callback_data' => 'back']]
        ]));
        exit;
    }
    
    // زر لوحة التحكم (للمطور)
    if ($data == 'admin' && is_admin($user_id)) {
        $bots = get_bots_list();
        edit_message($chat_id, $message_id, "⚙️ **لوحة التحكم**\n📦 عدد البوتات: " . count($bots), inline_keyboard([
            [['text' => '📊 الإحصائيات', 'callback_data' => 'stats']],
            [['text' => '🗑 مسح الكل', 'callback_data' => 'reset']],
            [['text' => '🔙 رجوع', 'callback_data' => 'back']]
        ]));
        exit;
    }
    
    // زر الإحصائيات (للمطور)
    if ($data == 'stats' && is_admin($user_id)) {
        $bots = get_bots_list();
        $total = count($bots);
        $running = 0;
        foreach ($bots as $bot) {
            if ($bot['token']) {
                $info = bot_api('getWebhookInfo', [], $bot['token']);
                if ($info && $info['ok'] && isset($info['result']['url']) && $info['result']['url'] == $bot['url']) $running++;
            }
        }
        edit_message($chat_id, $message_id, "📊 **الإحصائيات**\n📦 الكل: {$total}\n🟢 يعمل: {$running}\n🔴 متوقف: " . ($total - $running), inline_keyboard([
            [['text' => '🔙 رجوع', 'callback_data' => 'admin']]
        ]));
        exit;
    }
    
    // زر مسح الكل (للمطور)
    if ($data == 'reset' && is_admin($user_id)) {
        $bots = get_bots_list();
        foreach ($bots as $bot) {
            $folder = $UPLOAD_DIR . '/' . $bot['id'];
            if (is_dir($folder)) {
                array_map('unlink', glob("$folder/*.*"));
                rmdir($folder);
            }
        }
        edit_message($chat_id, $message_id, "🗑 تم حذف جميع البوتات.", inline_keyboard([
            [['text' => '🔙 رجوع', 'callback_data' => 'admin']]
        ]));
        exit;
    }
    
    // ===== إدارة البوتات الفردية =====
    if (preg_match('/^(detail|start|stop|delete)_(bot_.+)$/', $data, $matches)) {
        $action = $matches[1];
        $bot_id = $matches[2];
        $file_path = $UPLOAD_DIR . '/' . $bot_id . '/bot.php';
        $bot_url = get_bot_url($bot_id);
        
        if (!file_exists($file_path)) {
            answer_callback($callback_id, "❌ البوت غير موجود.", true);
            exit;
        }
        $content = file_get_contents($file_path);
        $token = extract_token($content);
        
        if ($action == 'detail') {
            $status = '🟢 يعمل';
            if ($token) {
                $info = bot_api('getWebhookInfo', [], $token);
                if ($info && $info['ok'] && isset($info['result']['url']) && $info['result']['url'] == $bot_url) {
                    $status = '🟢 يعمل';
                } else {
                    $status = '🔴 متوقف';
                }
            } else {
                $status = '⚠️ بدون توكن';
            }
            $text = "📁 **{$bot_id}**\n🔗 `{$bot_url}`\n📊 الحالة: {$status}";
            $keyboard = [
                [['text' => '▶️ تشغيل', 'callback_data' => "start_{$bot_id}"]],
                [['text' => '⏹ إيقاف', 'callback_data' => "stop_{$bot_id}"]],
                [['text' => '🗑 حذف', 'callback_data' => "delete_{$bot_id}"]],
                [['text' => '🔙 رجوع', 'callback_data' => 'my_bots']]
            ];
            edit_message($chat_id, $message_id, $text, inline_keyboard($keyboard));
            exit;
        }
        
        if (!$token) {
            answer_callback($callback_id, "❌ لا يوجد توكن صالح.", true);
            exit;
        }
        
        if ($action == 'start') {
            if (set_webhook($token, $bot_url)) {
                answer_callback($callback_id, "✅ تم التشغيل", true);
                edit_message($chat_id, $message_id, "✅ تم تشغيل `{$bot_id}`", inline_keyboard([
                    [['text' => '🔙 رجوع', 'callback_data' => "detail_{$bot_id}"]]
                ]));
            } else {
                answer_callback($callback_id, "❌ فشل التشغيل", true);
            }
            exit;
        }
        
        if ($action == 'stop') {
            if (delete_webhook($token)) {
                answer_callback($callback_id, "⏹ تم الإيقاف", true);
                edit_message($chat_id, $message_id, "⏹ تم إيقاف `{$bot_id}`", inline_keyboard([
                    [['text' => '🔙 رجوع', 'callback_data' => "detail_{$bot_id}"]]
                ]));
            } else {
                answer_callback($callback_id, "❌ فشل الإيقاف", true);
            }
            exit;
        }
        
        if ($action == 'delete') {
            delete_webhook($token);
            $folder = $UPLOAD_DIR . '/' . $bot_id;
            if (is_dir($folder)) {
                array_map('unlink', glob("$folder/*.*"));
                rmdir($folder);
            }
            answer_callback($callback_id, "🗑 تم الحذف", true);
            edit_message($chat_id, $message_id, "🗑 تم حذف `{$bot_id}`", inline_keyboard([
                [['text' => '🔙 رجوع', 'callback_data' => 'my_bots']]
            ]));
            exit;
        }
    }
    
    answer_callback($callback_id, "❌ خيار غير معروف", true);
}

// ============================================================
// 🏠 صفحة ويب للتأكيد
// ============================================================
?>
<!DOCTYPE html>
<html>
<head><title>🤖 بوت استضافة PHP</title></head>
<body style="font-family:sans-serif;text-align:center;padding:50px;background:#0f0f1a;color:#fff;">
    <h1>🤖 بوت استضافة PHP</h1>
    <p style="color:#4caf50;">✅ البوت يعمل ويستقبل التحديثات عبر Webhook.</p>
    <p>📌 أرسل ملف <code>.php</code> إلى البوت لرفعه.</p>
</body>
</html>