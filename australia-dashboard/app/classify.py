"""Routes every headline into one of the China v6 dashboard's 15 headings, applied to Australia, New Zealand, Papua New Guinea
and the Pacific islands. Order matters: the most specific headings come first; geopolitics is the default. Short words match
whole words only."""
import re

HEADINGS = ["geo", "milops", "arms", "naval", "scs", "air", "space", "tech", "cyber", "darkweb",
            "econ", "mss", "social", "wellbeing", "hazard"]

RULES = [
    ("darkweb", ["dark web", "darknet", "onion", "ransomware", "leak site", "infostealer", "stealer", "data breach",
                 "data leak", "threat intel", "threat intelligence", "initial access broker"]),
    ("cyber", ["cyber", "hacker", "hacked", "hacking", "malware", "vulnerabilit", "intrusion", "phishing", "ddos", "zero-day",
               "cyberattack", "volt typhoon", "salt typhoon", "apt40", "apt31", "signals intelligence", "sigint", "signals facility",
               "signals directorate", "asd", "gcsb", "wiper", "routers"]),
    ("hazard", ["earthquake", "tremor", "flood", "floods", "cyclone", "tropical cyclone", "bushfire", "tsunami", "volcan", "eruption",
                "heatwave", "heat wave", "drought", "wildfire", "landslide", "storm", "king tide", "sea level"]),
    ("milops", ["tpnpb", "insurgent", "insurgents", "rebels", "ambush", "militants", "militia", "hezbollah", "houthi", "hamas", "junta"]),
    ("mss", ["espionage", "spy", "spying", "sleeper cell", "informant", "crackdown", "arrested", "assassinat", "counterintelligence",
             "sabotage", "police raid", "organised crime", "money laundering"]),
    ("naval", ["navy", "naval", "submarine", "submarines", "warship", "frigate", "corvette", "destroyer", "fleet", "collins-class",
               "ssn-aukus", "aukus", "stirling", "lombrum", "shipyard", "shipbuilding", "hmas", "hmnzs", "virginia-class",
               "sea trial", "aircraft carrier", "patrol boat", "coast guard"]),
    ("scs", ["torres strait", "bass strait", "cook strait", "lombok", "sunda", "makassar", "strait", "straits", "shipping", "tanker",
             "undersea cable", "subsea cable", "cable fault", "vessel", "sea lane", "chokepoint", "vitiaz", "blockade"]),
    ("air", ["raaf", "rnzaf", "air force", "airbase", "air base", "fighter", "f-35", "f/a-18", "super hornet", "bomber", "b-52",
             "b-2", "b-1", "tanker aircraft", "airlift", "poseidon", "p-8", "triton", "uav", "airspace", "helicopter", "interceptor"]),
    ("arms", ["nuclear", "reactor", "uranium", "enrich", "plutonium", "radioactive", "radioactive waste", "warhead", "icbm", "ballistic",
              "hypersonic", "missile test", "missile", "minuteman", "trident", "opal", "ammunition", "arms deal", "arms sale",
              "weapons shipment", "test launch"]),
    ("space", ["space", "satellite", "orbital", "launch complex", "spaceport", "rocket launch", "electron", "koonibba", "arnhem space",
               "mahia", "māhia", "tidbinbilla", "re-entry", "cosmodrome", "space force", "deep space"]),
    ("milops", ["troops", "soldiers", "soldier", "army", "military exercise", "exercise pitch black", "talisman sabre", "rimpac",
                "deploy", "deployment", "marines", "marine rotational", "garrison", "offensive", "clashes", "clash", "shelling"]),
    ("tech", [" ai ", "artificial intelligence", "semiconductor", "quantum", "digital", "technology", "export control"]),
    ("geo", ["treaty", "agreement", "pact", "summit", "talks", "negotiat", "diplomat", "independence", "sovereignty", "aukus pillar",
             "security deal", "ceasefire", "peace", "referendum", "parliament", "forum", "pacific islands forum"]),
    ("econ", ["lng", "gas", "pipeline", "oil", "crude", "iron ore", "coal", "export", "exports", "trade", "tariff", "investment",
              "economy", "economic", "energy", "budget", "fuel", "prices", "mining investment", "resources", "gold"]),
    ("social", ["protest", "protests", "protesters", "refugee", "refugees", "asylum", "displaced", "displacement", "traditional owners",
                "indigenous", "barngarla", "migrants", "unrest", "riot", "riots", "civilians", "casualties", "famine", "students"]),
    ("wellbeing", ["happiness", "wellbeing", "well-being", "life expectancy", "human development index"]),
]

_SHORT = {"spy", "asd", "gcsb", "lng", "gas", "oil", "uav", "rnzaf", "raaf", "opal", "sigint", "f-35", "b-52", "b-2", "b-1",
          "p-8", "hmas", "hmnzs", "coal", "gold", "fuel", "trade", "uranium", "icbm", "satellite"}


def _has(text: str, word: str) -> bool:
    if " " in word or "-" in word or "'" in word or "." in word or "/" in word or "ā" in word:
        return word in text
    if word in _SHORT or (len(word) <= 4 and word.isalpha()):
        return re.search(r"\b" + re.escape(word) + r"\b", text) is not None
    return word in text


def classify(text: str) -> str:
    t = " " + (text or "").lower() + " "
    for heading, words in RULES:
        if any(_has(t, w) for w in words):
            return heading
    return "geo"
