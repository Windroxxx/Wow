from random import randint


def loop_search(window, way, x, y, is_del=False):
    while len(window.node[x - window.x0 + ((window.side * window.count_x) // 2) / window.side][
                  y - window.y0 + ((window.side * window.count_y) // 2) / window.side].wires) == 2 and not (
            wire := (w for w in window.wires if (x, y) in (w.p1(), w.p2()) and w not in way)[0]).resistor:
        way.append(wire)
    if is_del:
        window.erase((wire.x1() + wire.x2()) // 2, (wire.y1() + wire.y2()) // 2)
    window.actions[-1].add(wire.copy())
    x, y = wire.p2() if wire.p1() == (x, y) else wire.p1()
    if len((node := wire.node2() if wire.node1().coords() == (x, y) else wire.node1()).wires) != 2:
        return node
    else:
        return wire.resistor


def find(window, node):
    if node != node.head:
        node.head = window.find(node.head)
    return node.head


def merge(window, node1, node2):
    node1 = window.find(node1)
    node2 = window.find(node2)
    if randint(0, 2):
        node1, node2 = node2, node1
    node1.head = node2


def checking_for_integrity(used, node):
    if node not in used:
        used.append(node)
    for w in node.wires:
        next_node = w.node2() if w.node1() == node else w.node1()
        if next_node not in used:
            checking_for_integrity(used, next_node)


def do_clear(window):
    if window.check:
        window.otmena()
    for wire in window.wires:
        window.erase((wire.x1() + wire.x2()) / 2, (wire.y1() + wire.y2()) / 2)
        window.erase((wire.x1() + wire.x2()) / 2, (wire.y1() + wire.y2()) / 2)


def proverka(window):
    s = [len(k.wires) for k in window.useful_nodes]
    if s.count(1) != 2:
        return 'Неправильное количество клемм'
    for resistor in window.resistors_values:
        if resistor.value == 0:
            return 'Укажите значения у всех резисторов'
    used = []
    checking_for_integrity(used, list(window.useful_nodes)[0])
    if len(used) != len(window.useful_nodes):
        return 'Найдено более одной цепи.'
