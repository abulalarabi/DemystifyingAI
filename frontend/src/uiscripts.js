const appState = { dataset: null, run: null, busy: false };
const byId = (id) => document.getElementById(id);

function openTab(event, name) {
    document.querySelectorAll('.tabcontent').forEach((tab) => {
        tab.style.display = tab.id === name ? 'block' : 'none';
    });
    document.querySelectorAll('.tablinks').forEach((button) => {
        button.classList.toggle('active', button === event.currentTarget);
    });
}

function notify(message) {
    Toastify({ text: message, duration: 4500 }).showToast();
}

async function post(path, body) {
    const options = { method: 'POST', body };
    if (!(body instanceof FormData)) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }
    let response;
    try {
        response = await fetch(path, options);
    } catch {
        throw new Error('Could not connect to the app server.');
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.message || 'The server could not complete the request.');
    }
    return data;
}

async function updateWorkspace(action) {
    if (appState.busy) return;
    appState.busy = true;
    const controls = ['upload-btn', 'run-model-btn'].map(byId);
    controls.forEach((button) => { button.disabled = true; });
    try {
        await action();
    } catch (error) {
        notify(error.message);
    } finally {
        appState.busy = false;
        controls.forEach((button) => { button.disabled = false; });
    }
}

function setOptions(id, values, selected = 0) {
    const select = byId(id);
    select.replaceChildren(...values.map((value) => new Option(value, value)));
    if (values.length > selected) select.selectedIndex = selected;
}

function plotFigure(id, figure) {
    const { data, layout } = typeof figure === 'string' ? JSON.parse(figure) : figure;
    // ExplainerDashboard emits WebGL scatters. Use SVG for browsers and print
    // environments where a WebGL context is unavailable.
    for (const trace of data) {
        if (trace.type === 'scattergl') trace.type = 'scatter';
    }
    const { width, ...responsiveLayout } = layout;
    return Plotly.react(id, data, { ...responsiveLayout, autosize: true }, { responsive: true });
}

const plotRequests = new Map();

async function requestPlot(key, body, draw) {
    const run = appState.run;
    if (!run) return;
    const request = Symbol(key);
    plotRequests.set(key, request);
    const isCurrent = () => appState.run === run && plotRequests.get(key) === request;
    try {
        const data = await post('/' + key, {
            ...body, dataset_id: appState.dataset.dataset_id, run_id: run.run_id,
        });
        if (isCurrent()) await draw(data);
    } catch (error) {
        if (isCurrent()) notify(error.message);
    }
}
