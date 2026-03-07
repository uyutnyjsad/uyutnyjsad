from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone_number', 'email']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введите полный адрес доставки'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@mail.ru'}),
        }
        labels = {
            'shipping_address': 'Адрес доставки',
            'phone_number': 'Номер телефона',
            'email': 'Электронная почта',
        }
        help_texts = {
            'shipping_address': 'Укажите полный адрес, включая индекс, город, улицу, дом и квартиру',
            'phone_number': 'Номер должен быть в формате +7 XXX XXX XX XX',
        }