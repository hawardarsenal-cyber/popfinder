const backend = "https://popfinder-backend-production.up.railway.app";

document.getElementById("search-btn").addEventListener("click", search);

async function search() {
    const region = document.getElementById("region").value;
    const query = document.getElementById("query").value || ""; // allow empty

    const payload = { query, region };

    const res = await fetch(`${backend}/search`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    let data;

    try {
        data = await res.json();
    } catch {
        data = [{ title: "Error", description: "Invalid backend JSON" }];
    }

    renderResults(data);
}

function renderResults(events) {
    const box = document.getElementById("results");
    box.innerHTML = "";

    if (!events.length) {
        box.innerHTML = "<p>No results found.</p>";
        return;
    }

    events.forEach(ev => {
        const div = document.createElement("div");
        div.className = "event-card";

        div.innerHTML = `
            <h3>${ev.title || "Untitled Event"}</h3>
            <p><strong>Date:</strong> ${ev.date || "Unknown"}</p>
            <p><strong>Location:</strong> ${ev.location || "Unknown"}</p>
            <p>${ev.description || "No description available."}</p>

            ${ev.url ? `<a href="${ev.url}" target="_blank">Source</a>` : ""}
            <br>
            <button onclick='pin(${JSON.stringify(ev)})'>Pin ⭐</button>
        `;

        box.appendChild(div);
    });

    loadPins();
}

async function pin(item) {
    await fetch(`${backend}/pin`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({content: item})
    });
    loadPins();
}

async function saveNotes() {
    const text = document.getElementById("notes-box").value;

    await fetch(`${backend}/notes`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text})
    });

    alert("Notes saved!");
}

async function loadPins() {
    const res = await fetch(`${backend}/pins`);
    const pins = await res.json();

    const box = document.getElementById("pins");
    box.innerHTML = "";

    pins.forEach(ev => {
        const div = document.createElement("div");
        div.className = "pin-card";

        div.innerHTML = `<p><strong>${ev.title}</strong></p>`;
        box.appendChild(div);
    });
}
