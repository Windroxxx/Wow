from random import randint

from objects import Node, Resistor


def loop_search(window, way, x, y, is_del=False):
    """Поиск циклом.
    Запускает цикл от переданой точки и двигается по проводам,
    пока не найдёт резистор или узел имеющий больше двух проводов."""
    if len((
                   node := [node for nodes in window.nodes for node in nodes if (node.x(), node.y()) == (x, y)][
                       0]).wires) == 1:
        return node
    wire = [w for w in window.wires if (x, y) in (w.p1(), w.p2()) and w not in way][0]
    while len(window.nodes[(x - window.x0 + ((window.side * window.count_x) // 2)) // window.side][
                  (y - window.y0 + (
                          (window.side * window.count_y) // 2)) // window.side].wires) == 2 and not wire.resistor:
        wire = [w for w in window.wires if (x, y) in (w.p1(), w.p2()) and w not in way][0]
        if wire not in way:
            way.append(wire)
        x, y = (wire.node1.x() if wire.p1() != (x, y) else wire.node2.x()), (
            wire.node1.y() if wire.p1() != (x, y) else wire.node2.y())
        if len((node := [node for nodes in window.nodes for node in nodes if (node.x(), node.y()) == (x, y)][
            0]).wires) == 1:
            return node
    if is_del:
        pass
    if len((node := wire.node1 if wire.node1.coords() == (x, y) else wire.node2).wires) != 2:
        if is_del:
            for wire in way[1:]:
                window.erase((wire.x1() + wire.x2()) // 2, (wire.y1() + wire.y2()) // 2)
                window.actions[-1].add(wire)
        return node
    else:
        return wire.resistor


def calculation_nodes(window):
    """Расчёт узлов.
    Объединяет узлы в группы, если те соединенны проводом напрямую."""
    window.useful_nodes.clear()
    for wire in window.wires:
        window.useful_nodes.add(wire.node1)
        window.useful_nodes.add(wire.node2)
    for n in window.useful_nodes:
        n.head = n
    for n in window.useful_nodes:
        if len(n.wires) > 2:
            for w in n.wires:
                n1 = loop_search(window, [w], (w.node1.x() if w.node1 != n else w.node2.x()),
                                 (w.node1.y() if w.node1 != n else w.node2.y()))
                if type(n1) is Node and len(n1.wires) > 2:
                    merge(n, n1)


def make_series_group(resistor):
    """Создание последовательной группы.
    На вход получает резистор, после чего запускает поиск циклом, пока не найдёт узлы с двух сторон."""
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
        resistor = resistor.second_neighbour
        while not type(resistor.first_neighbour) is Node and not type(resistor.second_neighbour) is Node:
            group.add(resistor)
            resistor = resistor.first_neighbour if resistor.first_neighbour not in group else resistor.second_neighbour
        group.add(resistor)
    return group


def make_parallel_group(window, resistor):
    """Создание параллельной группы.
    Получает на вход резистор и выбирает все резисторы с такими же соседями как и у данного."""
    group = set()
    if type(resistor.first_neighbour) is Node and type(resistor.second_neighbour) is Node:
        group.add(resistor)
        for r in window.resistors:
            if type(r.first_neighbour) is Node and type(r.second_neighbour) == Node and {
                find_head(r.first_neighbour), find_head(r.second_neighbour)} == \
                    {find_head(resistor.first_neighbour), find_head(resistor.second_neighbour)}:
                group.add(r)
    return group


def find_head(node):
    if node != node.head:
        node.head = find_head(node.head)
    return node.head


def merge(node1, node2):
    node1 = find_head(node1)
    node2 = find_head(node2)
    if randint(0, 2):
        node1, node2 = node2, node1
    node1.head = node2


def checking_for_integrity(used, node):
    if node not in used:
        used.append(node)
    for w in node.wires:
        next_node = w.node2 if w.node1 == node else w.node1
        if next_node not in used:
            checking_for_integrity(used, next_node)


def proverka(window):
    window.calculation_nodes()
    s = [len(k.wires) for k in window.useful_nodes]
    if s.count(1) != 2:
        return 'Неправильное количество клемм'
    for resistor in window.resistors:
        if resistor.value == 0:
            return 'Укажите значения у всех резисторов'
    used = []
    checking_for_integrity(used, list(window.useful_nodes)[0])
    if len(used) != len(window.useful_nodes):
        return 'Найдено более одной цепи.'
