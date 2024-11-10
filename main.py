import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import login
import videogen_hub
import torch
import torchvision.io as io

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تسجيل الدخول باستخدام Token الخاص بك
login(token="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")

# تحميل النموذج
model = videogen_hub.load('VideoCrafter2')

# وظيفة لتوليد الفيديو بناءً على النص المدخل
def generate_video(prompt: str) -> str:
    try:
        video = model.infer_one_video(prompt=prompt)
        output_filename = "generated_video.mp4"
        io.write_video(output_filename, video.permute(0, 2, 3, 1).numpy(), fps=30)
        return output_filename
    except Exception as e:
        logging.error(f"Error in generating video: {e}")
        raise

# وظيفة لإرسال رسالة ترحيب عند استخدام أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Received /start command")
    await update.message.reply_text(
        "مرحبًا بك في بوت توليد الفيديوهات! أرسل لي وصفًا نصيًا وسأقوم بإنشاء فيديو لك 🎥."
    )

# وظيفة التعامل مع الرسائل من تيليجرام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    logging.info(f"Received message: {user_prompt}")
    await update.message.reply_text("جاري إنشاء الفيديو، يرجى الانتظار...")
    try:
        video_path = generate_video(user_prompt)
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء توليد الفيديو: {e}")

# إعداد البوت
def main():
    TELEGRAM_TOKEN = '7865424971:AAF_Oe6lu8ZYAl5XIF1M6qU_8MK6GHWEll8'  # ضع التوكن الخاص بالبوت هنا
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    try:
        logging.info("Bot is starting...")
        application.run_polling()
    except Exception as e:
        logging.error(f"Error occurred during bot polling: {e}")

if __name__ == '__main__':
    main()
