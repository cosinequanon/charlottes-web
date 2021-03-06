""" Generates an image that resembles a spider's web.  """
import hashlib
import math
import random

from math import sin, cos

import numpy as np
from PIL import Image, ImageDraw, ImageFont


color_white = (220, 220, 220)
color_black = (17, 17, 23)


class CharlottesWeb(object):
    """ Generates an image of a spider's web. """

    def __init__(self, image=None):
        self.im_scale = 2
        self.final_width = 1200
        self.final_height = int(self.final_width * (5 / 7))
        self.width = self.final_width * self.im_scale
        self.height = self.final_height * self.im_scale
        self.center = (self.width / 2, self.height / 2)

        self.web_lines = []
        self.line_color = (170, 188, 190, 1)
        self.num_circles = 50

        if image is not None:
            self.im = image
        else:
            self.im = Image.new(
                'RGBA',
                (self.width, self.height),
                color_black,
            )
        self.draw = ImageDraw.Draw(self.im)

    def draw_image(self, signature=False):
        self.draw_web_lines()
        self.draw_web_circles()
        self.erase_center()
        if signature:
            self.sign_image()
        self.im.resize((self.final_width, self.final_height))
        return self.im

    def show(self):
        self.im.show()

    def erase_center(self):
        center_point = Point(*self.center)
        self.draw_large_point(Point(*self.center), 16, color_black)

    def draw_web_circle(self, offset):
        # iterate over adjacent pairs of lines
        for i in range(len(self.web_lines)):
            # Sometimes the spider misses a connection
            if random.random() < 0.2:
                return
            line1 = self.web_lines[i]
            line2 = self.web_lines[(i + 1) % len(self.web_lines)]
            p1_positive, p1_negative = self.get_offset_points(line1, offset)
            p2_positive, p2_negative = self.get_offset_points(line2, offset)

            # There are two sets of lines we could draw, always draw lines that
            # are shorter
            off_line_positive_1 = Line(p1_positive, p2_positive)
            off_line_positive_2 = Line(p1_positive, p2_negative)
            off_line_negative_1 = Line(p1_negative, p2_positive)
            off_line_negative_2 = Line(p1_negative, p2_negative)


            if off_line_positive_1.length < off_line_positive_2.length:
                self.draw_web_bezier(off_line_positive_1, self.line_color)
                self.draw_web_bezier(off_line_negative_2, self.line_color)
            else:
                self.draw_web_bezier(off_line_positive_2, self.line_color)
                self.draw_web_bezier(off_line_negative_1, self.line_color)

    def draw_web_circles(self):
        growth_rate = 1.5
        min_offset = math.log(1)
        max_offset = math.log(self.height * growth_rate * 10)
        log_space = np.linspace(min_offset, max_offset, num=self.num_circles)
        random_var = np.array(
            [0.05 * random.random() for _ in range(self.num_circles)],
        )
        for log_off in (log_space + random_var):
            offset = math.exp(log_off / growth_rate) * max_offset + 10
            self.draw_web_circle(offset)

    def draw_web_lines(self):
        num_lines = 8
        for line in range(num_lines // 2):
            start = Point(0, 1.5 * self.height // 2)
            end = Point(0, -1.5 * self.height // 2)
            theta = 2 * math.pi * (line / num_lines)
            theta += (random.random() - 0.5) / 20
            nstart = self.trans_to_pil(start.rotate(theta))
            nend = self.trans_to_pil(end.rotate(theta))
            web_line = Line(nstart, nend)

            self.draw_line(web_line, fill=self.line_color, width=1)
            self.web_lines.append(web_line)

    def draw_line(self, line, fill=color_white, width=0):
        self.draw.line(line.to_tuple(), fill=fill, width=width)

    def draw_point(self, point, fill=color_white):
        self.draw.point(point.to_tuple(), fill=fill)

    def draw_large_point(self, point, size=3, fill=color_white):
        """ To debug things. """
        p1 = point - size
        p2 = point + size
        self.draw.ellipse(
            p1.to_tuple() + p2.to_tuple(),
            fill=fill,
        )

    def draw_web_bezier(self, line, fill=color_white):
        A, C = line.get_points()
        x_midpoint = A.x + C.x / 2
        perp_y_inter = A.y - line.slope * A.x
        B_no_offset = Point(x_midpoint, line.slope * A.x + perp_y_inter)
        B_no_offset = (A + C) / 2

        if self.trans_to_cartesian(B_no_offset).x < 0:
            direction = 1
        else:
            direction = -1

        offset = line.length * 0.3 * direction * (random.random() + 1.5) / 160

        y_inter = B_no_offset.y - (-1 / line.slope) * B_no_offset.x
        B = Point(
            B_no_offset.x + offset,
            (-1 / line.slope) * (B_no_offset.x + offset) + y_inter
        )

        p_prev = C
        for t in np.linspace(0, 1, 20):
            p1 = A * t + (1 - t) * B
            p2 = B * t + (1 - t) * C
            p_final = p1 * t + (1 - t) * p2
            self.draw_line(Line(p_prev, p_final), fill)
            p_prev = p_final

    def get_offset_points(self, line, offset):
        p1 = self.trans_to_cartesian(line.p1)
        p2 = self.trans_to_cartesian(line.p2)
        cart_line = Line(p1, p2)
        x_offset = math.sqrt((offset ** 2) / (1 + cart_line.slope ** 2))
        y_offset = x_offset * cart_line.slope
        return (
            self.trans_to_pil(Point(x_offset, y_offset)),
            self.trans_to_pil(Point(-x_offset, -y_offset)),
        )

    def sign_image(self):
        font = ImageFont.truetype('fonts/Tangerine_Regular.ttf', 60)
        signature = self._current_state_to_string()
        self.draw.text(
            (int(self.height * 1.14), int(self.width * 0.68)),
            signature,
            font=font,
        )

    def _current_state_to_string(self):
        current_data = str(hash(self)).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(current_data)
        hex_vals = md5.hexdigest()
        signature = [chr((ord(char) % 26) + 97) for char in hex_vals]
        first_name = ''.join(signature[:8]).capitalize()
        last_name = ''.join(signature[8:20]).capitalize()
        return first_name + ' ' + last_name

    def trans_to_cartesian(self, point):
        return Point(point.x - self.width / 2, point.y - self.height / 2)

    def trans_to_pil(self, point):
        return Point(point.x + self.width / 2, point.y + self.height / 2)


class Point(object):
    """ Silly little point class. """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            x, y = other.x, other.y
        else:
            x = y = other
        return Point(self.x + x, self.y + y)

    def __sub__(self, other):
        if isinstance(other, Point):
            x, y = other.x, other.y
        else:
            x = y = other
        return Point(self.x - x, self.y - y)

    def __radd__(self, other):
        return Point(self.x + other, self.y + other)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        return Point(self.x // other, self.y // other)

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def to_tuple(self):
        return self.x, self.y

    def rotate(self, theta):
        rotation_mat = np.matrix(
            [
                [cos(theta), sin(theta)],
                [-sin(theta), cos(theta)],
            ]
        )
        rotated = (rotation_mat @ np.matrix((self.x, self.y)).T).T.getA1()
        self.x = rotated[0]
        self.y = rotated[1]
        return self


class Line(object):
    """ Holds two points and knows a few things about them. """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        try:
            self.slope = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)
        except ZeroDivisionError:
            raise ValueError('No slope for a vertical line')
        self.intercept = self.p1.y - self.slope * self.p1.x
        self.length = math.sqrt(
            (self.p2.y - self.p1.y) ** 2 + (self.p2.x - self.p1.x) ** 2
        )

    def __repr__(self):
        return 'Line({}, {})'.format(repr(self.p1), repr(self.p2))

    def to_tuple(self):
        return self.p1.to_tuple() + self.p2.to_tuple()

    def get_points(self):
        return self.p1, self.p2


if __name__ == '__main__':
    image = CharlottesWeb().draw_image()
    times = 100
    for _ in range(times):
        image = CharlottesWeb(image).draw_image()
    image = CharlottesWeb(image).draw_image(signature=True)
    image.show()
    image.save("images/out.png", "PNG", Quality = 100)
