

/**
 * Sends an AJAX request to the server to update the user's session's persistent register.
 */
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

   performAJAXCall('GET', 'api/session/persistent-register', formData, function(response) {})
}


/**
 * Loads a register preset from the server
 *
 * @development
 */
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


/**
 * Hook for the 'register now' button which can be found next to names - registers all the students and organises the visual register.
 * 
 * @param  {event} event - The generated event
 */
function registerNowHook(event) {
    event.preventDefault();

    var row = event.originalEvent.srcElement.parentElement.parentElement;

    var date = document.getElementById('date');
    var club = document.getElementById('club');
    var club_id = document.getElementById('club-id');
    if (!date.checkValidity() || !club.checkValidity() || !club_id.checkValidity()) {
        FailurePopup("Please ensure the date and club name have been filled in before attempting to register", STANDARD_LONG_POPUP_TIME);
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

    performAJAXCall('POST', 'register_one_form', formData, function(response) {
        SuccessPopup("Successfully registered student", STANDARD_POPUP_TIME);
        row.remove();
        updateRegister();
    });
}


/**
 * Checks whether the register table has no entries left, and if so adds a terminal row saying there is no current entries.
 */
function addTerminalRow() {
    var table = document.getElementById("RegisterHolder");

    if ($('#RegisterHolder tr').length != 0) return;

    var row = table.insertRow(0);
    var cell = row.insertCell(0);
    cell.innerHTML = "No current entries";
    $('#RegisterHolder tr').attr("id", "terminal-row");
    $('#RegisterHolder tr td').attr("class", "text-muted text-center");
    $('#RegisterHolder tr td').attr("colspan", "4");
}


/**
 * Hook for the 'remove' button which can be found next to name - removes the student from the list.
 * 
 * @param  {event} - The generated event
 */
function removeHook(event) {
    // Remove the element
    var row = event.originalEvent.srcElement.parentElement.parentElement;
    row.remove();

    // Update the persistent register and inform user
    SuccessPopup("Successfully removed student", STANDARD_POPUP_TIME);
    updateRegister();

    // Add terminal row if needed
    addTerminalRow();
}


/**
 * Hook for the 'add name' button which adds a name to the register.
 * 
 * @param {event} event - The generated event
 */
function addNameHook(event) {
    event.preventDefault();
    var table = document.getElementById("RegisterHolder");

    var terminalRowActive = table.querySelector("#terminal-row") != null;
    if (terminalRowActive) {
        table.deleteRow(0);
    }

    for (let element of table.children) {
        var id = element.querySelector('#StudentID').children[0].innerHTML;
        if (id == $('input[name=name-id]').val()) {
            FailurePopup("Cannot add student to the register as they have already been added", STANDARD_POPUP_TIME);
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
}


/**
 * Takes the entire register and submits it to the server to be added to the records.
 * 
 * @param  {event} event - The generated event
 */
function registerAllHook(event) {
    event.preventDefault();

    var date = document.getElementById('date');
    var club = document.getElementById('club');
    var club_id = document.getElementById('club-id');
    if (!date.checkValidity() || !club.checkValidity() || !club_id.checkValidity()) {
        FailurePopup("Please ensure the date and club name have been filled in before attempting to register", STANDARD_LONG_POPUP_TIME);
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


    performAJAXCall('POST', 'register_class_form', formData, function(response) {
        var container = document.getElementById('RegisterHolder');
        container.innerHTML = '';
        SuccessPopup("Successfully registered students", 1000);
        updateRegister();
        addTerminalRow();
    });
}



$(document).ready(function() {
    // Register all the hooks
    $('#add-name-form').submit(addNameHook);

    $('#register-all').submit(registerAllHook);

    $('#load-preset').click(function(event) {
        var preset_to_load = $('#preset-name').val();
    });

    $('.register-now').submit(registerNowHook);
    $('.remove').submit(removeHook);
});