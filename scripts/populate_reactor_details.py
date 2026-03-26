#!/usr/bin/env python3
"""Create and populate reactor_details table with cooling type, vendors."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nuclear_reactors.db')


def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reactor_details (
            reactor_id INTEGER PRIMARY KEY,
            cooling_type TEXT,
            constructor TEXT,
            architect_engineer TEXT,
            turbine_supplier TEXT,
            pressure_vessel_manufacturer TEXT,
            FOREIGN KEY (reactor_id) REFERENCES reactors(id)
        )
    """)
    conn.commit()


def get_reactors(conn):
    """Get all reactors with country and design info."""
    return conn.execute("""
        SELECT r.id, r.plant_name, r.unit_number, r.design_series,
               c.name as country, s.name as supplier, r.latitude, r.longitude,
               r.status
        FROM reactors r
        JOIN countries c ON r.country_id = c.id
        LEFT JOIN suppliers s ON r.supplier_id = s.id
        ORDER BY c.name, r.plant_name, r.unit_number
    """).fetchall()


# ---------------------------------------------------------------------------
# COOLING TYPE
# ---------------------------------------------------------------------------

def determine_cooling_type(plant, unit, country, design, lat, lon):
    """Determine cooling type based on country, plant name, and design."""

    # --- France ---
    if country == 'France':
        # Seawater plants (Channel/Atlantic coast)
        if plant in ('Gravelines',):
            return 'Once-through (seawater)'
        if plant in ('Paluel', 'Penly', 'Flamanville'):
            return 'Once-through (seawater)'
        # River once-through
        if plant == 'Fessenheim':
            return 'Once-through (river)'
        if plant == 'Bugey':
            if unit in ('1',):
                return None  # UNGG, old
            if unit in ('2', '3'):
                return 'Once-through (river)'
            if unit in ('4', '5'):
                return 'Cooling tower (natural draft)'
        if plant == 'Tricastin':
            return 'Once-through (river)'
        if plant in ('Dampierre', 'Chinon B'):
            return 'Once-through (river)'
        if plant in ('St. Laurent B', 'St. Laurent A'):
            return 'Once-through (river)'
        if plant == 'Blayais':
            return 'Once-through (river)'
        # Cooling tower plants
        if plant in ('Cruas', 'St. Alban'):
            return 'Cooling tower (natural draft)'
        if plant in ('Golfech', 'Civaux', 'Cattenom', 'Belleville', 'Nogent'):
            return 'Cooling tower (natural draft)'
        if plant in ('Chooz B', 'Chooz-A'):
            return 'Cooling tower (natural draft)'
        # Old UNGG/other
        if plant in ('Chinon A (EDF1)', 'Chinon A (EDF2)', 'Chinon A (EDF3)'):
            return 'Once-through (river)'
        if plant in ('G2', 'G3'):
            return 'Once-through (river)'
        if plant == 'Phenix':
            return 'Once-through (river)'
        if plant == 'Super-Phenix':
            return 'Cooling tower (natural draft)'
        if plant == 'Brennilis':
            return None  # small experimental
        return None

    # --- Japan --- All coastal
    if country == 'Japan':
        return 'Once-through (seawater)'

    # --- South Korea --- All coastal
    if country == 'South Korea':
        return 'Once-through (seawater)'

    # --- Germany ---
    if country == 'Germany':
        # River once-through plants
        if plant in ('Brokdorf',):
            return 'Once-through (river)'
        if plant in ('Unterweser', 'Stade'):
            return 'Once-through (river)'
        if plant in ('Brunsbüttel', 'Krümmel'):
            return 'Once-through (river)'
        if plant == 'Grohnde':
            return 'Once-through (river)'
        if plant == 'Biblis':
            return 'Once-through (river)'
        if plant == 'Philippsburg':
            if unit == '1':
                return 'Cooling tower (natural draft)'
            return 'Once-through (river)'
        if plant == 'Isar':
            return 'Once-through (river)'
        if plant == 'Obrigheim':
            return 'Once-through (river)'
        if plant == 'Gundremmingen':
            if unit == '1':
                return 'Once-through (river)'
            return 'Cooling tower (natural draft)'
        if plant == 'Grafenrheinfeld':
            return 'Cooling tower (natural draft)'
        if plant == 'Emsland':
            return 'Cooling tower (natural draft)'
        if plant == 'Neckarwestheim':
            return 'Cooling tower (natural draft)'
        if plant == 'Mülheim-Kärlich':
            return 'Cooling tower (natural draft)'
        if plant == 'Würgassen':
            return 'Cooling tower (natural draft)'
        # Greifswald (Baltic coast)
        if plant == 'Greifswald':
            return 'Once-through (seawater)'
        if plant == 'Rheinsberg':
            return 'Once-through (lake)'
        # Experimental/small
        if plant in ('AVR Jülich', 'THTR-300', 'KNK II', 'HDR Großwelzheim',
                      'Niederaichbach', 'MZFR', 'Vak Kahl', 'Lingen'):
            return None
        return None

    # --- UK --- All coastal (Magnox + AGR)
    if country == 'UK':
        if plant == 'Trawsfynydd':
            return 'Once-through (lake)'
        if plant == 'Winfrith':
            return None  # experimental
        if plant in ('Dounreay DFR', 'Dounreay PFR'):
            return None  # experimental fast reactors
        return 'Once-through (seawater)'

    # --- Russia ---
    if country == 'Russia':
        if plant in ('Novovoronezh 1', 'Novovoronezh 2'):
            return 'Cooling pond'
        if plant in ('Kursk 1', 'Kursk 2'):
            return 'Cooling pond'
        if plant in ('Rostov',):
            return 'Cooling pond'
        if plant in ('Smolensk',):
            return 'Cooling tower (natural draft)'
        if plant in ('Leningrad 1', 'Leningrad 2'):
            return 'Once-through (seawater)'
        if plant == 'Kola':
            return 'Once-through (lake)'
        if plant in ('Balakovo',):
            return 'Cooling tower (natural draft)'
        if plant in ('Kalinin',):
            return 'Cooling tower (natural draft)'
        if plant == 'Beloyarsk':
            return 'Cooling pond'
        if plant in ('Bilibino',):
            return 'Once-through (river)'
        if plant in ('Akademik Lomonosov',):
            return 'Once-through (seawater)'
        if plant == 'APS1 Obninsk':
            return None  # experimental
        if plant == 'Baltic':
            return None  # suspended
        if plant == 'BREST':
            return None  # under construction, experimental
        if plant in ('Cape Nagloynyn',):
            return None
        return None

    # --- China --- Most coastal
    if country == 'China':
        # All current Chinese nuclear plants are coastal
        coastal_plants = (
            'Daya Bay', 'Ling Ao', 'Tianwan', 'Fuqing', 'Ningde',
            'Fangchenggang', 'Yangjiang', 'Taishan', 'Haiyang', 'Sanmen',
            'Hongyanhe', 'Changjiang', 'Taipingling', 'Zhangzhou', 'Bailong',
            'Lianjiang', 'Lufeng', 'Fangjiashan', 'Qinshan 1', 'Qinshan 2',
            'Qinshan 3', 'Shidao Bay', 'Shidaowan', 'Sanao', 'Jinqimen',
            'Xudabao', 'Linglong', 'CFR',
        )
        if plant in coastal_plants:
            return 'Once-through (seawater)'
        if plant == 'CEFR':
            return None  # experimental, inland Beijing area
        return 'Once-through (seawater)'

    # --- Canada ---
    if country == 'Canada':
        if plant == 'Bruce':
            return 'Once-through (lake)'
        if plant in ('Pickering', 'Darlington'):
            return 'Once-through (lake)'
        if plant == 'Douglas Point':
            return 'Once-through (lake)'
        if plant == 'Point Lepreau':
            return 'Once-through (seawater)'
        if plant in ('Gentilly',):
            return 'Once-through (river)'
        if plant == 'Rolphton NPD':
            return 'Once-through (river)'
        return None

    # --- India ---
    if country == 'India':
        if plant == 'Tarapur':
            return 'Once-through (seawater)'
        if plant == 'Rajasthan':
            return 'Once-through (river)'
        if plant == 'Madras':  # MAPS / Kalpakkam
            return 'Once-through (seawater)'
        if plant == 'Narora':
            return 'Cooling tower (natural draft)'
        if plant == 'Kakrapar':
            return 'Cooling tower (natural draft)'
        if plant == 'Kaiga':
            return 'Cooling tower (natural draft)'
        if plant == 'Kudankulam':
            return 'Once-through (seawater)'
        if plant == 'PFBR':
            return 'Once-through (seawater)'
        return None

    # --- Sweden --- All coastal
    if country == 'Sweden':
        if plant == 'Ågesta':
            return None  # underground experimental
        return 'Once-through (seawater)'

    # --- Finland ---
    if country == 'Finland':
        return 'Once-through (seawater)'

    # --- Switzerland ---
    if country == 'Switzerland':
        if plant in ('Beznau', 'Mühleberg'):
            return 'Once-through (river)'
        if plant == 'Gösgen':
            return 'Cooling tower (natural draft)'
        if plant == 'Leibstadt':
            return 'Cooling tower (natural draft)'
        if plant == 'Lucens':
            return None  # experimental
        return None

    # --- Belgium ---
    if country == 'Belgium':
        if plant == 'Doel':
            return 'Once-through (river)'
        if plant == 'Tihange':
            return 'Cooling tower (natural draft)'
        if plant == 'BR-3':
            return None  # experimental
        return None

    # --- Spain ---
    if country == 'Spain':
        if plant == 'Almaraz':
            return 'Cooling tower (natural draft)'
        if plant in ('Asco',):
            return 'Once-through (river)'
        if plant == 'Cofrentes':
            return 'Cooling tower (natural draft)'
        if plant in ('Vandellos',):
            if unit == '1':
                return 'Once-through (seawater)'
            return 'Once-through (seawater)'
        if plant == 'Trillo':
            return 'Cooling tower (natural draft)'
        if plant == 'Jose Cabrera':
            return 'Once-through (river)'
        if plant == 'Santa María de Garoña':
            return 'Once-through (river)'
        return None

    # --- USA ---
    if country == 'USA':
        return _us_cooling_type(plant, unit, design, lat, lon)

    # --- Ukraine ---
    if country == 'Ukraine':
        if plant == 'Chernobyl':
            return 'Cooling pond'
        if plant == 'Zaporizhzhia':
            return 'Cooling pond'
        if plant == 'South Ukraine':
            return 'Cooling pond'
        if plant in ('Rivne', 'Khmelnytskyi'):
            return 'Cooling tower (natural draft)'
        return None

    # --- Taiwan ---
    if country == 'Taiwan':
        return 'Once-through (seawater)'

    # --- Brazil ---
    if country == 'Brazil':
        return 'Once-through (seawater)'

    # --- South Africa ---
    if country == 'South Africa':
        return 'Once-through (seawater)'

    # --- Mexico ---
    if country == 'Mexico':
        return 'Once-through (seawater)'

    # --- UAE ---
    if country == 'UAE':
        return 'Once-through (seawater)'

    # --- Argentina ---
    if country == 'Argentina':
        if plant in ('Atucha', 'Carem25'):
            return 'Once-through (river)'
        if plant == 'Embalse':
            return 'Cooling tower (natural draft)'
        return None

    # --- Armenia ---
    if country == 'Armenia':
        return 'Cooling tower (natural draft)'

    # --- Bangladesh ---
    if country == 'Bangladesh':
        return 'Once-through (river)'

    # --- Belarus ---
    if country == 'Belarus':
        return 'Cooling tower (natural draft)'

    # --- Bulgaria ---
    if country == 'Bulgaria':
        return 'Once-through (river)'

    # --- Czech Republic ---
    if country == 'Czech Republic':
        if plant == 'Dukovany':
            return 'Cooling tower (natural draft)'
        if plant == 'Temelin':
            return 'Cooling tower (natural draft)'
        return None

    # --- Egypt ---
    if country == 'Egypt':
        return 'Once-through (seawater)'

    # --- Hungary ---
    if country == 'Hungary':
        return 'Cooling tower (natural draft)'

    # --- Iran ---
    if country == 'Iran':
        return 'Once-through (seawater)'

    # --- Italy ---
    if country == 'Italy':
        if plant == 'Latina':
            return 'Once-through (seawater)'
        if plant == 'Garigliano':
            return 'Once-through (river)'
        if plant == 'Enrico Fermi':
            return 'Once-through (river)'
        if plant == 'Caorso':
            return 'Cooling tower (natural draft)'
        return None

    # --- Kazakhstan ---
    if country == 'Kazakhstan':
        return 'Once-through (seawater)'  # Aktau on Caspian

    # --- Lithuania ---
    if country == 'Lithuania':
        return 'Once-through (lake)'

    # --- Netherlands ---
    if country == 'Netherlands':
        if plant == 'Borssele':
            return 'Once-through (seawater)'
        if plant == 'Dodewaard':
            return 'Once-through (river)'
        return None

    # --- Pakistan ---
    if country == 'Pakistan':
        if plant == 'Karachi':
            return 'Once-through (seawater)'
        if plant == 'Chashma':
            return 'Once-through (river)'
        return None

    # --- Romania ---
    if country == 'Romania':
        return 'Once-through (river)'

    # --- Slovakia ---
    if country == 'Slovakia':
        return 'Cooling tower (natural draft)'

    # --- Slovenia ---
    if country == 'Slovenia':
        return 'Cooling tower (natural draft)'

    # --- Turkey ---
    if country == 'Turkey':
        return 'Once-through (seawater)'

    return None


