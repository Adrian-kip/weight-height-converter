def lbs_to_kg(pounds):
    try:
        return round(pounds * 0.45359237, 2)
    except TypeError:
        raise ValueError("Input must be a number.")

def kg_to_lbs(kilograms):
    try:
        return round(kilograms / 0.45359237, 2)
    except TypeError:
        raise ValueError("Input must be a number.")

def inches_to_cm(inches):
    try:
        return round(inches * 2.54, 2)
    except TypeError:
        raise ValueError("Input must be a number.")

def cm_to_inches(cm):
    try:
        return round(cm / 2.54, 2)
    except TypeError:
        raise ValueError("Input must be a number.")

def get_conversion_result(conversion_type, value):
    """
    Takes a conversion type (string) and value (float),
    returns the converted result or raises a ValueError.
    """
    if conversion_type == "lbs_to_kg":
        return lbs_to_kg(value)
    elif conversion_type == "kg_to_lbs":
        return kg_to_lbs(value)
    elif conversion_type == "in_to_cm":
        return inches_to_cm(value)
    elif conversion_type == "cm_to_in":
        return cm_to_inches(value)
    else:
        raise ValueError("Unsupported conversion type.")
