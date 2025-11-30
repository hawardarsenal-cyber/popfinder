<!DOCTYPE html>
<html>
<head>
    <title>Pop-Up Opportunity Finder</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<h1>Pop-Up Opportunity Finder</h1>

<div class="search-block">
    <label>Search Keywords:</label>
    <input id="keywords" type="text" placeholder="markets, fairs, exhibitions...">

    <label>Choose region:</label>
    <select id="region">
        <option value="London">London (Default)</option>
        <option value="Kent">Kent</option>
        <option value="Other">Other UK Region</option>
    </select>

    <button onclick="runSearch()">Search</button>
</div>

<hr>

<h2>Results</h2>
<div id="results"></div>

<hr>

<h2>Pinned Opportunities</h2>
<div id="pinned"></div>

<hr>

<h2>Notes</h2>
<textarea id="newNote" placeholder="Write a note..."></textarea><br>
<button onclick="saveNote()">Save Note</button>

<div id="notes"></div>

<script src="assets/js/app.js"></script>
</body>
</html>
