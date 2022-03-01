

/**
 * Takes a single student and requests the server to register them at a certain club, at a certain time.
 * 
 * @param  {event} event - The generated event
 * @return {[type]}
 */
function registerOneHook(event) {
    event.preventDefault();

    var formData = {
        'date': $('input[name=date]').val(),
        'name': $('input[name=name]').val(),
        'name-id': $('input[name=name-id]').val(),
        'club': $('input[name=club]').val(),
        'club-id': $('input[name=club-id]').val(),
        'X-CSRF-TOKEN': $('meta[name=csrf-token]').attr("content")
    };

    performAJAXCall('POST', 'register_one_form', formData, function(response) {
        SuccessPopup("Successfully registered student", STANDARD_POPUP_TIME);
        $('input[name=name]').val("");
        $('input[name=name-id]').val("");
        name_valid = false;
    });
}


$(document).ready(function() {
    // Register the hook
    $('#register-one-form').submit(registerOneHook);
});