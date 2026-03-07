from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from .utils import generate_unique_slug, generate_slug_from_name
import math

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='categories', blank=True, null=True, verbose_name="Изображение")
    icon = models.CharField(max_length=50, default='leaf', verbose_name="Иконка")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self._state.adding:
            self.slug = generate_unique_slug(Category, self.name, instance=self)
        else:
            try:
                old_instance = Category.objects.get(pk=self.pk)
                if old_instance.name != self.name:
                    self.slug = generate_unique_slug(Category, self.name, instance=self)
            except Category.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/category-placeholder.jpg'

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='products', verbose_name="Изображение")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self._state.adding:
            self.slug = generate_unique_slug(Product, self.name, instance=self)
        else:
            try:
                old_instance = Product.objects.get(pk=self.pk)
                if old_instance.name != self.name:
                    self.slug = generate_unique_slug(Product, self.name, instance=self)
            except Product.DoesNotExist:
                pass
        
        # Убрана логика автоматической установки is_new
        super().save(*args, **kwargs)

    @property
    def is_new(self):
        """Вычисляемое свойство для определения новинки (30 дней с момента создания)"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days <= 30
    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/product-placeholder.jpg'
    



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user} на {self.product}"