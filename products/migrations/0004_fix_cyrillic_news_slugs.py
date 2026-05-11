from django.db import migrations
import re


def transliterate(text):
    table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    for cyr, lat in table.items():
        text = text.replace(cyr, lat)
    return text


def slug_from_title(title):
    transliterated = transliterate(title)
    slug = re.sub(r'[^\w\s-]', '', transliterated).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug


def fix_cyrillic_slugs(apps, schema_editor):
    News = apps.get_model('products', 'News')
    used_slugs = set(
        News.objects.values_list('slug', flat=True)
    )
    for news in News.objects.all():
        # Only fix slugs that contain non-ASCII characters
        if not news.slug.isascii():
            used_slugs.discard(news.slug)
            base = slug_from_title(news.title) or f'news-{news.pk}'
            candidate = base
            counter = 1
            while candidate in used_slugs:
                candidate = f'{base}-{counter}'
                counter += 1
            news.slug = candidate
            used_slugs.add(candidate)
            news.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_fix_empty_news_slugs'),
    ]

    operations = [
        migrations.RunPython(fix_cyrillic_slugs, migrations.RunPython.noop),
    ]
