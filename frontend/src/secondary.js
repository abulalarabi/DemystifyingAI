function plotContributions(contributions){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(contributions);
    console.log(plotData);
    Plotly.newPlot('feature-contribution-plot', plotData.data, plotData.layout);
}

function featureContributionCallback(indx){
    //console.log(indx);
    let data = {
        'index': indx
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/contribution',
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
                
                let interaction_summary = data.interaction_summary;
                plotContributions(interaction_summary);
            }
        },
        error: function (jqXHR, exception) {
            if (jqXHR.status === 0) console.log("Could not connect to server");
            else if (jqXHR.status == 404) console.log("Backend not working");
            else if (jqXHR.status == 500) console.log("Server Error");
            $("#modelloading").hide();
        },

    });
}

function plotIndividualShap(shap_values){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(shap_values);
    console.log(plotData);
    Plotly.newPlot('individual-shap-plot', plotData.data, plotData.layout);

    // add onclick event listener to the plot
    document.getElementById("individual-shap-plot").on('plotly_click', function(data){
        //console.log(data.points[0].pointIndex);
        featureContributionCallback(data.points[0].pointIndex);
    });

}



function plotFeatureInteraction(feature_interaction){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(feature_interaction);
    console.log(plotData);
    Plotly.newPlot('plot-interaction', plotData.data, plotData.layout);
}

function plotPartial(partial_data){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(partial_data);
    console.log(plotData);
    Plotly.newPlot('plot-partial', plotData.data, plotData.layout);
    
    // on click highlight the plotly trace
    document.getElementById("plot-partial").on('plotly_click', function(data){
        let trace = data.points[0].curveNumber;
        console.log(trace);
        let update = {
            'line': {
                'color': 'red'
            }
        };
        Plotly.restyle('plot-partial', update, [trace]);
        //console.log(data.points[0].curveNumber);
    });
}

function plotInteractionSummary(interaction_summary){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(interaction_summary);
    console.log(plotData);
    Plotly.newPlot('plot-interaction-summary', plotData.data, plotData.layout);
}



$('#plot-int-summary-btn').on('click', function() {
    let feature = document.getElementById('feature-summary').value;
    let data = {
        'feature': feature
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/interactionsummary',
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
                
                let interaction_summary = data.interaction_summary;
                plotInteractionSummary(interaction_summary);
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

$('#plot-individual-btn').on('click', function() {
    let feature = document.getElementById('individual-feature').value;
    let data = {
        'feature': feature
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/individualshap',
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
                
                let shap_values = data.shap_values;
                plotIndividualShap(shap_values);
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

$('#plot-interaction-btn').on('click', function() {
    let feature1 = document.getElementById('feature-int1').value;
    let feature2 = document.getElementById('feature-int2').value;
    let data = {
        'feature1': feature1,
        'feature2': feature2
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/interaction',
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
                
                let interaction_data = data.feature_interaction;
                plotFeatureInteraction(interaction_data);
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

$('#plot-partial-btn').on('click', function() {
    let feature = document.getElementById('partial-feature').value;
    let data = {
        'feature': feature
    };
    //console.log(data);
    $.ajax({
        contentType: "application/json;charset=utf-8",
        url: 'http://127.0.0.1:1407/partial',
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
                
                let partial_data = data.partial_data;
                plotPartial(partial_data);
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

