import numpy as np
import plotly.graph_objs as go
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import shap
from sklearn.model_selection import train_test_split
import pandas as pd
import explainerdashboard
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import json
from sklearn.svm import SVC, SVR

# Colorscale
bright_cscale = [[0, "#ff3700"], [1, "#0b8bff"]]
cscale = [
    [0.0000000, "#ff744c"],
    [0.1428571, "#ff916d"],
    [0.2857143, "#ffc0a8"],
    [0.4285714, "#ffe7dc"],
    [0.5714286, "#e5fcff"],
    [0.7142857, "#c8feff"],
    [0.8571429, "#9af8ff"],
    [1.0000000, "#20e6ff"],
]


def get_range(arr):

    MIN=min(arr)
    MAX=max(arr)

    return [MIN-(MAX-MIN)*0.05,MAX+(MAX-MIN)*0.05]

# get model metrics
def getMetrics(y,y_pred,model_type='classifier'):
    if model_type == 'classifier':
        from sklearn.metrics import classification_report
        report = classification_report(y, y_pred, output_dict=True)
        # convert the classification report to a dataframe
        report = pd.DataFrame(report).transpose()
        # convert the dataframe to json
        report = report.to_json()
        # print(report)
        return report
    else:
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        mae = mean_absolute_error(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y, y_pred)
        

        metric_dict = {'Mean Absolute Error (MAE)': mae, 'Mean Squared Error (MSE)': mse, 'Root Mean Squared Error (RMSE)': rmse, 'R-Squared (R2)': r2}
        # convert the dictionary to a json
        metric_dict = json.dumps(metric_dict)
        # return the json
        return metric_dict

    

# feature importance using shapely values
def getShapFigure(model,X,y,model_type='classifier'):
    
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    fig = explainer.plot_importances()
    # add hover info
    fig.update_traces(hovertemplate="ID: %{pointIndex}<br>Feature: %{y}<br>Importance: %{x}")
    return fig.to_json()

