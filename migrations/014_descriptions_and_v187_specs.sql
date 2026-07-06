-- 014_descriptions_and_v187_specs.sql
-- Date: 2026-07-06
-- Description: 16 model + 4 plant encyclopedic descriptions (each individually researched;
--   orchestrator-written for register consistency), plus completion of one confidently-
--   sourced VVER-1000/187 design spec (control-element count).
-- Affected tables: entity_descriptions (+20 rows); design_series_specs (1 row updated).
-- Note: Cape Nagloynyn is described as a FLOATING (moored FPU) SMR project per multiple
--   sources (WNN/GEM/Polar Journal), correcting an earlier 'land-based' framing.

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'BWRX-300', 'The BWRX-300 is a roughly 300 MWe small modular boiling water reactor from GE Hitachi (GE Vernova), the tenth iteration of the BWR line and a simplification of the licensed ESBWR. It relies on natural circulation and passive isolation-condenser decay-heat removal, dispensing with recirculation pumps and shrinking the plant footprint. Ontario Power Generation''s Darlington unit 1, the lead deployment, began construction in 2025.', 'GE Vernova; IAEA ARIS SMR Catalogue; World Nuclear News', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'CPR-1000+', 'The CPR-1000+ is an improved version of CGN''s CPR-1000, a Generation II+ three-loop pressurized water reactor of about 1,080 MWe gross descended from the French M310 design. The ''+'' marks added safety and digital-instrumentation upgrades over the base CPR-1000. It is used at Yangjiang units 3 and 4 in Guangdong, China.', 'Nuclear Engineering International; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'M310+', 'The M310+ is CNNC''s improved three-loop pressurized water reactor derived from the French M310 export design that also seeded the CPR-1000 line. Rated in the 1,000 MWe class, it carries upgraded safety systems over the original M310. It powers the Fuqing 1-4 and Ling Ao 1-2 units in China.', 'Nuclear Engineering International; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'RITM-200S', 'The RITM-200S is a compact integral-layout pressurized water reactor from OKBM Afrikantov, adapted from the RITM-200 reactor that powers Russia''s newest nuclear icebreakers. Each unit produces roughly 50 MWe with the steam generators built inside the reactor vessel. It is the reactor selected for the small modular power units serving the remote Baimskaya mining district in Chukotka.', 'OKBM Afrikantov / Rosatom; Nuclear Engineering International; World Nuclear News', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VBWR', 'The Vallecitos Boiling Water Reactor (VBWR) was an early experimental boiling water reactor built by General Electric at its Vallecitos site in California and operated from 1957 to 1963. In 1957 it became one of the first privately owned reactors to supply electricity to a US utility grid. It served as a testbed for the boiling-water technology that GE carried into the commercial Dresden 1 plant.', 'US NRC; ASME Engineering Landmark', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-213+', 'The VVER V-213+ is a safety-enhanced development of the Soviet-era VVER-440/V-213 pressurized water reactor, rated about 440 MWe net. Building on the V-213''s bubble-condenser containment and emergency core cooling, the ''+'' configuration adds Western-standard backfits such as upgraded instrumentation and additional injection capability. It is used at Mochovce units 3 and 4 in Slovakia.', 'World Nuclear Association; World Nuclear News', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-412M', 'The VVER V-412M is the reactor plant of Kudankulam units 3 and 4 in Tamil Nadu, India, a VVER-1000 (AES-92) design of about 1,000 MWe gross built by Russia''s Atomstroyexport to OKB Gidropress specifications. Units 3 and 4 repeat the earlier Kudankulam 1 and 2 with added post-Fukushima safety measures. Both units are under construction.', 'OKB Gidropress; World Nuclear Association; NPCIL', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-412T', 'The VVER V-412T is the reactor plant of Kudankulam units 5 and 6 in Tamil Nadu, India, continuing the VVER-1000 (AES-92) series of about 1,000 MWe gross begun at the site. Like the other Kudankulam pairs it is supplied by Russia''s Atomstroyexport to OKB Gidropress designs for NPCIL. Both units are under construction.', 'OKB Gidropress; Atomstroyexport; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-491S', 'The VVER V-491S is the reactor plant of Xudabao (Xudapu) units 3 and 4 in Liaoning, China, a VVER-1200 of about 1,270 MWe gross based on the St. Petersburg (Atomenergoproekt) V-491 design. It is supplied by Russia''s Atomstroyexport and is distinct from the Moscow-designed V-392M VVER-1200 used in Russia. Both units are under construction.', 'OKB Gidropress; World Nuclear Association; World Nuclear News', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-491T', 'The VVER V-491T is the reactor plant of Tianwan units 7 and 8 in Jiangsu, China, a VVER-1200 of about 1,265 MWe gross in the St. Petersburg V-491 family. It succeeds the earlier V-428 VVER-1000 units at Tianwan and is supplied by Russia''s Atomstroyexport. Both units are under construction.', 'OKB Gidropress; World Nuclear Association; CNNC', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-510K', 'The VVER V-510K is the VVER-TOI reactor plant used at Kursk II in Russia, an optimized development of the VVER-1200 of about 1,255 MWe gross designed by OKB Gidropress for standardized, faster construction. Kursk II unit 1 became the first VVER-TOI reactor to reach the grid, in early 2026. Units 2 and 3 are under construction.', 'OKB Gidropress; World Nuclear News; NucNet', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-527', 'The VVER V-527 is the reactor plant of the Paks II expansion (unit 5) in Hungary, a VVER-1200 of about 1,265 MWe gross in the St. Petersburg V-491 design family. It is being built by Russia''s Rosatom alongside the existing Paks station. The unit is under construction.', 'OKB Gidropress; World Nuclear News; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-528', 'The VVER V-528 is the reactor plant of Bushehr unit 2 in Iran, a Generation III+ VVER-1000 of about 974 MWe net supplied by Russia''s Atomstroyexport. It continues the Bushehr programme that began with the Russian-completed unit 1. The unit is under construction.', 'World Nuclear News; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER V-529', 'The VVER V-529 is the reactor plant of Egypt''s El Dabaa units 1-4, a VVER-1200 of about 1,200 MWe gross supplied by Russia''s Atomstroyexport. It is the reactor for Egypt''s first nuclear power station, on the Mediterranean coast. All four units are under construction.', 'World Nuclear News; NucNet; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER-210 (V-1)', 'The VVER-210 (project V-1) was the first VVER reactor, built as Novovoronezh unit 1 in Russia and generating from 1964 to 1984. Rated about 210 MWe (197 MWe net), it was the prototype that launched the Soviet pressurized-water reactor line. Its operating experience fed directly into the larger VVER-365 that followed at the same site.', 'IAEA PRIS; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('model', 'VVER-365 (V-3M)', 'The VVER-365 (project V-3M) was the second VVER reactor, built as Novovoronezh unit 2 in Russia and operating from 1969 to 1990. Rated about 365 MWe (336 MWe net), it was an enlarged development of the pioneering VVER-210 and a further step toward the standardized VVER-440 series.', 'IAEA PRIS; World Nuclear Association', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('plant', 'Cape Nagloynyn', 'Cape Nagloynyn is a Russian small modular reactor project on the Arctic coast of Chukotka, built to power the remote Baimskaya copper-and-gold mining district. It uses RITM-200S reactors - two per floating power unit of about 55 MWe each - moored near Pevek, with electricity carried inland by transmission line. Operated by Rosatom''s Rosenergoatom, the first units are under construction with staged commissioning planned through the late 2020s and early 2030s.', 'World Nuclear News; Global Energy Monitor; Rosatom', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('plant', 'Darlington SMR', 'The Darlington SMR is Ontario Power Generation''s small modular reactor project at the Darlington site in Clarington, Ontario, on the shore of Lake Ontario. Its first unit, a GE Hitachi BWRX-300 of about 300 MWe, began construction in 2025 - the first grid-scale SMR under construction in a G7 country - with up to four units planned. It is a new build adjacent to OPG''s existing Darlington CANDU station.', 'Ontario Power Generation; CNSC; World Nuclear News', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('plant', 'Shidaowan', 'Shidaowan is a nuclear power station at Shidao Bay in Rongcheng, Shandong, China, where a pair of Hualong One (HPR1000) pressurized water reactors of about 1,200 MWe gross each are under construction. It shares the coastal site with two other distinct programmes - the HTR-PM high-temperature pebble-bed demonstrator and the CAP1400 ''Guohe One'' units - but this entry covers the HPR1000 phase specifically. Construction of the first HPR1000 unit began in 2024.', 'World Nuclear News; NucNet; CNNC', CURRENT_TIMESTAMP);

INSERT INTO entity_descriptions (entity_type, entity_name, description, source, updated_at)
VALUES ('plant', 'Windscale AGR', 'The Windscale AGR (WAGR) was the United Kingdom''s prototype Advanced Gas-cooled Reactor, a small (about 32-36 MWe) graphite-moderated, carbon-dioxide-cooled unit operated by the UKAEA at the Windscale (Sellafield) site in Cumbria from 1963 to 1981. Housed under a distinctive spherical containment known as the ''golf ball'', it proved out the AGR concept that Britain built into its commercial fleet at Hinkley Point B, Hunterston B and later stations. It has since served as a demonstration project for reactor decommissioning.', 'World Nuclear News; IAEA INIS; UKAEA', CURRENT_TIMESTAMP);

-- VVER-1000/187 spec completion: V-187 prototype used 109 control assemblies (reduced to 61
--   in the serial V-320). Other NULL fields left NULL (not confidently V-187-specific).
UPDATE design_series_specs
SET number_of_control_elements = 109,
    source = 'IAEA PRIS, Wikipedia; V-187 control-assembly count (109, reduced to 61 in serial V-320) per MDEP/Gidropress VVER-1000 comparison; remaining fields pending sourced values'
WHERE design_series = 'VVER-1000/187';
