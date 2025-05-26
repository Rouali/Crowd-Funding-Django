from django import forms
from .models import Project, ProjectImage, Donation, Report

class ProjectForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border rounded',
            'placeholder': 'education, healthcare, technology'
        }),
        help_text="Separate tags with commas"
    )

    class Meta:
        model = Project
        fields = ['title', 'details', 'category', 'total_target', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border rounded'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-2 border rounded'}),
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'details': forms.Textarea(attrs={'class': 'w-full p-2 border rounded h-32'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'total_target': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('end_time') <= cleaned_data.get('start_time'):
            raise forms.ValidationError("End time must be after start time")
        return cleaned_data

ProjectImageFormSet = forms.inlineformset_factory(
    Project, ProjectImage,
    fields=('image',),
    extra=3,
    widgets={'image': forms.ClearableFileInput(attrs={'class': 'file:bg-blue-50 file:border-0 file:rounded'})}
)


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Please enter a valid donation amount.")
        return amount
    

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }