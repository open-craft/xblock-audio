function AudioBlockStudio(runtime, element) {
    $(element).find('.save-button').click(function(event) {
        event.preventDefault();
        $(element).find('form').submit();
    });

    $(element).find('form').submit(function(event) {
        event.preventDefault();
        var data = new FormData($(this).get(0));
        runtime.notify('save', {state: 'start'});

        $.ajax({
            url: runtime.handlerUrl(element, 'studio_submit'),
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(response) {
                runtime.notify('save', {state: 'end'});
            }
        });
    });

    $(element).find('.cancel-button').bind('click', function () {
        if ('notify' in runtime) { //xblock workbench runtime does not have `notify` method
            runtime.notify('cancel', {});
        }
    });

    window.audioSwitchType = function(tab) {
        if (tab === 'audio-tab') {
            $('#audio-tab').show();
            $('#podcast-tab').hide();

            // Reset podcast-tab fields when switching to audio type
            $('#embed-url').val('');
        } else if (tab === 'podcast-tab') {
            $('#audio-tab').hide();
            $('#podcast-tab').show();

            // Reset audio-tab fields when switching to podcast type
            $('#start-time').val('00:00');
            $('#end-time').val('00:00');
            $('#sources').val('');
            $('#transcript-file').val('');
            $('#transcript-url').val('');
            $('#allow-audio-download').val('true');
            $('#start-time-checkbox').prop('checked', false);
        }
    }

    $('#start-time-checkbox').on('change', function() {
        if ($('#start-time-checkbox').is(':checked')) {
            $('#time-fields').show();
        } else {
            $('#time-fields').hide();
            $('#start-time').val('00:00');
            $('#end-time').val('00:00');
        }
    });
}
