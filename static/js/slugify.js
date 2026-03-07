function cyrillicToLatin(text) {
    const cyrillicMap = {
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
    };

    return text.split('').map(char => cyrillicMap[char] || char).join('');
}

function generateSlug(text) {
    // Транслитерируем кириллицу в латиницу
    let transliterated = cyrillicToLatin(text);
    
    // Заменяем пробелы и специальные символы на дефисы
    let slug = transliterated
        .toLowerCase()
        .replace(/[^\w\s-]/g, '') // Удаляем не-алфавитные символы
        .replace(/[\s_-]+/g, '-') // Заменяем пробелы и подчеркивания на дефисы
        .replace(/^-+|-+$/g, ''); // Удаляем дефисы в начале и конце
    
    return slug;
}

document.addEventListener('DOMContentLoaded', function() {
    const nameInput = document.querySelector('input[name="name"]');
    const slugInput = document.querySelector('input[name="slug"]');
    
    if (nameInput && slugInput) {
        nameInput.addEventListener('input', function() {
            if (!slugInput.dataset.manualEdit) {
                slugInput.value = generateSlug(this.value);
            }
        });
        
        // Позволяем ручное редактирование slug
        slugInput.addEventListener('focus', function() {
            this.dataset.manualEdit = 'true';
        });
    }
});