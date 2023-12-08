import pytest
from e2D import *
import sys

def test_Vector2D_V2_init() -> None:
    vec = Vector2D(1, 2)
    assert vec.x == vec[0] == vec["x"] == 1
    assert vec.y == vec[1] == vec["y"] == 2

def test_Vector2D_V2_set() -> None:
    vec = Vector2D(1, 2)
    vec.set(2, 3)
    assert vec == Vector2D(2, 3)

def test_Vector2D_V2_distance_to() -> None:
    vec1 = Vector2D(0, 0)
    vec2 = Vector2D(3, 4)
    result = vec1.distance_to(vec2)
    assert result == 5.0
    result = vec1.distance_to(vec2, sqrd=False)
    assert result == 25.0

def test_Vector2D_V2_angle_to() -> None:
    vec1 = Vector2D(1, 2)
    vec2 = Vector2D(3, 4)
    angle = vec1.angle_to(vec2)
    assert angle == 0.7853981633974483

def test_Vector2D_V2_point_from_degs() -> None:
    vec1 = Vector2D(1, 2)
    degs = 60
    radius = 4
    vec2 = vec1.point_from_degs(degs, radius)
    assert vec2 == Vector2D(3.0000000000000004, 5.464101615137754)

def test_Vector2D_V2_point_from_rads() -> None:
    vec1 = Vector2D(1, 2)
    rads = PI / 3
    radius = 4
    vec2 = vec1.point_from_rads(rads, radius)
    assert vec2 == Vector2D(3.0000000000000004, 5.464101615137754)

def test_Vector2D_V2_sign() -> None:
    vec1 = Vector2D(1, 2).sign()
    assert vec1 == Vector2D(1, 1)
    vec1 = Vector2D(-1, 0).sign()
    assert vec1 == Vector2D(-1, 0)
    
def test_Vector2D_V2_floor() -> None:
    vec1 = Vector2D(1.5978623478332743, 6.985950086321505)
    vec2 = vec1.floor()
    assert vec2 == Vector2D(1, 6)
    vec2 = vec1.floor(5)
    assert vec2 == Vector2D(0, 5)
    vec2 = vec1.floor(.01)
    assert vec2 == Vector2D(1.59, 6.98)

def test_Vector2D_V2_ceil() -> None:
    vec1 = Vector2D(1.5978623478332743, 6.985950086321505)
    vec2 = vec1.ceil()
    assert vec2 == Vector2D(2, 7)
    vec2 = vec1.ceil(5)
    assert vec2 == Vector2D(5, 10)
    vec2 = vec1.ceil(.01)
    assert vec2 == Vector2D(1.6, 6.99)

def test_Vector2D_V2_round() -> None:
    vec1 = Vector2D(1.5978623478332743, 6.985950086321505)
    vec2 = vec1.round()
    assert vec2 == Vector2D(2, 7)
    vec2 = vec1.round(5)
    assert vec2 == Vector2D(0, 5)
    vec2 = vec1.round(.01)
    assert vec2 == Vector2D(1.6, 6.99)

def test_Vector2D_V2_dot_product() -> None:
    vec1 = Vector2D(1, 2)
    vec2 = Vector2D(1, 2)
    dot = vec1.dot_product(vec2)
    assert dot == 5.0

def test_Vector2D_V2_normalize() -> None:
    vec1 = Vector2D(1, 2)
    norm = vec1.normalize()
    assert norm == V2(0.4472135954999579, 0.8944271909999159)

def test_Vector2D_V2_projection() -> None:
    vec1 = Vector2D(1, 2)
    vec2 = Vector2D(3, 4)
    proj = vec1.projection(vec2)
    assert proj == Vector2D(1.32, 1.76)

def test_Vector2D_V2_reflection() -> None:
    vec1 = Vector2D(1, 2)
    vec2 = Vector2D(3, 4)
    refl = vec1.reflection(vec2)
    assert refl == Vector2D(-1.6400000000000001, -1.52)

def test_Vector2D_V2_cartesian_to_polar() -> None:
    vec1 = Vector2D(1, 2)
    polar = vec1.cartesian_to_polar()
    assert polar == (2.23606797749979, 1.1071487177940904)

