"""
inline_generators.py — Chaos Engine inline generator.

Pure Python procedural generation. Zero AI, zero API, zero HTTP.
Billions of possible combinations. Results almost never repeat.
"""

import random
import hashlib
import string
from datetime import datetime, timedelta


def _stable_pct(name: str, salt: str, lo: int = 0, hi: int = 100) -> int:
    h = int(hashlib.md5(f"{name}{salt}".encode()).hexdigest(), 16)
    return lo + (h % (hi - lo + 1))


def _case_id() -> str:
    return "CASE-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


EVENTS = [
    "walked into a Costco", "entered a library", "joined a Zoom call",
    "appeared at a wedding", "showed up at a funeral", "entered a McDonald's",
    "walked past a police station", "joined a Discord server",
    "entered a hospital", "appeared in a courtroom", "walked into IKEA",
    "joined a book club", "entered a gym", "showed up at a family reunion",
    "walked into a government building", "appeared on live TV",
    "entered a casino", "joined a therapy session", "walked into a church",
    "appeared at a press conference", "entered a laboratory",
]

REACTIONS = [
    "everyone immediately left", "the staff called security",
    "three people fainted", "a fire alarm went off",
    "the Wi-Fi disconnected", "plants wilted",
    "a priest started praying", "dogs started barking outside",
    "the lights flickered", "someone started recording",
    "NASA detected an anomaly", "the vibe shifted permanently",
    "government satellites repositioned", "birds flew away",
    "the manager was called", "insurance premiums went up",
    "the stock market dipped slightly", "a therapist started crying",
    "local authorities were notified", "the UN held an emergency meeting",
    "scientists requested a sample", "historians took notes",
    "three ambulances arrived", "the Pope was informed",
]

WITNESSES = [
    "A local pigeon", "A traumatized barista", "An off-duty detective",
    "A retired NASA engineer", "Three kindergarteners",
    "A philosophy professor", "An overworked intern",
    "A confused grandmother", "A Twitch streamer who was live",
    "A man who was just trying to get milk", "A certified accountant",
    "An emotional support animal", "A door-to-door salesman",
    "A government agent who won't give their name",
    "A cat who has seen things", "A Reddit moderator",
    "An Amazon delivery driver", "A conspiracy theorist who was right",
    "A surprisingly calm police officer",
]

WITNESS_QUOTES = [
    "I've never recovered.", "I'm not legally allowed to comment.",
    "I immediately deleted my social media.", "I still hear it sometimes.",
    "My therapist said not to talk about it.", "I've requested a transfer.",
    "I quit my job the next day.", "I've changed my name since.",
    "I don't go outside anymore.", "I've been sober ever since.",
    "The footage has been confiscated.", "I have a lawyer now.",
    "I submitted a formal complaint.", "I need more time.",
    "My insurance doesn't cover this.", "I wrote a book about it.",
]

DOCTOR_NOTES = [
    "Patient presents with unidentifiable energy.",
    "Symptoms cannot be reproduced in a laboratory setting.",
    "Scans came back blank. All three times.",
    "Diagnosis: existence itself.",
    "Recommended treatment: unclear.",
    "Staff requested not to be assigned this case again.",
    "We've sent samples to five universities.",
    "The hospital's Wi-Fi drops whenever patient enters.",
    "Patient's aura caused equipment malfunction.",
    "We've never seen numbers like this before.",
    "Results redacted pending further investigation.",
    "Insurance has already denied the claim.",
    "Peer review requested. No volunteers yet.",
]

POLICE_NOTES = [
    "Suspect remains at large.", "File sealed pending investigation.",
    "Evidence is being analyzed.", "Three officers requested reassignment.",
    "We don't fully understand what happened.",
    "Security footage reviewed. No comment.",
    "Subject cooperated. We wish they hadn't.",
    "This has been escalated to federal level.",
    "We've seen things. This is different.",
    "Case transferred to a different department.",
    "Charges pending. Lawyers are confused.",
]

ACHIEVEMENTS = [
    "Achievement Unlocked: No Witnesses",
    "Steam Achievement: Uninstalled Reality",
    "Achievement Unlocked: The Floor Is Lava (Literally)",
    "Steam Achievement: 500 Hours in Bed",
    "Achievement Unlocked: Certified Local Legend",
    "Steam Achievement: Escaped Tutorial",
    "Achievement Unlocked: Final Boss Behavior",
    "Steam Achievement: They Were Never The Same",
    "Achievement Unlocked: Chaos Incarnate",
    "Steam Achievement: Government Watchlist Member",
    "Achievement Unlocked: NPC Awareness",
    "Steam Achievement: Broke The Algorithm",
    "Achievement Unlocked: Vibe Check Passed Violently",
    "Steam Achievement: Main Character Activated",
    "Achievement Unlocked: Witnesses Requested Therapy",
]

