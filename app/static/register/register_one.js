$(document).ready(function() {
    $('#register-one-form').submit(function(event) {
        var formData = {
            'date': $('input[name=date]').val(),
            'name': $('input[name=name]').val(),
            'name-id': $('input[name=name-id]').val(),
            'club': $('input[name=club]').val(),
            'club-id': $('input[name=club-id]').val(),
            'X-CSRF-TOKEN': $('meta[name=csrf-token]').attr("content")
        };
        $.ajax({
            type        : 'POST',
            url         : 'register_one_form',
            data        : formData,
            dataType    : 'json',
            encode      : true
        })
        .done(function(data) {
                if (!data.success) {
                    if (data.redir) {
                        window.location.replace(data.redir);
                    } else if (data.error){
                        FailurePopup(data.error, 5000);
                    } else {
                        FailurePopup("Something has gone wrong, failed to register student", 5000);
                    }
                } else {
                    SuccessPopup("Successfully registered student", 1000);
                    $('input[name=name]').val("");
                    $('input[name=name-id]').val("");
                    name_valid = false;
                }
            })
        .fail(function(jqXHR, textStatus, errorThrown) {
                FailurePopup("Something has gone wrong, failed to register student", 5000);
            });

        event.preventDefault();
    });

    name_valid = false;
    club_valid = false;
    $('#name').autocomplete({
        serviceUrl: '/api/names',
        onSelect: function (suggestion) {
            $('#name-id').val(suggestion.data)
            name_valid = true;
        },
        onInvalidateSelection: function () {
            if (name_valid) {
                $('#name').val("");
                $('#name-id').val("");
                name_valid = false;
            }
        }
    });
    $('#name').blur(function () {
        if (!name_valid) {
            $('#name').val("");
        }
    });
    $('#name').autocomplete().setOptions({minChars: 3, showNoSuggestionNotice: true})

    $('#club').autocomplete({
        serviceUrl: '/api/clubs',
        onSelect: function (suggestion) {
            $('#club-id').val(suggestion.data)
            club_valid = true;
        },
        onInvalidateSelection: function () {
            $('#club').val("");
            $('#club-id').val("");
            club_valid = false;
        }
    });
    $('#club').blur(function () {
        if (!club_valid) {
            $('#club').val("");
        }
    });
    $('#club').autocomplete().setOptions({minChars: 1, showNoSuggestionNotice: true});
});