def test_Vector2D_V2_polar_to_cartesian() -> None:
    vec1 = V2.polar_to_cartesian(1, 2)
    assert vec1 == Vector2D(-0.4161468365471424, 0.9092974268256817)

def test_Vector2D_V2_cartesian_to_complex() -> None:
    vec1 = Vector2D(1, 2)
    complex_coords = vec1.cartesian_to_complex()
    assert complex_coords == (1+2j)

def test_Vector2D_V2_complex_to_cartesian() -> None:
    vec1 = V2.complex_to_cartesian(1+2j)
    assert vec1 == Vector2D(1.0, 2.0)

def test_Vector2D_V2_length() -> None:
    vec1 = Vector2D(1, 2)
    length = vec1.length()
    assert length == 2.23606797749979

def test_Vector2D_V2_rotate() -> None:
    vec1 = Vector2D(3.0, 4.0)
    rotated_vec = vec1.rotate(QUARTER_PI)()
    assert rotated_vec == pytest.approx([-0.7071067811865475, 4.949747468305834])
    center = Vector2D(1.0, 1.0)
    rotated_vec_center = vec1.rotate(QUARTER_PI, center)()
    assert rotated_vec_center == pytest.approx([.2928932188134523, 4.535533905932738])
    center = Vector2D(2.0, 2.0)
    vec2 = Vector2D(3.0, 3.0)
    rotated_vec_neg = vec2.rotate(-HALF_PI, center)()
    assert rotated_vec_neg == pytest.approx([3.0, 1.0])

def test_Vector2D_V2_no_zero_div_error() -> None:
    vector1 = Vector2D(3, 4)
    result1 = vector1.no_zero_div_error(2)
    assert result1 == Vector2D(1.5, 2)
    vector2 = Vector2D(5, 0)
    result2 = vector1.no_zero_div_error(vector2, error_mode="zero")
    assert result2 == Vector2D(.6, 0)
    result3 = vector1.no_zero_div_error(vector2, error_mode="null")
    assert result3 == Vector2D(.6, 4)
    vector3 = Vector2D(2, 2)
    result4 = vector1.no_zero_div_error(vector3)
    assert result4 == Vector2D(1.5, 2)
    vector4 = Vector2D(0, 2)
    result5 = vector1.no_zero_div_error(vector4, error_mode="zero")
    assert result5 == Vector2D(0, 2.0)
    result6 = vector1.no_zero_div_error(vector4, error_mode="null")
    assert result6 == Vector2D(3, 2)
    try:
        vector1.no_zero_div_error("invalid_input") #type: ignore
    except Exception as e:
        assert str(e) == "\nArg n must be in [Vector2D, int, float, tuple, list] not a [<class 'str'>]\n"

def test_Vector2D_V2_min_max() -> None:
    vector1 = Vector2D(3, 4)
    result_min_numeric = vector1.min(2)
    assert result_min_numeric == Vector2D(2, 2)
    vector2 = Vector2D(5, 2)
    result_min_vector = vector1.min(vector2)
    assert result_min_vector == Vector2D(3, 2)
    result_max_numeric = vector1.max(2)
    assert result_max_numeric == Vector2D(3, 4)
    result_max_vector = vector1.max(vector2)
    assert result_max_vector == Vector2D(5, 4)

def test_Vector2D_V2_arithmetic_operations() -> None:
    vector1 = Vector2D(3, 4)
    added_vector = vector1 + Vector2D(1, 2)
    assert added_vector == Vector2D(4, 6)
    subtracted_vector = vector1 - Vector2D(1, 2)
    assert subtracted_vector == Vector2D(2, 2)
    multiplied_vector = vector1 * Vector2D(2, 3)
    assert multiplied_vector == Vector2D(6, 12)
    modulo_vector = vector1 % Vector2D(2, 3)
    assert modulo_vector == Vector2D(1, 1)
    power_vector = vector1 ** Vector2D(2, 3)
    assert power_vector == Vector2D(9, 64)
    div_vector = vector1 / Vector2D(2, 4)
    assert div_vector == Vector2D(1.5, 1)
    floor_div_vector = vector1 // Vector2D(2, 3)
    assert floor_div_vector == Vector2D(1, 1)

