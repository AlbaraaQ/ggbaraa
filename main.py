from huggingface_hub import login
import videogen_hub
import torch
import torchvision.io as io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# تسجيل الدخول باستخدام Token الخاص بك
login(token="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")

# تحميل النموذج
model = videogen_hub.load('VideoCrafter2')

# وظيفة لتوليد الفيديو بناءً على النص المدخل
def generate_video(prompt: str) -> str:
    video = model.infer_one_video(prompt=prompt)
    output_filename = "generated_video.mp4"
    io.write_video(output_filename, video.permute(0, 2, 3, 1).numpy(), fps=30)
    return output_filename

# وظيفة لإرسال رسالة ترحيب عند استخدام أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "مرحبًا بك في بوت توليد الفيديوهات! أرسل لي وصفًا نصيًا وسأقوم بإنشاء فيديو لك 🎥."
    )

# وظيفة التعامل مع الرسائل من تيليجرام
def handle_message(update: Update, context: CallbackContext):
    user_prompt = update.message.text
    update.message.reply_text("جاري إنشاء الفيديو، يرجى الانتظار...")
    try:
        video_path = generate_video(user_prompt)
        with open(video_path, 'rb') as video_file:
            update.message.reply_video(video=video_file)
    except Exception as e:
        update.message.reply_text(f"حدث خطأ أثناء توليد الفيديو: {e}")

# إعداد البوت
def main():
    TELEGRAM_TOKEN = '7865424971:AAF_Oe6lu8ZYAl5XIF1M6qU_8MK6GHWEll8'  # ضع التوكن الخاص بالبوت هنا
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
