from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QLineF


from math import gcd


class Resistor(QLabel):
    # класс Сопротивления
    clicked = pyqtSignal()

    def __init__(self, window, orientation, x, y, value, is_show=True):
        super().__init__(window)
        self.orientation = orientation
        self.window = window

        self.move(x, y)
        self.setValue(value)
        self.setStyleSheet(
            f'border: {window.side // 40}px solid #4d4d4d; background-color: white; font-size: {window.side / 15}pt; font-family: Arial;')
        self.first_neighbour = None
        self.second_neighbour = None
        self.setAlignment(Qt.AlignCenter)
        if self.orientation == 'x':
            self.resize(window.side // 5 * 3, window.side // 7 * 2)
            wire = \
                [w for w in window.wires if [w.p1(), w.p2()] == sorted(((x - window.side // 4, y + window.side // 10),
                                                                        (x - window.side // 4 + window.side,
                                                                         y + window.side // 10)))][0]
        else:
            self.resize(window.side // 7 * 2, window.side // 5 * 3)
            wire = \
                [w for w in window.wires if [w.p1(), w.p2()] == sorted(((x + window.side // 10, y - window.side // 4),
                                                                        (x + window.side // 10,
                                                                         y - window.side // 4 + window.side)))][0]

        if is_show:
            self.window.resistors.add(self)
            wire.resistor = self
        self.clicked.connect(window.show_qle)

    def coords(self):
        return self.x(), self.y()

    def setValue(self, new_value):
        self.value = new_value
        if new_value > 0:
            self.setText(f'{self.value} Ом') if self.orientation == 'x' else self.setText(f'{self.value} \n Ом')
        else:
            self.setText('')

    def __lt__(self, other):
        return [type(self.first_neighbour) is Node and type(self.second_neighbour) is Node and find_head(
            self.first_neighbour) == find_head(self.second_neighbour), len(self.window.make_series_group(self)),
                len(self.window.make_parallel_group(self)),
                -self.y(), -self.x()] <= [type(self.first_neighbour) is Node and type(self.second_neighbour) is Node and find_head(
                       self.first_neighbour) == find_head(self.second_neighbour),
                   len(self.window.make_series_group(other)),
                   len(self.window.make_parallel_group(other)),
                   -other.y(), -other.x()]

    def __gt__(self, other):
        return [len(self.window.make_series_group(self)), len(self.window.make_parallel_group(self)),
                -self.y(), -self.x()] >= [len(self.window.make_series_group(other)),
                   len(self.window.make_parallel_group(other)),
                   -other.y(), -other.x()]

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


class Wire(QLineF):
    # класс Провода
    def __init__(self, window, x1, y1, x2, y2, orientation=None, resistor=None):
        if (x1, y1) > (x2, y2):
            (x1, y1), (x2, y2) = (x2, y2), (x1, y1)
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
        super().__init__(x1, y1, x2, y2)
        self.orientation = orientation
        self.resistor = resistor
        self.window = window
        self.node1 = [node for nodes in window.nodes for node in nodes if node.x() == x1 and node.y() == y1][0]
        self.node1.wires.add(self)
        self.node2 = [node for nodes in window.nodes for node in nodes if node.x() == x2 and node.y() == y2][0]
        self.node2.wires.add(self)

    def separation(self):
        x_length = abs(self.x2() - self.x1())
        y_length = abs(self.y2() - self.y1())
        if self.y2() == self.y1() and int(x_length) != self.window.side:
            self.node1.wires.discard(self)
            self.node2.wires.discard(self)
            for i in range(int(x_length) // self.window.side):
                yield Wire(self.window, self.x1() + (self.x2() - self.x1()) / x_length * i * self.window.side,
                           self.y1(),
                           self.x1() + (self.x2() - self.x1()) / x_length * (i + 1) * self.window.side,
                           self.y2(), 'x')
        elif self.x1() == self.x2() and int(y_length) != self.window.side:
            self.node1.wires.discard(self)
            self.node2.wires.discard(self)
            for i in range(int(y_length) // self.window.side):
                yield Wire(self.window, self.x1(),
                           self.y1() + (self.y2() - self.y1()) / y_length * i * self.window.side, self.x1(),
                           self.y1() + (self.y2() - self.y1()) / y_length * (i + 1) * self.window.side, 'y')
        elif (c := gcd(int(max(y_length, x_length)) // self.window.side,
                       int(min(y_length, x_length)) // self.window.side)) != 1:
            self.node1.wires.discard(self)
            self.node2.wires.discard(self)
            sdx = int(x_length) // c
            sdy = int(y_length) // c
            for i in range(c):
                yield Wire(self.window, self.x1() + (self.x2() - self.x1()) / abs(self.x2() - self.x1()) * i * sdx,
                           self.y1() + (self.y2() - self.y1()) / abs(self.y2() - self.y1()) * i * sdy,
                           self.x1() + (self.x2() - self.x1()) / abs(self.x2() - self.x1()) * (i + 1) * sdx,
                           self.y1() + (self.y2() - self.y1()) / abs(self.y2() - self.y1()) * (i + 1) * sdy)
        else:
            if self.y1() == self.y2():
                self.orientation = 'x'
            elif self.x1() == self.x2():
                self.orientation = 'y'
            yield self

    def p1(self):
        return self.x1(), self.y1()

    def p2(self):
        return self.x2(), self.y2()

    def __hash__(self):
        return hash(f'{self.x1()}, {self.y1()}, {self.x2()}, {self.y2()}')


class Node(QLabel):
    # класс Узла

    clicked = pyqtSignal()

    def __init__(self, window, X, Y, show_coordinates=False):
        self.window = window
        self.X, self.Y = X, Y
        self.wires = set()
        self.head = None
        super().__init__('', window)
        self.move(window.x0 - ((window.side * window.count_x) // 2) + X * window.side,
                  window.y0 - ((window.side * window.count_y) // 2) + Y * window.side)
        if not show_coordinates:
            self.resize(window.side // 10, window.side // 10)
            self.setPixmap(QPixmap('icons/node.png'))
        else:
            self.resize(window.side // 2, window.side // 10)
            self.setStyleSheet('border: 1px solid #4d4d4d;')
            self.setText(f'{self.x()}-{self.y()}')
        self.setScaledContents(True)
        self.clicked.connect(window.wire)

    def coords(self):
        return self.x(), self.y()

    def __hash__(self):
        return hash(f'{self.x()}, {self.y()}')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()
