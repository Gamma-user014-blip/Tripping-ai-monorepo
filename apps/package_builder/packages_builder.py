from score_algorithms import *

def build_package(packet):
    """
    Builds a package by selecting the best item from each stage.
    'packet' is a list of stage dictionaries: [ {"type": "...", "options": [...]}, ... ]
    """
    package = []

    for stage in packet:
        item_type = stage.get("type", "unknown")
        options = stage.get("options", [])
        
        if not options:
            continue
            
        if item_type == "flight":
            best_item = get_best_flight(options)
        elif item_type == "hotel":
            best_item = get_best_hotel(options)
        elif item_type == "activity":
            # Activities scoring to be implemented later
            best_item = options[0]
        else:
            best_item = options[0]
        
        best_item["type"] = item_type
        package.append(best_item)

    return package
