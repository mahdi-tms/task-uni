from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Order


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="نام", max_length=30, required=False)
    last_name = forms.CharField(label="نام خانوادگی", max_length=30, required=False)
    email = forms.EmailField(label="ایمیل")

    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")
        labels = {
            "username": "نام کاربری",
            "password1": "رمز عبور",
            "password2": "تکرار رمز عبور",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            "w-full rounded-lg border border-slate-200 px-3 py-3 text-sm "
            "focus:border-brand-500 focus:ring-2 focus:ring-brand-200"
        )
        for name, field in self.fields.items():
            css = base
            if "password" in name:
                field.widget.attrs.update({"class": css})
            else:
                field.widget.attrs.update({"class": css})
        self.fields["email"].widget.attrs.setdefault("autocomplete", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base = (
            "w-full rounded-lg border border-slate-200 px-3 py-3 text-sm "
            "focus:border-brand-500 focus:ring-2 focus:ring-brand-200"
        )

        self.fields["username"].widget.attrs.update({
            "class": base,
            "autocomplete": "username",
        })
        self.fields["password"].widget.attrs.update({
            "class": base,
            "autocomplete": "current-password",
        })

class CheckoutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = (
            "w-full rounded-lg border border-slate-200 px-3 py-3 text-sm "
            "focus:border-brand-500 focus:ring-2 focus:ring-brand-200"
        )
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": base})

    class Meta:
        model = Order
        fields = (
            "full_name",
            "email",
            "address",
            "city",
            "postal_code",
            "country",
        )
        labels = {
            "full_name": "نام و نام خانوادگی",
            "email": "ایمیل",
            "address": "آدرس کامل",
            "city": "شهر",
            "postal_code": "کد پستی",
            "country": "کشور",
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
