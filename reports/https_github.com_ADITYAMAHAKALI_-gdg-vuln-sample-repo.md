# Security Report

🚨 This repository contains a Flask and Node.js application with multiple critical security vulnerabilities, including remote code execution via `eval`, SQL injection, and hard-coded secrets. The codebase is intentionally insecure and poses a severe risk if deployed.

## Findings

## [F001] Remote Code Execution via `eval`
🚨 app.py around line 87
- Description: The `/eval` route executes user-provided Python code using the `eval()` function. This allows an unauthenticated attacker to run arbitrary code on the server, leading to a full system compromise.
- Recommendation: Never use `eval` with untrusted user input. Remove this functionality entirely. If dynamic expression evaluation is absolutely necessary, use a safer alternative like `ast.literal_eval` for parsing simple data structures, or redesign the feature to avoid executing user code.

## [F002] Hard-coded Secrets
🚨 secrets.py around line 10
- Description: Multiple secrets, including a Stripe API key, GitHub token, database password, and JWT secret, are hard-coded in the source code. This exposes them to anyone with repository access and makes rotation difficult, leading to potential account and database compromise.
- Recommendation: Externalize all secrets from the codebase. Use environment variables, a dedicated secrets management service (e.g., AWS Secrets Manager, HashiCorp Vault), or encrypted configuration files to store and access secrets securely.

## [F003] SQL Injection
🚨 db.py around line 35
- Description: The `unsafe_search_users` function constructs a raw SQL query by directly embedding user input into an f-string. An attacker can provide malicious input to manipulate the query, allowing them to bypass authentication, exfiltrate sensitive data, or modify the database.
- Recommendation: Use parameterized queries (prepared statements) to separate the SQL logic from user data. The database driver will safely handle escaping, preventing SQL injection attacks.

## [F004] Flask Debug Mode Enabled in Configuration
🚨 config.py around line 13
- Description: Flask's debug mode is permanently enabled in the configuration (`DEBUG = True`). When active in a production or publicly-accessible environment, it can leak sensitive information in error pages and provides an interactive web-based debugger that can be exploited for remote code execution.
- Recommendation: Disable debug mode for production builds. Set the `DEBUG` flag based on an environment variable that is explicitly set to `False` in production environments.

## [F005] Server-Side Request Forgery (SSRF) and Disabled TLS Verification
🚨 app.py around line 50
- Description: The `/proxy` endpoint fetches a URL provided by the user without validation, creating a Server-Side Request Forgery (SSRF) vulnerability. This allows an attacker to scan internal networks or access cloud provider metadata services. Additionally, `verify=False` disables TLS certificate validation, making the connection vulnerable to Man-in-the-Middle (MITM) attacks.
- Recommendation: Validate the user-provided URL against a strict allow-list of approved domains or IP addresses to mitigate SSRF. Remove `verify=False` to enforce TLS certificate validation on all outgoing HTTPS requests.

## [F006] Command Injection Pattern
🚨 node-demo/index.js around line 6
- Description: The `runCommand` function uses `child_process.exec`, which spawns a shell to execute the provided command. If this function is ever called with untrusted user input, it can lead to arbitrary command execution on the server.
- Recommendation: Avoid executing shell commands based on user input. If necessary, use a safer alternative like `child_process.execFile` and pass arguments as an array to prevent shell interpretation of metacharacters.

## [F007] Insecure CORS Policy
🟡 config.py around line 17
- Description: The Cross-Origin Resource Sharing (CORS) policy is configured with a wildcard (`"*"`) allowing any website to make requests to this application's API. If the application uses cookie-based authentication, this could be exploited in attacks like Cross-Site Request Forgery (CSRF).
- Recommendation: Restrict the `CORS_ORIGINS` configuration to a specific allow-list of trusted domains that need to access the API.

## [F008] Outdated and Vulnerable Dependencies
🟡 requirements.txt around line 1
- Description: The project uses several outdated dependencies (e.g., Flask 1.1.2, requests 2.19.0, lodash 4.17.11, axios 0.21.0) with known, publicly disclosed security vulnerabilities. Exploiting these vulnerabilities could lead to various attacks, including denial of service, information disclosure, or SSRF.
- Recommendation: Regularly scan and update all project dependencies to their latest secure versions. Use tools like `pip-audit` for Python and `npm audit` for Node.js to automate this process.
