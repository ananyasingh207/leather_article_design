from django import forms
from .models import Design


class DesignForm(forms.ModelForm):
    """
    Form for configuring a leather article in the Design Studio.
    User and Article are assigned in the view, not exposed in form fields.
    """
    clear_logo = forms.BooleanField(
        required=False,
        label="Remove existing logo",
        widget=forms.CheckboxInput(attrs={
            'id': 'id_clear_logo',
            'class': 'form-check-input',
        })
    )

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
            'logo',
            'custom_text',
            'font',
            'text_size',
            'position_x',
            'position_y',
            'rotation',
            'selected_side',
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
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'id_logo',
                'accept': 'image/png, image/jpeg, image/jpg',
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
            'position_x': forms.HiddenInput(attrs={
                'id': 'id_position_x',
            }),
            'position_y': forms.HiddenInput(attrs={
                'id': 'id_position_y',
            }),
            'rotation': forms.HiddenInput(attrs={
                'id': 'id_rotation',
            }),
            'selected_side': forms.HiddenInput(attrs={
                'id': 'id_selected_side',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['position_x', 'position_y', 'rotation', 'selected_side', 'logo']:
            if field in self.fields:
                self.fields[field].required = False

    def clean_logo(self):
        import os
        from PIL import Image
        logo = self.cleaned_data.get('logo')
        if logo and hasattr(logo, 'file'):
            ext = os.path.splitext(logo.name)[1].lower()
            valid_extensions = ['.png', '.jpg', '.jpeg']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file format. Please upload a PNG or JPEG image.")

            try:
                img = Image.open(logo)
                img.verify()
                if img.format.lower() not in ['png', 'jpeg']:
                    raise forms.ValidationError("Invalid image content. Only PNG and JPEG images are allowed.")
            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError("The uploaded file is not a valid image.")
            finally:
                if hasattr(logo, 'seek'):
                    logo.seek(0)
        return logo

    def save(self, commit=True):
        design = super().save(commit=False)
        if self.cleaned_data.get('clear_logo') and not (self.files and self.files.get('logo')):
            design.logo = None
        if commit:
            design.save()
        return design

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

    def clean_position_x(self):
        val = self.cleaned_data.get('position_x')
        if val is None:
            return 50
        return val

    def clean_position_y(self):
        val = self.cleaned_data.get('position_y')
        if val is None:
            return 50
        return val

    def clean_rotation(self):
        val = self.cleaned_data.get('rotation')
        if val is None:
            return 0
        return val

    def clean_selected_side(self):
        val = self.cleaned_data.get('selected_side')
        if not val:
            return Design.SIDE_FRONT
        return val

