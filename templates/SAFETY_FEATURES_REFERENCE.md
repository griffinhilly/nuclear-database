# Safety Features of Operating Light Water Reactors — Reference Summary

**Source:** Gavrilas, Hejzlar, Todreas, Shatilla. MIT / CRC Press, 1995 (reissued 2018). 312 pages.
**Scope:** All western-design LWRs operating as of June 1994. Excludes VVER/RBMK, PHWR, gas-cooled.

---

## 1. Reactor Family Trees — Standard Type Taxonomy

### BWR Standard Types (12 types, 3 design lineages)

| Designer | Country | Types | Key Plants |
|----------|---------|-------|------------|
| General Electric | USA | BWR/1, BWR/2, BWR/3, BWR/4, BWR/5, BWR/6 | BWR/1: Big Rock Point, Tarapur. BWR/3: Dresden 2, Fukushima Daiichi 1. BWR/4: Browns Ferry (largest deployed). BWR/6: Grand Gulf, Clinton |
| Siemens/KWU | Germany | BWR/69, BWR/72 | BWR/69: Brunsbüttel, Isar 1, Krümmel. BWR/72: Gundremmingen B&C |
| ABB-Atom | Sweden | BWR/G1, BWR/G2, BWR/G3, BWR/75 | G1: Oskarshamn 1, Ringhals 1. G3: Forsmark 1&2, Olkiluoto 1&2. BWR/75: Forsmark 3, Oskarshamn 3 |

### PWR Standard Types (17+ types, 5 design lineages)

| Designer | Country | Types | Key Plants |
|----------|---------|-------|------------|
| Westinghouse | USA | 1-loop, 2-loop, 3-loop, 4-loop, SNUPPS | Zorita (1-loop), Ginna (2-loop), Callaway/Wolf Creek (SNUPPS), Sizewell B (SNUPPS) |
| B&W | USA | 2-loop (OTSG) | Oconee 1-3, TMI-1, Crystal River 3, Davis-Besse 1 |
| CE / ABB-CE NP | USA | Pre-System 80, System 80, System 80K | Pre-S80: Calvert Cliffs, San Onofre 2&3. S80: Palo Verde 1-3. S80K: Korean plants |
| Framatome | France | CP0, CP1, CP2, P4, P'4, N4 | CP0: Fessenheim, Bugey. CP1: Tricastin, Gravelines. P4: Paluel. N4: Chooz B |
| Siemens/KWU | Germany | 2-loop, 3-loop, 4-loop, Konvoi | 2-loop: Obrigheim. Konvoi: Emsland, Isar 2, Neckar 2 |

---

## 2. Key Design Features by Reactor Type

### BWR Recirculation System Evolution

| Type | Recirculation | Power Density (kW/l) |
|------|--------------|---------------------|
| BWR/1 | Mixed (natural circ / external loops) | 24-46 |
| BWR/2 | Full external forced (5 loops) | 35 |
| BWR/3 | Jet pumps (1/3 external drives 2/3 internal) | 41 |
| BWR/4 | Jet pumps | 50 |
| BWR/5 | Jet pumps + valve throttling | 50 |
| BWR/6 | Jet pumps + valve throttling | 54 |
| BWR/69 | Internal axial pumps (8) — first in world | 50.6 |
| BWR/72 | Internal pumps (simplified) | 56.8 |
| BWR/G1 | External (4 pumps) | 36-48 |
| BWR/G2 | External (4-6 pumps) | 44-47 |
| BWR/G3 | Internal wet-motor pumps (8) | 46 |
| BWR/75 | Internal wet-motor pumps (8) | 48.6 |

### BWR Control Rod Drive Mechanisms

- **GE (all types):** Locking-piston hydraulic, bottom-entry. Scram ~1.5-5s. BWR/6 adds ganged rod movement.
- **Siemens BWR/69-72:** Dual mechanism — electromechanical (ball-screw, fine motion) + hydraulic (N₂ at 13 MPa for scram). Collective scram tank system.
- **ABB-Atom (all types):** Dual mechanism — electromechanical (screw-nut) + hydraulic scram. 4-10 rod scram groups with own modules.

