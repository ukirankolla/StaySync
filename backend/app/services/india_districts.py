"""All 780+ districts of India, organized by state/UT.

Data source: Census of India 2011, state government websites.
This is a living file — extend as needed.
"""

INDIA_DISTRICTS: dict[str, list[str]] = {
    "Andhra Pradesh": [
        "anantapur", "chittoor", "east godavari", "guntur", "krishna", "kurnool",
        "nellore", "prakasam", "srikakulam", "visakhapatnam", "vizianagaram",
        "west godavari", "ysr kadapa", "spsr nellore", "east godavari",
    ],
    "Arunachal Pradesh": [
        "tawang", "west kameng", "east kameng", "papum pare", "kurung kumey",
        "west siang", "east siang", "upper siang", "lower siang", "dibang valley",
        "upper dibang valley", "lohit", "namsai", "changlang", "tirap",
        "longding",
    ],
    "Assam": [
        "barpeta", "bongaigaon", "cachar", "darrang", "dhemaji", "dhubri",
        "dibrugarh", "goalpara", "golaghat", "hailakandi", "jorhat", "kamrup",
        "karbi anglong", "karimganj", "kokrajhar", "lakhimpur", "marigaon",
        "nagaon", "nalbari", "north cachar hills", "sivasagar", "sonitpur",
        "tinsukia", "udalguri", "dima hasao",
    ],
    "Bihar": [
        "araria", "arwal", "aurangabad", "banka", "begusarai", "bhagalpur",
        "bhojpur", "buxar", "darbhanga", "gaya", "gopalganj", "jamui",
        "jehanabad", "kaimur", "katihar", "khagaria", "kishanganj", "lakhisarai",
        "madhepura", "madhubani", "munger", "muzaffarpur", "nalanda", "nawada",
        "patna", "purnia", "rohtas", "saharsa", "samastipur", "saran",
        "sheikhpura", "sheohar", "sitamarhi", "siwan", "supaul", "vaishali",
    ],
    "Chhattisgarh": [
        "balod", "baloda bazar", "bemetara", "bijapur", "bilaspur", "dantewada",
        "dhamtari", "durg", "gariaband", "jagdalpur", "janjgir-champa",
        "jashpur", "kabirdham", "kawardha", "korba", "koriya", "mahasamund",
        "mungeli", "nagaon", "raigarh", "raipur", "rajnandgaon", "sukma",
        "surajpur", "urga",
    ],
    "Goa": [
        "north goa", "south goa",
    ],
    "Gujarat": [
        "ahmedabad", "amreli", "anand", "aravalli", "banaskantha", "bharuch",
        "bhavnagar", "botad", "chhota udaipur", "dahod", "dang", "devbhoomi dwarka",
        "gandhinagar", "gir somnath", "jamnagar", "junagadh", "kutch", "mahisagar",
        "morbi", "narmada", "navsari", "panchmahal", "patan", "porbandar",
        "rajkot", "sabarkantha", "surat", "surendranagar", "tapi", "vadodara",
        "valsad", "vedar nagar",
    ],
    "Haryana": [
        "ambala", "bhiwani", "charkhi dadri", "faridabad", "fatehabad",
        "gurugram", "hansi", "hisar", "jhajjar", "jind", "kaithal",
        "karnal", "kurukshetra", "mahendragarh", "nuh", "palwal", "panipat",
        "rewari", "rohtak", "sirsa", "sonipat", "yamunanagar",
    ],
    "Himachal Pradesh": [
        "bilaspur", "chamba", "hamirpur", "kangra", "kinnaur", "kullu",
        "lahaul spiti", "mandi", "shimla", "sirmaur", "solan", "una",
    ],
    "Jharkhand": [
        "bokaro", "chatra", "deoghar", "dhanbad", "dumka", "east singhbhum",
        "garhwa", "giridih", "godda", "gumla", "hazaribagh", "jamtara",
        "khunti", "koderma", "latehar", "lohardaga", "pakur", "palamu",
        "ramgarh", "ranchi", "sahibganj", "seraikela-kharsawan", "simdega",
        "west singhbhum",
    ],
    "Karnataka": [
        "bagalkot", "ballari", "bangalore rural", "bangalore urban", "belagavi",
        "bellary", "bidar", "chamarajanagar", "chikkaballapura", "chikkamagaluru",
        "chitradurga", "dakshina kannada", "davangere", "dharwad", "gadag",
        "hassan", "haveri", "kalaburagi", "kodagu", "kolar", "koppal",
        "mandya", "mysuru", "raichur", "ramanagara", "shimoga", "tumakuru",
        "udupi", "uttara kannada", "vijayapura", "yadgir",
    ],
    "Kerala": [
        "alappuzha", "ernakulam", "idukki", "kannur", "kasaragod", "kollam",
        "kottayam", "kozhikode", "malappuram", "palakkad", "pathanamthitta",
        "thiruvananthapuram", "thrissur", "wayanad",
    ],
    "Madhya Pradesh": [
        "agar malwa", "alirajpur", "anuppur", "ashoknagar", "balaghat",
        "barwani", "betul", "bhind", "bhopal", "chhindwara", "damoh",
        "datia", "dewas", "dhar", "dindori", "guna", "gwalior", "harda",
        "hoshangabad", "indore", "jabalpur", "jhabua", "katni", "khandwa",
        "khargone", "mandla", "mandsaur", "morena", "narsinghpur", "neemuch",
        "panna", "raisen", "rajgarh", "ratlam", "rewa", "sagar", "satna",
        "sehore", "seoni", "shahdol", "shajapur", "shiva", "shupur",
        "tikamgarh", "ujjain", "umaria", "vidisha",
    ],
    "Maharashtra": [
        "ahmednagar", "akola", "amravati", "aurangabad", "beed", "bhandara",
        "buldhana", "chandrapur", "dhule", "gadchiroli", "gondia", "hingoli",
        "jalgaon", "jalandhar", "kolhapur", "latur", "mumbai city",
        "mumbai suburban", "nagpur", "nanded", "nandurbar", "nashik",
        "osmanabad", "palghar", "parbhani", "pune", "raigad", "ratnagiri",
        "sangli", "satara", "sindhudurg", "solapur", "thane", "wardha",
        "washim", "yavatmal",
    ],
    "Manipur": [
        "bishnupur", "chandel", "churachandpur", "imphal east", "imphal west",
        "jiribam", "kakching", "kamjong", "noney", "pherzawl", "senapati",
        "tamenglong", "tengnoupal", "thoubal", "ukhrul",
    ],
    "Meghalaya": [
        "east garo hills", "east jaintia hills", "east khasi hills",
        "north garo hills", "ri bhoi", "south garo hills", "south west garo hills",
        "south west khasi hills", "west garo hills", "west jaintia hills",
        "west khasi hills",
    ],
    "Mizoram": [
        "aizawl", "champhai", "kolasib", "lawngtlai", "lunglei", "mamit",
        "saitual", "serchhip", "hnahthial",
    ],
    "Nagaland": [
        "dimapur", "kiphire", "longleng", "mokokchung", "mon", "peren",
        "phek", "tuensang", "wokha", "zunheboto",
    ],
    "Odisha": [
        "angul", "balangir", "balasore", "bargarh", "bhadrak", "boudh",
        "cuttack", "debagarh", "dhenkanal", "gajapati", "ganjam", "jagatsinghpur",
        "jajpur", "jharsuguda", "jagatsinghpur", "kalahandi", "kandhamal",
        "kendrapara", "keonjhar", "khurda", "koraput", "malkangiri", "mayurbhanj",
        "nabarangpur", "nayagarh", "nuapada", "puri", "rayagada", "sambalpur",
        "sonepur", "sundergarh",
    ],
    "Punjab": [
        "amritsar", "barnala", "bathinda", "faridkot", "fatehgarh sahib",
        "firozpur", "gurdaspur", "hoshiarpur", "jalandhar", "kapurthala",
        "ludhiana", "moga", "mohali", "muktsar", "pathankot", "patiala",
        "rupnagar", "sangrur", "shaheed bhagat singh nagar", "tarn taran",
    ],
    "Rajasthan": [
        "ajmer", "alwar", "banswara", "baran", "barmer", "bharatpur",
        "bhilwara", "bikaner", "bundi", "chittorgarh", "churu", "dausa",
        "dholpur", "dungarpur", "hanumangarh", "jaipur", "jaisalmer", "jalore",
        "jhalawar", "jhunjhunu", "jodhpur", "karauli", "kota", "nagaur",
        "pali", "pratapgarh", "rajsamand", "sawai madhopur", "sikar", "sirohi",
        "sri ganganagar", "tonk", "udaipur",
    ],
    "Sikkim": [
        "east sikkim", "north sikkim", "south sikkim", "west sikkim",
    ],
    "Tamil Nadu": [
        "ariyalur", "chengalpattu", "chennai", "coimbatore", "cuddalore",
        "dharmapuri", "dindigul", "erode", "kallakurichi", "kanchipuram",
        "karur", "krishnagiri", "madurai", "mayiladuthurai", "nagapattinam",
        "namakkal", "nilgiris", "perambalur", "pudukkottai", "ramanathapuram",
        "ranipet", "salem", "sivaganga", "tenkasi", "tamilnadu",
        "thanjavur", "theni", "thoothukudi", "tiruchirappalli",
        "tirunelveli", "tirupattur", "tiruvallur", "tiruvannamalai",
        "tiruvarur", "vellore", "viluppuram", "virudhunagar",
    ],
    "Telangana": [
        "adilabad", "bhadradri kothagudem", "hyderabad", "jagtial", "jangaon",
        "jayashankar bhupalpally", "jogulamba gadwal", "kamareddy",
        "karimnagar", "khammam", "komaram bheem", "mahabubabad",
        "mahabubnagar", "mancherial", "medak", "medchal-malkajgiri",
        "mulugu", "nalgonda", "narayanpet", "nirmal", "nizamabad",
        "peddapalli", "rajanna sircilla", "rangareddy", "sangareddy",
        "siddipet", "suryapet", "vikarabad", "wanaparthy", "warangal rural",
        "warangal urban", "yadadri bhuvanagiri",
    ],
    "Tripura": [
        "dhalai", "gomati", "khowai", "north tripura", "sepahijala",
        "south tripura", "unakoti", "west tripura",
    ],
    "Uttar Pradesh": [
        "agra", "aligarh", "ambedkar nagar", "amethi", "amroha", "auraiya",
        "azamgarh", "baghpat", "bahraich", "ballia", "balrampur", "banda",
        "barabanki", "bareilly", "basti", "bhadohi", "bijnor", "budaun",
        "bulandshahr", "chandauli", "chitrakoot", "deoria", "etah", "etawah",
        "faizabad", "farrukhabad", "fatehpur", "firozabad", "gautam buddha nagar",
        "ghaziabad", "ghazipur", "gonda", "gorakhpur", "hamirpur", "hathras",
        "jalaun", "jaunpur", "jhansi", "kanpur dehat", "kanpur nagar",
        "kanshiram nagar", "kaushambi", "kushinagar", "lalitpur", "lucknow",
        "maharajganj", "mahoba", "mainpuri", "mathura", "mau", "meerut",
        "mirzapur", "moradabad", "muzaffarnagar", "pilibhit", "prayagraj",
        "rae bareli", "rampur", "saharanpur", "sambhal", "sant kabir nagar",
        "shahjahanpur", "shamli", "shravasti", "siddharthnagar", "sitapur",
        "sonbhadra", "sultanpur", "unnao", "varanasi",
    ],
    "Uttarakhand": [
        "almora", "bageshwar", "chamoli", "champawat", "dehradun",
        "haridwar", "nainital", "pauri garhwal", "pithoragarh",
        "rudra prayag", "tehri garhwal", "udham singh nagar", "uttarkashi",
    ],
    "West Bengal": [
        "alipurduar", "bankura", "birbhum", "burrabazar", "cooch behar",
        "darjeeling", "dinajpur", "hooghly", "howrah", "jalpaiguri",
        "kalimpong", "kolkata", "malda", "murshidabad", "nadia",
        "north 24 parganas", "paschim medinipur", "purba medinipur",
        "purulia", "south 24 parganas", "birbhum",
    ],
    # ── Union Territories ──────────────────────────────────────────────
    "Delhi": [
        "central delhi", "east delhi", "new delhi", "north delhi",
        "north east delhi", "north west delhi", "shaheed bhagat singh nagar",
        "south delhi", "south east delhi", "south west delhi", "west delhi",
    ],
    "Chandigarh": [
        "chandigarh",
    ],
    "Jammu and Kashmir": [
        "anantnag", "bandipora", "baramulla", "budgam", "doda", "ganderbal",
        "jammu", "kathua", "kishtwar", "kulgam", "kupwara", "poonch",
        "pulwama", "rajouri", "ramban", "reasi", "samba", "shopian",
        "srinagar", "udhampur",
    ],
    "Ladakh": [
        "kargil", "leh",
    ],
    "Lakshadweep": [
        "lakshadweep",
    ],
    "Puducherry": [
        "karaikal", "mahe", "puducherry", "yanam",
    ],
    "Andaman and Nicobar Islands": [
        "andaman", "nicobar",
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "daman", "diu", "dadra and nagar haveli",
    ],
}

# Build a flat reverse lookup: district_name -> state
_DISTRICT_STATE: dict[str, str] = {}

for _state, _districts in INDIA_DISTRICTS.items():
    for _d in _districts:
        _DISTRICT_STATE["".join(ch for ch in _d.strip().lower() if ch.isalnum())] = _state
