function AudioBlock(runtime, element) {
    const audioElement = $(element).find('audio')[0];
    if (!audioElement || !audioElement.dataset) {
        console.error("Audio element or dataset is undefined.");
        return;
    }

    // these default to 0.0 if unset
    const startTime = parseFloat(audioElement.dataset.startTime);

    // calculate end time on the fly,
    // because it should be within the actual audio duration,
    // and the audio duration may not be available when the script initially runs.
    function getEndTime() {
      const endTime = parseFloat(audioElement.dataset.endTime);
      if (endTime == 0.0) {
        return 0.0;
      }

      const duration = audioElement.duration;
      if (!Number.isNaN(duration)) {
        return Math.min(duration, endTime);
      }

      return endTime;
    }

    $(audioElement).mediaelementplayer({
        features: ['playpause', 'progress', 'volume', 'tracks', 'fullscreen'],
        startLanguage: 'en',
        success: function(mediaElement, originalNode) {
            mediaElement.setCurrentTime(startTime);

            mediaElement.addEventListener('timeupdate', function() {
                const endTime = getEndTime();
                if (endTime > 0 && mediaElement.currentTime >= endTime) {
                    mediaElement.pause();
                    mediaElement.setCurrentTime(startTime);
                    mediaElement.stop();
                }
            });

            mediaElement.addEventListener('play', function() {
                const endTime = getEndTime();
                if (mediaElement.currentTime < startTime || (endTime > 0 && mediaElement.currentTime >= endTime)) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('seeking', function() {
                const endTime = getEndTime();
                if (mediaElement.currentTime < startTime || (endTime > 0 && mediaElement.currentTime >= endTime)) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('loadedmetadata', function() {
                const endTime = getEndTime();
                if (endTime > 0) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('timeupdate', function() {
                const endTime = getEndTime();
                if (endTime > 0) {
                    const playedPercent = (mediaElement.currentTime - startTime) / (endTime - startTime);
                    const progressBar = $(element).find('.mejs-time-current');
                    if (progressBar.length) {
                        progressBar.css('width', (playedPercent * 100) + '%');
                    }
                }
            });
        }
    });
}
