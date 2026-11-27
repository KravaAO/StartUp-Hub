from django import forms
from .models import ProjectRole


class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = ProjectRole
        fields = ['title', 'description', 'slots', 'is_open']

    def clean_slots(self):
        slots = self.cleaned_data.get('slots')
        if slots is None or slots < 1:
            raise forms.ValidationError('Кількість місць повинна бути не менше 1.')
        return slots