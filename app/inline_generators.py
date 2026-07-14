"""
inline_generators.py — 50+ funny Gen Z inline result generators.
Zero AI, zero DB, zero network. Pure Python random. Instant.

Each generator is a function that takes a name (str) and returns a dict:
  {
    "title": str,       # shown in inline result header
    "emoji": str,       # shown as thumbnail
    "body": str,        # full message sent when clicked
  }
"""

import random
import hashlib


def _seed(name: str, salt: str) -> None:
    """Seed random with name + salt so same name gets consistent results per salt."""
    h = int(hashlib.md5(f"{name}{salt}".encode()).hexdigest(), 16)
    random.seed(h)


def _pct(name: str, salt: str, lo: int = 1, hi: int = 100) -> int:
    _seed(name, salt)
    return random.randint(lo, hi)


def _pick(name: str, salt: str, options: list):
    _seed(name, salt)
    return random.choice(options)


# ── Generators ────────────────────────────────────────────────────────────────

def braincells(name: str) -> dict:
    n = _pct(name, "braincells", 0, 14)
    statuses = [
        "Both are arguing with each other.",
        "One is on vacation. The other called in sick.",
        "Currently buffering since 2019.",
        "Last seen: never.",
        "Sold on Craigslist for $3.",
        "They unionized and went on strike.",
        "Tragically lost in a group chat argument.",
        "Running on borrowed time.",
    ]
    status = _pick(name, "braincells_s", statuses)
    return {
        "emoji": "💀",
        "title": f"💀 Braincells Left — {n}",
        "body": f"💀 Braincells Left\n\n{name}'s remaining braincells: {n}\n\nStatus: {status}",
    }


def sigma_meter(name: str) -> dict:
    n = _pct(name, "sigma", 0, 100)
    levels = [
        (90, "Certified sigma. Even the shadows respect you."),
        (70, "Almost sigma. Still orders at the drive-thru though."),
        (50, "Mid sigma. Has a gym membership but hasn't been in 4 months."),
        (30, "Sigma in progress. Currently failing the vibe check."),
        (10, "Beta in sigma clothing. We can see through it."),
        (0, "Negative sigma. The sigma left the chat."),
    ]
    for threshold, desc in levels:
        if n >= threshold:
            break
    return {
        "emoji": "🗿",
        "title": f"🗿 Sigma Meter — {n}%",
        "body": f"🗿 Sigma Meter\n\n{name}'s sigma level: {n}%\n\n{desc}",
    }


def npc_scanner(name: str) -> dict:
    n = _pct(name, "npc", 40, 100)
    reasons = [
        "Replies with 'k' after reading 5 paragraphs.",
        "Has repeated the same daily routine for 7 years.",
        "Laughs at the same joke every time.",
        "Still says 'on my way' when they haven't left yet.",
        "Ambient dialogue only. No quest available.",
        "Walks into walls sometimes.",
        "Respawns at the same coffee shop every morning.",
    ]
    reason = _pick(name, "npc_r", reasons)
    return {
        "emoji": "🤖",
        "title": f"🤖 NPC Scanner — {n}% NPC",
        "body": f"🤖 NPC Scanner\n\n{name} is {n}% NPC.\n\nEvidence: {reason}",
    }


def pp_calculator(name: str) -> dict:
    _seed(name, "pp")
    size = round(random.uniform(0.1, 50.0), 1)
    comments = [
        "Scientists are asking questions.",
        "Physics has filed a complaint.",
        "NASA wants to study this.",
        "The ruler said 'error'.",
        "Confirmed by three independent labs.",
        "This defies the laws of nature.",
        "Doctors are baffled.",
        "String theory cannot explain this.",
    ]
    comment = _pick(name, "pp_c", comments)
    return {
        "emoji": "📏",
        "title": f"📏 PP Calculator™ — {size} cm",
        "body": f"📏 Totally Scientific PP Calculator™\n\n{name}'s result: {size} cm\n\n{comment}",
    }


def gyatt_detector(name: str) -> dict:
    n = _pct(name, "gyatt", 0, 100)
    readings = [
        "The detector needs recalibration.",
        "Seismographs detected movement.",
        "NASA satellites picked up the signal.",
        "Local pedestrians have noticed.",
        "Engineers are concerned about structural integrity.",
        "The detector overheated. Please stand back.",
    ]
    reading = _pick(name, "gyatt_r", readings)
    return {
        "emoji": "🍑",
        "title": f"🍑 Gyatt Detector — {n}%",
        "body": f"🍑 Gyatt Detector\n\n{name}'s gyatt reading: {n}%\n\n{reading}",
    }


