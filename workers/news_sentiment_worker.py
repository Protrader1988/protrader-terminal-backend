import time, yaml
from data.providers.news_providers import fetch_headlines, simple_sentiment

def main():
    with open("config/strategies.yaml","r") as f:
        cfg = yaml.safe_load(f)
    universe = cfg.get("universe", [])
    while True:
        items = fetch_headlines(universe)
        for it in items:
            it["sentiment"] = simple_sentiment(it.get("title","")+it.get("summary",""))
            print("NEWS", it["ticker"], it["sentiment"]["compound"], "-", it["title"])
        time.sleep(300)

if __name__=="__main__":
    main()
