"""
inline_generators.py — 49 funny Gen Z inline result generators.

Scores/percentages are seeded by name (consistent feel).
Funny reasons are AI-generated fresh every time (never boring).

Architecture:
  1. generate_scores(name) — instant, deterministic per name
  2. generate_reasons(name, scores) — one AI call, returns all 49 reasons
  3. build_results(name, scores, reasons) — combines into final cards
"""

import random
import hashlib
import logging
import json
import re

logger = logging.getLogger(__name__)


def _seed(name: str, salt: str) -> None:
    h = int(hashlib.md5(f"{name}{salt}".encode()).hexdigest(), 16)
    random.seed(h)


def _pct(name: str, salt: str, lo: int = 0, hi: int = 100) -> int:
    _seed(name, salt)
    return random.randint(lo, hi)


def _pick(name: str, salt: str, options: list):
    _seed(name, salt)
    return random.choice(options)


# ── Score generators (deterministic per name) ─────────────────────────────────

def _get_scores(name: str) -> dict:
    """Generate all numeric scores/values for a name. Always same for same name."""
    _seed(name, "aura")
    aura = random.randint(-99999, 99999)

    _seed(name, "zombie")
    zombie_days = random.randint(0, 847)

    _seed(name, "iq")
    iq = random.randint(12, 312)

    _seed(name, "pp")
    pp_size = round(random.uniform(0.1, 50.0), 1)

    _seed(name, "coffee")
    coffee_cups = random.randint(0, 12)

    _seed(name, "screen")
    screen_hours = round(random.uniform(4, 18), 1)

    _seed(name, "sleep")
    sleep_debt_hrs = random.randint(0, 847)

    _seed(name, "meme_c")
    meme_count = random.randint(50, 9999)

    _seed(name, "yapper_w")
    yapper_words = random.randint(500, 50000)

    _seed(name, "anime_l")
    anime_power_lvl = random.randint(1, 10000)

    marvel_heroes = [
        "Captain Microwave", "The Procrastinator", "WiFi Man",
        "Nap King", "The Algorithm", "Battery Saver",
        "Autocorrect", "The Overthinker",
    ]
    dc_villains = [
        "The Snooze Button", "Professor Low Battery", "The Roaming Charges",
        "Captain Spoiler", "The Buffering", "Commitment Issues", "The Monday",
    ]
    anime_powers = [
        "Maximum Overthinking Jutsu", "Ultimate Bed Rot Form",
        "Infinite Scroll Technique", "Zero Accountability Stance",
        "Chronically Online Mode", "Selective Hearing Mastery",
        "Last Minute Activation", "Main Character Delusion",
        "Ghost Mode: Activated", "Chaos Energy Release",
    ]
    gamer_ranks = [
        "Iron IV", "Bronze III", "Silver II", "Gold I",
        "Platinum", "Diamond", "Master", "Grandmaster",
        "Challenger", "NPC Difficulty",
    ]
    mc_mains = ["McDouble", "Big Mac", "Quarter Pounder", "McChicken",
                "Filet-O-Fish", "10pc Nuggets", "McRib"]
    mc_sides = ["large fries", "medium fries", "apple slices", "hash brown"]
    mc_drinks = ["large Coke", "McFlurry", "large sweet tea", "Sprite", "water"]
    screen_apps = ["TikTok", "Instagram", "YouTube", "Discord",
                   "Reddit", "Telegram", "Twitter/X"]

    import datetime
    today = datetime.date.today().isoformat()
    _seed(name + today, "luck")
    luck_today = random.randint(0, 100)
    _seed(name + today, "grass")
    grass_count = random.randint(0, 3)

    return {
        "braincells":       _pct(name, "braincells", 0, 14),
        "sigma":            _pct(name, "sigma"),
        "npc":              _pct(name, "npc", 40, 100),
        "pp_size":          pp_size,
        "gyatt":            _pct(name, "gyatt"),
        "aura":             aura,
        "broke":            _pct(name, "broke", 10, 100),
        "monkey_dna":       _pct(name, "monkey", 20, 99),
        "alien_dna":        _pct(name, "alien", 5, 95),
        "mental_age":       _pct(name, "mental_age", 4, 87),
        "villain_arc":      _pct(name, "villain"),
        "delulu":           _pct(name, "delulu"),
        "rizz":             _pct(name, "rizz"),
        "red_flag":         _pct(name, "redflag"),
        "green_flag":       _pct(name, "greenflag"),
        "luck_today":       luck_today,
        "billionaire":      _pct(name, "billionaire"),
        "cooking":          _pct(name, "cooking"),
        "zombie_days":      zombie_days,
        "grass_count":      grass_count,
        "iq":               iq,
        "marvel_hero":      _pick(name, "marvel", marvel_heroes),
        "dc_villain":       _pick(name, "dc", dc_villains),
        "anime_power":      _pick(name, "anime_p", anime_powers),
        "anime_power_lvl":  anime_power_lvl,
        "cat_energy":       _pct(name, "cat"),
        "dog_energy":       _pct(name, "dog"),
        "gamer_rank":       _pick(name, "gamer_r", gamer_ranks),
        "bed_rot":          _pct(name, "bedrot", 20, 100),
        "coffee_cups":      coffee_cups,
        "main_character":   _pct(name, "mainchar"),
        "chaos_energy":     _pct(name, "chaos_e"),
        "brainrot":         _pct(name, "brainrot"),
        "yapper_pct":       _pct(name, "yapper"),
        "yapper_words":     yapper_words,
        "drama":            _pct(name, "drama"),
        "sleep_debt":       sleep_debt_hrs,
        "goblin":           _pct(name, "goblin"),
        "meme_pct":         _pct(name, "meme"),
        "meme_count":       meme_count,
        "keyboard":         _pct(name, "keyboard"),
        "menace":           _pct(name, "menace"),
        "screen_hours":     screen_hours,
        "screen_app":       _pick(name, "screen_a", screen_apps),
        "penguin":          _pct(name, "penguin"),
        "gremlin":          _pct(name, "gremlin"),
        "feet":             _pct(name, "feet"),
        "pizza_pct":        _pct(name, "pizza"),
        "pizza_slices":     _pct(name, "pizza_s", 2, 847),
        "goober":           _pct(name, "goober"),
        "pp_size":          pp_size,
        "mc_main":          _pick(name, "mc1", mc_mains),
        "mc_side":          _pick(name, "mc2", mc_sides),
        "mc_drink":         _pick(name, "mc3", mc_drinks),
    }


