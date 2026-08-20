"""Location helpers for recommendation fallback (India-focused, best-effort).

When an exact city/area search has no users, we broaden to nearby cities in
the same state so the discovery feed never dead-ends. Every Indian state,
city, and common locality is mapped so the app works nationwide.
"""

from .india_districts import INDIA_DISTRICTS, _DISTRICT_STATE
from .india_locations import INDIA_STATES, _CITY_STATE

# ── Localities / neighbourhoods → state ───────────────────────────────────────
# Common search terms that are NOT cities themselves. Normalised (lowercase,
# no spaces) for matching. Covers major metros across India.
LOCALITY_STATE: dict[str, str] = {
    # ── Bengaluru ─────────────────────────────────────────────────────────
    "marathahalli": "Karnataka", "marathali": "Karnataka", "koramangala": "Karnataka",
    "hsr": "Karnataka", "hsrlayout": "Karnataka", "indiranagar": "Karnataka",
    "whitefield": "Karnataka", "jayanagar": "Karnataka", "btmlayout": "Karnataka",
    "electroniccity": "Karnataka", "bellandur": "Karnataka", "hebbal": "Karnataka",
    "jpnagar": "Karnataka", "banashankari": "Karnataka", "malleshwaram": "Karnataka",
    "basavanagudi": "Karnataka", "rajajinagar": "Karnataka", "yeshwanthpur": "Karnataka",
    "sarakki": "Karnataka", "kengeri": "Karnataka", "ulsoor": "Karnataka",
    "sarjapur": "Karnataka", "kadubeesanahalli": "Karnataka",
    "kundalahalli": "Karnataka", "brookefield": "Karnataka", "mahadevapura": "Karnataka",
    "varthur": "Karnataka", "gunjur": "Karnataka", "halasuru": "Karnataka",
    "domlur": "Karnataka", "vimanapura": "Karnataka", "jalahalli": "Karnataka",
    "peenya": "Karnataka", "rajajinagar": "Karnataka", "nagasandra": "Karnataka",
    "yelahanka": "Karnataka", "anashtali": "Karnataka", "sahakarnagar": "Karnataka",
    "amruthahalli": "Karnataka", "jakkur": "Karnataka",
    # ── Hyderabad ─────────────────────────────────────────────────────────
    "gachibowli": "Telangana", "madhapur": "Telangana", "hitec": "Telangana",
    "hiteccity": "Telangana", "kondapur": "Telangana", "kukatpally": "Telangana",
    "jubileehills": "Telangana", "banjarahills": "Telangana", "begumpet": "Telangana",
    "secunderabad": "Telangana", "miyapur": "Telangana", "mehdipatnam": "Telangana",
    "uppal": "Telangana", "ameerpet": "Telangana", "dilsukhnagar": "Telangana",
    "LBnagar": "Telangana", "lbnagar": "Telangana", "nacharam": "Telangana",
    "musheerabad": "Telangana", "tarnaka": "Telangana", "chaderghat": "Telangana",
    "abids": "Telangana", "sultanbazar": "Telangana", "padmarao nagar": "Telangana",
    "trimulgherry": "Telangana", "cantonment": "Telangana",
    # ── Chennai ───────────────────────────────────────────────────────────
    "adyar": "Tamil Nadu", "annanagar": "Tamil Nadu", "velachery": "Tamil Nadu",
    "tngar": "Tamil Nadu", "thoraipakkam": "Tamil Nadu", "omr": "Tamil Nadu",
    "guindy": "Tamil Nadu", "nungambakkam": "Tamil Nadu", "egmore": "Tamil Nadu",
    "porur": "Tamil Nadu", "madipakkam": "Tamil Nadu", "tambaram": "Tamil Nadu",
    "chromepet": "Tamil Nadu", "perungudi": "Tamil Nadu", "sholinganallur": "Tamil Nadu",
    "adyar east": "Tamil Nadu", "adyar west": "Tamil Nadu",
    "nanganallur": "Tamil Nadu", "alandur": "Tamil Nadu",
    "nallambakkam": "Tamil Nadu", "thiruvanmiyur": "Tamil Nadu",
    "palavakkam": "Tamil Nadu", "injambakkam": "Tamil Nadu",
    "ecr": "Tamil Nadu", "nungambakkam": "Tamil Nadu",
    # ── Mumbai ────────────────────────────────────────────────────────────
    "andheri": "Maharashtra", "bandra": "Maharashtra", "powai": "Maharashtra",
    "borivali": "Maharashtra", "goregaon": "Maharashtra", "malad": "Maharashtra",
    "dadar": "Maharashtra", "chembur": "Maharashtra", "worli": "Maharashtra",
    "lowerparel": "Maharashtra", "kandivali": "Maharashtra", "juhu": "Maharashtra",
    "bhayandar": "Maharashtra", "mira road": "Maharashtra", "naigaon": "Maharashtra",
    "vasai": "Maharashtra", "virar": "Maharashtra", "nallasopara": "Maharashtra",
    "bhiwandi": "Maharashtra", "thane west": "Maharashtra", "thane east": "Maharashtra",
    "vashi": "Maharashtra", "nerul": "Maharashtra", "belapur": "Maharashtra",
    "airoli": "Maharashtra", "ghansoli": "Maharashtra", "kopar khairane": "Maharashtra",
    # ── Pune ──────────────────────────────────────────────────────────────
    "kothrud": "Maharashtra", "hinjewadi": "Maharashtra", "hadapsar": "Maharashtra",
    "baner": "Maharashtra", "aundh": "Maharashtra", "vimanagar": "Maharashtra",
    "kharadi": "Maharashtra", "magarpatta": "Maharashtra", "wakad": "Maharashtra",
    "pimple": "Maharashtra", "bavdhan": "Maharashtra", "camp": "Maharashtra",
    "shivajinagar": "Maharashtra", "deccan": "Maharashtra", "fc road": "Maharashtra",
    "sadashiv peth": "Maharashtra", "koregaon park": "Maharashtra",
    "kalyani nagar": "Maharashtra", "vishrantwadi": "Maharashtra",
    "dighi": "Maharashtra", "bhosari": "Maharashtra", "charholi": "Maharashtra",
    "talawade": "Maharashtra", "chakan": "Maharashtra",
    # ── Delhi NCR ─────────────────────────────────────────────────────────
    "dwarka": "Delhi", "rohini": "Delhi", "saket": "Delhi",
    "karolbagh": "Delhi", "karol bagh": "Delhi", "lajpatnagar": "Delhi",
    "lajpat nagar": "Delhi", "pitampura": "Delhi", "vasantkunj": "Delhi",
    "vasant kunj": "Delhi", "laxminagar": "Delhi", "laxmi nagar": "Delhi",
    "southdelhi": "Delhi", "noida": "Delhi NCR", "gurgaon": "Delhi NCR",
    "gurugram": "Delhi NCR", "ghaziabad": "Delhi NCR", "faridabad": "Delhi NCR",
    "greater noida": "Delhi NCR", "noida sector 62": "Delhi NCR",
    "noida sector 137": "Delhi NCR", "noida sector 51": "Delhi NCR",
    "connaught place": "Delhi", "cp": "Delhi", "nehru place": "Delhi",
    "okhla": "Delhi", "jangpura": "Delhi", "hauz khas": "Delhi",
    "defence colony": "Delhi", "malviya nagar": "Delhi",
    "kalkaji": "Delhi", "southern avenue": "Delhi",
    "moti nagar": "Delhi", "patel nagar": "Delhi", "rajouri garden": "Delhi",
    "punjabi bagh": "Delhi", "janakpuri": "Delhi", "tilak nagar": "Delhi",
    "kasturba nagar": "Delhi", "south ex": "Delhi", "north ex": "Delhi",
    "shakti nagar": "Delhi", "model town": "Delhi", "shalimar bagh": "Delhi",
    "mukherjee nagar": "Delhi", "gtb nagar": "Delhi", "vijay nagar": "Delhi",
    "noida sector 18": "Delhi NCR", "noida sector 62": "Delhi NCR",
    "greater noida west": "Delhi NCR", "ajnara": "Delhi NCR",
    "sahibabad": "Delhi NCR", "indirapuram": "Delhi NCR",
    "vaishali": "Delhi NCR", "kaushambi": "Delhi NCR",
    "vasundhara": "Delhi NCR", "crossings republik": "Delhi NCR",
    "dlf phase 1": "Delhi NCR", "dlf phase 2": "Delhi NCR",
    "dlf phase 3": "Delhi NCR", "dlf phase 4": "Delhi NCR",
    "dlf phase 5": "Delhi NCR", "sushant lok": "Delhi NCR",
    "sohna road": "Delhi NCR", "golf course road": "Delhi NCR",
    "mg road gurgaon": "Delhi NCR", "udyog vihar": "Delhi NCR",
    "sector 29 gurgaon": "Delhi NCR", "sector 45 gurgaon": "Delhi NCR",
    # ── Kolkata ───────────────────────────────────────────────────────────
    "saltlake": "West Bengal", "salt lake": "West Bengal", "sectorv": "West Bengal",
    "sector v": "West Bengal", "newtown": "West Bengal", "new town": "West Bengal",
    "kankurgachi": "West Bengal", "dumdum": "West Bengal", "behala": "West Bengal",
    "ballygunge": "West Bengal", "park street": "West Bengal",
    "elgin road": "West Bengal", "gariahat": "West Bengal",
    "south calcutta": "West Bengal", "north calcutta": "West Bengal",
    "burrabazar": "West Bengal", "chowringhee": "West Bengal",
    "alipore": "West Bengal", "ballygunge place": "West Bengal",
    # ── Ahmedabad ─────────────────────────────────────────────────────────
    "bopal": "Gujarat", "satellite": "Gujarat", "prahladnagar": "Gujarat",
    "vastrapur": "Gujarat", "bodakdev": "Gujarat", "thaltej": "Gujarat",
    "maninagar": "Gujarat", "ellis bridge": "Gujarat", "navrangpura": "Gujarat",
    "cg road": "Gujarat", "sg highway": "Gujarat", "science city": "Gujarat",
    "sola": "Gujarat", "ghatlodia": "Gujarat", "nikol": "Gujarat",
    "naroda": "Gujarat", "vastral": "Gujarat", "ranip": "Gujarat",
    "sarkhej": "Gujarat", "bavla": "Gujarat",
    # ── Jaipur ────────────────────────────────────────────────────────────
    "vaishalinagar": "Rajasthan", "vaishali nagar": "Rajasthan",
    "malviyanagar": "Rajasthan", "malviya nagar": "Rajasthan",
    "mansarovar": "Rajasthan", "cscheme": "Rajasthan",
    "c scheme": "Rajasthan", "jagatpura": "Rajasthan", "tonk road": "Rajasthan",
    "mi road": "Rajasthan", "bani park": "Rajasthan", "raja park": "Rajasthan",
    "lal kothi": "Rajasthan", "tilak nagar": "Rajasthan",
    "vidhyadhar nagar": "Rajasthan", "murlipura": "Rajasthan",
    # ── Kochi ─────────────────────────────────────────────────────────────
    "kakkanad": "Kerala", "edappally": "Kerala", "aluva": "Kerala",
    "ernakulam": "Kerala", "fort kochi": "Kerala", "mattancherry": "Kerala",
    "vypin": "Kerala", "muvattupuzha": "Kerala", "perumbavoor": "Kerala",
    "kazhakootam": "Kerala", "nemom": "Kerala", "balaramapuram": "Kerala",
    "palarivattom": "Kerala", "kaloor": "Kerala", "panampilly nagar": "Kerala",
    # ── Lucknow ───────────────────────────────────────────────────────────
    "gomtinagar": "Uttar Pradesh", "gomti nagar": "Uttar Pradesh",
    "hazratganj": "Uttar Pradesh", "aliganj": "Uttar Pradesh",
    "indira nagar": "Uttar Pradesh", "gomti nagar extension": "Uttar Pradesh",
    "sitapur road": "Uttar Pradesh", "kanpur road": "Uttar Pradesh",
    "aashiana": "Uttar Pradesh", "jankipuram": "Uttar Pradesh",
    "telibagh": "Uttar Pradesh", "vishwas khand": "Uttar Pradesh",
    # ── Indore ────────────────────────────────────────────────────────────
    "vijaynagar": "Madhya Pradesh", "vijay nagar": "Madhya Pradesh",
    "schemeb": "Madhya Pradesh", "scheme b": "Madhya Pradesh",
    "schemec": "Madhya Pradesh", "scheme c": "Madhya Pradesh",
    "palasia": "Madhya Pradesh", "sapna sangeeta": "Madhya Pradesh",
    "vijay square": "Madhya Pradesh", "ab road": "Madhya Pradesh",
    "rajwada": "Madhya Pradesh", "bombay hospital": "Madhya Pradesh",
    "limbdi lane": "Madhya Pradesh", "safa bagh": "Madhya Pradesh",
    # ── Visakhapatnam ─────────────────────────────────────────────────────
    "mvpcolony": "Andhra Pradesh", "mvp colony": "Andhra Pradesh",
    "gajuwaka": "Andhra Pradesh", "akkayyapalem": "Andhra Pradesh",
    "dwaraka nagar": "Andhra Pradesh", "madhurawada": "Andhra Pradesh",
    "pcb colony": "Andhra Pradesh", "siripuram": "Andhra Pradesh",
    "monte carlo": "Andhra Pradesh", "bhel": "Andhra Pradesh",
    "gajuwaka": "Andhra Pradesh", "kancharapalem": "Andhra Pradesh",
    # ── Vijayawada ────────────────────────────────────────────────────────
    "governorpet": "Andhra Pradesh", "benzcircle": "Andhra Pradesh",
    "benz circle": "Andhra Pradesh", "patamata": "Andhra Pradesh",
    "labbipet": "Andhra Pradesh", "sidhartha nagar": "Andhra Pradesh",
    "mg road vijayawada": "Andhra Pradesh", "kanuru": "Andhra Pradesh",
    "gannavaram": "Andhra Pradesh", "tadigadapa": "Andhra Pradesh",
    # ── Bhubaneswar ───────────────────────────────────────────────────────
    "saheednagar": "Odisha", "shaheed nagar": "Odisha", "patia": "Odisha",
    "kalinganagar": "Odisha", "jaydev vihar": "Odisha", "jaydevvihar": "Odisha",
    "saheed nagar": "Odisha", "rajpath": "Odisha", "unit 1": "Odisha",
    "unit 4": "Odisha", "crp": "Odisha", "infocity": "Odisha",
    "chandrasekharpur": "Odisha", "patrapada": "Odisha",
    "nayapalli": "Odisha", "sahid nagar": "Odisha",
    # ── Guwahati ──────────────────────────────────────────────────────────
    "beltola": "Assam", "ulubari": "Assam", "zoo road": "Assam",
    "gs road": "Assam", "ganeshguri": "Assam", "christian basti": "Assam",
    "uzan bazar": "Assam", "fancy bazar": "Assam", "pandu": "Assam",
    "satgaon": "Assam", "bharalumukh": "Assam",
    # ── Bhopal ────────────────────────────────────────────────────────────
    "areracolony": "Madhya Pradesh", "arera colony": "Madhya Pradesh",
    "mpnagar": "Madhya Pradesh", "mp nagar": "Madhya Pradesh",
    "kolarroad": "Madhya Pradesh", "kolar road": "Madhya Pradesh",
    "shahpura": "Madhya Pradesh", "hoshangabad road": "Madhya Pradesh",
    "new market": "Madhya Pradesh", "mp nagar zone 1": "Madhya Pradesh",
    "mp nagar zone 2": "Madhya Pradesh", "6 no stop": "Madhya Pradesh",
    # ── Chandigarh ────────────────────────────────────────────────────────
    "sector17": "Chandigarh", "sector 17": "Chandigarh",
    "sector22": "Chandigarh", "sector 22": "Chandigarh",
    "sector35": "Chandigarh", "sector 35": "Chandigarh",
    "sector 36": "Chandigarh", "sector 43": "Chandigarh",
    "sector 26": "Chandigarh", "sector 11": "Chandigarh",
    "mohali": "Chandigarh", "phase 5 mohali": "Chandigarh",
    "phase 3 bdc": "Chandigarh", "phase 7": "Chandigarh",
    "phase 3b2": "Chandigarh", "phase 5": "Chandigarh",
    "kharar": "Chandigarh", "derabassi": "Chandigarh",
    # ── Surat ─────────────────────────────────────────────────────────────
    "vesu": "Gujarat", "adajan": "Gujarat", "city light": "Gujarat",
    "nanpura": "Gujarat", "Athwa": "Gujarat", "athwa lines": "Gujarat",
    "piplod": "Gujarat", "dumas": "Gujarat", "bhatar": "Gujarat",
    "udhna": "Gujarat", "sachin": "Gujarat", "magdalla": "Gujarat",
    "sumul dairy": "Gujarat", "rander": "Gujarat",
    # ── Nagpur ────────────────────────────────────────────────────────────
    "dharampeth": "Maharashtra", "sitabuldi": "Maharashtra",
    "manish nagar": "Maharashtra", "sadar": "Maharashtra",
    "wadi": "Maharashtra", "hingna": "Maharashtra", "kamptee": "Maharashtra",
    "gandhibagh": "Maharashtra", "sanghvi nagar": "Maharashtra",
    "pratap nagar": "Maharashtra", "sakkardara": "Maharashtra",
    # ── Thiruvananthapuram ────────────────────────────────────────────────
    "kowdiar": "Kerala", "pattoor": "Kerala", "technopark": "Kerala",
    "vazhuthacaud": "Kerala", "sreekaryam": "Kerala", "ulloor": "Kerala",
    "perurkada": "Kerala", "nemom": "Kerala", "kazhakkoottam": "Kerala",
    "attinkuzhy": "Kerala", "akathumuri": "Kerala",
    # ── Mysuru ────────────────────────────────────────────────────────────
    "vijayanagar": "Karnataka", "kuvempunagar": "Karnataka",
    "saraswathipuram": "Karnataka", "jayalakshmipuram": "Karnataka",
    "hebbal": "Karnataka", "gokulam": "Karnataka", "hunsur road": "Karnataka",
    "nazbad": "Karnataka", "chamundipuram": "Karnataka",
    # ── Coimbatore ────────────────────────────────────────────────────────
    "rs puram": "Tamil Nadu", "gandhipuram": "Tamil Nadu",
    "saibaba colony": "Tamil Nadu", "peelamedu": "Tamil Nadu",
    "sungam": "Tamil Nadu", "rafi ahmed kidwai road": "Tamil Nadu",
    "gandhipuram west": "Tamil Nadu", "singanallur": "Tamil Nadu",
    "sulur": "Tamil Nadu", "pollachi road": "Tamil Nadu",
    # ── Patna ─────────────────────────────────────────────────────────────
    "boring road": "Bihar", "kankarbagh": "Bihar", "baily road": "Bihar",
    "fraser road": "Bihar", "gandhi maidan": "Bihar",
    "bailey road": "Bihar", "patliputra colony": "Bihar",
    "rajendra nagar": "Bihar", "kanpur road patna": "Bihar",
    "danapur": "Bihar", "phulwari sharif": "Bihar",
    # ── Kochi additional ──────────────────────────────────────────────────
    "thrikkakara": "Kerala", "kakkanad infopark": "Kerala",
    "infopark": "Kerala", "smartcity": "Kerala", "seaport": "Kerala",
    # ── Ahmedabad additional ──────────────────────────────────────────────
    "hebatpur": "Gujarat", "thaltej road": "Gujarat",
    "science city road": "Gujarat", "sola road": "Gujarat",
    "sg highway ahmedabad": "Gujarat", "odia": "Gujarat",
    "memco": "Gujarat", "nana chiloda": "Gujarat",
    # ── Lucknow additional ────────────────────────────────────────────────
    "aashiana lucknow": "Uttar Pradesh", "telibagh lucknow": "Uttar Pradesh",
    "gomti nagar vit": "Uttar Pradesh", "gomti nagar gomti": "Uttar Pradesh",
    "indira nagar lucknow": "Uttar Pradesh", "alambagh": "Uttar Pradesh",
    "charbagh": "Uttar Pradesh",
    # ── Jaipur additional ─────────────────────────────────────────────────
    "lalkothi jaipur": "Rajasthan", "ajmer road": "Rajasthan",
    "tonk road jaipur": "Rajasthan", "jagatpura jaipur": "Rajasthan",
    # ── Ranchi ────────────────────────────────────────────────────────────
    "lalpur": "Jharkhand", "ashok nagar ranchi": "Jharkhand",
    "harmu": "Jharkhand", "doranda": "Jharkhand",
    "kanke": "Jharkhand", "argora": "Jharkhand",
    # ── Dehradun ──────────────────────────────────────────────────────────
    "rajpur road": "Uttarakhand", "clement town": "Uttarakhand",
    "vasant vihar": "Uttarakhand", "isbt": "Uttarakhand",
    "clock tower": "Uttarakhand", "paltan bazar": "Uttarakhand",
    "premnagar": "Uttarakhand",
    # ── Raipur ────────────────────────────────────────────────────────────
    "telibandha": "Chhattisgarh", "shankar nagar": "Chhattisgarh",
    "civil lines raipur": "Chhattisgarh", "mla colony": "Chhattisgarh",
    "vip road": "Chhattisgarh", "new rajender nagar": "Chhattisgarh",
    "devendra nagar": "Chhattisgarh", "pandri": "Chhattisgarh",
    # ── Tirupati ──────────────────────────────────────────────────────────
    "renigunta road": "Andhra Pradesh", "vedayapalem": "Andhra Pradesh",
    "sri city": "Andhra Pradesh", "karakambadi": "Andhra Pradesh",
    "k.t.r": "Andhra Pradesh", "chandragiri": "Andhra Pradesh",
    # ── Kurnool ───────────────────────────────────────────────────────────
    "nandyal road": "Andhra Pradesh", "river view colony": "Andhra Pradesh",
    "lakshmi nagar": "Andhra Pradesh", "budhawar pet": "Andhra Pradesh",
    "ram nagar": "Andhra Pradesh", "sri rama nagar": "Andhra Pradesh",
    # ── Madurai ───────────────────────────────────────────────────────────
    "anna nagar madurai": "Tamil Nadu", "kk nagar": "Tamil Nadu",
    "villapuram": "Tamil Nadu", "thiruparankundram": "Tamil Nadu",
    "meenakshi": "Tamil Nadu", "teppakulam": "Tamil Nadu",
    "kalavasal": "Tamil Nadu", "tallakulam": "Tamil Nadu",
    # ── Warangal ──────────────────────────────────────────────────────────
    "hanamkonda": "Telangana", "kazipet": "Telangana", "subedari": "Telangana",
    "warangal east": "Telangana", "warangal west": "Telangana",
    "nakkalagadda": "Telangana",
    # ── Mangaluru ─────────────────────────────────────────────────────────
    "bejai": "Karnataka", "kadri": "Karnataka", "urva": "Karnataka",
    "kankanady": "Karnataka", "nagori": "Karnataka", "surathkal": "Karnataka",
}


