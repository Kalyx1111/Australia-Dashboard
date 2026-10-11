# AUSTRALIA DASHBOARD - v1

Covers Australia (including its external territories), New Zealand (with the Cook Islands, Niue and Tokelau), Papua New Guinea, the
Pacific islands (Solomon Islands, Vanuatu, New Caledonia, Fiji, Samoa, Tonga, Tuvalu, Nauru, Kiribati, the Marshall Islands,
Micronesia, Palau, Guam, the Northern Marianas, American Samoa, Wallis and Futuna), Timor-Leste and the Indonesian islands inside the
frame. It uses the China Dashboard v6 architecture: Flask with waitress, a supervisor with automatic restart, AES-256-GCM key storage,
the same 15 headings (the maritime heading is "Maritime Chokepoints & Sea Lanes"), layer toggles and live connectors.

**India is outside this frame and nothing about India is plotted.** Its towns, airports, ports, rivers and outlines are not in the data.
The Indian Ocean appears only as the name of a sea in the notes.

## Start

Windows: double-click `start.bat`. The dashboard runs at **http://127.0.0.1:8830/** (set in `run.py` and `start.bat`). The first pass of the
news connectors takes a few minutes, because GDELT is paced at six seconds per query. The page is large (several MB) because it carries
589 points, each with its source.

## The 15 headings

Geopolitical & Diplomatic - Military Operations & Force Posture - Strategic Arms & Nuclear Program - Naval & Maritime Security -
Maritime Chokepoints & Sea Lanes - Air Force & Aviation - Space Tech & Aerospace - Critical Tech & AI Governance - Cyber Espionage &
APTs - Darkweb & Threat Intel - Economic & Trade - Internal Security & Intelligence Operations - Social Pulse & Public Sentiment -
Happiness & Wellbeing Indices - Natural Hazards & Environmental Risks.

Routing is rule-based (`app/classify.py`). A protest about a mine goes to the social heading; a cyclone that hits LNG plants goes to natural
hazards; a subsea cable fault goes to the chokepoints heading.

## The map

- **Projection:** Lambert azimuthal equal-area, centred on 150 degrees east and 25 degrees south. The frame runs from 105 to 202 degrees east
  (so the Pacific is drawn across the date line and Samoa, Tonga, Niue and the Cook Islands join the region) and from 55 degrees south to 16
  degrees north.
- **Outlines:** every outline is projected with the same formula as the points, so the shapes and the points always agree.
- **Shaded:** Australia, New Zealand, Papua New Guinea, the Pacific states and the Indonesian islands. **Outlined:** the neighbouring countries,
  the Spratly Islands and Scarborough Reef (claimed by several states).
- **State, region and province lines:** 82 boundary lines for Australia, New Zealand, Papua New Guinea and Indonesia.
- **Rivers:** 113 segments from Natural Earth.
- **Towns and capitals:** 53 places (200,000 or more people, and capitals) in the region.
- **Civil airports:** 351 large and medium airports from OurAirports (public domain, CC0).
- **Military-named airfields:** 41, chosen by name. A name is a clue, not a confirmation of use; the perimeter is not published.
- **Seaports:** 96 Natural Earth port points.
- **Sea labels:** the Coral, Tasman, Timor, Arafura, Java, Banda, Solomon and Celebes seas, the Gulf of Carpentaria, the Great Australian
  Bight, the Philippine Sea, the Southern Ocean and the Pacific Ocean.

## What is plotted: 101 points, each with its status, date and source

Each tooltip gives the source. "Not verified in this build" marks public knowledge that this build's searches did not confirm
(22 of the points carry that flag). 12 points for Indonesia and Timor-Leste are reused from the South-East Asia build,
where they were verified. Positions are approximate unless the note says otherwise.

- **Submarine and naval bases:** HMAS Stirling on Garden Island near Perth (Fleet Base West; six Collins-class submarines; AUKUS rotations from
  2027; US Naval Support Activity Stirling set up on 30 May 2026); the Henderson and Osborne AUKUS shipbuilding sites; Surabaya (Indonesia's 2nd
  Fleet and submarine base; reused); Lombrum on Manus Island (PNG; Australian-funded upgrade and US access); the Fleet Base East at Sydney (partly
  verified); and HMNZS Devonport and the French forces at Nouméa, flagged.
