# Motion Graphics Studio (mgs)

[English](README.md) · **العربية**

أداة مفتوحة المصدر لصنع فيديوهات الموشن جرافيكس بالكود (YouTube Shorts وReels وTikTok وفيديوهات 16:9)، بدون اشتراكات ولا مفاتيح API ولا تصيير على السحابة. كل شي يشتغل على جهازك بـPython وFFmpeg.

## شنو فيها
- **مشاهد بالكود:** عناوين، كروت تنزلق، عدادات، رسوم بيانية، نص حركي، تعليق سفلي، شعار، رسم على سبورة بيضاء، برق نيون، كونفيتي.
- **9 انتقالات** و**مؤثرات** (حبيبات، توهج، ارتجاج الكاميرا، فلاش، تدرج لوني).
- **ترجمة بالكلمة** (karaoke) مع تصدير SRT وVTT، تدعم العربي (من اليمين لليسار) والإنكليزي وأي لغة.
- **توقيت الصوت:** تقدير بدون إنترنت، أو دقيق إذا أعطيتها توقيت الكلمات.
- **مؤثرات صوتية مصنوعة بالكود** (بدون ملفات صوت مدفوعة)، وموسيقى تنخفض تلقائياً تحت الصوت.
- **أحجام جاهزة:** 9:16 و16:9 ومربع.
- **تصيير متوازي** وقابل للاستئناف، وتشغيل بالخلفية.
- **روبوت مقدّم اختياري** يتحرك ويتكلم مع الصوت.
- **أربعة قوالب جاهزة**، وتوثيق لأي مساعد ذكاء اصطناعي (`SKILL.md` و`AGENTS.md`).

## التثبيت
```bash
python -m venv .venv && source .venv/bin/activate     # ويندوز: .venv\Scripts\activate
pip install -r requirements.txt
# ثبّت FFmpeg (مجاني): apt install ffmpeg | brew install ffmpeg | winget install ffmpeg
python -m mgs doctor
```

## أول فيديو في دقيقة
```bash
python -m mgs init my-video --template compare
cd my-video
python -m mgs stills project.py 1 3 5 7 9          # صورة مرجعية تشوفها قبل التصيير
MGS_DURATION=5 python -m mgs all project.py        # معاينة 5 ثواني
python -m mgs all project.py --workers 4           # الفيديو كامل -> out.mp4
```

## الحدود الصريحة
الأداة ترسم موشن جرافيكس، ولا تسوي فيديو بالذكاء الاصطناعي، ولا تصلح حركة شخصيات بفيديو جاهز (مثل الأنمي)، ولا تزيد الفريمات أو ترفع الدقة بالذكاء الاصطناعي. التفاصيل في `docs/limits.md`.

## التوثيق
`docs/workflow.md` · `components.md` · `audio.md` · `style-analysis.md` · `script-craft.md` · `review-checklist.md` · `publishing.md` · `troubleshooting.md` · `limits.md` · `agents.md`

## الرخصة
Apache License 2.0 (راجع `LICENSE` و`NOTICE`). ملاحظات الأطراف الثالثة في `THIRD_PARTY.md`. شغّل ملفات `project.py` اللي تثق فيها بس، لأنها كود Python.
