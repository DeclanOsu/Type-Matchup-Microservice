"""
Gen 3 type chart (Ruby/Sapphire/Emerald, FireRed/LeafGreen).

17 types. Fairy does not exist in Gen 3.

One thing worth knowing: Steel did not resist Ghost or Dark until Gen 6.
Both are 1.0 here, which is correct for Gen 3.

Only non-1.0 matchups are stored. Everything else defaults to 1.0 at query
time. Combined dual-type multipliers are calculated by the calling code.

This is the only file that needs to change if the type chart needs updating.
"""

TYPES: list[str] = [
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel",
]

TYPE_CHART: dict[str, dict[str, float]] = {
    "normal": {
        "rock":   0.5,
        "steel":  0.5,
        "ghost":  0,
    },
    "fire": {
        "fire":   0.5,
        "water":  0.5,
        "rock":   0.5,
        "dragon": 0.5,
        "grass":  2,
        "ice":    2,
        "bug":    2,
        "steel":  2,
    },
    "water": {
        "water":  0.5,
        "grass":  0.5,
        "dragon": 0.5,
        "fire":   2,
        "ground": 2,
        "rock":   2,
    },
    "electric": {
        "electric": 0.5,
        "grass":    0.5,
        "dragon":   0.5,
        "ground":   0,
        "water":    2,
        "flying":   2,
    },
    "grass": {
        "fire":    0.5,
        "grass":   0.5,
        "poison":  0.5,
        "flying":  0.5,
        "bug":     0.5,
        "dragon":  0.5,
        "steel":   0.5,
        "water":   2,
        "ground":  2,
        "rock":    2,
    },
    "ice": {
        "water":  0.5,
        "ice":    0.5,
        "steel":  0.5,
        "fire":   0.5,
        "grass":  2,
        "ground": 2,
        "flying": 2,
        "dragon": 2,
    },
    "fighting": {
        "poison":  0.5,
        "flying":  0.5,
        "psychic": 0.5,
        "bug":     0.5,
        "ghost":   0,
        "normal":  2,
        "ice":     2,
        "rock":    2,
        "dark":    2,
        "steel":   2,
    },
    "poison": {
        "poison":  0.5,
        "ground":  0.5,
        "rock":    0.5,
        "ghost":   0.5,
        "steel":   0,
        "grass":   2,
    },
    "ground": {
        "grass":    0.5,
        "bug":      0.5,
        "flying":   0,
        "fire":     2,
        "electric": 2,
        "poison":   2,
        "rock":     2,
        "steel":    2,
    },
    "flying": {
        "electric": 0.5,
        "rock":     0.5,
        "steel":    0.5,
        "grass":    2,
        "fighting": 2,
        "bug":      2,
    },
    "psychic": {
        "psychic":  0.5,
        "steel":    0.5,
        "dark":     0,
        "fighting": 2,
        "poison":   2,
    },
    "bug": {
        "fire":     0.5,
        "fighting": 0.5,
        "flying":   0.5,
        "ghost":    0.5,
        "steel":    0.5,
        "grass":    2,
        "psychic":  2,
        "dark":     2,
    },
    "rock": {
        "fighting": 0.5,
        "ground":   0.5,
        "steel":    0.5,
        "fire":     2,
        "ice":      2,
        "flying":   2,
        "bug":      2,
    },
    "ghost": {
        "normal":  0,
        "dark":    0.5,
        "steel":   0.5,
        "ghost":   2,
        "psychic": 2,
    },
    "dragon": {
        "steel":  0.5,
        "dragon": 2,
    },
    "dark": {
        "fighting": 0.5,
        "dark":     0.5,
        "steel":    0.5,
        "ghost":    2,
        "psychic":  2,
    },
    "steel": {
        "steel":    0.5,
        "fire":     0.5,
        "water":    0.5,
        "electric": 0.5,
        "ice":      2,
        "rock":     2,
        # Ghost and Dark are intentionally absent (1.0 in Gen 3).
    },
}

VALID_TYPES: frozenset[str] = frozenset(TYPES)


def get_single_matchup(attacking: str, defending: str) -> float:
    """Returns the effectiveness of one type against another. Defaults to 1.0."""
    return TYPE_CHART.get(attacking, {}).get(defending, 1.0)
