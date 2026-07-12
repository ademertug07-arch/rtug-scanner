"""Consolidate learned patterns into canonical golden patterns"""
import json
from pathlib import Path
from rtug_pattern_memory import PatternMemory, IndicatorState

memory = PatternMemory()
print(f"Raw patterns: {len(memory.patterns)}")

# Group patterns by direction vector
groups = {}
for name, p in memory.patterns.items():
    vec = tuple(p.state.direction_vector)
    if vec not in groups:
        groups[vec] = []
    groups[vec].append(name)

print(f"\nPattern groups by direction vector:")

canonical_patterns = []

for vec, names in sorted(groups.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n  Vector {list(vec)} ({len(names)} occurrences):")
    for n in names:
        p = memory.get_pattern(n)
        print(f"    {n}: {p.state.pattern_type}")

    # Calculate average values for this pattern type
    avg_state = IndicatorState()
    count = len(names)
    total_div1 = 0; total_div2 = 0; total_div3 = 0
    total_div5 = 0; total_div6 = 0; total_obv = 0

    for n in names:
        p = memory.get_pattern(n)
        total_div1 += abs(p.state.div1)
        total_div2 += abs(p.state.div2)
        total_div3 += abs(p.state.div3)
        total_div5 += abs(p.state.div5)
        total_div6 += abs(p.state.div6)
        total_obv += abs(p.state.obv_norm)

    # Create canonical pattern
    canonical = IndicatorState()
    canonical.div1_dir = vec[0]; canonical.div2_dir = vec[1]
    canonical.div3_dir = vec[2]; canonical.div5_dir = vec[3]
    canonical.div6_dir = vec[4]; canonical.obv_dir = vec[5]
    canonical.div1 = (total_div1 / count) * vec[0] if vec[0] != 0 else 0
    canonical.div2 = (total_div2 / count) * vec[1] if vec[1] != 0 else 0
    canonical.div3 = (total_div3 / count) * vec[2] if vec[2] != 0 else 0
    canonical.div5 = (total_div5 / count) * vec[3] if vec[3] != 0 else 0
    canonical.div6 = (total_div6 / count) * vec[4] if vec[4] != 0 else 0
    canonical.obv_norm = (total_obv / count) * vec[5] if vec[5] != 0 else 0

    # Weight based on occurrence frequency
    weight = min(1.0, count / 5)  # 5+ occurrences = weight 1.0
    canonical_patterns.append((vec, canonical, weight, count))

# Save canonical patterns
print(f"\n--- Creating Canonical Patterns ---")
for vec, state, weight, count in canonical_patterns:
    if vec == (1, 1, 1, 1, 1, 1):
        name = "CANONICAL_FULL_BULL_BREAKOUT"
        tags = ["full_bull", "breakout", "golden"]
    elif vec == (1, -1, 1, 1, 1, 1):
        name = "CANONICAL_BULL_SURROUND"
        tags = ["bull_surround", "deep_bull", "golden"]
    elif vec == (-1, -1, 1, 1, 1, 0):
        name = "CANONICAL_CONSOLIDATION_BREAKOUT"
        tags = ["consolidation", "reversal", "golden"]
    elif vec == (1, -1, -1, -1, -1, -1):
        name = "CANONICAL_BEARISH"
        tags = ["bearish", "deep_bear"]
    elif vec == (1, -1, 1, 1, 1, 0):
        name = "CANONICAL_BULL_SURROUND_FLAT_OBV"
        tags = ["bull_surround", "flat_obv"]
    else:
        name = f"CANONICAL_VEC_{'_'.join(str(v) for v in vec)}"
        tags = ["auto"]

    if count >= 2:
        memory.add_pattern(name, state, source="vision", weight=weight,
                          tags=tags,
                          notes=f"Canonical pattern from {count} samples. Vector: {list(vec)}")
        print(f"  Created: {name} (w={weight:.1f}, {count} samples)")
    else:
        print(f"  Skipped (single sample): vec={list(vec)}")

# Promote to golden
for name in list(memory.patterns.keys()):
    if name.startswith("CANONICAL_"):
        for _ in range(3):
            memory.record_match(name, success=True)
        memory.promote_to_golden(name)

print(f"\nFinal pattern count: {len(memory.patterns)}")
goldens = memory.get_golden_patterns()
print(f"Golden patterns: {len(goldens)}")
for g in goldens:
    print(f"  {g.name}: vec={g.state.direction_vector} weight={g.weight} success=%{g.success_rate:.0f}")

# Quick match test
print(f"\n--- Match Test ---")
test = IndicatorState()
test.div1_dir = 1; test.div2_dir = 1; test.div3_dir = 1
test.div5_dir = 1; test.div6_dir = 1; test.obv_dir = 1
test.div1 = 40; test.div2 = 25; test.div3 = 20
test.div5 = 12; test.div6 = 15; test.obv_norm = 0.4

match = memory.find_best_match(test, min_similarity=0.70)
if match:
    print(f"Full bull query -> Matched: {match.pattern.name} (%{match.similarity:.1f})")
else:
    print(f"Full bull query -> No match (unexpected)")

test2 = IndicatorState()
test2.div1_dir = 1; test2.div2_dir = -1; test2.div3_dir = 1
test2.div5_dir = 1; test2.div6_dir = 1; test2.obv_dir = 1

match2 = memory.find_best_match(test2, min_similarity=0.70)
if match2:
    print(f"Surround query -> Matched: {match2.pattern.name} (%{match2.similarity:.1f})")
else:
    print(f"Surround query -> No match")

print("\nDone!")