### PWR Steam Generator Types

| Designer | SG Type | Key Distinction |
|----------|---------|----------------|
| Westinghouse | UTSG (U-tube) | Standard; Inconel 600 → 690 |
| B&W | OTSG (Once-through) | Unique; provides superheat; smaller secondary volume |
| CE | UTSG | Similar to Westinghouse |
| Framatome | UTSG (Model 68/19 for P4) | Broached 13%Cr tube support plates (first); no crossflow preheater |
| Siemens | UTSG | Incoloy 800 tubes (vs Inconel 600); preheating section from Brokdorf |

### PWR Fuel Array Evolution

| Designer | Array Progression |
|----------|------------------|
| Westinghouse | 14x14 → 15x15 → 17x17 (OFA/Vantage 5) |
| B&W | 15x15 |
| CE | 14x14 → 16x16 |
| Framatome | 15x15 → 17x17 (AFA design) |
| Siemens | 14x14 → 15x15 → 16x16 → 18x18 (first to 16x16 and 18x18) |

### Unique Siemens PWR Features
- **Reactor vessel:** "Short and fat" — larger diameter reduces neutron fluence by ~2x; no bottom-head penetrations; no longitudinal welds
- **Aeroball monitoring:** Pneumatic steel balls in 28 guide thimbles for 3D flux mapping (unique to Siemens)
- **Spherical containment:** All Siemens PWRs use spherical steel primary containment

---

## 3. Containment Types

### BWR Containments

| Type | Design Pressure (MPa) | Drywell Volume (m³) | Wetwell Air (m³) | Material | H₂ Control | Used By |
|------|----------------------|--------------------|--------------------|----------|------------|---------|
| MK-I | 0.38-0.42 | 3,700-5,000 | 2,700-3,800 | Steel-lined | N₂ inert | BWR/2, BWR/3, most BWR/4 |
| MK-I (Japan mod) | 0.38 | 8,900 | 5,300 | Steel-lined | N₂ inert | Japanese BWR/3-4 |
| MK-II | 0.31-0.36 | 5,500-8,600 | 3,800-5,400 | Steel-lined | N₂ inert | Later BWR/4, all BWR/5 |
| MK-III | 0.10 | 7,000-7,900 | 20,190-36,000 | Steel/concrete | Igniters | All BWR/6 |
| BWR/69 (Siemens) | 0.43 | 5,000 | 2,700 | Spherical double-wall steel | N₂ inert | German BWR/69 |
| BWR/72 (Siemens) | 0.43 | 8,500 | 6,000 | Cylindrical prestressed concrete | N₂ inert | Gundremmingen B&C |
| BWR/G2 (ABB) | 0.50 | 5,115 | 2,960 | Double-concrete + steel liner | N₂ inert + recombiners | Swedish BWR/G2 |
| BWR/G3 (ABB) | 0.55 | 4,320 | 3,560 | Prestressed concrete + steel | N₂ inert + recombiners | Swedish BWR/G3 |
| BWR/75 (ABB) | 0.60 | 5,857 | 2,850 | Prestressed concrete + steel | N₂ inert + recombiners | Forsmark 3, Oskarshamn 3 |

### PWR Containments

| Type | Design Pressure (MPa) | Free Volume (m³) | Leakage (%/day) | H₂ Control | Used By |
|------|----------------------|-------------------|-----------------|------------|---------|
| Large Dry (Single) | 0.40-0.65 | 60,000-95,000 | 0.1-1.0 | Recombiners | Most US PWRs |
| Large Dry (Double) | 0.40-0.65 | 70,000-95,000 | 0.25 | Recombiners | Some US PWRs |
| Subatmospheric | 0.40 | ~47,000 | 0.1-0.9 | Recombiners | Stone & Webster A-E plants (Surry, North Anna, etc.) |
| Ice Condenser | 0.18 | ~34,000 | 0.2-0.5 | Igniters | Sequoyah, McGuire, Catawba, Cook, Ohi 1&2 |
| German Spherical Double | 0.40-0.63 | 37,000-71,400 | 0.25 | Recombiners (Venturi) | All Siemens PWRs |
| French Single (3-loop) | 0.42 | ~49,400 | 0.165 | Recombiners | CPO, CP1, CP2 |
| French Double (4-loop) | 0.38-0.43 | 70,400-81,400 | 0.35 | Recombiners | P4, P'4, N4 |

