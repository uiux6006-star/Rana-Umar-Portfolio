from django import forms

from .models import ContactMessage


# ================= CONTACT FORM =================

class ContactForm(forms.ModelForm):

    # Honeypot: hidden from people, bots fill it in.
    website = forms.CharField(required=False)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "project_type", "budget", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your Email"}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject"}),
            "message": forms.Textarea(attrs={
                "rows": 6,
                "placeholder": "Tell me about your project, goals and deadline",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["project_type"].choices = [("", "What do you need?")] + ContactMessage.PROJECT_TYPE_CHOICES
        self.fields["budget"].choices = [("", "Estimated budget")] + ContactMessage.BUDGET_CHOICES

        for name, field in self.fields.items():
            css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
