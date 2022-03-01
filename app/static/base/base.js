

//GLOBAL CONSTANTS

var STANDARD_POPUP_TIME = 2000;
var STANDARD_LONG_POPUP_TIME = STANDARD_POPUP_TIME * 2.5;

var AJAX_MAX_RETRIES = 5;
var AJAX_RETRY_DELAY = 6000;


// GLOBAL VARIBALES

var name_valid = false;
var club_valid = false;


// GLOBAL FUNCTIONS

/**
 * Performs an AJAX call to the server and returns the server's response - automatically handles failed requests.
 * 
 * @param  {string} type - The type of request to submit to the server (GET/POST)
 * @param  {string} endpoint - The endpoint of the server to contact
 * @param  {array} args - The arguments to pass along in the data field of the request
 * @param  {Function} callback - Callback function that is called and passed along the response in the first argument 
 * @param  {Number} attempts - Internal recursive variable which manages how many times the server has been contacted
 */
function performAJAXCall(type, endpoint, args, callback, attempts = 0) {
    return $.ajax({
        type: type,
        url: endpoint,
        data: args
    }).done(function(data) {
        if (!data.success) {

            if (data.redir) {
                window.location.replace(data.redir);
                return null;
            }

            if (data.error){
                FailurePopup(data.error, STANDARD_LONG_POPUP_TIME);
                return null;
            }

            if (attempts >= AJAX_MAX_RETRIES) {
                FailurePopup("Something has gone wrong, some data has failed to load. Please try again later", STANDARD_LONG_POPUP_TIME);
                return null;
            }

            FailurePopup("Something has gone wrong, some data has failed to load. Will automatically try again in a second.", STANDARD_POPUP_TIME);

            setTimeout(function () {
                performAJAXCall(type, endpoint, args, callback, attempts+1)
            }, AJAX_RETRY_DELAY);
        }

        callback(data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        if (attempts >= AJAX_MAX_RETRIES) {
            FailurePopup("Something has gone wrong, some data has failed to load. Please try again later", STANDARD_LONG_POPUP_TIME);
            return null;
        }

        FailurePopup("Something has gone wrong, some data has failed to load. Will automatically try again in a second.", STANDARD_POPUP_TIME);

        setTimeout(function () {
            performAJAXCall(type, endpoint, args, callback, attempts+1)
        }, AJAX_RETRY_DELAY);
    });
}


/**
 * Configures a chart HTML object with the following settings, fecthing the data from the server.
 * 
 * @param  {Number} chart_id - The ID of the chart to configure
 * @param  {string} chart_type - The type of the chart to create
 * @param  {array} chart_options - The options to configure the chart with
 * @param  {string} endpoint - The endpoint on the server to contact for the data.
 * @param  {array} args - The arguments to pass along in the AJAX request.
 */
function configure_chart(chart_id, chart_type, chart_options, endpoint, args) {
    var response = performAJAXCall('GET', endpoint, args, function (response) {

        var config = {
            type: chart_type,
            options: chart_options,
            data: response
        }

        var ctx = document.getElementById(chart_id).getContext("2d");
        new Chart(ctx, config);
    })
}


/**
 * Shows a success popup to the user.
 * 
 * @param {string} message - The message to show to the user
 * @param {Number} time - How long to show the popup to the user (Can also be clicked out of)
 */
function SuccessPopup(message, time) {
    $('#success-message').text(message)
    $('#success').modal('show');
    setTimeout(function () {
        $('#success').modal('hide');
    }, time);
}


/**
 * Shows a failure popup to the user.
 * 
 * @param {string} message - The message to show to the user
 * @param {Number} time - How long to show the popup to the user (Can also be clicked out of)
 */
function FailurePopup(message, time) {
    $('#failure-message').text(message)
    $('#failure').modal('show');
    setTimeout(function () {
        $('#failure').modal('hide');
    }, time);
}


/**
 * Toggles the collapsing/rebuilding of the sidebar.
 */
function toggleSidebar() {
    if ($('#sidebar').hasClass('active')) {
        $('#sidebar').removeClass('active');
        $('#content').removeClass('active');
        $('.alert-overall').removeClass('active');
        $('.close-button').removeClass('active');
    } else {
        $('#sidebar').addClass('active');
        $('#content').addClass('active');
        $('.alert-overall').addClass('active');
        $('.close-button').addClass('active');
    }
}


/**
 * Returns whether the user has a mobile sized screen or not.
 * 
 * @return {boolean} - Returns whether the screen has a size which is too small for the website to display on
 */
function detect_mobile() {
   return (window.innerWidth <= 800 || window.innerHeight <= 600)
}



// The following section of code was library code which Copy+Pasted from the library into the source code.
// This was done to allow faster loading of the code without having to load the whole library.
// The following section, as marked below, was taken from an online module, which was in turn influenced by
// LINK: https://codepen.io/LeonGr/pen/yginI
// The code has additionally been edited to fit the application better.
// Please note this code provides no functionality and is decorative only proving the moving background, and nothing else.

// START SECTION \\

function doCanvasAnimation() {
    //Load the canvas
    var canvas = document.getElementById("canvas"),
    ctx = canvas.getContext('2d');

    //Set canvas height and width
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    //Pre-configure variables.
    var points = []
    var FPS = 30
    var x = screen.width / 19.2



    //Add all the points.
    for (var i = 0; i < x; i++) {
      points.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 1 + 1,
        vx: Math.floor(Math.random() * 50) - 25,
        vy: Math.floor(Math.random() * 50) - 25
      });
    }


    function draw() {
      ctx.clearRect(0,0,canvas.width,canvas.height);

      ctx.globalCompositeOperation = "lighter";

      for (var i = 0, x = points.length; i < x; i++) {
        var s = points[i];

        ctx.fillStyle = "#fff";
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.radius, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = 'black';
        ctx.stroke();
      }

      ctx.beginPath();
      for (var i = 0, x = points.length; i < x; i++) {
        var starI = points[i];
        ctx.moveTo(starI.x,starI.y);
        for (var j = 0, x = points.length; j < x; j++) {
          var starII = points[j];
          if(distance(starI, starII) < 150) {
            ctx.lineTo(starII.x,starII.y);
          }
        }
      }
      ctx.lineWidth = 0.05;
      ctx.strokeStyle = 'white';
      ctx.stroke();
    }

    function distance(point1, point2){
      var xs = 0;
      var ys = 0;

      xs = point2.x - point1.x;
      xs = xs * xs;

      ys = point2.y - point1.y;
      ys = ys * ys;

      return Math.sqrt( xs + ys );
    }

    // Update points locations
    function update() {
      for (var i = 0, x = points.length; i < x; i++) {
        var s = points[i];

        s.x += s.vx / FPS;
        s.y += s.vy / FPS;

        if (s.x < 0 || s.x > canvas.width) s.vx = -s.vx;
        if (s.y < 0 || s.y > canvas.height) s.vy = -s.vy;
      }
    }


    function onTick() {
      draw();
      update();
      requestAnimationFrame(onTick);
    }

    onTick();
}

// END SECTION \\






// Perform certain operations once the document has loaded
$(document).ready(function(){

    // Insert CSRF tokens into required forms
    $('.csrf-req').each(function(i, obj) {
        $('<input>').attr({
            type: 'hidden',
            name: 'X-CSRF-TOKEN',
            value: $('meta[name=csrf-token]').attr('content')
        }).appendTo(obj)
    });

    // Add functionality to sidebar
    $('.close-button').click(function() {
        toggleSidebar();
    });

    // Perform background animation
    doCanvasAnimation();

    // Check if mobile is currently being used
    if (detect_mobile()) {
        window.location.replace("/unsupported");
    }

    // Register global functionality for name auto-completion
    if ($('#club').length) {
        club_valid = false;
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
    }

    if ($('#name').length) {
        name_valid = false;
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
    }
});
