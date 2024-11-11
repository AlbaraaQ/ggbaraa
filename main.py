import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests
import base64
from io import BytesIO
from PIL import Image
import videogen_hub  # استيراد مكتبة توليد الفيديو
import torchvision.io as io  # مكتبة حفظ الفيديو

# إعداد تسجيل الأخطاء والمعلومات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد مفتاح API لـ Hugging Face
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large-turbo"
HUGGING_FACE_HEADERS = {"Authorization": "Bearer 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"}

# تحميل النموذج الجديد للفيديو
videogen_model = videogen_hub.load('VideoCrafter2')

# متغير لتحديد النموذج الذي اختاره المستخدم
user_selected_model = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Hugging Face (Stable Diffusion)", callback_data="stable_diffusion"),
            InlineKeyboardButton("Video Generation (VideoCrafter2)", callback_data="videogen")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر النموذج الذي ترغب باستخدامه:", reply_markup=reply_markup)

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    selected_model = query.data
    user_selected_model[user_id] = selected_model
    await query.answer()
    await query.edit_message_text(text=f"تم اختيار النموذج: {selected_model}")

async def generate_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_prompt = update.message.text

    # تحقق من النموذج الذي اختاره المستخدم
    model = user_selected_model.get(user_id, "stable_diffusion")

    if model == "stable_diffusion":
        await update.message.reply_text("جاري إنشاء الصورة باستخدام نموذج Hugging Face... قد يستغرق ذلك بعض الوقت.")
        try:
            response = requests.post(HUGGING_FACE_API_URL, headers=HUGGING_FACE_HEADERS, json={"inputs": user_prompt})
            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(BytesIO(image_bytes))
                with BytesIO() as output:
                    image.save(output, format="PNG")
                    output.seek(0)
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output)
            else:
                await update.message.reply_text("عذرًا، لم أتمكن من توليد صورة باستخدام نموذج Hugging Face.")
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء توليد الصورة باستخدام Hugging Face: {e}")

    elif model == "videogen":
        await update.message.reply_text("جاري إنشاء الفيديو باستخدام نموذج VideoCrafter2... قد يستغرق ذلك بعض الوقت.")
        try:
            video = videogen_model.infer_one_video(prompt=user_prompt)
            output_filename = "generated_video.mp4"
            io.write_video(output_filename, video.permute(0, 2, 3, 1).numpy(), fps=30)
            with open(output_filename, 'rb') as video_file:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=video_file)
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء توليد الفيديو: {e}")

def main():
    # استبدل 'YOUR_TELEGRAM_BOT_TOKEN' بالتوكن الخاص بالبوت
    app = ApplicationBuilder().token('7865424971:AAF_Oe6lu8ZYAl5XIF1M6qU_8MK6GHWEll8').build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate_content))

    app.run_polling()

if __name__ == "__main__":
    main()
