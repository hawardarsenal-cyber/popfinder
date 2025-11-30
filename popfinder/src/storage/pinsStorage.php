<?php

class PinsStorage {
    private static $file = __DIR__ . '/../../data/pins.json';

    public static function load() {
        if (!file_exists(self::$file)) return [];
        return json_decode(file_get_contents(self::$file), true) ?? [];
    }

    public static function save($pins) {
        file_put_contents(self::$file, json_encode($pins, JSON_PRETTY_PRINT));
    }

    public static function add($pin) {
        $pins = self::load();
        $pin['id'] = uniqid("pin_");
        $pins[] = $pin;
        self::save($pins);
    }

    public static function remove($id) {
        $pins = self::load();
        $pins = array_filter($pins, fn($p) => $p['id'] !== $id);
        self::save($pins);
    }
}