def _us_cooling_type(plant, unit, design, lat, lon):
    """Determine cooling type for US plants."""
    # Clearly seawater/coastal
    seawater = {
        'San Onofre', 'Diablo Canyon', 'Millstone', 'Pilgrim',
        'Oyster Creek', 'Salem', 'Hope Creek', 'Brunswick',
        'Calvert Cliffs', 'Surry', 'Seabrook', 'St Lucie',
        'Crystal River', 'Maine Yankee', 'Humboldt Bay',
        'GE Vallecitos', 'Shoreham',
    }
    if plant in seawater:
        return 'Once-through (seawater)'

    # Indian Point - Hudson River (tidal/brackish, technically river)
    if plant in ('Indian Point',):
        return 'Once-through (river)'

    # Haddam Neck - Connecticut River
    if plant in ('Haddam Neck (Connecticut Yankee)',):
        return 'Once-through (river)'

    # Turkey Point - cooling canals/pond
    if plant == 'Turkey Point':
        return 'Cooling pond'

    # Palo Verde - desert, mechanical draft cooling towers
    if plant == 'Palo Verde':
        return 'Cooling tower (mechanical draft)'

    # Great Lakes plants
    lake_plants = {
        'Cook (Donald C. Cook)', 'Point Beach', 'Kewaunee',
        'Davis Besse', 'Fitzpatrick (James A. Fitzpatrick)',
        'Ginna (R. E. Ginna)', 'Nine Mile Point', 'Perry',
        'Zion', 'Big Rock Point',
    }
    if plant in lake_plants:
        return 'Once-through (lake)'

    # Cooling tower plants
    cooling_tower = {
        'Vogtle', 'Limerick', 'Susquehanna', 'Beaver Valley',
        'Byron', 'Braidwood', 'Callaway', 'Wolf Creek',
        'Comanche Peak', 'South Texas Project', 'River Bend',
        'Grand Gulf', 'Clinton', 'Catawba', 'McGuire',
        'Harris (Shearon Harris)', 'Summer (V C Summer)',
        'Watts Bar', 'Sequoyah', 'Rancho Seco',
    }
    if plant in cooling_tower:
        return 'Cooling tower (natural draft)'

    # River once-through
    river_plants = {
        'Browns Ferry', 'Quad Cities', 'Dresden', 'Monticello',
        'Duane Arnold', 'Cooper', 'Fort Calhoun', 'Prairie Island',
        'Vermont Yankee', 'Yankee NPS', 'Robinson (H B Robinson)',
        'Farley (Joseph M. Farley)', 'Hatch (Edwin I. Hatch)',
    }
    if plant in river_plants:
        return 'Once-through (river)'

    # Lake cooling for inland reservoir plants
    if plant in ('North Anna',):
        return 'Once-through (lake)'
    if plant in ('Oconee',):
        return 'Once-through (lake)'

    # Arkansas Nuclear One - Lake Dardanelle
    if plant == 'Arkansas Nuclear One':
        return 'Once-through (lake)'

    # LaSalle
    if plant == 'LaSalle':
        return 'Cooling pond'

    # Columbia (Hanford area)
    if plant == 'Columbia':
        return 'Cooling tower (mechanical draft)'

    # Three Mile Island - Susquehanna River with cooling towers
    if plant == 'Three Mile Island':
        return 'Cooling tower (natural draft)'

    # Peach Bottom - Conowingo Pond (Susquehanna River)
    if plant == 'Peach Bottom':
        return 'Once-through (river)'

    # Palisades - Lake Michigan
    if plant == 'Palisades':
        return 'Once-through (lake)'

    # Trojan - Columbia River with cooling tower
    if plant == 'Trojan':
        return 'Cooling tower (natural draft)'

    # Waterford - Mississippi River
    if plant == 'Waterford':
        return 'Once-through (river)'

    # Fermi - Lake Erie
    if plant == 'Fermi':
        return 'Once-through (lake)'

    # St Lucie already handled above
    # Experimental / early plants
    if plant in ('Bonus', 'Elk River', 'Hallam', 'Pathfinder',
                 'Piqua', 'Saxton', 'Shippingport', 'CVTR',
                 'Fort St. Vrain'):
        return None

    return None


