import csv
import io
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from secrets import token_hex
from threading import Lock

import pandas as pd
from flask import Flask, abort, jsonify, request, session
from werkzeug.exceptions import HTTPException

from . import models


ROOT = Path(__file__).resolve().parents[1]
MAX_UPLOAD = 8 * 1024 * 1024
PREVIEW_ROWS = 200

app = Flask(__name__, static_folder=ROOT / "frontend", static_url_path="/assets")
app.config.update(
    SECRET_KEY=token_hex(32),
    MAX_CONTENT_LENGTH=MAX_UPLOAD,
)


@dataclass
class Workspace:
    dataset: pd.DataFrame
    revision: str = field(default_factory=lambda: token_hex(16))
    run: models.ModelRun | None = None
    lock: Lock = field(default_factory=Lock)


workspaces = OrderedDict()
workspaces_lock = Lock()


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(message=error.description), error.code


@app.errorhandler(models.InputError)
def invalid_input(error):
    return jsonify(message=str(error)), 400


@app.get("/")
def index():
    if "workspace" not in session:
        session["workspace"] = token_hex(16)
    return app.send_static_file("index.html")


def parse_dataset(stream):
    try:
        raw = stream.read().decode("utf-8-sig")
        if "\x00" in raw:
            raise models.InputError("The CSV contains a null byte.")
        reader = csv.reader(io.StringIO(raw, newline=""), strict=True)
        columns = next(reader, [])
        if len(columns) < 2 or any(not name.strip() for name in columns):
            raise models.InputError("Use a CSV with at least two named columns.")
        if len(set(columns)) != len(columns):
            raise models.InputError("CSV column names must be unique.")

        rows = []
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                continue
            if len(row) != len(columns):
                raise models.InputError(f"CSV row ending at line {reader.line_num} has the wrong number of columns.")
            rows.append(row)
        if not rows:
            raise models.InputError("The CSV has no data rows.")

        # Preserve headers and CSV row numbers while inferring numeric columns.
        frame = pd.read_csv(
            io.StringIO(raw), header=0, names=columns, keep_default_na=False, na_values=[""],
        )
    except (UnicodeDecodeError, csv.Error, pd.errors.ParserError) as error:
        raise models.InputError("Use a well-formed, comma-separated UTF-8 CSV.") from error
    return frame, rows[:PREVIEW_ROWS]


@app.post("/dataset")
def dataset():
    upload = request.files.get("file")
    if not upload or Path(upload.filename).suffix.lower() != ".csv":
        raise models.InputError("Select a CSV file to upload.")

    frame, preview = parse_dataset(upload.stream)
    workspace = Workspace(frame)
    key = session.get("workspace") or token_hex(16)
    session["workspace"] = key
    with workspaces_lock:
        workspaces[key] = workspace
        workspaces.move_to_end(key)
        if len(workspaces) > 16:
            workspaces.popitem(last=False)
    return jsonify(
        message="Dataset uploaded.", success=True, columns=list(frame.columns),
        preview=preview, row_count=len(frame), dataset_id=workspace.revision,
    )


def request_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise models.InputError("Send a JSON object with the request.")
    return data


def current_workspace():
    key = session.get("workspace")
    with workspaces_lock:
        workspace = workspaces.get(key)
        if workspace:
            workspaces.move_to_end(key)
    if workspace is None:
        abort(409, "Upload a dataset first.")
    return workspace


def check_revision(workspace, data):
    if "dataset_id" in data and data["dataset_id"] != workspace.revision:
        abort(409, "The dataset changed. Upload your CSV again.")


@app.post("/runmodel")
def runmodel():
    data = request_data()
    workspace = current_workspace()
    check_revision(workspace, data)
    with workspace.lock:
        run = models.train(workspace.dataset, data)
        result = run.summary()
        if current_workspace() is not workspace:
            abort(409, "The dataset changed while training. Run the model again.")
        workspace.run = run
    return jsonify(
        message="Model trained.", success=True, run_id=run.id,
        **result,
    )


PLOTS = {
    "decisionboundary": "frames",
    "individualshap": "shap_values",
    "interaction": "feature_interaction",
    "partial": "partial_data",
    "interactionsummary": "interaction_summary",
    "getpr": "pr",
    "getroc": "roc",
    "contribution": "interaction_summary",
}


def plot(plot_name):
    data = request_data()
    workspace = current_workspace()
    check_revision(workspace, data)
    with workspace.lock:
        run = workspace.run
        if run is None or ("run_id" in data and data["run_id"] != run.id):
            abort(409, "Run the model for this dataset first.")
        result = run.plot(plot_name, data)
        if current_workspace() is not workspace:
            abort(409, "The dataset changed. Run the model again.")
    return jsonify(message="Plot ready.", success=True, **{PLOTS[plot_name]: result})


for plot_name in PLOTS:
    app.add_url_rule(
        f"/{plot_name}", endpoint=plot_name,
        defaults={"plot_name": plot_name}, view_func=plot, methods=["POST"],
    )
