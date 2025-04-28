from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "title",
            "description",
            "location",
            "status",
            "price_per_night",
            "representative_image",
            "hero_image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "status": forms.Select(choices=Item.STATUS_CHOICES),
            "price_per_night": forms.NumberInput(attrs={"step": "0.01"}),
        }
        labels = {
            "title": "Title",
            "description": "Description",
            "location": "Location",
            "status": "Status",
            "price_per_night": "Price per Night",
            "representative_image": "Thumbnail Image",
            "hero_image": "Hero Image",
        }
        help_texts = {
            "representative_image": "The thumbnail image for the item",
            "hero_image": "The main banner image for the item",
        }
