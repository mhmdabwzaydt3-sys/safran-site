# سفران — مشروع الموقع (Astro + Cloudflare Pages)

نسخة أولية (v0.2) — **معاينة غير إنتاجية**. المصدر الكامل للمراجعة.

## ما يحتويه المشروع

```
src/
  data/posts.json          محتوى 19 مقالًا كما استُخرج من Blogger + حالة كل مقال (PUBLISHED/HOLD)
  data/blogger-pages.json  الصفحات الخمس الأصلية (مرجع فقط، غير منشورة)
  layouts/Base.astro       القالب الأساسي (RTL، ترويسة، تذييل بصفحات الثقة)
  pages/
    index.astro            الصفحة الرئيسية
    [year]/[month]/[slug].astro   صفحة المقال — المسار مطابق لـ Blogger
    label/[label].astro    صفحات التصنيف
    search.astro           بحث نصي + صوتي (Web Speech API)
    about, contact, privacy, terms, editorial-policy, corrections, disclosure, sitemap
    404.astro
    sitemap.xml.js         خريطة XML
  styles/global.css        نظام التصميم (Navy/Teal/Gold، RTL)
public/
  ads.txt (8 معرّفات)  robots.txt (معاينة: Disallow)  manifest.webmanifest  favicon.svg  search-index.json
docs/                      الوثيقة المرجعية v2.1 وتقارير التدقيق والبناء
  ARTICLE-INDEX.csv        خريطة كل مقال: المعرّف، المسار، الملف، الحالة، عدد الكلمات، رابط المعاينة
audit/                     سكربتات الاستخراج والتدقيق + جرد المحتوى (CSV)
data/raw-feed.json         نسخة Blogger الخام (أصل غير معدّل)
```

## التشغيل

```bash
npm install
npm run dev                 # تطوير محلي
PUBLIC_PREVIEW=1 npm run build   # بناء معاينة (noindex + robots disallow)
npm run build                    # بناء إصدار (indexable)
```

## النشر (معاينة)

```bash
npx wrangler pages deploy dist --project-name=safran-preview --branch=main
```

المشروع منشور على Cloudflare Pages بتحميل مباشر (بلا Git). لا يُربط أي نطاق ولا يُعدّل أي DNS من هذا المستودع.

## خط أنابيب المحتوى

1. `audit/extract_for_site.py` — يقرأ feed Blogger ويولّد `src/data/posts.json` (ينظّف السكربتات والإعلانات و`<h1>` المكرر).
2. `audit/fix_content.py` — تصحيحات تحريرية موثّقة: حذف تعليقات برمجية، حذف `【entity-…】`، تحويل الروابط المطلقة إلى نسبية، تصحيح ادعاء ETIAS، وتعليم المقال الفارغ كـ HOLD.
3. `audit/analyze2.py` + `make_inventory.py` — تدقيق وقياس لإنتاج `content-inventory.csv`.

كل تحويل مسجَّل في `docs/SAFRAN-INITIAL-BUILD-ar.md`، والنسخة الأصلية محفوظة في `data/raw-feed.json`.

## حالة المحتوى

- 18 مقالًا منشورًا، ومقال واحد (04 — شروط دخول بنين) **محجوب HOLD** لأن مصدره فارغ تمامًا في Blogger.
- لا إعلانات في هذه النسخة؛ سياسة الإعلانات (≤3 وحدات، تحميل مؤجل، حجز مساحة) موثقة في الوثيقة v2.1 §8.
- بريد التواصل: `safran@safrnblog.com` (مزوَّد من المالك).