HEADLINES = [
    "BREAKING: Local resident defies explanation",
    "DEVELOPING: Scientists baffled by recent events",
    "EXCLUSIVE: Government denies involvement",
    "ALERT: Area person causes unprecedented situation",
    "URGENT: Experts request further study",
    "REPORT: Three witnesses hospitalized after encounter",
    "CONFIRMED: The numbers don't lie",
    "BREAKING: NASA monitoring situation closely",
    "UPDATE: Insurance companies updating policies",
    "LIVE: Local authorities overwhelmed",
]

THREAT_LEVELS = [
    "GREEN", "YELLOW", "ORANGE", "RED", "PURPLE",
    "BLACK", "ULTRAVIOLET", "BEYOND COMPREHENSION", "CLASSIFIED",
]

VERDICTS = [
    "Guilty of existing.", "Not guilty. Somehow.",
    "Case dismissed. Judge needed a break.",
    "Verdict pending. Lawyers still arguing.",
    "Acquitted on a technicality.",
    "Sentenced to community service in another dimension.",
    "The jury could not reach a consensus.",
    "Charges upgraded three times during proceedings.",
    "Judge recused themselves immediately.",
    "Settlement reached. Amount undisclosed.",
]

GOVERNMENT_STATUSES = [
    "Under observation.", "File flagged.",
    "Do not approach without backup.",
    "Listed as a person of interest.",
    "Cleared. For now.", "Status: Complicated.",
    "Known to authorities.", "Special designation assigned.",
    "Monitoring ongoing.", "Classified. Ask your local representative.",
]

FAKE_REVIEWS = [
    "1/5 — Would not recommend.",
    "5/5 — Changed my life. Not for the better.",
    "3/5 — Consistent. Unfortunately.",
    "0/5 — I want a refund.",
    "5/5 — An experience unlike any other.",
    "2/5 — Showed up uninvited. Still here.",
    "4/5 — Surprisingly effective.",
    "1/5 — Filed a complaint. Pending review.",
    "5/5 — Scientists are studying this.",
]

NPC_QUOTES = [
    "Have you heard the news?", "Strange days, strange days.",
    "I used to be an adventurer like you.",
    "Be careful out there.", "I don't want any trouble.",
    "The weather's been odd lately.", "I mind my own business.",
    "My cousin's in the guard, you know.", "I have a family.",
    "This is fine.", "I didn't see anything.",
]

RANDOM_ENDINGS = [
    "The case remains open.", "No further questions.",
    "We've said too much.", "This report is classified.",
    "The truth is out there.", "Thank you for your cooperation.",
    "Please do not share this document.",
    "This has been peer reviewed. Unfortunately.",
    "The simulation continues.", "End of report.",
    "Filed under: Not Our Problem Anymore.",
    "God help us all.", "We are all witnesses now.",
    "This concludes our investigation.",
]

def _tier(pct: int) -> str:
    if pct <= 15:  return "Absolutely cooked 💀"
    if pct <= 35:  return "Embarrassing 😬"
    if pct <= 60:  return "Average 🤷"
    if pct <= 80:  return "Dangerous ⚠️"
    if pct <= 95:  return "Legendary 🔥"
    return "Biblically insane 🌀"


def _meta() -> str:
    lines = [
        f"Case ID: {_case_id()}",
        f"Threat Level: {random.choice(THREAT_LEVELS)}",
        f"Witness: {random.choice(WITNESSES)} — \"{random.choice(WITNESS_QUOTES)}\"",
        random.choice(ACHIEVEMENTS),
        f"📰 {random.choice(HEADLINES)}",
        f"Review: {random.choice(FAKE_REVIEWS)}",
        random.choice(RANDOM_ENDINGS),
    ]
    chosen = random.sample(lines, k=random.randint(3, 5))
    return "\n".join(chosen)


def _story(name: str, pct: int, topic: str) -> str:
    event    = random.choice(EVENTS)
    reaction = random.choice(REACTIONS)

    if pct <= 35:
        opener = f"{name}'s {topic} was measured. The results were concerning."
    elif pct <= 60:
        opener = f"{name} was tested for {topic}. Scientists took notes."
    elif pct <= 80:
        opener = f"{name} {event} and {reaction}."
    else:
        opener = f"{name} {event}. {reaction.capitalize()}. We cannot elaborate further."

    middle = f"{random.choice(WITNESSES)} reported: \"{random.choice(WITNESS_QUOTES)}\""
    note   = random.choice(DOCTOR_NOTES)
    return f"{opener}\n{middle}\n{note}"


