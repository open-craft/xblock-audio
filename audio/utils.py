from django.conf import settings
from django.core.files.storage import default_storage as django_default_storage
from django.core.files.storage import storages


def get_path_mimetype(path):
    ipath = path.lower()
    if ipath.endswith(".mp3"):
        return "audio/mpeg"
    elif ipath.endswith(".wav"):
        return "audio/wav"
    elif ipath.endswith(".opus"):
        return "audio/opus"
    elif ipath.endswith((".ogg", ".oga")):
        return "audio/ogg"
    elif ipath.endswith(".m4a"):
        return "audio/mp4"

    return None


def get_storage_backend():
    storages_config = getattr(settings, "STORAGES", {})
    if "xblock_audio_storage" in storages_config:
        return storages["xblock_audio_storage"]
    return django_default_storage
