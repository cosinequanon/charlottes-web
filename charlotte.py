# def xfile(afile, globalz=None, localz=None):
#     with open(afile, "r") as fh:
#         exec(fh.read(), globalz, localz)

import math
import random

from math import sin, cos

from PIL import Image, ImageDraw


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def to_tuple(self):
        return self.x, self.y

    def rotate(self, theta):
        rotation_mat = np.matrix(
            [[cos(theta), sin(theta)], [-sin(theta), cos(theta)]]
        )
        rotated = (rotation_mat @ np.matrix((self.x, self.y)).T).T.getA1()
        self.x = rotated[0]
        self.y = rotated[1]
        return self


class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        try:
            self.slope = (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)
        except ZeroDevisionError:
            raise ValueError('No slope for a vertical line')
        self.intercept = self.p1.y - self.slope * self.p1.x
        self.length = math.sqrt(
            (self.p2.y - self.p1.y) ** 2 + (self.p2.x - self.p1.x) ** 2
        )

    def __repr__(self):
        return 'Line({}, {})'.format(self.p1.__repr__(), self.p2.__repr__())

    def to_tuple(self):
        return self.p1.to_tuple() + self.p2.to_tuple()


class CharlottesWeb(object):
    def __init__(self):
        self.width = 600
        self.height = 600
        self.center = (self.width / 2, self.height / 2)
        self.web_lines = []
        self.num_circles = 20
        self.im = Image.new(
            'RGBA',
            (self.width, self.height),
            (50, 50, 50, 0),
        )
        self.draw = ImageDraw.Draw(self.im)

    def render(self):
        self.draw_web_lines()
        self.draw_web_circles()
        self.im.show()

    def draw_web_circle(self, offset):
        # iterate over adjacent pairs of lines
        for i in range(len(self.web_lines)):
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
                self.draw_line(off_line_positive_1)
                self.draw_line(off_line_negative_2)
            else:
                self.draw_line(off_line_positive_2)
                self.draw_line(off_line_negative_1)

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

    def draw_web_circles(self):
        for i in range(self.num_circles):
            # todo make this non-linear
            offset = 10 + 15 * i
            self.draw_web_circle(offset)

    def draw_web_lines(self):
        num_lines = 8
        for line in range(num_lines // 2):
            start = Point(0, 1.5 * self.height // 2)
            end = Point(0, -1.5 * self.height // 2)
            # theta = 2 * math.pi * (line / num_lines)
            theta = 2 * math.pi * (line / num_lines)
            theta += (random.random() - 0.5) / 2
            nstart = self.trans_to_pil(start.rotate(theta))
            nend = self.trans_to_pil(end.rotate(theta))
            web_line = Line(nstart, nend)

            self.draw_line(web_line)
            self.web_lines.append(web_line)

    def draw_line(self, line):
        self.draw.line(line.to_tuple(), fill=(220, 220, 210))

    def trans_to_cartesian(self, point):
        return Point(point.x - self.width / 2, point.y - self.height / 2)

    def trans_to_pil(self, point):
        return Point(point.x + self.width / 2, point.y + self.height / 2)


if __name__ == '__main__':
    CharlottesWeb().render()
