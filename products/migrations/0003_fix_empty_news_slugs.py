from django.db import migrations
from django.utils.text import slugify


def fix_empty_slugs(apps, schema_editor):
    News = apps.get_model('products', 'News')
    for news in News.objects.filter(slug=''):
        news.slug = slugify(news.title, allow_unicode=True)
        if not news.slug:
            news.slug = f'news-{news.id}'
        news.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_news'),
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs, migrations.RunPython.noop),
    ]