def aura_level(name: str) -> dict:
    _seed(name, "aura")
    score = random.randint(-99999, 99999)
    if score < 0:
        reasons = [
            "Even the Wi-Fi disconnects when you enter.",
            "Plants wilt. Candles go out.",
            "Your presence lowered the room's IQ.",
            "Birds fly away. Dogs bark.",
            "The vibe check came back negative.",
        ]
    else:
        reasons = [
            "The room gets brighter when you arrive.",
            "NPCs stop to stare.",
            "Main character energy detected.",
            "The algorithm blessed this one.",
            "Built different. Certified.",
        ]
    reason = _pick(name, "aura_r", reasons)
    return {
        "emoji": "✨",
        "title": f"✨ Aura Score — {score:,}",
        "body": f"✨ Aura Level\n\n{name}'s aura score: {score:,}\n\nReason: {reason}",
    }


def broke_meter(name: str) -> dict:
    n = _pct(name, "broke", 10, 100)
    statuses = [
        "Survival mode activated.",
        "Eats cereal with a fork to save milk.",
        "Calls it 'vintage' instead of 'falling apart'.",
        "Bank account: $3.47 and a loyalty card.",
        "Splits a single nugget with friends.",
        "Netflix password from 2018 still working.",
        "Considers finding a dollar a good day.",
    ]
    status = _pick(name, "broke_s", statuses)
    return {
        "emoji": "💸",
        "title": f"💸 Broke Meter — {n}%",
        "body": f"💸 Broke Meter\n\n{name} is {n}% broke.\n\nStatus: {status}",
    }


def monkey_dna(name: str) -> dict:
    n = _pct(name, "monkey", 20, 99)
    traits = [
        "Eats banana in public without shame.",
        "Climbs things that shouldn't be climbed.",
        "Screeches when Wi-Fi drops.",
        "Territorial over snacks.",
        "Grooms friends in public.",
        "Cannot resist a spinning chair.",
    ]
    trait = _pick(name, "monkey_t", traits)
    return {
        "emoji": "🐒",
        "title": f"🐒 Monkey DNA — {n}%",
        "body": f"🐒 Monkey DNA Analysis\n\n{name}'s monkey DNA: {n}%\n\nKey trait: {trait}",
    }


def alien_dna(name: str) -> dict:
    n = _pct(name, "alien", 5, 95)
    origins = [
        "Possibly from the Andromeda galaxy.",
        "Area 51 has a file on this one.",
        "The mothership called. They want you back.",
        "Communicates via weird hand gestures.",
        "Has never understood human sleeping hours.",
        "Eyes dilate in fluorescent lighting.",
    ]
    origin = _pick(name, "alien_o", origins)
    return {
        "emoji": "👽",
        "title": f"👽 Alien DNA — {n}%",
        "body": f"👽 Alien DNA Scanner\n\n{name}'s alien DNA: {n}%\n\nNote: {origin}",
    }


def mental_age(name: str) -> dict:
    _seed(name, "mental_age")
    age = random.randint(4, 87)
    notes = [
        "Refuses to eat vegetables.",
        "Still laughs at fart jokes.",
        "Goes to bed at 9pm voluntarily.",
        "Forgets why they walked into a room.",
        "Argues with the TV.",
        "Naps are now a personality trait.",
        "Adds 'back in my day' to sentences.",
    ]
    note = _pick(name, "mental_age_n", notes)
    return {
        "emoji": "🧠",
        "title": f"🧠 Mental Age — {age} years old",
        "body": f"🧠 Mental Age Calculator\n\n{name}'s mental age: {age}\n\nEvidence: {note}",
    }


def villain_arc(name: str) -> dict:
    n = _pct(name, "villain", 0, 100)
    stages = [
        (80, "Full villain arc activated. Origin story complete."),
        (60, "Mid villain arc. Still has a redemption option but choosing not to take it."),
        (40, "Villain arc loading. Currently in the brooding phase."),
        (20, "Pre-villain arc. Still has hope. Barely."),
        (0, "No villain arc detected. Painfully normal."),
    ]
    for threshold, desc in stages:
        if n >= threshold:
            break
    return {
        "emoji": "😈",
        "title": f"😈 Villain Arc — {n}%",
        "body": f"😈 Villain Arc Detector\n\n{name}'s villain arc: {n}%\n\n{desc}",
    }


def delulu_index(name: str) -> dict:
    n = _pct(name, "delulu", 0, 100)
    manifestations = [
        "Manifesting a private jet with $12 in their account.",
        "Genuinely believes they're main character.",
        "Makes eye contact and calls it a situationship.",
        "Grounded in reality. Unfortunately.",
        "The delulu is the solulu and they are committed.",
        "Sent a voice note to their celebrity crush. Twice.",
    ]
    manif = _pick(name, "delulu_m", manifestations)
    return {
        "emoji": "🌸",
        "title": f"🌸 Delulu Index — {n}%",
        "body": f"🌸 Delulu Index\n\n{name}'s delulu level: {n}%\n\n{manif}",
    }


