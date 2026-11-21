const uploadForm = byId('upload-form');
const fileInput = byId('file');

fileInput.addEventListener('change', () => {
    byId('datasetname').textContent = fileInput.files[0]?.name ?? 'Select a Dataset';
});

uploadForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(uploadForm);
    updateWorkspace(async () => {
        const data = await post('/dataset', formData);
        appState.dataset = data;
        clearResults();
        renderPreview(data);
        renderFilters(data.columns);
        byId('datasetviewer').style.display = 'block';
        byId('modelparams').style.display = 'block';
        notify(data.message);
    });
});

function renderPreview({ columns, preview, row_count }) {
    const table = byId('csvRoot');
    table.replaceChildren();
    const heading = table.createTHead().insertRow();
    for (const column of columns) {
        const cell = document.createElement('th');
        cell.scope = 'col';
        cell.textContent = column;
        heading.append(cell);
    }
    const body = table.createTBody();
    for (const row of preview) {
        const entry = body.insertRow();
        row.forEach((value) => { entry.insertCell().textContent = value; });
    }
    byId('dataset-preview-count').textContent = `Showing ${preview.length} of ${row_count} rows`;
}

function renderFilters(columns) {
    setOptions('output-select', columns, columns.length - 1);
    byId('filter_message').textContent = 'Uncheck features to exclude them.';
    byId('filter_checkboxes').replaceChildren(...columns.map((column) => {
        const label = document.createElement('label');
        label.className = 'filter-label';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = column;
        checkbox.checked = true;
        checkbox.className = 'filter-checkbox';
        label.append(checkbox, column);
        return label;
    }));
    updateTargetFilter();
}

function updateTargetFilter() {
    const target = byId('output-select').value;
    document.querySelectorAll('.filter-checkbox').forEach((checkbox) => {
        checkbox.disabled = checkbox.value === target;
    });
}

byId('output-select').addEventListener('change', updateTargetFilter);
