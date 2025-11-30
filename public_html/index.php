<!DOCTYPE html>
<html>
<head>
    <title>PopFinder</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
    <h1>PopFinder</h1>
    <p>Discover events, pop-up ideas, and vibrant locations.</p>
</header>

<section id="search-box">
    <input id="prompt" type="text" placeholder="Search for events...">
    <select id="region">
        <option value="London">London</option>
        <option value="Kent">Kent</option>
        <option value="UK">UK-wide</option>
    </select>
    <button onclick="runSearch()">Search</button>
</section>

<div id="results"></div>

<script src="app.js"></script>
</body>
</html>
