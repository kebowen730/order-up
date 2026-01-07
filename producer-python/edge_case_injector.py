"""
Edge Case Injector: Introduces duplicates, out-of-order events, and late arrivals
Demonstrates chaos engineering by injecting edge cases into the event stream.
"""
import random
import copy
from typing import List, Dict, Any, Tuple


class EdgeCaseInjector:
    """Injects realistic edge cases into event streams"""
    
    def __init__(
        self,
        duplicate_probability: float = 0.15,
        out_of_order_probability: float = 0.20,
        late_arrival_probability: float = 0.10
    ):
        self.duplicate_probability = duplicate_probability
        self.out_of_order_probability = out_of_order_probability
        self.late_arrival_probability = late_arrival_probability
        
    def inject_edge_cases(
        self,
        events: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Inject edge cases into event stream
        
        Returns:
            Tuple of (main_events, late_arrival_events)
            - main_events: Events to send immediately (may include duplicates and be out of order)
            - late_arrival_events: Events to send later (simulating late arrivals)
        """
        main_events = []
        late_arrivals = []
        
        i = 0
        while i < len(events):
            event = events[i]
            
            # 1. Duplicate events (same event_id sent twice)
            if random.random() < self.duplicate_probability:
                main_events.append(copy.deepcopy(event))
                main_events.append(copy.deepcopy(event))  # Duplicate!
                print(f"  💥 DUPLICATE: event_id={event['event_id'][:8]}... order_id={event['order_id']}")
            else:
                main_events.append(event)
            
            # 2. Late arrivals (event sent much later than it should be)
            if random.random() < self.late_arrival_probability and i > 0:
                # Mark this event for late arrival
                late_event = copy.deepcopy(event)
                late_arrivals.append(late_event)
                print(f"  ⏰ LATE ARRIVAL: event_id={event['event_id'][:8]}... will arrive after delay")
            
            i += 1
        
        # 3. Out-of-order events (shuffle some events)
        if random.random() < self.out_of_order_probability and len(main_events) > 2:
            # Shuffle a random subset
            shuffle_size = random.randint(2, min(5, len(main_events)))
            shuffle_start = random.randint(0, len(main_events) - shuffle_size)
            shuffle_end = shuffle_start + shuffle_size
            
            shuffled_section = main_events[shuffle_start:shuffle_end]
            random.shuffle(shuffled_section)
            main_events[shuffle_start:shuffle_end] = shuffled_section
            
            print(f"  🔀 OUT-OF-ORDER: Shuffled {shuffle_size} events starting at index {shuffle_start}")
        
        return main_events, late_arrivals

