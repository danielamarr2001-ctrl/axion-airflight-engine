from typing import Any, Dict, List



def generate_flight_options(classification: Dict[str, Any], enabled: bool) -> List[Dict[str, str]]:
    simulated_options = [
        {"flight": "LA513", "time": "14:30 - 17:45", "status": "disponible"},
        {"flight": "LA515", "time": "18:00 - 21:15", "status": "disponible"},
        {"flight": "LA517", "time": "07:30 - 10:45", "status": "no disponible"},
    ]

    if not enabled:
        return []

    if classification.get("same_route"):
        return simulated_options

    return simulated_options[:2]
