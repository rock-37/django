from django import forms
from .models import Subject

class SelectSubjectForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        label="Môn Học",
        empty_label="Chọn môn học",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