# ── Generators ────────────────────────────────────────────────────────────────

def gen_braincells(name):
    pct = _stable_pct(name, "bc", 0, 14)
    n   = random.randint(0, max(0, pct))
    body = f"💀 Braincells Detector\n\n{name}'s braincell count: {n}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'braincell activity')}\n\n{_meta()}"
    return {"emoji":"💀","preview_title":"💀 Braincells Detector","preview_description":f"Scan {name}'s braincell count.","title":f"💀 Braincells — {n} remaining","body":body}

def gen_sigma(name):
    pct = _stable_pct(name, "sig")
    body = f"🗿 Sigma Meter\n\n{name}'s sigma level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'sigma energy')}\n\n{_meta()}"
    return {"emoji":"🗿","preview_title":"🗿 Sigma Meter","preview_description":f"Measure {name}'s sigma level.","title":f"🗿 Sigma — {pct}%","body":body}

def gen_aura(name):
    pct   = _stable_pct(name, "aura")
    score = random.randint(-99999, 99999)
    sign  = "+" if score > 0 else ""
    body  = f"✨ Aura Scanner\n\n{name}'s aura score: {sign}{score:,}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'aura')}\n\nGovernment Status: {random.choice(GOVERNMENT_STATUSES)}\n{_meta()}"
    return {"emoji":"✨","preview_title":"✨ Aura Scanner","preview_description":f"Reveal {name}'s hidden aura.","title":f"✨ Aura — {sign}{score:,}","body":body}

def gen_npc(name):
    pct = _stable_pct(name, "npc", 40, 100)
    body = f"🤖 NPC Scanner\n\n{name} is {pct}% NPC.\nStatus: {_tier(pct)}\n\nDetected dialogue: \"{random.choice(NPC_QUOTES)}\"\n{_story(name, pct, 'NPC behavior')}\n\nQuest available: No\n{_meta()}"
    return {"emoji":"🤖","preview_title":"🤖 NPC Scanner","preview_description":f"Run NPC analysis on {name}.","title":f"🤖 NPC — {pct}%","body":body}

def gen_rizz(name):
    pct = _stable_pct(name, "rizz")
    body = f"😎 Rizz Score\n\n{name}'s rizz: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'rizz')}\n\nVerdict: {random.choice(VERDICTS)}\n{_meta()}"
    return {"emoji":"😎","preview_title":"😎 Rizz Score","preview_description":f"Score {name}'s rizz.","title":f"😎 Rizz — {pct}%","body":body}

def gen_delulu(name):
    pct = _stable_pct(name, "del")
    body = f"🌸 Delulu Index\n\n{name}'s delulu level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'delusion')}\n\nDoctor's note: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🌸","preview_title":"🌸 Delulu Index","preview_description":f"Measure {name}'s delulu level.","title":f"🌸 Delulu — {pct}%","body":body}

def gen_villain(name):
    pct = _stable_pct(name, "vil")
    body = f"😈 Villain Arc Detector\n\n{name}'s villain arc: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'villain energy')}\n\nPolice notes: {random.choice(POLICE_NOTES)}\n{_meta()}"
    return {"emoji":"😈","preview_title":"😈 Villain Arc","preview_description":f"Detect {name}'s villain arc.","title":f"😈 Villain Arc — {pct}%","body":body}

def gen_red_flag(name):
    pct = _stable_pct(name, "rf")
    body = f"🚩 Red Flag Meter\n\n{name}'s red flag level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'red flags')}\n\nVerdict: {random.choice(VERDICTS)}\n{_meta()}"
    return {"emoji":"🚩","preview_title":"🚩 Red Flag Meter","preview_description":f"Scan {name} for red flags.","title":f"🚩 Red Flags — {pct}%","body":body}

def gen_green_flag(name):
    pct = _stable_pct(name, "gf")
    body = f"💚 Green Flag Meter\n\n{name}'s green flag level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'green flags')}\n\nReview: {random.choice(FAKE_REVIEWS)}\n{_meta()}"
    return {"emoji":"💚","preview_title":"💚 Green Flag Meter","preview_description":f"Scan {name} for green flags.","title":f"💚 Green Flags — {pct}%","body":body}

