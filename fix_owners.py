#!/usr/bin/env python3
"""Fill in missing reactor owners and fix known ownership issues.

Usage:
    python fix_owners.py              # Dry run
    python fix_owners.py --apply      # Apply to DB
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path(__file__).parent / "nuclear_reactors.db"

# (plant_name, unit_number) -> owner
# Only for reactors that currently have NULL owner
OWNER_FIXES = {
    # === CHINA ===
    # CNNC group
    ("Sanmen", "1"): "CNNC",
    ("Sanmen", "2"): "CNNC",
    ("Sanmen", "3"): "CNNC",
    ("Sanmen", "4"): "CNNC",
    ("Tianwan", "7"): "Jiangsu Nuclear Power Company",
    ("Tianwan", "8"): "Jiangsu Nuclear Power Company",
    ("Changjiang", "3"): "CNNC",
    ("Changjiang", "4"): "CNNC",
    ("Sanao", "1"): "CNNC",
    ("Sanao", "2"): "CNNC",
    ("Sanao", "3"): "CNNC",
    ("Bailong", "1"): "CNNC",
    ("Jinqimen", "1"): "CNNC",
    ("Zhangzhou", "3"): "China National Nuclear Company",
    ("Zhangzhou", "4"): "China National Nuclear Company",
    ("Linglong", "1"): "CNNC",
    ("Xudabao", "3"): "CNNC",
    ("Xudabao", "4"): "CNNC",
    # CGN group
    ("Taishan", "1"): "CGN",
    ("Taishan", "2"): "CGN",
    ("Lianjiang", "1"): "CGN",
    ("Lianjiang", "2"): "CGN",
    ("Lufeng", "1"): "CGN",
    ("Lufeng", "2"): "CGN",
    ("Ningde", "5"): "China Guangdong Nuclear Power Group",
    ("Ningde", "6"): "China Guangdong Nuclear Power Group",
    ("Taipingling", "3"): "CGN",
    # SPIC group
    ("Haiyang", "1"): "State Power Investment Corporation",
    ("Haiyang", "2"): "State Power Investment Corporation",
    ("Haiyang", "3"): "State Power Investment Corporation",
    ("Haiyang", "4"): "State Power Investment Corporation",
    ("Shidaowan", "1"): "State Power Investment Corporation",
    ("Shidaowan", "2"): "State Power Investment Corporation",
    ("Shidaowan", "3"): "State Power Investment Corporation",
    ("Shidaowan", "4"): "State Power Investment Corporation",
    ("Xudabao", "1"): "State Power Investment Corporation",
    ("Xudabao", "2"): "State Power Investment Corporation",
    # Huaneng group
    ("Shidao Bay", "1"): "China Huaneng Group",
    # CNNC / CGN joint
    ("Lufeng", "5"): "CNNC",
    ("Lufeng", "6"): "CNNC",

    # === EGYPT ===
    ("El Dabaa", "1"): "Nuclear Power Plants Authority",
    ("El Dabaa", "2"): "Nuclear Power Plants Authority",
    ("El Dabaa", "3"): "Nuclear Power Plants Authority",
    ("El Dabaa", "4"): "Nuclear Power Plants Authority",

    # === GERMANY ===
    ("Greifswald", "1"): "Energiewerke Nord",
    ("Greifswald", "2"): "Energiewerke Nord",
    ("Greifswald", "3"): "Energiewerke Nord",
    ("Greifswald", "4"): "Energiewerke Nord",
    ("Greifswald", "5"): "Energiewerke Nord",
    ("Gundremmingen", "1"): "RWE",
    ("Rheinsberg", "1"): "Energiewerke Nord",
    ("Stade", "1"): "E.On",
    ("Obrigheim", "1"): "EnBW",
    ("Lingen", "1"): "RWE",
    ("Vak Kahl", "1"): "RWE",
    ("AVR Jülich", "1"): "AVR GmbH",
    ("THTR-300", "1"): "HKG",
    ("Mülheim-Kärlich", "1"): "RWE",
    ("MZFR", "1"): "KBG",
    ("Würgassen", "1"): "E.On",
    ("HDR Großwelzheim", "1"): "AEG",
    ("Niederaichbach", "1"): "KKN GmbH",
    ("KNK II", "1"): "KBG",

    # === HUNGARY ===
    ("Paks", "1"): "MVM Paks Nuclear Power Plant Ltd",
    ("Paks", "2"): "MVM Paks Nuclear Power Plant Ltd",
    ("Paks", "3"): "MVM Paks Nuclear Power Plant Ltd",
    ("Paks", "4"): "MVM Paks Nuclear Power Plant Ltd",
    ("Paks", "5"): "MVM Paks Nuclear Power Plant Ltd",

    # === INDIA ===
    ("Kudankulam", "5"): "NPCIL",
    ("Kudankulam", "6"): "NPCIL",

    # === ITALY ===
    ("Caorso", "1"): "ENEL",
    ("Enrico Fermi", "1"): "ENEL",
    ("Garigliano", "1"): "ENEL",
    ("Latina", "1"): "ENEL",

    # === LITHUANIA ===
    ("Ignalina", "1"): "Ignalina NPP",
    ("Ignalina", "2"): "Ignalina NPP",

    # === PAKISTAN ===
    ("Chashma", "5"): "Pakistan Atomic Energy Commission",

    # === RUSSIA ===
    ("BREST", "1"): "Rosenergoatom",
    ("Leningrad 2", "3"): "Rosenergoatom",

    # === SWITZERLAND ===
    ("Beznau", "1"): "Axpo",
    ("Beznau", "2"): "Axpo",
    ("Gösgen", "1"): "Kernkraftwerk Gösgen-Däniken AG",
    ("Leibstadt", "1"): "Kernkraftwerk Leibstadt AG",
    ("Mühleberg", "1"): "BKW",
    ("Lucens", "1"): "SNA",

    # === TURKEY ===
    ("Akkuyu", "3"): "Rusatom",
    ("Akkuyu", "4"): "Rusatom",

    # === USA ===
    ("Haddam Neck (Connecticut Yankee)", "1"): "Connecticut Yankee Atomic Power Co",
    ("Hallam", "1"): "Consumers Public Power District",
    ("Maine Yankee", "1"): "Maine Yankee Atomic Power Co",
}


def run(apply=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    not_found = 0
    already_set = 0

    for (plant, unit), owner in sorted(OWNER_FIXES.items()):
        cur.execute(
            "SELECT id, owner FROM reactors WHERE plant_name = ? AND unit_number = ?",
            (plant, unit)
        )
        row = cur.fetchone()
        if not row:
            print(f"  NOT FOUND: {plant}-{unit}")
            not_found += 1
            continue

        rid, current_owner = row
        if current_owner is not None:
            print(f"  SKIP {plant}-{unit}: already has owner '{current_owner}'")
            already_set += 1
            continue

        if apply:
            cur.execute("UPDATE reactors SET owner = ? WHERE id = ?", (owner, rid))
            print(f"  SET {plant}-{unit} -> {owner}")
        else:
            print(f"  Would set {plant}-{unit} -> {owner}")
        updated += 1

    if apply:
        conn.commit()

    print(f"\n{'Updated' if apply else 'Would update'} {updated} reactor owners")
    if not_found:
        print(f"Not found in DB: {not_found}")
    if already_set:
        print(f"Already had owner: {already_set}")

    # Post-fix summary
    cur.execute("SELECT COUNT(*) FROM reactors WHERE owner IS NULL")
    remaining = cur.fetchone()[0]
    print(f"Remaining NULL owners: {remaining}")

    conn.close()


if __name__ == "__main__":
    run("--apply" in sys.argv)
