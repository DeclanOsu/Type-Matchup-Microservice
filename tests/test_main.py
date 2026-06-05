import time
import pytest
from main import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestSingleDefendingType:
    def test_super_effective(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 2.0

    def test_not_very_effective(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=water")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 0.5

    def test_immune(self, client):
        r = client.get("/type-matchup?attacking=normal&defending=ghost")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 0.0

    def test_neutral(self, client):
        r = client.get("/type-matchup?attacking=water&defending=normal")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 1.0

    # Steel did not resist Ghost or Dark until Gen 6
    def test_steel_vs_ghost_neutral_in_gen3(self, client):
        r = client.get("/type-matchup?attacking=steel&defending=ghost")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 1.0

    def test_steel_vs_dark_neutral_in_gen3(self, client):
        r = client.get("/type-matchup?attacking=steel&defending=dark")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 1.0

    def test_poison_vs_steel_immune(self, client):
        r = client.get("/type-matchup?attacking=poison&defending=steel")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 0.0

    def test_case_insensitive(self, client):
        r = client.get("/type-matchup?attacking=FIRE&defending=Grass")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 2.0

    def test_response_includes_breakdown(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass")
        body = r.get_json()
        assert "breakdown" in body
        assert body["breakdown"] == [{"defending": "grass", "multiplier": 2.0}]

    def test_response_shape(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass")
        body = r.get_json()
        assert body["attacking_type"] == "fire"
        assert body["defending_types"] == ["grass"]
        assert "multiplier" in body
        assert "breakdown" in body

    def test_multiplier_is_numeric(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass")
        assert isinstance(r.get_json()["multiplier"], (int, float))


class TestDualDefendingType:
    def test_4x(self, client):
        # Fire vs Grass/Steel: 2 * 2 = 4
        r = client.get("/type-matchup?attacking=fire&defending=grass,steel")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 4.0

    def test_quarter_x(self, client):
        # Water vs Water/Dragon: 0.5 * 0.5 = 0.25
        r = client.get("/type-matchup?attacking=water&defending=water,dragon")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == pytest.approx(0.25)

    def test_immunity_in_dual(self, client):
        # Electric vs Ground/Flying: 0 * 2 = 0
        r = client.get("/type-matchup?attacking=electric&defending=ground,flying")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 0.0

    def test_neutral_dual(self, client):
        r = client.get("/type-matchup?attacking=normal&defending=fire,water")
        assert r.status_code == 200
        assert r.get_json()["multiplier"] == 1.0

    def test_breakdown_has_two_entries(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass,steel")
        breakdown = r.get_json()["breakdown"]
        assert len(breakdown) == 2
        assert breakdown[0] == {"defending": "grass", "multiplier": 2.0}
        assert breakdown[1] == {"defending": "steel", "multiplier": 2.0}

    def test_defending_types_in_response(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass,steel")
        assert r.get_json()["defending_types"] == ["grass", "steel"]


class TestValidation:
    def test_unknown_attacking_type(self, client):
        r = client.get("/type-matchup?attacking=faketype&defending=fire")
        assert r.status_code == 400
        assert "error" in r.get_json()
        assert "message" in r.get_json()

    def test_unknown_defending_type(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=notreal")
        assert r.status_code == 400

    def test_fairy_not_in_gen3(self, client):
        r = client.get("/type-matchup?attacking=fairy&defending=dragon")
        assert r.status_code == 400

    def test_missing_attacking(self, client):
        r = client.get("/type-matchup?defending=grass")
        assert r.status_code == 400

    def test_missing_defending(self, client):
        r = client.get("/type-matchup?attacking=fire")
        assert r.status_code == 400

    def test_three_defending_types_rejected(self, client):
        r = client.get("/type-matchup?attacking=fire&defending=grass,steel,water")
        assert r.status_code == 400


class TestTypeChart:
    def test_returns_17_types(self, client):
        r = client.get("/type-chart")
        assert r.status_code == 200
        body = r.get_json()
        assert len(body["types"]) == 17
        assert body["generation"] == 3

    def test_no_fairy(self, client):
        r = client.get("/type-chart")
        assert "fairy" not in r.get_json()["types"]

    def test_complete_17x17_matrix(self, client):
        r = client.get("/type-chart")
        body = r.get_json()
        types = body["types"]
        chart = body["chart"]
        for atk in types:
            assert atk in chart
            for def_ in types:
                assert def_ in chart[atk]
                assert isinstance(chart[atk][def_], (int, float))

    @pytest.mark.parametrize("atk,def_,expected", [
        ("fire",     "grass",    2.0),
        ("fire",     "water",    0.5),
        ("electric", "ground",   0.0),
        ("ghost",    "normal",   0.0),
        ("ghost",    "psychic",  2.0),
        ("dark",     "psychic",  2.0),
        ("steel",    "ice",      2.0),
        ("steel",    "ghost",    1.0),
        ("steel",    "dark",     1.0),
        ("fighting", "ghost",    0.0),
        ("poison",   "steel",    0.0),
        ("dragon",   "dragon",   2.0),
        ("psychic",  "dark",     0.0),
        ("normal",   "ghost",    0.0),
        ("bug",      "dark",     2.0),
        ("water",    "water",    0.5),
        ("grass",    "dragon",   0.5),
    ])
    def test_known_matchup(self, client, atk, def_, expected):
        chart = client.get("/type-chart").get_json()["chart"]
        assert chart[atk][def_] == expected

    def test_response_under_200ms(self, client):
        start = time.monotonic()
        client.get("/type-chart")
        assert (time.monotonic() - start) * 1000 < 200


class TestHealth:
    def test_returns_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"
