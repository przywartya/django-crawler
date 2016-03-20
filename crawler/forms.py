from django import forms
from django.core.validators import URLValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class UrlForm(forms.Form):
	url = forms.CharField(label="",
	 					required=True,
	 					error_messages={'required': 'You need to give me an URL!'},
	 					widget=forms.TextInput(attrs={
	 							'placeholder': 'http://www.example.com',
								'class':'form-control'}))
	
	# pages = forms.IntegerField(label="",
	# 						required= False,
	# 						validators=[MaxValueValidator(100)], 
	# 						widget=forms.TextInput(attrs={
	# 								'placeholder': '~25',
	# 								'class':'narrow-select'}))
	def clean_url(self):
		url = self.cleaned_data.get('url')
		validate = URLValidator()
		if url.startswith("http://") or url.startswith("https://"):
			try:
				validate(url)
				return url
			except ValidationError:
				raise forms.ValidationError("This is not an URL.")
		else:
			try:
				url = 'http://'+ url
				validate(url)
				return url
			except ValidationError:
				raise forms.ValidationError("This is not an URL.")
