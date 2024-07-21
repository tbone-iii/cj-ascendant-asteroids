import feedparser
import re, trafilatura

URL = "https://www.reddit.com/r/news/.rss"

feed = feedparser.parse(URL)
for entry in feed.entries:
    print(entry.title)
    print(
        trafilatura.extract(
            trafilatura.fetch_url(re.findall('"(.*?)"', entry.summary)[1])
        )
    )
    print("\n")
