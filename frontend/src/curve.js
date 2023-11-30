function plotPr(pr){
    plotData = JSON.parse(pr);
    console.log(plotData);
    Plotly.newPlot('plot-pr', plotData.data, plotData.layout);
}

function plotRoc(roc){
    plotData = JSON.parse(roc);
    console.log(plotData);
    Plotly.newPlot('plot-roc', plotData.data, plotData.layout);
}

$('#pr-slider').on('change', function() {
    let val = parseInt(this.value);
    $('#pr-label').text(`PR Threshold: ${val}`);
    let data = {
        'cut_off': val,
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/getpr',
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
                
                let pr = data.pr;
                plotPr(pr);
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


$('#roc-slider').on('change', function() {
    let val = parseInt(this.value);
    $('#roc-label').text(`ROC Threshold: ${val}`);
    let data = {
        'cut_off': val,
        'feature': 'none'
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/getroc',
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
                
                let roc = data.roc;
                plotRoc(roc);
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


function plotResidueFeature(residue_feature){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(residue_feature);
    console.log(plotData);
    Plotly.newPlot('plot-residue-feature', plotData.data, plotData.layout);
}

$('#plot-residue-feature-btn').on('click', function() {
    let feature = document.getElementById('residue-feature').value;
    let data = {
        'cut_off': 0,
        'feature': feature
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/getroc',
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
                
                let roc = data.roc;
                plotResidueFeature(roc);
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

// export the page in pdf format
$("#export-btn").on('click', function(){
    print();
});