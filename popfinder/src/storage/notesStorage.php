<?php

class NotesStorage {
    private static $file = __DIR__ . '/../../data/notes.json';

    public static function load() {
        if (!file_exists(self::$file)) return [];
        return json_decode(file_get_contents(self::$file), true) ?? [];
    }

    public static function save($notes) {
        file_put_contents(self::$file, json_encode($notes, JSON_PRETTY_PRINT));
    }

    public static function add($text) {
        $notes = self::load();
        $notes[] = [
            'id' => uniqid("note_"),
            'text' => $text,
            'created_at' => date("c")
        ];
        self::save($notes);
    }
}
