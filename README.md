# Gorilla — Layer-7 DDOS Tool

Gorilla is a Layer-7 DDOS tool for testing, stress simulation, and load benchmarking on web servers. 


> ⚠️ **Important:** Use **only** on systems you own or where you have explicit written permission to run load tests. Unauthorized use against third-party hosts is illegal and may result in criminal or civil penalties. The author is not responsible for misuse.

---

## Features

- Asynchronous HTTP requests using `aiohttp` and `asyncio` for high throughput.
- Randomized `User-Agent`, `Referer`, and other headers to simulate realistic clients.
- Configurable total requests and concurrency.
- Optional proxy support (simple `ip:port` list) to route requests.
- Graceful handling of common connection errors and timeouts.
- Lightweight ASCII Gorilla banner on startup.

---

## Requirements

- Python 3.11+ (3.10 may work, but 3.11+ is recommended)
- `aiohttp` library

**requirements.txt**

```
aiohttp==3.9.3
```

---

## Installation

```bash
# clone repository (or place gorilla.py in a folder)
git clone https://github.com/yourusername/gorilla.git
cd gorilla


# install dependencies
pip install -r requirements.txt
```

---

## Usage

```
usage: gorilla [-h] -t TARGET [-n TOTAL] [-c CONCURRENCY] [-p PROXIES] [--confirm CONFIRM]
```

### Quick start

```bash
python gorilla.py -t https://example.com
```

This runs the test with default settings:
- `total` (default): 2000 requests
- `concurrency` (default): 20 concurrent requests


### Common options

- `-t`, `--target` **(required)**  — Target URL to test (e.g. `https://example.com`).
- `-n`, `--total`  — Total number of requests to send (default: `2000`).
- `-c`, `--concurrency`  — Number of concurrent requests (default: `20`).
- `-p`, `--proxies`  — Optional path to a proxy file (one `ip:port` per line).
- `--confirm`  — Optional safety confirmation token (see notes).

### Example with options

```bash
python gorilla.py -t https://example.com -n 500 -c 10 -p proxies.txt --confirm I_HAVE_PERMISSION
```

---

## Proxy file format

If you want to use proxies, create a text file (e.g. `proxies.txt`) where each line is `ip:port` (no scheme). Example:

```
123.456.789.123:8080
111.222.333.444:80
555.666.777.888:1234
```

The tool will automatically prepend `http://` when passing the proxy URL to the HTTP client.

> Note: Public/free proxies are often unreliable and slow. Use trusted proxies for realistic results.

---

## Safety & Responsible Use

Gorilla is intended for legitimate performance testing, benchmarking and research **with permission**. To help avoid accidental misuse the repository includes a few recommended safeguards you should enable or follow:

1. **Require confirmation** before running against external targets. Use the `--confirm I_HAVE_PERMISSION` flag and check it in `main()`.
2. **Whitelist mode (optional)** — maintain a small file with allowed targets and require the target to be in that file.
3. **Conservative defaults** — keep default `total` and `concurrency` conservative and print a warning for very high values.
4. **Audit logs** — optionally append each run’s parameters (timestamp, target, total, concurrency, proxies path) to a local log file so you can demonstrate responsible operation.

---

## Output examples

Successful responses look like:

```
[5] Status: 200 | Content Length: 266465
[4] Status: 200 | Content Length: 230186
```

Errors are shown with type and message, e.g.:

```
[3] Error: TimeoutError | <details>
[7] Error: ClientProxyConnectionError | Cannot connect to host 1.2.3.4:8080
```

When a proxy or connection failure occurs the task is skipped but the overall run continues.

---

## Troubleshooting

- **`InvalidURL` when using proxies**: ensure your proxy file uses `ip:port` only. The tool will add `http://` automatically.
- **Timeouts**: raise `DEFAULT_TIMEOUT` or reduce `concurrency` if you see many `TimeoutError` entries.
- **Many proxy errors**: public proxy lists are unreliable — use better proxies or run without proxies.

---

---

## License

This project is provided under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgements

This tool uses `aiohttp` for asynchronous HTTP client functionality and takes inspiration from common CLI testing tools. Please use it responsibly.
