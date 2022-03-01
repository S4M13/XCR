var chartColors = {
  red: "rgb(255, 99, 132)",
  orange: "rgb(255, 159, 64)",
  yellow: "rgb(255, 205, 86)",
  green: "rgb(75, 192, 192)",
  blue: "rgb(54, 162, 235)",
  purple: "rgb(153, 102, 255)",
  grey: "rgb(231,233,237)",
};


$(document).ready(function () {

  // Load graphs
  var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: "Weekly % Attendance",
    },
    tooltips: {
      mode: "label",
    },
    hover: {
      mode: "nearest",
      intersect: true,
    },
    scales: {
      xAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "Week-Year",
          },
        },
      ],
      yAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "% Attendance",
          },
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
  };
  configure_chart(
    "PercentageAttendance",
    "line",
    options,
    "api/overall/weekly-attendance"
  );
  var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: "Weekly % Attendance by Club",
    },
    tooltips: {
      mode: "label",
    },
    hover: {
      mode: "nearest",
      intersect: true,
    },
    scales: {
      xAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "Week-Year",
          },
        },
      ],
      yAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "% Attendance",
          },
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
  };
  configure_chart(
    "PercentageAttendanceByClub",
    "line",
    options,
    "api/overall/weekly-attendance-by-club"
  );
  var options = {
    title: {
      display: true,
      text: "% Club attendance distribution",
    },
    maintainAspectRatio: false,
  };
  configure_chart(
    "ClubBreakdown",
    "doughnut",
    options,
    "api/overall/club-breakdown"
  );
  var options = {
    responsive: true,
    maintainAspectRatio: false,
    title: {
      display: true,
      text: "Weekly % Attendance of one club or more",
    },
    tooltips: {
      mode: "label",
    },
    hover: {
      mode: "nearest",
      intersect: true,
    },
    scales: {
      xAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "Week-Year",
          },
        },
      ],
      yAxes: [
        {
          display: true,
          gridLines: {
            display: true,
            color: "#101010",
          },
          scaleLabel: {
            display: true,
            labelString: "% Attendance",
          },
          ticks: {
            beginAtZero: true,
          },
        },
      ],
    },
  };
  configure_chart(
    "PercentageOnceAttendance",
    "line",
    options,
    "api/overall/weekly-attendance-once"
  );

  // Load flash cards
  performAJAXCall('GET', 'api/overall/flash-cards', {}, function(response) {
    $("#OneAttendance").html(response.one + "%");
    $("#ThreeAttendance").html(response.three + "%");
    $("#FiveAttendance").html(response.five + "%");
  });
});
