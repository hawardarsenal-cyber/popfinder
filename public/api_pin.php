<?php
require_once "../src/Storage/PinsStorage.php";

$action = $_GET['action'] ?? '';

if ($action === "add") {
    $data = json_decode(urldecode($_POST['event']), true);
    PinsStorage::add($data);
}
else if ($action === "list") {
    echo json_encode(PinsStorage::load());
}
else if ($action === "remove") {
    PinsStorage::remove($_GET['id']);
}

