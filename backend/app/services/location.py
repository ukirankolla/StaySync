"""Location helpers for recommendation fallback (India-focused, best-effort).

When an exact city/area search has no users, we broaden to nearby cities in
the same state so the discovery feed never dead-ends. Cities not in this map
fall back to a global search instead.

Both cities AND common localities/areas are mapped, so searching something
like "Marathahalli" (a Bengaluru locality) still broadens to Karnataka users.
"""

INDIA_STATES: dict[str, list[str]] = {
    "Andhra Pradesh": ["visakhapatnam", "vijayawada", "guntur", "tirupati", "ongole", "nellore", "kakinada", "rajahmundry"],
    "Telangana": ["hyderabad", "warangal", "karimnagar", "nizamabad"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "tiruchirappalli", "salem", "vellore"],
    "Karnataka": ["bengaluru", "mysuru", "hubli", "mangaluru", "belagavi"],
    "Maharashtra": ["mumbai", "pune", "nagpur", "nashik", "thane", "navi mumbai"],
    "Delhi NCR": ["new delhi", "delhi", "dwarka", "rohini", "gurgaon", "noida", "ghaziabad", "faridabad"],
    "Uttar Pradesh": ["lucknow", "kanpur", "varanasi", "prayagraj", "agra"],
    "Haryana": ["gurgaon", "faridabad", "panipat"],
    "West Bengal": ["kolkata", "howrah"],
    "Gujarat": ["ahmedabad", "surat", "vadodara", "rajkot"],
    "Rajasthan": ["jaipur", "jodhpur", "udaipur", "kota"],
    "Kerala": ["kochi", "thiruvananthapuram", "kozhikode"],
    "Punjab": ["chandigarh", "amritsar", "ludhiana"],
    "Madhya Pradesh": ["indore", "bhopal", "gwalior"],
    "Bihar": ["patna", "gaya"],
    "Odisha": ["bhubaneswar", "cuttack"],
    "Assam": ["guwahati"],
    "Jharkhand": ["ranchi", "jamshedpur"],
    "Goa": ["panaji", "margao"],
    "Chhattisgarh": ["raipur", "bilaspur"],
}