- **Air bases (12 sites with the military airfields):** RAAF Tindal (F-35A; US B-52H bombers arrived on 1 September 2026),
  Amberley, Williamtown, Pearce and Edinburgh; the Indonesian air bases reused from the South-East Asia build; and the RNZAF's Whenuapai and
  Ohakea, flagged.
- **Allied and joint bases (5 sites):** the Pine Gap joint facility near Alice Springs (operated with the US; protests on 20 July
  2026); the Harold E. Holt communications station at North West Cape; US Marines at Darwin; Andersen Air Force Base on Guam (the US bomber hub in
  the Western Pacific); and Naval Base Guam, flagged.
- **Missile and test ranges:** the RAAF Woomera Range Complex (about 122,000 km²) and the Ronald Reagan Space and Missile Test Range on
  Kwajalein Atoll (renamed in 2026).
- **Space:** Koonibba Test Range (Australia's first Launch Facility Licence), the Arnhem Space Centre near Nhulunbuy, Rocket Lab's Māhia site (last
  launch 11 September 2026); the Abbot Point spaceport and the Tidbinbilla deep-space station are flagged.
- **Cyber and signals:** the Shoal Bay receiving station (Darwin), the Kojarena satellite station, the Joint Geological and Geophysical Research
  Station (Alice Springs), and the ASD, GCSB and Waihopai sites, flagged.
- **Nuclear (10 sites):** the OPAL research reactor and HIFAR (Lucas Heights; HIFAR being decommissioned); the waste stores at
  Lucas Heights; the proposed national waste facility at Napandee (halted by a court ruling); the Olympic Dam, Beverley and Four Mile uranium
  mines (operating) and the Ranger mine (closed); and the British test sites at Maralinga and Monte Bello (flagged). **Australia and New Zealand have
  no nuclear power reactors, and nuclear power generation is currently illegal in Australia. No power plants are plotted in the region.**
- **Defence industry (3 sites):** the Henderson Defence Precinct and Osborne (SSN-AUKUS); PT PAL at Surabaya (reused).
- **Chokepoints (7):** the Torres Strait (between Queensland and PNG), the Bass Strait, and the Lombok, Sunda and Makassar straits
  (reused); the Cook Strait and the Vitiaz Strait are flagged.
- **Pipelines, LNG and subsea cables (12):** Gorgon LNG (Barrow Island; 15.6 MTPA; cyclone outage in 2026 reported), North West
  Shelf and Pluto at Karratha, Wheatstone, Ichthys and Darwin LNG, the Curtis Island plants at Gladstone, the Dampier to Bunbury gas pipeline, PNG LNG
  at Hides (over 450 km of onshore pipeline), Tangguh in West Papua (reused in part), the Moomba gas pipeline (flagged) and the Perth cable faults of
  8 to 9 August 2026 (reported).
- **Capitals (27):** the capitals and territorial capitals of the region, including the Cook Islands, Niue, Norfolk Island and Christmas
  Island; Jakarta and Dili are reused.
- **Command (3 sites):** the Australian Defence Headquarters, the NZDF headquarters and the Republic of Fiji Military Forces
  headquarters (all flagged as not verified).
- **Flashpoints (2):** the West Papua highlands (the TPNPB insurgency; more than 125,000 reported displaced) and Bougainville
  (the independence vote in PNG's Parliament, August 2026).

## Gaps (not verified in this build or not plotted)

- **Australian military structure:** most Army and Navy bases beyond those listed (for example the Army garrisons at Enoggera, Lavarack and
  Holsworthy, HMAS Cerberus and Jervis Bay), RAAF Learmonth and Curtin, and the Defence Cyber Command. The 41 military-named airfields from
  OurAirports are reference points only.
- **Nuclear:** the uranium mine positions are approximate, except Olympic Dam; Maralinga and Monte Bello are not verified.
- **Pacific security:** the status of the Australia-PNG defence treaty in 2026 was not verified; New Caledonia's political status and unrest were
  not verified; the PNG defence bases other than Lombrum are not plotted.
- **Indonesia:** only the Indonesian sites verified in the South-East Asia build are plotted here; its full detail is in that dashboard.
- **Space and pipelines:** Whalers Way, the Northern Gas Pipeline and most of the Pacific launch and cable infrastructure are not plotted.
- **News:** only seven verified global feeds are included. The regional press is reached through Google News search feeds, which are aggregators,
  so the outlets are not named by the feed. The USGS earthquake feed covers longitudes up to 180 degrees; the part of the Pacific east of 180 is
  not in it.

## News, social and dark-web sources

- **Verified feeds (7):** USNI News and the USNI Blog, Breaking Defense, SpaceNews, Space.com, The Record and Al Jazeera.
- **Google News search feeds (12):** AUKUS and Australian defence, Pine Gap, New Zealand defence, PNG security, Pacific security, West Papua,
  Australian LNG, uranium and waste, Australian space launches, Australian cyber, Pacific cables and Guam.
- **GDELT:** 30 English-language queries covering the bases, the submarines, the ranges, the straits, the cables, the energy plants and the
  Pacific security arrangements.
- **USGS earthquakes:** events in the frame (Australia, New Zealand, PNG and the Pacific to 180 degrees).
- **Ransomware.live:** claims filtered to the region's country codes. Group claims are labelled unverified.
- **X (Twitter):** official API v2 recent search with 10 queries. Set `X_BEARER_TOKEN`. Recent search needs a paid tier.
- **Facebook and Instagram:** official Graph and Business Discovery APIs. Set your tokens and list your own pages or accounts.
- **Telegram:** `data/telegram_channels.json` carries the public list from the earlier build. It has not been verified for this region.
- **Dark web (Tor):** none configured. Add onion sources you have verified on the outlet's own site.

## Reference items

36 dated items, each with its source: AUKUS at HMAS Stirling and its enduring access; the Henderson and Osborne sites; the Collins-class
boats; the B-52 deployment to Tindal and the nuclear-weapons arrangement there; the Pine Gap debate; North West Cape; Lombrum; the Vanuatu
Nakamal Agreement; the China-Solomon Islands security agreement; the Australia-PNG treaty (status not verified); the Bougainville vote;
West Papua and Indonesia's military build-up; Woomera; Koonibba; Māhia; Arnhem; the Kwajalein range; OPAL; the uranium mines and the
Napandee waste facility; Gorgon and the LNG fleet; Cyclone Narelle; the Perth cable faults; the straits; Andersen; Exercise Pitch Black; New
Zealand's nuclear-free law (not verified); and Timor-Leste.

## Tests

36 Python tests (`python -m pytest tests/`) and three browser suites (`npm test`), which load the shipped page into a real DOM. The layer
test fails the build if any toggle has no data behind it. The outline and point alignment was checked by rendering the map.

## Security

- Keys and tokens are encrypted with AES-256-GCM and never appear in error messages.
- The server listens on 127.0.0.1 only.
- Strict Content-Security-Policy: no third-party scripts, fonts or trackers.
- Headlines and labels are escaped before display; only http and https links become clickable.
- Telegram handles, Instagram usernames and Facebook Page IDs are validated before any URL is built.
- Requests can go through a proxy you choose (`PROXY_URL`).

A dashboard cannot secure your whole PC or phone, and it cannot hide your IP address from the sites it fetches from unless you route
traffic through a VPN, which can still see your traffic.

## Honest limitations

- **Most positions are approximate.** Bases and industrial sites sit at their town or area centre; open sources do not publish perimeters.
  Each tooltip says so.
- **Some points are not verified in this build.** They are flagged in their tooltips and listed under Gaps.
- **Incidents and displacement figures are reported claims.** The notes say who reports them; the situations change.
- **Nuclear information is public status only.** Nothing gives holdings, security arrangements or targeting information; the US B-52
  arrangement is described as the public sources describe it.
- **Events change daily.** The sources are current to reports up to 10 October 2026. Check them before you rely on any event.
- **No live news was fetched in the build sandbox,** which has no internet access. The status panel on your machine shows the real results.
- **The map is not a targeting product.** It maps publicly reported locations and events for analysis.
- **Single-user and local.** It runs on your machine while it is open.