# ---------------------------------------------------------------------------
# CONSTRUCTOR
# ---------------------------------------------------------------------------

def determine_constructor(plant, unit, country, design, supplier):
    """Determine the primary constructor."""

    # --- France ---
    if country == 'France':
        if design == 'UNGG':
            return 'EDF'
        if plant == 'Phenix':
            return 'CEA'
        if plant == 'Super-Phenix':
            return 'Novatome'
        if plant == 'Brennilis':
            return 'CEA'
        return 'Framatome'

    # --- Japan ---
    if country == 'Japan':
        if supplier in ('Toshiba',):
            return 'Toshiba'
        if supplier in ('Hitachi',):
            return 'Hitachi'
        if supplier in ('Hitatchi-GE',):
            return 'Hitachi-GE'
        if supplier in ('Mitsubishi',):
            return 'Mitsubishi Heavy Industries'
        if supplier == 'Westinghouse':
            return 'Mitsubishi Heavy Industries'
        if supplier == 'GE':
            return 'GE'
        # By design series for those without supplier
        if design and design.startswith('MHI'):
            return 'Mitsubishi Heavy Industries'
        if design and 'BWR' in design:
            # Early BWRs varied; Toshiba/Hitachi split
            if plant in ('Fukushima-Daiichi',):
                if unit == '1':
                    return 'GE'
                if unit in ('2', '3', '5'):
                    return 'Toshiba'
                if unit in ('4', '6'):
                    return 'Hitachi'
                return 'GE'
            if plant == 'Hamaoka':
                if unit in ('1', '2'):
                    return 'Toshiba'
                return 'Toshiba'
            if plant == 'Shimane':
                if unit == '1':
                    return 'Hitachi'
                return 'Hitachi'
            if plant == 'Tsuruga':
                if unit == '1':
                    return 'GE'
                return 'Mitsubishi Heavy Industries'
            if plant == 'Onagawa':
                return 'Toshiba'
            return None
        if design == 'Magnox':
            return 'GEC'  # Tokai was UK Magnox design
        if design == 'ATR':
            return 'Fuji Electric'
        if design == 'Monju':
            return 'Mitsubishi Heavy Industries'
        if plant == 'JPDR':
            return 'GE'
        return None

    # --- South Korea ---
    if country == 'South Korea':
        if design in ('APR1400',):
            return 'KEPCO E&C / Hyundai E&C'
        if design == 'OPR-1000':
            return 'KEPCO E&C / Hyundai E&C'
        if design == 'CANDU 6':
            return 'AECL'
        if design and design.startswith('W ') or design == 'CP1':
            return supplier if supplier else None
        return 'KEPCO E&C'

    # --- Russia ---
    if country == 'Russia':
        if supplier == 'Minsredmash':
            return 'Minsredmash'
        if design and 'VVER-1200' in design:
            return 'Atomstroyexport'
        if design and 'VVER-1000' in design:
            return 'Atomstroyexport'
        if design and 'VVER' in design:
            return 'Minsredmash'
        if design and 'RBMK' in design:
            return 'Minsredmash'
        if design and 'EGP' in design:
            return 'Minsredmash'
        if design and 'BN-' in design:
            return 'Minsredmash'
        if design and 'KLT' in design:
            return 'Baltiysky Zavod'
        if design == 'BREST-OD-300':
            return 'Rosatom'
        if design == 'RITM-200S':
            return 'Rosatom'
        return None

    # --- China ---
    if country == 'China':
        if supplier == 'Framatome':
            return 'Framatome'
        if supplier == 'Areva':
            return 'Areva'
        if supplier == 'Westinghouse':
            return 'Westinghouse'
        if supplier == 'Atomstroyexport':
            return 'Atomstroyexport'
        if supplier == 'Rosatom':
            return 'Atomstroyexport'
        if design and 'CNP' in design:
            return 'CNNC'
        if design and 'CPR' in design:
            return 'CGN'
        if design and 'ACPR' in design:
            return 'CGN'
        if design and 'HPR1000' in design:
            # HPR1000 built by both CNNC and CGN depending on site
            if plant in ('Fuqing', 'Zhangzhou', 'Changjiang', 'Shidaowan',
                         'Sanao', 'Jinqimen', 'Chashma', 'Karachi',
                         'Tianwan'):
                return 'CNNC'
            if plant in ('Fangchenggang', 'Taipingling', 'Ningde', 'Lufeng'):
                return 'CGN'
            if supplier == 'CNNC':
                return 'CNNC'
            return 'CNNC'
        if design and 'CAP' in design:
            return 'CNNC'
        if design == 'CANDU 6':
            return 'AECL'
        if design == 'HTR-PM':
            return 'CNNC'
        if design in ('BN-20', 'CFR-600'):
            return 'CNNC'
        if design == 'ACP100':
            return 'CNNC'
        return 'CNNC'

    # --- Germany ---
    if country == 'Germany':
        if design and ('Siemens' in design or design in ('Konvoi', 'Pre-Konvoi')):
            return 'Kraftwerk Union (KWU)'
        if design and 'BWR' in design:
            if supplier in ('KWU', 'Siemens'):
                return 'Kraftwerk Union (KWU)'
            if supplier == 'GE':
                return 'GE'
            return 'Kraftwerk Union (KWU)'
        if design and 'VVER' in design:
            return 'Atomenergoexport'
        if plant == 'Mülheim-Kärlich':
            return 'Brown Boveri / Babcock'
        if design == 'KWU PHWR':
            return 'Kraftwerk Union (KWU)'
        if design == 'PHWR':
            return 'Siemens'
        if design in ('AVR', 'THTR-300', 'KNK', 'HWGCR'):
            return None
        return None

    # --- UK ---
    if country == 'UK':
        if design == 'Magnox':
            if plant in ('Berkeley', 'Bradwell'):
                return 'TNPG'
            if plant in ('Hinkley Point A', 'Trawsfynydd'):
                return 'APC'
            if plant in ('Dungeness A', 'Sizewell A', 'Oldbury'):
                return 'TNPG'
            if plant in ('Wylfa',):
                return 'English Electric'
            if plant in ('Hunterston A',):
                return 'GEC'
            if plant in ('Sellafield',):
                return 'UKAEA'
            if plant in ('Chapelcross',):
                return 'UKAEA'
            return None
        if design == 'AGR':
            return 'National Nuclear Corporation (NNC)'
        if plant == 'Sizewell B':
            return 'Nuclear Electric'
        if design == 'EPR':
            return 'EDF Energy'
        if design in ('DFR', 'PFR', 'SGHWR'):
            return 'UKAEA'
        return None

    # --- USA ---
    if country == 'USA':
        # For US, the supplier is generally the NSSS vendor
        # Constructor is typically a separate A/E firm
        # Return supplier as a starting point where known
        if supplier:
            return supplier
        return None

    # --- Canada ---
    if country == 'Canada':
        return 'AECL'

    # --- India ---
    if country == 'India':
        if design and 'VVER' in design:
            return 'Atomstroyexport'
        if plant in ('Tarapur',) and design and 'BWR' in design:
            return 'GE'
        return 'NPCIL'

    # --- Belgium ---
    if country == 'Belgium':
        return supplier if supplier else None

    # --- Brazil ---
    if country == 'Brazil':
        if supplier == 'Westinghouse':
            return 'Westinghouse'
        if supplier == 'KWU':
            return 'Kraftwerk Union (KWU)'
        return supplier

    # --- Ukraine ---
    if country == 'Ukraine':
        if design and 'RBMK' in design:
            return 'Minsredmash'
        if design and 'VVER' in design:
            return 'Atomstroyexport'
        return None

    # VVER countries (standard pattern)
    if design and 'VVER' in design:
        if supplier in ('Atomstroyexport', 'Rosatom'):
            return 'Atomstroyexport'
        if supplier in ('Atomenergoexport',):
            return 'Atomenergoexport'
        if supplier == 'FAEA':
            return 'Atomenergoexport'
        return supplier if supplier else None

    # CANDU countries
    if design and 'CANDU' in design:
        return 'AECL'

    # Other Westinghouse-design plants
    if supplier == 'Westinghouse':
        return 'Westinghouse'

    # Other GE-design plants
    if supplier == 'GE':
        return 'GE'

    # KEPCO-exported designs (UAE)
    if supplier == 'KEPCO':
        return 'KEPCO'

    if supplier:
        return supplier

    return None


