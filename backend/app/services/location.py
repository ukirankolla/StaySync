"""Location helpers for recommendation fallback (India-focused, best-effort).

When an exact city search has no users, we broaden to nearby cities in the
same state so the discovery feed never dead-ends. Cities not in this map
fall back to a global search instead.
"""

INDIA_STATES: dict[str, list[str]] = {
    "Andhra Pradesh": ["visakhapatnam", "vijayawada", "guntur", "tirupati", "ongole", "nellore", "kakinada", "rajahmundry"],
    "Telangana": ["hyderabad", "warangal", "karimnagar", "nizamabad"],
    "Tamil Nadu": ["chennai", "coimbatore", "madurai", "tiruchirappalli", "salem", "vellore"],
    "Karnataka": ["bengaluru", "mysuru", "hubli", "mangaluru", "belagavi"],
    "Maharashtra": ["mumbai", "pune", "nagpur", "nashik", "thane"],
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


def nearby_cities(term: str) -> list[str] | None:
    """Return cities to broaden a search to, or None if the term is unknown.

    - A known state name -> all cities in that state.
    - A known city name -> other cities in the same state.
    - Anything else -> None (caller should fall back globally).
    """
    t = term.strip().lower()
    if not t:
        return None
    for state, cities in INDIA_STATES.items():
        if t == state.lower() or (len(t) >= 4 and t in state.lower()):
            return cities
    for cities in INDIA_STATES.values():
        for city in cities:
            if t == city or (len(t) >= 4 and t in city):
                return cities
    return None
