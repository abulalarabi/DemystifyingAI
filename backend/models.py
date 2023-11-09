import numpy as np
import plotly.graph_objs as go
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import plotly.express as px

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


def get_confusion_fig(X,y_true,model):

    y_pred=model.predict(X)
    z=confusion_matrix(y_true, y_pred)
    fig = px.imshow(z,labels=dict(x="Predicted", y="Actual",title='Confusion Matrix'), y=np.unique(y_true) ,x=np.unique(y_true),text_auto=True, aspect="auto")
    
    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': '#FAF9F6',
    })

    fig.update_layout(
    title={
        'text': "Confusion Matrix",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

    # return fig
    # return json format figure
    return fig.to_json()

def dtree_model(X,y,dtree_depth,leaves):
    
    model=DecisionTreeClassifier(max_depth=dtree_depth)
    model.fit(X,y)
    
    # get the confusion matrix
    confusion_fig=get_confusion_fig(X,y,model)

    return confusion_fig

def dtree_figure(X,y,dtree_depth, feature1="", feature2="", label=""):
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
        model=DecisionTreeClassifier(max_depth=depth)
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
            # show feature 1 name and value, feature 2 name and value, and label name and value
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