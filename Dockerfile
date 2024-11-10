# استخدم صورة Python الرسمية كأساس
FROM python:3.11-slim

# تعيين المجلد الذي سيعمل فيه التطبيق داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع إلى الحاوية
COPY . /app

# تحديث الحزم وتثبيت git والمكتبات اللازمة
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean

# تثبيت المكتبات المطلوبة من ملف requirements.txt
RUN pip install -r requirements.txt
RUN pip install -e .

# تحديد الأمر الذي سيتم تشغيله عند بدء الحاوية
CMD ["python", "main.py"]
