"""Fix the last 25 template plant descriptions with name-corrected keys."""
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = 'C:/Users/griff/nuclear-database/nuclear_reactors.db'

FIXES = {
    'Almaraz': "Spain's largest nuclear power station operates two Westinghouse three-loop PWRs in the remote Extremadura region. Commissioned in 1981 and 1983, Almaraz's 2074 MW of combined capacity has made it the single largest source of carbon-free electricity on the Iberian Peninsula for over four decades.",
    'Beznau': "With Unit 1 connected to the grid in 1969, Beznau holds the title of the oldest commercial nuclear power plant still operating anywhere in the world. The twin Westinghouse PWRs sit on a man-made island in the Aare River, their continued operation a subject of both pride and periodic controversy in Swiss energy politics.",
    'Biblis': "Once a flagship of Germany's civil nuclear program, Biblis housed two of the country's first large pressurized water reactors in Hesse. Unit A's 2011 shutdown in the wake of Fukushima became an iconic moment in Germany's abrupt nuclear reversal.",
    'Brokdorf': "Few nuclear plants anywhere provoked as fierce a public backlash as Brokdorf, where tens of thousands of demonstrators clashed with police during construction in the late 1970s and 1980s. The single PWR operated from 1986 until its closure at the end of 2021.",
    'Cofrentes': "Spain's sole boiling water reactor sits inland in the Valencia region, making it an outlier in a national fleet otherwise composed entirely of pressurized water reactors. The GE BWR/6, operational since 1984, generates over 1000 MW.",
    'Cook (Donald C. Cook)': "Overlooking the eastern shore of Lake Michigan near Bridgman, the Donald C. Cook Nuclear Plant is one of the few U.S. nuclear stations sited on a Great Lake. Its two Westinghouse four-loop PWRs produce 2,331 MW, operated by Indiana Michigan Power.",
    'Emsland': "Commissioned in 1988 in Lower Saxony, this Siemens/KWU PWR earned a reputation for reliable performance. Emsland was one of Germany's final three operating reactors, generating power until April 15, 2023 — the day the country exited nuclear energy entirely.",
    'Grafenrheinfeld': "This Bavarian PWR was the first German reactor permanently closed under the post-Fukushima nuclear phase-out, shutting down on June 27, 2015. Its decommissioning became a test case for dismantling large commercial reactors in a densely populated European country.",
    'Greifswald': "East Germany's sole nuclear power plant on the Baltic coast operated five Soviet VVER-440 units while three more were under construction. All reactors were shut down following reunification in 1990 when Western safety reviews deemed them unfit, making it Europe's largest nuclear decommissioning project.",
    'Grohnde': "Celebrated for consistently achieving some of the highest capacity factors of any reactor worldwide, Grohnde's single PWR on the Weser River was a model of operational excellence. Despite its stellar record, the plant closed at the end of 2021 under Germany's nuclear exit law.",
    'Gundremmingen': "Germany's largest nuclear complex in Bavaria operated three BWR units, though Unit A is remembered for its 1977 partial meltdown caused by operator error. Units B and C operated until 2017 and 2021 respectively before the phase-out claimed them.",
    'G\u00f6sgen': "A Siemens/KWU pressurized water reactor on the Aare River, G\u00f6sgen has been one of Switzerland's most reliable electricity sources since 1979, supplying roughly eight percent of the country's power from a single unit.",
    'Ikata': "Perched on a narrow peninsula jutting into the Seto Inland Sea from Shikoku island, Ikata has been reduced to a single operating reactor after two older units were shut down. Unit 3 earned distinction as one of the few Japanese reactors to clear post-Fukushima safety reviews.",
    'Leibstadt': "Switzerland's newest and most powerful reactor is a GE BWR/6 generating over 1275 MW since 1984 on the Rhine near the German border. As the only large BWR in the Swiss fleet, Leibstadt provides roughly 16 percent of Switzerland's nuclear output.",
    'Monju': "Japan's prototype fast breeder reactor in Tsuruga suffered a devastating sodium leak and fire in December 1995, just four months after reaching criticality. The scandal kept the plant shuttered for 15 years and led to its permanent closure in 2017, ending Japan's fast breeder ambitions.",
    'M\u00fchleberg': "A GE BWR/4 near Bern, M\u00fchleberg became the first Swiss reactor to permanently shut down in December 2019 under the country's gradual nuclear phase-out. The plant faced years of legal challenges from opponents who argued its Mark I containment posed risks to the nearby capital.",
    'Neckarwestheim': "Two PWRs of different vintages occupied this site: Unit 1 shut down in 2011, and Unit 2 survived as one of Germany's last three reactors until April 2023. Its final years were marked by debate over cracking found in steam generator tubes.",
    'Phenix': "France's first fast breeder reactor operated on the Rh\u00f4ne at Marcoule from 1973 as a 250 MWe prototype. After unexplained reactivity anomalies prompted a lengthy shutdown, it was restarted at reduced power in 2003 for transmutation research before final closure in 2009.",
    'Philippsburg': "A BWR and a PWR shared this site near Karlsruhe in Baden-W\u00fcrttemberg. The cooling tower demolition in 2020, broadcast live on German television, became one of the most powerful visual symbols of Germany's nuclear phase-out.",
    'South Ukraine': "Three VVER-1000 pressurized water reactors in Mykolaiv Oblast form one of Ukraine's four operating nuclear stations, contributing 3000 MW to a grid that depends on nuclear for over half its electricity. The plant's continued operation during the Russian invasion underscored the precarious intersection of nuclear infrastructure and armed conflict.",
    'Stade': "When this single PWR on the Elbe shut down in November 2003, it became one of the first German reactors to close under the original nuclear exit agreement, foreshadowing the wave of closures that would eliminate nuclear power from Germany two decades later.",
    'Super-Phenix': "At 1,240 MWe, Super-Ph\u00e9nix at Creys-Malville was the largest liquid-metal fast breeder reactor ever built. Chronic sodium leaks, political opposition, and enormous costs limited the plant to a fraction of its intended output before its 1997 shutdown.",
    'Trillo': "Commissioned in 1988 as the last nuclear reactor built in Spain, this Siemens/KWU PWR represents the endpoint of Spanish nuclear construction. The single 1066 MW unit has become a political lightning rod in Spain's energy transition debates.",
    'Unterweser': "A large PWR on the Weser River near Bremen, Unterweser was among the seven oldest German reactors immediately shut down by government order in March 2011, just days after Fukushima. The reactor never operated again.",
    'Zhangzhou': "The newest fleet of Hualong One reactors rises on the Fujian coast, with two units operational and two more under construction. Zhangzhou showcases China's rapid deployment capability for its flagship third-generation reactor design.",
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    for name, desc in FIXES.items():
        cur.execute(
            "UPDATE entity_descriptions SET description = ? WHERE entity_type = 'plant' AND entity_name = ?",
            (desc, name)
        )
        if cur.rowcount:
            updated += 1
        else:
            print(f"  NOT FOUND: {name}")

    print(f"Fixed {updated}/{len(FIXES)} remaining template descriptions")

    cur.execute("""SELECT COUNT(*) FROM entity_descriptions WHERE entity_type = 'plant'
        AND (description LIKE '%is a nuclear power station in%' OR description LIKE 'Located in%')""")
    print(f"Remaining template plant descriptions: {cur.fetchone()[0]}")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
