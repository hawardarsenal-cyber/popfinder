<?php
require_once __DIR__ . "/SearchRules.php";

class EventParser {

    public function parse(array $raw): array {
        $clean = [];

        foreach ($raw as $item) {
            $clean[] = $this->normalize($item);
        }

        return $clean;
    }

    private function normalize(array $r): array {

        $text = strtolower($r['title'] . " " . $r['snippet']);

        // Detect event type
        $type = $this->detectType($text);

        // Detect vendor opportunity
        $vendor = $this->detectVendorOpportunity($text);

        // Region guess
        $region = $this->guessRegion($text);

        return [
            "title"   => $r['title'],
            "url"     => $r['url'],
            "snippet" => $r['snippet'],
            "type"    => $type,
            "vendor_opportunity" => $vendor,
            "region"  => $region,
            "date"    => $this->guessDate($text),
        ];
    }

    private function detectType(string $text): string {
        foreach (SearchRules::keywords() as $k) {
            if (strpos($text, strtolower($k)) !== false) {
                return $k;
            }
        }
        return "unknown";
    }

    private function detectVendorOpportunity(string $text): bool {
        $terms = ["exhibitor", "stall", "vendor", "book a stand", "stand hire"];
        foreach ($terms as $t) {
            if (strpos($text, $t) !== false) return true;
        }
        return false;
    }

    private function guessRegion(string $text): string {
        if (strpos($text, "london") !== false) return "London";
        if (strpos($text, "kent") !== false) return "Kent";
        return "Unknown";
    }

    private function guessDate(string $text): string {
        // crude date detection (improve later)
        if (preg_match("/\b(202[4-9]|203\d)\b/", $text, $m)) {
            return $m[0];
        }
        return "Unknown";
    }
}