# ── AI reason generation ───────────────────────────────────────────────────────

async def _ai_generate_reasons(name: str, scores: dict) -> dict:
    """
    One AI call generates all 49 funny reasons at once.
    Returns dict of reason_key -> funny_text.
    Falls back to generic funny text if AI fails.
    """
    from app import providers

    prompt = f"""You are generating funny Gen Z internet humor results for someone named "{name}".

Generate a SHORT funny reason/explanation for each of these results. 
Each reason must be 1 sentence max. Absurd, Gen Z, brainrot humor.
Make each one different and creative. Reference the name "{name}" naturally in some of them.

Results to explain:
1. braincells_reason — they have {scores['braincells']} braincells left
2. sigma_reason — sigma level {scores['sigma']}%
3. npc_reason — {scores['npc']}% NPC
4. pp_reason — PP size {scores['pp_size']}cm (keep it funny not explicit)
5. gyatt_reason — gyatt level {scores['gyatt']}%
6. aura_reason — aura score {scores['aura']:,}
7. broke_reason — {scores['broke']}% broke
8. monkey_reason — {scores['monkey_dna']}% monkey DNA
9. alien_reason — {scores['alien_dna']}% alien DNA
10. mental_age_reason — mental age {scores['mental_age']}
11. villain_reason — villain arc {scores['villain_arc']}%
12. delulu_reason — delulu index {scores['delulu']}%
13. rizz_reason — rizz score {scores['rizz']}%
14. redflag_reason — red flag level {scores['red_flag']}%
15. greenflag_reason — green flag level {scores['green_flag']}%
16. luck_reason — luck today {scores['luck_today']}%
17. billionaire_reason — billionaire chance {scores['billionaire']}%
18. cooking_reason — cooking skill {scores['cooking']}%
19. zombie_reason — zombie survival {scores['zombie_days']} days
20. grass_reason — touched grass {scores['grass_count']} times today
21. iq_reason — NASA IQ {scores['iq']}
22. marvel_reason — marvel hero is {scores['marvel_hero']}
23. dc_reason — DC villain is {scores['dc_villain']}
24. anime_reason — anime power is {scores['anime_power']} at level {scores['anime_power_lvl']:,}
25. cat_reason — cat energy {scores['cat_energy']}%
26. dog_reason — dog energy {scores['dog_energy']}%
27. gamer_reason — gamer rank {scores['gamer_rank']}
28. bedrot_reason — bed rot {scores['bed_rot']}%
29. coffee_reason — drinks {scores['coffee_cups']} cups of coffee daily
30. mainchar_reason — main character energy {scores['main_character']}%
31. chaos_reason — chaos energy {scores['chaos_energy']}%
32. brainrot_reason — brainrot level {scores['brainrot']}%
33. yapper_reason — professional yapper {scores['yapper_pct']}%, spoke {scores['yapper_words']:,} words today
34. drama_reason — drama magnet {scores['drama']}%
35. sleep_reason — owes {scores['sleep_debt']} hours of sleep
36. goblin_reason — goblin level {scores['goblin']}%
37. meme_reason — meme addiction {scores['meme_pct']}%, saved {scores['meme_count']:,} memes
38. keyboard_reason — keyboard warrior {scores['keyboard']}%
39. menace_reason — professional menace {scores['menace']}%
40. screen_reason — {scores['screen_hours']}h screen time, mostly on {scores['screen_app']}
41. penguin_reason — penguin compatibility {scores['penguin']}%
42. gremlin_reason — gremlin level {scores['gremlin']}%
43. feet_reason — feet enjoyer level {scores['feet']}%
44. pizza_reason — pizza addiction {scores['pizza_pct']}%, eaten {scores['pizza_slices']} slices lifetime
45. goober_reason — certified goober {scores['goober']}%
46. secret_talent_reason — one sentence describing a random secret talent {name} has
47. biggest_flex_reason — one sentence describing {name}'s biggest flex
48. daily_curse_reason — one sentence curse for {name} today (something minor that will go wrong)
49. mcdonalds_reason — a funny comment about their order: {scores['mc_main']}, {scores['mc_side']}, {scores['mc_drink']}

Return ONLY a JSON object with these 49 keys and their string values.
No markdown, no explanation, just the JSON."""

    try:
        raw = await providers.chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.95,
            tier="fast",
        )
        raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        reasons = json.loads(raw)
        logger.info(f"[inline] AI generated {len(reasons)} reasons for '{name}'")
        return reasons
    except Exception as e:
        logger.warning(f"[inline] AI reason generation failed: {e}")
        return {}


