from django import forms

from .services import GENRE_IDS, PROVIDER_IDS


class MovieSearchForm(forms.Form):
    query = forms.CharField(
        label="Movie title",
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={"placeholder": "Try Inception"}
        ),
    )

    genre = forms.ChoiceField(
        required=False,
        choices=[("", "All genres")] + [
            (name, name.title()) for name in GENRE_IDS
        ],
    )

    year = forms.RegexField(
        label="Release year",
        regex=r"^[0-9]{4}$",
        required=False,
        error_messages={
            "invalid": "Enter a four-digit year."
        },
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "placeholder": "2010",
            }
        ),
    )

    min_rating = forms.FloatField(
        label="Minimum rating",
        required=False,
        min_value=0,
        max_value=10,
        widget=forms.NumberInput(
            attrs={
                "step": "0.1",
                "placeholder": "0–10",
            }
        ),
    )

    provider = forms.ChoiceField(
        label="Streaming service (US)",
        required=False,
        choices=[("", "Any service")] + [(name, name) for name in PROVIDER_IDS],
    )
