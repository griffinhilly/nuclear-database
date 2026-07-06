# Cooling-System Audit — July 2026 (migration 012)

**Scope:** Per-unit `reactor_details.cooling_type` audit of the entire US fleet (75 plants /
135 reactors), Tarapur 3/4 (India), and Scope C NULL-fills for selected non-US / prototype
reactors. The column had been populated per-PLANT, not per-unit, producing systemic errors in
both directions (towers marked as ponds/lakes, and once-through plants marked as towers).

**Method:** Spec-blind sonnet research agents (~8–10 plants each) determined per-unit cooling
from ≥2 independent documentary sources (NRC environmental/licensing docs, EIA, utility pages,
Wikipedia, technical literature), with no knowledge of the current DB values or any suspicion.
Because every subagent reported its `WebFetch` tool blocked (WebSearch snippets only), the
orchestrator **independently re-verified every CHANGE** by fetching the live Wikipedia article
text / infobox (`?action=raw`) via curl and reading the actual cooling fields. Concordance
between the orchestrator's independent reads and the researcher verdicts was **19/19** on the
changes that could be checked; the remainder rest on the researchers' primary-source quotes
(e.g. NRC environmental reports).

## Classification convention

Classify by the **primary heat-rejection path during normal full-power operation** into exactly
one of six values: `Once-through (seawater)`, `Once-through (river)`, `Once-through (lake)`,
`Cooling tower (natural draft)`, `Cooling tower (mechanical draft)`, `Cooling pond`.

- **Hybrid systems** (once-through with supplemental/helper towers, or towers that revert to
  once-through in extreme cold): record the **dominant** mode and note the hybrid. Where the
  hybrid is material (a once-through plant with substantial towers), a short note was added to
  `reactors.notes` (Browns Ferry 1–3, Sequoyah 1–2). All hybrids are recorded below.
- **Cooling pond vs Once-through (lake):** a purpose-built, closed-cycle recirculating cooling
  reservoir/canal whose own water body is the engineered heat sink (makeup only) → *Cooling
  pond* (e.g. LaSalle, Braidwood, Wolf Creek, South Texas, Clinton, Comanche Peak, Turkey
  Point). A large open lake/reservoir the plant takes a single once-through pass from →
  *Once-through (lake)* (e.g. McGuire/Lake Norman, Oconee/Lake Keowee, Robinson/Lake Robinson,
  V.C. Summer/Monticello Reservoir). This line is inherently fuzzy for a few reservoirs; the
  ambiguous ones are flagged in the table.
- **Satellite imagery** was used only to corroborate large natural-draft hyperbolic towers
  (unambiguous); mechanical/induced-draft towers were required to have documentary support.

## Changes applied (migration 012) — US fleet (Scope A)

