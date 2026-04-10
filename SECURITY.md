# Security Policy

## What this plugin does with your filesystem

Cortex reads and writes **plain-text markdown files** in a single directory on your computer:

```
~/Documents/Claude/memory/
```

(On Windows: `%USERPROFILE%\Documents\Claude\memory\`)

It does **not**:
- Access files outside this directory.
- Send data to any remote server.
- Execute code or scripts.

All memory files are human-readable markdown. You can inspect, edit, move, or delete them at any time.

## Supported versions

| Version | Supported |
|---------|-----------|
| 4.x     | Yes       |
| 3.x     | Yes       |
| < 3.0   | No        |

## Reporting a vulnerability

If you discover a security issue — for example, a command file that could be manipulated to read or write outside the expected memory directory — please report it **privately**:

1. **GitHub private vulnerability reporting**: Go to the repo's **Security** tab → **Report a vulnerability**.
2. **Email**: security@brightwayai.com

Please **do not** open a public issue for security problems. We will acknowledge reports within 72 hours and aim to publish a fix within 7 days for confirmed issues.
