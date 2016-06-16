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

    return None
