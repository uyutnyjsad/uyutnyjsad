from django import forms
from .models import Product, Category, Review


class PlantClassifierForm(forms.Form):
    image = forms.ImageField(
        label='Фото объекта',
        help_text='Загрузите четкое фото объекта или сцены (JPG/PNG).',
        widget=forms.ClearableFileInput(
            attrs={'class': 'form-control', 'accept': 'image/*'}
        ),
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'image', 'category', 'in_stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Оставьте ваш отзыв...'}),
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
        }

