<?php
require_once __DIR__ . "/Config.php";
require_once __DIR__ . "/SearchRules.php";

class EventFetcher {

    public function fetch(array $queries, string $region): array {
        $results = [];

        foreach ($queries as $q) {
            $hits = $this->googleSearch($q . " " . $region);
            $results = array_merge($results, $hits);
        }

        return $results;
    }

    // Google Search API wrapper
    private function googleSearch(string $query): array {
        $apiKey = Config::$GOOGLE_API_KEY;
        $cx     = Config::$GOOGLE_SEARCH_ENGINE_ID;

        $url = "https://www.googleapis.com/customsearch/v1?q="
             . urlencode($query)
             . "&key=$apiKey&cx=$cx";

        $json = @file_get_contents($url);

        if (!$json) return [];

        $data = json_decode($json, true);

        if (!isset($data['items'])) return [];

        $structured = [];

        foreach ($data['items'] as $item) {
            $structured[] = [
                "title"   => $item['title'] ?? '',
                "snippet" => $item['snippet'] ?? '',
                "url"     => $item['link'] ?? '',
                "source"  => "google",
            ];
        }

        return $structured;
    }
}
