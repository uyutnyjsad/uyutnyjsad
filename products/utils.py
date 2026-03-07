from django.utils.text import slugify
import re

def transliterate_russian_to_english(text):
    """
    Транслитерирует русский текст в английский
    """
    # Словарь для транслитерации
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    # Заменяем русские буквы на английские аналоги
    for rus, eng in translit_dict.items():
        text = text.replace(rus, eng)
    
    return text

def generate_slug_from_name(name):
    """
    Генерирует slug из названия с транслитерацией русского текста
    """
    # Транслитерируем русский текст в английский
    transliterated_name = transliterate_russian_to_english(name)
    
    # Используем стандартную slugify для создания slug
    slug = slugify(transliterated_name)
    
    # Удаляем возможные двойные дефисы
    slug = re.sub(r'[-]+', '-', slug)
    
    # Удаляем дефисы в начале и конце
    slug = slug.strip('-')
    
    return slug

def generate_unique_slug(model, name, current_slug=None, instance=None):
    """
    Генерирует уникальный slug для модели
    """
    if current_slug:
        base_slug = generate_slug_from_name(current_slug)
    else:
        base_slug = generate_slug_from_name(name)
    
    slug = base_slug
    counter = 1
    
    # Проверяем уникальность slug
    while model.objects.filter(slug=slug).exists():
        # Если это редактирование существующего объекта и slug принадлежит ему
        if instance and model.objects.filter(slug=slug, pk=instance.pk).exists():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug