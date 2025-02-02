import json
import re
from datetime import datetime
from urllib import urlencode
from urllib2 import urlopen

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class BasicQueryForm(forms.Form):
    position = forms.CharField(widget=forms.TextInput(
            attrs={'placeholder':'Position'}))
    main_categories = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple(), required=False)

    def __init__(self, *args, **kwargs):
        super(BasicQueryForm, self).__init__(*args, **kwargs)

        # TODO - Generalize this request on the utils.py file
        request_data = {
            'oauth_token': settings.OAUTH_FOURSQUARE,
            'v': datetime.now().strftime("%Y%m%d"),
        }
        url = '%s/venues/categories?%s' % (
            settings.BASE_FOURSQUARE_URL, urlencode(request_data))
        categories = [
            (x['id'], x['name']) for x in
            json.loads(urlopen(url).readlines()[0])['response']['categories']]
        self.fields['main_categories'].choices = categories

    def clean(self):
        isdigit = lambda x: re.search('^-?\d+((\.|,)\d+)?$', x)
        cleaned_data = self.cleaned_data
        ll = cleaned_data['position'].replace(' ', '').split(',')

        if len(ll) != 2 or not isdigit(ll[0]) or not isdigit(ll[1]):
            raise forms.ValidationError(
                _('The given position value is not valid'))
        return cleaned_data