# ---------------------------------------------------------------------------
# ARCHITECT-ENGINEER
# ---------------------------------------------------------------------------

def determine_architect_engineer(plant, country, design, supplier):
    """Determine the architect-engineer."""

    if country == 'France':
        return 'EDF'

    if country == 'Japan':
        # Vertically integrated — same as constructor
        if supplier in ('Toshiba',):
            return 'Toshiba'
        if supplier in ('Hitachi',):
            return 'Hitachi'
        if supplier in ('Hitatchi-GE',):
            return 'Hitachi-GE'
        if supplier in ('Mitsubishi',):
            return 'Mitsubishi Heavy Industries'
        if supplier == 'Westinghouse':
            return 'Mitsubishi Heavy Industries'
        if supplier == 'GE':
            return 'GE'
        if design and design.startswith('MHI'):
            return 'Mitsubishi Heavy Industries'
        return None

    if country == 'South Korea':
        return 'KEPCO E&C'

    if country == 'Russia':
        return 'Atomenergoproekt'

    if country == 'China':
        if supplier == 'Framatome' or supplier == 'Areva':
            return 'EDF / CNPEC'  # joint for early imports
        if supplier == 'Westinghouse':
            return 'SNPTC'  # State Nuclear Power Technology Corp
        if supplier in ('Atomstroyexport', 'Rosatom'):
            return 'Atomenergoproekt / JNPC'
        if design and ('CPR' in design or 'ACPR' in design):
            return 'CNPEC'
        if design and 'CNP' in design:
            return 'CNPE'
        if design and ('HPR1000' in design or 'CAP' in design):
            if plant in ('Fuqing', 'Zhangzhou', 'Changjiang', 'Sanao',
                         'Jinqimen', 'Shidaowan', 'Tianwan', 'Xudabao'):
                return 'CNPE'
            if plant in ('Fangchenggang', 'Taipingling', 'Ningde', 'Lufeng'):
                return 'CNPEC'
            if supplier == 'CNNC':
                return 'CNPE'
            return 'CNPE'
        if design == 'CANDU 6':
            return 'AECL'
        if design == 'HTR-PM':
            return 'Tsinghua University / CNEC'
        return 'CNPE'

    if country == 'Germany':
        if design and ('Siemens' in design or design in ('Konvoi', 'Pre-Konvoi')):
            return 'KWU'
        if design and 'BWR' in design:
            return 'KWU'
        if design and 'VVER' in design:
            return 'Atomenergoproekt'
        return None

    if country == 'UK':
        if design == 'EPR':
            return 'EDF Energy'
        return None

    if country == 'USA':
        # Most varied — only populate confident cases
        return _us_architect_engineer(plant, design)

    if country == 'Canada':
        return 'AECL'

    if country == 'India':
        if design and 'VVER' in design:
            return 'Atomenergoproekt'
        return 'NPCIL'

    if country == 'Ukraine':
        return 'Atomenergoproekt'

    if country == 'Belgium':
        if plant in ('Doel', 'Tihange'):
            return 'Tractebel'
        return None

    if country == 'Brazil':
        if plant == 'Angra' and design and 'W ' in design:
            return 'Westinghouse'
        if design in ('Pre-Konvoi',):
            return 'KWU'
        return None

    if country == 'UAE':
        return 'KEPCO E&C'

    if country == 'Taiwan':
        if supplier == 'GE':
            return 'GE'
        if supplier == 'Westinghouse':
            return 'Bechtel'
        return None

    if country == 'South Africa':
        return 'Framatome'

    if country == 'Spain':
        if supplier == 'Westinghouse':
            return 'Westinghouse'
        if supplier == 'GE':
            return 'GE'
        if plant == 'Trillo':
            return 'KWU'
        return None

    if country == 'Sweden':
        if design and 'BWR' in design:
            return 'ASEA-Atom'
        if supplier == 'Westinghouse':
            return 'Westinghouse'
        return None

    if country == 'Finland':
        if design and 'VVER' in design:
            return 'Imatran Voima'
        if supplier == 'ASEA-Atom':
            return 'ASEA-Atom'
        if design == 'EPR':
            return 'Areva'
        return None

    if country == 'Switzerland':
        if plant in ('Beznau',):
            return 'Westinghouse'
        if plant == 'Gösgen':
            return 'KWU'
        if plant == 'Leibstadt':
            return 'GE'
        if plant == 'Mühleberg':
            return 'GE'
        return None

    if country == 'Netherlands':
        if plant == 'Borssele':
            return 'KWU'
        return None

    if country == 'Mexico':
        return 'GE'

    # VVER countries
    if design and 'VVER' in design:
        return 'Atomenergoproekt'

    # CANDU countries
    if design and 'CANDU' in design:
        return 'AECL'

    return None


