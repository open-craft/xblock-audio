# -*- coding: utf-8 -*-
from functools import partial
import logging
import pkg_resources
import os
from django.conf import settings
from django.utils.text import get_valid_filename
from django.core.files import File
from webob.response import Response

from xblock.core import XBlock
from xblock.fragment import Fragment

from .fields import AudioFields
from .utils import get_path_mimetype, get_storage_backend

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
        'transcript_file',
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

    def get_resolved_transcript_url(self):
        """
        Return the transcript url to be used (if present) for the xblock.
        """
        if self.transcript_url:
            return self.transcript_url
        elif self.transcript_file:
            return self.runtime.handler_url(self, 'transcript_file_handler')

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
                'transcript_file_url': self.runtime.handler_url(self, 'transcript_file_handler') if self.transcript_file else "",
                'transcript_file_name': os.path.basename(self.transcript_file) if self.transcript_file else "",
                'alt_transcript_file_url': self.runtime.handler_url(self, 'alt_transcript_file_handler') if self.alt_transcript_file else "",
                'alt_transcript_file_name': os.path.basename(self.alt_transcript_file) if self.alt_transcript_file else "",
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

        resolved_transcript_url = self.get_resolved_transcript_url()
        html = self.loader.render_django_template(
            'templates/html/audio.html', {
                'audio_id': self.audio_id,
                'sources': annotated_sources,
                'allow_audio_download': self.allow_audio_download,
                'audio_download_url': audio_download_url,
                'description': self.description,
                'resolved_transcript_url': resolved_transcript_url,
                'alt_transcript_url': self.runtime.handler_url(self, 'alt_transcript_file_handler') if self.alt_transcript_file else "",
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

        storage = get_storage_backend()
        will_upload_transcript_file = 'transcript_file' in data and hasattr(data.get('transcript_file'), 'file')

        if data.get("delete_transcript_file", "") == "on" or will_upload_transcript_file:
            if self.transcript_file and storage.exists(self.transcript_file):
                storage.delete(self.transcript_file)
            self.transcript_file = None

        if will_upload_transcript_file:
            transcript_file = data['transcript_file']

            # generate a safe path for the transcript file
            name = get_valid_filename(transcript_file.filename)
            safe_usage_key = get_valid_filename(self.usage_key)
            file_path = f"{safe_usage_key}/transcripts/{name}"
            storage.save(file_path, File(transcript_file.file))
            self.transcript_file = file_path

        will_upload_alt_transcript_file = 'alt_transcript_file' in data and hasattr(data.get('alt_transcript_file'), 'file')

        if data.get("delete_alt_transcript_file", "") == "on" or will_upload_alt_transcript_file:
            if self.alt_transcript_file and storage.exists(self.alt_transcript_file):
                storage.delete(self.alt_transcript_file)
            self.alt_transcript_file = None

        if will_upload_alt_transcript_file:
            alt_transcript_file = data['alt_transcript_file']

            # generate a safe path for the alt_transcript file
            name = get_valid_filename(alt_transcript_file.filename)
            safe_usage_key = get_valid_filename(self.usage_key)
            file_path = f"{safe_usage_key}/alt_transcripts/{name}"
            storage.save(file_path, File(alt_transcript_file.file))
            self.alt_transcript_file = file_path

        return Response(json_body={'result': 'success'})

    @XBlock.handler
    def transcript_file_handler(self, request, suffix=''):
        BLOCK_SIZE = 2 ** 10 * 8  # 8kb
        storage = get_storage_backend()
        path = self.transcript_file

        if path:
            try:
                return Response(
                    app_iter=iter(partial(storage.open(path).read, BLOCK_SIZE), b""),
                    content_type='text/vtt',
                    content_disposition=f"attachment; filename*=UTF-8''{os.path.basename(path)}",
                )
            except OSError:
                pass

        return Response("file not found", status_code=404)

    @XBlock.handler
    def alt_transcript_file_handler(self, request, suffix=''):
        BLOCK_SIZE = 2 ** 10 * 8  # 8kb
        storage = get_storage_backend()
        path = self.alt_transcript_file

        if path:
            try:
                return Response(
                    app_iter=iter(partial(storage.open(path).read, BLOCK_SIZE), b""),
                    content_type='application/octet-stream',
                    content_disposition=f"attachment; filename*=UTF-8''{os.path.basename(path)}",
                )
            except OSError:
                pass

        return Response("file not found", status_code=404)
