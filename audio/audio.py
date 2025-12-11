# -*- coding: utf-8 -*-
import logging
import pkg_resources
from django.conf import settings
from webob.response import Response

from xblock.core import XBlock
from xblock.fragment import Fragment

from .fields import AudioFields
from .utils import get_path_mimetype

try:
    from xblock.utils.studio_editable import StudioEditableXBlockMixin, StudioContainerXBlockMixin
except ModuleNotFoundError:  # For compatibility with Palm and earlier
    from xblockutils.studio_editable import StudioEditableXBlockMixin, StudioContainerXBlockMixin

try:
    from xblock.utils.resources import ResourceLoader
except ModuleNotFoundError:  # For compatibility with releases older than Quince.
    from xblockutils.resources import ResourceLoader



log = logging.getLogger(__name__)


def convert_seconds_to_time(seconds):
    """Convert total seconds to the format MM:SS."""
    # It's stored as a float in the xblock, but treated as an int.
    seconds = int(seconds)
    return f"{seconds // 60:02}:{seconds % 60:02}"


@XBlock.needs('i18n')
class AudioBlock(AudioFields, StudioEditableXBlockMixin, StudioContainerXBlockMixin, XBlock):
    icon_class = 'other'
    loader = ResourceLoader(__name__)

    editable_fields = (
        'sources',
        'allow_audio_download',
        'description',
        'transcript_url',
        'embed_url',
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def convert_time_to_seconds(self, time_str):
        """Convert a time string in the format MM:SS to total seconds."""
        try:
            minutes, seconds = time_str.split(":")
            return int(minutes) * 60 + int(seconds)
        except ValueError:
            return 0.0

    def studio_view(self, context):
        """
        View for editing the XBlock settings in Studio
        """
        html = self.loader.render_django_template(
            'templates/html/audio_edit.html', {
                'description': self.description,
                'sources': self.sources,
                'embed_url': self.embed_url,
                'transcript_url': self.transcript_url or "",
                'alt_transcript_url': self.alt_transcript_url,
                'allow_audio_download': self.allow_audio_download,
                'start_time': convert_seconds_to_time(self.start_time),
                'end_time': convert_seconds_to_time(self.end_time),
            }
        )

        fragment = Fragment(html)
        fragment.add_css_url(self.runtime.local_resource_url(self, 'public/css/audio.css'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/audio_edit.js'))
        fragment.initialize_js('AudioBlockStudio')
        return fragment

    def student_view(self, context):
        """
        Player view, displayed to the student
        """
        sources = list(filter(None, self.sources.split('\n')) if self.sources else '')
        audio_download_url = sources[0] if sources else None

        # Add the MIME type if we think we know it.
        annotated_sources = []
        for source in sources:
            type = get_path_mimetype(source)
            annotated_sources.append((source, type))

        html = self.loader.render_django_template(
            'templates/html/audio.html', {
                'audio_id': self.audio_id,
                'sources': annotated_sources,
                'allow_audio_download': self.allow_audio_download,
                'audio_download_url': audio_download_url,
                'description': self.description,
                'transcript_url': self.transcript_url,
                'alt_transcript_url': self.alt_transcript_url,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'embed_url': self.embed_url
            })

        fragment = Fragment(html)
        fragment.add_css_url(self.runtime.local_resource_url(self, 'public/css/audio.css'))
        fragment.add_css_url(self.runtime.local_resource_url(self, 'public/css/mediaelement.player.min.css'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/mediaelement.player.min.js'))
        fragment.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/audio.js'))

        fragment.initialize_js("AudioBlock")

        return fragment


    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        """
        Handle studio form submissions
        """
        data = request.POST
        self.description = data.get('description', "")
        self.sources = data.get('sources')
        self.allow_audio_download = data.get('allow_audio_download') == 'true'
        self.start_time = float(self.convert_time_to_seconds(data.get('start_time', '00:00')))
        self.end_time = float(self.convert_time_to_seconds(data.get('end_time', '00:00')))
        self.embed_url = data.get('embed_url', '') if not data.get('sources', '') else ''
        self.transcript_url = data.get('transcript_url')
        self.alt_transcript_url = data.get('alt_transcript_url')

        return Response(json_body={'result': 'success'})
