<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PopFinder – Event & Pop-Up Opportunity Radar</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f9;
            margin: 0;
            padding: 0;
        }

        header {
            background: #222;
            color: white;
            padding: 20px 40px;
            font-size: 24px;
            letter-spacing: 0.5px;
        }

        .container {
            max-width: 900px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }

        h2 {
            margin-top: 0;
            font-weight: 600;
        }

        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
        }

        .search-bar input, .search-bar select {
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
            flex: 1;
        }

        .search-btn {
            padding: 10px 20px;
            background: #0078ff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }

        .event-card {
            padding: 20px;
            background: #fafafa;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
        }

        .event-card h3 {
            margin: 0 0 5px 0;
        }

        .loading {
            text-align: center;
            font-size: 18px;
            padding: 20px;
        }

        .error {
            color: red;
            margin-bottom: 20px;
            font-weight: bold;
        }

    </style>
</head>

<body>

<header>PopFinder — Discover Events & Pop-Up Locations</header>

<div class="container">

    <h2>Find Opportunities</h2>

    <div class="error" id="error"></div>

    <div class="search-bar">
        <input type="text" id="keywords" placeholder="Try: markets, festivals, exhibitions, food events…">
        <select id="region">
            <option>London</option>
            <option>Manchester</option>
            <option>Birmingham</option>
            <option>Glasgow</option>
            <option>Liverpool</option>
        </select>

        <button class="search-btn" onclick="searchEvents()">Search</button>
    </div>

    <div id="results"></div>

</div>

<script>
async function searchEvents() {
    const keywords = document.getElementById("keywords").value.trim();
    const region = document.getElementById("region").value;
    const resultsBox = document.getElementById("results");
    const errorBox = document.getElementById("error");

    errorBox.textContent = "";
    resultsBox.innerHTML = `<div class="loading">Searching opportunities…</div>`;

    try {
        const response = await fetch("backend_proxy.php", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded"},
            body: `keywords=${encodeURIComponent(keywords)}&region=${encodeURIComponent(region)}`
        });

        const data = await response.json();

        resultsBox.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            resultsBox.innerHTML = `<div>No events found. Try a different search.</div>`;
            return;
        }

        data.forEach(event => {
            const card = document.createElement("div");
            card.className = "event-card";

            card.innerHTML = `
                <h3>${event.title || "Untitled Event"}</h3>
                <p><strong>Date:</strong> ${event.date || "Unknown"}</p>
                <p><strong>Location:</strong> ${event.location || "Unknown"}</p>
                <p>${event.description || "No description available."}</p>
                <p><a href="${event.url}" target="_blank">Source →</a></p>
                <p><strong>Opportunity Score:</strong> ${event.score}</p>
            `;
            resultsBox.appendChild(card);
        });

    } catch (e) {
        console.error(e);
        resultsBox.innerHTML = "";
        errorBox.textContent = "Error: Could not reach backend.";
    }
}


// Auto-load initial suggestions
window.onload = () => {
    document.getElementById("keywords").value = "markets";
    searchEvents();
};
</script>

</body>
</html>
