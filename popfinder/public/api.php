<?php

$query = $_POST['query'] ?? '';
$location = $_POST['location'] ?? 'london';

$payload = json_encode([
    "query" => $query,
    "location" => $location
]);

$opts = [
    'http' => [
        'method' => 'POST',
        'header' => "Content-Type: application/json",
        'content' => $payload
    ]
];

$context = stream_context_create($opts);

$response = file_get_contents('http://127.0.0.1:5001/search', false, $context);

echo $response;
