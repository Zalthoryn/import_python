#!/usr/bin/env python3
"""
Ultimate setup script v2 for Django exam project (shoe_store).
Includes ALL fixes and improvements from the review session.

Run this script from the directory where you want your Django project root.
It will create all necessary files and directories with the correct content.

Usage:
    python ult2.py

After running, you should:
    - Create the PostgreSQL database 'shoe_store_3'
    - Run: python manage.py makemigrations
    - Run: python manage.py migrate
    - Import data: python manage.py import_excel_data  (requires CSV files in import/)
    - Run server: python manage.py runserver

Note: This script overwrites existing files. Make backups if needed.
"""

import os
from pathlib import Path

# ----------------------------------------------------------------------
# File contents dictionary
# Key: relative file path, Value: file content as string
# ----------------------------------------------------------------------

FILES = {
    # ==================== CONFIG ====================
    "config/__init__.py": "",
    "config/settings.py": '''
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-juxbbv#f+93@&1rt#7fyj=@e^700n1bdzjvx)9k!c7&abhet_q"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "shoe_store_3",
        "USER": "postgres",
        "PASSWORD": "123456",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "core.User"

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_REDIRECT_URL = "product_list"
LOGOUT_REDIRECT_URL = "login"
''',
    "config/urls.py": '''
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path

from core.views import (
    ProductCreateView,
    ProductListView,
    ProductUpdateView,
    ProductDeleteView,
    UserLoginView,
    OrderListView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrderListView.as_view(), name="order_list"),
    path("orders/add/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/edit/", OrderUpdateView.as_view(), name="order_edit"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
''',

    # ==================== CORE APP ====================
    "core/__init__.py": "",
    "core/apps.py": '''
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
''',
    "core/models.py": '''
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Name of the role")

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        return self.name


class PickupPoint(models.Model):
    address = models.TextField()

    def __str__(self) -> str:
        return self.address[:50]


class Product(models.Model):
    article = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, default="шт.")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    manufacturer = models.CharField(max_length=200)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    category = models.CharField(max_length=200)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)
    description = models.TextField()
    photo = models.ImageField(upload_to="products/", null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            this = Product.objects.get(id=self.id)
            if this.photo and self.photo and this.photo != self.photo:
                this.photo.delete(save=False)
        except Exception:
            pass
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.price * (1 - self.discount / 100) if self.discount else self.price


class Order(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=255, null=True, blank=True)
    pickup_code = models.IntegerField()
    status = models.CharField(max_length=50, default="Новый")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.IntegerField()
''',
    "core/admin.py": '''
from django.contrib import admin
from .models import Role, User, Supplier, PickupPoint, Product, Order, OrderItem

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Supplier)
admin.site.register(PickupPoint)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
''',

    # ==================== VIEWS (с исправлениями) ====================
    "core/views.py": '''
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from .forms import ProductForm, OrderForm
from .models import Product, Supplier, Order, OrderItem


class UserLoginView(LoginView):
    template_name = "core/login.html"


class ProductListView(ListView):
    model = Product
    template_name = "core/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        user_role = self.request.user.role.name if (self.request.user.is_authenticated and self.request.user.role) else "guest"
        if user_role in ["admin", "manager"]:
            queryset = Product.objects.all().select_related("supplier")
            search_query = self.request.GET.get("search", "")
            if search_query:
                # Поиск по всем текстовым полям, включая связанные модели
                queryset = queryset.filter(
                    Q(name__icontains=search_query)
                    | Q(description__icontains=search_query)
                    | Q(manufacturer__icontains=search_query)
                    | Q(category__icontains=search_query)
                    | Q(supplier__name__icontains=search_query)
                    | Q(article__icontains=search_query)
                    | Q(unit__icontains=search_query)
                )
            supplier_id = self.request.GET.get("supplier", "")
            if supplier_id and supplier_id != "all":
                queryset = queryset.filter(supplier_id=supplier_id)
            sort = self.request.GET.get("sort", "")
            if sort == "asc":
                queryset = queryset.order_by("quantity")
            elif sort == "desc":
                queryset = queryset.order_by("-quantity")
        else:
            queryset = Product.objects.all().select_related("supplier")

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["suppliers"] = Supplier.objects.all()
        context["current_search"] = self.request.GET.get("search", "")
        context["current_supplier"] = self.request.GET.get("supplier", "")
        context["current_sort"] = self.request.GET.get("sort", "")
        return context


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role
            and self.request.user.role.name == "admin"
        )


class ProductCreateUpdateMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_suppliers"] = Supplier.objects.all()
        return context


class ProductCreateView(AdminRequiredMixin, ProductCreateUpdateMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        messages.success(self.request, "Товар успешно добавлен")
        return super().form_valid(form)


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    model = Product
    template_name = "core/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        product = self.get_object()
        # Товар, который присутствует в заказе, удалить нельзя
        if OrderItem.objects.filter(product=product).exists():
            messages.error(
                self.request,
                f"Невозможно удалить товар '{product.name}', так как он присутствует в заказах.",
            )
            return HttpResponseRedirect(self.get_success_url())
        product.delete()
        messages.success(self.request, "Товар успешно удален.")
        return HttpResponseRedirect(self.get_success_url())


class ProductUpdateView(AdminRequiredMixin, ProductCreateUpdateMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Товар успешно обновлен")
        return super().form_valid(form)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role
            and self.request.user.role.name in ["admin", "manager"]
        )


class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "core/order_list.html"
    context_object_name = "orders"


class OrderCreateView(AdminRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "core/order_form.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        messages.success(self.request, "Заказ успешно добавлен")
        return super().form_valid(form)


class OrderUpdateView(AdminRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "core/order_form.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Заказ успешно обновлен")
        return super().form_valid(form)


class OrderDeleteView(AdminRequiredMixin, DeleteView):
    model = Order
    template_name = "core/order_confirm_delete.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        messages.success(self.request, "Заказ успешно удален.")
        return super().form_valid(form)
''',

    # ==================== FORMS (с исправлениями) ====================
    "core/forms.py": '''
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

from .models import Product, Supplier, Order


class ProductForm(forms.ModelForm):
    # Текстовое поле для ввода названия поставщика
    supplier_name = forms.CharField(label="Поставщик", required=True)

    class Meta:
        model = Product
        fields = [
            "article",
            "name",
            "unit",
            "price",
            "discount",
            "quantity",
            "description",
            "photo",
            "category",
            "manufacturer",
        ]
        labels = {
            "article": "Артикул",
            "name": "Название",
            "unit": "Единица измерения",
            "price": "Цена",
            "discount": "Скидка",
            "quantity": "Количество",
            "description": "Описание",
            "photo": "Фото",
            "category": "Категория",
            "manufacturer": "Производитель",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически собираем уникальные значения из БД
        categories = [('', '--- Выберите категорию ---')] + [
            (c, c) for c in Product.objects.values_list('category', flat=True).distinct() if c
        ]
        manufacturers = [('', '--- Выберите производителя ---')] + [
            (m, m) for m in Product.objects.values_list('manufacturer', flat=True).distinct() if m
        ]

        # Меняем текстовое поле ввода на выпадающий список
        self.fields['category'].widget = forms.Select(choices=categories)
        self.fields['manufacturer'].widget = forms.Select(choices=manufacturers)

        if self.instance.pk and self.instance.supplier:
            self.fields["supplier_name"].initial = self.instance.supplier.name

    def save(self, commit=True):
        # Найти существующего поставщика или создать нового
        supplier, _ = Supplier.objects.get_or_create(
            name=self.cleaned_data["supplier_name"].strip()
        )

        instance = super().save(commit=False)
        instance.supplier = supplier

        if commit:
            instance.save()
        return instance

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is not None and qty < 0:
            raise forms.ValidationError("Количество не может быть отрицательным")
        return qty

    def clean_discount(self):
        discount = self.cleaned_data.get("discount")
        if discount is not None and discount < 0:
            raise forms.ValidationError("Скидка не может быть отрицательной")
        if discount is not None and discount > 100:
            raise forms.ValidationError("Скидка не может превышать 100%")
        return discount

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        # Проверяем размер только для новых загруженных файлов
        if photo and hasattr(photo, "read"):
            width, height = get_image_dimensions(photo)
            if width and height and (width > 300 or height > 200):
                raise ValidationError("Размер изображения не должен превышать 300x200 пикселей.")
        return photo


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "pickup_point", "delivery_date", "pickup_code", "client_name"]
        labels = {
            "status": "Статус заказа",
            "pickup_point": "Пункт выдачи",
            "delivery_date": "Дата выдачи",
            "pickup_code": "Код получения",
            "client_name": "ФИО Клиента",
        }
        widgets = {
            "delivery_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Статус в виде выпадающего списка по ТЗ
        self.fields['status'].widget = forms.Select(choices=[
            ('Новый', 'Новый'),
            ('В сборке', 'В сборке'),
            ('Готов', 'Готов'),
            ('Завершен', 'Завершен'),
        ])
''',

    # ==================== IMPORT COMMAND (с sequence reset) ====================
    "core/management/__init__.py": "",
    "core/management/commands/__init__.py": "",
    "core/management/commands/import_excel_data.py": '''
import csv
import os
from typing import Any

from django.core.management.base import BaseCommand

from core.models import Order, OrderItem, PickupPoint, Product, Role, Supplier, User


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        base_path = "import/"

        # 1. Пункты выдачи
        with open(os.path.join(base_path, "pp.csv")) as f:
            reader = csv.DictReader(f, ["address"])
            for row in reader:
                print(row)
                PickupPoint.objects.get_or_create(address=row["address"])

        # 2. Товары и поставщики
        with open(os.path.join(base_path, "products.csv"), encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row)
                if not row:
                    continue

                sup_obj, _ = Supplier.objects.get_or_create(name=row["supplier"])
                row["supplier"] = sup_obj

                if row.get("photo") and not row["photo"].startswith("products/"):
                    row["photo"] = f"products/{row['photo']}"

                Product.objects.update_or_create(article=row["article"], defaults=row)

        # 3. Пользователи
        with open(os.path.join(base_path, "users.csv"), encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row)
                if not row:
                    continue

                role_obj, _ = Role.objects.get_or_create(name=row["role"])
                if not User.objects.filter(username=row["login"]).exists():
                    user = User.objects.create(
                        username=row["login"], full_name=row["full_name"], role=role_obj
                    )
                    user.set_password(str(row["password"]).strip())
                    user.save()

        # 4. Заказы и позиции заказов
        with open(os.path.join(base_path, "orders.csv"), encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(row)
                if not row:
                    continue

                pp_obj = (
                    PickupPoint.objects.get(id=row["pp"])
                    if PickupPoint.objects.filter(id=row["pp"]).exists()
                    else PickupPoint.objects.first()
                )
                order, created = Order.objects.get_or_create(
                    id=row["id"],
                    defaults={
                        "order_date": row["order_date"],
                        "delivery_date": row["delivery_date"],
                        "client_name": row["client_name"],
                        "pickup_code": row["pickup_code"],
                        "status": row["status"],
                        "pickup_point": pp_obj,
                    },
                )
                if created:
                    items = row["items"].split(",")
                    for i in range(0, len(items), 2):
                        art = items[i].strip()
                        try:
                            prod = Product.objects.get(article=art)
                            OrderItem.objects.create(
                                order=order, product=prod, count=int(items[i + 1])
                            )
                        except Exception:
                            pass

        # 5. Сброс PostgreSQL sequences после импорта с явными ID
        from django.db import connection

        with connection.cursor() as cursor:
            for table in ["core_order", "core_product", "core_pickuppoint"]:
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
                )
            self.stdout.write(self.style.SUCCESS("Sequences synced."))
''',
    "core/tests.py": '''
from django.test import TestCase
''',

    # ==================== TEMPLATES ====================
    "core/templates/core/base.html": '''
{% load static %}
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}ООО «Обувь»{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
    <link rel="icon" type="image/png" href="{% static 'images/Icon.ico' %}">
</head>
<body>
    <header>
        <div class="header-left">
            <img src="{% static 'images/Icon.png' %}" alt="Логотип">
            <span>ООО «Обувь»</span>
        </div>
        <div>
            {% if user.is_authenticated %}
                <span>{{ user.role.name }}</span>
                <strong>{{ user.full_name }}</strong> |
                <form action="{% url 'logout' %}" method="post" style="display: inline;">
                    {% csrf_token %}
                    <button type="submit" style="background: none; border: none; color: blue; text-decoration: underline; cursor: pointer; padding: 0; font-family: inherit; font-size: inherit;">Выйти</button>
                </form>
            {% else %}
                <span class="role-badge">Гость</span> |
                <a href="{% url 'login' %}">Вернуться ко входу</a>
            {% endif %}
        </div>
    </header>

    <div class="container">
        <h1>{% block h1 %}{% endblock %}</h1>
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {% if message.tags == 'error' %}❗{% elif message.tags == 'success' %}✔{% else %}❕{% endif %}
                    <strong>{{ message.tags|capfirst }}:</strong> {{ message }}
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </div>
</body>
</html>
''',
    "core/templates/core/login.html": '''
{% extends 'core/base.html' %}

{% block title %}Авторизация - ООО «Обувь»{% endblock %}
{% block h1 %}Вход в систему{% endblock %}

{% block content %}
<div>
    <form method="post">
        {% csrf_token %}
        {% if form.errors %}
        <div style="color: red;">
            {% for field in form %}
            {% for error in field.errors %}
            {{ error }}
            {% endfor %}
            {% endfor %}
            {% for error in form.non_field_errors %}
            {{ error }}
            {% endfor %}
        </div>
        {% endif %}

        <label>Логин (Email):</label><br>
        <input type="text" name="username">
        <label>Пароль:</label><br>
        <input type="password" name="password">
        <button type="submit" class="btn">Войти</button>
    </form>

    <a href="{% url 'product_list' %}">Войти как гость</a>
</div>
{% endblock %}
''',
    "core/templates/core/product_list.html": '''
{% extends 'core/base.html' %}
{% load static %}

{% block title %}Список товаров - ООО «Обувь»{% endblock %}
{% block h1 %}Каталог товаров{% endblock %}

{% block content %}
{% if user.role.name == "admin" or user.role.name == "manager" %}
<div>
    <form method="get" id="filter-form" style="display: flex;">
        <div>
            <label>Поиск:</label><br>
            <input type="text" name="search" value="{{ current_search }}" placeholder="Найти..."
                oninput="clearTimeout(this.delay); this.delay = setTimeout(() => updateFilters(), 500);">
        </div>

        <div>
            <label>Поставщик:</label><br>
            <select name="supplier" onchange="updateFilters()">
                <option value="all">Все поставщики</option>
                {% for s in suppliers %}
                <option value="{{ s.id }}" {% if current_supplier == s.id|stringformat:"i" %}selected{% endif %}>{{ s.name }}</option>
                {% endfor %}
            </select>
        </div>

        <div>
            <label>Сортировка (кол-во):</label><br>
            <select name="sort" onchange="updateFilters()">
                <option value="">Без сортировки</option>
                <option value="asc" {% if current_sort == "asc" %}selected{% endif %}>По возрастанию</option>
                <option value="desc" {% if current_sort == "desc" %}selected{% endif %}>По убыванию</option>
            </select>
        </div>

        <div style="margin-left: auto; display: flex; gap: 10px;">
            <a href="{% url 'order_list' %}" class="btn" style="background-color: #007bff; color: white; padding: 5px 10px; text-decoration: none;">Заказы</a>
            {% if user.role.name == 'admin' %}
                <a href="{% url 'product_create' %}" class="btn">Добавить товар</a>
            {% endif %}
        </div>
    </form>

</div>
{% endif %}
<div id="products-wrapper">
    {% for product in products %}
    <div class="product-card
        {% if product.discount > 15 %}sale{% endif %}
        {% if product.quantity == 0 %}out-of-stock{% endif %}">
        {% if product.photo %}
        <img src="{{ product.photo.url }}" class="image" alt="{{ product.name }}">
        {% else %}
        <img src="{% static 'images/picture.png' %}" class="image" alt="Заглушка">
        {% endif %}
        <div class="details">
            <strong>{{ product.category }} | {{ product.name }}</strong>
            <br />
            Описание товара: {{ product.description }}
            <br />
            Производитель: {{ product.manufacturer }}
            <br />
            Поставщик: {{ product.supplier.name }}
            <br />
            {% if product.discount > 0 %}
            Цена: <span class="old-price">{{ product.price }}</span> {{ product.final_price|floatformat:2 }} руб.
            {% else %}
            Цена: {{ product.price }} руб.
            {% endif %}
            <br />
            Единица измерения: {{ product.unit }}
            <br />
            Количество на складе: {{ product.quantity }}
            {% if user.role.name == "admin" %}
                <br>
                <a href="{% url 'product_edit' product.id %}">Редактировать товар</a> |
                <a href="{% url 'product_delete' product.id %}" style="color: red;">Удалить товар</a>
            {% endif %}
        </div>
        <div class="sale">{{ product.discount }}%</div>
    </div>
    {% empty %}
    <p>Товары не найдены.</p>
    {% endfor %}
</div>

<script>
function updateFilters() {
    const form = document.getElementById('filter-form');

    const formData = new FormData(form);
    const searchParams = new URLSearchParams(formData).toString();

    const url = `${window.location.pathname}?${searchParams}`;

    fetch(url)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const newContent = doc.getElementById('products-wrapper').innerHTML;

            document.getElementById('products-wrapper').innerHTML = newContent;

            window.history.pushState({}, '', url);
        })
        .catch(err => console.error("Ошибка фильтрации:", err));
}
</script>
{% endblock %}
''',
    "core/templates/core/product_form.html": '''
{% extends 'core/base.html' %}

{% block title %}
{% if is_edit %}Редактирование товара{% else %}Добавление товара{% endif %}
{% endblock %}

{% block h1 %}
{% if is_edit %}Редактирование товара: {{ object.article }}{% else %}Новый товар{% endif %}
{% endblock %}

{% block content %}
<div>
    <p><a href="{% url 'product_list' %}" class="btn-secondary">Назад к каталогу</a></p>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}

        {% if form.errors %}
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin-bottom: 15px; color: #721c24;">
            <strong>❗ Ошибка:</strong> Пожалуйста, исправьте ошибки ниже.
            <ul>
            {% for field, errors in form.errors.items %}
                {% for error in errors %}
                <li>{{ field }}: {{ error }}</li>
                {% endfor %}
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if is_edit %}
        <div style="margin-bottom: 15px;">
            <label><strong>ID товара (только для чтения):</strong></label><br>
            <input type="text" value="{{ object.id }}" readonly style="background-color: #f0f0f0; color: #555;">
        </div>
        {% endif %}

        {{ form.as_p }}
        <button type="submit" class="btn">Сохранить</button>

    </form>
</div>
{% endblock %}
''',
    "core/templates/core/product_confirm_delete.html": '''
{% extends 'core/base.html' %}
{% block title %}Удаление товара{% endblock %}
{% block h1 %}Вы уверены, что хотите удалить товар №{{ object.id }}?{% endblock %}

{% block content %}
<div>
    <form method="post">
        {% csrf_token %}
        <p style="color: red; font-weight: bold;">Это действие необратимо!</p>
        <button type="submit" class="btn" style="background-color: red; color: white;">Да, удалить</button>
        <a href="{% url 'product_list' %}" style="margin-left: 15px;">Отмена</a>
    </form>
</div>
{% endblock %}
''',
    "core/templates/core/order_list.html": '''
{% extends 'core/base.html' %}
{% block title %}Список заказов{% endblock %}
{% block h1 %}Управление заказами{% endblock %}

{% block content %}
<div style="margin-bottom: 20px;">
    <a href="{% url 'product_list' %}" style="text-decoration: none;">← Назад в каталог</a>
    {% if user.role.name == 'admin' %}
        <a href="{% url 'order_create' %}" class="btn" style="margin-left: 20px;">Добавить заказ</a>
    {% endif %}
</div>

<table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background-color: #f2f2f2;">
            <th>ID / Номер заказа</th>
            <th>Статус</th>
            <th>Пункт выдачи</th>
            <th>Дата выдачи</th>
            <th>Клиент</th>
            <th>Код</th>
            {% if user.role.name == 'admin' %}<th>Действия</th>{% endif %}
        </tr>
    </thead>
    <tbody>
        {% for order in orders %}
        <tr>
            <td>Заказ №{{ order.id }} (от {{ order.order_date|date:"d.m.Y" }})</td>
            <td><strong>{{ order.status }}</strong></td>
            <td>{{ order.pickup_point.address }}</td>
            <td>{{ order.delivery_date|date:"d.m.Y H:i" }}</td>
            <td>{{ order.client_name|default:"Не указан" }}</td>
            <td><span style="background: #eee; padding: 2px 5px;">{{ order.pickup_code }}</span></td>
            {% if user.role.name == 'admin' %}
            <td>
                <a href="{% url 'order_edit' order.id %}">Редактировать</a> |
                <a href="{% url 'order_delete' order.id %}" style="color: red;">Удалить</a>
            </td>
            {% endif %}
        </tr>
        {% empty %}
        <tr>
            <td colspan="7">Заказов пока нет.</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
''',
    "core/templates/core/order_form.html": '''
{% extends 'core/base.html' %}
{% block title %}{% if is_edit %}Редактирование заказа{% else %}Добавление заказа{% endif %}{% endblock %}
{% block h1 %}{% if is_edit %}Редактирование заказа №{{ object.id }}{% else %}Новый заказ{% endif %}{% endblock %}

{% block content %}
<div>
    <p><a href="{% url 'order_list' %}">← Вернуться к списку заказов</a></p>
    <form method="post">
        {% csrf_token %}

        {% if form.errors %}
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin-bottom: 15px; color: #721c24;">
            <strong>❗ Ошибка:</strong> Пожалуйста, исправьте ошибки ниже.
            <ul>
            {% for field, errors in form.errors.items %}
                {% for error in errors %}
                <li>{{ field }}: {{ error }}</li>
                {% endfor %}
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {{ form.as_p }}
        <button type="submit" class="btn">Сохранить заказ</button>
    </form>
</div>
{% endblock %}
''',
    "core/templates/core/order_confirm_delete.html": '''
{% extends 'core/base.html' %}
{% block title %}Удаление заказа{% endblock %}
{% block h1 %}Вы уверены, что хотите удалить заказ №{{ object.id }}?{% endblock %}

{% block content %}
<div>
    <form method="post">
        {% csrf_token %}
        <p style="color: red; font-weight: bold;">Это действие необратимо!</p>
        <button type="submit" class="btn" style="background-color: red; color: white;">Да, удалить</button>
        <a href="{% url 'order_list' %}" style="margin-left: 15px;">Отмена</a>
    </form>
</div>
{% endblock %}
''',

    # ==================== STATIC ====================
    "static/css/style.css": '''
body {
  font-family: "Times New Roman", serif;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  align-content: center;
  background-color: #7fff00;
  margin: 10px;
}

.header-left {
  font-size: xxx-large;
  padding: 10px;
}

.header-left img {
  width: 50px;
  height: 50px;
}

.product-card {
  border: solid black 2px;
  display: flex;
  padding: 10px;
}

.product-card.sale {
  background-color: #2e8b57;
}

.product-card.out-of-stock {
  background-color: aqua;
}

.product-card .image {
  width: 30%;
  border: 2px gray solid;
}

.product-card .details {
  flex: 1;
  border: solid black 1px;
  margin: 0 10px;
  padding: 5px;
}

.product-card .sale {
  border: solid black 1px;
  font-weight: bold;
  font-size: x-large;
  padding: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 15%;
}

.old-price {
  text-decoration: line-through;
  color: red;
}
''',

    # ==================== MANAGE.PY ====================
    "manage.py": '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''',
}

