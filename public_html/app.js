const API = "https://popfinder-backend-production.up.railway.app";

async function runSearch() {
    const prompt = document.getElementById("prompt").value;
    const region = document.getElementById("region").value;

    document.getElementById("results").innerHTML = "Searching...";

    const res = await fetch(`${API}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, region })
    });

    const data = await res.json();
    renderResults(data);
}

function renderResults(data) {
    const box = document.getElementById("results");
    box.innerHTML = "";

    if (!Array.isArray(data)) {
        box.innerHTML = `<p>Error: ${data.error}</p>`;
        return;
    }

    data.forEach(ev => {
        const card = document.createElement("div");
        card.className = "event";

        card.innerHTML = `
            <h3>${ev.title || "Untitled Event"}</h3>
            <p><strong>Date:</strong> ${ev.date || "Unknown"}</p>
            <p><strong>Location:</strong> ${ev.location || "Unknown"}</p>
            <p>${ev.description || ""}</p>
            <button onclick='pinEvent(${JSON.stringify(ev)})'>⭐ Pin</button>
        `;

        box.appendChild(card);
    });
}

async function pinEvent(ev) {
    await fetch(`${API}/pin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event: ev })
    });
    alert("Pinned!");
}