---

## 4. Emergency Core Cooling Systems (ECCS)

### BWR ECCS by Type

| Type | HP System | LP Systems | ADS | Redundancy |
|------|-----------|-----------|-----|-----------|
| BWR/2 | FCI 1×100% | LPCS 2×100% | Yes | N+1 |
| BWR/3 | HPCI 1×100% | LPCS 2×100% + LPCI 2×100% | Yes | N+1 |
| BWR/4 | HPCI 1×100% | LPCS 2×100% + LPCI 2-4×100% | Yes | N+1 |
| BWR/5 | HPCS 1×100% | LPCS 2×100% + LPCI 1×100% | Yes | N+1 |
| BWR/6 | HPCS 1×100% (407 kg/s) | LPCS 1×100% + LPCI 3×33% | Yes | 3-division |
| BWR/69 | HP inj + HPCS | LPCI 4×50% | Yes | N+2 |
| BWR/72 | 3×100% (HP+LP+RHR per train) | Integrated in trains | Yes | N+2 (300%) |
| BWR/G1 | AFS 2×100% | LPCI | Yes | N+1 |
| BWR/G3 | AFS 4×50% | LPCI 4×50% + LPCS 4×50% | Yes | N+2 |
| BWR/75 | AFS 4×50% (22 kg/s ea) | LPCI 2×50% + LPCS 2×50% (710 kg/s ea) | Yes | N+2 |

### PWR ECCS Comparison (4-loop designs)

| Feature | Westinghouse | Siemens Konvoi | Framatome P4 |
|---------|-------------|---------------|--------------|
| Accumulators | 4 (136 m³, 4.5 MPa) | 8 (272 m³, 2.5 MPa) | 4 (188 m³, 4.4 MPa) |
| HHSI trains | 2 (N+1) | 4×50% (N+2) | 2 (N+1) |
| HHSI shutoff | 5.0-8.3 MPa | 11.0 MPa | 10.2-12.0 MPa |
| LHSI trains | 2 | 4×50% (N+2) | 2 (N+1) |
| EFW trains | 2-3 | 4×50% (N+2) | 2 (N+1) |
| Injection legs | Cold only | Hot + cold (3-way valve) | Cold only |

### Redundancy Gradient by Country
- **USA / France:** ~N+1 (2-train baseline)
- **Sweden:** N+1 to N+2 (BWR/G3 and BWR/75 achieve N+2)
- **Germany:** N+2 throughout (regulatory requirement)

---

## 5. Severe Accident Provisions

### Filtered Containment Venting by Country

| Country | System | Efficiency | When |
|---------|--------|-----------|------|
| Sweden | FILTRA gravel bed / MVSS venturi scrubber | 99.9% | 1985 (first in world) |
| Germany | Venturi scrubber + fiber filter (BWR) / 2-stage steel (PWR) | >99.99% | All units complete |
| France | Single-stage sand filters | Lower | Post-Chernobyl |
| Switzerland | Filtered venting + IRHRS/SEHR | — | Backfitted |
| USA | Hardened vent (MK-I only, no filter) | No filtering | Requires AC/DC power |

### Hydrogen Control by Containment

| Containment | Method |
|-------------|--------|
| All BWRs (small volume) | N₂ inerting |
| MK-III, Ice Condenser | Igniters |
| Large Dry PWR, Subatmospheric | Recombiners only |
| German BWR/69 | N₂ inert, double-wall annulus processing |

---

## 6. Designer Lineages & Licensing

### BWR Licensing Chain
- **GE** → AEG-Telefunken (1964 license) → KWU/Siemens (1969, independent by 1987)
- **GE** → Hitachi + Toshiba (1967 licenses) → ABWR co-design (1985+)
- **GE** ↔ Asea-Atom (1974 cross-license) → ABB-Atom internal pump tech → GE (1981 sublicense for ABWR)

