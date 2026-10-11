"""
Fixed reference points for the AUSTRALIA dashboard: Australia (including its external territories), New Zealand (with the
Cook Islands, Niue and Tokelau), Papua New Guinea, the Pacific islands (Solomon Islands, Vanuatu, New Caledonia, Fiji, Samoa,
Tonga, Tuvalu, Nauru, Kiribati, the Marshall Islands, Micronesia, Palau, Guam and the Northern Marianas, American Samoa, Wallis
and Futuna), Timor-Leste and the Indonesian islands inside the frame. Indonesian and Timor-Leste entries are reused from the
South-East Asia build, where they were verified.

Each point carries its status, date and source in `note` and `source`. Points marked "not verified in this build" come from
public knowledge that this build's searches did not confirm; they are shown, but treat them as unconfirmed. Positions for bases
are approximate. Reported incidents are claims; the notes say so. Nothing about India is plotted: India is outside the frame.
Nuclear material and weapons-test information is limited to public status. Nothing here is a targeting product.
"""
import json
import os


def M(id, name, lat, lon, cat, note, source, aliases=()):
    al = list(aliases) or [name.split(":")[0].split(" (")[0].strip().lower()]
    return {"id": id, "name": name, "lat": lat, "lon": lon, "cat": cat, "note": note, "source": source, "aliases": al}


