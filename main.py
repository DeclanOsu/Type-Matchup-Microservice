"""
Type matchup service (Gen 3).

GET /health
GET /type-matchup?attacking=<type>&defending=<type>[,<type>]
GET /type-chart
"""

from math import prod
from flask import Flask, jsonify, request
from data.type_chart import TYPES, VALID_TYPES, get_single_matchup

app = Flask(__name__)


def validated_type(raw: str) -> str | None:
    """Returns the lowercased type name if valid, otherwise None."""
    normalised = raw.strip().lower()
    return normalised if normalised in VALID_TYPES else None


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "type-matchup"})


@app.get("/type-matchup")
def type_matchup():
    """
    Returns the combined damage multiplier for an attacking type against
    one or two defending types.

    Query params:
        attacking  - attacking move type
        defending  - one or two defending types, comma-separated

    Returns 400 if any type name is not valid for Gen 3.
    """
    attacking_raw = request.args.get("attacking", "").strip()
    defending_raw = request.args.get("defending", "").strip()

    if not attacking_raw:
        return jsonify({
            "error": "Bad Request",
            "message": '"attacking" is required.',
        }), 400

    attacking = validated_type(attacking_raw)
    if attacking is None:
        return jsonify({
            "error": "Bad Request",
            "message": (
                f'"{attacking_raw}" is not a valid Gen 3 type. '
                f'Valid types: {", ".join(TYPES)}.'
            ),
        }), 400

    if not defending_raw:
        return jsonify({
            "error": "Bad Request",
            "message": '"defending" is required. Provide one or two types, comma-separated.',
        }), 400

    raw_defenders = [t for t in defending_raw.split(",") if t.strip()]

    if not raw_defenders or len(raw_defenders) > 2:
        return jsonify({
            "error": "Bad Request",
            "message": '"defending" must contain one or two type names.',
        }), 400

    defending: list[str] = []
    for raw in raw_defenders:
        valid = validated_type(raw)
        if valid is None:
            return jsonify({
                "error": "Bad Request",
                "message": (
                    f'"{raw.strip()}" is not a valid Gen 3 type. '
                    f'Valid types: {", ".join(TYPES)}.'
                ),
            }), 400
        defending.append(valid)

    breakdown = [
        {"defending": d, "multiplier": get_single_matchup(attacking, d)}
        for d in defending
    ]
    multiplier = prod(get_single_matchup(attacking, d) for d in defending)

    return jsonify({
        "attacking_type": attacking,
        "defending_types": defending,
        "multiplier": multiplier,
        "breakdown": breakdown,
    })


@app.get("/type-chart")
def type_chart():
    """
    Returns the full Gen 3 type chart as a 17x17 matrix. Every
    attacker/defender pair is explicitly present, so callers can do a
    straightforward chart[attacker][defender] lookup.
    """
    chart = {
        attacking: {
            defending: get_single_matchup(attacking, defending)
            for defending in TYPES
        }
        for attacking in TYPES
    }
    return jsonify({"generation": 3, "types": TYPES, "chart": chart})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found", "message": str(e)}), 404


if __name__ == "__main__":
    app.run(port=3002, debug=False)
