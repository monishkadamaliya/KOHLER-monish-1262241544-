from app.constraints.geometry import RectangleSpec, door_swing_polygon, rectangle_polygon, room_polygon


def test_fixture_inside_room():
    room = room_polygon(2400, 1800)
    fixture = rectangle_polygon(RectangleSpec(600, 450, 1200, 900))
    assert room.contains(fixture)


def test_fixture_outside_room():
    room = room_polygon(2400, 1800)
    fixture = rectangle_polygon(RectangleSpec(600, 450, 100, 100))
    assert not room.contains(fixture)


def test_collision_is_detectable():
    first = rectangle_polygon(RectangleSpec(600, 450, 1000, 900))
    second = rectangle_polygon(RectangleSpec(500, 400, 1200, 900))
    assert first.intersection(second).area > 0


def test_door_swing_has_area():
    swing = door_swing_polygon(0, 0, 750, 90, 0)
    assert swing.area > 0
