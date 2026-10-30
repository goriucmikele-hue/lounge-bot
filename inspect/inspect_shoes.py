import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def main():
    items = json.loads((DATA_DIR / "full_scan.json").read_text(encoding="utf-8"))
    words = ("sneakers", "pantofi", "ghete", "încălțăminte", "sandale", "bocanci")

    shoes = [i for i in items if any(w in (i.get("tag") or "").lower() for w in words)]
    print("Pantofi după tag:", len(shoes), "\n")

    for i in shoes:
        sz = [(s["size"], s["simple_sku"][-7:]) for s in i["simples"]]
        print(f'{i.get("name_prefix") or "(gol)":<22} {i.get("tag")[:22]:<22} {i.get("gender"):<7} '
              f'{i["special_price"]/100:>6.0f} lei | {[x[0] for x in sz]}')

    print("\nExemplu simple_sku (cod mărime la final):")
    for i in shoes[:3]:
        print([s["simple_sku"] for s in i["simples"][:3]])


if __name__ == "__main__":
    main()