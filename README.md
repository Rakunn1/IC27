<h3><i>IC27 project. Dedicated to predicting ETA of a train based on Open Data Portal of the Finnish Transport Agency; with extra ETL layer.</i></h3>

<b>Launching an app:</b>
<ul>
<li>Download project and extract in destination of your choice</li>
<li>Remember to place config.ini file in project directory</li>
<li>To run the project you need to install Python 3.8 or higher and install requirements. To do so run the command from the directory you extracted the project to: pip install -r requirements.txt</li>
<li>Next, launch the app: python IC27_app.py</li>
<li>app is hosted at http://localhost:5000</li>
</ul>
</br>
<h3><i>Application overview</i></h3>
<ol>
  <li>Web Application Layer</li>
  <li>ETL pipelines</li>
  <li>Database Layer</li>
  <li>Configuration and Utilities</li>
</ol>

<h4><i>1. Web Application Layer</i></h4>
<p>The web app is an interface between user and the backend. It contains of 2 sections: IC27 predictor and Orchestration. First of which is dedicated to solving Janna's problem - predicting if she is able to arrive on time via train. To make a prediction click green button. It will generate description, ansewere and graph with actual data points of train delays and regression curve on which prediction is made. In second section, Orchestration, it is possible to download data, for given perion. The data is saved on database and later used for prediction.</p>
<p>The web app is built in Flask Framework connected with user-facing HTML via JavaScript. [...]</p>