### PWR Licensing Chain
- **Westinghouse** → Framatome (1958 license, terminated 1981) → CP0 ≈ Virgil C. Summer
- **Westinghouse** → MHI (1961 technical assistance) → 3 generations of Japanese PWRs
- **Westinghouse** ↔ Siemens (1962-1969 collaboration, then independent)
- **B&W** → BBR/ABB-Reaktor (license for Mülheim-Kärlich, heavily modified)
- **CE** acquired by ABB (1990) → ABB-CE NP; S80K developed with KAERI for Korea

### Key Corporate Genealogy
- **KWU** = AEG + Siemens (1969) → Siemens sole owner (1980s)
- **ABB-Atom** = Asea-Atom (1969) → Asea sole owner (1981) → ABB merger (1988)
- **ABB** houses 3 independent nuclear lineages: ABB-Atom (Swedish BWR), ABB-Reaktor (German PWR/BBR), ABB-CE NP (US PWR/CE)

---

## 7. Potential Database Fields

Based on the textbook's data, these fields could enrich reactor detail pages:

| Field | Examples | Source Chapter |
|-------|---------|---------------|
| `design_series` | BWR/4, Konvoi, CP1, Pre-S80 | Ch 2 |
| `containment_type` | MK-I, Large Dry, Ice Condenser, Spherical Double | Ch 8 |
| `containment_design_pressure_mpa` | 0.42, 0.63 | Ch 8 |
| `containment_volume_m3` | 60,000 | Ch 8 |
| `loop_count` | 1, 2, 3, 4 (PWR only) | Ch 2 |
| `recirculation_type` | Jet pumps, Internal pumps, External loops, Natural circulation | Ch 4 |
| `steam_generator_type` | UTSG, OTSG | Ch 4 |
| `hydrogen_control` | N₂ inert, Igniters, Recombiners | Ch 8-9 |
| `filtered_venting` | FILTRA, MVSS, Sand bed, Hardened vent, None | Ch 9 |
| `eccs_redundancy` | N+1, N+2 | Ch 7 |
| `architect_engineer` | Bechtel, Stone & Webster, Ebasco, etc. | Ch 2 |
| `designer_lineage` | "GE-licensed, Toshiba-built" | Ch 3 |
| `fuel_array` | 8x8, 17x17, SVEA 10x10 | Ch 4 |
| `vessel_material` | SA 508, SA 533-B, 22NiMoCr37 | Ch 4 |

---

## 8. Country Fleet Summaries

| Country | BWR Types | PWR Types | Total (1994) |
|---------|-----------|-----------|-------------|
| USA | BWR/1-6 (37) | WH 1-4 loop + SNUPPS, B&W 2-loop, CE Pre-S80/S80 (72) | 109 |
| France | — | CP0/CP1/CP2/P4/P'4 (52) | 52 |
| Japan | BWR/2-5 (24) | WH/MHI 2-4 loop (21) | 45 |
| Germany | BWR/69, BWR/72 (7) | Siemens 2-4 loop + Konvoi (13) | 20 |
| Korea | — | WH 2-3 loop + Framatome CP2 (8) | 8 |
| Sweden | BWR/G1-G3, BWR/75 (9) | WH 3-loop (3) | 12 |
| Belgium | — | WH 2-loop + Framatome 3-loop (7) | 7 |
| Spain | BWR/3, BWR/6 (2) | WH 1+3 loop + Siemens 3-loop (7) | 9 |
| Switzerland | BWR/4, BWR/6 (2) | WH 2-loop + Siemens 3-loop (3) | 5 |
| Taiwan | BWR/4, BWR/6 (4) | WH 3-loop (2) | 6 |
| Finland | BWR/G3 (2) | VVER-440 (2, excluded from scope) | 2 (LWR) |
| India | BWR/1 (2) | — | 2 |
| Others | BWR/1: Netherlands (1), BWR/5: Mexico (1) | Various single units | — |
