# -*- coding: utf-8 -*-
import logging

from xblock.core import XBlock
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

from .fields import AudioFields
from .utils import get_path_mimetype


log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


@XBlock.needs('i18n')
class AudioBlock(AudioFields, StudioEditableXBlockMixin, XBlock):
    # Styling and asset controls.
    icon_class = 'audio'
    js_module_name = "Audio"

    editable_fields = ('sources', 'allow_audio_download')


    def student_view(self, context):
      """
      Player view, displayed to the student
      """

      sources = filter(None, self.sources.split('\n')) if self.sources else ''
      audio_download_url = sources[0] if sources else None

      # Add the MIME type if we think we know it.
      annotated_sources = []
      for source in sources:
          type = get_path_mimetype(source)

          annotated_sources.append((source, type))

      fragment = Fragment()
      fragment.add_content(loader.render_mako_template(
        'templates/html/audio.html', {
          'audio_id': self.audio_id,
          'sources': annotated_sources,
          'allow_audio_download': self.allow_audio_download,
          'audio_download_url': audio_download_url
        }))
      fragment.add_css_url(self.runtime.local_resource_url(self, 'public/css/audio.css'))

      return fragment
