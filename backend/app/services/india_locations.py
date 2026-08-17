"""Comprehensive Indian location data — every state, UT, major city, and
common locality. Used for intelligent fallback matching in discovery feed.

Data sources: Census of India, Wikipedia, common knowledge. This is a
living file — extend as needed.
"""

# All 28 states + 8 union territories with major cities and towns.
# Lowercase keys.
INDIA_STATES: dict[str, list[str]] = {
    # ── States ──────────────────────────────────────────────────────
    "Andhra Pradesh": [
        "visakhapatnam", "vijayawada", "guntur", "tirupati", "nellore", "kakinada",
        "rajahmundry", "ongole", "anantapur", "kurnool", "kadapa", "khammam",
        "machilipatnam", "eluru", "nuzvid", "chittoor", "proddatur", "tuni",
        "srikakulam", "vizianagaram", "bhimavaram", "narsapur", "tenali",
        "guntur east", "guntur west", "ponnur", "repalle", "bapatla",
        "chilakaluripeta", "narasaraopet", "gudur", "srikalahasti", "puttur",
        "rayachoti", "madanapalle", "hospet", "bellary", "raichur",
    ],
    "Arunachal Pradesh": [
        "itanagar", "naharlagun", "pasighat", "tawang", "ziro", "along",
        "bomdila", "changlang", "deomali", "tezu", "roing", "daporijo",
        "aalo", "yinkiong", "seppa", "kurung kumey", "upper siang",
    ],
    "Assam": [
        "guwahati", "silchar", "dibrugarh", "jorhat", "nagaon", "tezpur",
        "bongaigaon", "tinsukia", "sivasagar", "goalpara", "barpeta",
        "karimganj", "hailakandi", "diphu", "north lakhimpur", "morigaon",
        "golaghat", "jorhat", "sonitpur", "darrang", "kamrup",
    ],
    "Bihar": [
        "patna", "gaya", "bhagalpur", "muzaffarpur", "darbhanga", "arrah",
        "begusarai", "katihar", "munger", "purnia", "banka", "saharsa",
        "madhepura", "samastipur", "sitamarhi", "vaishali", "nawada",
        "jamui", "kaimur", "buxar", "rohtas", "jehanabad", "aurangabad",
        "lakhisarai", "sheikhpura", "nalanda", "nalanda bihar",
    ],
    "Chhattisgarh": [
        "raipur", "bilaspur", "durg", "bhilai", "korba", "jagdalpur",
        "raigarh", "ambikapur", "chirmiri", "kawardha", "kabirdham",
        "rajnandgaon", "dongargarh", "dhamtari", "gariaband", "balod",
        "bemetara", "mungeli", "janjgir", "sakti", "korba",
    ],
    "Goa": [
        "panaji", "margao", "vasco da gama", "mapusa", "ponda", "calangute",
        "candolim", "baga", "anjuna", "colva", "benaulim", "cavelossim",
        "assagao", "arpora", "sinquerim", "porvorim", "merul",
    ],
    "Gujarat": [
        "ahmedabad", "surat", "vadodara", "rajkot", "bhavnagar", "jamnagar",
        "junagadh", "anand", "navsari", "mahesana", "nadiad", "gandhinagar",
        "gandhidham", "morbi", "surendranagar", "bharuch", "bardoli",
        "veraval", "porbandar", "palanpur", "jetpur", "keshod",
        "dahod", "godhra", "valsad", "vapi", "bopal", "satellite",
        "vastrapur", "prahladnagar", "thaltej", "maninagar", "ellis bridge",
    ],
    "Haryana": [
        "gurgaon", "faridabad", "panipat", "ambala", "yamunanagar",
        "rohtak", "hisar", "karnal", "sonipat", "jind", "bhiwani",
        "bahadurgarh", "dabwali", "kaithal", "palwal", "narnaul",
        "mandi dabwali", "pinjore", "kalka", "tohana", "narwana",
        "sirsa", "jhajjar", "charkhi dadri", "rewari", "mahendragarh",
    ],
    "Himachal Pradesh": [
        "shimla", "manali", "kullu", "dharamsala", "mcleodganj", "kangra",
        "mandi", "hamirpur", "bilaspur", "solan", "chamba", "una",
        "sundarnagar", "nahan", "paonta sahib", "baddi", "parwanoo",
        "kasauli", "dalhousie", "khajjiar", "keylong", "rekong peo",
    ],
    "Jharkhand": [
        "ranchi", "jamshedpur", "dhanbad", "bokaro", "deoghar", "hazaribagh",
        "giridih", "chaibasa", "medininagar", "dumka", "godda", "sahebganj",
        "pakur", "rajmahal", "chaibasa", "west singhbhum", "east singhbhum",
    ],
    "Karnataka": [
        "bengaluru", "mysuru", "hubballi", "dharwad", "mangaluru", "belagavi",
        "kalaburagi", "vijayapura", "ballari", "tumakuru", "shivamogga",
        "hassan", "chikkamagaluru", "davangere", "gangavathi", "bidar",
        "raichur", "kolar", "chikkaballapura", "ramanagara", "tumkur",
        "madikeri", "gokarna", "karwar", "bidar", "yadgir",
    ],
    "Kerala": [
        "kochi", "thiruvananthapuram", "kozhikode", "thrissur", "kollam",
        "kottayam", "palakkad", "malappuram", "wayanad", "idukki",
        "ernakulam", "aluva", "kakkanad", "edappally", "tripunithura",
        "fort kochi", "mattancherry", "vypin", "muvattupuzha", "perumbavoor",
        "kazhakootam", "nemom", "balaramapuram", "kazhakoottam", "attukal",
    ],
    "Madhya Pradesh": [
        "indore", "bhopal", "gwalior", "jabalpur", "ujjain", "sagar",
        "satna", "ratlam", "rewa", "dewas", "satna", "chhindwara",
        "gwalior", "morena", "bhopal", "raisen", "sehore", "vidisha",
        "hoshangabad", "narmadapuram", "betul", "chhindwara", "narsinghpur",
        "mandla", "dindori", "katni", "umaria", "panna", "chhatarpur",
        "tikamgarh", "damoh", "sagar", "sehore", "indore",
    ],
    "Maharashtra": [
        "mumbai", "pune", "nagpur", "nashik", "thane", "navi mumbai",
        "aurangabad", "solapur", "amravati", "kolhapur", "sangli",
        "akola", "jalgaon", "buldhana", "beed", "osmanabad", "latur",
        "parbhani", "hingoli", "washim", "yavatmal", "wardha", "gadchiroli",
        "ratnagiri", "sindhudurg", "dhule", "nandurbar", "bhandara",
        "gondia", "chandrapur", "katol", "kalyan", "dombivli",
        "vasai", "virar", "bhiwandi", "ulhasnagar", "ambarnath",
    ],
    "Manipur": [
        "imphal", "thoubal", "bishnupur", "churachandpur", "jiribam",
        "tamenglong", "senapati", "ukhrul", "chandel", "noney", "tengnoupal",
    ],
    "Meghalaya": [
        "shillong", "tura", "jowai", "cherrapunji", "sohra", "nongpoh",
        "baghmara", "resubelpara", "dawki", "mairang",
    ],
    "Mizoram": [
        "aizawl", "lawngtlai", "champhai", "kolasib", "serchhip",
        "mamit", "saitual", "khawzawl", "hnahthial",
    ],
    "Nagaland": [
        "kohima", "dimapur", "mokokchung", "tuensang", "wokha", "zunheboto",
        "phek", "mon", "longleng", "kiphire", "peren",
    ],
    "Odisha": [
        "bhubaneswar", "cuttack", "rourkela", "berhampur", "sambalpur",
        "balasore", "bhadrak", "puri", "jajpur", "angul", "dhenkanal",
        "keonjhar", "mayurbhanj", "koraput", "rayagada", "gajapati",
        "ganjam", "gajapati", "nayagarh", "khurda", "jagatsinghpur",
        "kendrapara", "jajpur", "sundargarh", "deogarh",
    ],
    "Punjab": [
        "chandigarh", "ludhiana", "amritsar", "jalandhar", "patiala",
        "bathinda", "hoshiarpur", "gurdaspur", "moga", "pathankot",
        "phagwara", "moga", "kapurthala", "sangrur", "faridkot",
        "mansa", "barnala", "mohali", "kharar", "derabassi",
        "zirakpur", "lalru", "attari", "ranjit nagar",
    ],
    "Rajasthan": [
        "jaipur", "jodhpur", "udaipur", "kota", "ajmer", "bikaner",
        "udaipur", "alwar", "bharatpur", "sikar", "pali", "kota",
        "sri ganganagar", "bhilwara", "tonk", "nagaur", "churu",
        "jalore", "jhalawar", "dungarpur", "barmer", "jaisalmer",
        "banswara", "rajsamand", "pratapgarh", "chittorgarh",
    ],
    "Sikkim": [
        "gangtok", "namchi", "gyalshing", "rangit", "ravangla",
        "mangan", "singtam", "pelling",
    ],
    "Tamil Nadu": [
        "chennai", "coimbatore", "madurai", "tiruchirappalli", "salem",
        "vellore", "tirunelveli", "erode", "thoothukudi", "dindigul",
        "karur", "namakkal", "theni", "virudhunagar", "ramanathapuram",
        "cuddalore", "tiruvannamalai", "kanchipuram", "chengalpattu",
        "tiruvallur", "arani", "arcot", "washington", "krishnagiri",
        "dharmapuri", "hossur", "palani", "kodaikanal", "ooty",
        "nilgiris", "coonoor", "gudalur", "mettupalayam", "pollachi",
    ],
    "Telangana": [
        "hyderabad", "warangal", "karimnagar", "nizamabad", "adilabad",
        "khammam", "mahabubnagar", "nalgonda", "medak", "ranga reddy",
        "siddipet", "jagtial", "mancherial", "nirmal", "ramagundam",
        "bhongir", "suryapet", "kodad", "miryalaguda", "nagarjuna sagar",
        "gachibowli", "madhapur", "HITEC city", "kondapur", "kukatpally",
        "jubilee hills", "banjara hills", "secunderabad", "begumpet",
    ],
    "Tripura": [
        "agartala", "dharmanagar", "kailashahar", "ambassa", "belonia",
        "sabroom", "kamalpur", "melaghar",
    ],
    "Uttar Pradesh": [
        "lucknow", "kanpur", "varanasi", "agra", "meerut", "allahabad",
        "prayagraj", "bareilly", "meerut", "noida", "ghaziabad", "aligarh",
        "jhansi", "mathura", "firozabad", "rae bareli", "sitapur",
        "barabanki", "gorakhpur", "azamgarh", "ballia", "mau",
        "jaunpur", "mirzapur", "bhadohi", "chitrakoot", "fatehpur",
        "unnao", "hardoi", "shahjahanpur", "bulandshahr", "muzaffarnagar",
        "saharanpur", "dehradun", "rampur", "moradabad", "bijnor",
    ],
    "Uttarakhand": [
        "dehradun", "haridwar", "haldwani", "rishikesh", "kashipur",
        "roorkee", "manglaur", "sitanagar", "kotdwar", "ramnagar",
        "nainital", "almora", "pithoragarh", "champawat", "udham singh nagar",
        "bageshwar", "chamoli", "uttarkashi", "tehrigari", "srinagar garhwal",
    ],
    "West Bengal": [
        "kolkata", "howrah", "siliguri", "asansol", "durgapur", "bardhaman",
        "murshidabad", "birbhum", "malda", "nadia", "24 parganas north",
        "24 parganas south", "hooghly", "purulia", "bankura", "medinipur",
        "alipurduar", "jalpaiguri", "darjeeling", "cooch behar",
        "salt lake", "new town", "sector v", "salt lake sector v",
        "ballygunge", "park street", "elgin road", "gariahat",
    ],
    # ── Union Territories ──────────────────────────────────────────
    "Delhi": [
        "new delhi", "delhi", "dwarka", "rohini", "saket", "karol bagh",
        "lajpat nagar", "pitampura", "vasant kunj", "laxmi nagar",
        "connaught place", "chanakyapuri", "nehru place", "okhla",
        "moti nagar", "patel nagar", "rajouri garden", "punjabi bagh",
        "janakpuri", "tilak nagar", "malviya nagar", "hauz khas",
        "defence colony", "kalkaji", "jangpura", "kasturba nagar",
        "south ex", "north ex", "shakti nagar", "model town",
    ],
    "Chandigarh": [
        "chandigarh", "sector 17", "sector 22", "sector 35", "sector 43",
        "sector 26", "sector 11", "sector 31", "sector 44", "sector 46",
    ],
    "Jammu and Kashmir": [
        "srinagar", "jammu", "anantnag", "baramulla", "badgam",
        "poonch", "rajouri", "kathua", "samba", "udhampur",
        "rekhi", "gulmarg", "pahalgam", "sonamarg", "leh",
        "kargil", "nubra", "zanskar",
    ],
    "Ladakh": [
        "leh", "kargil", "nubra", "zanskar", "changthang", "drass",
    ],
    "Lakshadweep": [
        "kavaratti", "agatti", "minicoy", "andrott", "bangaram",
    ],
    "Puducherry": [
        "puducherry", "karaikal", "mahe", "yanam",
    ],
    "Andaman and Nicobar Islands": [
        "port blair", "diglipur", "rangat", "mayabunder", "havelock",
        "neil island", "baratang",
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "daman", "diu", "silvassa", "nani daman",
    ],
}

# Flatten for reverse lookup: city -> state
_CITY_STATE: dict[str, str] = {}


def _norm(s: str) -> str:
    return "".join(ch for ch in s.strip().lower() if ch.isalnum())


for _state, _cities in INDIA_STATES.items():
    for _city in _cities:
        _CITY_STATE[_norm(_city)] = _state
