<?php

$keywords = $_POST['keywords'] ?? "";
$region   = $_POST['region'] ?? "London";

$payload = json_encode([
    "keywords" => $keywords,
    "region" => $region
]);

$opts = [
    "http" => [
        "method"  => "POST",
        "header"  => "Content-Type: application/json",
        "content" => $payload,
        "timeout" => 60
    ]
];

$ctx = stream_context_create($opts);

$response = @file_get_contents("http://127.0.0.1:5001/search", false, $ctx);

if ($response === FALSE) {
    echo json_encode(["error" => "Could not connect to AI backend"]);
    exit;
}

header("Content-Type: application/json");
echo $response;
