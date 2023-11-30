function plotConfusionMatrix(confusion_matrix){
    //console.log(confusion_matrix);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(confusion_matrix);
    console.log(plotData);
    Plotly.newPlot('confusion-matrix-plot', plotData.data, plotData.layout);

    
}

function plotShapValues(shap_values){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(shap_values);
    console.log(plotData);
    Plotly.newPlot('feature-importance-plot', plotData.data, plotData.layout);
}

function viewMetrics(data){
    //console.log(data);
    // use plotly to plot the confusion matrix
    metricData = JSON.parse(data);
    // get the model type
    let model_type = document.getElementById('model-type-select').value;
    if(model_type == "classifier"){
        // get metricData keys
        let keys = Object.keys(metricData);
        // console.log(keys);
        // create a table with the keys
        let table = document.createElement('table');
        table.className = "table metric-table";

        // uses keys to create table headers
        let tableHeader = document.createElement('tr');
        // create a blank header
        let th = document.createElement('th');
        th.innerHTML = "";
        tableHeader.appendChild(th);
        keys.forEach((key) => {
            let th = document.createElement('th');
            th.innerHTML = key;
            tableHeader.appendChild(th);
        });
        table.appendChild(tableHeader);
        // get the children of the first key
        let children = Object.keys(metricData[keys[0]]);
        console.log(children);

        // for each child key create a row and add the key and values
        children.forEach((child) => {
            let tableRow = document.createElement('tr');
            let th = document.createElement('th');
            th.innerHTML = child;
            tableRow.appendChild(th);
            keys.forEach((key) => {
                let td = document.createElement('td');
                // keep upto two decimal places
                td.innerHTML = metricData[key][child].toFixed(2);
                tableRow.appendChild(td);
            });
            table.appendChild(tableRow);
        });



        // append the table to the metrics div
        let metricsDiv = document.getElementById('model-metrics');
        metricsDiv.innerHTML = "";
        metricsDiv.appendChild(table);
    }
    else{
        // its a regression model
        // the data is a dictionary with keys as the metric names and values as the metric values
        // format: {'Mean Absolute Error (MAE)': mae, 'Mean Squared Error (MSE)': mse, 'Root Mean Squared Error (RMSE)': rmse, 'R-Squared (R2)': r2}
        // get metricData keys
        let keys = Object.keys(metricData);
        // console.log(keys);
        
        // there will be a header row with two columns: Metric and Value
        let table = document.createElement('table');
        table.className = "table metric-table";
        let tableHeader = document.createElement('tr');
        let th = document.createElement('th');
        th.innerHTML = "Metric";
        tableHeader.appendChild(th);
        th = document.createElement('th');
        th.innerHTML = "Value";
        tableHeader.appendChild(th);
        table.appendChild(tableHeader);

        // add keys in the first column and values in the second column
        keys.forEach((key) => {
            let tableRow = document.createElement('tr');
            let td = document.createElement('td');
            td.innerHTML = key;
            tableRow.appendChild(td);
            td = document.createElement('td');
            td.innerHTML = metricData[key].toFixed(2);
            tableRow.appendChild(td);
            table.appendChild(tableRow);
        });

        // append the table to the metrics div
        let metricsDiv = document.getElementById('model-metrics');
        metricsDiv.innerHTML = "";
        metricsDiv.appendChild(table);

    }

    
}

function plotResidue(residue_data){
    //console.log(shap_values);
    // use plotly to plot the confusion matrix
    plotData = JSON.parse(residue_data);
    console.log(plotData);
    Plotly.newPlot('plot-residue', plotData.data, plotData.layout);
}

