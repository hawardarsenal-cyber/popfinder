<!DOCTYPE html>
<html>
<head>
    <title>PopFinder</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

<div class="container">

    <header>
        <h1>PopFinder</h1>
        <p class="subtitle">Discover opportunities, markets, events & footfall hotspots across the UK.</p>
    </header>

    <section class="search-section">
        <div class="search-controls">
            <select id="region">
                <option>London</option>
                <option>Kent</option>
                <option>UK</option>
                <option>Custom</option>
            </select>

            <input id="query" placeholder="Optional search keyword (leave empty for full scan)">
            
            <button id="search-btn" onclick="search()">Search</button>
        </div>
    </section>

    <section id="results" class="results-section">
        <!-- Results appear here -->
    </section>

    <section class="notes-section">
        <h2>Notes</h2>
        <textarea id="notes-box" placeholder="Write notes here..."></textarea>
        <button onclick="saveNotes()">Save Notes</button>
    </section>

    <section class="pinned-section">
        <h2>⭐ Pinned Events</h2>
        <div id="pins"></div>
    </section>

</div>

<script src="script.js"></script>
</body>
</html>
