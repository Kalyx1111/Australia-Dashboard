# Australia Dashboard

A locally hosted **OSINT and Geospatial Intelligence Platform** for monitoring Australia, New Zealand, Papua New Guinea, Timor-Leste, Indonesia and the wider Pacific region, with strategic military, maritime, aerospace, cyber, energy and geopolitical intelligence.

***

#### 🌏 Geographic Coverage

- **Primary focus:** Australia and its states and territories.
- **Regional coverage:** New Zealand, Papua New Guinea, Timor-Leste, selected Indonesian islands and Pacific island states.
- **Strategic geography:** Western Pacific, Pacific island chains, regional maritime routes and the approaches to Australia and New Zealand.
- **Map projection:** Lambert Azimuthal Equal-Area, designed for the Pacific region and islands crossing the 180° meridian.
- **Infrastructure:** 53 regional towns, 351 civil airports, 41 military-named airfields and 96 ports.
- **Strategic sites:** 101 sourced points, each with status, date and source information.
- **India exclusion:** India lies outside the map frame; no Indian territory or installations are plotted.

***

#### 🧭 15 Intelligence Categories

1. Geopolitical & Diplomatic
2. Military Operations & Force Posture
3. Strategic Arms & Nuclear Program
4. Maritime Chokepoints & Sea Lanes
5. Air Force & Aviation
6. Space Tech & Aerospace
7. Critical Tech & AI Governance
8. Cyber Espionage & APTs
9. Darkweb & Threat Intel
10. Economic & Trade
11. Internal Security & Intelligence Operations
12. Social Pulse & Public Sentiment
13. Happiness & Wellbeing Indices
14. Natural Hazards & Environmental Risks
15. Regional Strategic Developments

***

#### 🚢 Naval & Submarine Infrastructure

- **HMAS Stirling:** Fleet Base West and home of Australia's Collins-class submarines.
- **AUKUS:** Submarine rotational-force infrastructure and the Henderson and Osborne shipbuilding precincts.
- **Pacific security:** Lombrum naval facility on Manus Island and selected regional defence references.
- **Maritime geography:** Torres Strait, Bass Strait, Lombok Strait, Sunda Strait and Makassar Strait.
- **Regional naval monitoring:** Selected Indonesian and Timor-Leste sites reused from the Southeast Asia Dashboard.

***

#### ✈️ Air Bases & Allied Presence

- **Australian air bases:** RAAF Tindal, Amberley, Williamtown, Pearce, Darwin and Edinburgh.
- **Allied facilities:** Pine Gap, Andersen Air Force Base on Guam and selected communications facilities.
- **Signals infrastructure:** North West Cape, Shoal Bay and Kojarena.
- **New Zealand:** Regional aviation and strategic infrastructure references, with unverified entries labelled accordingly.

***

#### 🚀 Space & Test Ranges

- **Woomera Range Complex:** Australia's major defence test-range area.
- **Koonibba Test Range:** Launch and test-range reference near Ceduna.
- **Arnhem Space Centre:** Commercial space-launch infrastructure in the Northern Territory.
- **Rocket Lab Launch Complex 1:** Orbital launch facility on New Zealand's Māhia Peninsula.
- **Kwajalein range:** US missile-test and space-tracking infrastructure in the Marshall Islands.

***

#### ☢️ Nuclear & Strategic Materials

- **OPAL research reactor:** Australia's operating research reactor at Lucas Heights.
- **Uranium resources:** Olympic Dam, Ranger, Beverley and Four Mile.
- **Nuclear waste:** Lucas Heights waste-storage references and the proposed Napandee facility.
- **Nuclear power:** Australia has no operating nuclear power station; nuclear power generation is prohibited under current Australian law.
- **Verification:** Nuclear-related entries distinguish research facilities, uranium mines, waste infrastructure and other site types.

***

#### ⚡ Energy & Critical Infrastructure

- **LNG facilities:** Gorgon, North West Shelf, Ichthys, Darwin LNG, Wheatstone, Pluto and Curtis Island facilities.
- **Regional energy:** PNG LNG and selected gas infrastructure.
- **Maritime and communications:** Submarine-cable fault references and regional connectivity concerns.
- **Infrastructure monitoring:** Selected pipelines, ports and strategic energy facilities.

***

#### 📰 News & Intelligence Sources

- Configurable news and intelligence connectors.
- Keyword-based classification across 15 intelligence categories.
- Regional strategic, defence, maritime, energy and geopolitical monitoring.
- Reuses selected Indonesian and Timor-Leste references from the Southeast Asia Dashboard.

**Live-feed limitation:** External news retrieval could not be tested in the build environment because internet access was unavailable. The first news retrieval may take several minutes after launching the dashboard.

***

#### 🗺️ Map & Geospatial Features

- 37 countries and territories represented in the map frame.
- 24 countries and territories shaded according to the dashboard's regional configuration.
- 113 river segments and 82 state, regional and provincial boundary lines.
- 53 regional towns and capitals.
- 18 interactive layer toggles covering geographic and infrastructure layers.
- Consistent projection for country outlines, markers and geographic points.
- Pacific islands crossing the 180° meridian handled within a continuous map frame.

***

#### ⚙️ Installation & Launch

**Local dashboard URL:** http://127.0.0.1:8830

1. Extract `australia-dashboard-v1.zip`.
2. Open the extracted project folder.
3. Run `start.bat` on Windows or launch `run.py`.
4. Open `http://127.0.0.1:8830` in your browser.

***

#### 🧪 Testing

- 36 Python tests passed in a clean rebuild from the ZIP.
- Three browser test suites passed.
- Local server and page responses checked.
- All 15 intelligence categories populated.
- Geographic alignment, map layers and strategic-site placement checked.
- No server tracebacks reported during the live local check.

Live external news retrieval remains unverified in the offline build environment.

***

#### ⚠️ Known Limitations

- **Site verification:** 22 of the 101 strategic points are marked as not verified in this build.
- **Military coverage:** Several Australian and New Zealand Army and Navy facilities are missing or require further verification.
- **Regional agreements:** The current status of some Australia–Papua New Guinea defence arrangements and New Caledonia's political status was not verified in this build.
- **Regional conflict reporting:** West Papua displacement figures and Bougainville developments are reported claims, attributed in the relevant site notes.
- **Reused data:** Indonesian and Timor-Leste entries are drawn from the Southeast Asia Dashboard; consult that dashboard for additional regional detail.
- **External sources:** News-feed availability depends on internet access and third-party services.

***

#### 🔐 Responsible Use

This dashboard organizes publicly sourced information for research, strategic awareness and geospatial analysis. Verify source dates, claims and facility status independently. Approximate map positions should not be treated as exact facility boundaries, and reported incidents should not be interpreted as independently confirmed facts.

***
