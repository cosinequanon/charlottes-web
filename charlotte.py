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

    def to_tuple(self):
        return self.x, self.y


class Line(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x.to_tuple() + self.y.to_tuple()


class CharlottesWeb(object):
    def __init__(self):
        self.width = 600
        self.height = 600
        self.center = (self.width / 2, self.height / 2)
        self.web_lines = []
        self.im = Image.new(
            'RGBA',
            (self.width, self.height),
            (50, 50, 50, 0),
        )
        self.draw = ImageDraw.Draw(self.im)

    def render(self):
        # self.draw.line((100,200, 150,300), fill=128)
        self.draw_web_lines()
        self.draw_web_circles()
        self.im.show()

    def draw_web_circles(self):
        pass
        # for i in

    def draw_web_lines(self):
        num_lines = 8
        for line in range(num_lines // 2):
            start = Point(0, 1.5 * self.height // 2)
            end = Point(0, -1.5 * self.height // 2)
            theta = 2 * math.pi * (line / num_lines) + (random.random() - 0.5) / 5
            nstart = self.trans_to_pil(self.rotate(start, theta))
            nend = self.trans_to_pil(self.rotate(end, theta))
            web_line = Line(Point(*nstart), Point(*nend))

            self.draw.line(web_line.to_tuple(), fill=(220, 220, 210))
            self.web_lines.append(web_line)

    def rotate(self, pt, theta):
        rotation_mat = np.matrix(
            [[cos(theta), sin(theta)], [-sin(theta), cos(theta)]]
        )
        rotated = (rotation_mat @ np.matrix(pt.to_tuple()).T).T.getA1()
        return (rotated[0], rotated[1])

    def trans_to_cartesian(self, point):
        return (point[0] - self.width / 2, point[1] - self.height / 2)

    def trans_to_pil(self, point):
        return (point[0] + self.width / 2, point[1] + self.height / 2)


if __name__ == '__main__':
    CharlottesWeb().render()
