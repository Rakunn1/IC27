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
  <li>Data Layer</li>
  <li>Configuration and Utilities</li>
</ol>

<h4><i>1. Web Application Layer</i></h4>
<p>The Flask-based web application features two sections: IC27 predictor and Orchestration.</p>
<p>The <b>IC27 Predictor</b> is designed to address Janna's problem - predicting whether she can arrive on time via train. To make a prediction, click the green button, which generates a description, answere, and a graph showing train delay data along with regression curve used for prediction.</p>
<p>In the <b>Orchestration</b> section, user can download data for a specified period. This data is stored on database and used for predictions.</p>

<h4><i>2. Data Layer</i></h4>
<p></p>
