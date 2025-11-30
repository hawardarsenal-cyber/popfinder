<?php
require_once "../src/Storage/NotesStorage.php";

$action = $_GET['action'] ?? '';

if ($action === "add") {
    NotesStorage::add($_POST['text']);
}
else if ($action === "list") {
    echo json_encode(NotesStorage::load());
}
