<?php
declare(strict_types=1);

final class OneTimeCode
{
    private const ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

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

    public static function generate(): string
    {
        $out = '';
        $max = strlen(self::ALPHABET) - 1;
        for ($i = 0; $i < 8; $i++) {
            $out .= self::ALPHABET[random_int(0, $max)];
        }
        return $out;
    }

    public static function store(string $dir, string $code, int $ttlSeconds): void
    {
        self::cleanup($dir);
        $hash = hash('sha256', strtoupper($code));
        $path = $dir . DIRECTORY_SEPARATOR . $hash . '.json';
        $payload = [
            'expiresAt' => gmdate('c', time() + $ttlSeconds),
            'used' => false,
        ];
        file_put_contents($path, json_encode($payload, JSON_UNESCAPED_UNICODE), LOCK_EX);
    }

    /**
     * @return true wenn gültig und (nach Konsum) gelöscht
     */
    public static function consume(string $dir, string $code): bool
    {
        self::cleanup($dir);
        $code = strtoupper(trim($code));
        if ($code === '' || !preg_match('/^[A-Z0-9]{8}$/', $code)) {
            return false;
        }
        $path = $dir . DIRECTORY_SEPARATOR . hash('sha256', $code) . '.json';
        if (!is_file($path)) {
            return false;
        }
        $raw = @file_get_contents($path);
        $data = is_string($raw) ? json_decode($raw, true) : null;
        if (!is_array($data)) {
            @unlink($path);
            return false;
        }
        if (!empty($data['used'])) {
            @unlink($path);
            return false;
        }
        $exp = isset($data['expiresAt']) ? strtotime((string) $data['expiresAt']) : false;
        if ($exp === false || $exp < time()) {
            @unlink($path);
            return false;
        }
        @unlink($path);
        return true;
    }
}
