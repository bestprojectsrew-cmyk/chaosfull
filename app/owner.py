OWNER_IDS = {
    5893469399,   # Your first Telegram ID
    8248612020,   # Your second Telegram ID
}

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS