byId('plot-individual-btn').addEventListener('click', () => {
    requestPlot('individualshap', { feature: byId('individual-feature').value }, async (data) => {
        const chart = byId('individual-shap-plot');
        const figure = JSON.parse(data.shap_values);
        // Refresh the chart and its single click handler together.
        if (chart.removeAllListeners) chart.removeAllListeners('plotly_click');
        await plotFigure(chart.id, figure);
        const rows = figure.data.flatMap((trace) => trace.customdata);
        setOptions('feature-contribution', rows);
        byId('contribution-controls').hidden = false;
        chart.on('plotly_click', ({ points }) => {
            const row = points[0]?.customdata;
            if (row == null) return;
            byId('feature-contribution').value = row;
            plotContribution(row);
        });
    });
});

function plotContribution(row) {
    requestPlot('contribution', { index: row }, (result) => {
        return plotFigure('feature-contribution-plot', result.interaction_summary);
    });
}

byId('feature-contribution-btn').addEventListener('click', () => {
    plotContribution(byId('feature-contribution').value);
});

byId('plot-partial-btn').addEventListener('click', () => {
    requestPlot('partial', { feature: byId('partial-feature').value }, async (result) => {
        const chart = byId('plot-partial');
        if (chart.removeAllListeners) chart.removeAllListeners('plotly_click');
        await plotFigure(chart.id, result.partial_data);
        chart.on('plotly_click', ({ points }) => {
            Plotly.restyle(chart, { 'line.color': 'red' }, [points[0].curveNumber]);
        });
    });
});

byId('plot-interaction-btn').addEventListener('click', () => {
    requestPlot('interaction', {
        feature1: byId('feature-int1').value, feature2: byId('feature-int2').value,
    }, ({ feature_interaction }) => plotFigure('plot-interaction', feature_interaction));
});

byId('plot-int-summary-btn').addEventListener('click', () => {
    requestPlot('interactionsummary', { feature: byId('feature-summary').value }, (result) => {
        return plotFigure('plot-interaction-summary', result.interaction_summary);
    });
});

function plotCurve(name) {
    const cutoff = Number(byId(name + '-slider').value) / 100;
    byId(name + '-label').textContent = `Threshold: ${cutoff.toFixed(2)} · Class: ${appState.run.positive_class}`;
    requestPlot('get' + name, { cut_off: cutoff }, (result) => plotFigure('plot-' + name, result[name]));
}

byId('pr-slider').addEventListener('change', () => plotCurve('pr'));
byId('roc-slider').addEventListener('change', () => plotCurve('roc'));
byId('plot-residue-feature-btn').addEventListener('click', () => {
    requestPlot('getroc', { feature: byId('residue-feature').value }, (result) => {
        return plotFigure('plot-residue-feature', result.roc);
    });
});
byId('export-btn').addEventListener('click', () => window.print());