# Common localities/areas mapped to their state, so locality searches still
# broaden to nearby cities. Keys are lowercased with spaces removed.
LOCALITY_STATE: dict[str, str] = {
    # Bengaluru
    "marathahalli": "Karnataka", "marathali": "Karnataka", "koramangala": "Karnataka",
    "hsr": "Karnataka", "hsrlayout": "Karnataka", "indiranagar": "Karnataka",
    "whitefield": "Karnataka", "jayanagar": "Karnataka", "btmlayout": "Karnataka",
    "electroniccity": "Karnataka", "bellandur": "Karnataka", "hebbal": "Karnataka",
    "jpnagar": "Karnataka", "banashankari": "Karnataka", "malleshwaram": "Karnataka",
    "basavanagudi": "Karnataka", "rajajinagar": "Karnataka", "yeshwanthpur": "Karnataka",
    "sarakki": "Karnataka", "kengeri": "Karnataka", "ulsoor": "Karnataka",
    # Hyderabad
    "gachibowli": "Telangana", "madhapur": "Telangana", "hitec": "Telangana",
    "hiteccity": "Telangana", "kondapur": "Telangana", "kukatpally": "Telangana",
    "jubileehills": "Telangana", "banjarahills": "Telangana", "begumpet": "Telangana",
    "secunderabad": "Telangana", "miyapur": "Telangana", "mehdipatnam": "Telangana",
    "uppal": "Telangana", "ameerpet": "Telangana", "madhapur": "Telangana",
    # Chennai
    "adyar": "Tamil Nadu", "annanagar": "Tamil Nadu", "velachery": "Tamil Nadu",
    "tngar": "Tamil Nadu", "thoraipakkam": "Tamil Nadu", "omr": "Tamil Nadu",
    "guindy": "Tamil Nadu", "nungambakkam": "Tamil Nadu", "egmore": "Tamil Nadu",
    "porur": "Tamil Nadu", "madipakkam": "Tamil Nadu", "tambaram": "Tamil Nadu",
    "chromepet": "Tamil Nadu", "perungudi": "Tamil Nadu", "sholinganallur": "Tamil Nadu",
    # Mumbai
    "andheri": "Maharashtra", "bandra": "Maharashtra", "powai": "Maharashtra",
    "borivali": "Maharashtra", "goregaon": "Maharashtra", "malad": "Maharashtra",
    "dadar": "Maharashtra", "chembur": "Maharashtra", "worli": "Maharashtra",
    "lowerparel": "Maharashtra", "kandivali": "Maharashtra", "juhu": "Maharashtra",
    # Pune
    "kothrud": "Maharashtra", "hinjewadi": "Maharashtra", "hadapsar": "Maharashtra",
    "baner": "Maharashtra", "aundh": "Maharashtra", "vimanagar": "Maharashtra",
    "kharadi": "Maharashtra", "magarpatta": "Maharashtra", "wakad": "Maharashtra",
    "pimple": "Maharashtra", "bavdhan": "Maharashtra", "camp": "Maharashtra",
    # Delhi NCR
    "dwarka": "Delhi NCR", "rohini": "Delhi NCR", "saket": "Delhi NCR",
    "karolbagh": "Delhi NCR", "lajpatnagar": "Delhi NCR", "pitampura": "Delhi NCR",
    "vasantkunj": "Delhi NCR", "laxminagar": "Delhi NCR", "southdelhi": "Delhi NCR",
    "noida": "Delhi NCR", "gurgaon": "Delhi NCR", "ghaziabad": "Delhi NCR",
    # Kolkata
    "saltlake": "West Bengal", "sectorv": "West Bengal", "newtown": "West Bengal",
    "kankurgachi": "West Bengal", "dumdum": "West Bengal", "behala": "West Bengal",
    # Ahmedabad
    "bopal": "Gujarat", "satellite": "Gujarat", "prahladnagar": "Gujarat",
    "vastrapur": "Gujarat", "bodakdev": "Gujarat",
    # Jaipur
    "vaishalinagar": "Rajasthan", "malviyanagar": "Rajasthan", "mansarovar": "Rajasthan",
    "cscheme": "Rajasthan",
    # Kochi
    "kakkanad": "Kerala", "edappally": "Kerala", "aluva": "Kerala", "ernakulam": "Kerala",
    # Lucknow
    "gomtinagar": "Uttar Pradesh", "hazratganj": "Uttar Pradesh", "aliganj": "Uttar Pradesh",
    # Indore
    "vijaynagar": "Madhya Pradesh", "schemeb": "Madhya Pradesh", "schemec": "Madhya Pradesh",
    # Visakhapatnam
    "mvpcolony": "Andhra Pradesh", "gajuwaka": "Andhra Pradesh", "akkayyapalem": "Andhra Pradesh",
    # Vijayawada
    "governorpet": "Andhra Pradesh", "benzcircle": "Andhra Pradesh", "patamata": "Andhra Pradesh",
    # Bhubaneswar
    "saheednagar": "Odisha", "patia": "Odisha", "kalinganagar": "Odisha", "jaydevvihar": "Odisha",
    # Guwahati
    "beltola": "Assam", "ulubari": "Assam", "zooroad": "Assam",
    # Bhopal
    "areracolony": "Madhya Pradesh", "mpnagar": "Madhya Pradesh", "kolarroad": "Madhya Pradesh",
    # Chandigarh
    "sector17": "Punjab", "sector22": "Punjab", "sector35": "Punjab",
}


def _norm(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalnum())


def nearby_cities(term: str) -> tuple[list[str], str] | None:
    """Return (nearby_cities, state_label) to broaden to, or None if unknown.

    - Known state name -> all cities in that state.
    - Known city -> other cities in the same state.
    - Known locality/area -> cities in its state.
    - Anything else -> None (caller should fall back globally).
    """
    t = _norm(term)
    if not t:
        return None

    if t in LOCALITY_STATE:
        state = LOCALITY_STATE[t]
        return INDIA_STATES[state], state

    for state, cities in INDIA_STATES.items():
        if t == _norm(state) or (len(t) >= 4 and t in _norm(state)):
            return cities, state

    for state, cities in INDIA_STATES.items():
        for city in cities:
            if t == _norm(city) or (len(t) >= 4 and t in _norm(city)):
                return cities, state

    # Prefix/substring match against known localities for fuzzy input like
    # "marathali" -> "marathahalli".
    for locality, state in LOCALITY_STATE.items():
        if len(t) >= 6 and (locality.startswith(t) or t in locality or locality in t):
            return INDIA_STATES[state], state

    return None
