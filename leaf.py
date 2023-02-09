from random import random, randint
from dataclasses import dataclass
from abc import abstractmethod, ABC

import pygame.gfxdraw
from pygame import Rect

from point import Point
from misc import SCREEN, WHITE

MIN_LEAF_SIZE: int = 6
MAX_LEAF_SIZE: int = 20


@dataclass
class _ABCLeaf(ABC):
    x: int
    y: int
    width: int
    height: int

    @abstractmethod
    def split(self): ...

    @abstractmethod
    def create_rooms(self): ...

    @abstractmethod
    def get_room(self): ...

    @abstractmethod
    def create_hall(self, left: Rect, right: Rect): ...


class Leaf(_ABCLeaf):
    left_child: "Leaf" = None
    right_child: "Leaf" = None

    room: Rect = None

    def split(self):
        # разрезаем лист на два дочерних объекта
        if self.left_child is not None or self.right_child is not None:
            return False

        # определяем направление разрезания
        # если ширина больше 25% высоты, то режем по вертикали
        # если высота больше 25% ширины, то режем по горизонтали
        split_h = random() > 0.5
        if self.width > self.height and self.width / self.height >= 1.25:
            split_h = False
        elif self.height > self.width and self.height / self.width >= 1.25:
            split_h = True

        # определяем максимальную высоту или ширину
        max_ = (self.height if split_h else self.width) - MIN_LEAF_SIZE
        if max_ <= MIN_LEAF_SIZE:
            return False

        split = randint(MIN_LEAF_SIZE, max_)

        # создаём левый или правый дочерние листы на основании направления разрезания
        if split_h:
            self.left_child = Leaf(self.x, self.y, self.width, split)
            self.right_child = Leaf(self.x, self.y + split, self.width, self.height - split)
        else:
            self.left_child = Leaf(self.x, self.y, split, self.height)
            self.right_child = Leaf(self.x + split, self.y, self.width - split, self.height)
        return True

    def create_rooms(self):
        """Генерирует комнаты для листа и дочерних объектов"""
        # если лист был разрезан, переходим к его дочерним объектам
        if self.left_child or self.right_child:
            if self.left_child:
                self.left_child.create_rooms()
            if self.right_child:
                self.right_child.create_rooms()

            if self.left_child and self.right_child:
                self.create_hall(self.left_child.get_room(), self.right_child.get_room())
        else:
            # размер комнаты не меньше 3х3 тайла до размера листа - 2
            room_size = Point(randint(3, self.width - 2), randint(3, self.height - 2))
            # размещаем комнаты, но не впритык к границам, иначе соседние комнаты могут слиться
            room_pos = Point(randint(1, self.width - room_size.x - 1), randint(1, self.height - room_size.y - 1))
            self.room = Rect(self.x + room_pos.x, self.y + room_pos.y, room_size.x, room_size.y)
            # отрисовываем комнаты
            _draw(self.room, WHITE)

    def get_room(self) -> None | Rect:
        if self.room:
            return self.room
        else:
            l_room = None
            r_room = None
            if self.left_child:
                l_room = self.left_child.get_room()
            if self.right_child:
                r_room = self.right_child.get_room()
            if l_room is None and r_room is None:
                return None
            elif r_room is None:
                return l_room
            elif l_room is None:
                return r_room
            elif random() > 0.5:
                return l_room
            else:
                return r_room

    def create_hall(self, left: Rect, right: Rect):
        halls = []
        point1 = Point(randint(left.left + 1, left.right - 2), randint(left.top + 1, left.bottom - 2))
        point2 = Point(randint(right.left + 1, right.right - 2), randint(right.top + 1, right.bottom - 2))
        w = point2.x - point1.x
        h = point2.y - point1.y
        if w < 0:
            if h < 0:
                if random() < 0.5:
                    halls.append(Rect(point2.x, point1.y, abs(w), 1))
                    halls.append(Rect(point2.x, point2.y, 1, abs(h)))
                else:
                    halls.append(Rect(point2.x, point2.y, abs(w), 1))
                    halls.append(Rect(point1.x, point2.y, 1, abs(h)))
            elif h > 0:
                if random() < 0.5:
                    halls.append(Rect(point2.x, point1.y, abs(w), 1))
                    halls.append(Rect(point2.x, point1.y, 1, abs(h)))
                else:
                    halls.append(Rect(point2.x, point2.y, abs(w), 1))
                    halls.append(Rect(point1.x, point1.y, 1, abs(h)))
            else:  # h == 0
                halls.append(Rect(point2.x, point2.y, abs(w), 1))
        elif w > 0:
            if h < 0:
                if random() < 0.5:
                    halls.append(Rect(point1.x, point2.y, abs(w), 1))
                    halls.append(Rect(point1.x, point2.y, 1, abs(h)))
                else:
                    halls.append(Rect(point1.x, point1.y, abs(w), 1))
                    halls.append(Rect(point2.x, point2.y, 1, abs(h)))
            elif h > 0:
                if random() < 0.5:
                    halls.append(Rect(point1.x, point1.y, abs(w), 1))
                    halls.append(Rect(point2.x, point1.y, 1, abs(h)))
                else:
                    halls.append(Rect(point1.x, point2.y, abs(w), 1))
                    halls.append(Rect(point1.x, point1.y, 1, abs(h)))
            else:  # h == 0
                halls.append(Rect(point1.x, point1.y, abs(w), 1))
        else:  # w == 0
            if h < 0:
                halls.append(Rect(point2.x, point2.y, 1, abs(h)))
            elif h > 0:
                halls.append(Rect(point1.x, point1.y, 1, abs(h)))
        for hall in halls:
            _draw(hall, WHITE)


def create_leaf(width, height):
    leafs = []
    did_split = True

    root = Leaf(0, 0, width, height)
    leafs.append(root)

    while did_split:
        did_split = False
        for i in leafs:
            if i.left_child is None and i.right_child is None:
                if i.width > MAX_LEAF_SIZE or i.height > MAX_LEAF_SIZE \
                        or random() > 0.25:
                    if i.split():
                        leafs.append(i.left_child)
                        leafs.append(i.right_child)
                        did_split = True
    root.create_rooms()
    return leafs


def _draw(rect: Rect, color: tuple):
    pygame.gfxdraw.box(SCREEN, rect, color)
    pygame.display.flip()
