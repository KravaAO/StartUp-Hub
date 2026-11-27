
from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["message"]

        labels = {
            "message": "Повідомлення автору проєкту"
        }

        widgets = {
            "message": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Чому ви хочете приєднатися до команди?"
            })
        }
