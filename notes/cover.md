# Set-cover search for the skipped-seed criterion

135 non-constant predicates; 29 are false on all 8 published curves and so usable in a cover.

**True labelling:** minimal cover size = 4; 10 distinct minimal covers. Examples:

- 20(i-1) mod 4096 < 1024 ∪ b ≡ 1 mod 7 ∪ n ≡ 7 mod 8 ∪ t ≡ 0 mod 7
- 20(i-1) mod 4096 < 1024 ∪ b ≡ 1 mod 7 ∪ t ≡ 0 mod 7 ∪ t ≡ 1 mod 8
- 20(i-1) mod 4096 < 1024 ∪ b ≡ 7 mod 16 ∪ n ≡ 7 mod 8 ∪ t ≡ 0 mod 7
- 20(i-1) mod 4096 < 1024 ∪ b ≡ 7 mod 16 ∪ t ≡ 0 mod 7 ∪ t ≡ 1 mod 8
- 20(i-1) mod 4096 < 1024 ∪ b ≡ 7 mod 8 ∪ n ≡ 7 mod 8 ∪ t ≡ 0 mod 7
- 20(i-1) mod 4096 < 1024 ∪ b ≡ 7 mod 8 ∪ t ≡ 0 mod 7 ∪ t ≡ 1 mod 8
- b ≡ 1 mod 7 ∪ b ≡ 2 mod 7 ∪ b ≡ 4 mod 16 ∪ t ≡ 1 mod 8
- b ≡ 1 mod 7 ∪ b ≡ 2 mod 7 ∪ b ≡ 4 mod 16 ∪ t ≡ 9 mod 16
- b ≡ 2 mod 7 ∪ b ≡ 4 mod 16 ∪ b ≡ 7 mod 16 ∪ t ≡ 1 mod 8
- b ≡ 2 mod 7 ∪ b ≡ 4 mod 16 ∪ b ≡ 7 mod 8 ∪ t ≡ 1 mod 8

Best single usable predicates (how many of the 11 skipped each covers):

- 6/11  t ≡ 1 mod 8
- 5/11  20(i-1) mod 4096 < 1024
- 4/11  t ≡ 9 mod 16
- 4/11  n ≡ 7 mod 8
- 4/11  b ≡ 4 mod 16
- 3/11  t ≡ 0 mod 7
- 3/11  n ≡ 9 mod 16
- 3/11  n ≡ 3 mod 5

**Exact permutation test** (126 relabellings preserving per-run published counts and keeping each final candidate published): distribution of minimal cover size

- size 2: 1 (0.8%)
- size 3: 35 (27.8%)
- size 4: 52 (41.3%)
- size 5: 23 (18.3%)
- size None: 15 (11.9%)

Fraction with cover size at most 4: 0.6984.

This null conditions on the observed stopping endpoints. It replaces the exploratory 300-sample, count-only null (35%). The predicate library was selected during exploration, so neither comparison is a confirmatory test of all possible selection rules.
