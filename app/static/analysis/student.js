/**
 * Reset all the canvases so that they are empty once again.
 */
function reset_all_canvas() {
    $('#Attendance').remove();
    $('#Attendance-Holder').append('<canvas id="Attendance"><canvas>');

    $('#ClubBreakdown').remove();
    $('#ClubBreakdown-Holder').append('<canvas id="ClubBreakdown"><canvas>');

    $('#ClubBarChart').remove();
    $('#ClubBarChart-Holder').append('<canvas id="ClubBarChart"><canvas>');
}

$(document).ready(function() {
    // Register the on-click functionality
    $('#student-select').submit(function(event) {
        event.preventDefault();


        // Show the grid and set the links
        $('.hidden').removeAttr("style");
        $('#generate-analysis').attr("href", "/generate-student?student-id=" + $('input[name=name-id]').val());

        // Load form data, clear graphs, and load in the new data
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
          maintainAspectRatio: false}
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
            maintainAspectRatio: false}
        configure_chart("ClubBarChart", "bar", options, "api/student/club-bar-chart", formData)

        // Load in the custom flash cards
        performAJAXCall('GET', 'api/student/flash-cards', formData, function(response) {
            $('#FlashOne').html(data.one);
                $('#FlashTwo').html(data.two);
                $('#FlashThree').html(data.three);
                $('.student-name').html(data.name)
        });
    });
});