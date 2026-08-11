"""
Generates a labeled training dataset of URLs (legitimate=0, phishing=1).

IMPORTANT: This is a SYNTHETIC dataset built from pattern templates, not
a scrape of a real phishing feed. It exists so the training pipeline
(preprocess -> train -> evaluate) is fully runnable offline and
end-to-end. Before relying on this model for real decisions, replace
ml/data/raw/urls.csv with a real labeled dataset (e.g. PhishTank,
OpenPhish, or a Kaggle phishing-URL dataset) using the same two
columns: `url,label`.

Run:
    python ml/scripts/generate_dataset.py
"""

import csv
import random
from pathlib import Path

random.seed(42)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "urls.csv"

LEGITIMATE_DOMAINS = [
    "google.com", "github.com", "wikipedia.org", "microsoft.com", "apple.com",
    "amazon.com", "netflix.com", "spotify.com", "stackoverflow.com", "reddit.com",
    "nytimes.com", "bbc.co.uk", "npr.org", "mozilla.org", "python.org",
    "npmjs.com", "docs.python.org", "linkedin.com", "dropbox.com", "slack.com",
    "notion.so", "figma.com", "cloudflare.com", "digitalocean.com", "gitlab.com",
    "medium.com", "quora.com", "coursera.org", "khanacademy.org", "mit.edu",
    "stanford.edu", "wsj.com", "theguardian.com", "protonmail.com", "outlook.com",
    "office.com", "adobe.com", "salesforce.com", "atlassian.com", "zoom.us",
    "twitch.tv", "pinterest.com", "shopify.com", "etsy.com", "ebay.com",
    "paypal.com", "chase.com", "wellsfargo.com", "irs.gov", "usa.gov",
]

LEGITIMATE_PATHS = [
    "", "/", "/about", "/products", "/blog/2024/annual-report",
    "/docs/getting-started", "/en/help", "/account/settings",
    "/search?q=python+tutorial", "/user/profile", "/news/latest",
    "/api/v1/status", "/pricing", "/contact-us", "/careers",
]

BRAND_NAMES = [
    "paypal", "google", "microsoft", "apple", "amazon", "netflix",
    "chase", "wellsfargo", "instagram", "facebook", "coinbase", "office365",
]

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking",
    "confirm", "signin", "billing", "password", "wallet", "suspend",
    "unlock", "recover", "invoice",
]

SUSPICIOUS_TLDS = ["tk", "ml", "ga", "cf", "gq", "xyz", "top", "info", "click", "work"]

RANDOM_WORDS = [
    "portal", "session", "auth", "gateway", "id", "user", "center",
    "service", "support", "team", "mobile", "app", "web", "online",
]


def random_token(length=6):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choice(chars) for _ in range(length))


def make_legitimate_url():
    domain = random.choice(LEGITIMATE_DOMAINS)
    path = random.choice(LEGITIMATE_PATHS)
    scheme = "https"
    if random.random() < 0.15:
        # occasional www / subdomain
        domain = f"www.{domain}"
    return f"{scheme}://{domain}{path}"


def make_phishing_url():
    style = random.choice(["brand_subdomain", "brand_hyphen", "ip_based", "shortener_like", "random_suspicious"])
    brand = random.choice(BRAND_NAMES)
    keyword = random.choice(SUSPICIOUS_KEYWORDS)
    tld = random.choice(SUSPICIOUS_TLDS)
    scheme = random.choice(["http", "https"])

    if style == "brand_subdomain":
        sub = random.choice(RANDOM_WORDS)
        url = f"{scheme}://{brand}-{keyword}.{sub}-{random_token(4)}.{tld}/{keyword}"
    elif style == "brand_hyphen":
        url = f"{scheme}://{brand}-{keyword}-{random_token(5)}.com/{keyword}.php"
    elif style == "ip_based":
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        url = f"http://{ip}/{keyword}/{brand}/{random_token(4)}"
    elif style == "shortener_like":
        url = f"http://{random.choice(['bit.ly', 'tinyurl.com', 'is.gd'])}/{random_token(7)}"
    else:  # random_suspicious
        url = f"{scheme}://{random_token(8)}-{keyword}.{tld}/{brand}/{keyword}?id={random_token(10)}"

    return url


def generate(n_per_class=1200):
    rows = []
    seen = set()

    while len([r for r in rows if r[1] == 0]) < n_per_class:
        url = make_legitimate_url()
        if url in seen:
            continue
        seen.add(url)
        rows.append((url, 0))

    while len([r for r in rows if r[1] == 1]) < n_per_class:
        url = make_phishing_url()
        if url in seen:
            continue
        seen.add(url)
        rows.append((url, 1))

    random.shuffle(rows)
    return rows


def main():
    rows = generate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()