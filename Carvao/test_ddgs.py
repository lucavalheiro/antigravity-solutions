from duckduckgo_search import DDGS
import json

def test():
    with DDGS() as ddgs:
        results = list(ddgs.text("preço saco carvao vegetal atacado brasil", max_results=5))
        print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test()