def test_Vector2D_V2_reverse_arithmetic_operations() -> None:
    vector1 = Vector2D(3, 4)
    reversed_added_vector = 2 + vector1
    assert reversed_added_vector == Vector2D(5, 6)
    reversed_subtracted_vector = 2 - vector1
    assert reversed_subtracted_vector == Vector2D(-1, -2)
    reversed_multiplied_vector = 2 * vector1
    assert reversed_multiplied_vector == Vector2D(6, 8)
    reversed_modulo_vector = 2 % vector1
    assert reversed_modulo_vector == Vector2D(2, 2)
    reversed_power_vector = 2 ** vector1
    assert reversed_power_vector == Vector2D(8, 16)
    reversed_div_vector = 2 / vector1
    assert reversed_div_vector == Vector2D(2/3, 0.5)
    reversed_floor_div_vector = 2 // vector1
    assert reversed_floor_div_vector == Vector2D(0, 0)

def test_Vector2D_V2_inplace_arithmetic_operations() -> None:
    vector1 = Vector2D(3, 4)
    vector2 = Vector2D(1, 2)
    vector1_copy = vector1.copy()
    vector1_copy += vector2
    assert vector1_copy == vector1 + vector2
    vector1_copy = vector1.copy()
    vector1_copy -= vector2
    assert vector1_copy == vector1 - vector2
    vector1_copy = vector1.copy()
    vector1_copy *= vector2
    assert vector1_copy == vector1 * vector2
    vector1_copy = vector1.copy()
    vector1_copy /= vector2
    assert vector1_copy == vector1 / vector2
    vector1_copy = vector1.copy()
    vector1_copy %= vector2
    assert vector1_copy == vector1 % vector2
    vector1_copy = vector1.copy()
    vector1_copy **= vector2
    assert vector1_copy == vector1 ** vector2
    vector1_copy = vector1.copy()
    vector1_copy //= vector2
    assert vector1_copy == vector1 // vector2

def test_Vector2D_equality_operations() -> None:
    vector1 = Vector2D(3, 4)
    vector2 = Vector2D(3, 4)
    vector3 = Vector2D(1, 2)
    assert vector1 == vector2
    assert not vector1 == vector3
    assert vector1 != vector3
    assert not vector1 != vector2
    v2_vector = V2(3, 4)
    assert vector1 == v2_vector
    assert not vector1 != v2_vector
    list_vector = [3, 4]
    assert vector1 == list_vector
    assert not vector1 != list_vector
    tuple_vector = (3, 4)
    assert vector1 == tuple_vector
    assert not vector1 != tuple_vector

def test_Vector2D_normalize() -> None:
    vector1 = Vector2D(3, 4)
    vector2 = Vector2D(1, 2)
    normalized_vector = vector1.__normalize__(vector2)
    assert normalized_vector == vector2
    v2_vector = V2(3, 4)
    normalized_vector = vector1.__normalize__(v2_vector)
    assert normalized_vector == v2_vector
    int_value = 5
    normalized_vector = vector1.__normalize__(int_value)
    assert normalized_vector == Vector2D(int_value, int_value)
    float_value = 3.5
    normalized_vector = vector1.__normalize__(float_value)
    assert normalized_vector == Vector2D(float_value, float_value)
    list_value = [2, 3]
    normalized_vector = vector1.__normalize__(list_value)
    assert normalized_vector == Vector2D(2, 3)
    tuple_value = (4, 5)
    normalized_vector = vector1.__normalize__(tuple_value)
    assert normalized_vector == Vector2D(4, 5)

def test_color_functions() -> None:
    interpolated_color = color_lerp((255, 0, 0), (0, 0, 255), 0.5)
    assert interpolated_color == pytest.approx((127.5, 0.0, 127.5))
    color_at_index = color_fade((255, 0, 0), (0, 0, 255), 50, 100)
    assert color_at_index == pytest.approx((127.5, 0.0, 127.5))
    colors_dict = {(255, 255, 255): 0.1, (0, 0, 0): 0.9}
    weighted_color = weighted_color_fade(colors_dict)
    assert weighted_color == (25.5, 25.5, 25.5)
    squared_distance = color_distance([255, 0, 0], [0, 255, 0])
    assert squared_distance == 360.62445840513925
    distance = color_distance([255, 0, 0], [0, 255, 0], sqrd=False)
    assert distance == 130050

