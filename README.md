# type-matchup-service

Calculates Gen 3 damage multipliers given an attacking type and one or two defending types. Part of the Pokemon damage calculator backend.

**Gen 3 specifics:** 17 types (no Fairy). Steel does not resist Ghost or Dark - that changed in Gen 6. All matchups reflect RSE/FRLG.

## Endpoints

### `GET /type-matchup`

Query params:

| Param | Required | Description |
|---|---|---|
| `attacking` | Yes | Attacking move type |
| `defending` | Yes | One or two defending types, comma-separated |

Input is case-insensitive. Returns `400` if any type name is not valid for Gen 3.

**Single defending type:**

```
GET /type-matchup?attacking=fire&defending=grass
```

```json
{
    "attacking_type": "fire",
    "defending_types": ["grass"],
    "multiplier": 2.0,
    "breakdown": [
        { "defending": "grass", "multiplier": 2.0 }
    ]
}
```

**Dual defending type:**

```
GET /type-matchup?attacking=fire&defending=grass,steel
```

```json
{
    "attacking_type": "fire",
    "defending_types": ["grass", "steel"],
    "multiplier": 4.0,
    "breakdown": [
        { "defending": "grass", "multiplier": 2.0 },
        { "defending": "steel", "multiplier": 2.0 }
    ]
}
```

Possible `multiplier` values: `0.0`, `0.25`, `0.5`, `1.0`, `2.0`, `4.0`

---

### `GET /type-chart`

Returns the full Gen 3 chart as a 17x17 matrix. Every attacker/defender pair is explicitly present, so you can do `chart[attacker][defender]` without handling missing keys.

```json
{
    "generation": 3,
    "types": ["normal", "fire", "water", ...],
    "chart": {
        "fire": {
            "normal": 1.0,
            "fire": 0.5,
            "water": 0.5,
            "grass": 2.0,
            ...
        },
        ...
    }
}
```

---

### `GET /health`

```json
{ "status": "ok", "service": "type-matchup" }
```

---

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Runs on port `3002` by default.

## Tests

```bash
pytest
```

## Structure

```
type-matchup-service/
+-- main.py
+-- requirements.txt
+-- pytest.ini
+-- data/
|   `-- type_chart.py   <- edit type chart data here
`-- tests/
    `-- test_main.py
```

All type chart data is in `data/type_chart.py`. That is the only file that needs to change if a matchup needs updating.
"# Type-Matchup-Microservice" 
