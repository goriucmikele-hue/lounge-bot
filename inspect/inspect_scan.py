import json, collections
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def main():
    items = json.loads((DATA_DIR / "full_scan.json").read_text(encoding="utf-8"))

    def is_shoe_size(s):
        try:
            return 35 <= float(s) <= 47
        except ValueError:
            return False

    shoes = [i for i in items if any(is_shoe_size(s["size"]) for s in i.get("simples", []))]
    print("Total:", len(items), "| cu mărimi de încălțăminte:", len(shoes))
    print("\nTag-uri:", collections.Counter(i.get("tag") for i in items).most_common(15))
    print("Stock produs:", collections.Counter(i.get("stock_status") for i in items))
    print("Stock simples:", collections.Counter(s.get("stock_status") for i in items for s in i.get("simples", [])))
    print("Flags:", collections.Counter(str(i.get("flags")) for i in items).most_common(8))

    print("\nPantofi cu name_prefix gol:")
    for i in shoes:
        if not (i.get("name_prefix") or "").strip():
            print("-", i.get("tag"), i.get("color_name"), i["special_price"] / 100, "lei | model_sku:", i.get("model_sku"))

    mine = {"41", "41.5", "42"}
    print("\nProduse care au măcar o dată 41 / 41.5 / 42 (orice stoc):")
    for i in shoes:
        ms = [(s["size"], s.get("stock_status")) for s in i["simples"] if s["size"] in mine]
        if ms:
            print("-", i.get("name_prefix") or "(gol)", i.get("color_name"), i["special_price"] / 100, "lei |", ms)

    print("\nPantofi pe model (nume -> număr):")
    print(collections.Counter(i.get("name_prefix") or "(gol)" for i in shoes).most_common(40))


if __name__ == "__main__":
    main()