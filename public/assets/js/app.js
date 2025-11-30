function runSearch() {
    const formData = new FormData();
    formData.append("keywords", document.getElementById("keywords").value);
    formData.append("region", document.getElementById("region").value);

    fetch("api_search.php", {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        let html = "";
        data.forEach(ev => {
            html += `
                <div class="event-box">
                    <h3>${ev.title}</h3>
                    <p><strong>Location:</strong> ${ev.location}</p>
                    <p><strong>Date:</strong> ${ev.date}</p>
                    <p><strong>Score:</strong> ${ev.score}</p>
                    <a href="${ev.url}" target="_blank">View</a>
                    <button onclick="pinEvent('${encodeURIComponent(JSON.stringify(ev))}')">Pin</button>
                </div>
            `;
        });
        document.getElementById("results").innerHTML = html;
        loadPins();
    });
}

function pinEvent(data) {
    const ev = new FormData();
    ev.append("event", data);

    fetch("api_pin.php?action=add", {
        method: "POST",
        body: ev
    }).then(() => loadPins());
}

function loadPins() {
    fetch("api_pin.php?action=list")
    .then(r => r.json())
    .then(data => {
        let html = "";
        data.forEach(p => {
            html += `<div class="pin-box">
                        <h4>${p.title}</h4>
                        <button onclick="removePin('${p.id}')">Remove</button>
                     </div>`;
        });
        document.getElementById("pinned").innerHTML = html;
    });
}

function removePin(id) {
    fetch("api_pin.php?action=remove&id=" + id)
    .then(() => loadPins());
}

function saveNote() {
    const fd = new FormData();
    fd.append("text", document.getElementById("newNote").value);

    fetch("api_notes.php?action=add", {
        method: "POST",
        body: fd
    }).then(() => loadNotes());
}

function loadNotes() {
    fetch("api_notes.php?action=list")
    .then(r => r.json())
    .then(notes => {
        let html = "";
        notes.forEach(n => {
            html += `<div class="note-box">${n.text}</div>`;
        });
        document.getElementById("notes").innerHTML = html;
    });
}

function runSearch() {
    const fd = new FormData();
    fd.append("keywords", document.getElementById("keywords").value);
    fd.append("region", document.getElementById("region").value);

    fetch("api_search.php", {
        method: "POST",
        body: fd
    })
    .then(r => r.json())
    .then(data => {
        let html = "";

        if (data.error) {
            html = `<p style="color:red">${data.error}</p>`;
        } else {
            data.forEach(ev => {
                html += `
                    <div class="event-box">
                        <h3>${ev.title}</h3>
                        <p><strong>Location:</strong> ${ev.location}</p>
                        <p><strong>Date:</strong> ${ev.date}</p>
                        <p><strong>Footfall:</strong> ${ev.estimated_footfall}</p>
                        <p><strong>Score:</strong> ${ev.score}</p>
                        <a href="${ev.source_url}" target="_blank">Open Source</a>
                    </div>
                `;
            });
        }

        document.getElementById("results").innerHTML = html;
    });
}


loadPins();
loadNotes();
