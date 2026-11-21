import io
import json
import unittest
from pathlib import Path

from backend.backend import app


ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def upload(self, name, content=None):
        if content is None:
            content = (ROOT / "testdataset" / name).read_bytes()
        return self.client.post("/dataset", data={"file": (io.BytesIO(content), name)})

    def train(self, **options):
        body = dict(
            model="decision-tree", model_type="classifier", target="variety",
            split=0.8, max_depth=3, leaves=1,
        )
        body.update(options)
        return self.client.post("/runmodel", json=body)

    def test_validation_preserves_current_workspace(self):
        dataset = self.upload("iris.csv").json
        for bad_csv in (b"", b"x,x\n1,2", b"x,y\n1,2,3", b"\xff", b"x,y\n1,2\x00"):
            with self.subTest(csv=bad_csv):
                self.assertEqual(self.upload("bad.csv", bad_csv).status_code, 400)
        self.assertEqual(self.train(split=1).status_code, 400)
        self.assertEqual(self.train(model="unknown").status_code, 400)
        self.assertEqual(self.train(target="unknown").status_code, 400)
        self.assertEqual(self.train(dataset_id=dataset["dataset_id"]).status_code, 200)

    def test_upload_replaces_run_and_clients_are_isolated(self):
        first = self.upload("iris.csv").json
        run = self.train(dataset_id=first["dataset_id"]).json
        other = app.test_client()
        request = {"feature": "petal.length", "run_id": run["run_id"]}
        self.assertEqual(other.post("/individualshap", json=request).status_code, 409)
        self.assertEqual(self.client.post("/individualshap", json=request).status_code, 200)

        second = self.upload("Housing.csv").json
        self.assertNotEqual(first["dataset_id"], second["dataset_id"])
        self.assertEqual(self.client.post("/individualshap", json=request).status_code, 409)
        self.assertEqual(self.train(dataset_id=first["dataset_id"]).status_code, 409)

    def test_all_classifiers_report_holdout_and_multiclass_boundary(self):
        self.assertEqual(self.upload("iris.csv").status_code, 200)
        for name in ("decision-tree", "random-forest", "svm"):
            with self.subTest(model=name):
                result = self.train(model=name)
                self.assertEqual(result.status_code, 200, result.json)
                self.assertEqual((result.json["train_rows"], result.json["test_rows"]), (120, 30))
                self.assertEqual(json.loads(result.json["metrics"])["Setosa"]["support"], 10)
                response = self.client.post("/decisionboundary", json={
                    "feature1": "petal.length", "feature2": "petal.width",
                })
                self.assertEqual(response.status_code, 200, response.json)
                frames = response.json["frames"]
                self.assertEqual(len(frames), 1 if name == "svm" else 3)
                traces = json.loads(frames[0])["data"]
                self.assertEqual([trace["name"] for trace in traces[1:]], ["Setosa", "Versicolor", "Virginica"])
                self.assertEqual(len(traces[0]["x"]), 100)

    def test_cutoff_and_contribution_row_identity(self):
        self.upload("iris.csv")
        self.assertEqual(self.train().status_code, 200)
        response = self.client.post("/getroc", json={"cut_off": 0})
        self.assertEqual(response.status_code, 200, response.json)
        marker = json.loads(response.json["roc"])["data"][1]
        self.assertEqual((marker["x"], marker["y"]), ([1.0], [1.0]))
        self.assertEqual(self.client.post("/getroc", json={"cut_off": 70}).status_code, 400)

        response = self.client.post("/individualshap", json={"feature": "petal.length"})
        self.assertEqual(response.status_code, 200, response.json)
        row = json.loads(response.json["shap_values"])["data"][0]["customdata"][0]
        response = self.client.post("/contribution", json={"index": row})
        self.assertEqual(response.status_code, 200, response.json)
        self.assertIn(f"Row {row}", json.loads(response.json["interaction_summary"])["layout"]["title"]["text"])

    def test_svm_regression_explanations_and_residuals(self):
        self.assertEqual(self.upload("Housing.csv").status_code, 200)
        result = self.train(model="svm", model_type="regression", target="price")
        self.assertEqual(result.status_code, 200, result.json)
        self.assertGreater(json.loads(result.json["metrics"])["R-Squared (R2)"], 0)
        for route, data in (
            ("/getpr", {}),
            ("/getroc", {"feature": "area"}),
            ("/interaction", {"feature1": "area", "feature2": "bedrooms"}),
            ("/interactionsummary", {"feature": "area"}),
        ):
            with self.subTest(route=route):
                result = self.client.post(route, json=data)
                self.assertEqual(result.status_code, 200, result.json)

    def test_frontend_is_served_by_the_api_process(self):
        for route in ("/", "/assets/src/modelrun.js", "/assets/vendor/plotly-2.27.0.min.js"):
            with self.subTest(route=route):
                with self.client.get(route) as response:
                    self.assertEqual(response.status_code, 200)