def rizz_score(name: str) -> dict:
    n = _pct(name, "rizz", 0, 100)
    verdicts = [
        (90, "Unspoken rizz. Dangerous level. Handle with care."),
        (70, "High rizz. Charming without trying."),
        (50, "Mid rizz. Sometimes it works. Sometimes it really doesn't."),
        (30, "Low rizz. Tripped on the way to say hi."),
        (10, "Rizz in the negatives. Actively repels."),
        (0, "Rizzless. Scientists are studying this case."),
    ]
    for threshold, desc in verdicts:
        if n >= threshold:
            break
    return {
        "emoji": "😎",
        "title": f"😎 Rizz Score — {n}%",
        "body": f"😎 Rizz Score\n\n{name}'s rizz: {n}%\n\n{desc}",
    }


def red_flag_meter(name: str) -> dict:
    n = _pct(name, "redflag", 0, 100)
    flags = [
        "Reads messages and doesn't reply for 6 hours.",
        "Still has their ex's hoodie and 'it's just comfy'.",
        "Goes quiet and says 'I'm fine'.",
        "Brings up their ex unprompted in every conversation.",
        "Love bombs in week one.",
        "Says 'I don't do labels' but texts you 47 times a day.",
        "None detected. Suspicious.",
    ]
    flag = _pick(name, "redflag_f", flags)
    return {
        "emoji": "🚩",
        "title": f"🚩 Red Flag Meter — {n}%",
        "body": f"🚩 Red Flag Meter\n\n{name}'s red flag level: {n}%\n\nFlag detected: {flag}",
    }


def green_flag_meter(name: str) -> dict:
    n = _pct(name, "greenflag", 0, 100)
    traits = [
        "Actually texts back.",
        "Remembers small things you mentioned once.",
        "Apologizes properly and means it.",
        "Has read at least one book this year.",
        "Doesn't start drama before 9am.",
        "Feeds others before themselves.",
        "Checks in just because.",
    ]
    trait = _pick(name, "greenflag_t", traits)
    return {
        "emoji": "💚",
        "title": f"💚 Green Flag Meter — {n}%",
        "body": f"💚 Green Flag Meter\n\n{name}'s green flag level: {n}%\n\nTrait detected: {trait}",
    }


def luck_today(name: str) -> dict:
    import datetime
    today = datetime.date.today().isoformat()
    _seed(name + today, "luck")
    n = random.randint(0, 100)
    outcomes = [
        (90, "The universe is on your side today. Buy a lottery ticket."),
        (70, "Decent luck. That parking spot might actually be open."),
        (50, "Neutral day. Nothing will go terribly wrong. Probably."),
        (30, "Mild misfortune incoming. Don't make big decisions."),
        (10, "Stay inside. Touch nothing. Talk to no one."),
        (0, "Historic bad luck day. We're so sorry."),
    ]
    for threshold, desc in outcomes:
        if n >= threshold:
            break
    return {
        "emoji": "🍀",
        "title": f"🍀 Luck Today — {n}%",
        "body": f"🍀 Daily Luck Reading\n\n{name}'s luck today: {n}%\n\n{desc}",
    }


def billionaire_chance(name: str) -> dict:
    n = _pct(name, "billionaire", 0, 100)
    paths = [
        "Definitely not through hard work.",
        "One viral TikTok away.",
        "Marrying into money is still on the table.",
        "The lottery exists for a reason.",
        "Inheriting it is technically an option.",
        "Starting a religion seems to be working for others.",
        "At this rate: never. But stay positive.",
    ]
    path = _pick(name, "bill_p", paths)
    return {
        "emoji": "💰",
        "title": f"💰 Billionaire Chance — {n}%",
        "body": f"💰 Billionaire Probability\n\n{name}'s chance: {n}%\n\nMost likely path: {path}",
    }


def cooking_skill(name: str) -> dict:
    n = _pct(name, "cooking", 0, 100)
    skills = [
        "Burned water. Twice.",
        "Can make cereal. Sometimes forgets the milk.",
        "Microwave is a personality.",
        "DoorDash platinum member.",
        "Makes one dish really well and serves it at every occasion.",
        "Could open a restaurant. Probably won't.",
        "Gordon Ramsay has personally issued a restraining order.",
    ]
    skill = _pick(name, "cook_s", skills)
    return {
        "emoji": "👨‍🍳",
        "title": f"👨‍🍳 Cooking Skill — {n}%",
        "body": f"👨‍🍳 Cooking Skill Assessment\n\n{name}'s cooking skill: {n}%\n\nNote: {skill}",
    }


def zombie_survival(name: str) -> dict:
    _seed(name, "zombie")
    days = random.randint(0, 847)
    strategies = [
        "Trips over flat ground immediately.",
        "Would stop to take a photo of the zombies.",
        "Offers snacks to negotiate peace.",
        "Already has a bunker. Has had it for years.",
        "Becomes the zombie. Somehow still survives.",
        "Dies on day 1. Gets better.",
        "Leads the survivor camp. Surprisingly.",
    ]
    strategy = _pick(name, "zombie_s", strategies)
    return {
        "emoji": "🧟",
        "title": f"🧟 Zombie Survival — {days} days",
        "body": f"🧟 Zombie Apocalypse Survival\n\n{name} would survive: {days} days\n\nCause: {strategy}",
    }


def touch_grass_counter(name: str) -> dict:
    import datetime
    today = datetime.date.today().isoformat()
    _seed(name + today, "grass")
    n = random.randint(0, 3)
    statuses = [
        "Has not touched grass this year. The grass has moved on.",
        "Touched grass once. Screenshotted it.",
        "Grass touching scheduled for next quarter.",
        "Is grass. Ironically still chronically online.",
    ]
    return {
        "emoji": "🌿",
        "title": f"🌿 Grass Touched Today — {n}x",
        "body": f"🌿 Touch Grass Counter\n\n{name} touched grass today: {n} times\n\n{statuses[n]}",
    }


def nasa_iq(name: str) -> dict:
    _seed(name, "iq")
    iq = random.randint(12, 312)
    notes = [
        "Couldn't find the 'any' key.",
        "Googles how to Google things.",
        "Once outsmarted a door handle.",
        "Reads terms and conditions. Voluntarily.",
        "NASA called. They need help.",
        "Too smart to explain. You wouldn't get it.",
        "The tests keep breaking.",
    ]
    note = _pick(name, "iq_n", notes)
    return {
        "emoji": "🚀",
        "title": f"🚀 NASA IQ — {iq}",
        "body": f"🚀 NASA IQ Test Results\n\n{name}'s IQ: {iq}\n\nNote: {note}",
    }


def marvel_hero(name: str) -> dict:
    heroes = [
        ("Captain Microwave", "Burns food unevenly.", "The 30-second timer."),
        ("The Procrastinator", "Defeats enemies eventually.", "Deadlines."),
        ("WiFi Man", "Speeds up near routers.", "Walls and basements."),
        ("Nap King", "Recharges in 20 minutes flat.", "Alarm clocks."),
        ("The Algorithm", "Knows what you want before you do.", "Ad blockers."),
        ("Battery Saver", "Survives on 3% longer than physics allows.", "Fast chargers."),
        ("Autocorrect", "Changes situations unpredictably.", "Accountability."),
        ("The Overthinker", "Can predict 47 outcomes simultaneously.", "Making decisions."),
    ]
    hero, power, weakness = _pick(name, "marvel", heroes)
    return {
        "emoji": "🦸",
        "title": f"🦸 Marvel Hero — {hero}",
        "body": f"🦸 Marvel Hero Assignment\n\n{name} is: {hero}\n\nPower: {power}\nWeakness: {weakness}",
    }


def dc_villain(name: str) -> dict:
    villains = [
        ("The Snooze Button", "Makes heroes miss everything.", "Urgency."),
        ("Professor Low Battery", "Strikes at 1% remaining.", "Charging cables."),
        ("The Roaming Charges", "Drains resources internationally.", "Wi-Fi."),
        ("Captain Spoiler", "Ruins everything before it starts.", "Headphones."),
        ("The Buffering", "Freezes at the worst moment.", "Good internet."),
        ("Commitment Issues", "Vanishes at the worst time.", "Receipts."),
        ("The Monday", "Returns every 7 days without fail.", "Friday."),
    ]
    villain, power, weakness = _pick(name, "dc", villains)
    return {
        "emoji": "🦹",
        "title": f"🦹 DC Villain — {villain}",
        "body": f"🦹 DC Villain Assignment\n\n{name} is: {villain}\n\nPower: {power}\nWeakness: {weakness}",
    }


def anime_power(name: str) -> dict:
    powers = [
        "Maximum Overthinking Jutsu",
        "Ultimate Bed Rot Form",
        "Infinite Scroll Technique",
        "Zero Accountability Stance",
        "Chronically Online Mode",
        "Selective Hearing Mastery",
        "Last Minute Activation",
        "Main Character Delusion",
        "Ghost Mode: Activated",
        "Chaos Energy Release",
    ]
    power = _pick(name, "anime_p", powers)
    n = _pct(name, "anime_l", 1, 10000)
    return {
        "emoji": "⚡",
        "title": f"⚡ Anime Power — {power}",
        "body": f"⚡ Anime Power Level\n\n{name}'s power: {power}\n\nPower level: {n:,}\n\nThe enemies are shaking.",
    }


def secret_talent(name: str) -> dict:
    talents = [
        "Can identify a song from 0.3 seconds of audio.",
        "Sleeps through any alarm but wakes up 5 minutes before it.",
        "Makes perfect toast without a timer. Every time.",
        "Can parallel park on the first try.",
        "Finishes other people's sentences. Always correctly.",
        "Instinctively knows when the microwave hits 0:01.",
        "Can find anything on Google in under 10 seconds.",
        "Wins every staring contest without trying.",
        "Can fold a fitted sheet properly.",
        "Always picks the fastest checkout line.",
    ]
    talent = _pick(name, "talent", talents)
    return {
        "emoji": "🌟",
        "title": "🌟 Secret Talent",
        "body": f"🌟 Secret Talent Revealed\n\n{name}'s hidden talent:\n\n{talent}\n\nUse this power wisely.",
    }


def biggest_flex(name: str) -> dict:
    flexes = [
        "Once found $20 in an old jacket.",
        "Has 4 bars of signal indoors.",
        "Finishes Netflix shows without getting distracted.",
        "Has a credit score above 300.",
        "Wakes up without an alarm sometimes.",
        "Parallel parked perfectly in front of witnesses.",
        "Got 8 hours of sleep last Thursday.",
        "Read an entire Wikipedia article.",
        "Finished a chapstick before losing it.",
        "Actually replied to emails same day.",
    ]
    flex = _pick(name, "flex", flexes)
    return {
        "emoji": "💪",
        "title": "💪 Biggest Flex",
        "body": f"💪 Biggest Flex Detected\n\n{name}'s biggest flex:\n\n{flex}\n\nRespect.",
    }


def daily_curse(name: str) -> dict:
    import datetime
    today = datetime.date.today().isoformat()
    curses = [
        "Your left earbud will stop working today.",
        "You will stub your toe twice.",
        "Someone will spoil something for you.",
        "Your phone will die at 12%.",
        "You'll send a message to the wrong person.",
        "You will be put on hold for 45 minutes.",
        "Autocorrect will embarrass you publicly.",
        "Your umbrella will be useless when it rains.",
        "You'll think of the perfect comeback 3 hours later.",
        "Your food order will be slightly wrong.",
    ]
    _seed(name + today, "curse")
    curse = random.choice(curses)
    return {
        "emoji": "🪄",
        "title": "🪄 Daily Curse",
        "body": f"🪄 Today's Curse for {name}:\n\n{curse}\n\nWe are so sorry. (We are not sorry.)",
    }


def mcdonalds_order(name: str) -> dict:
    mains = ["McDouble", "Big Mac", "Quarter Pounder", "McChicken", "Filet-O-Fish", "10pc Nuggets", "McRib (it's back)"]
    sides = ["large fries", "medium fries", "apple slices (liar)", "hash brown", "mozzarella sticks"]
    drinks = ["large Coke", "McFlurry", "Hi-C Orange (it's back again)", "large sweet tea", "Sprite", "water (bold choice)"]
    extras = ["extra sauce", "no pickles (coward)", "extra pickles (brave)", "add bacon", "make it a meal x2"]
    main = _pick(name, "mc1", mains)
    side = _pick(name, "mc2", sides)
    drink = _pick(name, "mc3", drinks)
    extra = _pick(name, "mc4", extras)
    return {
        "emoji": "🍔",
        "title": f"🍔 McDonald's Order",
        "body": f"🍔 {name}'s McDonald's Order\n\n{main}\n{side}\n{drink}\n{extra}\n\nTotal: $3.47 before it was $18.99.",
    }


def cat_energy(name: str) -> dict:
    n = _pct(name, "cat", 0, 100)
    traits = [
        "Knocks things off tables for no reason.",
        "Only affectionate at 3am.",
        "Judges everyone silently.",
        "Ignores you then demands attention.",
        "Finds one cardboard box and never leaves.",
        "Hisses when touched unexpectedly.",
        "Absolutely unbothered. Perpetually.",
    ]
    trait = _pick(name, "cat_t", traits)
    return {
        "emoji": "🐱",
        "title": f"🐱 Cat Energy — {n}%",
        "body": f"🐱 Cat Energy Reading\n\n{name}'s cat energy: {n}%\n\nKey trait: {trait}",
    }


def dog_energy(name: str) -> dict:
    n = _pct(name, "dog", 0, 100)
    traits = [
        "Excited to see you every single time.",
        "Will eat literally anything.",
        "Loyal to a fault. Almost concerning.",
        "Gets the zoomies randomly.",
        "Cries when left alone for 10 minutes.",
        "Would befriend anyone with snacks.",
        "Chases things they'll never catch.",
    ]
    trait = _pick(name, "dog_t", traits)
    return {
        "emoji": "🐶",
        "title": f"🐶 Dog Energy — {n}%",
        "body": f"🐶 Dog Energy Reading\n\n{name}'s dog energy: {n}%\n\nKey trait: {trait}",
    }


def gamer_rank(name: str) -> dict:
    ranks = ["Iron IV", "Bronze III", "Silver II", "Gold I", "Platinum", "Diamond", "Master", "Grandmaster", "Challenger", "NPC Difficulty"]
    rank = _pick(name, "gamer_r", ranks)
    stats = [
        "Blames lag for everything.",
        "Has a 'pro setup' and still loses.",
        "Tilts after one bad game.",
        "Actually cracked. Suspiciously.",
        "Their teammates are always the problem.",
        "Has rage quit at least once today.",
        "Toxic in chat. Somehow still in ranked.",
    ]
    stat = _pick(name, "gamer_s", stats)
    return {
        "emoji": "🎮",
        "title": f"🎮 Gamer Rank — {rank}",
        "body": f"🎮 Gamer Rank Assessment\n\n{name}'s rank: {rank}\n\nNote: {stat}",
    }


def bed_rot(name: str) -> dict:
    n = _pct(name, "bedrot", 20, 100)
    levels = [
        (90, "Professional bed rotter. Has a system."),
        (70, "Advanced stage. The bed has absorbed them."),
        (50, "Moderate bed rot. Gets up for snacks."),
        (30, "Recreational bed rotter. Still functional."),
        (0, "Goes outside voluntarily. We don't trust this."),
    ]
    for threshold, desc in levels:
        if n >= threshold:
            break
    return {
        "emoji": "🛏️",
        "title": f"🛏️ Bed Rot % — {n}%",
        "body": f"🛏️ Bed Rot Assessment\n\n{name}'s bed rot level: {n}%\n\n{desc}",
    }


def coffee_addiction(name: str) -> dict:
    _seed(name, "coffee")
    cups = random.randint(0, 12)
    stages = [
        "Doesn't drink coffee. Some kind of alien.",
        "One cup. Barely a coffee drinker. Baby.",
        "Normal range. Functional.",
        "Getting concerning.",
        "The coffee is a personality now.",
        "Their blood type is espresso.",
        "Doctors are worried. They ordered another cup.",
    ]
    idx = min(cups // 2, len(stages) - 1)
    return {
        "emoji": "☕",
        "title": f"☕ Coffee Addiction — {cups} cups/day",
        "body": f"☕ Coffee Addiction Report\n\n{name} drinks: {cups} cups/day\n\nDiagnosis: {stages[idx]}",
    }


def main_character_energy(name: str) -> dict:
    n = _pct(name, "mainchar", 0, 100)
    signs = [
        "Narrates their own life internally.",
        "Has a 'montage song' ready for any situation.",
        "Walks slower when a good song plays.",
        "Thinks strangers are watching their story arc.",
        "Every obstacle is 'part of their journey'.",
        "Has given themselves a character arc this year.",
        "Wears sunglasses more than necessary.",
    ]
    sign = _pick(name, "mc_s", signs)
    return {
        "emoji": "🎬",
        "title": f"🎬 Main Character Energy — {n}%",
        "body": f"🎬 Main Character Energy\n\n{name}'s level: {n}%\n\nSigns: {sign}",
    }


def chaos_energy(name: str) -> dict:
    n = _pct(name, "chaos_e", 0, 100)
    manifestations = [
        "Sends voice notes instead of typing.",
        "Rearranges furniture at midnight.",
        "Makes impulsive decisions and thrives.",
        "Their plans never make sense but somehow work.",
        "Starts four projects and finishes none.",
        "Says 'what's the worst that could happen' genuinely.",
        "Ordered something random and it became their favourite.",
    ]
    manif = _pick(name, "chaos_m", manifestations)
    return {
        "emoji": "🌀",
        "title": f"🌀 Chaos Energy — {n}%",
        "body": f"🌀 Chaos Energy Scan\n\n{name}'s chaos energy: {n}%\n\nManifestation: {manif}",
    }


def brainrot_meter(name: str) -> dict:
    n = _pct(name, "brainrot", 0, 100)
    symptoms = [
        "Says 'skibidi' unironically.",
        "Understands every meme format from 2019-present.",
        "Cannot explain things without a reference.",
        "Communicates primarily in reaction images.",
        "Has a TikTok sound for every situation.",
        "Their entire vocabulary is from the internet.",
        "Forgot what sunlight looks like.",
    ]
    symptom = _pick(name, "brainrot_s", symptoms)
    return {
        "emoji": "🧠",
        "title": f"🧠 Brainrot Meter — {n}%",
        "body": f"🧠 Brainrot Level\n\n{name}'s brainrot: {n}%\n\nSymptom: {symptom}",
    }


def professional_yapper(name: str) -> dict:
    n = _pct(name, "yapper", 0, 100)
    _seed(name, "yapper_w")
    words = random.randint(500, 50000)
    topics = [
        "things nobody asked about",
        "their situationship",
        "why their opinion is correct",
        "that one thing that happened in 2019",
        "their very specific grievances",
        "the plot of a show nobody watched",
    ]
    topic = _pick(name, "yapper_t", topics)
    return {
        "emoji": "🗣️",
        "title": f"🗣️ Professional Yapper — {n}%",
        "body": f"🗣️ Yapper Certification\n\n{name}'s yapper level: {n}%\n\nWords spoken today: {words:,}\nMainly about: {topic}",
    }


def drama_magnet(name: str) -> dict:
    n = _pct(name, "drama", 0, 100)
    sources = [
        "Drama finds them. They don't look for it.",
        "Was just standing there. Drama arrived anyway.",
        "Started drama by existing in a room.",
        "Active drama creator. Has a schedule.",
        "Neutral party somehow always involved.",
        "The drama called. They said 'finally'.",
    ]
    source = _pick(name, "drama_s", sources)
    return {
        "emoji": "🎭",
        "title": f"🎭 Drama Magnet — {n}%",
        "body": f"🎭 Drama Magnet Index\n\n{name}'s drama attraction: {n}%\n\nPattern: {source}",
    }


def sleep_debt(name: str) -> dict:
    _seed(name, "sleep")
    hours = random.randint(0, 847)
    advice = [
        "No amount of sleep will fix this.",
        "A three-day coma might help.",
        "Consider hibernation.",
        "The circles under the eyes have circles.",
        "Sleep is a distant memory.",
        "Doctors suggest immediate bed rest.",
        "Running purely on spite and caffeine.",
    ]
    adv = _pick(name, "sleep_a", advice)
    return {
        "emoji": "😴",
        "title": f"😴 Sleep Debt — {hours} hours owed",
        "body": f"😴 Sleep Debt Calculator\n\n{name} owes sleep: {hours} hours\n\nAdvice: {adv}",
    }


def goblin_meter(name: str) -> dict:
    n = _pct(name, "goblin", 0, 100)
    behaviors = [
        "Hoards pens that don't work.",
        "Eats snacks in bed unrepentantly.",
        "Has a corner of 'stuff' that nobody touches.",
        "Picks up shiny things.",
        "Prefers dim lighting for no reason.",
        "Makes a nest and defends it.",
        "Communicates in grunts before 10am.",
    ]
    behavior = _pick(name, "goblin_b", behaviors)
    return {
        "emoji": "👺",
        "title": f"👺 Goblin Meter — {n}%",
        "body": f"👺 Goblin Level Assessment\n\n{name}'s goblin level: {n}%\n\nBehavior: {behavior}",
    }


def meme_addiction(name: str) -> dict:
    n = _pct(name, "meme", 0, 100)
    _seed(name, "meme_c")
    count = random.randint(50, 9999)
    symptoms = [
        "Thinks in meme formats.",
        "Cannot respond without an image attached.",
        "Has a meme for every possible situation.",
        "Organizes memes by emotional category.",
        "Sends memes instead of saying good morning.",
        "Their camera roll is 94% memes.",
    ]
    symptom = _pick(name, "meme_s", symptoms)
    return {
        "emoji": "😂",
        "title": f"😂 Meme Addiction — {n}%",
        "body": f"😂 Meme Addiction Report\n\n{name}'s addiction: {n}%\nMemes saved: {count:,}\n\nSymptom: {symptom}",
    }


def keyboard_warrior(name: str) -> dict:
    n = _pct(name, "keyboard", 0, 100)
    moves = [
        "Types aggressively when calm.",
        "Uses ALL CAPS for emphasis at all times.",
        "Has strong opinions about things they've never experienced.",
        "Replies in paragraphs to one-sentence messages.",
        "Never backs down from an internet argument.",
        "Has won zero arguments but hasn't accepted it.",
        "Corrects grammar during emotional conversations.",
    ]
    move = _pick(name, "keyboard_m", moves)
    return {
        "emoji": "⌨️",
        "title": f"⌨️ Keyboard Warrior — {n}%",
        "body": f"⌨️ Keyboard Warrior Level\n\n{name}'s level: {n}%\n\nSignature move: {move}",
    }


def professional_menace(name: str) -> dict:
    n = _pct(name, "menace", 0, 100)
    crimes = [
        "Replies to group chats at 3am.",
        "Puts the milk in before the cereal.",
        "Finishes the last of something and doesn't replace it.",
        "Spoils things casually in passing.",
        "Leaves one bite of food so they 'didn't finish it'.",
        "Talks during movies.",
        "Opens bags from the bottom.",
        "Sends 'k'.",
    ]
    crime = _pick(name, "menace_c", crimes)
    return {
        "emoji": "😤",
        "title": f"😤 Professional Menace — {n}%",
        "body": f"😤 Menace to Society Report\n\n{name}'s menace level: {n}%\n\nRecent crime: {crime}",
    }


def screen_time(name: str) -> dict:
    _seed(name, "screen")
    hours = round(random.uniform(4, 18), 1)
    apps = ["TikTok", "Instagram", "YouTube", "Discord", "Reddit", "Telegram", "Twitter/X", "Pinterest"]
    app = _pick(name, "screen_a", apps)
    verdicts = [
        "Healthy. Suspicious.",
        "Moderate. Lying to yourself but okay.",
        "Concerning. Your eyes are tired.",
        "Alarming. Your phone is your personality.",
        "Critical. You ARE the screen.",
    ]
    idx = min(int(hours / 4), len(verdicts) - 1)
    return {
        "emoji": "📱",
        "title": f"📱 Screen Time — {hours}h",
        "body": f"📱 Screen Time Report\n\n{name}'s daily screen time: {hours} hours\nMost used: {app}\n\nVerdict: {verdicts[idx]}",
    }


def penguin_compatibility(name: str) -> dict:
    n = _pct(name, "penguin", 0, 100)
    reasons = [
        "Would share fish without being asked.",
        "Appreciates tuxedos. A lot.",
        "Slides on ice recklessly. Kindred spirit.",
        "Has the same energy as a penguin at 8am.",
        "Penguins have reviewed your application and declined.",
        "Honorary penguin. Waddling included.",
        "Would protect the egg. Proven reliable.",
    ]
    reason = _pick(name, "penguin_r", reasons)
    return {
        "emoji": "🐧",
        "title": f"🐧 Penguin Compatibility — {n}%",
        "body": f"🐧 Penguin Compatibility Test\n\n{name}'s compatibility: {n}%\n\nReason: {reason}",
    }


def gremlin_level(name: str) -> dict:
    n = _pct(name, "gremlin", 0, 100)
    behaviors = [
        "Only comes alive after midnight.",
        "Gets fed after midnight. Chaos follows.",
        "Hisses at bright lights.",
        "Has a secret snack stash.",
        "Makes strange noises when happy.",
        "Don't get them wet. Don't ask why.",
        "Tiny. Menacing. Beloved.",
    ]
    behavior = _pick(name, "gremlin_b", behaviors)
    return {
        "emoji": "😈",
        "title": f"😈 Gremlin Level — {n}%",
        "body": f"😈 Gremlin Level\n\n{name}'s gremlin energy: {n}%\n\nBehavior: {behavior}",
    }


def feet_enjoyer(name: str) -> dict:
    n = _pct(name, "feet", 0, 100)
    evidence = [
        "Can identify shoe brands from 200 meters.",
        "Has strong opinions about sandal straps.",
        "The algorithm knows.",
        "No evidence found. Yet.",
        "Suspicious search history. Moving on.",
        "Owns 47 pairs of shoes. 'Just likes options'.",
    ]
    evid = _pick(name, "feet_e", evidence)
    return {
        "emoji": "🦶",
        "title": f"🦶 Feet Enjoyer Level — {n}%",
        "body": f"🦶 Feet Enjoyer Detector\n\n{name}'s level: {n}%\n\nEvidence: {evid}",
    }


def pizza_addiction(name: str) -> dict:
    n = _pct(name, "pizza", 0, 100)
    _seed(name, "pizza_s")
    slices = random.randint(2, 847)
    opinions = [
        "Pineapple on pizza is fine and they'll die on this hill.",
        "Has a favourite pizza place and will not hear alternatives.",
        "Eats cold pizza for breakfast without shame.",
        "Judges people by their pizza order.",
        "Has eaten pizza for three meals in a row.",
        "Knows the exact minute the pizza arrives before the app says.",
    ]
    opinion = _pick(name, "pizza_o", opinions)
    return {
        "emoji": "🍕",
        "title": f"🍕 Pizza Addiction — {n}%",
        "body": f"🍕 Pizza Addiction Report\n\n{name}'s addiction: {n}%\nLifetime slices: {slices:,}\n\nNote: {opinion}",
    }


def certified_goober(name: str) -> dict:
    n = _pct(name, "goober", 0, 100)
    goober_traits = [
        "Trips on flat surfaces regularly.",
        "Laughs at their own jokes before finishing them.",
        "Does the little run when a car lets them cross.",
        "Says 'you too' when a waiter says 'enjoy your meal'.",
        "Waves back at someone who wasn't waving at them.",
        "Falls asleep during movies they suggested.",
        "Absolutely, irreversibly a goober. It's a compliment.",
    ]
    trait = _pick(name, "goober_t", goober_traits)
    return {
        "emoji": "🤪",
        "title": f"🤪 Certified Goober — {n}%",
        "body": f"🤪 Goober Certification\n\n{name}'s goober level: {n}%\n\nEvidence: {trait}",
    }


# ── Master list of all generators ─────────────────────────────────────────────

ALL_GENERATORS = [
    braincells, sigma_meter, npc_scanner, pp_calculator, gyatt_detector,
    aura_level, broke_meter, monkey_dna, alien_dna, mental_age,
    villain_arc, delulu_index, rizz_score, red_flag_meter, green_flag_meter,
    luck_today, billionaire_chance, cooking_skill, zombie_survival,
    touch_grass_counter, nasa_iq, marvel_hero, dc_villain, anime_power,
    secret_talent, biggest_flex, daily_curse, mcdonalds_order, cat_energy,
    dog_energy, gamer_rank, bed_rot, coffee_addiction, main_character_energy,
    chaos_energy, brainrot_meter, professional_yapper, drama_magnet,
    sleep_debt, goblin_meter, meme_addiction, keyboard_warrior,
    professional_menace, screen_time, penguin_compatibility, gremlin_level,
    feet_enjoyer, pizza_addiction, certified_goober,
]


def generate_all(name: str) -> list[dict]:
    """Run all generators for a given name. Returns list of result dicts."""
    results = []
    for gen in ALL_GENERATORS:
        try:
            results.append(gen(name))
        except Exception:
            pass
    return results