def _fallback_reason(key: str, name: str) -> str:
    """Generic fallback if AI fails for a specific key."""
    fallbacks = {
        "braincells_reason": "The rest filed for early retirement.",
        "sigma_reason": f"{name} has been studied by scientists.",
        "npc_reason": "Dialogue options are limited.",
        "pp_reason": "The measuring tape had thoughts.",
        "gyatt_reason": "The detector needed recalibration.",
        "aura_reason": "The vibe check has been submitted.",
        "broke_reason": "The bank account sent thoughts and prayers.",
        "monkey_reason": "Cannot resist a spinning chair.",
        "alien_reason": "Area 51 has a file.",
        "mental_age_reason": "Refuses to act their age. Thriving.",
        "villain_reason": "The origin story is almost complete.",
        "delulu_reason": "The delulu is the solulu.",
        "rizz_reason": "Results were unexpected.",
        "redflag_reason": "The flags are visible from space.",
        "greenflag_reason": "Actually texts back. Rare.",
        "luck_reason": "The universe has spoken.",
        "billionaire_reason": "The math is not mathing.",
        "cooking_reason": "The smoke alarm is their personal chef timer.",
        "zombie_reason": "Surprisingly resourceful under pressure.",
        "grass_reason": "The grass has mixed feelings.",
        "iq_reason": "NASA is interested.",
        "marvel_reason": "The powers are very specific.",
        "dc_reason": "The origin story writes itself.",
        "anime_reason": "The power level shocked even the author.",
        "cat_reason": "Judges everything silently.",
        "dog_reason": "Excited about everything always.",
        "gamer_reason": "The teammates are always the problem.",
        "bedrot_reason": "The bed has accepted them.",
        "coffee_reason": "Their blood type is espresso.",
        "mainchar_reason": "The narration never stops.",
        "chaos_reason": "Plans somehow always work out.",
        "brainrot_reason": "The internet did this.",
        "yapper_reason": "Nobody asked but they answered anyway.",
        "drama_reason": "Drama arrives uninvited. Always.",
        "sleep_reason": "Running on spite and caffeine.",
        "goblin_reason": "The snack stash is well hidden.",
        "meme_reason": "Has a meme for every situation.",
        "keyboard_reason": "Types aggressively when calm.",
        "menace_reason": "A menace to society but make it cute.",
        "screen_reason": "The screen time report was not opened.",
        "penguin_reason": "The penguins have reviewed the application.",
        "gremlin_reason": "Only functional after midnight.",
        "feet_reason": "The algorithm has noticed.",
        "pizza_reason": "Eats cold pizza for breakfast unironically.",
        "goober_reason": "Irreversibly a goober. It's a compliment.",
        "secret_talent_reason": f"{name} has a talent nobody expected.",
        "biggest_flex_reason": f"{name}'s flex is surprisingly specific.",
        "daily_curse_reason": "Something minor will go wrong today.",
        "mcdonalds_reason": "The order reflects the soul.",
    }
    return fallbacks.get(key, "Results were inconclusive.")


