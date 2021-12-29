
var attempts = 0;
function getStudentsRecords(student_id) {
    var formData = {
            'student-id': student_id,
        };

    $.ajax({
        type: 'GET',
        url: "/api/student/fetch_records",
        data: formData
    }).done(function(data) {
        if (!data.success) {
            if (data.redir) {
                window.location.replace(data.redir);
            } else if (data.error){
                FailurePopup(data.error, 5000);
                return null;
            } else {
                if (attempts < 5) {
                    FailurePopup("Something has gone wrong. Will automatically try again in a second.", 5000);
                    attempts += 1;
                    setTimeout(function () {
                        getStudentsRecords(student_id)
                    }, 6000);
                }else {
                    FailurePopup("Something has gone wrong. Please try again later.", 10000);
                }
                return null;
            }
        } else {
            attempts = 0;
            configureTable(student_id, data)
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        if (attempts < 5) {
            FailurePopup("Something has gone wrong. Will automatically try again in a second.", 10000);
            attempts += 1;
            setTimeout(function () {
                getStudentsRecords(student_id)
            }, 4000);
        }else {
            FailurePopup("Something has gone wrong. Please try again later.", 20000);
        }
        return null;
    });
}


function deleteRecord(student_id, club_id, timestamp) {
    var formData = {
        'student-id': student_id,
        'club-id': club_id,
        'timestamp': timestamp,
        'X-CSRF-TOKEN': $('meta[name=csrf-token]').attr("content")
    };

    return $.ajax({
        type        : 'POST',
        url         : '/api/student/delete_record',
        data        : formData,
        dataType    : 'json',
        encode      : true
    }).done(function(data) {
        if (!data.success) {
            if (data.redir) {
                window.location.replace(data.redir);
            } else if (data.error){
                FailurePopup(data.error, 5000);
                return false;
            } else {
                FailurePopup("Something has gone wrong. Please try again later.", 10000);
                return false;
            }
        } else {
            SuccessPopup("Successfully removed the record of attendance", 10000)
            return true;
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        FailurePopup("Something has gone wrong. Please try again later.", 20000);
        return false;
    });
}

function clearTable() {
    $("#records tr").remove();
}

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
    $('#student-select').submit(function(event) {
        console.log(1);
        event.preventDefault();

        var student = document.getElementById('name');
        if (!student.checkValidity()) {
            FailurePopup("Invalid student selection, please try again.");
            return;
        }

        getStudentsRecords($('input[name=name-id]').val());

    });


    name_valid = false;
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
});