function plotResidueCallback() {
    let data = {
        'cut_off': 0,
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
                plotResidue(pr);
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


$('#run-model-btn').on('click', function() {
    let max_depth = document.getElementById('depth-slider').value;
    let model_name = document.getElementById('model-select').value;
    let output_column = document.getElementById('output-select').value;
    let leaves = document.getElementById('leaves-slider').value;
    let train_test_split = document.getElementById('train-test-slider').value/100;
    
    // get the list of unchecked columns from the filter_checkboxes div
    let unchecked_columns = [];
    let filter_checkbox_div = document.getElementById('filter_checkboxes');
    console.log(filter_checkbox_div);
    // get all checkboxes by checking the type
    let filter_checkboxes = filter_checkbox_div.querySelectorAll('input[type="checkbox"]');
    //console.log(filter_checkboxes);
    // get the unchecked checkboxes
    for(let i=0; i<filter_checkboxes.length; i++){
        if(!filter_checkboxes[i].checked){
            unchecked_columns.push(filter_checkboxes[i].value);
        }
    }

    let output_select = document.getElementById('output-select');
    let feature1_select = document.getElementById('feature1');
    let feature2_select = document.getElementById('feature2');
    let inidividual_feature_select = document.getElementById('individual-feature');
    let feature_int1 = document.getElementById('feature-int1');
    let feature_int2 = document.getElementById('feature-int2');
    let feature_partial = document.getElementById('partial-feature');
    let interaction_summary = document.getElementById('feature-summary');
    let residue_feature = document.getElementById('residue-feature');

    // clear all the options from the dropdowns
    feature1_select.innerHTML = "";
    feature2_select.innerHTML = "";
    inidividual_feature_select.innerHTML = "";
    feature_int1.innerHTML = "";
    feature_int2.innerHTML = "";
    feature_partial.innerHTML = "";
    interaction_summary.innerHTML = "";
    residue_feature.innerHTML = "";

    // append the checked column names from filter_checkboxes
    for(let i=0; i<filter_checkboxes.length; i++){
        if(filter_checkboxes[i].checked){
            // check if this column is the output column
            if(filter_checkboxes[i].value != output_select.value){
                let option = document.createElement('option');
                option.value = filter_checkboxes[i].value;
                option.text = filter_checkboxes[i].value;
                feature1_select.appendChild(option.cloneNode(true));
                feature2_select.appendChild(option.cloneNode(true));
                feature_int1.appendChild(option.cloneNode(true));
                feature_int2.appendChild(option.cloneNode(true));
                feature_partial.appendChild(option.cloneNode(true));
                interaction_summary.appendChild(option.cloneNode(true));
                inidividual_feature_select.appendChild(option.cloneNode(true));
                residue_feature.appendChild(option.cloneNode(true));
            }
        }
    }
    // select the second element from feature2_select
    feature2_select.selectedIndex = 1;
    // select the first element from feature-int1
    feature_int1.selectedIndex = 0;
    // select the second element from feature-int2
    feature_int2.selectedIndex = 1;
    // select the first element from feature-partial
    feature_partial.selectedIndex = 0;
    // select the first element from feature-summary
    interaction_summary.selectedIndex = 0;

    // get the model type
    let model_type = document.getElementById('model-type-select').value;

    let data = {
        'max_depth': max_depth,
        'model': model_name,
        'leaves': leaves,
        'target': output_column,
        'split': train_test_split,
        'filter_columns': unchecked_columns,
        'model_type': model_type
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
                $('#primary-information').fadeIn(300, function() {
                    $('#secondary-information').fadeIn(300);
                });
                
                // get confusion matrix
                let confusion_matrix = data.confusion_matrix;
                //console.log(confusion_matrix);
                plotConfusionMatrix(confusion_matrix);

                // get shap values
                let shap_values = data.shap_values;
                //console.log(shap_values);
                plotShapValues(shap_values);

                // get metrics
                let metrics = data.metrics;
                //console.log(metrics);
                viewMetrics(metrics);

                plotResidueCallback();

                // check if the model is a classifier
                let model_type = document.getElementById('model-type-select').value;
                // if the model is not a classifier then rename confusion-banner id to "Predicted vs Actual"
                if(model_type != "classifier"){
                    // hide the decision boundary
                    $('#decision-boundary').hide();
                    document.getElementById('confusion-banner').textContent = "Predicted vs Actual";
                    $("#residue-div").show(400);
                    $("#residue-feature-div").show(400);
                    $("#pr-div").hide();
                    $("#roc-div").hide();
                }
                else{
                    // show the decision boundary
                    $('#decision-boundary').show();
                    document.getElementById('confusion-banner').textContent = "Confusion Matrix";
                    $("#residue-div").hide(400);
                    $("#residue-feature-div").hide(400);
                    $("#pr-div").show();
                    $("#roc-div").show();
                }


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
