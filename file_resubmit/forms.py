import django.forms
from .widgets import ResubmitBaseWidget


class ResubmitImageField (django.forms.ImageField):

    def __init__(self, *pos, **kw):
        super(ResubmitImageField, self).__init__(*pos, **kw)
        assert isinstance(self.widget, ResubmitBaseWidget)

    def delete_cached(self, value):
        self.widget.cache.delete_by_value(value)