def _us_architect_engineer(plant, design):
    """Determine A/E for US plants — only confident cases."""
    ae_map = {
        'Byron': 'Sargent & Lundy',
        'Braidwood': 'Sargent & Lundy',
        'LaSalle': 'Sargent & Lundy',
        'Clinton': 'Sargent & Lundy',
        'Dresden': 'Sargent & Lundy',
        'Quad Cities': 'Sargent & Lundy',
        'Oconee': 'Duke Power',
        'McGuire': 'Duke Power',
        'Catawba': 'Duke Power',
        'Browns Ferry': 'TVA',
        'Sequoyah': 'TVA',
        'Watts Bar': 'TVA',
        'Three Mile Island': 'Gilbert Associates',
        'Oyster Creek': 'Burns & Roe',
        'Fitzpatrick (James A. Fitzpatrick)': 'Stone & Webster',
        'Nine Mile Point': 'Stone & Webster',
        'Pilgrim': 'Bechtel',
        'San Onofre': 'Bechtel',
        'Palisades': 'Bechtel',
        'Diablo Canyon': 'Pacific Gas & Electric',
        'Millstone': 'Bechtel',
        'Palo Verde': 'Bechtel',
        'Calvert Cliffs': 'Bechtel',
        'South Texas Project': 'Bechtel',
        'Vogtle': 'Bechtel',
        'Limerick': 'Bechtel',
        'Susquehanna': 'Bechtel',
        'Comanche Peak': 'Gibbs & Hill',
        'Grand Gulf': 'Bechtel',
        'River Bend': 'Stone & Webster',
        'Hope Creek': 'Bechtel',
        'Salem': 'Public Service Electric',
        'Surry': 'Stone & Webster',
        'North Anna': 'Stone & Webster',
        'Beaver Valley': 'Stone & Webster',
        'Summer (V C Summer)': 'Gilbert Associates',
        'Harris (Shearon Harris)': 'Ebasco',
        'Hatch (Edwin I. Hatch)': 'Bechtel',
        'Farley (Joseph M. Farley)': 'Bechtel',
        'Cooper': 'Burns & Roe',
        'Wolf Creek': 'Bechtel',
        'Callaway': 'Bechtel',
        'Indian Point': 'United Engineers',
        'Waterford': 'Ebasco',
        'Seabrook': 'United Engineers',
        'Brunswick': 'United Engineers',
        'Perry': 'Gilbert Associates',
        'Robinson (H B Robinson)': 'Ebasco',
        'Cook (Donald C. Cook)': 'American Electric Power',
        'Monticello': 'Bechtel',
        'Vermont Yankee': 'Ebasco',
        'Peach Bottom': 'Bechtel',
        'Arkansas Nuclear One': 'Bechtel',
        'Turkey Point': 'Bechtel',
        'Crystal River': 'Gilbert Associates',
        'Davis Besse': 'Bechtel',
        'Trojan': 'Bechtel',
        'Rancho Seco': 'Bechtel',
        'Point Beach': 'Bechtel',
        'Kewaunee': 'Pioneer Service & Engineering',
        'St Lucie': 'Ebasco',
        'Fort Calhoun': 'Gibbs & Hill',
        'Prairie Island': 'Fluor',
        'Ginna (R. E. Ginna)': 'Gilbert Associates',
        'Shoreham': 'Stone & Webster',
        'Duane Arnold': 'Bechtel',
        'Columbia': 'Burns & Roe',
        'Maine Yankee': 'Stone & Webster',
        'Yankee NPS': 'Stone & Webster',
        'Zion': 'Sargent & Lundy',
        'Haddam Neck (Connecticut Yankee)': 'Stone & Webster',
    }
    return ae_map.get(plant)


