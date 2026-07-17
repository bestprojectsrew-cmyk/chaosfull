"""
inline_generators.py — Chaos Engine v2.

Pure Python, zero AI, zero API, zero seeding.
Every click = different result. Max 4 lines per card.
Format: Emoji + Name / Person / Result / Punchline
"""

import random


def _card(emoji: str, gen_name: str, name: str, result: str, punchline: str) -> dict:
    body  = f"{emoji} {gen_name}\n\n{name}\n{result}\n\n{punchline}"
    title = f"{emoji} {gen_name}"
    return {
        "emoji": emoji,
        "title": title,
        "preview_title": title,
        "preview_description": f"Tap to reveal {name}'s {gen_name.lower()}.",
        "body": body,
    }



# ── Gay Detector ─────────────────────────────────────────────────────────────

def gen_gay(name):
    tiers = [
        ("0% Gay", ["Bro speedran 'No homo.'", "Straight as a ruler.", "The socks stayed on.", "Certified heterosexual."]),
        ("A Little Sus", ["That compliment was a little too passionate.", "Caught admiring the homies.", "The playlist raised questions.", "The fit was immaculate."]),
        ("Bi Energy", ["Playing both teams.", "Unlimited dating options unlocked.", "The vibes are balanced.", "No labels, just aura."]),
        ("Very Gay", ["Rainbow energy detected.", "Serving confidence.", "The detector started glowing.", "Slay level increased."]),
        ("Ultra Gay", ["The rainbow has accepted you.", "Pride parade VIP.", "Sparkles appeared automatically.", "The detector exploded."]),
        ("Legendary Gay", ["Beyond mortal classification.", "The rainbow asked for an autograph.", "Maximum fabulousness achieved.", "Even unicorns are impressed."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🏳️‍🌈", "Gay Detector", name, result, random.choice(punchlines))


# ── Freak Meter ──────────────────────────────────────────────────────────────

def gen_freak(name):
    tiers = [
        ("Pure Soul", ["Innocence protected.", "Needs adult supervision for jokes.", "Still blushes at hand holding.", "Vanilla certified."]),
        ("Curious", ["Read the comments twice.", "Double meaning detected.", "Pretends not to understand.", "Suspicious search history."]),
        ("Down Bad", ["Liked the post too fast.", "The reposts are public.", "The algorithm knows.", "Caught lacking at 2 AM."]),
        ("Certified Freak", ["The group chat has evidence.", "No shame detected.", "Too confident with it.", "The FBI agent sighed."]),
        ("Freakzilla", ["Beyond saving.", "The therapist quit.", "The algorithm gave up.", "Built with zero chill."]),
        ("The Freakiest", ["History will remember this.", "Even the internet is concerned.", "The demons took notes.", "Maximum freak achieved."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("😈", "Freak Meter", name, result, random.choice(punchlines))


# ── Ass Size ─────────────────────────────────────────────────────────────────

def gen_ass(name):
    tiers = [
        ("Flat",          ["Back pockets are decorative.", "Local chairs feel safe.", "Gravity couldn't find anything.", "The jeans hang like a flag."]),
        ("Small",         ["It's there. Somewhere.", "Points for effort.", "The seat appreciated the rest.", "Barely registered."]),
        ("Mid",           ["Mid. We move.", "Acceptable.", "The pants fit fine.", "Average distribution detected."]),
        ("Big",           ["People noticed.", "Seismograph twitched.", "Local chairs filed a report.", "The room shifted."]),
        ("Extra Large",   ["Traffic hesitated.", "Structural engineers were called.", "Pants filed for early retirement.", "The floor said ow."]),
        ("Massive",       ["Earthquake advisory issued.", "Scientists needed a moment.", "The building moved.", "Three people fainted."]),
        ("Biblically Huge",["Continental drift confirmed.", "NASA tracking it.", "Geography has changed.", "Gravity applied for a raise."]),
        ("Gravity Well",  ["Moons entered orbit.", "The sun looked.", "Physics gave up.", "Earth relocated slightly."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🍑", "Ass Size", name, result, random.choice(punchlines))

# ── Boob Size ────────────────────────────────────────────────────────────────

def gen_boobs(name):
    tiers = [
        ("Flat", ["The ironing board is jealous.", "Minimalist design.", "Aerodynamic build.", "Less is more."]),
        ("Small", ["Cute and compact.", "Pocket edition.", "Still gets appreciation.", "Balanced stats."]),
        ("Medium", ["Perfectly balanced.", "The golden standard.", "Certified classic.", "No complaints detected."]),
        ("Large", ["Back pain entered the chat.", "Definitely noticeable.", "Built with confidence.", "Turning heads daily."]),
        ("Huge", ["Gravity is working overtime.", "The shirt is under pressure.", "Maximum presence.", "Built different."]),
        ("Planetary", ["NASA picked up a signal.", "Physics filed a complaint.", "The measuring tape surrendered.", "Beyond scientific understanding."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🍒", "Boob Size", name, result, random.choice(punchlines))


# ── Braincells ────────────────────────────────────────────────────────────────

def gen_braincells(name):
    tiers = [
        (0,  ["Impressive in a different way.", "The skull is just storage now.", "Running on vibes exclusively.", "The void stares back."]),
        (1,  ["Solitary. Brave. Lost.", "One soldier in an empty field.", "It's doing its best.", "Lone warrior."]),
        (2,  ["They're arguing.", "One is buffering.", "Democracy of two.", "They take shifts."]),
        (5,  ["A small committee.", "Quorum achieved. Barely.", "Majority rules. Usually.", "Progress."]),
        (8,  ["Functioning.", "Getting things done somehow.", "Middle management energy.", "Works in bursts."]),
        (12, ["Solid.", "Dependable. Mostly.", "Runs fine.", "Respectable."]),
        (14, ["Peak performance.", "The limit.", "Science won't allow more.", "Maximum capacity reached."]),
    ]
    n, punchlines = random.choice(tiers)
    return _card("🧠", "Braincells", name, str(n), random.choice(punchlines))


# ── Sigma Meter ───────────────────────────────────────────────────────────────

def gen_sigma(name):
    tiers = [
        ("Negative Sigma",  ["The sigma left and took the wifi.", "Even the NPCs avoid you.", "Anti-sigma energy.", "Sigma in reverse."]),
        ("Beta",            ["The group chat on mute.", "Replies with 'k'.", "Agrees with everything.", "Conflict avoidance champion."]),
        ("NPC",             ["Dialogue: 'Strange weather lately.'", "Repeating the same route since 2019.", "Quest unavailable.", "Ambient background character."]),
        ("Average",         ["Exists. Successfully.", "Mid sigma. Comfortable.", "Sigma loading.", "Getting there."]),
        ("Sigma",           ["Moves different.", "No explanation needed.", "The room felt it.", "Certified."]),
        ("Ultra Sigma",     ["Rejected gravity once.", "Eye contact closed a deal.", "Silent. Winning.", "The algorithm fears this."]),
        ("Gigachad",        ["Statues were erected.", "The sigma peaked.", "Scientists studying this.", "Beyond measurement."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🗿", "Sigma Meter", name, result, random.choice(punchlines))


# ── Rizz Score ────────────────────────────────────────────────────────────────

def gen_rizz(name):
    tiers = [
        ("No Rizz",       ["Tried. It didn't.", "The rejection was fast.", "Even autocorrect gave up.", "Boldly unsuccessful."]),
        ("Dry",           ["The vibe left first.", "Conversation: painful.", "They're still cringing.", "Cactus energy."]),
        ("Average",       ["Sometimes it works.", "Hit or miss.", "Chaotic neutral rizz.", "Decent attempt."]),
        ("Smooth",        ["Went well.", "Kept it together.", "Solid delivery.", "The person smiled."]),
        ("Elite",         ["Effortless.", "They texted first.", "The rizz was unspoken.", "Dangerous levels."]),
        ("Infinite Rizz", ["Walls confessed.", "The sky apologized.", "NPCs proposed.", "Illegal in 4 countries."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("😎", "Rizz Score", name, result, random.choice(punchlines))


# ── Dick Size ────────────────────────────────────────────────────────────────

def gen_dick(name):
    tiers = [
        ("Microscopic", ["Scientists need better equipment.", "Lost in the laundry.", "Needs a GPS to locate.", "Practically theoretical."]),
        ("Small", ["Gets the job... maybe.", "Compact edition.", "Travel-sized.", "Built for efficiency."]),
        ("Average", ["The global standard.", "Nothing to brag or cry about.", "Respectably normal.", "Factory settings."]),
        ("Above Average", ["Got a little bonus.", "Confidence justified.", "Main character energy.", "Solid stats."]),
        ("Huge", ["Jeans fear this individual.", "Gravity is working overtime.", "Built different.", "Certified unit."]),
        ("Legendary", ["Medical journals are interested.", "Physics has questions.", "The measuring tape gave up.", "Beyond human comprehension."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("📏", "Dick Size", name, result, random.choice(punchlines))


# ── Aura ──────────────────────────────────────────────────────────────────────

def gen_aura(name):
    tiers = [
        ("-100,000 Aura",    ["The Wi-Fi disconnects first.", "Plants apologized and left.", "The vibe check bounced.", "Negative aura record."]),
        ("Negative Aura",    ["The room got quieter.", "People checked their phones.", "Candles went out.", "The energy left."]),
        ("No Aura",          ["Invisible to the algorithm.", "Exists. Barely.", "Aura: pending.", "Mid presence."]),
        ("Mid Aura",         ["Some people noticed.", "Present. Acknowledged.", "The room felt something.", "Neutral impact."]),
        ("Strong Aura",      ["The energy shifted.", "People looked twice.", "Presence felt.", "The algorithm boosted it."]),
        ("Main Character Aura",["The BGM started.", "Everyone's a side character now.", "Camera follows you.", "Narrative selected."]),
        ("Infinite Aura",    ["The laws of physics adjusted.", "History paused.", "Stars acknowledged.", "Biblically felt."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("✨", "Aura", name, result, random.choice(punchlines))


# ── Aura Lost ─────────────────────────────────────────────────────────────────

def gen_aura_lost(name):
    lost = random.randint(0, 999999)
    tiers_low  = ["Doing fine actually.", "Minor losses only.", "Recoverable.", "Still standing."]
    tiers_mid  = ["The cringe is real.", "Multiple incidents.", "It adds up.", "Documented losses."]
    tiers_high = ["Cannot be recovered.", "The losses are historical.", "Scientists are studying this.", "Generational damage."]
    if lost < 10000:   punchline = random.choice(tiers_low)
    elif lost < 100000: punchline = random.choice(tiers_mid)
    else:               punchline = random.choice(tiers_high)
    return _card("🥶", "Aura Lost", name, f"-{lost:,}", punchline)


# ── Delulu Index ──────────────────────────────────────────────────────────────

def gen_delulu(name):
    tiers = [
        ("Mentally Stable",   ["Boring but respected.", "Grounded. Unfortunately.", "Logic-based existence.", "Facts only."]),
        ("Slightly Delulu",   ["Manifesting on a budget.", "Hopeful. Barely.", "The delulu is warming up.", "Optimistic liar."]),
        ("Dangerously Delulu",["They genuinely believe it.", "Reality is negotiable.", "The manifestation board is full.", "Concerning but entertaining."]),
        ("Maximum Delulu",    ["Sent a letter to their celebrity crush.", "Expecting a callback.", "The vision board has a vision board.", "Delusional excellence."]),
        ("Beyond Reality",    ["Transcended logic.", "Physics doesn't apply.", "The delulu is the solulu.", "Cannot be reached by facts."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🌸", "Delulu Index", name, result, random.choice(punchlines))


# ── Nigga Pass ────────────────────────────────────────────────────────────────

def gen_niggapass(name):
    tiers = [
        ("Denied", ["Application rejected.", "Security said 'not today.'", "Needs more street credits.", "Try again next season."]),
        ("Temporary Pass", ["Valid until someone questions it.", "Proceed with caution.", "Under observation.", "Don't get too comfortable."]),
        ("Neighborhood Approved", ["The locals know you.", "Respect earned.", "Can hang around.", "Certified familiar face."]),
        ("Block Certified", ["The whole block vouches.", "Street approval granted.", "No questions asked.", "Officially accepted."]),
        ("Nigga Legend", ["Everyone knows the name.", "Respect is automatic.", "The streets remember.", "Neighborhood icon."]),
        ("Mayor of the Niggas", ["Owns the block spiritually.", "Local legend status achieved.", "Even the OGs salute.", "Maximum street reputation."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🧢", "Nigga Pass", name, result, random.choice(punchlines))

# ── Red Flag ──────────────────────────────────────────────────────────────────

def gen_red_flag(name):
    counts = [0, 1, 2, 3, 5, 7, 11, 17, "∞"]
    jokes_low  = ["Clean record.", "Suspicious but okay.", "Minor concerns only.", "One flag is fine. Apparently."]
    jokes_mid  = ["Proceed with caution.", "The flags are visible.", "Run.", "The flags waved."]
    jokes_high = ["The flags have flags.", "The parade has started.", "Whole wardrobe is red.", "The UN is involved."]
    count = random.choice(counts)
    if count in [0, 1]:     punchline = random.choice(jokes_low)
    elif count in [2, 3, 5]: punchline = random.choice(jokes_mid)
    else:                    punchline = random.choice(jokes_high)
    return _card("🚩", "Red Flag Count", name, str(count), punchline)


# ── Green Flag ────────────────────────────────────────────────────────────────

def gen_green_flag(name):
    tiers = [
        ("None Detected",    ["Disappointing.", "The search continues.", "Zero confirmed.", "Results: bleak."]),
        ("Barely Any",       ["One. Maybe.", "Looking hard.", "There's potential.", "Found one. Fragile."]),
        ("A Few",            ["Progress.", "Worth considering.", "Signs of life.", "Not terrible."]),
        ("Solid",            ["Dependable.", "Actually texts back.", "Respects boundaries.", "Rare find."]),
        ("Very Green",       ["Certified.", "Screenshotworthy.", "Save this one.", "The gold standard."]),
        ("Genuinely Perfect",["Suspicious actually.", "Too good. Verify.", "Scientists are skeptical.", "Background check recommended."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("💚", "Green Flag", name, result, random.choice(punchlines))


# ── Luck ──────────────────────────────────────────────────────────────────────

def gen_luck(name):
    tiers = [
        ("Cursed",        ["Don't leave the house.", "The universe said no.", "Avoid tall objects.", "Stay in bed."]),
        ("Unlucky",       ["Minor disasters incoming.", "Check your surroundings.", "The odds aren't it.", "Something will go wrong."]),
        ("Average",       ["Neutral day.", "Nothing spectacular.", "Fine. Whatever.", "Exists without incident."]),
        ("Lucky",         ["Things might work out.", "Buy a scratch card.", "The stars are considering it.", "Green light day."]),
        ("Blessed",       ["Universe said yes.", "Everything lands.", "Golden day.", "The algorithm is on your side."]),
        ("God's Favorite",["Untouchable.", "The RNG maxed out.", "Born different.", "Suspiciously fortunate."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🍀", "Luck Today", name, result, random.choice(punchlines))


# ── Broke Meter ───────────────────────────────────────────────────────────────

def gen_broke(name):
    tiers = [
        ("Homeless",     ["The pigeons judged.", "Wallet: spiritually empty.", "Negative balance achieved.", "Bank closed the account for safety."]),
        ("Broke",        ["Eating crackers strategically.", "Card declined at the dollar store.", "Borrowing from future self.", "Survival mode."]),
        ("Surviving",    ["Enough for ramen.", "Month-to-month champion.", "One bill away.", "Stable. Barely."]),
        ("Comfortable",  ["Pays bills on time.", "Occasionally treats self.", "Healthy relationship with money.", "Doing fine."]),
        ("Rich",         ["Comfortable flex.", "Doesn't check the price.", "The good seats.", "Upgraded."]),
        ("Millionaire",  ["Private problems.", "Still complains about prices.", "The jet is maintained.", "Upper tier."]),
        ("Billionaire",  ["Multiple houses. Zero reasons.", "The yacht has a yacht.", "Taxes optional apparently.", "Different species."]),
        ("Oil Prince",   ["The economy adjusts.", "Countries named after them.", "The number has a name.", "Beyond wealth."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("💸", "Broke Meter", name, result, random.choice(punchlines))


# ── Rich Meter ────────────────────────────────────────────────────────────────

def gen_rich(name):
    tiers = [
        ("Financially Deceased", ["RIP bank account.", "The overdraft said hi.", "Spiritually bankrupt.", "Wallet: haunted."]),
        ("Penny Counter",        ["Exact change always.", "Coupon royalty.", "The discount is the reward.", "Math-based survival."]),
        ("Getting By",           ["Expenses: covered. Barely.", "One paycheck ahead.", "The hustle is real.", "Functional poverty."]),
        ("Middle Class",         ["Netflix and stress.", "The vacation was budgeted.", "Coffee shop twice a week.", "Comfortable anxiety."]),
        ("Doing Well",           ["Savings account: exists.", "The car is new.", "Tipped 20% without pain.", "Stable king/queen."]),
        ("Loaded",               ["Business class unironically.", "The restaurant bill: unbothered.", "Multiple investments.", "Generational energy."]),
        ("Old Money",            ["Has a family crest.", "The house has a name.", "Never discusses money. Has it.", "Ancestry: profitable."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("💰", "Rich Meter", name, result, random.choice(punchlines))


# ── Simp Meter ────────────────────────────────────────────────────────────────

def gen_simp(name):
    tiers = [
        ("Not a Simp",    ["Emotionally unavailable.", "Unbothered.", "Doesn't text first.", "Certified stone."]),
        ("Low Key Simp",  ["Likes their posts immediately.", "Checked their story 4 times.", "It's fine. It's fine.", "Subtle dedication."]),
        ("Mid Simp",      ["Wrote a paragraph reply.", "Watched their story 8 times.", "Said 'no worries' and worried.", "Classic."]),
        ("High Simp",     ["Sent a gift unprompted.", "Defended them in a stranger's comment section.", "The dedication is showing.", "Deeply committed."]),
        ("Certified Simp",["Named their wifi after them.", "The parasocial is mutual now.", "Beyond saving.", "Peak simp. Respect."]),
        ("Simp God",      ["Wrote a thesis.", "Commissioned fan art.", "The stan account is active.", "Achieved enlightenment through simping."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("❤️", "Simp Meter", name, result, random.choice(punchlines))


# ── Wife Material ─────────────────────────────────────────────────────────────

def gen_wife(name):
    tiers = [
        ("Run",           ["Multiple red flags confirmed.", "The prenup has a prenup.", "Lawyers were consulted.", "Love is blind and so are you."]),
        ("Low",           ["Potential exists. Buried.", "With work. A lot of work.", "Possible. Statistically.", "Hope is not a plan."]),
        ("Average",       ["Gets the job done.", "Standard package.", "Has their moments.", "Acceptable."]),
        ("Good Catch",    ["Communicates. Rare.", "Actually listens.", "Remembers the small things.", "Certified keeper."]),
        ("Premium",       ["Scientists are studying this.", "Too good to be real.", "Verify before proceeding.", "Background check: passed."]),
        ("Legendary",     ["Poets will write about this.", "The standard everyone else failed.", "Once in a civilization.", "The benchmark."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("💍", "Wife Material", name, result, random.choice(punchlines))


# ── Husband Material ──────────────────────────────────────────────────────────

def gen_husband(name):
    tiers = [
        ("Flee",          ["Left for milk once. Still out.", "The red flags have red flags.", "Emotional availability: 0%.", "The wedding planner refunded."]),
        ("Work in Progress",["Potential. Maybe.", "Needs calibration.", "Promising but unfinished.", "Possible with patience."]),
        ("Average",       ["Shows up. Usually.", "Remembered the anniversary. Once.", "Mid husband energy.", "Functional."]),
        ("Solid",         ["Actually communicates.", "Plans things in advance.", "Knows the anniversary unprompted.", "Dependable king."]),
        ("Elite",         ["Fixed things without being asked.", "Remembers her coffee order.", "Listening: certified.", "Rare species."]),
        ("Peak Husband",  ["Myths are told about this.", "The standard others failed.", "Poets wept.", "Irreplaceable."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🤵", "Husband Material", name, result, random.choice(punchlines))


# ── NPC Meter ─────────────────────────────────────────────────────────────────

def gen_npc(name):
    tiers = [
        ("100% NPC",       ["Dialogue: 'Strange weather lately.'", "Same route since 2007.", "Quest unavailable.", "Respawns at the same coffee shop."]),
        ("Mostly NPC",     ["Has one repeated line.", "The backstory is thin.", "Low polygon emotions.", "Follows the script."]),
        ("Background NPC", ["Present. Unimportant.", "Fills the scene.", "No arc detected.", "Side character energy."]),
        ("Quest NPC",      ["Has information. Won't share.", "Objective: unclear.", "Part of the story. Barely.", "The hint system."]),
        ("Semi-Conscious", ["Shows signs of independent thought.", "Occasionally deviates from script.", "Emerging from NPC-ness.", "Progress."]),
        ("Player Character",["Has a quest. Has an arc.", "Makes choices. Lives with them.", "Main character energy.", "The game is about them."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🧍", "NPC Meter", name, result, random.choice(punchlines))


# ── Clown Meter ───────────────────────────────────────────────────────────────

def gen_clown(name):
    tiers = [
        ("Not a Clown",      ["Completely normal. Boring.", "Zero clown detected.", "Grounded. Unfortunately.", "Plain."]),
        ("Clown in Training",["Occasional clown behavior.", "The honk is quiet.", "Beginning stages.", "The red nose is forming."]),
        ("Certified Clown",  ["The honk is real.", "Professionally unserious.", "The shoes are enormous.", "Hired for events."]),
        ("Senior Clown",     ["Years of experience.", "The chaos is practiced.", "The circus asked for a raise.", "Career clown."]),
        ("Head Clown",       ["Leads the clowns.", "The circus obeys.", "The biggest shoes.", "Legendary fool."]),
        ("Clown Overlord",   ["The clown car has a clown car.", "Infinite honks.", "The Big Top bows.", "Clownmaxxing achieved."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🤡", "Clown Meter", name, result, random.choice(punchlines))


# ── Rat Meter ─────────────────────────────────────────────────────────────────

def gen_rat(name):
    tiers = [
        ("No Rat",      ["Loyalty: verified.", "Passed the test.", "Zero leaks detected.", "Solid."]),
        ("Slight Rat",  ["Told one person. Just one.", "The secret is almost safe.", "Minor leak.", "Mostly trustworthy."]),
        ("Mid Rat",     ["Mentioned it casually.", "The details slipped.", "Technically didn't lie.", "Grey area."]),
        ("Big Rat",     ["The whole group knows now.", "It came out in conversation.", "The cap was detected.", "Spilled everything."]),
        ("Certified Rat",["Told the group chat.", "Posted about it.", "The victim found out from a stranger.", "Peak rat energy."]),
        ("King Rat",    ["Sold the information.", "Went to the other side.", "History judged this.", "Legendary betrayal."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🐀", "Rat Meter", name, result, random.choice(punchlines))


# ── Goblin DNA ────────────────────────────────────────────────────────────────

def gen_goblin(name):
    pcts = list(range(0, 101, 5))
    pct = random.choice(pcts)
    if pct < 25:
        punchlines = ["Disturbingly normal.", "Human. Almost.", "The goblin is dormant.", "Mostly civilized."]
    elif pct < 60:
        punchlines = ["Snack hoarding detected.", "The nest is messy.", "Prefers dim lighting.", "Goblin tendencies rising."]
    elif pct < 90:
        punchlines = ["Full goblin hours.", "The hoard is impressive.", "Only comes out at night.", "Certified goblin behavior."]
    else:
        punchlines = ["Pure goblin.", "The caves called.", "Society is optional.", "Goblinmaxxed."]
    return _card("🧬", "Goblin DNA", name, f"{pct}%", random.choice(punchlines))


# ── Alien DNA ─────────────────────────────────────────────────────────────────

def gen_alien(name):
    pct = random.randint(0, 100)
    if pct < 20:
        p = ["Fully human. Unfortunately.", "Zero anomalies.", "Disappointingly normal.", "Earth native confirmed."]
    elif pct < 50:
        p = ["Slightly off.", "Minor anomalies detected.", "Something is different.", "Not quite human."]
    elif pct < 80:
        p = ["Area 51 has a file.", "Communicates via vibes.", "The mothership called.", "Cannot be explained."]
    else:
        p = ["Not from here.", "The disguise is failing.", "They want you back.", "The scan said 'ERROR'."]
    return _card("👽", "Alien DNA", name, f"{pct}%", random.choice(p))


# ── Monkey DNA ────────────────────────────────────────────────────────────────

def gen_monkey(name):
    pct = random.randint(5, 98)
    if pct < 30:
        p = ["Almost human.", "Minimal primate behavior.", "The evolution is mostly done.", "Respectable."]
    elif pct < 60:
        p = ["Cannot resist a spinning chair.", "Territorial over snacks.", "The banana was not optional.", "Progress has stalled."]
    elif pct < 85:
        p = ["The zoo called.", "Climbs things unprovoked.", "The screeching is frequent.", "Returning to nature."]
    else:
        p = ["Fully reverted.", "The trees are calling.", "Evolution said never mind.", "Pure primate."]
    return _card("🐒", "Monkey DNA", name, f"{pct}%", random.choice(p))


# ── IQ Meter ──────────────────────────────────────────────────────────────────

def gen_iq(name):
    iq = random.randint(1, 300)
    if iq < 50:
        p = ["Googled how to Google.", "The tutorial was too hard.", "Fought a wall. Lost.", "Bravely unaware."]
    elif iq < 100:
        p = ["Gets the joke eventually.", "Functioning. Slowly.", "The math is mathing.", "Close enough."]
    elif iq < 150:
        p = ["Solid.", "Thinks before speaking. Sometimes.", "Above average thinker.", "Respectable."]
    elif iq < 200:
        p = ["Concerning amounts of intelligence.", "Overthinks everything.", "Big brain, small patience.", "Nerd detected."]
    else:
        p = ["Incomprehensible.", "Speaks in theorems.", "Scientists are nervous.", "Left the simulation."]
    return _card("🧠", "IQ Meter", name, str(iq), random.choice(p))


# ── Nerd Meter ────────────────────────────────────────────────────────────────

def gen_nerd(name):
    tiers = [
        ("Not a Nerd",    ["Cool. Confirmed.", "Zero nerd energy.", "Socially calibrated.", "Passes the vibe check."]),
        ("Casual Nerd",   ["Watches one sci-fi show.", "Owns a funko pop ironically.", "Knows some facts.", "Nerd lite."]),
        ("Mid Nerd",      ["Has opinions about lore.", "The wiki edits are frequent.", "Wears it proudly.", "Invested."]),
        ("Mega Nerd",     ["The trivia is a weapon.", "Corrects teachers.", "The collection is extensive.", "Power nerd."]),
        ("Supreme Nerd",  ["Wrote fan fiction about physics.", "Has a tier list of tier lists.", "The debate record is undefeated.", "Nerd royalty."]),
        ("Nerd God",      ["Transcended human knowledge.", "The library cried.", "Cannot be defeated in facts.", "Beyond mortal nerding."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🤓", "Nerd Meter", name, result, random.choice(punchlines))


# ── Gamer Meter ───────────────────────────────────────────────────────────────

def gen_gamer(name):
    tiers = [
        ("Doesn't Game",    ["Touched grass. Voluntarily.", "Controller is dusty.", "Has a life. Allegedly.", "The betrayal."]),
        ("Casual Gamer",    ["Mobile only.", "Plays Wordle.", "Story mode. Easy.", "Gamer-adjacent."]),
        ("Mid Gamer",       ["1000 hours in one game.", "Has opinions about graphics.", "Lost sleep to ranked.", "Dedicated."]),
        ("Competitive",     ["Has a gaming chair.", "The teammates are always the problem.", "Rage quit once. Today.", "Ranked sufferer."]),
        ("Cracked",         ["The aim is suspicious.", "Frame-perfect timing.", "The opposition reported.", "Unnatural skill."]),
        ("God Tier",        ["Pros study their footage.", "The controller feared them.", "The world record is theirs.", "Peak gaming achieved."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🎮", "Gamer Meter", name, result, random.choice(punchlines))


# ── Sleep Schedule ────────────────────────────────────────────────────────────

def gen_sleep(name):
    tiers = [
        ("Functioning Human",  ["8 hours. Consistently.", "The schedule is respected.", "Goes to bed before midnight.", "Suspicious."]),
        ("Slightly Off",       ["11pm most nights.", "Wakes up tired.", "The routine is loosening.", "Holding on."]),
        ("Nocturnal",          ["2am is the new 10pm.", "Morning is theoretical.", "Alarm: ignored.", "Night owl confirmed."]),
        ("What Is Sleep",      ["4am routine.", "The sun is an enemy.", "Dreams: unlocked occasionally.", "Sleep deprived but consistent."]),
        ("Completely Inverted",["Awake when birds sleep.", "The birds judge.", "Asleep during daylight.", "Separate timezone."]),
        ("Sleep Is a Myth",    ["Has not confirmed sleep's existence.", "Running on spite.", "Doctors are concerned.", "Transcended rest."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("😴", "Sleep Schedule", name, result, random.choice(punchlines))


# ── Bed Rot Meter ─────────────────────────────────────────────────────────────

def gen_bedrot(name):
    hrs = random.randint(0, 23)
    if hrs < 4:
        p = ["Productive. Disturbing.", "Out in the world. Why.", "Suspicious activity.", "Grass was touched."]
    elif hrs < 8:
        p = ["Normal rest.", "Recovering.", "The bed was visited.", "Healthy-ish."]
    elif hrs < 14:
        p = ["The bed accepted them.", "Horizontal lifestyle.", "The sheets know everything.", "Committed."]
    elif hrs < 20:
        p = ["The bed IS the life.", "The groceries are delivered.", "Movement: optional.", "Peak bed rot."]
    else:
        p = ["The mattress has absorbed them.", "Legally a fixture.", "The bed says thank you.", "One with the pillow."]
    return _card("🛏️", "Bed Rot Meter", name, f"{hrs} hours in bed today", random.choice(p))


# ── Shower Needed Meter ───────────────────────────────────────────────────────

def gen_shower(name):
    days = random.randint(0, 14)
    if days == 0:
        p = ["Fresh. Verified.", "Responsible hygiene.", "Soap was involved.", "Clean confirmed."]
    elif days < 2:
        p = ["Yesterday. Fine.", "Within acceptable range.", "Still passing.", "Manageable."]
    elif days < 5:
        p = ["People are noticing.", "The deodorant is carrying.", "Extended dry run.", "Concerning."]
    elif days < 10:
        p = ["The air around them has texture.", "Plants wilted.", "The Wi-Fi disconnected.", "Historical."]
    else:
        p = ["A biohazard event.", "The shower filed a missing person report.", "Archaeologists are interested.", "Legendary."]
    return _card("🧼", "Shower Needed", name, f"{days} days", random.choice(p))


# ── McDonald's Addiction ──────────────────────────────────────────────────────

def gen_mcdonalds(name):
    mains  = ["McDouble", "Big Mac", "Quarter Pounder", "McChicken", "10pc McNuggets", "McRib", "Filet-O-Fish"]
    sides  = ["large fries", "medium fries", "hash browns", "apple slices (delusional)"]
    drinks = ["large Coke", "McFlurry", "sweet tea", "Sprite", "water (bold choice)"]
    jokes  = [
        "The loyalty card has loyalty cards.",
        "The cashier knows their name.",
        "The drive-thru said 'welcome back'.",
        "McDonald's wrote them in the will.",
        "The app crashed from their orders.",
        "Ronald McDonald sent a personal invite.",
        "The calorie count is classified.",
    ]
    order = f"{random.choice(mains)}, {random.choice(sides)}, {random.choice(drinks)}"
    return _card("🍔", "McDonald's Order", name, order, random.choice(jokes))


# ── Screen Time ───────────────────────────────────────────────────────────────

def gen_screen(name):
    hrs = round(random.uniform(1, 20), 1)
    apps = ["TikTok", "Instagram", "YouTube", "Discord", "Reddit", "Telegram", "Twitter/X", "Pinterest", "BeReal (ironic)"]
    if hrs < 4:
        p = ["Touching grass apparently.", "Functional member of society.", "Suspicious low usage.", "The outdoors happened."]
    elif hrs < 8:
        p = ["Normal range. Allegedly.", "The screen is a lifestyle.", "Expected numbers.", "Standard operation."]
    elif hrs < 12:
        p = ["The screen raised them.", "Concerning but relatable.", "The eyes are red.", "Life: digital."]
    else:
        p = ["The phone is an organ.", "Screen time: a personality.", "What is outside.", "One with the device."]
    return _card("📱", "Screen Time", name, f"{hrs}h on {random.choice(apps)}", random.choice(p))


# ── Aim Accuracy ──────────────────────────────────────────────────────────────

def gen_aim(name):
    tiers = [
        ("0%",         ["Missed the wall.", "The bullet apologized.", "The reticle is decorative.", "Shooting as a concept failed."]),
        ("12%",        ["Hit something adjacent.", "The area was damaged.", "Close. Spiritually.", "The aim is creative."]),
        ("37%",        ["Occasional success.", "The body count is mixed.", "Hit or miss.", "Statistical charity."]),
        ("64%",        ["Decent.", "Above chaos.", "Works in a pinch.", "Reliable enough."]),
        ("89%",        ["Sharp.", "The crosshair obeys.", "Enemies are concerned.", "Trained."]),
        ("100%",       ["The bullets find them.", "Unfair according to the enemy.", "The aim is a crime.", "Reported 4 times."]),
        ("404% (???)", ["Physics opted out.", "The game had questions.", "Broke the hitbox.", "Suspicious accuracy."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🎯", "Aim Accuracy", name, result, random.choice(punchlines))


# ── Fight Win Chance ──────────────────────────────────────────────────────────

def gen_fight(name):
    tiers = [
        ("0%",      ["Would trip walking to the fight.", "The opponent laughed.", "Packed their own ambulance.", "Bravely unsuccessful."]),
        ("15%",     ["Showed up. Points for that.", "Got one hit in.", "Moral victory.", "Tried."]),
        ("35%",     ["Competitive.", "Could have gone either way.", "Left an impression.", "Respectable loss."]),
        ("60%",     ["Usually wins.", "Calibrated aggression.", "The odds were there.", "Solid record."]),
        ("85%",     ["The opponent reconsidered.", "Fight didn't last long.", "Trained different.", "The rep precedes them."]),
        ("100%",    ["Undefeated.", "The fight found them.", "No contest.", "The legend grows."]),
        ("120%",    ["Won a fight that wasn't scheduled.", "The opponent apologized preemptively.", "Extra-legal victory.", "Beyond fighting."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🥊", "Fight Win Chance", name, result, random.choice(punchlines))


# ── Chair Break Chance ────────────────────────────────────────────────────────

def gen_chair(name):
    pct = random.randint(0, 100)
    if pct < 20:
        p = ["Featherweight.", "The chair is safe.", "Furniture breathes easy.", "Light footed."]
    elif pct < 50:
        p = ["The chair is cautious.", "Moderate risk.", "The creak was a warning.", "Manageable."]
    elif pct < 80:
        p = ["The chair has concerns.", "Structural integrity: questioned.", "Extended warranty recommended.", "The screws are stressed."]
    else:
        p = ["The chair prayed.", "The legs gave a statement.", "Engineers warned about this.", "The wood said no."]
    return _card("🪑", "Chair Break Chance", name, f"{pct}%", random.choice(p))


# ── Cooked Meter ──────────────────────────────────────────────────────────────

def gen_cooked(name):
    tiers = [
        ("Raw",          ["Untouched by struggle.", "Life is fine.", "Vibes: intact.", "Comfortable."]),
        ("Slightly Warm",["Something happened.", "Minor incident.", "Recovering.", "The heat is manageable."]),
        ("Medium",       ["The situation is active.", "Ongoing damage.", "It's getting there.", "Mid-cook."]),
        ("Well Done",    ["Fully cooked.", "The damage is thorough.", "No rescue incoming.", "Done."]),
        ("Extra Crispy", ["Beyond saving.", "The smoke alarm gave up.", "Historically cooked.", "Certified crispy."]),
        ("Ash",          ["Nothing remains.", "The chef cried.", "The plate is empty.", "Annihilated."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🔥", "Cooked Meter", name, result, random.choice(punchlines))


# ── Roast Level ───────────────────────────────────────────────────────────────

def gen_roast(name):
    roasts = [
        f"{name} is the human equivalent of buffering.",
        f"{name}'s vibe is an unread email from 2019.",
        f"{name} peaked in a dream they can't remember.",
        f"{name} is what happens when the NPC escapes the tutorial.",
        f"{name}'s personality is a terms and conditions page.",
        f"{name} has the energy of a dying phone at 3%.",
        f"{name} is the reason they put instructions on shampoo.",
        f"{name}'s aura is a warning label.",
        f"{name} is built like a loading screen.",
        f"{name} gives off 'sent a LinkedIn request to their own cousin' energy.",
        f"{name} is the WiFi password that doesn't work.",
        f"{name} has the confidence of an error 404 page.",
        f"{name} is the human version of a software update that makes things worse.",
        f"{name}'s vibe is Microsoft Terms of Service.",
        f"{name} is living proof that some NPCs escape the tutorial.",
        f"{name} is the beige wall of human beings.",
        f"{name} has main character energy in someone else's story.",
        f"{name} is what the algorithm serves at 3am.",
    ]
    endings = [
        "We say this with love.",
        "This is peer reviewed.",
        "The committee agrees.",
        "No notes.",
        "We stand by this.",
        "Screenshotted.",
        "This is facts.",
        "Science confirmed.",
    ]
    roast = random.choice(roasts)
    ending = random.choice(endings)
    body = f"🫵 Roast Level\n\n{name}\n\n{roast}\n\n{ending}"
    return {
        "emoji": "🫵",
        "title": "🫵 Roast Level",
        "preview_title": "🫵 Roast Level",
        "preview_description": f"Tap to roast {name}.",
        "body": body,
    }


# ── Yapper Level ──────────────────────────────────────────────────────────────

def gen_yapper(name):
    words = random.randint(0, 99999)
    if words < 100:
        p = ["Silent type.", "Economy of words.", "Quality over quantity.", "The strong silent type."]
    elif words < 1000:
        p = ["Moderate output.", "Said their piece.", "Measurable.", "Acceptable."]
    elif words < 10000:
        p = ["Active yapper.", "The group chat suffers.", "Volume is a choice.", "Consistent output."]
    else:
        p = ["Olympic yapper.", "Nobody asked. Didn't stop.", "The voice note was 47 minutes.", "Professional yapper. Certified."]
    return _card("🎤", "Yapper Level", name, f"{words:,} words today", random.choice(p))


# ── Touch Book Meter ──────────────────────────────────────────────────────────

def gen_book(name):
    tiers = [
        ("Never",       ["The library is a myth.", "Books: decorative only.", "Reading: theoretical.", "Words: skimmed at best."]),
        ("Rarely",      ["One book. Two years ago.", "Half read, fully claimed.", "The bookmark hasn't moved.", "Selective literacy."]),
        ("Sometimes",   ["Reads occasionally.", "Finishes some.", "Has opinions on some books.", "Casual reader."]),
        ("Often",       ["The bookmarks are used.", "Reads on the commute.", "Goodreads account: active.", "Bookworm in progress."]),
        ("Daily",       ["The shelf is full.", "Library card: worn.", "Reads instead of sleeping.", "Certified reader."]),
        ("Biblically",  ["Reads dictionaries for fun.", "Knows every ISBN.", "The library named a chair after them.", "Ascended reader."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("📚", "Touch Book Meter", name, result, random.choice(punchlines))


# ── Juice Level ───────────────────────────────────────────────────────────────

def gen_juice(name):
    tiers = [
        ("Empty",      ["Completely dry.", "No sauce detected.", "The drip left.", "Running on fumes."]),
        ("Low",        ["Barely any juice.", "Almost out.", "The reserves are thin.", "Rationing."]),
        ("Half",       ["Some juice.", "Enough for now.", "Mid supply.", "Getting by."]),
        ("Full",       ["Well hydrated.", "The juice is real.", "Dripping.", "Loaded."]),
        ("Overflowing",["Cannot contain the juice.", "Dripping on the floor.", "The sauce is uncontrollable.", "Too much juice."]),
        ("Juice God",  ["Made of juice.", "Science studies this.", "The juice became sentient.", "Juiced beyond comprehension."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🧃", "Juice Level", name, result, random.choice(punchlines))


# ── Back Pain Meter ───────────────────────────────────────────────────────────

def gen_back(name):
    tiers = [
        ("No Pain",     ["Yoga-doer energy.", "The spine is intact.", "Stretches regularly.", "Suspicious flexibility."]),
        ("Mild",        ["The back protests quietly.", "Occasional twinge.", "Posture: decent.", "Managing."]),
        ("Moderate",    ["The chair is the enemy.", "Stands up slowly.", "The creak is audible.", "Mid back situation."]),
        ("Severe",      ["The back has opinions.", "Stands like a question mark.", "The mattress is blamed.", "Chronic."]),
        ("Catastrophic",["Can only sit at a 47° angle.", "The physiotherapist has a yacht.", "Walking: negotiated.", "Historical."]),
        ("Generational",["Passed it down already.", "The pain has memories.", "Science studies this spine.", "Ancient back pain."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🦴", "Back Pain Meter", name, result, random.choice(punchlines))


# ── Freedom Meter ─────────────────────────────────────────────────────────────

def gen_freedom(name):
    tiers = [
        ("Imprisoned",      ["The routine has them.", "Cannot leave the schedule.", "The calendar said no.", "Zero autonomy."]),
        ("Restricted",      ["Limited freedom.", "The obligations are real.", "Technically free.", "Constrained."]),
        ("Average Freedom", ["Some choices.", "Freedom: scheduled.", "Gets out sometimes.", "Manages."]),
        ("Free",            ["Makes own decisions.", "The schedule is optional.", "No obligations this week.", "Liberated."]),
        ("Very Free",       ["Answers to no one.", "The schedule is decorative.", "Calendar: empty.", "Untethered."]),
        ("Eagle Energy",    ["Cannot be contained.", "The sky is the baseline.", "The world is the schedule.", "Fully free."]),
    ]
    result, punchlines = random.choice(tiers)
    return _card("🦅", "Freedom Meter", name, result, random.choice(punchlines))


# ── Master list ───────────────────────────────────────────────────────────────

ALL_GENERATORS = [
    gen_gay, gen_ass, gen_braincells, gen_sigma, gen_rizz,
    gen_aura, gen_aura_lost, gen_delulu, gen_dick, gen_red_flag,
    gen_green_flag, gen_luck, gen_broke, gen_rich, gen_simp,
    gen_wife, gen_husband, gen_niggapass, gen_clown, gen_boobs,
    gen_rat, gen_freak, gen_goblin, gen_alien, gen_monkey,
    gen_iq, gen_nerd, gen_gamer, gen_sleep, gen_bedrot,
    gen_shower, gen_gay, gen_mcdonalds, gen_screen, gen_aim,
    gen_fight, gen_chair, gen_cooked, gen_roast, gen_yapper,
    gen_book, gen_juice, gen_back, gen_freedom,
    gen_freak,
]


async def generate_all(name: str) -> list[dict]:
    """
    Generate all cards. Fully random every call — no seeding, no memory.
    Instant. Zero API. Zero AI.
    """
    results = []
    for gen in ALL_GENERATORS:
        try:
            results.append(gen(name))
        except Exception:
            pass
    return results
