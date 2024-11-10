import logging

from huggingface_hub import login
import videogen_hub
import torch
import torchvision.io as io
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تسجيل الدخول باستخدام Token الخاص بك
login(token="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")

# تحميل النموذج
model = videogen_hub.load('VideoCrafter2')

# وظيفة لتوليد الفيديو بناءً على النص المدخل
def generate_video(prompt: str) -> str:
    logging.info(f"Starting video generation for prompt: {prompt}")
    video = model.infer_one_video(prompt=prompt)
    output_filename = "generated_video.mp4"
    io.write_video(output_filename, video.permute(0, 2, 3, 1).numpy(), fps=30)
    logging.info(f"Video generation complete, saved to {output_filename}")
    return output_filename

# وظيفة لإرسال رسالة ترحيب عند استخدام أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا بك في بوت توليد الفيديوهات! أرسل لي وصفًا نصيًا وسأقوم بإنشاء فيديو لك 🎥."
    )

# وظيفة التعامل مع الرسائل من تيليجرام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    await update.message.reply_text("جاري إنشاء الفيديو، يرجى الانتظار...")
    try:
        video_path = generate_video(user_prompt)
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file)
    except Exception as e:
        logging.error(f"Error during video generation: {e}")
        await update.message.reply_text(f"حدث خطأ أثناء توليد الفيديو: {e}")

# إعداد البوت
def main():
    TELEGRAM_TOKEN = '7865424971:AAF_Oe6lu8ZYAl5XIF1M6qU_8MK6GHWEll8'
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
