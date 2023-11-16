import sys

from objects import Resistor, Wire, Node
from methods import loop_search, merge, do_clear, proverka

from PyQt5.QtGui import QColor, QPainter, QDoubleValidator, QIcon, QCursor, QPixmap, QPen
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QAction
from PyQt5.QtCore import Qt
from PyQt5 import uic

from random import randint


class mainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('1.ui', self)

        self.initUI()

    def initUI(self):

        self.desktop = QApplication.desktop()

        self.nodes = []
        self.actions = []
        self.wires = set()
        self.useful_nodes = set()
        self.resistors = set()

        self.screenRect = self.desktop.screenGeometry()
        self.height = self.screenRect.height()
        self.width = self.screenRect.width()

        self.x0 = self.width // 2
        self.y0 = self.height // 2

        self.count_x = 50
        self.count_y = 35
        self.x1, self.y1, self.x2, self.y2, self.glowing, self.check, self.deleteb = [False] * 7
        self.side = 200
        self.qp_glowing, self.qp_wire = [QPainter()] * 2

        for i in range(self.count_x):
            self.nodes.append([])
            for g in range(self.count_y):
                self.nodes[-1].append(Node(self, i, g))

        self.message.move(self.width - self.message.width(), 0)

        self.qle = QLineEdit('', self)
        self.qle.resize(self.side // 5 * 3, 30)
        self.qle.setValidator(QDoubleValidator(1, 1000, 2))
        self.qle.editingFinished.connect(self.setValue)
        self.qle.id = False
        self.qle.setVisible(False)

        self.eraser = QAction(QIcon("eraser.png"), "ластик", self)
        self.eraser.triggered.connect(self.delete)
        self.eraser.setCheckable(True)
        self.toolBar.addAction(self.eraser)

        self.clear = QAction(QIcon("clear.png"), "очистка", self)
        self.clear.triggered.connect(do_clear)
        self.toolBar.addAction(self.clear)

        self.toolBar.addSeparator()

        self.play_pause_button = QAction(QIcon("start.png"), "старт", self)
        self.play_pause_button.triggered.connect(self.play_pause)
        self.toolBar.addAction(self.play_pause_button)

        self.previous = QAction(QIcon('left-arrow.png'), 'назад', self)
        self.previous.triggered.connect(self.previous_step)
        self.previous.setEnabled(False)
        self.toolBar.addAction(self.previous)

        self.next = QAction(QIcon('right-arrow.png'), 'вперёд', self)
        self.next.triggered.connect(self.next_step)
        self.next.setEnabled(False)
        self.toolBar.addAction(self.next)

        self.setGeometry(0, 0, self.width - 200, self.height - 200)
        self.setWindowTitle('Приложение для упрощения электрических цепей')

    def setValue(self):
        resistor = self.qle.id
        resistor.setValue(float(self.qle.text()))
        self.qle.clear()
        self.qle.setVisible(False)

    def show_qle(self):
        if not self.deleteb and not self.qle.isVisible():
            resistor = self.sender()
            x, y = resistor.x(), resistor.y()
            self.qle.move(int(x), int(y - 32)) if resistor.orientation == 'x' else self.qle.move(
                int(x) + self.side // 7 * 2 + 20,
                int(y) + self.side // 10 * 2)
            self.qle.setVisible(True)
            self.qle.id = resistor
            if resistor.value:
                resistor.setValue(0)

    def wire(self):
        print('wow')
        if not self.deleteb and not self.check:
            node = self.sender()
            X = node.X
            Y = node.Y
            x = self.x0 - ((self.side * self.count_x) / 2) + X * self.side
            y = self.y0 - ((self.side * self.count_y) / 2) + Y * self.side
            if not self.x1 and not self.y1:
                print('nice')
                self.x1 = x
                self.y1 = y
                self.glowing = True
            elif x == self.x1 and y == self.y1:
                self.x1, self.y1, self.glowing = [False] * 3
            else:
                self.x2 = x
                self.y2 = y
                self.spawm_wire(self.x1, self.y1, self.x2, self.y2)
                self.x1, self.y1, self.x2, self.y2, self.glowing = [False] * 5

    def spawm_wire(self, x1, y1, x2, y2):
        self.wires.extend(Wire(x1, y1, x2, y2).separation())

    def check_resistor(self, x, y):
        for wire in self.wires:
            x1, y1 = wire.p1()
            x2, y2 = wire.p2()
            e = self.side // 5
            if min(x1, x2) + e < x < max(x1, x2) - e and abs(y - y1) < self.side // 8 and wire.orientation == 'x' and \
                    not wire.resistor:
                self.spawn_resistor('x', min(x1, x2) + self.side // 4, y1 - self.side // 10)
                break
            elif min(y1, y2) + e < y < max(y1, y2) - e and abs(x - x1) < self.side // 7 and wire.orientation == 'y' and \
                    not wire.resistor:
                self.spawn_resistor('y', x1 - self.side // 10, min(y1, y2) + self.side // 4)
                break

    def spawn_resistor(self, k, x, y, value=0):
        Resistor(self, k, x, y, value)

    def find_neighbourhood_resistor(self):
        for resistor in self.resistors:
            self.find_neighbour(resistor)

    def find_neighbour(self, resistor):
        if resistor.orientation == 'y':
            x, y = resistor.coords
            x += self.side // 10
            y -= self.side // 4
            way = [tuple(sorted(((x, y), (x, y + self.side))))]
            resistor.setFirstNeighbour(self.loop_search(self, way, x, y))
            x, y = resistor.x(), resistor.y()
            x += self.side // 10
            y -= (self.side // 4 - self.side)
            way = [tuple(sorted(((x, y), (x, y - self.side))))]
            resistor.setSecondNeighbour(self.loop_search(self, way, x, y))
        elif resistor.orientation == 'x':
            x, y = resistor.coords
            y += self.side // 10
            x -= self.side // 4
            way = [tuple(sorted(((x + self.side, y), (x, y))))]
            resistor.setFirstNeighbour(self.loop_search(self, way, x, y))
            x, y = resistor.coords
            y += self.side // 10
            x -= (self.side // 4 - self.side)
            way = [tuple(sorted(((x - self.side, y), (x, y))))]
            resistor.setSecondNeighbour(self.loop_search(self, way, x, y))

    def make_series_group(self, resistor):
        group = set()
        if type(resistor.first_neighbour) is Resistor:
            group.add(resistor)
            resistor = resistor.first_neighbour
            while not type(resistor.first_neighbour) is Node and not type(resistor.second_neighbour) is Node:
                group.add(resistor)
                resistor = resistor.first_neighbour if resistor.first_neighbour not in group else resistor.second_neighbour
            group.add(resistor)
        if type(resistor.second_neighbour) is Resistor:
            group.add(resistor)
            resistor = resistor.first_neighbour
            while not type(resistor.first_neighbour) is Node and not type(resistor.second_neighbour) is Node:
                group.add(resistor)
                resistor = resistor.first_neighbour if resistor.first_neighbour not in group else resistor.second_neighbour
            group.add(resistor)
        return group

    def make_parallel_group(self, resistor):
        group = set()
        if type(resistor.first_neighbour) is Node and type(resistor.second_neighbour) is Node:
            group.add(resistor)
            for r in self.resistors:
                if type(r.first_neighbour) is Node and type(r.second_neighbour) == Node and {
                    self.find(r.first_neighbour), self.find(r.second_neighbour)} == \
                        {self.find(resistor.first_neighbour), self.find(resistor.second_neighbour)}:
                    group.add(r)
        return group

    def next_step(self):
        if self.check:
            for resistor in sorted(self.resistors, reverse=True):
                if type(resistor.first_neighbour) is Node and type(resistor.second_neighbour) is Node and self.find(
                        resistor.first_neighbour.coords()) == self.find(resistor.second_neighbour.coords):
                    self.actions.append(set(resistor.copy()))
                    if resistor.orientation == 'y':
                        x, y = resistor.coords()
                        x += self.side // 10
                        y -= self.side // 4
                        way = [tuple(sorted(((x, y), (x, y + self.side))))]
                        self.loop_search(way, x, y, True)
                        x, y = resistor.coords()
                        x += self.side // 10
                        y -= (self.side // 4 - self.side)
                        way = [tuple(sorted(((x, y), (x, y - self.side))))]
                        self.loop_search(way, x, y, True)
                    elif resistor.orientation == 'x':
                        x, y = resistor.coords()
                        y += self.side // 10
                        x -= self.side // 4
                        way = [tuple(sorted(((x + self.side, y), (x, y))))]
                        self.loop_search(way, x, y, True)
                        x, y = resistor.coords()
                        y += self.side // 10
                        x -= (self.side // 4 - self.side)
                        way = [tuple(sorted(((x - self.side, y), (x, y))))]
                        self.loop_search(way, x, y, True)
                    self.erase(resistor.x() + resistor.width() // 2, resistor.y() + resistor.height() // 2)
                    self.erase(resistor.x() + resistor.width() // 2, resistor.y() + resistor.height() // 2)
                    self.calculation_nodes()
                    break
                group = self.make_series_group(resistor)
                if len(group) > 1:
                    self.actions.append(set())
                    resistor = max(group)
                    for r in group:
                        self.actions[-1].add(r.copy())
                        if r != resistor:
                            self.erase(r.x() + r.width() // 2, r.y() + r.height() // 2)
                    resistor.setValue(sum(map(lambda r: r.value, group)))
                    self.find_neighbourhood_resistor()
                    break
                else:
                    group.clear()
                group = self.make_parallel_group(resistor)
                if len(group) > 1:
                    self.actions.append(set())
                    resistor = max(group)
                    for r in group:
                        self.actions[-1].add(r.copy())
                        if r != resistor:
                            if r.orientation == 'y':
                                x, y = r.coords()
                                x += self.side // 10
                                y -= self.side // 4
                                way = [tuple(sorted(((x, y), (x, y + self.side))))]
                                self.loop_search(way, x, y, True)
                                x, y = r.coords()
                                x += self.side // 10
                                y -= (self.side // 4 - self.side)
                                way = [tuple(sorted(((x, y), (x, y - self.side))))]
                                self.loop_search(way, x, y, True)
                            elif resistor.orientation == 'x':
                                x, y = r.coords()
                                y += self.side // 10
                                x -= self.side // 4
                                way = [tuple(sorted(((x + self.side, y), (x, y))))]
                                self.loop_search(way, x, y, True)
                                x, y = r.coords()
                                y += self.side // 10
                                x -= (self.side // 4 - self.side)
                                way = [tuple(sorted(((x - self.side, y), (x, y))))]
                                self.loop_search(way, x, y, True)
                            self.erase(r.x() + r.width() // 2, r.y() + r.height() // 2)
                            self.erase(r.x() + r.width() // 2, r.y() + r.height() // 2)
                            self.calculation_nodes()
                    resistor.setValue(round(1 / sum(map(lambda r: 1 / r.value, group)), 2))
                    self.find_neighbourhood_resistor()
                    break
            else:
                self.message.setText('Цепь упрощена')
                self.stop()

    def previous_step(self):
        if self.actions:
            for obj in self.actions[-1]:
                if type(obj) is Resistor:
                    resistor = obj
                    if resistor not in self.resistors:
                        if not (wire for wire in self.wires if wire.resistor == resistor):
                            if resistor.orientation == 'x':
                                self.spawm_wire(resistor.x() - self.side // 4, resistor.y() + self.side // 10,
                                                resistor.x() - self.side // 4 + self.side,
                                                resistor.y() + self.side // 10)
                            else:
                                self.spawm_wire(resistor.x() + self.side // 10, resistor.y() - self.side // 4,
                                                resistor.x() + self.side // 10,
                                                resistor.y() - self.side // 4 + self.side)
                        self.spawn_resistor(resistor.orientation, *resistor.coords(), resistor.value)
                    else:
                        r = (res for res in self.resistors if res.coords() == resistor.coords())
                        r.setValue(resistor.value)
                else:
                    w = obj
                    self.spawm_wire(*w.p1(), *w.p2())
            del self.actions[-1]
            self.calculation_nodes()
            self.find_neighbourhood_resistor()

    def calculation_nodes(self):
        self.useful_nodes.clear()
        for wire in self.wires:
            x1, y1 = wire.p1()
            x2, y2 = wire.p2()
            self.useful_nodes.add(wire.node1())
            self.useful_nodes.add(wire.node2())
        for n in self.useful_nodes:
            n.head = n
        for n in self.useful_nodes:
            if len(n.wires) > 2:
                for w in n.wires:
                    n1 = loop_search(self, [w], (w.node1().x() if w.node1() != n else w.node2().x()),
                                               (w.node1().y() if w.node1() != n else w.node2().y()))
                    if type(n1) is Node and len(n1.wires) > 2:
                        merge(self, n, n1)

    def play_pause(self):
        self.check = (self.check + 1) % 2
        self.x1, self.y1, self.glowing = [False] * 3
        if self.check:
            self.play_pause_button.setIcon(QIcon('pause.png'))
            if proverka(self):
                self.message.setText(proverka(self))
                self.stop()
                return 0
            if self.deleteb:
                self.delete()
            self.find_neighbourhood_resistor()
            self.calculation_nodes()
        else:
            self.play_pause_button.setIcon(QIcon('start.png'))
            self.stop()


    def stop(self):
        self.check = False
        self.play_pause_button.setIcon(QIcon('start.png'))
        for i in self.resistors:
            i.first_neighbour = None
            i.second_neighbour = None
        self.useful_nodes.clear()
        self.actions.clear()

    def delete(self):
        if not self.deleteb:
            self.deleteb = True
            self.eraser.setChecked(True)
            self.setCursor(QCursor(QPixmap('eraser.png').scaled(self.width // 42, self.width // 42)))
        else:
            self.deleteb = False
            self.eraser.setChecked(False)
            self.unsetCursor()

    def erase(self, x_mouse, y_mouse):
        for wire in self.wires:
            x1, y1 = wire.p1()
            x2, y2 = wire.p2()
            e = self.side // 10
            if not wire.resistor:
                if x1 == x2:
                    if x1 - e < x_mouse < x1 + e and min(y1, y2) < y_mouse < max(y1, y2):
                        self.wires.remove(wire)
                        break
                elif y1 == y2:
                    if y1 - e < y_mouse < y1 + e and min(x1, x2) < x_mouse < max(x1, x2):
                        self.wires.remove(wire)
                        break
                else:
                    k = (y1 - y2) / (x1 - x2)
                    m = y1 - k * x1
                    if min(x1, x2) < x_mouse < max(x1, x2) and min(y1, y2) < y_mouse < max(y1,
                                                                                           y2) and x_mouse * k + m - e < y_mouse < x_mouse * k + m + e:
                        self.wires.remove(wire)
                        break
            else:
                if (wire.orientation == 'x' and y1 - e < y_mouse < y1 + e and min(x1, x2) < x_mouse < max(x1,
                                                                                                             x2)) or (
                        wire.orientation == 'y' and x1 - e < x_mouse < x1 + e and min(y1, y2) < y_mouse < max(y1,
                                                                                                                 y2)):
                    resistor = wire.resistor
                    wire.resistor = None
                    resistor.hide()
                    self.resistors_values.remove(resistor)

    def paintEvent(self, event):
        e = self.side // 20
        for wire in self.wires:
            self.qp_wire.begin(self)
            x1, y1 = wire.p1()
            x2, y2 = wire.p2()
            self.draw_line(self.qp_wire, x1 + e, y1 + e, x2 + e, y2 + e)
            self.qp_wire.end()
            self.update()
        if self.glowing:
            self.qp_glowing.begin(self)
            self.show_glowing(self.qp_glowing, self.x1, self.y1)
            self.qp_glowing.end()
            self.update()
        self.draw()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.deleteb and not self.check:
            self.check_resistor(event.x(), event.y())
        elif event.button() == Qt.LeftButton and not self.check:
            self.erase(event.x(), event.y())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_E:
            self.delete()

    def draw_line(self, qp, x1, y1, x2, y2):
        qp.setPen(QPen(QColor(77, 77, 77), self.side // 20, Qt.SolidLine))
        qp.drawLine(int(x1), int(y1), int(x2), int(y2))

    def show_glowing(self, qp, x1, y1):
        qp.setPen(QPen(QColor(185, 185, 185), self.side // 20, Qt.SolidLine))
        qp.drawEllipse(int(x1), int(y1), self.side // 10, self.side // 10)
        self.update()

    def draw(self):
        for el in self.resistors:
            el.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = mainWindow()
    ex.showMaximized()
    sys.exit(app.exec_())
