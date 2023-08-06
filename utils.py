def get_value_from_tuple(t):
    if t is None:
        return None
    elif isinstance(t, tuple) and len(t) == 1:
        return t[0]
    else:
        raise ValueError("Le paramètre doit être soit None, soit un tuple avec un seul élément.")
