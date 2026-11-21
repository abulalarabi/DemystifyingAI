let boundaryFrames = [];
let boundaryTimer;

function resetBoundary() {
    clearTimeout(boundaryTimer);
    boundaryFrames = [];
    byId('boundary-controls').hidden = true;
}

function showBoundaryFrame(index) {
    byId('seek-slider').value = index + 1;
    byId('seek-slider-label').textContent = `Depth: ${index + 1}`;
    return plotFigure('boundary-plot', boundaryFrames[index]);
}

function playBoundary() {
    clearTimeout(boundaryTimer);
    function next(index) {
        if (index >= boundaryFrames.length) return;
        showBoundaryFrame(index);
        if (index + 1 < boundaryFrames.length) {
            boundaryTimer = setTimeout(() => next(index + 1), 1000);
        }
    }
    next(0);
}

byId('seek-slider').addEventListener('input', (event) => {
    clearTimeout(boundaryTimer);
    if (boundaryFrames.length) showBoundaryFrame(Number(event.target.value) - 1);
});

byId('play-pause-btn').addEventListener('click', playBoundary);

byId('plot-boundary-btn').addEventListener('click', () => {
    return requestPlot('decisionboundary', {
        feature1: byId('feature1').value, feature2: byId('feature2').value,
    }, ({ frames }) => {
        boundaryFrames = frames;
        byId('seek-slider').max = frames.length;
        byId('boundary-controls').hidden = frames.length < 2;
        playBoundary();
    });
});
