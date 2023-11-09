
frames = [];


$('#seek-slider').on('change', function () {
    let val = parseInt(this.value)-1;
    each_frame = JSON.parse(frames[val]);
    console.log(each_frame);
    //console.log(frames[animationFrame].layout);
    Plotly.newPlot('boundary-plot', each_frame.data, each_frame.layout);
    $('#seek-slider-label').text(`Depth:${val+1}`);
});

$('#play-pause-btn').on('click', createAnimation);

// Function to create the animation
function createAnimation() {
    // Render the Plotly figure in the 'boundary-plot' div
    let animationFrame = 0;

    function animate() {
        if (animationFrame < frames.length) {
            each_frame = JSON.parse(frames[animationFrame]);
            // //console.log(frames[animationFrame].layout);
            Plotly.newPlot('boundary-plot', each_frame.data, each_frame.layout);
            // 
            $('#seek-slider-label').text(`Depth:${animationFrame+1}`);
            // change the current value of the slider with id seek-slider
            let seek_slider = document.getElementById('seek-slider');
            seek_slider.value = animationFrame+1;
            animationFrame++;

            // Use a time delay to control the animation speed (adjust as needed)
            setTimeout(animate, 1000);
        }
    }

    animate();
}

// add an event listener to the button plot-boundary-btn
const plotBoundaryBtn = document.getElementById('plot-boundary-btn');
// get the feature 1, feature 2, max depth, model name and output column name on click and send it to 127.0.0.1:1407/decisionboundary on click
plotBoundaryBtn.addEventListener('click', async (event) => {
    event.preventDefault();
    let feature1 = document.getElementById('feature1').value;
    let feature2 = document.getElementById('feature2').value;
    let max_depth = document.getElementById('depth-slider').value;
    let model_name = document.getElementById('model-select').value;
    let output_column = document.getElementById('output-select').value;
    let data = {
        'feature1': feature1,
        'feature2': feature2,
        'max_depth': max_depth,
        'model': model_name,
        'target': output_column
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/decisionboundary',
        type: 'POST',
        data: JSON.stringify(data),
        dataType: "json",
        cache: false,
        success: function (data) {
            if (data.hasOwnProperty('message')) {
                Toastify({
                    text: data.message,
                    duration: 3000
                }).showToast();
                
                // get frames
                frames = data.frames;
                // console.log(frames);
                // create animation
                createAnimation();
            }
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) console.log("Could not connect to server");
            else if (jqXHR.status == 404) console.log("Backend not working");
            else if (jqXHR.status == 500) console.log("Server Error");
            $("#modelloading").hide();
        },

    });

});