MARKERS = [
    # ---------- Capitals and territorial capitals ----------
    M("cap_canberra", "Canberra (capital, Australia)", -35.2809, 149.1300, "capital", "Seat of government. Australian Defence Headquarters and the Australian Signals Directorate are in the Canberra area (public information).", "public information"),
    M("cap_darwin", "Darwin (capital, Northern Territory)", -12.4634, 130.8456, "capital", "Territory capital. RAAF Base Darwin and the US Marine Rotational Force-Darwin are here (Wikipedia; Naval News, Aug 2026).", "Wikipedia (Exercise Pitch Black); Naval News (Aug 2026)"),
    M("cap_hobart", "Hobart (capital, Tasmania)", -42.8821, 147.3272, "capital", "State capital of Tasmania (public information).", "public information"),
    M("cap_wellington", "Wellington (capital, New Zealand)", -41.2865, 174.7762, "capital", "Seat of government. The New Zealand Defence Force and the GCSB are headquartered here (public information).", "public information"),
    M("cap_port_moresby", "Port Moresby (capital, Papua New Guinea)", -9.4438, 147.1803, "capital", "Capital; the Papua New Guinea Defence Force headquarters is here (public information).", "public information"),
    M("cap_honiara", "Honiara (capital, Solomon Islands)", -9.4456, 159.9729, "capital", "Capital. The 2022 China-Solomon Islands security agreement concerns this government (see reference items).", "Georgetown GJIA (2022); Pantheon Insights (2025)"),
    M("cap_port_vila", "Port Vila (capital, Vanuatu)", -17.7333, 168.3273, "capital", "Capital. The Nakamal Agreement with Australia was signed in Canberra on 29 June 2026 (AAP).", "AAP via Islands Business (30 Jun 2026)"),
    M("cap_suva", "Suva (capital, Fiji)", -18.1416, 178.4419, "capital", "Capital. The Republic of Fiji Military Forces headquarters is in Suva (public information).", "public information"),
    M("cap_noumea", "Nouméa (capital, New Caledonia; France)", -22.2758, 166.4580, "capital", "Capital of New Caledonia, a French territory. French armed forces are based here (public information).", "public information"),
    M("cap_apia", "Apia (capital, Samoa)", -13.8333, 188.2667, "capital", "Capital of Samoa.", "public information"),
    M("cap_nukualofa", "Nuku'alofa (capital, Tonga)", -21.1333, 184.8000, "capital", "Capital of Tonga.", "public information"),
    M("cap_funafuti", "Funafuti (capital, Tuvalu)", -8.5211, 179.1963, "capital", "Capital of Tuvalu, a low-lying atoll state (public information).", "public information"),
    M("cap_yaren", "Yaren (de facto capital, Nauru)", -0.5477, 166.9209, "capital", "De facto capital of Nauru, which has no formal capital.", "public information"),
    M("cap_tarawa", "South Tarawa (capital, Kiribati)", 1.3278, 172.9784, "capital", "Capital of Kiribati.", "public information"),
    M("cap_majuro", "Majuro (capital, Marshall Islands)", 7.1164, 171.1858, "capital", "Capital. The Ronald Reagan test range on Kwajalein Atoll is in the same republic (see missile ranges).", "public information"),
    M("cap_palikir", "Palikir (capital, Federated States of Micronesia)", 6.9248, 158.1610, "capital", "Capital of the Federated States of Micronesia.", "public information"),
    M("cap_ngerulmud", "Ngerulmud (capital, Palau)", 7.4961, 134.6249, "capital", "Capital of Palau, which has a Compact of Free Association with the United States.", "public information"),
    M("cap_hagatna", "Hagåtña (capital, Guam; US territory)", 13.4443, 144.7937, "capital", "Capital of Guam. Andersen Air Force Base and Naval Base Guam are on the island (see foreign bases).", "public information"),
    M("cap_saipan", "Saipan (capital, Northern Mariana Islands; US)", 15.1850, 145.7500, "capital", "Capital of the Northern Mariana Islands, a US Commonwealth.", "public information"),
    M("cap_pago_pago", "Pago Pago (capital, American Samoa; US)", -14.2756, 189.2980, "capital", "Capital of American Samoa, a US territory.", "public information"),
    M("cap_avarua", "Avarua (capital, Cook Islands; New Zealand)", -21.2078, 200.2250, "capital", "Capital of the Cook Islands, self-governing in free association with New Zealand.", "public information"),
    M("cap_alofi", "Alofi (capital, Niue; New Zealand)", -19.0544, 190.1323, "capital", "Capital of Niue, self-governing in free association with New Zealand.", "public information"),
    M("cap_mata_utu", "Mata-Utu (capital, Wallis and Futuna; France)", -13.2820, 183.8256, "capital", "Capital of Wallis and Futuna, a French territory.", "public information"),
    M("cap_kingston", "Kingston (Norfolk Island; Australian territory)", -29.0565, 167.9580, "capital", "Administrative centre of Norfolk Island, an Australian external territory.", "public information"),
    M("cap_flying_fish", "Flying Fish Cove (Christmas Island; Australian territory)", -10.4200, 105.6789, "capital", "Settlement on Christmas Island, an Australian external territory.", "public information"),

    # ---------- Allied and foreign bases, joint facilities ----------
    M("pine_gap", "Joint Defence Facility Pine Gap (Alice Springs, NT): US-Australian signals and satellite facility", -23.7985, 133.7370, "foreign_base",
      "Joint signals intelligence and satellite communications facility since 1966. About 700 military and civilian personnel (2019 count; Wikipedia). Operated by the Australian Signals Directorate with the US NSA, CIA and NRO (Wikipedia). Protests on 20 July 2026 (The Diplomat). Ministers say half the personnel are Australian; activists dispute this (Declassified Australia, Jul 2026). Position approximate.",
      "Wikipedia (Signals intelligence platforms; Mount Zeil); The Diplomat (Jul 2026); Declassified Australia (Jul 2026)",
      aliases=("pine gap", "jdfpg", "joint defence facility pine gap")),
    M("nw_cape", "Harold E. Holt Naval Communication Station (North West Cape, Exmouth, WA): US-Australian communications station", -21.8167, 114.1667, "foreign_base",
      "Operated mainly by the Royal Australian Navy with a significant US presence (Operation Military Kids, 2026; Wikipedia). Position approximate.",
      "Operation Military Kids (2026); Wikipedia (Naval Communication Station Harold E. Holt)",
      aliases=("north west cape", "harold e holt", "exmouth")),
    M("mrf_darwin", "RAAF Base Darwin (Darwin, NT): US Marine Rotational Force-Darwin", -12.4081, 130.8795, "foreign_base",
      "US Marines rotate through Darwin under the Marine Rotational Force-Darwin (Naval News, Aug 2026). RAAF Base Darwin and RAAF Base Tindal host Exercise Pitch Black (Wikipedia). Position approximate.",
      "Naval News (Aug 2026); Wikipedia (Exercise Pitch Black)", aliases=("raaf base darwin", "marine rotational force darwin")),
    M("andersen", "Andersen Air Force Base (Guam): America's bomber hub in the Western Pacific", 13.5840, 144.9300, "foreign_base",
      "Bomber hub in the Western Pacific (migflug, Sep 2026). Position approximate.", "migflug (Sep 2026)", aliases=("andersen", "andersen air force base")),
    M("guam_navy", "Naval Base Guam (Apra Harbor, Guam) (not verified in this build)", 13.4420, 144.6500, "foreign_base",
      "Public information: US Navy base on Apra Harbor. Not verified in this build.", "public information (not verified in this build)"),

    # ---------- Air bases ----------
    M("tindal", "RAAF Base Tindal (near Katherine, NT): F-35A squadron; US B-52H bomber deployments", -14.5219, 132.3780, "air_base",
      "B-52H bombers of the 2nd Bomb Wing (Barksdale) arrived on 1 Sep 2026 for Bomber Task Force 26-3 (Air & Space Forces; Army Recognition, Sep 2026). The A$1.1bn upgrade is US-funded (Wikipedia). No. 75 Squadron flies the F-35A; MQ-4C Triton operates here (Wikipedia). Position approximate.",
      "Air & Space Forces (Sep 2026); Army Recognition (Sep 2026); Wikipedia (RAAF Base Tindal)", aliases=("tindal", "raaf base tindal")),
    M("amberley", "RAAF Base Amberley (Queensland): 82 Wing headquarters; 1 and 6 Squadrons", -27.6344, 152.7108, "air_base",
      "Headquarters of 82 Wing; 1 and 6 Squadrons are based here (Air Combat Group, Wikipedia). US B-2 bombers deployed here in 2024 (Air & Space Forces). Position approximate.",
      "Wikipedia (Air Combat Group RAAF); Air & Space Forces (2024)", aliases=("amberley", "raaf base amberley")),
    M("williamtown", "RAAF Base Williamtown (NSW): F-35A 3 Squadron; 78 and 81 Wing headquarters", -32.7906, 151.8417, "air_base",
      "Home of 3 Squadron (F-35A) and the 2 Operational Conversion Unit; 78 and 81 Wing headquarters (Air Combat Group, Wikipedia). Position approximate.",
      "Wikipedia (Air Combat Group RAAF)", aliases=("williamtown", "raaf base williamtown")),
    M("pearce", "RAAF Base Pearce (WA): 79 Squadron", -31.6728, 116.0175, "air_base",
      "Home of 79 Squadron (Air Combat Group, Wikipedia). Position approximate.", "Wikipedia (Air Combat Group RAAF)", aliases=("pearce", "raaf base pearce")),
    M("edinburgh", "RAAF Base Edinburgh (Adelaide, SA): Air Warfare Centre headquarters", -34.7000, 138.6200, "air_base",
      "Headquarters of the Air Warfare Centre; it manages the Woomera Range Complex (Wikipedia). Position approximate.",
      "Wikipedia (RAAF Base Woomera)", aliases=("edinburgh", "raaf base edinburgh")),
    M("rnzaf_whenuapai", "RNZAF Base Auckland (Whenuapai, NZ) (not verified in this build)", -36.7876, 174.6244, "air_base",
      "Public information: principal air base of the RNZAF. Position approximate; not verified in this build.", "public information (not verified in this build)"),
    M("rnzaf_ohakea", "RNZAF Base Ohakea (Manawatu, NZ) (not verified in this build)", -40.2000, 175.3900, "air_base",
      "Public information: RNZAF base. Position approximate; not verified in this build.", "public information (not verified in this build)"),

    # ---------- Navy, fleet and submarine bases ----------
    M("hmas_stirling", "HMAS Stirling (Garden Island, WA): Fleet Base West and submarine base for AUKUS rotations", -32.2500, 115.6900, "submarine_base",
      "Home of the six Collins-class submarines and of the Anzac-class frigates. Submarine Rotational Force-West (one UK and up to four US nuclear-powered submarines) from 2027. US Naval Support Activity Stirling was established on 30 May 2026; enduring US access was confirmed in August 2026 (ASA; Defence Connect, Jun 2026; Army Recognition, Aug 2026). Position approximate.",
      "Australian Submarine Agency (SRF-West); Defence Connect (15 Jun 2026); MilitarySpot (8 Jun 2026); Army Recognition (9 Aug 2026)",
      aliases=("hmas stirling", "stirling submarine", "garden island", "fleet base west", "srf-west", "submarine rotational force")),
    M("fleet_base_east", "Fleet Base East (Garden Island, Sydney): Royal Australian Navy east-coast base", -33.8430, 151.2270, "navy_base",
      "East-coast fleet base in Sydney (Royal Australian Navy material, via a secondary summary; the position was not independently verified in this build).",
      "Royal Australian Navy (via secondary summary); partly verified in this build", aliases=("fleet base east", "garden island sydney")),
    M("coonawarra", "HMAS Coonawarra (Darwin, NT): Royal Australian Navy northern base (not verified in this build)", -12.4500, 130.8700, "navy_base",
      "Public information: Royal Australian Navy base in Darwin. Not verified in this build.", "public information (not verified in this build)"),
    M("lombrum", "Lombrum Naval Base (Manus Island, PNG): PNG Defence Force base with Australian-funded upgrade and US access", -2.0500, 147.2600, "navy_base",
      "Australian-funded upgrade (about A$500 million; PINA, Jun 2026). US access under the 2023 Defense Cooperation Agreement. PNG's prime minister says it is not a foreign base (PINA, 2 Jun 2026). Built by the US in 1944 (GlobalSecurity).",
      "PINA (2 Jun 2026); GlobalSecurity (Lombrum); Wikipedia (Lombrum Naval Base)", aliases=("lombrum", "lombrum naval base", "manus island")),
    M("nz_devonport", "HMNZS Devonport (Auckland, NZ): Royal New Zealand Navy base (not verified in this build)", -36.8330, 174.7960, "navy_base",
      "Public information: Royal New Zealand Navy base. Not verified in this build.", "public information (not verified in this build)"),
    M("fanc_noumea", "French Armed Forces in New Caledonia (FANC), Nouméa (not verified in this build)", -22.2600, 166.4400, "navy_base",
      "Public information: French forces in New Caledonia. Not verified in this build.", "public information (not verified in this build)"),

    # ---------- Missile and test ranges ----------
    M("woomera", "RAAF Woomera Range Complex (SA): Australian Defence Force test and evaluation range (about 122,000 km²)", -30.9731, 136.4756, "missile_base",
      "Test and evaluation range run by the RAAF for defence materiel; the Woomera Prohibited Area and its restricted airspace are controlled by the RAAF. Launch Area 5 hosted British rocket launches from 1958 to 1971 (Wikipedia). Coordinates are for Launch Area 5.",
      "Wikipedia (RAAF Woomera Range Complex; Woomera Launch Area 5)", aliases=("woomera", "woomera range complex", "woomera test range")),
    M("kwajalein", "Ronald Reagan Space and Missile Test Range (Kwajalein Atoll, Marshall Islands): US Army test range", 8.7200, 167.7300, "missile_base",
      "Renamed in 2026 from the Ronald Reagan Ballistic Missile Defense Test Site; run by the US Army Kwajalein Atoll (Wikipedia; DVIDS, Apr 2026). Minuteman III test launches from Vandenberg have flown to this range (Newsweek, navigational warnings, 2025).",
      "Wikipedia (Ronald Reagan Space and Missile Test Range); DVIDS (Apr 2026); Newsweek (2025)", aliases=("kwajalein", "reagan test", "ronald reagan space and missile test range")),

    # ---------- Space launch and tracking ----------
    M("koonibba", "Koonibba Test Range (SA; Southern Launch): sub-orbital and re-entry test range", -32.3667, 133.6500, "space_site",
      "Australia's first Launch Facility Licence (SpaceAustralia, 2021). The range covers up to 41,000 km². 2026 orbital re-entries W-5 and W-6, and a June 2026 mission for Defence Science and Technology Group (AeroVia, 2026). Position approximate.",
      "AeroVia (2026); SpaceAustralia (2021); Wikipedia (Koonibba Test Range)", aliases=("koonibba", "southern launch")),
    M("arnhem", "Arnhem Space Centre (Nhulunbuy, NT): commercial spaceport (Equatorial Launch Australia)", -12.2000, 136.7500, "space_site",
      "Operated by Equatorial Launch Australia. The first suborbital sounding rocket was launched from here; the operator's headquarters moved to Adelaide (Wikipedia, 2026). Position approximate.",
      "Wikipedia (Arnhem Space Centre; 2026)", aliases=("arnhem space centre", "equatorial launch australia")),
    M("mahia", "Rocket Lab Launch Complex 1 (Māhia Peninsula, NZ): private orbital spaceport", -39.2600, 177.8600, "space_site",
      "The world's first private orbital spaceport; more than 80 launches. The last launch was on 11 Sep 2026 (rocketlaunch.org, 2026). Kakushin Rising (JAXA) launched from here on 23 Apr 2026 (Rocket Lab).",
      "Rocket Lab (launch list, 2026); rocketlaunch.org (2026)", aliases=("mahia", "māhia", "rocket lab launch complex 1")),
    M("abbot_point", "Abbot Point spaceport (Queensland) (listed in 2026 launch sites; not verified in this build)", -19.9000, 148.0800, "space_site",
      "Listed among 2026 orbital launch sites (Gunter's Space Page). Not verified in this build; position approximate.", "Gunter's Space Page (2026 listing); not verified in this build"),
    M("tidbinbilla", "Canberra Deep Space Communication Complex (Tidbinbilla, ACT): NASA deep-space station (not verified in this build)", -35.4017, 148.9813, "space_site",
      "Public information: NASA's Australian deep-space tracking station. Not verified in this build.", "public information (not verified in this build)"),

    # ---------- Signals, cyber and monitoring ----------
    M("shoal_bay", "Defence Receiving Station Shoal Bay (Darwin, NT): Australian Signals Directorate satellite and HF intercept", -12.3200, 130.8600, "cyber_hub",
      "Controlled by the Australian Signals Directorate; satellite communications interception and HF signals (Wikipedia, Signals intelligence platforms by nation).",
      "Wikipedia (Signals intelligence operational platforms by nation)", aliases=("shoal bay",)),
    M("kojarena", "Australian Defence Satellite Communications Station (Kojarena, WA): satellite communications", -31.7600, 115.9000, "cyber_hub",
      "Part of the Defence satellite communications network near Kojarena (Wikipedia, Joint Geological and Geophysical Research Station). Position approximate.",
      "Wikipedia (Joint Geological and Geophysical Research Station)", aliases=("kojarena",)),
    M("jggrs", "Joint Geological and Geophysical Research Station (Alice Springs, NT): seismic monitoring, US and Australian", -23.7700, 133.7000, "cyber_hub",
      "Seismic monitoring station (USAF and Australian Defence). Its data are processed in Canberra and shared with seismologists and international agencies (Wikipedia). Position approximate.",
      "Wikipedia (Joint Geological and Geophysical Research Station)", aliases=("jggrs", "joint geological and geophysical research station")),
    M("asd_hq", "Australian Signals Directorate headquarters (Canberra) (not verified in this build)", -35.2950, 149.1450, "cyber_hub",
      "Public information: Australia's signals and cyber agency. Position approximate; not verified in this build.", "public information (not verified in this build)"),
    M("gcsb", "GCSB headquarters (Wellington, NZ) (not verified in this build)", -41.2930, 174.7800, "cyber_hub",
      "Public information: New Zealand's signals and cyber agency. Position approximate; not verified in this build.", "public information (not verified in this build)"),
    M("waihopai", "Waihopai signals station (Blenheim, NZ): historic intercept station; current status not verified in this build", -41.5360, 173.9180, "cyber_hub",
      "Historic GCSB satellite intercept station. Its current status was not verified in this build. Position approximate.", "public information (not verified in this build)"),

    # ---------- Command headquarters ----------
    M("adf_hq", "Australian Defence Headquarters (Russell, Canberra) (not verified in this build)", -35.3000, 149.1600, "cantonment",
      "Public information: Australia's defence headquarters. Position approximate; not verified in this build.", "public information (not verified in this build)"),
    M("nzdf_hq", "New Zealand Defence Force headquarters (Wellington) (not verified in this build)", -41.2880, 174.7800, "cantonment",
      "Public information: NZDF headquarters. Position approximate; not verified in this build.", "public information (not verified in this build)"),
    M("rfmf_hq", "Republic of Fiji Military Forces headquarters (Queen Elizabeth Barracks, Suva) (not verified in this build)", -18.1300, 178.4100, "cantonment",
      "Public information: the RFMF headquarters. Position approximate; not verified in this build.", "public information (not verified in this build)"),

    # ---------- Nuclear: research reactor, waste, uranium and test sites ----------
    M("opal", "OPAL multi-purpose research reactor (Lucas Heights, Sydney): ANSTO's 20 MW research reactor", -34.0500, 150.9900, "nuclear_site",
      "Australia's only nuclear reactor: a 20 MW research reactor using low-enriched uranium. It operated 98.3% of its scheduled time in 2025-26 (ANSTO). It produces radioisotopes and neutron beams and cannot produce electricity (ANSTO; Nuclear Engineering International).",
      "ANSTO (OPAL, 2026); Nuclear Engineering International (2025)", aliases=("opal", "lucas heights", "lucas heights reactor")),
    M("hifar", "HIFAR research reactor (Lucas Heights; 1958-2007): decommissioning under way", -34.0520, 150.9880, "nuclear_site",
      "Australia's first research reactor, operated 1958-2007 and now being decommissioned. Radiological waste is managed on site (ANSTO, 2026).",
      "ANSTO (2026)", aliases=("hifar",)),
    M("lucas_waste", "Lucas Heights waste stores (ANSTO): legacy and intermediate-level radioactive waste storage", -34.0530, 150.9940, "nuclear_site",
      "Most of Australia's radioactive waste is stored at Lucas Heights; the former MOATA reactor remains encased in concrete and steel (ABC News, Jul 2024; Conservation Council SA, 2022).",
      "ABC News (16 Jul 2024); Conservation Council SA (2022)", aliases=("lucas heights waste",)),
    M("napandee", "Napandee (near Kimba, SA): proposed National Radioactive Waste Management Facility (plan halted by court ruling)", -33.1400, 136.4300, "nuclear_site",
      "The 2020-21 site declaration was torn up after a Federal Court ruling in favour of the Barngarla traditional owners (ABC News, Jul 2024). Position approximate.",
      "ABC News (16 Jul 2024); Conservation Council SA (May 2022)", aliases=("napandee", "kimba")),
    M("olympic_dam", "Olympic Dam mine (Roxby Downs, SA): copper, gold and uranium (BHP)", -30.4400, 136.8900, "nuclear_site",
      "Underground mine with 261,000 tonnes of contained uranium oxide; about 20% of revenue comes from uranium (World Nuclear Association).",
      "World Nuclear Association (Australia's uranium mines)", aliases=("olympic dam",)),
    M("beverley", "Beverley uranium mine (SA; in-situ recovery) (approximate position)", -30.3300, 139.5600, "nuclear_site",
      "Operating uranium mine using in-situ recovery (World Nuclear Association). Position approximate.", "World Nuclear Association (Australia's uranium mines)", aliases=("beverley",)),
    M("four_mile", "Four Mile uranium mine (SA; in-situ recovery) (approximate position)", -29.9500, 139.9400, "nuclear_site",
      "Operating uranium mine using in-situ recovery (World Nuclear Association). Position approximate.", "World Nuclear Association (Australia's uranium mines)", aliases=("four mile",)),
    M("ranger", "Ranger uranium mine (Jabiru, NT): closed; rehabilitation under the closure plan", -12.6670, 132.9000, "nuclear_site",
      "Closed. Rehabilitation is planned over about seven years under the 2020 closure plan (World Nuclear Association).",
      "World Nuclear Association (Australia's uranium mines)", aliases=("ranger mine", "ranger uranium")),
    M("maralinga", "Maralinga and Emu Field (SA): British nuclear weapons test sites, 1956-1963 (not verified in this build)", -30.2100, 131.6800, "nuclear_site",
      "Public information: British atomic tests in the 1950s and 1960s; clean-up disputes continue. Not verified in this build.", "public information (not verified in this build)"),
    M("monte_bello", "Monte Bello Islands (WA): British atomic test site, 1952-1957 (not verified in this build)", -20.4200, 115.5500, "nuclear_site",
      "Public information: the first British atomic test (1952) was held here. Not verified in this build.", "public information (not verified in this build)"),

    # ---------- Defence industry (submarines and shipbuilding) ----------
    M("henderson", "Henderson Defence Precinct (Western Australia): AUKUS submarine and shipbuilding precinct", -32.1200, 115.7700, "defense_industry",
      "Site and boundary announced on 26 Aug 2026. It supports the sustainment pipeline for the submarine programme, about 10,000 jobs over two decades (Australian Submarine Agency, 26 Aug 2026).",
      "Australian Submarine Agency (26 Aug 2026)", aliases=("henderson", "henderson defence precinct")),
    M("osborne", "Osborne shipyard (Adelaide, SA): construction centre for SSN-AUKUS submarines", -34.7980, 138.1100, "defense_industry",
      "Will be the centre of construction for Australia's SSN-AUKUS nuclear-powered submarines (Australian Submarine Agency, 26 Aug 2026).",
      "Australian Submarine Agency (26 Aug 2026)", aliases=("osborne",)),

    # ---------- Chokepoints and sea routes ----------
    M("torres", "Torres Strait (Australia-PNG): sea route between the Coral Sea and the Arafura Sea", -10.3000, 142.3000, "chokepoint",
      "Between Queensland and Papua New Guinea. PNG determined the maritime border in the strait (Wikipedia). It connects the Coral Sea and the Arafura Sea (Anantam IAS, 2026). Position approximate.",
      "Wikipedia (Torres Strait); Anantam IAS (2026)", aliases=("torres strait",)),
    M("bass", "Bass Strait (Victoria-Tasmania): between mainland Australia and Tasmania", -39.6000, 146.3000, "chokepoint",
      "Connects the Tasman Sea and the Southern Ocean; separates mainland Australia from Tasmania (Anantam IAS, 2026). Position approximate.",
      "Anantam IAS (2026)", aliases=("bass strait",)),
    M("cook", "Cook Strait (New Zealand): between the North and South Islands (not verified in this build)", -41.2000, 174.3000, "chokepoint",
      "Public information: the strait that carries New Zealand's main undersea and ferry links between the islands. Not verified in this build.", "public information (not verified in this build)"),
    M("vitiaz", "Vitiaz Strait (Papua New Guinea): between New Guinea and New Britain (not verified in this build)", -5.6000, 148.2000, "chokepoint",
      "Public information: a PNG strait on a major sea route north of the Solomon Sea. Not verified in this build.", "public information (not verified in this build)"),

    # ---------- Pipelines, LNG and subsea cables ----------
    M("gorgon", "Gorgon LNG (Barrow Island, WA): 15.6 MTPA, three trains; domestic gas plant (300 TJ/d)", -20.8000, 115.4500, "pipeline",
      "Chevron-operated. Three LNG trains of 5.2 MTPA each; the first cargo left in March 2016; a 90 km domestic pipeline links the island to the mainland (Chevron; Wikipedia). Stage Three (Geryon and Eurytion fields) was expected to start production in 2026 (Offshore Technology). Position approximate.",
      "Chevron (fact sheet); Offshore Technology; Wikipedia (Gorgon gas project)", aliases=("gorgon", "barrow island")),
    M("nws", "North West Shelf LNG (Karratha, WA): 14.3 MTPA; one of five trains shut (Woodside, 2026)", -20.7300, 116.8500, "pipeline",
      "Australia's oldest LNG project. One of five production trains was shut after the March 2026 cyclone (Hydrocarbon Processing, Mar 2026). Position approximate.",
      "Hydrocarbon Processing (Mar 2026)", aliases=("north west shelf", "karratha lng")),
    M("pluto", "Pluto LNG (Karratha, WA; Woodside) (approximate position)", -20.6100, 116.7500, "pipeline",
      "Downtime at Pluto in 2026 lowered Woodside's production guidance (Hydrocarbon Processing, Mar 2026). Position approximate.",
      "Hydrocarbon Processing (Mar 2026)", aliases=("pluto lng",)),
    M("wheatstone", "Wheatstone LNG (Onslow, WA; Chevron) (approximate position)", -20.6500, 115.1200, "pipeline",
      "Outages in March 2026 were likely due to Tropical Cyclone Narelle (Hydrocarbon Processing, Mar 2026). Position approximate.",
      "Hydrocarbon Processing (Mar 2026)", aliases=("wheatstone",)),
    M("ichthys", "Ichthys LNG (offshore field off WA; onshore plant near Darwin, NT; Inpex)", -12.3500, 130.8500, "pipeline",
      "Two trains of 4.0 MTPA each, commissioned in 2018 (SEALA AI, 2026). Inpex reported no damage from the 2026 cyclone (Hydrocarbon Processing, Mar 2026). Position approximate.",
      "SEALA AI (2026); Hydrocarbon Processing (Mar 2026)", aliases=("ichthys",)),
    M("darwin_lng", "Darwin LNG (Wickham Point, NT; Santos): 3.7 MTPA; temporarily offline after the March 2026 cyclone", -12.4000, 130.8000, "pipeline",
      "A 3.7 MTPA plant that was offline temporarily after the March 2026 cyclone (Hydrocarbon Processing, Mar 2026). Position approximate.",
      "Hydrocarbon Processing (Mar 2026)", aliases=("darwin lng",)),
    M("curtis", "Curtis Island LNG (Gladstone, Queensland): Queensland Curtis, Australia Pacific and Gladstone LNG", -23.9000, 151.2000, "pipeline",
      "Coal-seam gas export plants on Curtis Island; part of Australia's ten-plant LNG fleet with 85.1 MTPA of capacity (SEALA AI, Feb 2026). Position approximate.",
      "SEALA AI (Feb 2026)", aliases=("curtis island", "gladstone lng")),
    M("dbngp", "Dampier to Bunbury Natural Gas Pipeline (Western Australia): main gas trunk line", -27.0000, 116.2000, "pipeline",
      "The domestic gas trunk line that the Gorgon domestic pipeline ties into (Offshore Technology; Chevron). Position approximate (route midpoint).",
      "Offshore Technology; Chevron", aliases=("dampier to bunbury", "dbngp")),
    M("png_lng", "PNG LNG (Hides, Southern Highlands, PNG): gas conditioning plant and over 450 km of onshore pipeline", -5.2500, 143.9000, "pipeline",
      "Hides gas field and gas conditioning plant, with over 450 km of onshore pipeline (Spiecapag, 2026). Position approximate.",
      "Spiecapag (2026)", aliases=("png lng", "hides")),
    M("tangguh", "Tangguh LNG (Bintuni Bay, West Papua, Indonesia): LNG expansion (approximate position)", -2.2500, 133.2000, "pipeline",
      "Expansion project on the southern shore of Bintuni Bay (Spiecapag, 2026). Position approximate.",
      "Spiecapag (2026)", aliases=("tangguh",)),
    M("moomba", "Moomba gas field and plant (SA) and gas pipeline to Sydney (not verified in this build)", -28.1000, 140.2000, "pipeline",
      "Public information: the Moomba-Sydney gas pipeline. Not verified in this build; position approximate.", "public information (not verified in this build)", aliases=("moomba",)),
    M("perth_cable", "Submarine cable protection zone off Perth: two cable faults on 8-9 August 2026 (reported)", -31.9000, 115.2000, "pipeline",
      "Two cables faulted one after the other on 8-9 August 2026; a vessel was reportedly seen nearby (SpecialEurasia, 11 Aug 2026). Reported; not confirmed in this build.",
      "SpecialEurasia (11 Aug 2026)", aliases=("perth cable", "subsea cable perth")),

    # ---------- Flashpoints and disputes (reported; the situation changes) ----------
    M("west_papua", "West Papua highlands (Puncak, Yahukimo): TPNPB insurgency; more than 125,000 reported displaced", -4.4800, 137.1200, "flashpoint",
      "Indonesian security forces are fighting the West Papua National Liberation Army (TPNPB). More than 125,000 people are reported displaced (Asia Pacific Report, 25 Sep 2026). The April 2025 Yahukimo attack killed 15 to 17 gold miners (Wikipedia; AP). Position approximate.",
      "Asia Pacific Report (25 Sep 2026); Wikipedia (Yahukimo massacre); AP (2025)", aliases=("west papua", "papua conflict", "tpnpb")),
    M("bougainville", "Bougainville (Buka and Arawa): independence vote; PNG Parliament ratification pending", -6.3000, 155.0000, "flashpoint",
      "97.7% of voters chose independence in the 2019 non-binding referendum. PNG Parliament debated ratification in August 2026; the autonomous government plans to declare independence in 2030 (Asia Pacific Report, 26 Aug 2026). Position approximate.",
      "Asia Pacific Report (26 Aug 2026); bne IntelliNews (2026)", aliases=("bougainville",)),
]

# Indonesian and Timor-Leste points reused from the South-East Asia build, where they were verified with sources.
_REUSED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sea_reused.json")
if os.path.exists(_REUSED):
    with open(_REUSED, encoding="utf-8") as _f:
        MARKERS.extend(json.load(_f))

for _m in MARKERS:
    if _m["id"] == "cap_jakarta":
        _m["aliases"] = ["jakarta"]