def gen_luck(name):
    pct = _stable_pct(name, "luck")
    body = f"🍀 Daily Luck Reading\n\n{name}'s luck today: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'luck')}\n\nHeadline: {random.choice(HEADLINES)}\n{_meta()}"
    return {"emoji":"🍀","preview_title":"🍀 Luck Today","preview_description":f"Check {name}'s luck today.","title":f"🍀 Luck — {pct}%","body":body}

def gen_broke(name):
    pct = _stable_pct(name, "brk", 10, 100)
    body = f"💸 Broke Meter\n\n{name} is {pct}% broke.\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'financial stability')}\n\nBank's verdict: {random.choice(VERDICTS)}\n{_meta()}"
    return {"emoji":"💸","preview_title":"💸 Broke Meter","preview_description":f"Check {name}'s financial status.","title":f"💸 Broke — {pct}%","body":body}

def gen_zombie(name):
    pct  = _stable_pct(name, "zmb")
    days = random.randint(0, 1200)
    body = f"🧟 Zombie Survival Report\n\n{name} would survive: {days} days\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'zombie survival')}\n\nCause of eventual death: {random.choice(EVENTS)}\n{_meta()}"
    return {"emoji":"🧟","preview_title":"🧟 Zombie Survival","preview_description":f"Calculate {name}'s zombie survival time.","title":f"🧟 Survival — {days} days","body":body}

def gen_mental_age(name):
    pct = _stable_pct(name, "mage")
    age = random.randint(4, 87)
    body = f"🧠 Mental Age Calculator\n\n{name}'s mental age: {age}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'mental maturity')}\n\nDoctor's note: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🧠","preview_title":"🧠 Mental Age","preview_description":f"Calculate {name}'s mental age.","title":f"🧠 Mental Age — {age}","body":body}

def gen_alien(name):
    pct = _stable_pct(name, "ali", 5, 95)
    body = f"👽 Alien DNA Scanner\n\n{name}'s alien DNA: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'alien origin')}\n\nGovernment Status: {random.choice(GOVERNMENT_STATUSES)}\n{_meta()}"
    return {"emoji":"👽","preview_title":"👽 Alien DNA Scanner","preview_description":f"Scan {name}'s alien DNA.","title":f"👽 Alien DNA — {pct}%","body":body}

def gen_monkey(name):
    pct = _stable_pct(name, "mnk", 20, 99)
    body = f"🐒 Monkey DNA Analysis\n\n{name}'s monkey DNA: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'primate behavior')}\n\nZoologist's report: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🐒","preview_title":"🐒 Monkey DNA","preview_description":f"Analyze {name}'s monkey DNA.","title":f"🐒 Monkey DNA — {pct}%","body":body}

def gen_marvel(name):
    heroes = [
        ("Captain Microwave","Burns food unevenly from 400m","Foil"),
        ("The Procrastinator","Defeats enemies eventually","Deadlines"),
        ("WiFi Man","Unstoppable near routers","Walls"),
        ("Nap King","Recharges in 17 minutes flat","Alarm clocks"),
        ("The Algorithm","Knows your needs before you do","Ad blockers"),
        ("Battery Saver","Survives on 1% indefinitely","Fast chargers"),
        ("Autocorrect","Changes reality unpredictably","Spellcheck"),
        ("The Overthinker","Sees 200 outcomes simultaneously","Deciding"),
        ("Yelp Reviewer","One star destroys empires","Being ignored"),
        ("The Passive Aggressor","Never raises voice. Wins always.","Direct confrontation"),
    ]
    hero, power, weakness = random.choice(heroes)
    pct = _stable_pct(name, "mrv")
    body = f"🦸 Marvel Hero Assignment\n\n{name} is: {hero}\nPower: {power}\nWeakness: {weakness}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'hero activity')}\n\n{_meta()}"
    return {"emoji":"🦸","preview_title":"🦸 Marvel Hero Assignment","preview_description":f"Assign {name} a Marvel hero.","title":f"🦸 {hero}","body":body}

def gen_dc(name):
    villains = [
        ("The Snooze Button","Returns every morning","Willpower"),
        ("Professor Low Battery","Strikes at 1%","Chargers"),
        ("The Roaming Charges","Ruins trips internationally","Wi-Fi"),
        ("Captain Spoiler","Destroys joy effortlessly","Headphones"),
        ("The Buffering","Freezes at peak moments","Good internet"),
        ("Commitment Issues","Disappears strategically","Receipts"),
        ("The Monday","Returns weekly without fail","Friday"),
        ("Group Chat Muter","Silent. Informed. Dangerous.","Notifications"),
        ("The Terms and Conditions","Never read. Always binding.","Skipping"),
    ]
    villain, power, weakness = random.choice(villains)
    pct = _stable_pct(name, "dc")
    body = f"🦹 DC Villain Assignment\n\n{name} is: {villain}\nPower: {power}\nWeakness: {weakness}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'villain activity')}\n\n{_meta()}"
    return {"emoji":"🦹","preview_title":"🦹 DC Villain Assignment","preview_description":f"Assign {name} a DC villain.","title":f"🦹 {villain}","body":body}

def gen_gyatt(name):
    pct = _stable_pct(name, "gyt")
    body = f"🍑 Gyatt Detector\n\n{name}'s gyatt reading: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'gyatt levels')}\n\nSeismograph: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🍑","preview_title":"🍑 Gyatt Detector","preview_description":f"Run gyatt analysis on {name}.","title":f"🍑 Gyatt — {pct}%","body":body}

def gen_pp(name):
    size = round(random.uniform(0.1, 50.0), 1)
    pct  = _stable_pct(name, "pp")
    body = f"📏 Totally Scientific PP Calculator\n\n{name}'s result: {size} cm\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'measurement')}\n\nLab report: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"📏","preview_title":"📏 PP Calculator","preview_description":f"Run scientific measurement on {name}.","title":f"📏 PP Size — {size} cm","body":body}

def gen_clown(name):
    pct = _stable_pct(name, "clwn")
    body = f"🤡 Clown Meter\n\n{name}'s clown level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'clown behavior')}\n\nCircus HR: {random.choice(POLICE_NOTES)}\n{_meta()}"
    return {"emoji":"🤡","preview_title":"🤡 Clown Meter","preview_description":f"Measure {name}'s clown energy.","title":f"🤡 Clown Level — {pct}%","body":body}

def gen_crybaby(name):
    pct = _stable_pct(name, "cry")
    body = f"😭 Crybaby Meter\n\n{name}'s crybaby level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'emotional stability')}\n\nTherapist: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"😭","preview_title":"😭 Crybaby Meter","preview_description":f"Measure {name}'s crybaby level.","title":f"😭 Crybaby — {pct}%","body":body}

def gen_rat(name):
    pct = _stable_pct(name, "rat")
    body = f"🐀 Rat Detector\n\n{name}'s rat energy: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'suspicious activity')}\n\nFBI notes: {random.choice(POLICE_NOTES)}\n{_meta()}"
    return {"emoji":"🐀","preview_title":"🐀 Rat Detector","preview_description":f"Detect rat energy in {name}.","title":f"🐀 Rat Energy — {pct}%","body":body}

def gen_feet(name):
    pct = _stable_pct(name, "ft")
    body = f"🦶 Feet Rating\n\n{name}'s feet rating: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'podiatric analysis')}\n\nPodiatrist: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🦶","preview_title":"🦶 Feet Rating","preview_description":f"Rate {name}'s feet scientifically.","title":f"🦶 Feet Rating — {pct}%","body":body}

def gen_smell(name):
    pct = _stable_pct(name, "sml")
    body = f"🧦 Smell Detector\n\n{name}'s smell level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'olfactory presence')}\n\nLab analysis: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🧦","preview_title":"🧦 Smell Detector","preview_description":f"Analyze {name}'s smell scientifically.","title":f"🧦 Smell Level — {pct}%","body":body}

def gen_shower(name):
    pct  = _stable_pct(name, "shwr")
    days = random.randint(0, 14)
    body = f"🚿 Shower Detector\n\n{name}'s last shower: {days} days ago\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'hygiene')}\n\nHealth department: {random.choice(POLICE_NOTES)}\n{_meta()}"
    return {"emoji":"🚿","preview_title":"🚿 Shower Detector","preview_description":f"Check when {name} last showered.","title":f"🚿 Last Shower — {days} days ago","body":body}

def gen_bedrot(name):
    pct = _stable_pct(name, "bdr", 20, 100)
    hrs = random.randint(8, 23)
    body = f"🛏️ Bed Rot Detector\n\n{name}'s bed rot level: {pct}%\nHours in bed today: {hrs}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'bed rot')}\n\nDoctor: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🛏️","preview_title":"🛏️ Bed Rot Detector","preview_description":f"Measure {name}'s bed rot level.","title":f"🛏️ Bed Rot — {pct}%","body":body}

