from django import forms

from .models import ContactMessage, Testimonial


def style_fields(form):
    for field in form.fields.values():
        css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
        field.widget.attrs["class"] = css


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

        style_fields(self)

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))


# ================= REVIEW FORM =================

class TestimonialForm(forms.ModelForm):

    # Honeypot: hidden from people, bots fill it in.
    website = forms.CharField(required=False)

    class Meta:
        model = Testimonial
        fields = ["name", "role", "rating", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your Name"}),
            "role": forms.TextInput(attrs={"placeholder": "Your role & business (optional), e.g. Owner, Royal Stitch"}),
            "message": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "How was working with me? What did the website change for you?",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["rating"].choices = [
            (5, "★★★★★  Excellent"),
            (4, "★★★★  Very good"),
            (3, "★★★  Good"),
            (2, "★★  Fair"),
            (1, "★  Poor"),
        ]

        style_fields(self)

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