# ── Build final result cards ───────────────────────────────────────────────────

def _build_cards(name: str, scores: dict, reasons: dict) -> list[dict]:
    """Combine scores + AI reasons into final card list."""

    def r(key):
        return reasons.get(key) or _fallback_reason(key, name)

    cards = [
        {
            "title": f"💀 Braincells Left — {scores['braincells']}",
            "body": f"💀 Braincells Left\n\n{name}'s remaining braincells: {scores['braincells']}\n\n{r('braincells_reason')}",
        },
        {
            "title": f"🗿 Sigma Meter — {scores['sigma']}%",
            "body": f"🗿 Sigma Meter\n\n{name}'s sigma level: {scores['sigma']}%\n\n{r('sigma_reason')}",
        },
        {
            "title": f"🤖 NPC Scanner — {scores['npc']}% NPC",
            "body": f"🤖 NPC Scanner\n\n{name} is {scores['npc']}% NPC.\n\n{r('npc_reason')}",
        },
        {
            "title": f"📏 PP Calculator™ — {scores['pp_size']} cm",
            "body": f"📏 Totally Scientific PP Calculator™\n\n{name}'s result: {scores['pp_size']} cm\n\n{r('pp_reason')}",
        },
        {
            "title": f"🍑 Gyatt Detector — {scores['gyatt']}%",
            "body": f"🍑 Gyatt Detector\n\n{name}'s gyatt reading: {scores['gyatt']}%\n\n{r('gyatt_reason')}",
        },
        {
            "title": f"✨ Aura Score — {scores['aura']:,}",
            "body": f"✨ Aura Level\n\n{name}'s aura score: {scores['aura']:,}\n\n{r('aura_reason')}",
        },
        {
            "title": f"💸 Broke Meter — {scores['broke']}%",
            "body": f"💸 Broke Meter\n\n{name} is {scores['broke']}% broke.\n\n{r('broke_reason')}",
        },
        {
            "title": f"🐒 Monkey DNA — {scores['monkey_dna']}%",
            "body": f"🐒 Monkey DNA Analysis\n\n{name}'s monkey DNA: {scores['monkey_dna']}%\n\n{r('monkey_reason')}",
        },
        {
            "title": f"👽 Alien DNA — {scores['alien_dna']}%",
            "body": f"👽 Alien DNA Scanner\n\n{name}'s alien DNA: {scores['alien_dna']}%\n\n{r('alien_reason')}",
        },
        {
            "title": f"🧠 Mental Age — {scores['mental_age']} years old",
            "body": f"🧠 Mental Age Calculator\n\n{name}'s mental age: {scores['mental_age']}\n\n{r('mental_age_reason')}",
        },
        {
            "title": f"😈 Villain Arc — {scores['villain_arc']}%",
            "body": f"😈 Villain Arc Detector\n\n{name}'s villain arc: {scores['villain_arc']}%\n\n{r('villain_reason')}",
        },
        {
            "title": f"🌸 Delulu Index — {scores['delulu']}%",
            "body": f"🌸 Delulu Index\n\n{name}'s delulu level: {scores['delulu']}%\n\n{r('delulu_reason')}",
        },
        {
            "title": f"😎 Rizz Score — {scores['rizz']}%",
            "body": f"😎 Rizz Score\n\n{name}'s rizz: {scores['rizz']}%\n\n{r('rizz_reason')}",
        },
        {
            "title": f"🚩 Red Flag Meter — {scores['red_flag']}%",
            "body": f"🚩 Red Flag Meter\n\n{name}'s red flag level: {scores['red_flag']}%\n\n{r('redflag_reason')}",
        },
        {
            "title": f"💚 Green Flag Meter — {scores['green_flag']}%",
            "body": f"💚 Green Flag Meter\n\n{name}'s green flag level: {scores['green_flag']}%\n\n{r('greenflag_reason')}",
        },
        {
            "title": f"🍀 Luck Today — {scores['luck_today']}%",
            "body": f"🍀 Daily Luck Reading\n\n{name}'s luck today: {scores['luck_today']}%\n\n{r('luck_reason')}",
        },
        {
            "title": f"💰 Billionaire Chance — {scores['billionaire']}%",
            "body": f"💰 Billionaire Probability\n\n{name}'s chance: {scores['billionaire']}%\n\n{r('billionaire_reason')}",
        },
        {
            "title": f"👨‍🍳 Cooking Skill — {scores['cooking']}%",
            "body": f"👨‍🍳 Cooking Skill Assessment\n\n{name}'s cooking skill: {scores['cooking']}%\n\n{r('cooking_reason')}",
        },
        {
            "title": f"🧟 Zombie Survival — {scores['zombie_days']} days",
            "body": f"🧟 Zombie Apocalypse Survival\n\n{name} would survive: {scores['zombie_days']} days\n\n{r('zombie_reason')}",
        },
        {
            "title": f"🌿 Grass Touched Today — {scores['grass_count']}x",
            "body": f"🌿 Touch Grass Counter\n\n{name} touched grass today: {scores['grass_count']} times\n\n{r('grass_reason')}",
        },
        {
            "title": f"🚀 NASA IQ — {scores['iq']}",
            "body": f"🚀 NASA IQ Test Results\n\n{name}'s IQ: {scores['iq']}\n\n{r('iq_reason')}",
        },
        {
            "title": f"🦸 Marvel Hero — {scores['marvel_hero']}",
            "body": f"🦸 Marvel Hero Assignment\n\n{name} is: {scores['marvel_hero']}\n\n{r('marvel_reason')}",
        },
        {
            "title": f"🦹 DC Villain — {scores['dc_villain']}",
            "body": f"🦹 DC Villain Assignment\n\n{name} is: {scores['dc_villain']}\n\n{r('dc_reason')}",
        },
        {
            "title": f"⚡ Anime Power — {scores['anime_power']}",
            "body": f"⚡ Anime Power Level\n\n{name}'s power: {scores['anime_power']}\nPower level: {scores['anime_power_lvl']:,}\n\n{r('anime_reason')}",
        },
        {
            "title": f"🌟 Secret Talent",
            "body": f"🌟 Secret Talent Revealed\n\n{name}'s hidden talent:\n\n{r('secret_talent_reason')}",
        },
        {
            "title": f"💪 Biggest Flex",
            "body": f"💪 Biggest Flex Detected\n\n{name}'s biggest flex:\n\n{r('biggest_flex_reason')}",
        },
        {
            "title": f"🪄 Daily Curse",
            "body": f"🪄 Today's Curse for {name}:\n\n{r('daily_curse_reason')}",
        },
        {
            "title": f"🍔 McDonald's Order",
            "body": f"🍔 {name}'s McDonald's Order\n\n{scores['mc_main']}\n{scores['mc_side']}\n{scores['mc_drink']}\n\n{r('mcdonalds_reason')}",
        },
        {
            "title": f"🐱 Cat Energy — {scores['cat_energy']}%",
            "body": f"🐱 Cat Energy Reading\n\n{name}'s cat energy: {scores['cat_energy']}%\n\n{r('cat_reason')}",
        },
        {
            "title": f"🐶 Dog Energy — {scores['dog_energy']}%",
            "body": f"🐶 Dog Energy Reading\n\n{name}'s dog energy: {scores['dog_energy']}%\n\n{r('dog_reason')}",
        },
        {
            "title": f"🎮 Gamer Rank — {scores['gamer_rank']}",
            "body": f"🎮 Gamer Rank Assessment\n\n{name}'s rank: {scores['gamer_rank']}\n\n{r('gamer_reason')}",
        },
        {
            "title": f"🛏️ Bed Rot % — {scores['bed_rot']}%",
            "body": f"🛏️ Bed Rot Assessment\n\n{name}'s bed rot level: {scores['bed_rot']}%\n\n{r('bedrot_reason')}",
        },
        {
            "title": f"☕ Coffee Addiction — {scores['coffee_cups']} cups/day",
            "body": f"☕ Coffee Addiction Report\n\n{name} drinks: {scores['coffee_cups']} cups/day\n\n{r('coffee_reason')}",
        },
        {
            "title": f"🎬 Main Character Energy — {scores['main_character']}%",
            "body": f"🎬 Main Character Energy\n\n{name}'s level: {scores['main_character']}%\n\n{r('mainchar_reason')}",
        },
        {
            "title": f"🌀 Chaos Energy — {scores['chaos_energy']}%",
            "body": f"🌀 Chaos Energy Scan\n\n{name}'s chaos energy: {scores['chaos_energy']}%\n\n{r('chaos_reason')}",
        },
        {
            "title": f"🧠 Brainrot Meter — {scores['brainrot']}%",
            "body": f"🧠 Brainrot Level\n\n{name}'s brainrot: {scores['brainrot']}%\n\n{r('brainrot_reason')}",
        },
        {
            "title": f"🗣️ Professional Yapper — {scores['yapper_pct']}%",
            "body": f"🗣️ Yapper Certification\n\n{name}'s yapper level: {scores['yapper_pct']}%\nWords spoken today: {scores['yapper_words']:,}\n\n{r('yapper_reason')}",
        },
        {
            "title": f"🎭 Drama Magnet — {scores['drama']}%",
            "body": f"🎭 Drama Magnet Index\n\n{name}'s drama attraction: {scores['drama']}%\n\n{r('drama_reason')}",
        },
        {
            "title": f"😴 Sleep Debt — {scores['sleep_debt']} hours owed",
            "body": f"😴 Sleep Debt Calculator\n\n{name} owes sleep: {scores['sleep_debt']} hours\n\n{r('sleep_reason')}",
        },
        {
            "title": f"👺 Goblin Meter — {scores['goblin']}%",
            "body": f"👺 Goblin Level Assessment\n\n{name}'s goblin level: {scores['goblin']}%\n\n{r('goblin_reason')}",
        },
        {
            "title": f"😂 Meme Addiction — {scores['meme_pct']}%",
            "body": f"😂 Meme Addiction Report\n\n{name}'s addiction: {scores['meme_pct']}%\nMemes saved: {scores['meme_count']:,}\n\n{r('meme_reason')}",
        },
        {
            "title": f"⌨️ Keyboard Warrior — {scores['keyboard']}%",
            "body": f"⌨️ Keyboard Warrior Level\n\n{name}'s level: {scores['keyboard']}%\n\n{r('keyboard_reason')}",
        },
        {
            "title": f"😤 Professional Menace — {scores['menace']}%",
            "body": f"😤 Menace to Society Report\n\n{name}'s menace level: {scores['menace']}%\n\n{r('menace_reason')}",
        },
        {
            "title": f"📱 Screen Time — {scores['screen_hours']}h",
            "body": f"📱 Screen Time Report\n\n{name}'s daily screen time: {scores['screen_hours']} hours\nMost used: {scores['screen_app']}\n\n{r('screen_reason')}",
        },
        {
            "title": f"🐧 Penguin Compatibility — {scores['penguin']}%",
            "body": f"🐧 Penguin Compatibility Test\n\n{name}'s compatibility: {scores['penguin']}%\n\n{r('penguin_reason')}",
        },
        {
            "title": f"😈 Gremlin Level — {scores['gremlin']}%",
            "body": f"😈 Gremlin Level\n\n{name}'s gremlin energy: {scores['gremlin']}%\n\n{r('gremlin_reason')}",
        },
        {
            "title": f"🦶 Feet Enjoyer Level — {scores['feet']}%",
            "body": f"🦶 Feet Enjoyer Detector\n\n{name}'s level: {scores['feet']}%\n\n{r('feet_reason')}",
        },
        {
            "title": f"🍕 Pizza Addiction — {scores['pizza_pct']}%",
            "body": f"🍕 Pizza Addiction Report\n\n{name}'s addiction: {scores['pizza_pct']}%\nLifetime slices: {scores['pizza_slices']:,}\n\n{r('pizza_reason')}",
        },
        {
            "title": f"🤪 Certified Goober — {scores['goober']}%",
            "body": f"🤪 Goober Certification\n\n{name}'s goober level: {scores['goober']}%\n\nEvidence: {r('goober_reason')}",
        },
    ]
    # Add generic previews to every card so scores are hidden until clicked
    preview_descriptions = {
        "💀": f"Tap to reveal {name}'s braincells.",
        "🗿": f"Scan {name}'s sigma level.",
        "🤖": f"Run NPC analysis on {name}.",
        "📏": f"Scientific measurement for {name}.",
        "🍑": f"Scan {name}'s gyatt level.",
        "✨": f"Reveal {name}'s hidden aura.",
        "💸": f"Check {name}'s financial status.",
        "🐒": f"Analyze {name}'s monkey DNA.",
        "👽": f"Scan {name}'s alien DNA.",
        "🧠": f"Calculate {name}'s mental age.",
        "😈": f"Detect {name}'s villain arc.",
        "🌸": f"Measure {name}'s delulu index.",
        "😎": f"Score {name}'s rizz.",
        "🚩": f"Run red flag analysis on {name}.",
        "💚": f"Run green flag analysis on {name}.",
        "🍀": f"Check {name}'s luck today.",
        "💰": f"Calculate {name}'s billionaire chance.",
        "👨‍🍳": f"Assess {name}'s cooking skill.",
        "🧟": f"Calculate {name}'s zombie survival.",
        "🌿": f"Count {name}'s grass touches today.",
        "🚀": f"Run NASA IQ test on {name}.",
        "🦸": f"Assign {name} a Marvel hero.",
        "🦹": f"Assign {name} a DC villain.",
        "⚡": f"Reveal {name}'s anime power.",
        "🌟": f"Reveal {name}'s secret talent.",
        "💪": f"Reveal {name}'s biggest flex.",
        "🪄": f"Reveal {name}'s daily curse.",
        "🍔": f"Generate {name}'s McDonald's order.",
        "🐱": f"Read {name}'s cat energy.",
        "🐶": f"Read {name}'s dog energy.",
        "🎮": f"Check {name}'s gamer rank.",
        "🛏️": f"Measure {name}'s bed rot level.",
        "☕": f"Assess {name}'s coffee addiction.",
        "🎬": f"Measure {name}'s main character energy.",
        "🌀": f"Scan {name}'s chaos energy.",
        "🗣️": f"Certify {name} as a yapper.",
        "🎭": f"Measure {name}'s drama attraction.",
        "😴": f"Calculate {name}'s sleep debt.",
        "👺": f"Measure {name}'s goblin level.",
        "😂": f"Assess {name}'s meme addiction.",
        "⌨️": f"Measure {name}'s keyboard warrior level.",
        "😤": f"Rate {name}'s menace to society.",
        "📱": f"Check {name}'s screen time.",
        "🐧": f"Test {name}'s penguin compatibility.",
        "🦶": f"Detect {name}'s feet enjoyer level.",
        "🍕": f"Assess {name}'s pizza addiction.",
        "🤪": f"Certify {name} as a goober.",
    }

    for card in cards:
        emoji = card["title"].split()[0]
        generic_name = card["title"].split("—")[0].strip() if "—" in card["title"] else card["title"]
        card["preview_title"] = generic_name
        card["preview_description"] = preview_descriptions.get(emoji, f"Tap to reveal {name}'s result.")

    return cards


# ── Main public function ───────────────────────────────────────────────────────

async def generate_all(name: str) -> list[dict]:
    """
    Generate all 49 cards for a name.
    Scores are deterministic per name.
    Reasons are AI-generated fresh every call.
    """
    scores = _get_scores(name)
    reasons = await _ai_generate_reasons(name, scores)
    return _build_cards(name, scores, reasons)