def gen_fbi(name):
    pct = _stable_pct(name, "fbi")
    body = f"🚨 FBI Watchlist Scanner\n\n{name}'s threat level: {pct}%\nStatus: {_tier(pct)}\n\nCase ID: {_case_id()}\nClassification: {random.choice(THREAT_LEVELS)}\nAgent notes: {random.choice(POLICE_NOTES)}\nGovernment Status: {random.choice(GOVERNMENT_STATUSES)}\n{_meta()}"
    return {"emoji":"🚨","preview_title":"🚨 FBI Watchlist Scanner","preview_description":f"Check if {name} is on the FBI watchlist.","title":f"🚨 FBI Threat — {pct}%","body":body}

def gen_skill_issue(name):
    pct = _stable_pct(name, "ski")
    body = f"💀 Skill Issue Meter\n\n{name}'s skill issue level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'skill deficiency')}\n\nGame review: {random.choice(FAKE_REVIEWS)}\n{random.choice(ACHIEVEMENTS)}\n{_meta()}"
    return {"emoji":"💀","preview_title":"💀 Skill Issue Meter","preview_description":f"Measure {name}'s skill issue level.","title":f"💀 Skill Issue — {pct}%","body":body}

def gen_simp(name):
    pct = _stable_pct(name, "smp")
    body = f"💘 Simp Detector\n\n{name}'s simp level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'simping activity')}\n\nWitness: {random.choice(WITNESSES)} — \"{random.choice(WITNESS_QUOTES)}\"\n{_meta()}"
    return {"emoji":"💘","preview_title":"💘 Simp Detector","preview_description":f"Detect simp energy in {name}.","title":f"💘 Simp Level — {pct}%","body":body}

def gen_goblin(name):
    pct = _stable_pct(name, "gbl")
    body = f"🧌 Goblin Mode Detector\n\n{name}'s goblin level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'goblin behavior')}\n\nZoologist: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🧌","preview_title":"🧌 Goblin Mode Detector","preview_description":f"Detect goblin mode in {name}.","title":f"🧌 Goblin Level — {pct}%","body":body}

def gen_menace(name):
    pct = _stable_pct(name, "mnc")
    body = f"🧨 Menace Level\n\n{name}'s menace level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'menace activity')}\n\nPolice report: {random.choice(POLICE_NOTES)}\n{_meta()}"
    return {"emoji":"🧨","preview_title":"🧨 Menace Level","preview_description":f"Measure {name}'s menace to society.","title":f"🧨 Menace — {pct}%","body":body}

def gen_chaos(name):
    pct = _stable_pct(name, "chs")
    body = f"💥 Chaos Level\n\n{name}'s chaos energy: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'chaos')}\n\nEmergency services: {random.choice(POLICE_NOTES)}\n{random.choice(ACHIEVEMENTS)}\n{_meta()}"
    return {"emoji":"💥","preview_title":"💥 Chaos Level","preview_description":f"Measure {name}'s chaos energy.","title":f"💥 Chaos — {pct}%","body":body}

def gen_mutation(name):
    pct = _stable_pct(name, "mut")
    mutations = [
        "Extra toe", "Mild electrokinesis", "Immune to Mondays",
        "Can hear Wi-Fi", "Slightly magnetic", "Bioluminescent under stress",
        "Speaks to pigeons", "Predicts microwave beeps", "Coffee immunity",
    ]
    mutation = random.choice(mutations)
    body = f"🧪 Mutation Detector\n\n{name}'s mutation level: {pct}%\nDetected: {mutation}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'genetic mutation')}\n\nLab notes: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🧪","preview_title":"🧪 Mutation Detector","preview_description":f"Scan {name} for mutations.","title":f"🧪 Mutation — {pct}%","body":body}

def gen_demon(name):
    pct = _stable_pct(name, "dmn")
    body = f"👹 Demon Level\n\n{name}'s demon energy: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'demonic presence')}\n\nPriest's notes: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"👹","preview_title":"👹 Demon Level","preview_description":f"Measure {name}'s demon energy.","title":f"👹 Demon Level — {pct}%","body":body}

def gen_father(name):
    pct = _stable_pct(name, "dad")
    milk = random.choice(["Yes", "No", "Expired"])
    body = f"📵 Father Return Probability\n\n{name}'s dad return chance: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'parental return')}\n\nMilk still warm: {milk}\n{_meta()}"
    return {"emoji":"📵","preview_title":"📵 Father Return Probability","preview_description":f"Calculate if {name}'s dad comes back.","title":f"📵 Dad Return — {pct}%","body":body}

