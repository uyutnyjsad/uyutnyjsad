from django import forms
from products.models import Product, Category, Review
from orders.models import Order
from django.contrib.auth.models import User

class ProductAdminForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'image', 'category', 'in_stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле slug только для чтения
        self.fields['slug'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})

class CategoryAdminForm(forms.ModelForm):
    slug = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле slug только для чтения
        self.fields['slug'].widget.attrs.update({'class': 'form-control', 'readonly': 'readonly'})

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']