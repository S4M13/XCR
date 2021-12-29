var chartColors = {
  red: 'rgb(255, 99, 132)',
  orange: 'rgb(255, 159, 64)',
  yellow: 'rgb(255, 205, 86)',
  green: 'rgb(75, 192, 192)',
  blue: 'rgb(54, 162, 235)',
  purple: 'rgb(153, 102, 255)',
  grey: 'rgb(231,233,237)'
};

//Get AJAX data from server

var attempts = 0;

function configure_chart(chart_id, chart_type, chart_options, endpoint) {

    $.ajax({
        type: 'GET',
        url: endpoint
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
                        configure_chart(chart_id, chart_type, chart_options, endpoint)
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
                configure_chart(chart_id, chart_type, chart_options, endpoint)
            }, 4000);
        }else {
            FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
        }
        return null;0
    });
}



var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: 'Weekly % Attendance'
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
          labelString: '% Attendance'
        },
        ticks: {
            beginAtZero: true
        }
      }]
    }
  }
configure_chart("PercentageAttendance", "line", options, "api/overall/weekly-attendance")
var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: 'Weekly % Attendance by Club'
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
          labelString: '% Attendance'
        },
        ticks: {
            beginAtZero: true
        }
      }]
    }
  }
configure_chart("PercentageAttendanceByClub", "line", options, "api/overall/weekly-attendance-by-club")
var options = {
  title: {
    display: true,
    text: '% Club attendance distribution'
  },
  maintainAspectRatio: false
}
configure_chart("ClubBreakdown", "doughnut", options, "api/overall/club-breakdown")
var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: 'Weekly % Attendance of one club or more'
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
          labelString: '% Attendance'
        },
        ticks: {
            beginAtZero: true
        }
      }]
    }
  }
configure_chart("PercentageOnceAttendance", "line", options, "api/overall/weekly-attendance-once")

//Custom statistics

$.ajax({
    type: 'GET',
    url: 'api/overall/flash-cards'
}).done(function(data) {
    if (!data.success) {
        if (data.redir) {
            window.location.replace(data.redir);
        } else if (data.error){
            FailurePopup(data.error, 5000);
            return null;
        } else {
            if (attempts < 5) {
                FailurePopup("Something has gone wrong, failed to load chart data. Will automatically try again in a second.", 10000);
                attempts += 1;
                setTimeout(function () {
                    configure_chart(chart_id, chart_type, chart_options, endpoint)
                }, 4000);
            }else {
                FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
            }
            return null;
        }
    } else {
        $('#OneAttendance').html(data.one + "%");
        $('#ThreeAttendance').html(data.three + "%");
        $('#FiveAttendance').html(data.five + "%");
    }
}).fail(function(jqXHR, textStatus, errorThrown) {
    if (attempts < 5) {
        FailurePopup("Something has gone wrong, failed to load chart data. Will automatically try again in a second.", 10000);
        attempts += 1;
        setTimeout(function () {
            configure_chart(chart_id, chart_type, chart_options, endpoint)
        }, 4000);
    }else {
        FailurePopup("Something has gone wrong, failed to load chart data. Please try again later.", 20000);
    }
    return null;0
});