# get individual feature importance
def getIndividualShap(model,X,y,feature,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    

    fig = explainer.plot_dependence(feature)
    
    # set color value to the fig based on the y value
    fig['data'][0]['marker']['color'] = y
    
    # check the number of unique values in the feature
    if len(X[feature].unique()) < 7:
        # get x and y values from the figure
        x = fig['data'][0]['x']
        y = fig['data'][0]['y']

        # create a violin plot using plotly express
        fig = px.violin(x=x, y=y, color=x)
        # add title
        fig.update_layout(title=f'Dependence plot for {feature}')
    
    # add x and y axis labels
    fig.update_xaxes(title=feature)
    fig.update_yaxes(title='Dependence from SHAP Value')
    
    
    # add hover info with id, feature and shap value
    fig.update_traces(hovertemplate="ID:%{pointIndex}<br>Feature: %{x}<br>SHAP Value: %{y}")

    return fig.to_json()

# get feature interaction
def getInteraction(model,X,y,feature1,feature2,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    fig = explainer.plot_interaction(feature1,feature2)

    # check the number of unique values in the feature
    if len(X[feature1].unique()) < 7 and len(X[feature2].unique()) < 7:
        # get x and y values from the figure
        x = fig['data'][0]['x']
        y = fig['data'][0]['y']

        # create a violin plot using plotly express
        fig = px.violin(x=x, y=y, color=x)
        # add title
        fig.update_layout(title=f'Interaction plot for {feature1} and {feature2}')

    # add x and y axis labels
    fig.update_xaxes(title=feature1)
    fig.update_yaxes(title='Interaction from SHAP Value')

    # add hover info
    fig.update_traces(hovertemplate="ID:%{pointIndex}<br>Feature 1 value: %{x}<br>Prediction Value: %{y}")
    return fig.to_json()


# get feature interaction
def getContribution(model,X,y,indx,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    fig = explainer.plot_contributions(index=indx, topx=5)
    
    return fig.to_json()

# get feature interaction
def getInteractionSummary(model,X,y,feature,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    fig = explainer.plot_interactions_detailed(feature, topx=5)
    
    # add hover info
    fig.update_traces(hovertemplate="ID:%{pointIndex}<br>Predicted Value: %{x}<br>SHAP Value: %{y}")

    return fig.to_json()

# get auc
def getPr(model,X,y,cut_off,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
        fig = explainer.plot_pr_auc(cutoff=cut_off)
        # add hover info
        #fig.update_traces(hovertemplate="Precision: %{x}<br>Recall: %{y}<br>Threshold: %{z}")
        return fig.to_json()
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
        fig = explainer.plot_residuals()
        return fig.to_json()
    
    

# get auc
def getRoc(model,X,y,cut_off,model_type='classifier',feature=None):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
        fig = explainer.plot_roc_auc(cutoff=cut_off)
        # add hover info
        #fig.update_traces(hovertemplate="False Positive Rate: %{x}<br>True Positive Rate: %{y}<br>Threshold: %{z}")
        return fig.to_json()
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
        fig = explainer.plot_residuals_vs_feature(feature)
        return fig.to_json()

    
    

# get feature partial
def getPartial(model,X,y,feature,model_type='classifier'):
    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
    
    fig = explainer.plot_pdp(feature)
    # add hover info
    fig.update_traces(hovertemplate="Feature Value: %{x}<br>SHAP Value: %{y}")
    return fig.to_json()

def getConfusion(model,X,y, model_type='classifier'):

    # check if y is numeric or not
    if y.dtype == 'object':
        # convert y to numeric
        label_encoder = LabelEncoder()
        y=label_encoder.fit_transform(y)
    
    # create a shap explainer
    if model_type == 'classifier':
        explainer = explainerdashboard.ClassifierExplainer(model, X, y)
        # get confusion matrix
        fig = explainer.plot_confusion_matrix(cutoff=0.5, percentage=True)
        # add hover info
        fig.update_traces(hovertemplate="Predicted: %{x}<br>Actual: %{y}<br>Percentage: %{z:.2f}")

    else:
        explainer = explainerdashboard.RegressionExplainer(model, X, y)
        # get actual vs predicted
        fig = explainer.plot_predicted_vs_actual()
        # add hover info
        fig.update_traces(hovertemplate="Actual: %{y}<br>Predicted: %{x}")
        
            
    return fig.to_json()

def dtree_model(X,y,dtree_depth,leaves, model_type='classifier'):
    if model_type == 'classifier':
        model=DecisionTreeClassifier(max_depth=dtree_depth, random_state=0, min_samples_leaf=leaves)
    else:
        model=DecisionTreeRegressor(max_depth=dtree_depth, random_state=0, min_samples_leaf=leaves)
    model.fit(X,y)
    return model

def random_forest_model(X,y,tree_depth,leaves, model_type='classifier'):
    if model_type == 'classifier':
        model=RandomForestClassifier(max_depth=tree_depth, random_state=0, min_samples_leaf=leaves)
    else:
        model=RandomForestRegressor(max_depth=tree_depth, random_state=0, min_samples_leaf=leaves)
    
    model.fit(X,y)
    return model

def svm_model(X,y, model_type='classifier'):
    if model_type == 'classifier':
        model=SVC()
    else:
        model=SVR()
    
    model.fit(X,y)
    return model

def decision_figure(X,y,dtree_depth, feature1="", feature2="", label="",model_type='decision-tree'):
    h =mesh_step= 0.3  # step size in the mesh
    threshold=0.5

    x_min = X[:, 0].min() - 1.5
    x_max = X[:, 0].max() + 1.5
    y_min = X[:, 1].min() - 1.5
    y_max = X[:, 1].max() + 1.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    y=np.array(y)
    label_encoder = LabelEncoder()

    frames=[]

    for depth in range(1,dtree_depth+1):
        print('Running for depth: ',depth)
        if model_type == 'decision-tree':
            model=DecisionTreeClassifier(max_depth=depth)
        elif model_type == 'random-forest':
            model=RandomForestClassifier(max_depth=depth)

        model.fit(X,y)
        Z = model.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
        scaled_threshold = threshold * (Z.max() - Z.min()) + Z.min()
        Range = max(abs(scaled_threshold - Z.min()), abs(scaled_threshold - Z.max()))
        
        trace0 = go.Contour(
            x=np.arange(xx.min(), xx.max(), mesh_step),
            y=np.arange(yy.min(), yy.max(), mesh_step),
            z=Z.reshape(xx.shape),
            zmin=scaled_threshold - Range,
            zmax=scaled_threshold + Range,
            hoverinfo="none",
            showscale=False,
            contours=dict(showlines=False),
            colorscale=cscale,
            opacity=0.9,
        )

        # Plot the threshold
        trace1 = go.Contour(
            x=np.arange(xx.min(), xx.max(), mesh_step),
            y=np.arange(yy.min(), yy.max(), mesh_step),
            z=Z.reshape(xx.shape),
            showscale=False,
            hovertemplate="Threshold: %{z:.2f}",
            name='Boundary',
            contours=dict(
                showlines=False, type="constraint", operation="=", value=scaled_threshold
            ),
            line=dict(color="#708090"),
        )

        # Plot Training Data
        trace2 = go.Scatter(
            x=X[:, 0],
            y=X[:, 1],
            mode="markers",
            name='Data',
            hovertemplate="Feature 1: %{x:.2f}<br>Feature 2: %{y:.2f}<br>Prediction: %{text}",
            text=label_encoder.fit_transform(y),
            marker=dict(size=10, color=label_encoder.fit_transform(y), colorscale=bright_cscale),
        )
        layout = go.Layout(
            xaxis=dict(ticks="", showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(ticks="", showticklabels=False, showgrid=False, zeroline=False),
            hovermode="closest",
            legend=dict(x=0, y=-0.01, orientation="h"),
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="#282b38",
            paper_bgcolor="#FAF9F6",
            font={"color": "#a5b1cd"},
            # x and y axis labels
            xaxis_title=feature1,
            yaxis_title=feature2,
        )

        data = [trace0, trace1, trace2]

        frames.append(go.Frame(data=data,layout=layout))

    all_frames_json = [frame.to_json() for frame in frames]

    return all_frames_json