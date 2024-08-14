function AudioBlockStudio(runtime, element) {
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
                window.location.reload();
            }
        });
    });

    $(element).find('.cancel-button').bind('click', function () {
        if ('notify' in runtime) { //xblock workbench runtime does not have `notify` method
            runtime.notify('cancel', {});
        }
    });

    var sourcesField = document.getElementById('sources');
    var embedUrlField = document.getElementById('embed_url');
    var startTimeCheckbox = document.getElementById('start_time_checkbox');
    var timeFields = document.getElementById('time_fields');

    // Remove the existing openTab function and add the showContent function
    window.showContent = function(contentType) {
        var audioTab = document.getElementById('audioTab');
        var podcastTab = document.getElementById('podcastTab');

        if (contentType === 'audioTab') {
            audioTab.style.display = 'block';
            podcastTab.style.display = 'none';
        } else if (contentType === 'podcastTab') {
            podcastTab.style.display = 'block';
            audioTab.style.display = 'none';
        }
    }

    // Initialize the "Audio files" content by default
    showContent('audioTab');
    document.getElementById("audioRadio").checked = true;


    // Handle mutual exclusivity
    sourcesField.addEventListener('input', function() {
        if (sourcesField.value.trim() !== '') {
            embedUrlField.disabled = true;
        } else {
            embedUrlField.disabled = false;
        }
    });

    embedUrlField.addEventListener('input', function() {
        if (embedUrlField.value.trim() !== '') {
            sourcesField.disabled = true;
        } else {
            sourcesField.disabled = false;
        }
    });

    // Handle start time checkbox
    startTimeCheckbox.addEventListener('change', function() {
        if (startTimeCheckbox.checked) {
            timeFields.style.display = "block";
        } else {
            timeFields.style.display = "none";
        }
    });
}
