from pathlib import Path

from pregenerate_data.generate import main

if __name__ == "__main__":
    paths = [
        Path("./pregenerate_data/20240621_real_articles.json"),
        Path("./pregenerate_data/20240710_real_articles.json"),
        Path("./pregenerate_data/20240728_real_articles.json"),
    ]
    for path in paths:
        main(path)