def gen_mommy(name):
    pct = _stable_pct(name, "mom")
    body = f"🍼 Mommy Issues Meter\n\n{name}'s mommy issues: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'childhood experiences')}\n\nTherapist: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🍼","preview_title":"🍼 Mommy Issues Meter","preview_description":f"Measure {name}'s mommy issues.","title":f"🍼 Mommy Issues — {pct}%","body":body}

def gen_alcohol(name):
    pct   = _stable_pct(name, "alc")
    pints = random.randint(0, 47)
    body  = f"🍺 Alcohol Resistance\n\n{name}'s resistance: {pct}%\nEstimated capacity: {pints} pints\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'alcohol tolerance')}\n\nBartender: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🍺","preview_title":"🍺 Alcohol Resistance","preview_description":f"Test {name}'s alcohol resistance.","title":f"🍺 Alcohol Resistance — {pct}%","body":body}

def gen_discord_mod(name):
    pct     = _stable_pct(name, "dsc")
    servers = random.randint(1, 847)
    hours   = random.randint(8, 24)
    body    = f"📱 Discord Mod Probability\n\n{name}'s Discord mod chance: {pct}%\nServer count: {servers}\nHours online today: {hours}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'moderation activity')}\n\nNPC Quote: \"{random.choice(NPC_QUOTES)}\"\n{_meta()}"
    return {"emoji":"📱","preview_title":"📱 Discord Mod Probability","preview_description":f"Calculate {name}'s Discord mod probability.","title":f"📱 Discord Mod — {pct}%","body":body}

def gen_jail(name):
    pct  = _stable_pct(name, "jl")
    secs = random.randint(3, 847)
    body = f"🚓 Jail Speedrun\n\n{name}'s jail speedrun: {pct}%\nPersonal record: {secs} seconds to first offense\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'criminal activity')}\n\nPolice notes: {random.choice(POLICE_NOTES)}\nVerdict: {random.choice(VERDICTS)}\n{_meta()}"
    return {"emoji":"🚓","preview_title":"🚓 Jail Speedrun","preview_description":f"Calculate {name}'s jail speedrun time.","title":f"🚓 Jail Speedrun — {pct}%","body":body}

def gen_main_char(name):
    pct = _stable_pct(name, "mc")
    body = f"🎰 Main Character Luck\n\n{name}'s main character energy: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'main character behavior')}\n\nNarrative arc: {random.choice(ACHIEVEMENTS)}\nHeadline: {random.choice(HEADLINES)}\n{_meta()}"
    return {"emoji":"🎰","preview_title":"🎰 Main Character Luck","preview_description":f"Check {name}'s main character energy.","title":f"🎰 Main Character — {pct}%","body":body}

def gen_aura_lost(name):
    lost = random.randint(0, 999999)
    pct  = _stable_pct(name, "auralost")
    body = f"💀 Lifetime Aura Lost\n\n{name} has lost {lost:,} aura points in their lifetime.\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'aura loss')}\n\nInsurance claim: Denied\nWitness: {random.choice(WITNESSES)} — \"{random.choice(WITNESS_QUOTES)}\"\n{_meta()}"
    return {"emoji":"💀","preview_title":"💀 Lifetime Aura Lost","preview_description":f"Calculate total aura {name} has lost.","title":f"💀 Aura Lost — {lost:,}","body":body}

def gen_iq(name):
    pct = _stable_pct(name, "iq")
    iq  = random.randint(12, 312)
    body = f"🚀 NASA IQ Test\n\n{name}'s IQ: {iq}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'intelligence')}\n\nNASA notes: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🚀","preview_title":"🚀 NASA IQ Test","preview_description":f"Run NASA IQ test on {name}.","title":f"🚀 IQ — {iq}","body":body}

def gen_brainrot(name):
    pct = _stable_pct(name, "brt")
    body = f"🧠 Brainrot Meter\n\n{name}'s brainrot level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'brainrot')}\n\nDiagnosis: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"🧠","preview_title":"🧠 Brainrot Meter","preview_description":f"Measure {name}'s brainrot level.","title":f"🧠 Brainrot — {pct}%","body":body}

def gen_yapper(name):
    pct   = _stable_pct(name, "yap")
    words = random.randint(500, 99999)
    body  = f"🗣️ Professional Yapper Certification\n\n{name}'s yapper level: {pct}%\nWords spoken today: {words:,}\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'yapping')}\n\nAudience review: {random.choice(FAKE_REVIEWS)}\n{_meta()}"
    return {"emoji":"🗣️","preview_title":"🗣️ Yapper Certification","preview_description":f"Certify {name} as a professional yapper.","title":f"🗣️ Yapper — {pct}%","body":body}

