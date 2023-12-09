# DemystifyingAI
Machine learning is currently like a black box. It is difficult to understand what and how the models learn. The central objective is to facilitate user empowerment by furnishing them with visual representations of machine-learning models and how different features contribute to the learned model via an intuitively accessible interface. This will, in turn, equip users with the capacity to delve into, comprehend, and deliberate upon the predictions generated by artificial intelligence models, thus enabling them to make well-informed decisions. The overarching goal is to serve as a conduit between the realm of artificial intelligence technology and its tangible utility, thereby fostering an ethos of transparency.

### Example
![Classification Example](example.png "Classification Example")

### Installation Manual for Python Backend

---

#### Overview

This manual guides you through setting up a Python web application utilizing Flask for web functionalities and various machine learning libraries for data processing and analysis.

#### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

#### Dependencies

- Flask
- Pandas
- scikit-learn
- Flask-CORS
- Plotly
- SHAP
- ExplainerDashboard

---

#### Installation Steps

**1. Environment Setup**

   - Create a virtual environment to avoid conflicts with other projects:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```bash
       venv\Scripts\activate
       ```
     - On Unix or MacOS:
       ```bash
       source venv/bin/activate
       ```

**2. Install Required Libraries**

   - Install all the required Python libraries using pip:
     ```bash
     pip install Flask pandas scikit-learn Flask-CORS plotly shap explainerdashboard
     ```

**3. Running the Application**

   - Navigate to the project directory/backend and run the Flask app:
     ```bash
     python backend.py
     ```
   - The Flask application should start and be accessible via `http://localhost:1407` or the configured port.


### Web Application Setup Guide

---

## Overview
This guide provides instructions for setting up an environment to run a HTML and JavaScript-based web application.

## Prerequisites

1. **Web Browser**: 
   - Ensure a web browser is installed on your system, preferably Google Chrome. Download from [google.com/chrome](https://www.google.com/chrome/).

2. **VS Code**: 
   - Recommended IDE for easy running of the application. Download from [Visual Studio Code](https://code.visualstudio.com/).

---

## Steps to Set Up Environment

**1. Install Live Server in VSCode**:
   - Open VSCode.
   - Install the Live Server extension for real-time page reloading.

**2. Set Up the Web Application**:
   - Ensure all necessary files (e.g., `Assets/logo.png`) are in one project directory.
   - Open the project directory in VSCode.

**3. Run the Application**:
   - Right-click on `login.html` in VSCode.
   - Select `Open with Live Server`.
   - The application will open in your default browser.

---

## Alternate Steps

### Dependencies

- **Install Node.js and NPM**: 
  - For Windows users, follow the tutorial [here](https://github.com/abulalarabi/nodejs_windows).

### Running the Application

**1. Set Up a Server**:
   - Open a terminal or PowerShell in the project directory.
   - Run the command to install Express:
     ```bash
     npm install express --save
     ```

**2. Start the Server**:
   - Run the following command to start a local server on port 3000:
     ```bash
     node app.js
     ```
   - Open a web browser and navigate to `127.0.0.1:3000`.
   - The `login.html` page should be displayed.

---

These steps will help you set up and run the web application either through VSCode with Live Server for a simpler approach, or using Node.js for a more traditional server setup.
#### Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Plotly Python Graphing Library](https://plotly.com/python/)
- [SHAP Library](https://github.com/slundberg/shap)
- [ExplainerDashboard on GitHub](https://github.com/oegedijk/explainerdashboard)
