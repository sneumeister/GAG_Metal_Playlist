<?php
declare(strict_types=1);

final class Mailer
{
    /** @param array<string,mixed> $smtp */
    public static function send(array $smtp, string $to, string $toName, string $subject, string $body): void
    {
        $host = (string) ($smtp['host'] ?? '');
        $port = (int) ($smtp['port'] ?? 465);
        $user = (string) ($smtp['user'] ?? '');
        $pass = (string) ($smtp['pass'] ?? '');
        $from = (string) ($smtp['from'] ?? $user);
        $fromName = (string) ($smtp['fromName'] ?? $from);
        $enc = (string) ($smtp['encryption'] ?? 'ssl');

        if ($host === '' || $user === '' || $pass === '') {
            throw new RuntimeException('SMTP ist unvollständig konfiguriert.');
        }

        $remote = ($enc === 'ssl' ? 'ssl://' : '') . $host . ':' . $port;
        $errno = 0;
        $errstr = '';
        $fp = @stream_socket_client($remote, $errno, $errstr, 30, STREAM_CLIENT_CONNECT);
        if ($fp === false) {
            throw new RuntimeException('SMTP-Verbindung fehlgeschlagen: ' . $errstr);
        }
        stream_set_timeout($fp, 30);

        try {
            self::expect($fp, 220);
            self::cmd($fp, 'EHLO gag-playlist.local', 250);
            self::cmd($fp, 'AUTH LOGIN', 334);
            self::cmd($fp, base64_encode($user), 334);
            self::cmd($fp, base64_encode($pass), 235);
            self::cmd($fp, 'MAIL FROM:<' . $from . '>', 250);
            self::cmd($fp, 'RCPT TO:<' . $to . '>', 250);
            self::cmd($fp, 'DATA', 354);

            $headers = [
                'Date: ' . date('r'),
                'From: ' . self::encodeAddress($fromName, $from),
                'To: ' . self::encodeAddress($toName, $to),
                'Subject: ' . self::encodeHeader($subject),
                'MIME-Version: 1.0',
                'Content-Type: text/plain; charset=UTF-8',
                'Content-Transfer-Encoding: 8bit',
            ];
            $data = implode("\r\n", $headers) . "\r\n\r\n" . self::dotStuff($body) . "\r\n.";
            fwrite($fp, $data . "\r\n");
            self::expect($fp, 250);
            self::cmd($fp, 'QUIT', 221);
        } finally {
            fclose($fp);
        }
    }

    /** @param resource $fp */
    private static function cmd($fp, string $line, int $expectCode): void
    {
        fwrite($fp, $line . "\r\n");
        self::expect($fp, $expectCode);
    }

    /** @param resource $fp */
    private static function expect($fp, int $code): void
    {
        $resp = '';
        while (($line = fgets($fp, 515)) !== false) {
            $resp .= $line;
            if (isset($line[3]) && $line[3] === ' ') {
                break;
            }
        }
        $got = (int) substr($resp, 0, 3);
        if ($got !== $code) {
            throw new RuntimeException('SMTP unerwartet: ' . trim($resp));
        }
    }

    private static function encodeAddress(string $name, string $email): string
    {
        $name = trim($name);
        if ($name === '' || $name === $email) {
            return '<' . $email . '>';
        }
        return self::encodeHeader($name) . ' <' . $email . '>';
    }

    private static function encodeHeader(string $value): string
    {
        if (preg_match('/^[\x20-\x7E]+$/', $value)) {
            return $value;
        }
        return '=?UTF-8?B?' . base64_encode($value) . '?=';
    }

    private static function dotStuff(string $body): string
    {
        $body = str_replace(["\r\n", "\r"], "\n", $body);
        $body = str_replace("\n", "\r\n", $body);
        return preg_replace('/^\./m', '..', $body) ?? $body;
    }
}
