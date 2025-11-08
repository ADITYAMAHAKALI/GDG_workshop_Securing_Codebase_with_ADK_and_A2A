# Security Report

## Summary
🚨 This repository contains a deliberately insecure Python Flask and Node.js application with multiple critical vulnerabilities, including remote code execution, SQL injection, command injection, and hard-coded secrets. The configuration is also insecure, with debug mode enabled and an overly permissive CORS policy.

## Findings

## [F001] Remote Code Execution via eval()
🚨 Severity: CRITICAL
File: app.py around line 97
- Description: The application uses `eval()` to execute user-provided code from the 'code' query parameter. This allows an attacker to execute arbitrary Python code on the server, leading to a full system compromise.
- Recommendation: Never use `eval()` on untrusted user input. If dynamic expression evaluation is required, use a safer alternative like `ast.literal_eval` for simple literals or implement a tightly controlled parser for a limited, well-defined language.

## [F002] SQL Injection
🚨 Severity: CRITICAL
File: db.py around line 34
- Description: The `unsafe_search_users` function constructs a SQL query by directly concatenating user-provided input (`search_term`) into the query string. An attacker can manipulate this input to alter the SQL query's logic, allowing them to bypass authentication, exfiltrate, modify, or delete data from the database.
- Recommendation: Use parameterized queries (prepared statements) to safely pass user input to the database. The database driver will handle the proper escaping, preventing malicious input from being interpreted as SQL code.

## [F003] Hard-coded Secrets
🚨 Severity: CRITICAL
File: secrets.py around line 9
- Description: The file `secrets.py` contains hard-coded sensitive values, including a Stripe secret key, a GitHub access token, a database password, and a JWT secret. Committing secrets directly into source code makes them accessible to anyone with read access to the repository and exposes them in the git history, even if removed later.
- Recommendation: Remove all secrets from the source code. Store them in a secure secret management system (e.g., AWS Secrets Manager, HashiCorp Vault, Google Secret Manager) or, for development, use environment variables loaded via a `.env` file that is not committed to version control.

## [F004] Command Injection
🚨 Severity: CRITICAL
File: node-demo/index.js around line 6
- Description: The `runCommand` function uses `child_process.exec` to execute a command string. If the `cmd` parameter is controlled by user input, an attacker could inject malicious shell commands (e.g., `'; rm -rf /'`), leading to arbitrary command execution on the server.
- Recommendation: Avoid executing shell commands based on user input. If necessary, use safer alternatives like `child_process.execFile` which does not invoke a shell, and pass arguments as an array to prevent injection.

## [F005] Flask Debug Mode Enabled
🚨 Severity: HIGH
File: config.py around line 13
- Description: The application configuration has `DEBUG = True` hard-coded, which is then used to run the Flask application. Running a production or publicly-accessible application in debug mode can expose a Werkzeug debugger, allowing attackers to gain an interactive shell and execute arbitrary code on the server if an error occurs.
- Recommendation: Ensure debug mode is disabled in production environments. Set the `DEBUG` flag based on an environment variable (e.g., `os.getenv('FLASK_DEBUG') == '1'`) and ensure this variable is not set to '1' in production.

## [F006] Server-Side Request Forgery (SSRF)
🚨 Severity: HIGH
File: app.py around line 53
- Description: The `/proxy` endpoint fetches a URL provided in the `url` query parameter without any validation. An attacker can use this to make the server send requests to arbitrary external domains or, more critically, to internal services on the local network that are not publicly accessible. This can be used for network reconnaissance or to attack internal services.
- Recommendation: Validate the user-provided URL against a strict allow-list of known, safe domains and protocols. Never allow requests to arbitrary or internal IP addresses.

## [F007] Outdated and Vulnerable Dependencies
🚨 Severity: HIGH
File: requirements.txt around line N/A
- Description: The project uses outdated dependencies (e.g., Flask 1.1.2, requests 2.19.0, lodash 4.17.11) with known security vulnerabilities. Exploiting these vulnerabilities could lead to various impacts, including denial of service, information disclosure, or remote code execution.
- Recommendation: Regularly scan dependencies for known vulnerabilities using tools like `pip-audit`, `npm audit`, or Snyk. Update all dependencies to the latest stable and non-vulnerable versions.

## [F008] Insecure TLS Validation Disabled
🟡 Severity: MEDIUM
File: app.py around line 57
- Description: The HTTP request made in the `/proxy` endpoint uses `verify=False`. This disables TLS certificate validation, making the connection vulnerable to Man-in-the-Middle (MITM) attacks where an attacker can intercept, read, and modify the traffic between the server and the target URL.
- Recommendation: Remove `verify=False` from all `requests` calls. If connecting to a service with a self-signed certificate, configure the client to trust that specific certificate authority (CA) instead of disabling validation entirely.

## [F009] Insecure CORS Policy (Wildcard)
🟡 Severity: MEDIUM
File: config.py around line 17
- Description: The Cross-Origin Resource Sharing (CORS) policy is configured to `*`, allowing any website to make authenticated requests to this application's API. If the application relies on session cookies for authentication, this could allow a malicious website to perform actions on behalf of a logged-in user.
- Recommendation: Restrict `CORS_ORIGINS` to a specific list of trusted domains that need to interact with the API. Avoid using the wildcard `*` in production.
