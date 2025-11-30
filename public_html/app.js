document.getElementById("searchBtn").addEventListener("click", async () => {
    const location = document.getElementById("locationSelect").value;
    const keyword = document.getElementById("keywordInput").value;

    const resultsBox = document.getElementById("results");
    resultsBox.innerHTML = "Searching...";

    try {
        const response = await fetch("https://popfinder-backend-production.up.railway.app/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                location: location,
                keyword: keyword
            })
        });

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            resultsBox.innerHTML = "No results found.";
            return;
        }

        resultsBox.innerHTML = "";
        data.forEach(ev => {
            const div = document.createElement("div");
            div.className = "event-card";
            div.innerHTML = `
                <h3>${ev.title || "Untitled Event"}</h3>
                <p><strong>Date:</strong> ${ev.date || "Unknown"}</p>
                <p><strong>Location:</strong> ${ev.location || "Unknown"}</p>
                <p>${ev.description || "No description."}</p>
                <a href="${ev.url}" target="_blank">Source</a>
                <button class="pin-btn" data-event='${JSON.stringify(ev)}'>📌 Pin</button>
            `;
            resultsBox.appendChild(div);
        });

    } catch (err) {
        console.error(err);
        resultsBox.innerHTML = "Error connecting to backend.";
    }
});
