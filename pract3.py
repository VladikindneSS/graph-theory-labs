import collections
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):
        self.edge_list = [] # список ребер в виде кортежей (u,v)
        self.nodes = set() # множество вершин

    def add_edge(self, u, v): # добавляет ребро и обе его вершины
        self.edge_list.append((u, v))
        self.nodes.add(u)
        self.nodes.add(v)

    def add_node(self, v): # добавляет вершину без ребер
        self.nodes.add(v)


def parse_code(text): # фильтр входной строки (чтобы оставить только нули и единицы)
    return [c for c in text if c in "01"] 


def decode_binary_tree(code, root=1): 
    next_id = root + 1 # следующий номер вершины
    stack = [root] # стек для текущего пути в дереве
    edges = [] # список ребер

    for i, bit in enumerate(code): # проход по каждому символу входного двоичного кода
        b = int(bit)
        if b == 0: # если встречаем 0, то создаем новую вершину
            child = next_id
            next_id += 1
            edges.append((stack[-1], child)) # добавляем ребро от текущей вершины к новой
            stack.append(child) # спускаемся в новую вершину
        elif b == 1: # если встречаем 1, то возвращаемся к родителю
            if len(stack) <= 1:
                raise ValueError(f"Некорректный код: лишняя '1' на позиции {i} "
                                  f"(некуда возвращаться)")
            stack.pop()
        else:
            raise ValueError(f"Недопустимый символ в коде: {bit!r}")

    if len(stack) != 1:
        raise ValueError("Некорректный код: не все спуски завершены возвратом "
                          f"(остались незакрытые вершины: {stack[1:]})")

    return edges # возвращаем список ребер дерева


def tree_from_binary_code(text_or_bits, root=1): # восстанавливаем дерево по двоичному коду
    code = parse_code(text_or_bits) if isinstance(text_or_bits, str) else list(text_or_bits)
    edges = decode_binary_tree(code, root=root)
    g = Graph()
    g.add_node(root)
    for u, v in edges:
        g.add_edge(u, v)
    return g # возвращаем итоговый граф

def to_dot(graph, filename=None, graph_name="G"): # экспорт в DOT
    lines = [f"graph {graph_name} {{"]
    for node in sorted(graph.nodes, key=str):
        lines.append(f'    "{node}";')
    for (u, v) in graph.edge_list:
        lines.append(f'    "{u}" -- "{v}";')
    lines.append("}")

    text = "\n".join(lines)
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
    return text

def get_tree_layout(graph, root=1):
    adj = collections.defaultdict(list) # создаем список смежности
    for u, v in graph.edge_list:
        adj[u].append(v)
        adj[v].append(u)

    levels = collections.defaultdict(list) # словарь вершин по уровням
    visited = {root} # множество посещенных вершин
    queue = collections.deque([(root, 0)]) # очередь для BFS

    while queue: # обход в ширину
        node, depth = queue.popleft()
        levels[depth].append(node)
        
        for neighbor in adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))

    pos = {} # словарь координат вершин
    for depth, nodes in levels.items(): 
        width = len(nodes)
        for i, node in enumerate(nodes):
            x = i - (width - 1) / 2 if width > 1 else 0.0 # размещение вершины относительно центра уровня
            y = -depth
            pos[node] = (x, y)
            
    return pos # возвращаем словарь координат вершин


def visualize(graph, filename="tree.png", root=1):
    pos = get_tree_layout(graph, root)
    
    plt.figure(figsize=(6, 6)) # размер фигуры
    
    for u, v in graph.edge_list: # рисуем ребра
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        plt.plot([x1, x2], [y1, y2], color="gray", zorder=1) # zorder - номер слоя (чем больше, тем выше слой)
        
    for node, (x, y) in pos.items(): # рисуем вершины
        color = "tomato" if node == root else "skyblue" # цвет вершин (красный для корня, синий для остальных)
        plt.plot(x, y, marker="o", markersize=25, color=color, 
                 markeredgecolor="black", zorder=2)
        plt.text(x, y, str(node), ha="center", va="center", 
                 fontsize=10, fontweight="bold", zorder=3)
        
    plt.axis("off") # отключаем координатные оси
    plt.tight_layout() # автоматическая настройка расположения элементов
    plt.savefig(filename, dpi=300) # dpi - разрешение изображения
    plt.close()


if __name__ == "__main__":
    code = input("Введите двоичный код дерева: ")

    tree = tree_from_binary_code(code)

    dot_text = to_dot(tree, filename="tree.dot", graph_name="BinaryTree")
    print("\nDOT-представление:\n")
    print(dot_text)

    visualize(tree, "tree.png", root=1)
    print("\nВизуализация сохранена в tree.png")