# ---------------------------------------------------------------------------
# TURBINE SUPPLIER
# ---------------------------------------------------------------------------

def determine_turbine_supplier(country, design, supplier):
    """Determine the turbine supplier."""

    if country == 'France':
        if design in ('UNGG',):
            return 'Alstom'
        if design in ('Phenix', 'Super-Phenix'):
            return 'Alstom'
        if design == 'EL-4':
            return None
        return 'Alstom'

    if country == 'Japan':
        if supplier in ('Toshiba',):
            return 'Toshiba'
        if supplier in ('Hitachi',):
            return 'Hitachi'
        if supplier in ('Hitatchi-GE',):
            return 'Hitachi'
        if supplier in ('Mitsubishi',):
            return 'Mitsubishi Heavy Industries'
        if supplier == 'Westinghouse':
            return 'Mitsubishi Heavy Industries'
        if supplier == 'GE':
            return 'GE'
        if design and design.startswith('MHI'):
            return 'Mitsubishi Heavy Industries'
        if design and 'BWR' in design:
            return None  # could be Toshiba or Hitachi
        return None

    if country == 'South Korea':
        return 'Doosan Heavy Industries'

    if country == 'Russia':
        return 'Power Machines (LMZ)'

    if country == 'China':
        if supplier == 'Framatome' or supplier == 'Areva':
            return 'Alstom'  # early French imports
        if supplier == 'Westinghouse':
            return 'Harbin Electric'
        if supplier in ('Atomstroyexport', 'Rosatom'):
            return 'Power Machines (LMZ)'
        if design and ('CPR' in design or 'ACPR' in design):
            return 'Dongfang Electric'
        if design and 'CNP' in design:
            return 'Harbin Electric'
        if design and ('HPR1000' in design or 'CAP' in design):
            return 'Dongfang Electric'
        if design == 'HTR-PM':
            return 'Harbin Electric'
        if design == 'CANDU 6':
            return 'Harbin Electric'
        return 'Dongfang Electric'

    if country == 'Germany':
        if design and 'VVER' in design:
            return 'Skoda'
        if design and ('Siemens' in design or design in ('Konvoi', 'Pre-Konvoi')
                       or 'BWR' in (design or '')):
            return 'KWU'
        return 'KWU'

    if country == 'UK':
        if design == 'EPR':
            return 'Alstom'
        return 'GEC'

    if country == 'USA':
        # BWRs — GE supplied reactor + turbine
        if design and 'BWR' in design:
            return 'General Electric'
        # W PWRs
        if design and design.startswith('W '):
            return 'Westinghouse'
        if design == 'SNUPPS':
            return 'Westinghouse'
        if design == 'AP1000':
            return 'Westinghouse'
        if design and design.startswith('CE'):
            return 'General Electric'
        if design and design.startswith('B&W'):
            return 'Westinghouse'
        if design == 'PLWBR':
            return 'Westinghouse'
        return None

    if country == 'Canada':
        return 'GE Canada'

    if country == 'India':
        if design and 'BWR' in design:
            return 'GE'
        if design and 'VVER' in design:
            return 'Power Machines (LMZ)'
        return 'BHEL'

    if country == 'Belgium':
        return 'ACEC'

    if country == 'Brazil':
        if design and 'W ' in design:
            return 'Westinghouse'
        if design in ('Pre-Konvoi',):
            return 'KWU'
        return None

    if country == 'Ukraine':
        return 'Power Machines (LMZ)'

    if country == 'Sweden':
        if design and 'BWR' in design:
            return 'ASEA-Atom'
        if supplier == 'Westinghouse':
            return 'Westinghouse'
        return None

    if country == 'Finland':
        if design and 'VVER' in design:
            return 'Skoda'
        if supplier == 'ASEA-Atom':
            return 'ASEA-Atom'
        if design == 'EPR':
            return 'Alstom'
        return None

    if country == 'Switzerland':
        if design and 'W ' in design:
            return 'Brown Boveri (BBC)'
        if design and 'Siemens' in design:
            return 'KWU'
        if design and 'BWR' in design:
            return 'Brown Boveri (BBC)'
        return None

    if country == 'Spain':
        if design and 'BWR' in design:
            return 'General Electric'
        if design and 'W ' in design:
            return 'Westinghouse'
        if design and 'Siemens' in design:
            return 'KWU'
        return None

    if country == 'Taiwan':
        if design and 'BWR' in design:
            return 'General Electric'
        if design and 'W ' in design:
            return 'Westinghouse'
        return None

    if country == 'South Africa':
        return 'Alstom'

    if country == 'Mexico':
        return 'General Electric'

    if country == 'UAE':
        return 'Doosan Heavy Industries'

    if country == 'Netherlands':
        if design and 'Siemens' in design:
            return 'KWU'
        if design and 'BWR' in design:
            return 'General Electric'
        return None

    if country == 'Argentina':
        if design == 'KWU PHWR':
            return 'KWU'
        if design == 'CANDU 6':
            return 'GE Canada'
        return None

    if country == 'Pakistan':
        if design and 'CNP' in design:
            return 'Harbin Electric'
        if design == 'CANDU':
            return 'GE Canada'
        if design == 'HPR1000':
            return 'Dongfang Electric'
        return None

    # VVER countries
    if design and 'VVER' in design:
        return 'Skoda'

    # CANDU
    if design and 'CANDU' in design:
        return 'GE Canada'

    return None


