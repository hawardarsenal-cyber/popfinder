<?php
require_once __DIR__ . "/Storage/PinsStorage.php";
require_once __DIR__ . "/Storage/NotesStorage.php";
require_once __DIR__ . "/SearchRules.php";

class SearchEngine {

    public function rank(array $events, string $region): array {

        $pins  = PinsStorage::load();
        $notes = NotesStorage::load();

        foreach ($events as &$ev) {
            $score = 0;

            // Base score for vendor opportunities
            if ($ev['vendor_opportunity']) $score += 30;

            // Region bonus
            if (strtolower($ev['region']) == strtolower($region)) {
                $score += 40;
            }

            // Additional boost for London/Kent (our primary areas)
            if (SearchRules::isPrimaryRegion($region)) {
                if (in_array(strtolower($ev['region']), ['london','kent'])) {
                    $score += 30;
                }
            }

            // Pins influence
            foreach ($pins as $p) {
                if (stripos($ev['title'], $p['title']) !== false) {
                    $score += 20;
                }
            }

            // Notes influence
            foreach ($notes as $n) {
                if (stripos($ev['title'], $n['text']) !== false ||
                    stripos($ev['snippet'], $n['text']) !== false) {
                    $score += 15;
                }
            }

            $ev['score'] = $score;
        }

        usort($events, fn($a, $b) => $b['score'] <=> $a['score']);
        return $events;
    }
}
