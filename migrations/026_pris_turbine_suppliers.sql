-- 026_pris_turbine_suppliers.sql
-- Date: 2026-10-13
-- Description: Audit batch E: turbine supplier from PRIS where ours is blank (mostly values hidden
--   since July for lack of a source). Manufacturers only, mapped to house names; export agencies,
--   utilities and design institutes skipped. Whitelisted in verification_2026-07/final_verdicts.psv
--   (rows from audit/whitelist_026.psv) in the same change, per validator check 15.
-- Source: IAEA PRIS API (pris-stats.iaea.org), pulled 2026-10-13. Rows: 475.

BEGIN TRANSACTION;
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 1;  -- Atucha 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 2;  -- Atucha 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 19;  -- Angra 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 20;  -- Angra 2
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 28;  -- Bruce 1
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 29;  -- Bruce 2
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 30;  -- Bruce 3
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 31;  -- Bruce 4
UPDATE reactor_details SET turbine_supplier = 'GE Canada' WHERE reactor_id = 32;  -- Bruce 5
UPDATE reactor_details SET turbine_supplier = 'GE Canada' WHERE reactor_id = 33;  -- Bruce 6
UPDATE reactor_details SET turbine_supplier = 'GE Canada' WHERE reactor_id = 34;  -- Bruce 7
UPDATE reactor_details SET turbine_supplier = 'GE Canada' WHERE reactor_id = 35;  -- Bruce 8
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 36;  -- Darlington 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 37;  -- Darlington 2
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 38;  -- Darlington 3
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 39;  -- Darlington 4
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 43;  -- Pickering 1
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 44;  -- Pickering 2
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 45;  -- Pickering 3
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 46;  -- Pickering 4
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 47;  -- Pickering 5
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 49;  -- Pickering 7
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 50;  -- Pickering 8
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 51;  -- Point Lepreau 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 56;  -- Changjiang 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 57;  -- Changjiang 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 60;  -- Fangchenggang 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 61;  -- Fangchenggang 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 62;  -- Fangchenggang 3
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 63;  -- Fangchenggang 4
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 66;  -- Fuqing 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 67;  -- Fuqing 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 68;  -- Fuqing 3
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 69;  -- Fuqing 4
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 72;  -- Haiyang 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 73;  -- Haiyang 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 74;  -- Hongyanhe 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 75;  -- Hongyanhe 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 76;  -- Hongyanhe 3
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 77;  -- Hongyanhe 4
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 78;  -- Hongyanhe 5
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 79;  -- Hongyanhe 6
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 82;  -- Ling Ao 3
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 83;  -- Ling Ao 4
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 84;  -- Ningde 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 85;  -- Ningde 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 86;  -- Ningde 3
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 87;  -- Ningde 4
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 88;  -- Qinshan 1 1
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 89;  -- Qinshan 2 1
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 90;  -- Qinshan 2 2
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 91;  -- Qinshan 2 3
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 92;  -- Qinshan 2 4
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 93;  -- Qinshan 3 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 94;  -- Qinshan 3 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 97;  -- Shidao Bay 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 98;  -- Taipingling 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 106;  -- Tianwan 5
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 107;  -- Tianwan 6
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 108;  -- Yangjiang 1
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 109;  -- Yangjiang 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 110;  -- Yangjiang 3
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 111;  -- Yangjiang 4
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 112;  -- Yangjiang 5
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 113;  -- Yangjiang 6
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 114;  -- Zhangzhou 1
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 115;  -- Zhangzhou 2
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 124;  -- Olkiluoto 1
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 125;  -- Olkiluoto 2
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 126;  -- Olkiluoto 3
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 157;  -- Paluel 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 158;  -- Paluel 2
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 165;  -- St. Alban 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 166;  -- Paluel 3
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 168;  -- St. Alban 2
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 174;  -- Paluel 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 234;  -- Paks 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 235;  -- Paks 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 236;  -- Paks 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 237;  -- Paks 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 240;  -- Kaiga 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 241;  -- Kaiga 4
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 256;  -- Rajasthan 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 259;  -- Rajasthan 5
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 260;  -- Rajasthan 6
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 286;  -- Genkai 3
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 287;  -- Genkai 4
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 296;  -- Ikata 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 303;  -- Kashiwazaki Kariwa 6
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 307;  -- Mihama 3
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 311;  -- Ohi 3
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 312;  -- Ohi 4
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 315;  -- Onagawa 2
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 317;  -- Sendai 1
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 318;  -- Sendai 2
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 322;  -- Shimane 2
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 324;  -- Takahama 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 325;  -- Takahama 2
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 326;  -- Takahama 3
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 327;  -- Takahama 4
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 338;  -- Laguna Verde 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 339;  -- Laguna Verde 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 340;  -- Borssele 1
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 342;  -- Chashma 1
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 343;  -- Chashma 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 344;  -- Chashma 3
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 345;  -- Chashma 4
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 347;  -- Karachi 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 348;  -- Karachi 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 349;  -- Cernavodă 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 350;  -- Cernavodă 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 354;  -- Balakovo 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 355;  -- Balakovo 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 356;  -- Balakovo 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 357;  -- Balakovo 4
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 361;  -- Beloyarsk 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 367;  -- Kalinin 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 368;  -- Kalinin 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 370;  -- Kalinin 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 371;  -- Kola 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 372;  -- Kola 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 373;  -- Kola 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 374;  -- Kola 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 375;  -- Kursk 1 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 376;  -- Kursk 1 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 377;  -- Kursk 1 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 378;  -- Kursk 1 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 381;  -- Leningrad 1 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 382;  -- Leningrad 1 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 383;  -- Leningrad 1 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 384;  -- Leningrad 1 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 387;  -- Novovoronezh 1 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 388;  -- Novovoronezh 1 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 389;  -- Novovoronezh 1 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 390;  -- Novovoronezh 1 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 391;  -- Novovoronezh 1 5
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 394;  -- Rostov 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 398;  -- Smolensk 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 399;  -- Smolensk 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 400;  -- Smolensk 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 410;  -- Krško 1
UPDATE reactor_details SET turbine_supplier = 'Alsthom' WHERE reactor_id = 411;  -- Koeberg 1
UPDATE reactor_details SET turbine_supplier = 'Alsthom' WHERE reactor_id = 412;  -- Koeberg 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 413;  -- Hanbit (Yonggwang) 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 414;  -- Hanbit (Yonggwang) 2
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 419;  -- Hanul (Ulchin) 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 420;  -- Hanul (Ulchin) 2
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 425;  -- Kori 1
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 426;  -- Kori 2
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 427;  -- Kori 3
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 428;  -- Kori 4
UPDATE reactor_details SET turbine_supplier = 'Doosan Heavy Industries / General Electric' WHERE reactor_id = 440;  -- Wolsong 2
UPDATE reactor_details SET turbine_supplier = 'Doosan Heavy Industries / General Electric' WHERE reactor_id = 441;  -- Wolsong 3
UPDATE reactor_details SET turbine_supplier = 'Doosan Heavy Industries / General Electric' WHERE reactor_id = 442;  -- Wolsong 4
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 443;  -- Almaraz 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 444;  -- Almaraz 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 445;  -- Asco 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 446;  -- Asco 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 450;  -- Trillo 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 452;  -- Vandellos 2
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 456;  -- Forsmark 1
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 458;  -- Forsmark 3
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 461;  -- Oskarshamn 3
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 464;  -- Ringhals 3
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 465;  -- Ringhals 4
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 468;  -- Gösgen 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 469;  -- Leibstadt 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 502;  -- Dungeness B 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 503;  -- Dungeness B 2
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 508;  -- Heysham B 1
UPDATE reactor_details SET turbine_supplier = 'NEI Parsons' WHERE reactor_id = 509;  -- Heysham B 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 518;  -- Hunterston B 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 519;  -- Hunterston B 2
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 537;  -- Khmelnytskyi 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 538;  -- Khmelnytskyi 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 541;  -- Rivne 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 542;  -- Rivne 2
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 543;  -- Rivne 3
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 544;  -- Rivne 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 545;  -- South Ukraine 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 546;  -- South Ukraine 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 548;  -- Zaporizhzhia 1
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 549;  -- Zaporizhzhia 2
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 550;  -- Zaporizhzhia 3
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 551;  -- Zaporizhzhia 4
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 552;  -- Zaporizhzhia 5
UPDATE reactor_details SET turbine_supplier = 'Turboatom' WHERE reactor_id = 553;  -- Zaporizhzhia 6
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 556;  -- Beaver Valley 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 557;  -- Beaver Valley 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 560;  -- Braidwood 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 561;  -- Braidwood 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 562;  -- Browns Ferry 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 563;  -- Browns Ferry 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 564;  -- Browns Ferry 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 565;  -- Brunswick 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 566;  -- Brunswick 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 567;  -- Byron 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 568;  -- Byron 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 569;  -- Callaway 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 570;  -- Calvert Cliffs 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 571;  -- Calvert Cliffs 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 572;  -- Catawba 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 573;  -- Catawba 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 574;  -- Clinton 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 575;  -- Columbia 1
UPDATE reactor_details SET turbine_supplier = 'Allis-Chalmers' WHERE reactor_id = 576;  -- Comanche Peak 1
UPDATE reactor_details SET turbine_supplier = 'Allis-Chalmers' WHERE reactor_id = 577;  -- Comanche Peak 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 578;  -- Cook (Donald C. Cook) 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 579;  -- Cook (Donald C. Cook) 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 580;  -- Cooper 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 583;  -- Davis Besse 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 584;  -- Diablo Canyon 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 585;  -- Diablo Canyon 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 587;  -- Dresden 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 588;  -- Dresden 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 591;  -- Farley (Joseph M. Farley) 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 592;  -- Farley (Joseph M. Farley) 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 599;  -- Ginna (R. E. Ginna) 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 600;  -- Grand Gulf 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 603;  -- Harris (Shearon Harris) 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 604;  -- Hatch (Edwin I. Hatch) 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 605;  -- Hatch (Edwin I. Hatch) 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 606;  -- Hope Creek 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 613;  -- LaSalle 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 614;  -- LaSalle 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 615;  -- Limerick 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 616;  -- Limerick 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 618;  -- McGuire 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 619;  -- McGuire 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 621;  -- Millstone 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 622;  -- Millstone 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 623;  -- Monticello 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 624;  -- Nine Mile Point 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 625;  -- Nine Mile Point 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 626;  -- North Anna 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 627;  -- North Anna 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 628;  -- Oconee 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 629;  -- Oconee 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 630;  -- Oconee 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 638;  -- Peach Bottom 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 639;  -- Peach Bottom 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 640;  -- Perry 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 643;  -- Point Beach 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 644;  -- Point Beach 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 645;  -- Prairie Island 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 646;  -- Prairie Island 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 647;  -- Quad Cities 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 648;  -- Quad Cities 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 650;  -- River Bend 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 651;  -- Robinson (H B Robinson) 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 652;  -- Salem 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 653;  -- Salem 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 658;  -- Seabrook 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 659;  -- Sequoyah 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 660;  -- Sequoyah 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 663;  -- South Texas Project 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 664;  -- South Texas Project 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 665;  -- St Lucie 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 666;  -- St Lucie 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 667;  -- Summer (V C Summer) 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 670;  -- Susquehanna 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 671;  -- Susquehanna 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 675;  -- Turkey Point 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 676;  -- Turkey Point 4
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 678;  -- Vogtle 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 679;  -- Vogtle 2
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 680;  -- Vogtle 3
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 681;  -- Vogtle 4
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 682;  -- Waterford 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 683;  -- Watts Bar 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 684;  -- Watts Bar 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 685;  -- Wolf Creek 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 7;  -- Rooppur 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 8;  -- Rooppur 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 11;  -- BR-3 1
UPDATE reactor_details SET turbine_supplier = 'Cockerill-Tosi' WHERE reactor_id = 12;  -- Doel 1
UPDATE reactor_details SET turbine_supplier = 'Cockerill-Tosi' WHERE reactor_id = 13;  -- Doel 2
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 17;  -- Tihange 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 21;  -- Angra 3
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 40;  -- Douglas Point 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 42;  -- Gentilly 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 54;  -- CFR 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 55;  -- CFR 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 99;  -- Taipingling 2
UPDATE reactor_details SET turbine_supplier = 'SACM' WHERE reactor_id = 127;  -- G2 2
UPDATE reactor_details SET turbine_supplier = 'Rateau' WHERE reactor_id = 128;  -- G3 3
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 129;  -- Chinon A (EDF1) 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 130;  -- Chinon A (EDF2) 2
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 131;  -- Chinon A (EDF3) 3
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 132;  -- Chooz-A 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 133;  -- Brennilis 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 138;  -- St. Laurent A 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 139;  -- Bugey 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 190;  -- St. Laurent A 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 199;  -- Emsland 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 201;  -- Neckarwestheim 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 202;  -- Brokdorf 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 203;  -- Grohnde 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 205;  -- Philippsburg 2
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 206;  -- Grafenrheinfeld 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 207;  -- Biblis A
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 208;  -- Biblis B
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 209;  -- Brunsbüttel 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 211;  -- Krümmel 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 212;  -- Neckarwestheim 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 213;  -- Philippsburg 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 214;  -- Unterweser 1
UPDATE reactor_details SET turbine_supplier = 'KWU' WHERE reactor_id = 216;  -- Stade 1
UPDATE reactor_details SET turbine_supplier = 'AEG' WHERE reactor_id = 217;  -- Würgassen 1
UPDATE reactor_details SET turbine_supplier = 'AEG' WHERE reactor_id = 218;  -- KNK II 1
UPDATE reactor_details SET turbine_supplier = 'Bergmann-Borsig' WHERE reactor_id = 220;  -- Rheinsberg 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 225;  -- AVR Jülich 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 226;  -- THTR-300 1
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 227;  -- Mülheim-Kärlich 1
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 229;  -- MZFR 1
UPDATE reactor_details SET turbine_supplier = 'AEG' WHERE reactor_id = 230;  -- Gundremmingen A
UPDATE reactor_details SET turbine_supplier = 'AEG' WHERE reactor_id = 231;  -- Lingen 1
UPDATE reactor_details SET turbine_supplier = 'Siemens' WHERE reactor_id = 232;  -- Niederaichbach 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 233;  -- HDR Großwelzheim 1
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 255;  -- Rajasthan 1
UPDATE reactor_details SET turbine_supplier = 'Franco Tosi' WHERE reactor_id = 270;  -- Enrico Fermi 1
UPDATE reactor_details SET turbine_supplier = 'Ansaldo' WHERE reactor_id = 271;  -- Garigliano 1
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 273;  -- Fugen ATR 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 274;  -- Fukushima-Daiichi 1
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 276;  -- Fukushima-Daiichi 3
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 277;  -- Fukushima-Daiichi 4
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 278;  -- Fukushima-Daiichi 5
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 279;  -- Fukushima-Daiichi 6
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 280;  -- Fukushima-Daini 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 281;  -- Fukushima-Daini 2
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 282;  -- Fukushima-Daini 3
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 283;  -- Fukushima-Daini 4
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 284;  -- Genkai 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 285;  -- Genkai 2
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 288;  -- Hamaoka 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 289;  -- Hamaoka 2
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 290;  -- Hamaoka 3
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 291;  -- Hamaoka 4
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 292;  -- Hamaoka 5
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 293;  -- Higashi Dori 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 294;  -- Ikata 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 295;  -- Ikata 2
UPDATE reactor_details SET turbine_supplier = 'General Electric / Toshiba' WHERE reactor_id = 297;  -- JPDR 1
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 298;  -- Kashiwazaki Kariwa 1
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 299;  -- Kashiwazaki Kariwa 2
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 300;  -- Kashiwazaki Kariwa 3
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 301;  -- Kashiwazaki Kariwa 4
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 302;  -- Kashiwazaki Kariwa 5
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 304;  -- Kashiwazaki Kariwa 7
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 305;  -- Mihama 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 306;  -- Mihama 2
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 308;  -- Monju 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 309;  -- Ohi 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 310;  -- Ohi 2
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 313;  -- Ohma 1
UPDATE reactor_details SET turbine_supplier = 'Toshiba' WHERE reactor_id = 314;  -- Onagawa 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 316;  -- Onagawa 3
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 319;  -- Shika 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 320;  -- Shika 2
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 321;  -- Shimane 1
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 323;  -- Shimane 3
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 328;  -- Tokai 1
UPDATE reactor_details SET turbine_supplier = 'General Electric / Hitachi' WHERE reactor_id = 329;  -- Tokai 2
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 330;  -- Tomari 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 331;  -- Tomari 2
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 332;  -- Tomari 3
UPDATE reactor_details SET turbine_supplier = 'General Electric / Toshiba' WHERE reactor_id = 333;  -- Tsuruga 1
UPDATE reactor_details SET turbine_supplier = 'Mitsubishi Heavy Industries' WHERE reactor_id = 334;  -- Tsuruga 2
UPDATE reactor_details SET turbine_supplier = 'Hitachi' WHERE reactor_id = 346;  -- Karachi 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 359;  -- Beloyarsk 1
UPDATE reactor_details SET turbine_supplier = 'Power Machines (LMZ)' WHERE reactor_id = 360;  -- Beloyarsk 2
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 448;  -- Jose Cabrera 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 449;  -- Santa María de Garoña 1
UPDATE reactor_details SET turbine_supplier = 'Alstom' WHERE reactor_id = 451;  -- Vandellos 1
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 459;  -- Oskarshamn 1
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 460;  -- Oskarshamn 2
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 463;  -- Ringhals 2
UPDATE reactor_details SET turbine_supplier = 'Brown Boveri (BBC)' WHERE reactor_id = 470;  -- Lucens 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 478;  -- Maanshan (Third) 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 479;  -- Maanshan (Third) 2
UPDATE reactor_details SET turbine_supplier = 'AEI' WHERE reactor_id = 486;  -- Berkeley 1
UPDATE reactor_details SET turbine_supplier = 'AEI' WHERE reactor_id = 487;  -- Berkeley 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 488;  -- Bradwell 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 489;  -- Bradwell 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 490;  -- Calder Hall 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 491;  -- Calder Hall 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 492;  -- Calder Hall 3
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 493;  -- Calder Hall 4
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 494;  -- Chapelcross 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 495;  -- Chapelcross 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 496;  -- Chapelcross 3
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 497;  -- Chapelcross 4
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 498;  -- Dounreay DFR 1
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 499;  -- Dounreay PFR 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 500;  -- Dungeness A 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 501;  -- Dungeness A 2
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 510;  -- Hinkley Point A 1
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 511;  -- Hinkley Point A 2
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 522;  -- Sizewell A 1
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 523;  -- Sizewell A 2
UPDATE reactor_details SET turbine_supplier = 'Richardsons Westgarth' WHERE reactor_id = 527;  -- Trawsfynydd 1
UPDATE reactor_details SET turbine_supplier = 'Richardsons Westgarth' WHERE reactor_id = 528;  -- Trawsfynydd 2
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 529;  -- Windscale AGR 1
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 530;  -- Winfrith 1
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 531;  -- Wylfa 1
UPDATE reactor_details SET turbine_supplier = 'English Electric' WHERE reactor_id = 532;  -- Wylfa 2
UPDATE reactor_details SET turbine_supplier = 'Skoda' WHERE reactor_id = 539;  -- Khmelnytskyi 3
UPDATE reactor_details SET turbine_supplier = 'Skoda' WHERE reactor_id = 540;  -- Khmelnytskyi 4
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 559;  -- Bonus 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 581;  -- Crystal River 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 582;  -- CVTR 1
UPDATE reactor_details SET turbine_supplier = 'Allis-Chalmers' WHERE reactor_id = 590;  -- Elk River 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 593;  -- Fermi 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 596;  -- Fort Calhoun 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 598;  -- GE Vallecitos 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 601;  -- Haddam Neck (Connecticut Yankee) 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 602;  -- Hallam 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 607;  -- Humboldt Bay 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 609;  -- Indian Point 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 610;  -- Indian Point 3
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 611;  -- Kewaunee 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 631;  -- Oyster Creek 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 632;  -- Palisades 1
UPDATE reactor_details SET turbine_supplier = 'Allis-Chalmers' WHERE reactor_id = 636;  -- Pathfinder 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 641;  -- Pilgrim 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 642;  -- Piqua 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 649;  -- Rancho Seco 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 654;  -- San Onofre 1
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 655;  -- San Onofre 2
UPDATE reactor_details SET turbine_supplier = 'GEC' WHERE reactor_id = 656;  -- San Onofre 3
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 657;  -- Saxton 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 662;  -- Shoreham 1
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 672;  -- Three Mile Island 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 673;  -- Three Mile Island 2
UPDATE reactor_details SET turbine_supplier = 'General Electric' WHERE reactor_id = 677;  -- Vermont Yankee 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 686;  -- Yankee NPS 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 687;  -- Zion 1
UPDATE reactor_details SET turbine_supplier = 'Westinghouse' WHERE reactor_id = 688;  -- Zion 2
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 689;  -- Changjiang 3
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 690;  -- Changjiang 4
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 691;  -- Linglong 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 692;  -- Sanao 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 693;  -- Sanao 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 694;  -- Sanao 3
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 695;  -- Haiyang 3
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 696;  -- Haiyang 4
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 697;  -- Sanmen 3
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 698;  -- Sanmen 4
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 699;  -- Lufeng 1
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 700;  -- Lufeng 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 701;  -- Lufeng 5
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 702;  -- Lufeng 6
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 703;  -- Xudabao 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 704;  -- Xudabao 2
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 705;  -- Xudabao 3
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 706;  -- Xudabao 4
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 707;  -- Tianwan 7
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 708;  -- Tianwan 8
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 709;  -- Zhangzhou 3
UPDATE reactor_details SET turbine_supplier = 'Shanghai Electric' WHERE reactor_id = 710;  -- Zhangzhou 4
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 712;  -- Lianjiang 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 713;  -- Ningde 5
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 715;  -- Jinqimen 1
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 716;  -- Bailong 1
UPDATE reactor_details SET turbine_supplier = 'Harbin Electric' WHERE reactor_id = 717;  -- Taipingling 3
UPDATE reactor_details SET turbine_supplier = 'Arabelle Solutions' WHERE reactor_id = 729;  -- Paks 5
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 731;  -- Shidaowan 1
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 732;  -- Shidaowan 2
UPDATE reactor_details SET turbine_supplier = 'Dongfang Electric' WHERE reactor_id = 733;  -- Ningde 6
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 734;  -- Kaiga 5
UPDATE reactor_details SET turbine_supplier = 'Alstom-BHEL' WHERE reactor_id = 735;  -- Kaiga 6
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 454;  -- Barsebäck 1
UPDATE reactor_details SET turbine_supplier = 'Stal-Laval' WHERE reactor_id = 455;  -- Barsebäck 2
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 520;  -- Oldbury 1
UPDATE reactor_details SET turbine_supplier = 'C. A. Parsons' WHERE reactor_id = 521;  -- Oldbury 2
COMMIT;
