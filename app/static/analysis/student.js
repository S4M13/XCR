var attempts = 0;
function configure_chart(chart_id, chart_type, chart_options, endpoint, args) {
    $.ajax({
        type: 'GET',
        url: endpoint,
        data: args
    }).done(function(data) {
        if (!data.success) {
            if (data.redir) {
                window.location.replace(data.redir);
            } else if (data.error){
                FailurePopup(data.error, 5000);
                return null;
            } else {
                if (attempts < 5) {
                    FailurePopup("Something has gone wrong, failed to load chart data. Will automatically try again in a second.", 5000);
                    attempts += 1;
                    setTimeout(function () {
                        configure_chart(chart_id, chart_type, chart_options, endpoint, args)
                    }, 6000);
                }else {
                    FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 10000);
                }
                return null;
            }
        } else {
            var config = {
                type: chart_type,
                options: chart_options,
                data: data
            }

            var ctx = document.getElementById(chart_id).getContext("2d");
            new Chart(ctx, config);

            attempts = 0;
        }
    }).fail(function(jqXHR, textStatus, errorThrown) {
        if (attempts < 5) {
            FailurePopup("Something has gone wrong, failed to load chart data. Will automatically try again in a second.", 10000);
            attempts += 1;
            setTimeout(function () {
                configure_chart(chart_id, chart_type, chart_options, endpoint, args)
            }, 4000);
        }else {
            FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
        }
        return null;
    });
}

function reset_all_canvas() {
    $('#Attendance').remove();
    $('#Attendance-Holder').append('<canvas id="Attendance"><canvas>');

    $('#ClubBreakdown').remove();
    $('#ClubBreakdown-Holder').append('<canvas id="ClubBreakdown"><canvas>');

    $('#ClubBarChart').remove();
    $('#ClubBarChart-Holder').append('<canvas id="ClubBarChart"><canvas>');
}

$(document).ready(function() {
    $('#student-select').submit(function(event) {
        event.preventDefault();
        $('.hidden').removeAttr("style");
        $('#generate-analysis').attr("href", "/generate-student?student-id=" + $('input[name=name-id]').val());
        var formData = {
            'name': $('input[name=name]').val(),
            'name-id': $('input[name=name-id]').val()
        };

        reset_all_canvas();

        var options = {
            responsive: true,
            maintainAspectRatio: false,
            title: {
              display: true,
              text: 'Weekly Attendance'
            },
            tooltips: {
              mode: 'label',
            },
            hover: {
              mode: 'nearest',
              intersect: true
            },
            scales: {
              xAxes: [{
                display: true,
                gridLines: {
                  display: true,
                  color: '#101010'
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Week-Year'
                }
              }],
              yAxes: [{
                display: true,
                gridLines: {
                  display: true,
                  color: '#101010'
                },
                scaleLabel: {
                  display: true,
                  labelString: 'Attendance'
                },
                ticks: {
                    beginAtZero: true
                }
              }],
            }
          }
        configure_chart("Attendance", "line", options, "api/student/weekly-attendance", formData)
        var options = {
          title: {
            display: true,
            text: 'Club Attendance Distribution'
          },
          maintainAspectRatio: false
        }
        configure_chart("ClubBreakdown", "doughnut", options, "api/student/club-breakdown", formData)
        var options = {
            responsive: true,
            tooltips: {
              mode: 'label',
            },
            hover: {
              mode: 'nearest',
              intersect: true
            },
            title: {
                display: true,
                text: 'Club Attendance'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },
            maintainAspectRatio: false
        }
        configure_chart("ClubBarChart", "bar", options, "api/student/club-bar-chart", formData)

        //Custom statistics
        $.ajax({
            type: 'GET',
            url: 'api/student/flash-cards',
            data: formData
        }).done(function(data) {
            if (!data.success) {
                if (data.redir) {
                    window.location.replace(data.redir);
                } else if (data.error){
                    FailurePopup(data.error, 5000);
                    return null;
                } else {
                    FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
                    return null;
                }
            } else {
                $('#FlashOne').html(data.one);
                $('#FlashTwo').html(data.two);
                $('#FlashThree').html(data.three);
                $('.student-name').html(data.name)
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
            return null;
        });

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