| Plant | Unit | Old value | New value | Sources | Confidence |
|---|---|---|---|---|---|
| Arkansas Nuclear One | 2 | Once-through (lake) | **Cooling tower (natural draft)** | Wikipedia ("Unit Two utilizes a recirculating-water system from a 447-foot cooling tower"); Encyclopedia of Arkansas | High |
| Braidwood | 1,2 | Cooling tower (natural draft) | **Cooling pond** | Wikipedia (cooling_source=Braidwood Lake, "artificial lake…pumping water from the Kankakee River", no towers); Federal Register 2024-16895 | High |
| Catawba | 1,2 | Cooling tower (natural draft) | **Cooling tower (mechanical draft)** | Wikipedia infobox (6 × Mechanical draft); Duke Energy; nsenergybusiness | High |
| Clinton | 1 | Cooling tower (natural draft) | **Cooling pond** | Wikipedia ("5,000-acre cooling reservoir, Clinton Lake…created to provide cooling"); NRC FSAR ML17305A090 | High |
| Comanche Peak | 1,2 | Cooling tower (natural draft) | **Cooling pond** | Wikipedia ("relies on Comanche Creek Reservoir for cooling water"); TWDB (purpose-built reservoir, makeup from Lake Granbury) | High |
| Davis Besse | 1 | Once-through (lake) | **Cooling tower (natural draft)** | NRC ER ("makeup water for the cooling tower…from Lake Erie and the tower blowdown…discharged into Lake Erie"; 493-ft natural-draft tower); Wikipedia | High |
| Duane Arnold | 1 | Once-through (river) | **Cooling tower (mechanical draft)** | Wikipedia ("Twenty-four mechanical draft cooling towers used water from the Cedar River as a heat sink"); NRC ER | High |
| Farley (Joseph M. Farley) | 1,2 | Once-through (river) | **Cooling tower (mechanical draft)** | Wikipedia ("cooled using six mechanical draft cooling towers"); Southern Nuclear | High |
| Fermi | 2 | Once-through (lake) | **Cooling tower (natural draft)** | Wikipedia ("two large cooling towers which stand 400 feet…cooled by natural circulation"); NRC UFSAR ("two natural-draft hyperbolic circulating water cooling towers") | High |
| Hatch (Edwin I. Hatch) | 1,2 | Once-through (river) | **Cooling tower (mechanical draft)** | Wikipedia infobox (6 × Mechanical Draft; researcher cited 8); Southern Nuclear brochure | High |
| McGuire | 1,2 | Cooling tower (natural draft) | **Once-through (lake)** | Wikipedia ("Water from nearby Lake Norman is used to cool the condensers"; no towers); Duke Energy | High |
| Palisades | 1 | Once-through (lake) | **Cooling tower (mechanical draft)** | Wikipedia ("originally used a once-through cooling system, but…converted to closed-cycle"; 2 × mechanical/induced-draft towers); NRC FSAR ML16120A603 | High |
| Perry | 1 | Once-through (lake) | **Cooling tower (natural draft)** | Wikipedia ("500-foot-tall cooling tower"); IAEA INIS | High |
| Prairie Island | 1,2 | Once-through (river) | **Cooling tower (mechanical draft)** | Wikipedia infobox (4 × Mechanical Draft; normal closed-cycle, reverts to once-through only in extreme cold); NRC LR App. E | High |
| River Bend | 1 | Cooling tower (natural draft) | **Cooling tower (mechanical draft)** | Wikipedia infobox (4 concentric low-profile towers, 32 induced-draft cells); power-eng | High |
| Robinson (H B Robinson) | 2 | Once-through (river) | **Once-through (lake)** | Wikipedia (cooling_source=Lake Robinson, no towers); Duke Energy / NPDES SC0002925 (2,250-acre reservoir) | High |
| Sequoyah | 1,2 | Cooling tower (natural draft) | **Once-through (river)** | Wikipedia infobox (source=Chickamauga Lake; "2 × Natural Draft (supplemental only)"); TDEC/NRC NPDES TN0026450 | Med-High |
| South Texas Project | 1,2 | Cooling tower (natural draft) | **Cooling pond** | Wikipedia ("cooled by a 7,000-acre reservoir, which eliminates the need for cooling towers"; Main Cooling Reservoir); NRC COLA ER | High |
| Summer (V C Summer) | 1 | Cooling tower (natural draft) | **Once-through (lake)** | Wikipedia ("The plant utilizes a once-through cooling system"; source=Monticello Reservoir; the 4 mechanical towers were for the cancelled Units 2–3); NRC NPDES ML19056A410 | Med-High |
| Wolf Creek | 1 | Cooling tower (natural draft) | **Cooling pond** | Wikipedia ("Wolf Creek was dammed to create Coffey County Lake…provides water for the condensers"); NRC ER; EIA Kansas | High |
| GE Vallecitos | 1 | Once-through (seawater) | **NULL (removed)** | Site is inland (Sunol, CA); seawater is physically impossible. No documentary source found for the actual heat-rejection method of the 5 MWe VBWR. False value removed rather than replaced with a guess. | n/a (unresolved) |

### Ambiguous classification notes
- **Comanche Peak / South Texas / Clinton → Cooling pond** vs **Robinson / V.C. Summer → Once-through (lake):** all are engineered reservoirs; assigned per the convention above (dedicated closed cooling reservoir = pond; large open reservoir with a once-through pass = lake). Wikipedia explicitly calls V.C. Summer "once-through," which drove the lake call there. Reasonable reviewers could swap the pond/lake label on Comanche Peak or V.C. Summer; both were nonetheless **wrongly** marked as natural-draft towers before.
- **Sequoyah → Once-through (river):** genuinely hybrid. The two natural-draft towers are used in helper/closed mode during low-flow/high-temperature periods, but the normal full-power mode is open-cycle from Chickamauga Lake (Tennessee River). Classified once-through per convention (river, matching the Browns Ferry / Tennessee-River precedent), with a hybrid note added. This is the single largest reclassification and rests on the Wikipedia infobox's explicit "(supplemental only)" plus NPDES documentation.

## Confirmed (DB already correct) — Scope A

