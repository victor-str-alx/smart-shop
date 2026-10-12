from django import forms
from .models import Review


class RatingForm(forms.Form):
    score = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        label="Alege un rating (1-5)",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "content"]
        labels = {
            "rating": "Rating (1-5 stele)",
            "title": "Titlu review",
            "content": "Review-ul tău",
        }
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} ★") for i in range(1, 6)],
                attrs={"class": "form-select"}
            ),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Rezumă experiența ta..."
            }),
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Scrie un review detaliat..."
            }),
        }