def gen_drama(name):
    pct = _stable_pct(name, "drm")
    orders = random.randint(0, 7)
    body = f"🎭 Drama Magnet Index\n\n{name}'s drama attraction: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'drama')}\n\nRestraining orders filed: {orders}\n{_meta()}"
    return {"emoji":"🎭","preview_title":"🎭 Drama Magnet","preview_description":f"Measure {name}'s drama attraction.","title":f"🎭 Drama Magnet — {pct}%","body":body}

def gen_keyboard(name):
    pct = _stable_pct(name, "kbw")
    body = f"⌨️ Keyboard Warrior Level\n\n{name}'s keyboard warrior level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'online combat')}\n\nArguments won: 0\nArguments had: {random.randint(47, 9999)}\n{_meta()}"
    return {"emoji":"⌨️","preview_title":"⌨️ Keyboard Warrior","preview_description":f"Measure {name}'s keyboard warrior level.","title":f"⌨️ Keyboard Warrior — {pct}%","body":body}

def gen_sleep(name):
    pct  = _stable_pct(name, "slp")
    debt = random.randint(0, 1200)
    body = f"😴 Sleep Debt Calculator\n\n{name} owes sleep: {debt} hours\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'sleep deprivation')}\n\nDoctor: {random.choice(DOCTOR_NOTES)}\n{_meta()}"
    return {"emoji":"😴","preview_title":"😴 Sleep Debt","preview_description":f"Calculate {name}'s sleep debt.","title":f"😴 Sleep Debt — {debt} hrs","body":body}

def gen_meme(name):
    pct   = _stable_pct(name, "mme")
    count = random.randint(500, 99999)
    pct2  = random.randint(80, 99)
    body  = f"😂 Meme Addiction Report\n\n{name}'s meme addiction: {pct}%\nMemes saved: {count:,}\nCamera roll: {pct2}% memes\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'meme consumption')}\n\n{_meta()}"
    return {"emoji":"😂","preview_title":"😂 Meme Addiction","preview_description":f"Assess {name}'s meme addiction.","title":f"😂 Meme Addict — {pct}%","body":body}

def gen_penguin(name):
    pct = _stable_pct(name, "png")
    body = f"🐧 Penguin Compatibility Test\n\n{name}'s penguin compatibility: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'penguin relations')}\n\nPenguin council verdict: {random.choice(VERDICTS)}\n{_meta()}"
    return {"emoji":"🐧","preview_title":"🐧 Penguin Compatibility","preview_description":f"Test {name}'s penguin compatibility.","title":f"🐧 Penguin Compat — {pct}%","body":body}

def gen_goober(name):
    pct = _stable_pct(name, "gbr")
    body = f"🤪 Certified Goober Test\n\n{name}'s goober level: {pct}%\nStatus: {_tier(pct)}\n\n{_story(name, pct, 'goober behavior')}\n\nCertification: {random.choice(ACHIEVEMENTS)}\n{_meta()}"
    return {"emoji":"🤪","preview_title":"🤪 Certified Goober","preview_description":f"Certify {name} as a goober.","title":f"🤪 Goober — {pct}%","body":body}


# ── Master list ───────────────────────────────────────────────────────────────

ALL_GENERATORS = [
    gen_braincells, gen_sigma, gen_aura, gen_npc, gen_rizz,
    gen_delulu, gen_villain, gen_red_flag, gen_green_flag, gen_luck,
    gen_broke, gen_zombie, gen_mental_age, gen_alien, gen_monkey,
    gen_marvel, gen_dc, gen_gyatt, gen_pp, gen_clown,
    gen_crybaby, gen_rat, gen_feet, gen_smell, gen_shower,
    gen_bedrot, gen_fbi, gen_skill_issue, gen_simp, gen_goblin,
    gen_menace, gen_chaos, gen_mutation, gen_demon, gen_father,
    gen_mommy, gen_alcohol, gen_discord_mod, gen_jail, gen_main_char,
    gen_aura_lost, gen_iq, gen_brainrot, gen_yapper, gen_drama,
    gen_keyboard, gen_sleep, gen_meme, gen_penguin, gen_goober,
]


async def generate_all(name: str) -> list[dict]:
    """
    Generate all 50 cards for a name.
    Instant — pure Python, zero API calls.
    Percentages stable per name. Stories and metadata random every time.
    """
    results = []
    for gen in ALL_GENERATORS:
        try:
            results.append(gen(name))
        except Exception:
            pass
    return results