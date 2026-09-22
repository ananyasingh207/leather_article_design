from django import forms
from .models import Design


class DesignForm(forms.ModelForm):
    """
    Form for configuring a leather article in the Design Studio.
    User and Article are assigned in the view, not exposed in form fields.
    """
    class Meta:
        model = Design
        fields = [
            'name',
            'leather_type',
            'leather_color',
            'leather_finish',
            'width',
            'height',
            'depth',
            'stitching_color',
            'custom_text',
            'font',
            'text_size',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Classic Brown Bi-Fold Wallet',
                'id': 'id_name',
                'autocomplete': 'off',
                'required': True,
            }),
            'leather_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_leather_type',
            }),
            'leather_color': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_leather_color',
            }),
            'leather_finish': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_leather_finish',
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Width in cm (e.g. 11.5)',
                'id': 'id_width',
                'step': '0.1',
                'min': '0.1',
                'max': '500.0',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height in cm (e.g. 9.0)',
                'id': 'id_height',
                'step': '0.1',
                'min': '0.1',
                'max': '500.0',
            }),
            'depth': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Depth in cm (e.g. 2.0)',
                'id': 'id_depth',
                'step': '0.1',
                'min': '0.1',
                'max': '500.0',
            }),
            'stitching_color': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_stitching_color',
            }),
            'custom_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional embossed initials or brand name',
                'id': 'id_custom_text',
                'maxlength': '100',
                'autocomplete': 'off',
            }),
            'font': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_font',
            }),
            'text_size': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_text_size',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Design name is required.")
        return name

    def clean_width(self):
        width = self.cleaned_data.get('width')
        if width is None or width <= 0:
            raise forms.ValidationError("Width must be greater than zero.")
        return width

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height is None or height <= 0:
            raise forms.ValidationError("Height must be greater than zero.")
        return height

    def clean_depth(self):
        depth = self.cleaned_data.get('depth')
        if depth is None or depth <= 0:
            raise forms.ValidationError("Depth must be greater than zero.")
        return depth
