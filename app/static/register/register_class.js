function updateRegister() {
    var students = [];
    var student_ids = [];

    var container = document.getElementById('RegisterHolder');

    for (let element of container.children) {
        var name = element.querySelector('#StudentName').children[0].innerHTML;
        var id = element.querySelector('#StudentID').children[0].innerHTML;
        students.push(name);
        student_ids.push(id)
    }

    var formData = {
        'students': students,
        'student-ids': student_ids
   }

    $.ajax({
        type        : 'GET',
        url         : 'api/session/persistent-register',
        data        : formData,
        dataType    : 'json',
        encode      : true
    }).done(function(data) {
        if (data.redir) {
            window.location.replace(data.redir);
        } else if (data.error){
            FailurePopup(data.error, 5000);
            return null;
        }
    });
}

function registerNowHook(event) {
    event.preventDefault();

    var row = event.originalEvent.srcElement.parentElement.parentElement;

    var date = document.getElementById('date');
    var club = document.getElementById('club');
    var club_id = document.getElementById('club-id');
    if (!date.checkValidity() || !club.checkValidity() || !club_id.checkValidity()) {
        FailurePopup("Please ensure the date and club name have been filled in before attempting to register", 2000);
        return;
    }

    var formData = {
        'date': $('input[name=date]').val(),
        'name': row.querySelector('#StudentName').children[0].innerHTML,
        'name-id': row.querySelector('#StudentID').children[0].innerHTML,
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
            row.remove();
            updateRegister();
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        FailurePopup("Something has gone wrong, failed to register student", 5000);
    });

}

function removeHook(event) {
    var row = event.originalEvent.srcElement.parentElement.parentElement;
    row.remove();
    SuccessPopup("Successfully removed student", 1000);
    updateRegister();

    var table = document.getElementById("RegisterHolder");
    if ($('#RegisterHolder tr').length == 0) {
        var row = table.insertRow(0);
        var cell = row.insertCell(0);
        cell.innerHTML = "No current entries";
        $('#RegisterHolder tr').attr("id", "terminal-row");
        $('#RegisterHolder tr td').attr("class", "text-muted text-center");
        $('#RegisterHolder tr td').attr("colspan", "4");
    }
}

function loadPreset(preset_id) {
    var formData = {
        'students': students,
        'student-ids': student_ids
   }

    $.ajax({
        type        : 'GET',
        url         : 'api/session/persistent-register',
        data        : formData,
        dataType    : 'json',
        encode      : true
    }).done(function(data) {
        if (data.redir) {
            window.location.replace(data.redir);
        } else if (data.error){
            FailurePopup(data.error, 5000);
            return null;
        }
    });
}

$(document).ready(function() {
    $('#add-name-form').submit(function(event) {
        event.preventDefault();
        var table = document.getElementById("RegisterHolder");

        var terminalRowActive = table.querySelector("#terminal-row") != null;
        if (terminalRowActive) {
            table.deleteRow(0);
        }

        for (let element of table.children) {
            var id = element.querySelector('#StudentID').children[0].innerHTML;
            if (id == $('input[name=name-id]').val()) {
                FailurePopup("Cannot add student to the register as they have already been added", 2000);
                return;
            }
        }

        var row = table.insertRow(0);

        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);

        cell1.innerHTML = '<strong>' + $('input[name=name-id]').val() + '</strong>';
        cell2.innerHTML = '<strong>' + $('input[name=name]').val() + '</strong>';
        cell3.innerHTML = '<form class="register-now"> <input type="submit" class="btn btn-info" value="Register Now"> </form>'
        cell4.innerHTML = '<form class="remove"> <input type="submit" class="btn btn-danger" value="Remove"> </form>'

        cell3.style.textAlign = 'center';
        cell4.style.textAlign = 'center';

        cell1.id = "StudentID"
        cell2.id = "StudentName"

        event.preventDefault();
        $('input[name=name]').val("");
        $('input[name=name-id]').val("");
        name_valid = false;

        $('.register-now').submit(registerNowHook);
        $('.remove').submit(removeHook);
        updateRegister();
    });

    $('#register-all').submit(function(event) {
        event.preventDefault();

        var date = document.getElementById('date');
        var club = document.getElementById('club');
        var club_id = document.getElementById('club-id');
        if (!date.checkValidity() || !club.checkValidity() || !club_id.checkValidity()) {
            FailurePopup("Please ensure the date and club name have been filled in before attempting to register", 2000);
            return;
        }

        var students = [];
        var student_ids = [];

        var container = document.getElementById('RegisterHolder');

        for (let element of container.children) {
            var name = element.querySelector('#StudentName').children[0].innerHTML;
            var id = element.querySelector('#StudentID').children[0].innerHTML;
            students.push(name);
            student_ids.push(id)
        }


       var formData = {
            'date': $('input[name=date]').val(),
            'students': students,
            'student-ids': student_ids,
            'club': $('input[name=club]').val(),
            'club-id': $('input[name=club-id]').val(),
            'X-CSRF-TOKEN': $('meta[name=csrf-token]').attr("content")
       }

        $.ajax({
            type        : 'POST',
            url         : 'register_class_form',
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
                var container = document.getElementById('RegisterHolder');
                container.innerHTML = '';
                SuccessPopup("Successfully registered students", 1000);
                updateRegister();
            }
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            FailurePopup("Something has gone wrong, failed to register students", 5000);
        });
    });

    $('#load-preset').click(function(event) {
        var preset_to_load = $('#preset-name').val();
        console.log(preset_to_load);
    });

    name_valid = false;
    club_valid = false;
    $('#name').autocomplete({
        serviceUrl: '/api/names',
        autoSelectFirst: true,
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
        autoSelectFirst: true,
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

    $('.register-now').submit(registerNowHook);
    $('.remove').submit(removeHook);
});