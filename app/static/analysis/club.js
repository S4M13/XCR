/**
 * Reset all the canvases so that they are empty once again.
 */
function reset_all_canvas() {
    $('#Attendance').remove();
    $('#Attendance-Holder').append('<canvas id="Attendance"><canvas>');

    $('#ClubBreakdown').remove();
    $('#ClubBreakdown-Holder').append('<canvas id="ClubBreakdown"><canvas>');
}

$(document).ready(function() {

    // Register the on-click functionality
    $('#student-select').submit(function(event) {
        event.preventDefault();

        // Show the grid and set the links
        $('.hidden').removeAttr("style");
        $('#generate-analysis').attr("href", "/generate-club?club-id=" + $('input[name=club-id]').val());


        // Load form data, clear graphs, and load in the new data
        var formData = {
            'club': $('input[name=club]').val(),
            'club-id': $('input[name=club-id]').val()
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
        configure_chart("Attendance", "line", options, "api/club/weekly-attendance", formData)
        
        var options = {
            title: {
                display: true,
                text: '% Club attendance distribution'
            },
            maintainAspectRatio: false}
        configure_chart("ClubBreakdown", "doughnut", options, "api/overall/club-breakdown")

        // Load in the custom flash cards
        performAJAXCall('GET', 'api/club/flash-cards', formData, function (response) {
            $('#FlashOne').html(response.one);
            $('#FlashTwo').html(response.two);
            $('#FlashThree').html(response.three);
            $('.club-name').html(response.name)
        })

    });
});