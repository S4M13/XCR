
/**
 * Loads the data into the table for a given student
 * 
 * @param  {Number} student_id - Takes in the ID of the associated student to load the data for
 */
function getStudentsRecords(student_id) {
    var formData = {
        'student-id': student_id,
    };

    performAJAXCall('GET', '/api/student/fetch_records', formData, function(response) {
        configureTable(student_id, response)
    });
}


/**
 * Deletes a student's record for a given student, at a given club, at a given time.
 * 
 * @param  {Number} student_id - The ID of the associated student
 * @param  {Number} club_id - The ID of the associated club
 * @param  {string} timestamp - The timestamp of the attendance
 * @return {boolean} - Whether or not the deletion was successfull
 */
function deleteRecord(student_id, club_id, timestamp) {
    var formData = {
        'student-id': student_id,
        'club-id': club_id,
        'timestamp': timestamp,
        'X-CSRF-TOKEN': $('meta[name=csrf-token]').attr("content")
    };


    performAJAXCall('POST', '/api/student/delete_record', formData, function(response) {
        SuccessPopup("Successfully removed the record of attendance", STANDARD_POPUP_TIME)
    });

    return true;
}


/**
 * Clears the table from all of the current data
 */
function clearTable() {
    $("#records tr").remove();
}


/**
 * Takes in a student ID and their associated data and loads it into the table.
 * 
 * @param  {Number} student_id - The ID of the associated student
 * @param  {array} data - The data for the associated student from the server callback
 */
function configureTable(student_id, data) {
    $('.hidden').removeAttr("style");

    var table = document.getElementById("records");
    clearTable();

    var dates = data["data"]
    dates.forEach(function (record) {
        var row = table.insertRow(-1);

        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);
        var cell5 = row.insertCell(4);

        cell1.innerHTML = '<strong>' + student_id + '</strong>';
        cell2.innerHTML = '<strong>' + record[0] + '</strong>';
        cell3.innerHTML = '<strong>' + record[1] + '</strong>';
        cell4.innerHTML = '<strong>' + record[2] + '</strong>';
        cell5.innerHTML = '<form class="csrf-req delete-record" > <input name="student-id" type="hidden" value="' + student_id + '"> <input name="timestamp" type="hidden" value="' + record[1] + '"> <input name="club-id" type="hidden" value="' + record[3] + '"> <input type="submit" class="btn btn-danger" value="Delete"> </form>';
        cell5.style.textAlign = 'center';
    })

    $("#records tr").hide();
    $("#records tr").each(function(index){
        $(this).delay(index*50).show(1000);
    });

    $('.delete-record').submit(function(event) {
        event.preventDefault();

        var row = event.originalEvent.srcElement.parentElement.parentElement;
        var student_id = row.querySelector('.delete-record input[name=student-id]').value;
        var club_id = row.querySelector('.delete-record input[name=club-id]').value;
        var timestamp = row.querySelector('.delete-record input[name=timestamp]').value;

        if (deleteRecord(student_id, club_id, timestamp)) {
            $(row).fadeOut(2000);
        }
    });
}



$(document).ready(function() {
    // Load the on-click functionality for the student select button
    $('#student-select').submit(function(event) {
        event.preventDefault();

        var student = document.getElementById('name');
        if (!student.checkValidity()) {
            FailurePopup("Invalid student selection, please try again.", STANDARD_LONG_POPUP_TIME);
            return;
        }

        getStudentsRecords($('input[name=name-id]').val());

    });

});