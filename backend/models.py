import json
from dataclasses import dataclass, field
from functools import cached_property
from secrets import token_hex

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from explainerdashboard import ClassifierExplainer, RegressionExplainer
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    r2_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


class InputError(ValueError):
    pass


MODEL_NAMES = {"decision-tree", "random-forest", "svm"}
TREE_MODELS = {
    "decision-tree": (DecisionTreeClassifier, DecisionTreeRegressor),
    "random-forest": (RandomForestClassifier, RandomForestRegressor),
}


def number(value, name, minimum, maximum, *, integer=False):
    try:
        parsed = float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise InputError(f"{name} must be a number.") from error
    if isinstance(value, bool) or not minimum <= parsed <= maximum:
        raise InputError(f"{name} must be between {minimum} and {maximum}.")
    if integer:
        if not parsed.is_integer():
            raise InputError(f"{name} must be a whole number.")
        return int(parsed)
    return parsed


def fit_model(name, classifier, X, y, depth, leaves):
    if name == "svm":
        if classifier:
            model = make_pipeline(StandardScaler(), SVC(probability=True, random_state=42))
        else:
            model = TransformedTargetRegressor(
                regressor=make_pipeline(StandardScaler(), SVR()),
                transformer=StandardScaler(),
            )
    else:
        estimator = TREE_MODELS[name][0 if classifier else 1]
        model = estimator(max_depth=depth, random_state=0, min_samples_leaf=leaves)
    return model.fit(X, y)


def train(dataset, options):
    name = options.get("model")
    if not isinstance(name, str) or name not in MODEL_NAMES:
        raise InputError("Select Decision Tree, Random Forest, or Support Vector Machine.")
    model_type = options.get("model_type")
    if model_type not in ("classifier", "regression"):
        raise InputError("Select classification or regression.")
    classifier = model_type == "classifier"
    target = options.get("target")
    if not isinstance(target, str) or target not in dataset:
        raise InputError("Select a target column from the uploaded CSV.")
    excluded = options.get("filter_columns", [])
    if not isinstance(excluded, list) or any(not isinstance(col, str) or col not in dataset for col in excluded):
        raise InputError("Choose filters from the uploaded CSV.")
    features = [col for col in dataset if col != target and col not in excluded]
    if not features:
        raise InputError("Keep at least one feature column.")
    split = number(options.get("split"), "Training fraction", 0.01, 0.99)
    depth = leaves = None
    if name != "svm":
        depth = number(options.get("max_depth"), "Maximum depth", 1, 10, integer=True)
        leaves = number(options.get("leaves"), "Minimum samples per leaf", 1, 100, integer=True)

    selected = dataset[[*features, target]]
    if selected.isna().any().any() or not np.isfinite(selected.select_dtypes(include="number")).all().all():
        raise InputError("Remove missing or infinite values from the selected columns.")
    raw_y = dataset[target]
    if not classifier and not pd.api.types.is_numeric_dtype(raw_y):
        raise InputError("Regression requires a numeric target.")

    labels = None
    if classifier:
        encoder = LabelEncoder()
        y = pd.Series(encoder.fit_transform(raw_y), index=raw_y.index, name=target)
        labels = encoder.classes_.astype(str).tolist()
        if len(labels) < 2 or y.value_counts().min() < 2:
            raise InputError("Classification needs at least two classes with at least two rows each.")
    else:
        y = raw_y.astype(float)

    train_rows = int(len(dataset) * split + 1e-9)
    min_rows = max(2, len(labels or []))
    if min(train_rows, len(dataset) - train_rows) < min_rows:
        raise InputError("Choose a split with enough rows for both training and testing.")
    X_train, X_test, y_train, y_test = train_test_split(
        dataset[features], y, train_size=train_rows, random_state=42,
        stratify=y if classifier else None,
    )
    if classifier and min(y_train.nunique(), y_test.nunique()) < len(labels):
        raise InputError("Choose a split that leaves examples of every class in both sets.")

    # Fit category codes on training rows. The fallback code covers unseen test categories.
    numeric = []
    for feature in features:
        if pd.api.types.is_numeric_dtype(X_train[feature]):
            numeric.append(feature)
        else:
            categories = {value: code for code, value in enumerate(sorted(X_train[feature].unique()))}
            X_train[feature] = X_train[feature].map(categories)
            X_test[feature] = X_test[feature].map(categories).fillna(-1)

    X_train = X_train.astype(float)
    X_test = X_test.astype(float)
    model = fit_model(name, classifier, X_train, y_train, depth, leaves)
    return ModelRun(name, model, X_train, X_test, y_train, y_test, labels, numeric, depth, leaves)