def _norm(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalnum())


# Normalise LOCALITY_STATE keys so lookups work regardless of spacing/typos.
LOCALITY_STATE = {_norm(k): v for k, v in LOCALITY_STATE.items()}


def nearby_cities(term: str) -> tuple[list[str], str] | None:
    """Return (nearby_cities, state_label) to broaden to, or None if unknown.

    - Known state name → all cities in that state.
    - Known city → other cities in the same state.
    - Known locality/area → cities in its state.
    - Anything else → None (caller should fall back globally).
    """
    t = _norm(term)
    if not t:
        return None

    # 1. Exact locality match
    if t in LOCALITY_STATE:
        state = LOCALITY_STATE[t]
        return INDIA_STATES.get(state, []), state

    # 2. Exact state name
    for state, cities in INDIA_STATES.items():
        if t == _norm(state):
            return cities, state

    # 3. Exact city
    if t in _CITY_STATE:
        state = _CITY_STATE[t]
        return INDIA_STATES.get(state, []), state

    # 3b. Exact district
    if t in _DISTRICT_STATE:
        state = _DISTRICT_STATE[t]
        return INDIA_STATES.get(state, []), state

    # 4. Substring / prefix match against state names
    for state, cities in INDIA_STATES.items():
        if len(t) >= 4 and t in _norm(state):
            return cities, state

    # 5. Substring / prefix match against known cities and districts
    for state, cities in INDIA_STATES.items():
        for city in cities:
            if t == _norm(city) or (len(t) >= 4 and (t in _norm(city) or _norm(city) in t)):
                return cities, state
    for state, districts in INDIA_DISTRICTS.items():
        for district in districts:
            if t == _norm(district) or (len(t) >= 4 and (t in _norm(district) or _norm(district) in t)):
                return INDIA_STATES.get(state, []), state

    # 6. Fuzzy match against known localities (handles typos / short names)
    for locality, state in LOCALITY_STATE.items():
        if len(t) >= 6 and (locality.startswith(t) or t in locality or locality in t):
            return INDIA_STATES.get(state, []), state

    return None
