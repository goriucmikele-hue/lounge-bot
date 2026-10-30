import json, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def main():
    items = []
    for f in sorted(DATA_DIR.glob("grid_*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f.name, "ilizibil:", e); continue
        res = d.get("results") or []
        print(f.name, "->", len(res), "produse, cursor:", bool(d.get("next_cursor")), "total:", d.get("total_count"))
        items += res

    print("\nTotal produse:", len(items))
    if items:
        print("Chei produs:", sorted(items[0].keys()))
        s = (items[0].get("simples") or [{}])[0]
        print("Chei simple:", sorted(s.keys()))

    sizes = sorted({str(s.get("size")) for it in items for s in it.get("simples", [])})
    print("\nMărimi distincte văzute:", sizes)

    pat = re.compile(r"1906|2002|550", re.I)
    print("\nPotriviri 1906/2002/550:")
    for it in items:
        if pat.search(str(it.get("name_prefix", ""))):
            sz = [s["size"] for s in it.get("simples", []) if s.get("stock_status") == "AVAILABLE"]
            print("-", it["name_prefix"], it.get("color_name"), it.get("special_price"), "| mărimi:", sz)

    print("\nNume modele (primele 40):")
    print(sorted({str(it.get("name_prefix")) for it in items})[:40])
    print("\nurls.txt:")
    u = DATA_DIR / "urls.txt"
    print(u.read_text(encoding="utf-8") if u.exists() else "(lipsește)")


if __name__ == "__main__":
    main()