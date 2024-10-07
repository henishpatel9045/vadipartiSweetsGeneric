def convert_number_to_weight(val) -> str:
    val = int(val)
    if val < 1000:
        return f"{val} GM"
    val = val / 1000
    
    if val == int(val):
        val = int(val)
    
    return f"{val} KG"