# Additional empty directories to create
DIRS = [
    "core/templates/core",
    "core/management/commands",
    "core/migrations",
    "static/css",
    "static/images",
    "media/products",
    "import",
]

# ----------------------------------------------------------------------
# Helper function
# ----------------------------------------------------------------------
def write_file(path: Path, content: str) -> None:
    """Create parent directories and write file content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  ✓ {path}")


def main():
    base = Path.cwd()
    print(f"📁 Writing files to: {base}\n")

    # Create directories
    print("Creating directories...")
    for dir_path in DIRS:
        full_dir = base / dir_path
        full_dir.mkdir(parents=True, exist_ok=True)
        print(f"  📂 {full_dir}")

    # Write all files
    print("\nWriting files...")
    for rel_path, content in FILES.items():
        target = base / rel_path
        write_file(target, content)

    print(f"\n✅ All {len(FILES)} files written successfully!")
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Create PostgreSQL database 'shoe_store_3'")
    print("2. python manage.py makemigrations core")
    print("3. python manage.py migrate")
    print("4. python manage.py import_excel_data")
    print("   (requires CSV files in import/: pp.csv, products.csv, users.csv, orders.csv)")
    print("5. python manage.py runserver")
    print()
    print("📌 Don't forget to place static images into static/images/:")
    print("   Icon.png, Icon.ico, picture.png")
    print("📌 Place product photos into media/products/:")
    print("   1.jpg ... 10.jpg")


if __name__ == "__main__":
    main()
