from app.ml.optimizer import redeploy


def test_spare_unit_moves_to_open_slot():
    units = [dict(id="a1", home="A", tpd=100), dict(id="b1", home="B", tpd=100),
             dict(id="b2", home="B", tpd=100)]
    res = redeploy(units, slots={"A": 2, "B": 1}, weather_loss={"A": 0.1, "B": 0.5}, horizon=7)
    assert len(res["moves"]) == 1 and res["moves"][0]["to"] == "A"
    assert res["expected_tonnes"] > 0


def test_no_move_when_gain_is_small():
    units = [dict(id="a1", home="A", tpd=100), dict(id="b1", home="B", tpd=100)]
    res = redeploy(units, slots={"A": 2, "B": 2}, weather_loss={"A": 0.1, "B": 0.1}, horizon=7)
    assert res["moves"] == [] and res["expected_tonnes"] == 0.0
