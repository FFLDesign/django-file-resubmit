# -*- coding: utf-8 -*-
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

import os, shutil, pickle
from os import path

# Django 1.9 removes support for django.core.cache.get_cache
try:
    from django.core.cache import get_cache
except ImportError:
    from django.core.cache import caches
    get_cache = lambda cache_name: caches[cache_name]

from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from django.conf import settings


def copy_file_obj(src, dest=None):
    d = dest or BytesIO()
    src_orig, d_orig = src.tell(), d.tell()
    shutil.copyfileobj(src, d)
    src.seek(src_orig)
    d.seek(d_orig)
    return dest or d.read()


class FileCache(object):
    def __init__(self, cache_name='file_resubmit'):
        self.cache_name = cache_name

    @property
    def backend(self):
        return get_cache(self.cache_name)

    def set(self, key, upload):
        state = {
            "name": upload.name,
            "size": upload.size,
            "content_type": upload.content_type,
            "charset": upload.charset,
            "content": copy_file_obj(upload.file)}
        self.backend.set(key, state)

    def get(self, key, field_name):
        upload = None
        state = self.backend.get(key)
        if state:
            f = BytesIO()
            f.write(state["content"])
            upload = InMemoryUploadedFile(
                file=f,
                field_name=field_name,
                name=state["name"],
                content_type=state["content_type"],
                size=state["size"],
                charset=state["charset"],
            )
            upload.file.seek(0)
        return upload

    def delete(self, key):
        self.backend.delete(key)


class MediaFileCache(object):
    """Store the uploaded files in MEDIA_ROOT so they can be referenced by web pages."""

    pickled_attributes = ['name', 'size', 'content_type', 'charset']

    def __init__(self, media_root=None, subdir='file_resubmit'):
        if media_root is None:
            media_root = settings.MEDIA_ROOT
        self.dir = path.abspath(path.join(media_root, subdir))
        if not path.exists(self.dir):
            os.mkdir(self.dir)

    def set(self, key, upload):
        kd = path.join(self.dir, key)
        assert not path.lexists(kd)
        os.mkdir(kd)  # TODO: Give a mode?
        with open(path.join(kd, 'content'), 'w') as f:
            copy_file_obj(upload.file, f)
        with open(path.join(kd, 'attributes'), 'w') as f:
            pickle.dump({a: getattr(upload, a) for a in self.pickled_attributes}, f)

    def get(self, key, field_name):
        kd = path.join(self.dir, key)
        if path.exists(kd):
            f = UploadedFile(file = open(path.join(kd, 'content')),
                             **pickle.load(open(path.join(kd, 'attributes'))))
            # Add this attribute so it's like InMemoryUploadedFile.
            f.field_name = field_name
            return f

    def delete(self, key):
        shutil.rmtree(path.join(self.dir, key))
