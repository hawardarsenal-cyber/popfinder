<?php

class SearchRules {

    public static function isPrimaryRegion(string $region): bool {
        return in_array(strtolower($region), ['london', 'kent']);
    }

    // Base search templates for each region
    public static function baseQueries(string $region): array {
        $regionLower = strtolower($region);

        return [
            "markets in $region vendor opportunities",
            "$region events exhibitor info",
            "$region pop up space",
            "$region shopping centre promotional space",
            "$region mall stand hire",
            "$region county show book a stand",
            "$region expo exhibitor opportunities",
            "$region street fair stalls",
        ];
    }

    // Keyword dictionary for parsing
    public static function keywords(): array {
        return [
            "market", "fair", "festival", "exhibition",
            "expo", "shopping centre", "mall",
            "vendor", "exhibitor", "stall", "stand hire",
            "county show", "pop up", "popup", "trade show"
        ];
    }
}