# ---------------------------------------------------------------------------
# PRESSURE VESSEL MANUFACTURER
# ---------------------------------------------------------------------------

def determine_rpv_manufacturer(country, design, supplier):
    """Determine the reactor pressure vessel manufacturer."""

    # CANDU uses pressure tubes, not a pressure vessel
    if design and ('CANDU' in design or design in ('PHWR', 'IPHWR', 'PHWR-700',
                                                     'KWU PHWR', 'BLWR-250')):
        return None

    # Fast reactors don't have traditional RPVs in the same sense
    if design in ('Phenix', 'Super-Phenix', 'Monju', 'PFR', 'DFR',
                  'BN-600', 'BN-800', 'BN-350', 'BN-20', 'PFBR',
                  'LMFBR', 'SGR', 'KNK', 'CFR-600', 'BREST-OD-300'):
        return None

    # RBMK has no pressure vessel (graphite-moderated, pressure tubes)
    if design and 'RBMK' in design:
        return None

    # EGP-6 (Bilibino) — small, channel-type
    if design and 'EGP' in design:
        return None

    # UNGG and Magnox — some used steel vessels, some pre-stressed concrete
    if design == 'UNGG':
        return None  # varied, some concrete
    if design == 'Magnox':
        return None  # varied between steel and concrete vessels
    if design == 'AGR':
        return None  # pre-stressed concrete vessels

    # HTR designs
    if design in ('HTR-PM', 'AVR', 'Fort St. Vrain', 'THTR-300',
                  'Peach Bottom HTGR'):
        return None

    if country == 'France':
        return 'Creusot-Loire'

    if country == 'Japan':
        # JSW does most forgings, IHI and MHI also involved
        return 'Japan Steel Works (JSW)'

    if country == 'South Korea':
        if design == 'CANDU 6':
            return None  # CANDU
        return 'Doosan Heavy Industries'

    if country == 'Russia':
        if design and 'KLT' in design:
            return 'Izhora Plants'
        if design and 'RITM' in design:
            return 'Izhora Plants'
        if design and 'VVER' in design:
            return 'Izhora Plants'
        if design and ('AMB' in design or design == 'AM-1'):
            return None
        return None

    if country == 'China':
        if supplier == 'Framatome':
            return 'Framatome'  # early imports
        if supplier == 'Areva':
            return 'Mitsubishi Heavy Industries'  # Taishan EPR vessels
        if supplier == 'Westinghouse':
            return 'Doosan Heavy Industries'  # AP1000 vessels
        if supplier in ('Atomstroyexport', 'Rosatom'):
            return 'Izhora Plants'
        # Domestically produced
        if design and ('CPR' in design or 'ACPR' in design):
            return 'China First Heavy Industries'
        if design and 'CNP' in design:
            return 'China First Heavy Industries'
        if design and ('HPR1000' in design or 'CAP' in design):
            return 'China First Heavy Industries'
        if design == 'ACP100':
            return 'China First Heavy Industries'
        return 'China First Heavy Industries'

    if country == 'Germany':
        if design and 'VVER' in design:
            return 'Izhora Plants'
        # German RPV makers
        if design and 'BWR' in design:
            return 'Rotterdam Dockyard (RDM)'
        if design and ('Siemens' in design or design in ('Konvoi', 'Pre-Konvoi')):
            return 'Rotterdam Dockyard (RDM)'
        return None

    if country == 'UK':
        if design == 'SNUPPS':
            return 'Framatome'  # Sizewell B
        if design == 'EPR':
            return 'Mitsubishi Heavy Industries'
        return None

    if country == 'USA':
        # US had multiple RPV makers — use NULL for most
        if design and design.startswith('B&W'):
            return 'Babcock & Wilcox'
        if design and design.startswith('CE'):
            return 'Combustion Engineering'
        if design == 'AP1000':
            return 'Doosan Heavy Industries'
        return None

    if country == 'Canada':
        return None  # CANDU = pressure tubes

    if country == 'India':
        if design and 'VVER' in design:
            return 'Izhora Plants'
        if design and 'BWR' in design:
            return None  # early GE imports
        return 'Larsen & Toubro (L&T)'

    if country == 'Belgium':
        return None  # varied

    if country == 'Brazil':
        if design and 'W ' in design:
            return None
        if design in ('Pre-Konvoi',):
            return 'Rotterdam Dockyard (RDM)'
        return None

    if country == 'Ukraine':
        if design and 'VVER' in design:
            return 'Izhora Plants'
        return None

    if country == 'Sweden':
        if design and 'BWR' in design:
            return 'Uddcomb'
        if design and 'W ' in design:
            return 'Rotterdam Dockyard (RDM)'
        return None

    if country == 'Finland':
        if design and 'VVER' in design:
            return 'Izhora Plants'
        if design and 'BWR' in design:
            return 'Uddcomb'
        if design == 'EPR':
            return 'Mitsubishi Heavy Industries'
        return None

    if country == 'Switzerland':
        return None

    if country == 'Spain':
        if design and 'BWR' in design:
            return None
        if design and 'W ' in design:
            return None
        if design and 'Siemens' in design:
            return 'Rotterdam Dockyard (RDM)'
        return None

    if country == 'Taiwan':
        return None

    if country == 'South Africa':
        return 'Framatome'

    if country == 'UAE':
        return 'Doosan Heavy Industries'

    if country == 'Mexico':
        return None

    if country == 'Argentina':
        if design == 'KWU PHWR':
            return None  # pressure tube variant
        return None

    if country == 'Netherlands':
        if design and 'Siemens' in design:
            return 'Rotterdam Dockyard (RDM)'
        return None

    if country == 'Italy':
        return None

    if country == 'Slovenia':
        return None

    if country == 'Pakistan':
        if design and 'CNP' in design:
            return 'China First Heavy Industries'
        if design == 'HPR1000':
            return 'China First Heavy Industries'
        return None

    if country == 'Romania':
        return None  # CANDU

    # VVER countries
    if design and 'VVER' in design:
        return 'Izhora Plants'

    return None


