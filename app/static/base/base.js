function SuccessPopup(message, time) {
    $('#success-message').text(message)
    $('#success').modal('show');
    setTimeout(function () {
        $('#success').modal('hide');
    }, time);
}

function FailurePopup(message, time) {
    $('#failure-message').text(message)
    $('#failure').modal('show');
    setTimeout(function () {
        $('#failure').modal('hide');
    }, time);
}

$(document).ready(function(){
    $('.csrf-req').each(function(i, obj) {
        $('<input>').attr({
            type: 'hidden',
            name: 'X-CSRF-TOKEN',
            value: $('meta[name=csrf-token]').attr('content')
        }).appendTo(obj)
    });
});