def test_angular_interpolation() -> None:
    starting_angle = 0.7167994059004553
    final_angle = 4.26734922253127
    interpolated_angle = angular_interpolation(starting_angle, final_angle, .1)
    assert interpolated_angle == -0.27326354905487715
    interpolated_angle = angular_interpolation(starting_angle, final_angle, 1)
    assert interpolated_angle == -2.7326354905487715
    starting_angle = 2.159458479718132
    final_angle = 0.9991081931615399
    interpolated_angle = angular_interpolation(starting_angle, final_angle, .3)
    assert interpolated_angle == -0.3481050859669777

def test_avg_position() -> None:
    pos1 = Vector2D(1, 2)
    pos2 = Vector2D(3, 4)
    average_pos_two = avg_position(pos1, pos2)
    assert average_pos_two == Vector2D(2, 3)
    pos3 = Vector2D(5, 6)
    average_pos_three = avg_position(pos1, pos2, pos3)
    assert average_pos_three == Vector2D(3, 4)
    pos4 = Vector2D(7, 8)
    pos5 = Vector2D(9, 10)
    average_pos_more = avg_position(pos1, pos2, pos3, pos4, pos5)
    assert average_pos_more == Vector2D(5, 6)

def test_inter_points() -> None:
    ray = [Vector2D(1, 2), Vector2D(5, 3)]
    lines = [(Vector2D(2, 2), Vector2D(4, 4)), (Vector2D(3, 3), Vector2D(6, 2))]
    result = inter_points(ray, lines, return_inter_lines=True, sort=True)
    assert result == [(V2(2.333333333333333, 2.333333333333333), (V2(2, 2), V2(4, 4))), (V2(3.8571428571428568, 2.7142857142857144), (V2(3, 3), V2(6, 2)))]
    ray = [Vector2D(1, 2), Vector2D(5, 3)]
    lines = [(Vector2D(6, 6), Vector2D(8, 8)), (Vector2D(7, 7), Vector2D(10, 6))]
    result = inter_points(ray, lines, return_inter_lines=True, sort=True)
    assert result == [(None, (V2(6, 6), V2(8, 8))), (None, (V2(7, 7), V2(10, 6)))]
    ray = [Vector2D(1, 2), Vector2D(5, 3)]
    lines = [(Vector2D(2, 2), Vector2D(4, 4)), (Vector2D(3, 3), Vector2D(6, 2))]
    result = inter_points(ray, lines, return_inter_lines=False, sort=True)
    assert result == [V2(2.333333333333333, 2.333333333333333), V2(3.8571428571428568, 2.7142857142857144)]

def test_get_points_and_lines() -> None:
    position = Vector2D(100, 100)
    size = Vector2D(50, 30)
    rotation = QUARTER_PI
    points = get_points(position, size, rotation)
    assert points == (V2(129.1401201201909, 99.07620382072331), V2(129.1544929786152, 100.12465616662436), V2(129.1038465300589, 101.72224189787013), V2(129.14695430317605, 100.67457753339954))
    lines = get_lines(position, size, rotation)
    assert lines == [[V2(129.1401201201909, 99.07620382072331), V2(129.1544929786152, 100.12465616662436)], [V2(129.1401201201909, 99.07620382072331), V2(129.1038465300589, 101.72224189787013)], [V2(129.1038465300589, 101.72224189787013), V2(129.14695430317605, 100.67457753339954)], [V2(129.14695430317605, 100.67457753339954), V2(129.1544929786152, 100.12465616662436)]]

def test_distance_line_point() -> None:
    line_point_a = Vector2D(0, 0)
    line_point_b = Vector2D(10, 0)
    point_c = Vector2D(5, 5)
    distance = distance_line_point(line_point_a, line_point_b, point_c)
    assert distance == 5.0

if __name__ == '__main__':
    exit_code = pytest.main()
    sys.exit(exit_code)