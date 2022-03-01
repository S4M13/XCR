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

function detect_mobile() {
   return (window.innerWidth <= 800 || window.innerHeight <= 600)
}


$(document).ready(function(){
    animateCanvas();

    if (detect_mobile()) {
        window.location.replace("/unsupported");
    }
});
