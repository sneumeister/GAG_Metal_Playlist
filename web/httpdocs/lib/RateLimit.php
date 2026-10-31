<?php
declare(strict_types=1);

final class RateLimit
{
    public static function cleanup(string $dir): void
    {
        if (!is_dir($dir)) {
            return;
        }
        $now = time();
        foreach (glob($dir . DIRECTORY_SEPARATOR . '*.json') ?: [] as $file) {
            $raw = @file_get_contents($file);
            if ($raw === false) {
                continue;
            }
            $data = json_decode($raw, true);
            if (!is_array($data)) {
                @unlink($file);
                continue;
            }
            $exp = isset($data['expiresAt']) ? strtotime((string) $data['expiresAt']) : false;
            if ($exp !== false && $exp < $now) {
                @unlink($file);
            }
        }
    }

    /**
     * @return true wenn erlaubt, false wenn Limit erreicht
     */
    public static function allow(string $dir, string $key, int $max, int $windowSeconds): bool
    {
        self::cleanup($dir);
        $safe = preg_replace('/[^a-zA-Z0-9_-]/', '_', $key) ?? 'key';
        $path = $dir . DIRECTORY_SEPARATOR . $safe . '.json';
        $now = time();
        $data = ['count' => 0, 'windowStart' => $now, 'expiresAt' => gmdate('c', $now + $windowSeconds)];

        if (is_file($path)) {
            $raw = @file_get_contents($path);
            $parsed = is_string($raw) ? json_decode($raw, true) : null;
            if (is_array($parsed)) {
                $start = (int) ($parsed['windowStart'] ?? 0);
                if ($start > 0 && ($now - $start) < $windowSeconds) {
                    $data = $parsed;
                }
            }
        }

        $count = (int) ($data['count'] ?? 0);
        if ($count >= $max) {
            return false;
        }

        $data['count'] = $count + 1;
        $data['windowStart'] = (int) ($data['windowStart'] ?? $now);
        $data['expiresAt'] = gmdate('c', $data['windowStart'] + $windowSeconds);
        file_put_contents($path, json_encode($data, JSON_UNESCAPED_UNICODE), LOCK_EX);
        return true;
    }

    public static function emailHash(string $email): string
    {
        return hash('sha256', app_normalize($email));
    }
}
