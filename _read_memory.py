"""Read pattern memory with proper property access"""
import json
from pathlib import Path
from rtug_pattern_memory import PatternMemory

memory = PatternMemory()
patterns = memory.list_patterns()

print(f"Total patterns: {len(patterns)}\n")
if patterns:
    for p in patterns:
        rec = memory.get_pattern(p['name'])
        if rec:
            s = rec.state
            dv = s.direction_vector
            tags = ','.join(rec.tags)
            print(f"{rec.name:35s} Bull:{s.bull_count}/5 Bear:{s.bear_count}/5")
            print(f"  Vektor: {dv}  Tags: [{tags}]  Weight: {rec.weight}")
            print(f"  Fiyat: {s.price_action}  Kaynak: {rec.source}")
            print(f"  Eslesme: {rec.match_count}  Basari: %{rec.success_rate:.0f}")
            notes_short = rec.notes[:120].replace('\n', ' | ')
            print(f"  {notes_short}")
            print()
    
    # Match test: find patterns matching query
    print("--- MATCH TEST ---")
    q = PatternMemory().patterns
    if q:
        name = list(q.keys())[0]
        rec = q[name]
        print(f"Test pattern: {name}")
        print(f"  State vektor: {rec.state.direction_vector}")
        print(f"  State values: {rec.state.value_vector}")
        print(f"  State raw div1: {rec.state.div1}, div2: {rec.state.div2}")
