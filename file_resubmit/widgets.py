# -*- coding: utf-8 -*-

# TODO: This is still broken because Widgets are often only instantiated once
# per form class and so cannot be used to maintain multiple different states for
# multiple instances of a form.  Instead, maybe will try redesigning this to
# make value_from_datadict return a special type that holds the cache key so
# output_extra_data can access that from its argument, or something.

import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from .cache import FileCache, MediaFileCache

class ResubmitBaseWidget(ClearableFileInput):
    def __init__(self, attrs=None, cache=FileCache):
        super(ResubmitBaseWidget, self).__init__(attrs=attrs)
        self.called_value_from_datadict = 0
        self.input_name = None
        self.cache_key = ''
        self.cache = cache()

    def value_from_datadict(self, data, files, name):
        # Note: This can be called more than once.
        self.called_value_from_datadict += 1
        upload = super(ResubmitBaseWidget, self).value_from_datadict(
            data, files, name)
        if upload is False or upload == FILE_INPUT_CONTRADICTION:
            return upload

        input_name = "%s_cache_key" % name
        if not self.input_name:
            self.input_name = input_name
        else:
            assert input_name == self.input_name

        given_key = data.get(self.input_name)

        if upload:
            # A file is uploaded, so use it regardless if there was a previous.
            if self.called_value_from_datadict == 1:
                if self.cache_key:
                    self.cache.delete(self.cache_key)
                self.cache_key = self.random_key()
                self.cache.set(self.cache_key, upload)
        elif given_key:
            if self.cache_key:
                assert given_key == self.cache_key
            restored = self.cache.get(given_key, name)
            if restored:
                self.cache_key = given_key
                upload = restored
                files[name] = upload
        return upload

    def random_key(self):
        return uuid.uuid4().hex

    def output_extra_data(self, value):
        output = ''
        if self.cache_key:
            output += forms.HiddenInput().render(
                self.input_name,
                self.cache_key,
                {},
            )
        return output

    def filename_from_value(self, value):
        if value:
            return os.path.split(value.name)[-1]


class ResubmitFileWidget(ResubmitBaseWidget):
    template_with_initial = ClearableFileInput.template_with_initial
    template_with_clear = ClearableFileInput.template_with_clear

    def render(self, name, value, attrs=None):
        output = ClearableFileInput.render(self, name, value, attrs)
        output += self.output_extra_data(value)
        return mark_safe(output)


class ResubmitImageWidget(ResubmitFileWidget):
    pass


class MediaResubmitFileWidget(ResubmitFileWidget):
    def __init__(self, *pos, **kw):
        super(MediaResubmitFileWidget, self).__init__(cache=MediaFileCache, *pos, **kw)

class MediaResubmitImageWidget(ResubmitImageWidget):
    def __init__(self, *pos, **kw):
        super(MediaResubmitImageWidget, self).__init__(cache=MediaFileCache, *pos, **kw)