@dataclass
class ModelRun:
    name: str
    model: object
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    labels: list[str] | None
    numeric_features: list[str]
    depth: int | None
    leaves: int | None
    id: str = field(default_factory=lambda: token_hex(16))

    @cached_property
    def evaluation(self):
        return self.make_explainer(self.X_test, self.y_test)

    @cached_property
    def explanation(self):
        # Kernel SHAP scales with background size, feature count, and explained rows.
        if self.name == "svm" and len(self.X_test) > 128:
            X = self.X_test.sample(n=128, random_state=42).sort_index()
            return self.make_explainer(X, self.y_test.loc[X.index])
        return self.evaluation

    @cached_property
    def background(self):
        return self.X_train.sample(n=min(16, len(self.X_train)), random_state=42)

    def make_explainer(self, X, y):
        kwargs = {}
        if self.name == "svm":
            kwargs = dict(
                shap="kernel", X_background=self.background,
                shap_kwargs=dict(nsamples=max(64, 2 * X.shape[1] + 32), silent=True, l1_reg="aic"),
            )
        if self.labels:
            return ClassifierExplainer(self.model, X, y, labels=self.labels, **kwargs)
        return RegressionExplainer(self.model, X, y, **kwargs)

    @property
    def output_title(self):
        return f" · Class: {self.labels[1]}" if self.labels else ""

    @cached_property
    def positive_probabilities(self):
        return self.model.predict_proba(self.X_test)[:, 1]

    def summary(self):
        prediction = self.model.predict(self.X_test)
        if self.labels:
            names = self.labels
            if set(names) & {"accuracy", "macro avg", "weighted avg"}:
                names = [f"Class: {label}" for label in names]
            report = classification_report(
                self.y_test, prediction, labels=list(range(len(self.labels))),
                target_names=names, output_dict=True, zero_division=0,
            )
            metrics = pd.DataFrame(report).to_json()
            matrix = confusion_matrix(self.y_test, prediction, normalize="all") * 100
            figure = go.Figure(go.Heatmap(
                x=self.labels, y=self.labels, z=matrix, colorscale="Blues",
                text=np.round(matrix, 1), texttemplate="%{text}%",
                hovertemplate="Predicted: %{x}<br>Actual: %{y}<br>Share of test rows: %{z:.1f}%<extra></extra>",
            ))
            figure.update_layout(xaxis_title="Predicted", yaxis_title="Actual")
            figure.update_xaxes(type="category")
            figure.update_yaxes(type="category", autorange="reversed")
        else:
            mse = mean_squared_error(self.y_test, prediction)
            metrics = json.dumps({
                "Mean Absolute Error (MAE)": mean_absolute_error(self.y_test, prediction),
                "Mean Squared Error (MSE)": mse,
                "Root Mean Squared Error (RMSE)": np.sqrt(mse),
                "R-Squared (R2)": r2_score(self.y_test, prediction),
            })
            figure = self.evaluation.plot_predicted_vs_actual()

        importance = self.explanation.plot_importances()
        importance.update_layout(title=f"Mean absolute SHAP value{self.output_title}")
        importance.update_traces(marker_color=np.abs(importance.data[0].x))
        return dict(
            metrics=metrics, confusion_matrix=figure.to_json(), shap_values=importance.to_json(),
            features=list(self.X_train.columns), boundary_features=self.numeric_features,
            train_rows=len(self.X_train), test_rows=len(self.X_test),
            positive_class=self.labels[1] if self.labels else None,
        )

    def feature(self, data, key):
        value = data.get(key)
        if not isinstance(value, str) or value not in self.X_train:
            raise InputError("Select a feature used by this model.")
        return value

    def plot(self, name, data):
        if name == "decisionboundary":
            first, second = (self.feature(data, key) for key in ("feature1", "feature2"))
            if not self.labels or first == second or not {first, second} <= set(self.numeric_features):
                raise InputError("Select two different numeric features for a classification boundary.")
            return self.decision_frames(first, second)

        if name in ("getpr", "getroc"):
            if self.labels:
                cutoff = number(data.get("cut_off"), "Probability threshold", 0, 1)
                return self.classification_curve(name, cutoff).to_json()
            if name == "getpr":
                return self.evaluation.plot_residuals().to_json()
            feature = self.feature(data, "feature")
            return self.evaluation.plot_residuals_vs_feature(feature).to_json()

        if name == "contribution":
            row = data.get("index")
            if isinstance(row, bool) or not isinstance(row, (int, str)) or str(row) not in self.explanation.idxs:
                raise InputError("Select a row displayed in the feature-dependence chart.")
            return self.contribution(str(row)).to_json()

        if name == "interaction":
            first, second = (self.feature(data, key) for key in ("feature1", "feature2"))
            if first == second:
                raise InputError("Select two different features for interaction.")
            fig = self.interaction(first, second)
        else:
            feature = self.feature(data, "feature")
            if name == "individualshap":
                fig = self.dependence(feature)
            elif name == "partial":
                fig = self.evaluation.plot_pdp(feature, drop_na=False)
                fig.update_layout(title=f"Partial dependence · {feature}")
            else:
                fig = self.interaction_summary(feature)

        fig.update_layout(title_text=(fig.layout.title.text or "") + self.output_title)
        return fig.to_json()

    def classification_curve(self, name, cutoff):
        actual = self.y_test.to_numpy() == 1
        probabilities = self.positive_probabilities
        selected = probabilities >= cutoff
        true_positives = (actual & selected).sum()
        recall = true_positives / actual.sum()
        if name == "getpr":
            precision, recalls, _ = precision_recall_curve(actual, probabilities)
            x, y = recalls, precision
            x_title, y_title = "Recall", "Precision"
            point = (recall, true_positives / selected.sum() if selected.any() else 1.0)
            title = f"Precision–recall (AP {average_precision_score(actual, probabilities):.2f})"
        else:
            x, y, _ = roc_curve(actual, probabilities)
            x_title, y_title = "False positive rate", "True positive rate"
            point = ((~actual & selected).sum() / (~actual).sum(), recall)
            title = f"ROC (AUC {roc_auc_score(actual, probabilities):.2f})"
        fig = go.Figure(go.Scatter(x=x, y=y, mode="lines", name="Curve"))
        fig.add_trace(go.Scatter(
            x=[point[0]], y=[point[1]], mode="markers", name=f"Threshold {cutoff:.2f}",
            marker=dict(size=10, color="#d62728"),
        ))
        return fig.update_layout(
            title=title + self.output_title, xaxis_title=x_title, yaxis_title=y_title,
            legend=dict(orientation="h", y=1.08),
        )

    def contribution(self, row):
        explainer = self.explanation
        values = explainer.get_shap_values_df().iloc[explainer.idxs.get_loc(row)]
        largest = values.abs().nlargest(5).index
        changes = values.loc[largest].tolist()
        names = largest.tolist()
        if len(values) > len(largest):
            names.append("Other features")
            changes.append(values.drop(largest).sum())
        fig = go.Figure(go.Waterfall(
            x=["Baseline", *names, "Prediction"],
            y=[explainer.shap_base_value(), *changes, 0],
            measure=["absolute", *(["relative"] * len(changes)), "total"],
        ))
        return fig.update_layout(title=f"Feature contribution · Row {row}{self.output_title}")

    def dependence(self, feature):
        X = self.explanation.X
        values = self.explanation.get_shap_values_df()[feature]
        x = X[feature].to_numpy()
        row_ids = self.explanation.idxs.tolist()
        if X[feature].nunique() < 7:
            fig = go.Figure()
            for level in sorted(set(x)):
                mask = x == level
                fig.add_trace(go.Violin(
                    name=str(level), x=x[mask], y=values.to_numpy()[mask],
                    points="all", customdata=np.asarray(row_ids)[mask], showlegend=False,
                ))
        else:
            fig = go.Figure(go.Scatter(
                x=x, y=values, mode="markers", customdata=row_ids,
                marker=dict(color=np.abs(values), colorscale="Blues"),
            ))
        fig.update_traces(hovertemplate="Row: %{customdata}<br>Value: %{x}<br>SHAP: %{y}<extra></extra>")
        return fig.update_layout(title=f"SHAP dependence · {feature}", xaxis_title=feature, yaxis_title="SHAP value")

    def interaction(self, first, second):
        if self.name != "svm":
            return self.explanation.plot_interaction(first, second)
        effects = self.svm_interaction(first, second)
        X = self.explanation.X
        return go.Figure(go.Scatter(
            x=X[first], y=effects, mode="markers",
            marker=dict(color=X[second], colorscale="Viridis", colorbar=dict(title=second)),
        )).update_layout(
            title=f"Estimated SHAP interaction · {first} and {second}",
            xaxis_title=first, yaxis_title="Estimated SHAP interaction",
        )

    def interaction_summary(self, feature):
        others = [col for col in self.X_train if col != feature]
        if not others:
            raise InputError("Interaction summaries require at least two features.")
        if self.name != "svm":
            return self.explanation.plot_interactions_detailed(feature, topx=min(5, len(others)))
        scores = pd.Series({col: np.abs(self.svm_interaction(feature, col)).mean() for col in others})
        top = scores.nlargest(5).sort_values()
        return go.Figure(go.Bar(x=top, y=top.index, orientation="h")).update_layout(
            title=f"Estimated SHAP interactions · {feature}", xaxis_title="Mean absolute interaction",
        )

    def svm_interaction(self, first, second):
        # Estimate the Shapley interaction via the mixed difference for a random
        # coalition excluding the feature pair. Coalition sizes have equal weight.
        X = self.explanation.X.to_numpy()
        background = self.background.to_numpy()
        pair = tuple(sorted(self.X_train.columns.get_loc(col) for col in (first, second)))
        remaining = np.delete(np.arange(X.shape[1]), pair)
        rng = np.random.default_rng(42)
        effects = np.zeros(len(X))
        for _ in range(16):
            cols = rng.permutation(remaining)[:rng.integers(len(remaining) + 1)]
            base = background[rng.integers(len(background), size=len(X))].copy()
            base[:, cols] = X[:, cols]
            left, right, both = base.copy(), base.copy(), base.copy()
            left[:, pair[0]] = X[:, pair[0]]
            right[:, pair[1]] = X[:, pair[1]]
            both[:, pair] = X[:, pair]
            rows = pd.DataFrame(np.concatenate([base, left, right, both]), columns=self.X_train.columns)
            pred = self.model.predict_proba(rows)[:, 1] if self.labels else self.model.predict(rows)
            p0, p1, p2, p12 = np.split(pred, 4)
            effects += p12 - p1 - p2 + p0
        return effects / 32  # Average across 16 draws, with half assigned to each feature.

    def decision_frames(self, first, second):
        X = self.X_train[[first, second]]
        axes = []
        for column in (first, second):
            lo, hi = X[column].min(), X[column].max()
            pad = (hi - lo) * 0.05 or max(abs(lo) * 0.05, 0.5)
            axes.append(np.linspace(lo - pad, hi + pad, 100))
        xx, yy = np.meshgrid(*axes)
        grid = pd.DataFrame({first: xx.ravel(), second: yy.ravel()})
        colors = px.colors.qualitative.Plotly
        count = len(self.labels)
        palette = [colors[i % len(colors)] for i in range(count)]
        scale = [[edge / count, color] for i, color in enumerate(palette) for edge in (i, i + 1)]
        frames = []
        for depth in range(1, (self.depth or 1) + 1):
            model = fit_model(self.name, True, X, self.y_train, depth, self.leaves)
            regions = model.predict(grid).reshape(xx.shape)
            traces = [go.Heatmap(
                x=axes[0], y=axes[1], z=regions, zmin=-0.5, zmax=count - 0.5,
                colorscale=scale, showscale=False, opacity=0.26, hoverinfo="skip",
            )]
            for code, label in enumerate(self.labels):
                points = X.loc[self.y_train == code]
                traces.append(go.Scatter(
                    x=points[first], y=points[second], name=label, mode="markers",
                    marker=dict(color=palette[code], size=7),
                ))
            frames.append(go.Frame(
                data=traces, layout=go.Layout(
                    xaxis_title=first, yaxis_title=second,
                    margin=dict(l=60, r=15, t=22, b=90), legend=dict(orientation="h", y=-0.22),
                ),
            ).to_json())
        return frames