# ---------------------------------------------------------------------------
# MAIN POPULATE
# ---------------------------------------------------------------------------

def populate(conn):
    """Populate reactor_details for all reactors."""
    reactors = get_reactors(conn)

    for r in reactors:
        reactor_id, plant, unit, design, country, supplier, lat, lon, status = r

        cooling = determine_cooling_type(plant, unit, country, design, lat, lon)
        constructor = determine_constructor(plant, unit, country, design, supplier)
        ae = determine_architect_engineer(plant, country, design, supplier)
        turbine = determine_turbine_supplier(country, design, supplier)
        rpv = determine_rpv_manufacturer(country, design, supplier)

        conn.execute("""
            INSERT OR REPLACE INTO reactor_details
            (reactor_id, cooling_type, constructor, architect_engineer,
             turbine_supplier, pressure_vessel_manufacturer)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (reactor_id, cooling, constructor, ae, turbine, rpv))

    conn.commit()
    return len(reactors)


def print_summary(conn):
    """Print coverage statistics."""
    total = conn.execute("SELECT COUNT(*) FROM reactor_details").fetchone()[0]

    fields = [
        'cooling_type', 'constructor', 'architect_engineer',
        'turbine_supplier', 'pressure_vessel_manufacturer'
    ]

    print(f"\n{'='*60}")
    print(f"reactor_details table — {total} rows")
    print(f"{'='*60}")

    for field in fields:
        filled = conn.execute(
            f"SELECT COUNT(*) FROM reactor_details WHERE {field} IS NOT NULL"
        ).fetchone()[0]
        pct = (filled / total * 100) if total else 0
        print(f"  {field:35s}: {filled:4d} / {total} ({pct:5.1f}%)")

    print()

    # Top values per field
    for field in fields:
        print(f"\n  Top {field} values:")
        rows = conn.execute(f"""
            SELECT {field}, COUNT(*) as cnt
            FROM reactor_details
            WHERE {field} IS NOT NULL
            GROUP BY {field}
            ORDER BY cnt DESC
            LIMIT 8
        """).fetchall()
        for val, cnt in rows:
            print(f"    {val:45s}: {cnt:4d}")

    # Country coverage
    print(f"\n{'='*60}")
    print("Coverage by country (cooling_type as representative):")
    print(f"{'='*60}")
    rows = conn.execute("""
        SELECT c.name,
               COUNT(*) as total,
               SUM(CASE WHEN rd.cooling_type IS NOT NULL THEN 1 ELSE 0 END) as filled
        FROM reactor_details rd
        JOIN reactors r ON rd.reactor_id = r.id
        JOIN countries c ON r.country_id = c.id
        GROUP BY c.name
        ORDER BY total DESC
    """).fetchall()
    for name, tot, filled in rows:
        pct = (filled / tot * 100) if tot else 0
        print(f"  {name:25s}: {filled:3d} / {tot:3d} ({pct:5.1f}%)")


def main():
    print(f"Database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)

    create_table(conn)
    count = populate(conn)
    print(f"Populated {count} reactor_details rows.")

    print_summary(conn)
    conn.close()


if __name__ == '__main__':
    main()
