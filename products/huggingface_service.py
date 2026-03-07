import io
import os
import tempfile
import time
from typing import Any

try:
    from huggingface_hub import InferenceClient
except ImportError:
    InferenceClient = None

try:
    from PIL import Image
except ImportError:
    Image = None


class PlantClassifierError(Exception):
    pass


def _parse_label(item: Any) -> tuple[str, float]:
    if isinstance(item, dict):
        label = str(item.get('label', '')).strip()
        score = float(item.get('score', 0.0) or 0.0)
        return label, score

    label = str(getattr(item, 'label', '')).strip()
    score = float(getattr(item, 'score', 0.0) or 0.0)
    return label, score


def _build_landscape_prompt(object_label: str) -> str:
    return (
        f"Нейросеть определила объект на фото как: '{object_label}' (название на английском).\n\n"
        "Твоя задача:\n"
        "1. Переведи название объекта на русский язык (укажи перевод в начале ответа).\n"
        "2. Дай 5 коротких практичных рекомендаций для проекта «Уютный Сад».\n\n"
        "Рекомендации должны включать:\n"
        "• Как этот объект можно использовать или обыграть в садовом оформлении.\n"
        "• С какими материалами и элементами декора сочетать.\n"
        "• Где лучше разместить объект/зону с таким мотивом.\n"
        "• На что обратить внимание по уходу/эксплуатации.\n"
        "• Идею для визуально гармоничного оформления.\n\n"
        "Если объект не относится к саду напрямую, предложи близкий декоративный аналог для сада."
    )


def classify_plant_and_recommend(image_bytes: bytes) -> dict[str, Any]:
    if InferenceClient is None:
        raise PlantClassifierError('Пакет huggingface_hub не установлен.')
    if Image is None:
        raise PlantClassifierError('Пакет Pillow не установлен.')

    token = os.getenv('HUGGINGFACEHUB_API_TOKEN', '')
    if not token:
        raise PlantClassifierError('Не найден токен Hugging Face.')

    image_model = os.environ.get('HF_IMAGE_MODEL', 'google/vit-base-patch16-224')
    chat_model = os.environ.get('HF_CHAT_MODEL', 'Qwen/Qwen2.5-7B-Instruct')

    client = InferenceClient(token=token)

    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
    except Exception as exc:
        raise PlantClassifierError(f'Не удалось прочитать изображение: {exc}') from exc

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            image.save(tmp_file, format='JPEG')
            temp_file_path = tmp_file.name

        try:
            predictions_raw = client.image_classification(temp_file_path, model=image_model)
        except Exception as exc:
            error_msg = str(exc).lower()
            if '503' in error_msg or 'loading' in error_msg:
                time.sleep(15)
                predictions_raw = client.image_classification(temp_file_path, model=image_model)
            else:
                raise PlantClassifierError(f'Ошибка API классификации: {exc}') from exc

    except Exception as exc:
        raise PlantClassifierError(f'Ошибка классификации изображения: {exc}') from exc
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    predictions: list[dict[str, Any]] = []
    for item in predictions_raw[:3]:
        label, score = _parse_label(item)
        if not label:
            continue
        predictions.append({'label': label, 'score': round(score * 100, 2)})

    if not predictions:
        raise PlantClassifierError('На фото не найдено распознаваемых классов. Попробуйте другое фото.')

    top_label = predictions[0]['label']
    prompt = _build_landscape_prompt(top_label)

    try:
        completion = client.chat_completion(
            model=chat_model,
            messages=[
                {'role': 'system', 'content': 'Ты эксперт по предметному анализу и садовому декору.'},
                {'role': 'user', 'content': prompt},
            ],
            temperature=0.3,
        )
        recommendation = completion.choices[0].message.content.strip()
    except Exception:
        recommendation = (
            f'На фото вероятнее всего: {top_label}. Используйте это как ориентир для подбора декора, '
            'материалов и композиции в зоне отдыха сада.'
        )

    return {
        'predictions': predictions,
        'top_label': top_label,
        'recommendation': recommendation,
        'image_model': image_model,
        'chat_model': chat_model,
    }
