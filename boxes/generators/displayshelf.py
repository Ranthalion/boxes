#!/usr/bin/env python3
# Copyright (C) 2013-2016 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *

class DisplayShelf(Boxes): # change class name here and below
    """Shelf with slanted floors"""

    ui_group = "Shelf"

    def __init__(self):
        Boxes.__init__(self)

        self.addSettingsArgs(edges.FingerJointSettings)

        #self.buildArgParser(x=400, y=100, h=300, outside=True)
        self.buildArgParser(x=140, y=215, h=215, outside=False)
        self.argparser.add_argument(
            "--num",  action="store", type=int, default=1,
            help="number of shelves")
        self.argparser.add_argument(
            "--frontWallHeight",  action="store", type=float, default=50.0,
            help="height of front walls")
        self.argparser.add_argument(
            "--angle",  action="store", type=float, default=45.0,
            help="angle of floors (negative values for slanting backwards)")
        self.argparser.add_argument(
            "--include_back", action="store", type=boolarg, default=False,
            help="Include panel on the back of the shelf")
        self.argparser.add_argument(
            "--slope_top", action="store", type=boolarg, default=True,
            help="Slope the sides a the top by front wall height")
        self.argparser.add_argument(
            "--hole_diameter", action="store", type=float, default=0,
            help="Hole diamater for running cords through the shelves and side walls. A value of 0 will not generate any holes.")


    def generate_finger_holes(self, a=None, b=None, c=None):

        print(f'a={a}, b={b}, c={c}')
        t = self.thickness
        a = math.radians(self.angle)

        hs = (self.sl+t) * math.sin(a) + math.cos(a) * t

        for i in range(self.num):
            pos_x = abs(0.5*t*math.sin(a))
            pos_y = hs - math.cos(a)*0.5*t + i * (self.h-hs) / (self.num - 0.5)
            self.fingerHolesAt(pos_x, pos_y, self.sl, -self.angle)
            pos_x += math.cos(-a) * (self.sl+0.5*t) + math.sin(a)*0.5*t
            pos_y += math.sin(-a) * (self.sl+0.5*t) + math.cos(a)*0.5*t
            self.fingerHolesAt(pos_x, pos_y, self.frontWallHeight, 90-self.angle)
            self.hole_at(self.hole_diameter*1.5, pos_y+self.hole_diameter, self.hole_diameter/2)

    def generate_sides(self, width, height):
        if self.slope_top:
            top_segment_height = height/self.num
            unmodified_segment_height = height - top_segment_height
            a = math.radians(self.angle)
            lip_height = self.frontWallHeight #* math.cos(a)
            m = top_segment_height - lip_height
            hypotenuse = m / math.sin(a)
            top_width = width - math.sqrt((hypotenuse ** 2) - (m ** 2))
            missing_top = 0

            if (top_width <= 0):
                modified_hypotenuse = width / math.cos(a)
                m = math.sqrt((modified_hypotenuse ** 2) - (width ** 2))
                modified_height = unmodified_segment_height + lip_height + m
                edges = 'eeeF'
                borders = [width, 90, unmodified_segment_height + lip_height, 90-self.angle, modified_hypotenuse, 90+self.angle, modified_height, 90]
            else:
                edges = 'eeeeF'
                borders = [width, 90, unmodified_segment_height + lip_height, 90-self.angle, hypotenuse, self.angle, top_width, 90, height, 90]

            self.polygonWall(borders, edge=edges, callback=[self.generate_finger_holes], move="up", label="left side")
            self.polygonWall(borders, edge=edges, callback=[self.generate_finger_holes], move="up", label='right side')
        else:
            edges = "eeee"
            if self.include_back:
                edges = "eeeF"
            self.rectangularWall(width, height, edges, callback=[self.generate_finger_holes], move="up", label="left side")
            self.rectangularWall(width, height, edges, callback=[self.generate_finger_holes], move="up", label="right side")

    def generate_shelves(self):
        cb = [lambda : self.hole_at(self.x/2, self.sl-(self.hole_diameter), self.hole_diameter/2)]
        if self.frontWallHeight:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "ffef", callback=cb, move="up", label=f"shelf {i+1}")
                self.rectangularWall(self.x, self.frontWallHeight, "Ffef", move="up", label=f"front lip {i+1}")
        else:
            for i in range(self.num):
                self.rectangularWall(self.x, self.sl, "Efef", callback=cb, move="up", label=f"shelf {i+1}")

    def hole_at(self, x, y, r):
        if r <= 0:
            return
        self.hole(x, y, r)


    def render(self):
        #TODO: [ML] Validate design.  If validation fails, then output a problem to the user
        # e.g. Is the height too small for the angle and depth?

        # adjust to the variables you want in the local scope
        x, y, h = self.x, self.y, self.h
        front = self.frontWallHeight
        thickness = self.thickness

        if self.outside:
            x = self.adjustSize(x)

        a = math.radians(self.angle)

        self.sl = (y - (thickness * (math.cos(a) + abs(math.sin(a)))) - max(0, math.sin(a) * front)) / math.cos(a)

        # render your parts here
        self.generate_sides(y, h)
        self.generate_shelves()

        if self.include_back:
            self.rectangularWall(x, h, "eFeF", label="back wall", move="up")

