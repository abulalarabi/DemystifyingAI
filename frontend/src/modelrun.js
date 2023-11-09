function plotConfusionMatrix(confusion_matrix){
    //console.log(confusion_matrix);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(confusion_matrix);
    console.log(plotData);
    Plotly.newPlot('confusion-matrix-plot', plotData.data, plotData.layout);
}

$('#run-model-btn').on('click', function() {
    let max_depth = document.getElementById('depth-slider').value;
    let model_name = document.getElementById('model-select').value;
    let output_column = document.getElementById('output-select').value;
    let leaves = document.getElementById('leaves-slider').value;
    let data = {
        'max_depth': max_depth,
        'model': model_name,
        'leaves': leaves,
        'target': output_column
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/runmodel',
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
                
                // get confusion matrix
                let confusion_matrix = data.confusion_matrix;
                //console.log(confusion_matrix);
                plotConfusionMatrix(confusion_matrix);


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
