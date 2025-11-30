<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PopFinder – Event & Pop-Up Locator</title>
    <link rel="stylesheet" href="style.css">
</head>

<body>
    <header>
        <h1>PopFinder</h1>
        <p>Discover events, pop-up ideas, and vibrant locations across the city.</p>
    </header>

    <section id="search-box">
        <input type="text" id="keywords" placeholder="What are you looking for? e.g. markets, festivals">
        <input type="text" id="region" placeholder="Region e.g. London">
        <button onclick="runSearch()">Search</button>
    </section>

    <section id="results"></section>

    <script src="app.js"></script>
</body>
</html>
