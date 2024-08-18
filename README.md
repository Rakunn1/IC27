<h3><i>IC27 project.</i></h3>
<h3><i>Dedicated to predicting ETA of a train based on Open Data Portal of the Finnish Transport Agency; with extra ETL layer.</i></h3>

<i><h3>Launching an app:</i></h3>
<ul>
<li>Download project and extract in destination of your choice</li>
<li>Remember to place config.ini file in project directory</li>
<li>To run the project you need to install Python 3.8 or higher and install requirements. To do so run the command from the directory you extracted the project to: pip install -r requirements.txt</li>
<li>Next, launch the app: python IC27_app.py</li>
<li>app is hosted at http://localhost:5000</li>
</ul>
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
<p>Hstorical data from the actual arrival times of the trains is used to make predictions. The Open Data Portal of the Finnish Traffic Agency 
 provides an API for querying the railway traffic history. A subset of the retrieved data is stored in a Snowflake database and queried during predictions.</p>
 <p>The <b>ETL process</b> is implemented via the Fetch Period feature in Orchestration section. This process involves validating the database connection, fetching data for each date within the selected period, selecting relevant fields, and storing the data in the database. Data is only inserted if it isn't already present in the ODS table and a staging table is utilized to ensure maximum accessibility.</p>
 <p>For <b>predictions</b>, the database is queried for historical differences between actual and scheduled arrival times at Tampere Station. This data is then used to calculate the expected delay, which is added to the scheduled arrival time for the next Thursday, fetched from the API.</p>

<h4><i>3. Configuration and Utilities</i></h4>
<p>The configuration settings and utility functions are abstracted into separate files: <i>config.ini</i> centralizes credentials, while <i>tab_config.py</i> contains the DDLs for database structures, the <i>db_initialization.py</i> script is used when setting up a new Snowflake account, creating structures required for the project.</p>
