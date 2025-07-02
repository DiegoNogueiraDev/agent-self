from typing import List, Dict, Any

def analyze_root_cause(snapshot: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Analyzes a snapshot of process metrics to find the top N processes
    consuming the most memory.

    Args:
        snapshot (List[Dict[str, Any]]): A list of process metric dictionaries, 
                                         as collected by the SystemCollector.
        top_n (int): The number of top memory-consuming processes to return.

    Returns:
        A list containing the top N memory-consuming process dictionaries,
        sorted by 'memory_percent' in descending order. Returns an empty
        list if the snapshot is empty or invalid.
    """
    if not snapshot:
        return []

    try:
        # Filter out non-dictionary items before sorting
        valid_processes = [p for p in snapshot if isinstance(p, dict)]
        
        # Sort processes by memory_percent in descending order
        sorted_processes = sorted(
            valid_processes, 
            key=lambda p: p.get('memory_percent', 0), 
            reverse=True
        )
        return sorted_processes[:top_n]
    except (TypeError, KeyError) as e:
        # Handle cases where snapshot items are not dicts or lack 'memory_percent'
        # In a real scenario, we would log this error.
        print(f"Error during root cause analysis: {e}")
        return []
