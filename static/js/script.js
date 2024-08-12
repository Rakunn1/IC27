document.addEventListener('DOMContentLoaded', function () {
// function utilized in Orchestration
    const fetch_form = document.getElementById('fetch-form');
    const logsDiv = document.getElementById('logs');
    fetch_form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);

        fetch('/fetch-period', {
            method: 'POST',
            body: new URLSearchParams(formData)
        })
          .then(response => {
            const reader = response.body.getReader()
            const decoder = new TextDecoder("utf-8");function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        console.log('Stream finished.');
                        return;
                    }

                    const chunk = decoder.decode(value, { stream: true });
                    console.log(chunk);

                    logsDiv.innerHTML += '<p>' + chunk + '</p>';
                    logsDiv.scrollTop = logsDiv.scrollHeight;

                    read();
                });
            }

            read();
        })
        .catch((err) => console.error('Error: ', err));
    });
});


function makePrediction() {
// function utilized in IC27 predictor
    const eventSource = new EventSource('/predict');
    const prediction_div = document.getElementById('prediction_log');
    prediction_div.innerHTML = "";
    eventSource.onmessage = function(event) {
        prediction_div.innerHTML += '<p>' + event.data + '</p>';
    };

    eventSource.onerror = function(event) {
        console.error("EventSource error:", event);
        eventSource.close();
    };

    fetch('/generate-plot')
        .then(response => response.text())
        .then(data => {
            const plotDiv = document.getElementById('plot-div');
            const plotImg = document.getElementById('plot-img');
            plotImg.src = 'data:image/png;base64,' + data;
            plotDiv.style.display = 'block';

            plotImg.onclick = function() {
                openModal(this.src);
            };
        })
        .catch(error => console.error('Error fetching plot:', error));
}

function openModal(src) {
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");
    modal.style.display = "block";
    modalImg.src = src;
}

function closeModal() {
    const modal = document.getElementById("myModal");
    modal.style.display = "none";
}