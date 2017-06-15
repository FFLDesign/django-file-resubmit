# -*- coding: utf-8 -*-

import os
import uuid

from django import forms
from django.forms.widgets import FILE_INPUT_CONTRADICTION
from django.forms import ClearableFileInput
from django.utils.safestring import mark_safe

from .cache import FileCache, MediaFileCache

class ResubmitBaseWidget(ClearableFileInput):

    cache_key_input_suffix = '_cache_key'

    # Note the strangeness that, per Django's design for form fields and
    # widgets, new instances of this class are created by shallow-copying
    # prototype instances declared for form class fields, and __init__ is rarely
    # called usually only for form class declarations.
    def __init__(self, attrs=None, cache=FileCache, show_filename=False):
        super(ResubmitBaseWidget, self).__init__(attrs=attrs)
        self.cache = cache()
        self.show_filename = show_filename

    def cache_key_input_name(self, name):
        return name + self.cache_key_input_suffix

    def value_from_datadict(self, data, files, name):
        # Note: This can be called more than once for the same field of a form instance.
        upload = super(ResubmitBaseWidget, self).value_from_datadict(
            data, files, name)
        if upload is False or upload == FILE_INPUT_CONTRADICTION:
            return upload
        if hasattr(upload, '_file_resubmit'):
            # value_from_datadict is being called again for the same
            # arguments.  We already handled it the first time.
            return upload

        given_key = data.get(self.cache_key_input_name(name))

        if upload:
            # A file is uploaded, so use it regardless if there is a given_key for a previous.
            cache_key = self.random_key()
            self.cache.set(cache_key, upload)
            if given_key:
                self.cache.delete(given_key)
        elif given_key:
            restored = self.cache.get(given_key, name)
            if restored:
                cache_key = given_key
                upload = restored
                files[name] = upload

        if upload:
            # Add a new attribute to the "value" object for output_extra_data to use.
            upload._file_resubmit = {'name': name, 'cache_key': cache_key}
        return upload

    def random_key(self):
        # It is important that the keys be unguessable to thwart malicious users.
        return uuid.uuid4().hex

    def output_extra_data(self, value):
        output = ''
        if hasattr(value, '_file_resubmit'):
            if self.show_filename:
                output += ' ' + self.filename_from_value(value)
            output += forms.HiddenInput().render(
                self.cache_key_input_name(value._file_resubmit['name']),
                value._file_resubmit['cache_key'],
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
        self.media_subdir = self.cache.subdir

class MediaResubmitImageWidget(ResubmitImageWidget):
    def __init__(self, *pos, **kw):
        super(MediaResubmitImageWidget, self).__init__(cache=MediaFileCache, *pos, **kw)
        self.media_subdir = self.cache.subdir
