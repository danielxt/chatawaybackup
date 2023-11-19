from django.forms import ModelForm
from . import Data
class DataForm(ModelForm):
    class Meta:
        model = Data
