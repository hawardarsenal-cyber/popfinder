async function runSearch() {
    const keywords = document.getElementById("keywords").value;
    const region = document.getElementById("region").value;

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Searching...</p>";

    const response = await fetch("https://popfinder-backend-production.up.railway.app/search", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ keywords, region })
    });

    const data = await response.json();

    if (!data.length) {
        resultsDiv.innerHTML = "<p>No results found.</p>";
        return;
    }

    resultsDiv.innerHTML = "";

    data.forEach(ev => {
        const card = document.createElement("div");
        card.className = "event-card";

        card.innerHTML = `
            <h3>${ev.title || "No title"}</h3>
            <p><strong>Date:</strong> ${ev.date || "Unknown"}</p>
            <p><strong>Location:</strong> ${ev.location || "Unknown"}</p>
            <p>${ev.description || ""}</p>
            <p><a href="${ev.url}" target="_blank">Source</a></p>
        `;

        resultsDiv.appendChild(card);
    });
}
