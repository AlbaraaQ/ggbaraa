from huggingface_hub import login
import videogen_hub

# تسجيل الدخول باستخدام Token الخاص بك
login(token="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")
# تحميل النموذج وتنفيذ الاستدلال
model = videogen_hub.load('VideoCrafter2')
video = model.infer_one_video(prompt="A child excitedly swings on a rusty swing set, laughter filling the air.")

# هنا الفيديو هو tensor من نوع torch وحجمه torch.Size([16, 3, 320, 512])
