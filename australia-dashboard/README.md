# AUSTRALIA DASHBOARD - v1.7

## What changed in v1.7

- Three screen controls sit in the map's top-right corner: **Full map**, **Full screen** and **Hide bars**.
- **Full map** hides the KPI strip, the map's header row, the news drawer and its tab, the heading panels below the map, the layers panel and the footer note, so the map fills the window below the title. Press **Show panels** to bring them back.
- **Full screen** hides the browser's tabs and address bar. A web page cannot start full screen by itself: the button or the F key needs a click or key press first. Whether the Windows taskbar hides was not tested on Windows; it can be set to auto-hide in Windows settings.
- **Hide bars** (3, 4 or 5 seconds, or never; default 4 seconds) fades the header controls, the KPI strip, the map's header row, the news tab, the map tools, the zoom control and the footer note after no mouse, touch, wheel or key use. The title stays. Moving the mouse brings everything back. The bars do not hide while a dialog is open or while you type in a field.
- Keys: **M** for Full map, **F** for Full screen.
- The Full map state and the hide delay are kept in this browser only. They hold no personal data and no keys.
- Tests: a browser suite for the controls (`tests/dom_layout_test.js`) and a Python test that the shipped page is exactly what `build_frontend.py` builds (`tests/test_layout_controls.py`).

## Upgrading from an earlier version

- Your API keys are kept in the folder `~/..australia_dashboard` in your user profile, so they carry over with no step.
- Plotted custom markers are saved in `data/custom_markers.json` inside the dashboard folder. Copy that file from the old folder into the new one to keep them.
- `data/cache.json` is rebuilt by the first poll after start, so nothing needs copying.

## What changed in v1.6

- India lies outside this map's area, so no India outline or highlight is drawn in this dashboard.
- Military sites inside India's survey outline are not plotted. Civil points (pipelines, ports, airports, power plants) and news about India are shown.
- Layers and the legend show only the categories that have data in this dashboard.

## Permanent data updates
- Update data (top bar) fetches the latest public data for this dashboard's layers now. The status line shows when data was last updated and when the next automatic update is due.
- Automatic: every 7 days while the dashboard is running (the first run starts about 2 minutes after launch). Change update_every_days in data/dashboard.json; 0 switches automatic updates off.
- Command line (for Windows Task Scheduler): python run.py --update-now runs one update and exits.
- Sources, fixed in app/updates.py (no other address is ever fetched): OurAirports airports (public domain); WRI Global Power Plant Database, nuclear plants (CC BY 4.0); UCDP georeferenced conflict events from the last 30 days (CC BY 4.0); OpenStreetMap military sites, ports and pipelines as points (ODbL, © OpenStreetMap contributors).
- Only layers this dashboard already shows are updated. Curated points are never overwritten; a new point within 2 km of a point in the same layer is skipped. Each point shows its source, licence, accuracy rating and fetch date.
- OpenStreetMap points are crowd-sourced (accuracy Medium): check them before relying on them. Pipelines and cables are shown as points here; their route lines are not updated automatically.
- If a source cannot be reached, its last good data stays and the error is shown in data/updates/status.json.
- Military sites inside India's outline are never added to a dashboard that is not in focus mode.

- Start (start.bat) creates a shortcut named "AUSTRALIA Dashboard" on the Desktop and in the Start menu each time it runs, then opens http://127.0.0.1:8830/ in the browser. To pin it to the taskbar, right-click the Desktop shortcut and choose Pin to taskbar (Windows does not let a script pin apps).

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
- **Ransomware.live:** claims filtered to the region's country codes. Shown as group claims, not confirmed victims.
- **X (Twitter):** official API v2 recent search with 10 queries. Set `X_BEARER_TOKEN`.
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

39 Python tests (`python -m pytest tests/`) and four browser suites (`npm test`), which load the shipped page into a real DOM. The layer
test fails the build if any toggle has no data behind it. The outline and point alignment was checked by rendering the map.

## Security

- Keys are encrypted with AES-256-GCM. The X and Facebook connectors remove their tokens from error messages.
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
