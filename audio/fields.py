from xblock.fields import Scope, String, List, Boolean, UNIQUE_ID
from xblock.validation import ValidationMessage

from urlparse import urlparse

# Override '_' so they can be scraped for translations.
_ = lambda text: text

class AudioFields(object):
    audio_id = String(
        default=UNIQUE_ID,
        scope=Scope.settings,
    )

    display_name = String(
        help=_(u"The name students see. This name appears in the course ribbon and as a header for the video."),
        display_name=_(u"Component Display Name"),
        default=_(u"Audio"),
        scope=Scope.settings,
    )

    sources = String(
        help=_(u"The URL or URLs where the audio files are located.  We recommend to at least provide an MP3 version and Ogg Vorbis version of the audio, which will provide maximum browser capability.  Alternative formats, such as AAC/M4A and WAVE, are typically supported by most browsers, but may not provide the best file size."),  # pylint: disable=line-too-long
        display_name=_(u"Audio File URLs"),
        default='',
        scope=Scope.settings,
        multiline_editor=True,
    )

    allow_audio_download = Boolean(
        help=_(u"Allow students to download the source audio file.  If enabled, the first source URL specified will be used."),
        display_name=_(u"Audio Download Allowed"),
        scope=Scope.settings,
        default=True,
    )

    def validate_field_data(self, validation, data):
        """
        Ensure we've been passed legitimate values, particularly for the audio URLs.
        """
        if data.sources is None:
            validation.add(ValidationMessage(ValidationMessage.ERROR, _(u"You must specify at least one source URL!")))
        else:
            sources = filter(None, data.sources.split('\n'))
            if len(sources) == 0:
                validation.add(ValidationMessage(ValidationMessage.ERROR, _(u"You must specify at least one source URL!")))
            else:
                for source in sources:
                    # Parse the string to see if it's a URL.  It has to, at least, have a path, which could
                    # mean it's a relative `/static/` URL.
                    _scheme, _netloc, path, _params, _qs, _fragment = urlparse(source)
                    if path is None:
                        validation.add(ValidationMessage(ValidationMessage.ERROR, _(u"Invalid URL '") + unicode(source) + _(u"' entered.")))
