# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |

Only the latest release receives security patches.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability, use [GitHub's private vulnerability reporting](https://github.com/laplacef/ogcards/security/advisories/new). You can expect an initial response within 72 hours.

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment

## Scope

The following are considered security issues:
- Path traversal or arbitrary file write through manifest or theme paths
- Image or font parsing vulnerabilities reachable through Pillow
- Dependency vulnerabilities in direct dependencies

## Out of Scope

The following are **not** security issues:
- Card layout, typography, or rendering quality
- Font or asset licensing questions
- Failures on malformed manifests that are caught and reported
