function AudioBlock(runtime, element) {
    const audioElement = $(element).find('audio')[0];
    if (!audioElement || !audioElement.dataset) {
        console.error("Audio element or dataset is undefined.");
        return;
    }

    // these default to 0.0 if unset
    const startTime = parseFloat(audioElement.dataset.startTime);
    const endTime = parseFloat(audioElement.dataset.endTime);

    $(audioElement).mediaelementplayer({
        features: ['playpause', 'progress', 'volume', 'tracks', 'fullscreen'],
        startLanguage: 'en',
        success: function(mediaElement, originalNode) {
            mediaElement.setCurrentTime(startTime);

            mediaElement.addEventListener('timeupdate', function() {
                if (endTime > 0 && mediaElement.currentTime >= endTime) {
                    mediaElement.pause();
                    mediaElement.setCurrentTime(startTime);
                    mediaElement.stop();
                }
            });

            mediaElement.addEventListener('play', function() {
                if (mediaElement.currentTime < startTime || (endTime > 0 && mediaElement.currentTime >= endTime)) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('seeking', function() {
                if (mediaElement.currentTime < startTime || (endTime > 0 && mediaElement.currentTime >= endTime)) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('loadedmetadata', function() {
                if (endTime > 0) {
                    mediaElement.setCurrentTime(startTime);
                }
            });

            mediaElement.addEventListener('timeupdate', function() {
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
