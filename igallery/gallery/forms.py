from django import forms

class SavedPhotosUploadForm(forms.Form):
    json_file = forms.FileField(label="Upload Saved Photos JSON") 