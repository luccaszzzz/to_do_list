from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        required=False,
        label="Data de Vencimento",
    )

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "status", "priority"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Título",
            "description": "Descrição",
            "status": "Status",
            "priority": "Prioridade",
        }
