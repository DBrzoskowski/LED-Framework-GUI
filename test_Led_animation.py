import unittest
import math
from unittest.mock import patch
from Led_animation import Cube3D, vector


class TestCube3D(unittest.TestCase):
    def setUp(self):
        self.cube = Cube3D(8, 0.15 * 1, 1, 0.1 * 1 * math.sqrt(1 / 1))
        self.cube.initialize()

    def tearDown(self):
        self.cube.delete()

    def test_hex2vector(self):
        hex_red_color = '#FF0000'
        vector_red = vector(1, 0, 0)
        self.assertEqual(self.cube.hex2vector(hex_red_color),  vector_red)

    def test_hex2vector_incorrect_result(self):
        hex_red_color = '#FF0000'
        vector_red = vector(1, 0, 1)
        self.assertNotEqual(self.cube.hex2vector(hex_red_color),  vector_red)

    def test_hex2vector_result_none(self):
        hex_red_color = 'FF0000'
        self.assertEqual(self.cube.hex2vector(hex_red_color),  None)

    @patch('Led_animation.Cube3D.get_led_from_visible', return_value=[1, 0, 0])
    def test_get_led_from_visible(self, mocked):
        result = [1, 0, 0]
        get_led_from_visible = self.cube.get_led_from_visible(result)
        mocked.assert_called_once()
        self.assertEqual(get_led_from_visible, result)

    @patch('Led_animation.Cube3D.get_led_from_visible', return_value=[1, 0, 0])
    def test_get_led_from_visible_incorrect_result(self, mocked):
        result = [0, 0, 0]
        get_led_from_visible = self.cube.get_led_from_visible(result)
        mocked.assert_called_once()
        self.assertNotEqual(get_led_from_visible, result)
