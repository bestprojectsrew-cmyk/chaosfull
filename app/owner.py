OWNER_IDS = {
    5893469399,
    8248612020,
}

def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS
