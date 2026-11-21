const modelSelect = byId('model-select');

modelSelect.addEventListener('change', () => {
    byId('tree-settings').hidden = modelSelect.value === 'svm';
});

function clearResults() {
    appState.run = null;
    plotRequests.clear();
    resetBoundary();
    byId('contribution-controls').hidden = true;
    byId('primary-information').style.display = 'none';
    byId('secondary-information').style.display = 'none';
    document.querySelectorAll('#primary-information .js-plotly-plot, #secondary-information .js-plotly-plot')
        .forEach((chart) => Plotly.purge(chart));
    byId('model-metrics').replaceChildren();
}

function viewMetrics(metrics, classifier) {
    const data = JSON.parse(metrics);
    const table = document.createElement('table');
    table.className = 'table metric-table';

    function addRow(values, heading) {
        const row = table.insertRow();
        values.forEach((value, index) => {
            const cell = document.createElement(heading || index === 0 ? 'th' : 'td');
            cell.textContent = typeof value === 'number' ? value.toFixed(2) : value;
            row.append(cell);
        });
    }

    if (classifier) {
        addRow(['Class', 'Precision', 'Recall', 'F1', 'Support'], true);
        for (const [label, values] of Object.entries(data)) {
            if (label !== 'accuracy') {
                addRow([label, values.precision, values.recall, values['f1-score'], String(values.support)]);
            }
        }
        addRow(['Accuracy', '', '', data.accuracy['f1-score'], '']);
    } else {
        addRow(['Metric', 'Value'], true);
        Object.entries(data).forEach((entry) => addRow(entry));
    }
    byId('model-metrics').replaceChildren(table);
}

byId('run-model-btn').addEventListener('click', () => {
    const model = modelSelect.value;
    const modelType = byId('model-type-select').value;
    const target = byId('output-select').value;
    const filters = [...document.querySelectorAll('.filter-checkbox:not(:checked):not(:disabled)')];
    updateWorkspace(async () => {
        const data = await post('/runmodel', {
            dataset_id: appState.dataset.dataset_id,
            model, model_type: modelType, target,
            split: Number(byId('train-test-slider').value) / 100,
            max_depth: byId('depth-slider').value,
            leaves: byId('leaves-slider').value,
            filter_columns: filters.map((input) => input.value),
        });

        clearResults();
        const classifier = modelType === 'classifier';
        appState.run = data;
        byId('split-summary').textContent = `${data.train_rows} training rows · ${data.test_rows} test rows`;
        for (const id of ['individual-feature', 'partial-feature', 'feature-summary', 'feature-int1', 'residue-feature']) {
            setOptions(id, data.features);
        }
        setOptions('feature-int2', data.features, 1);
        setOptions('feature1', data.boundary_features);
        setOptions('feature2', data.boundary_features, 1);

        byId('confusion-banner').textContent = classifier ? 'Confusion Matrix' : 'Predicted vs Actual';
        byId('decision-boundary').hidden = !classifier || data.boundary_features.length < 2;
        byId('plot-boundary-btn').textContent = model === 'svm' ? 'Plot Decision Boundary' : 'Run Boundary Animation';
        byId('interaction-card').hidden = data.features.length < 2;
        byId('interaction-summary-card').hidden = data.features.length < 2;
        byId('pr-div').hidden = !classifier;
        byId('roc-div').hidden = !classifier;
        byId('residue-div').hidden = classifier;
        byId('residue-feature-div').hidden = classifier;
        byId('primary-information').style.display = 'block';
        byId('secondary-information').style.display = 'block';

        viewMetrics(data.metrics, classifier);
        await Promise.all([
            plotFigure('confusion-matrix-plot', data.confusion_matrix),
            plotFigure('feature-importance-plot', data.shap_values),
        ]);
        if (classifier) {
            plotCurve('pr');
            plotCurve('roc');
        } else {
            requestPlot('getpr', {}, (result) => plotFigure('plot-residue', result.pr));
        }
        notify(data.message);
    });
});