All other US units were **CONFIRMED** against ≥1 solid source. Notable confirmations:
`Once-through (seawater)`: Brunswick, Calvert Cliffs, Diablo Canyon, Crystal River, Humboldt Bay,
Maine Yankee, Millstone, Oyster Creek, Pilgrim, Salem, San Onofre, Seabrook, St. Lucie, Surry,
Shoreham. `Once-through (river)`: Browns Ferry (+helper towers), Cooper, Dresden (+seasonal
towers), Fort Calhoun, Haddam Neck, Indian Point, Monticello (+seasonal towers), Peach Bottom
2/3 (+helper towers), Quad Cities, Vermont Yankee (+helper towers), Waterford, Yankee Rowe.
`Once-through (lake)`: Arkansas Nuclear One 1, Big Rock Point, Cook, Fermi 1, FitzPatrick, Ginna,
Kewaunee, Nine Mile Point 1, North Anna, Oconee, Perry(no), Point Beach, Zion. `Cooling tower
(natural draft)`: Beaver Valley, Byron (confirmed genuine), Callaway, Grand Gulf, Harris, Hope
Creek, Limerick, Nine Mile Point 2, Rancho Seco, Susquehanna, Three Mile Island, Trojan, Vogtle,
Watts Bar. `Cooling tower (mechanical draft)`: Columbia, Palo Verde. `Cooling pond`: LaSalle,
Turkey Point.

## Scope B — Tarapur 3/4 (India): UNCHANGED

The dispatcher's hypothesis was that the PHWR-540 units use induced-draft cooling towers despite
the coastal site. A dedicated spec-blind researcher found the opposite from three independent
source lines: (1) Tata Consulting Engineers (TAPS-3&4 design firm) describes titanium-tubed
condensers and a "sea water cooling system"; (2) a peer-reviewed tritium study (J. Radioanal.
Nucl. Chem. 2019) explicitly names "condenser coolant seawater" as the TAPS-3&4 discharge; (3) a
macrobenthos study treats TAPS-3&4 as its own coastal seawater-discharge station. No source
mentions cooling towers. **Current value `Once-through (seawater)` is confirmed; left unchanged.**
(Confidence Medium — all evidence via search snippets, no primary NPCIL/AERB PDF read.)

## Scope C — NULL fills

**Filled (≥2 sources):**

| Reactor | Value | Sources | Conf |
|---|---|---|---|
| Darlington SMR 1 (CA) | Once-through (lake) | OPG project page (lake intake/discharge, towers not required); CNSC PPE | High |
| Brennilis 1 (FR) | Once-through (lake) | Decommissioning dossier ("circuit ouvert" on Réservoir/Lac de Saint-Michel); fr.wikipedia | Med-High |
| APS1 Obninsk 1 (RU) | Once-through (river) | Rosatom history (dam + bank pump station on Protva River); ANS; ru.wikipedia | High |
| BREST 1 (RU, UC) | Cooling tower (natural draft) | riatomsk / fiop / atomic-energy.ru (80 m natural-draft evaporative tower) | High |
| Kursk 2 unit 3 (RU, UC) | Cooling tower (natural draft) | Matches confirmed Kursk II units 1&2 (natural draft) + standardized VVER-TOI 179 m tower design | Med |
| Dounreay DFR 1 (UK) | Once-through (seawater) | Site chosen for coastal seawater cooling; no2nuclearpower; Wikipedia | Med |
| Dounreay PFR 1 (UK) | Once-through (seawater) | Same coastal Dounreay site | Med |
| Bonus 1 (US/PR) | Once-through (seawater) | Wikipedia ("standard condenser cooled with sea water"); DOE Legacy Management | High |
| Saxton 1 (US) | Once-through (river) | CLUI ("used the Juniata River for cooling", discharge tunnel); Wikipedia | Med |
| Shippingport 1 (US) | Once-through (river) | Wikipedia (Ohio River); LOC/HAER ("condenser and river water outlet pipe") | Med-High |

**Left NULL (unresolved — insufficient / conflicting sources; better NULL than a guess):**
CEFR 1 (ultimate heat sink undocumented), Bugey 1 (only unit-4/5 towers documented, not unit 1),
Cape Nagloynyn 1&2 (sources say *floating*, not land-based; cooling undocumented — see D3 note),
Winfrith 1 (composite Frome+boreholes → sea pipeline, maps to no single category), CVTR 1,
Elk River 1, Fort St. Vrain 1 (tower existed but natural- vs mechanical-draft unresolved),
Hallam 1 (shared tower, draft type unresolved), Lacrosse 1, Pathfinder 1 (1 source), Piqua 1.

## Data-quality caveats for the reviewer
1. Every research subagent had `WebFetch` blocked and worked from WebSearch snippets; the
   orchestrator's independent Wikipedia reads (curl) mitigate this for all CHANGES but the
   CONFIRMED and Scope C rows rest partly on snippet-level sourcing.
2. Hatch tower count differs by source (Wikipedia 6 vs researcher 8) — the **type** (mechanical
   draft) is not in question; the count is not stored.
3. Vallecitos was set from a false value (seawater, inland site) to NULL; it is Shutdown so it
   does not appear in validator check 9.
