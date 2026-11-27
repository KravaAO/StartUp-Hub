from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    """Create/Edit form. budget, owner, status, is_public are intentionally excluded."""

    class Meta:
        model = Project
        fields = ['title', 'short_description', 'description', 'category', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'deadline': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('Назва не може бути порожньою.')
        return title
