from collections import deque

INF = float("inf")


def parse_number(token):
    try:
        return int(token)
    except ValueError:
        return float(token)


def hungarian_min(cost):
    n = len(cost)
    u = [0] * (n + 1) # Потенциалы строк
    v = [0] * (n + 1) # Потенциалы столбцов
    p = [0] * (n + 1) # Кто сейчас назначен каждому столбцу
    way = [0] * (n + 1) # Путь, чтобы потом восстановить
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (n + 1) # для каждого столбца храним минимальную найденную стоимость
        used = [False] * (n + 1) # Показывает, какой столбец уже используется в текущем поиске
        while True:
            used[j0] = True
            i0 = p[j0] # Строка, связанная с данным столбцом
            delta = INF # неизвестная минимальная величина
            j1 = 0 # Столбец, куда будем двигаться дальше
            for j in range(1, n + 1): # Перебираем столбцы
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j] # Приведенная стоимость ребра
                    if cur < minv[j]: # Если нашли более дешевый путь
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta: # Является ли найденная стоимость лучшей среди всех
                        delta = minv[j]
                        j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta # Увеличиваем потенциал соответствующей строки
                    v[j] -= delta # Уменьшаем потенциал столбца
                else:
                    minv[j] -= delta # Уменьшаем значение, если столбец не используется
            j0 = j1 # Найденный лучший столбец
            if p[j0] == 0: # Свободный столбец
                break
        while True: # Восстановление пути
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    assignment = [-1] * n
    for j in range(1, n + 1):
        assignment[p[j] - 1] = j - 1
    return assignment # Возвращаем результат    


def min_weight_perfect_matching(n, m, edges): # Поиск минимального полного паросочетания в двудольном графе
    if n != m:
        return None
    weights = {}
    for a, b, c in edges: # Перебираем ребра
        if (a, b) not in weights or c < weights[(a, b)]: # Если ребра нет или новый вес меньше ->
            weights[(a, b)] = c # Сохраняем минимальный вес
    big = (sum(abs(c) for c in weights.values()) + 1) * (n + 1) # Если ребра нет, создается ребро с огромным весом
    cost = [[weights.get((i, j), big) for j in range(n)] for i in range(n)] # Создаем квадратную матрицу
    assignment = hungarian_min(cost) # Запуск венгерского алгоритма
    matching = [] # Создаем список выбранных ребер
    for i, j in enumerate(assignment):
        if (i, j) not in weights: # Если выбранного ребра нет - значит полного паросочетания нет
            return None
        matching.append((i, j, weights[(i, j)])) # Добавляем настоящее ребро 
    return sum(c for _, _, c in matching), matching # Возвращается общий вес и список ребер


def bipartition(n, adjacency): # Проверка на двудольность
    color = [-1] * n # Присваиваем всем вершинам неизвестный цвет
    for s in range(n): # Перебираем все вершины
        if color[s] != -1: # Если вершина раскрашена - пропускаем
            continue
        color[s] = 0 
        queue = deque([s]) # Очередь для BFS
        while queue:
            x = queue.popleft() # Берем следующую вершину
            for y in adjacency[x]: # Перебираем ее соседей
                if color[y] == -1: 
                    color[y] = 1 - color[x] # Красим вершину в противоположный цвет
                    queue.append(y)
                elif color[y] == color[x]:
                    return None # Граф не двудольный
    return color # Возвращаем раскраску 


def general_graph_matching(n, edges):
    best = {}
    adjacency = [set() for _ in range(n)] # Список соседей 
    for a, b, c in edges: # Перебор всех ребер
        if a == b:
            continue # Игнорирование петель
        key = (min(a, b), max(a, b)) # Единый вид
        if key not in best or c < best[key]: # Оставляем минимальный вес, если уже встречали ребро
            best[key] = c
        adjacency[a].add(b)
        adjacency[b].add(a) # Соседство записываем в обе стороны
    color = bipartition(n, adjacency)
    if color is None:
        return None
    left = [v for v in range(n) if color[v] == 0] # Все вершины цвета 0 - влево
    right = [v for v in range(n) if color[v] == 1] # Все вершины цвета 1 - вправо
    left_index = {v: i for i, v in enumerate(left)} # Новые индексы для левых
    right_index = {v: i for i, v in enumerate(right)} # Новые индексы для правых
    bip_edges = []
    for (a, b), c in best.items():
        if color[a] == 1:
            a, b = b, a
        bip_edges.append((left_index[a], right_index[b], c))
    outcome = min_weight_perfect_matching(len(left), len(right), bip_edges) # Запуск венгерского алгоритма
    if outcome is not None:
        weight, matching = outcome
        outcome = (weight, [(left[i], right[j], c) for i, j, c in matching])
    return best, outcome # Возврат лучших ребер и минимального паросочетания


def to_dot(n, best_edges, outcome): # Сохранение в DOT
    if outcome is None:
        chosen = set()
        title = "no perfect matching"
    else:
        weight, matching = outcome
        chosen = {(min(a, b), max(a, b)) for a, b, _ in matching}
        title = f"minimum perfect matching weight = {weight}"
    lines = [
        "graph G {",
        f'  label="{title}";',
        "  labelloc=t;",
        "  node [shape=circle];",
    ]
    for v in range(n):
        lines.append(f"  {v};")
    for (a, b), c in sorted(best_edges.items()):
        if (a, b) in chosen:
            lines.append(f'  {a} -- {b} [label="{c}", color=red, penwidth=3];') # Красным и толстым если ребро входит в паросочестание
        else:
            lines.append(f'  {a} -- {b} [label="{c}", color=gray];') # Иначе серым
    lines.append("}")
    return "\n".join(lines)


def read_ints(prompt, count): 
    while True:
        parts = input(prompt).split()
        try:
            if len(parts) != count:
                raise ValueError
            values = [int(x) for x in parts]
            if any(x < 0 for x in values):
                raise ValueError
            return values
        except ValueError:
            print(f"Нужно ввести {count} неотрицательных целых чисел через пробел")


def read_matrix(rows, cols):
    matrix = []
    for i in range(rows):
        while True:
            parts = input(f"Строка {i + 1} из {rows}: ").split()
            try:
                if len(parts) != cols:
                    raise ValueError
                row = [None if x == "-" else parse_number(x) for x in parts]
                break
            except ValueError:
                print(f"Нужно ввести {cols} значений через пробел (число или - если ребра нет)")
        matrix.append(row)
    return matrix


def run_bipartite():
    n, m = read_ints("Вершин слева и справа (n m): ", 2)
    print("Матрица весов (строки - левая доля, столбцы - правая, - означает отсутствие ребра):")
    matrix = read_matrix(n, m)
    edges = [
        (i, j, matrix[i][j])
        for i in range(n)
        for j in range(m)
        if matrix[i][j] is not None
    ]
    outcome = min_weight_perfect_matching(n, m, edges)
    print()
    if outcome is None:
        print("Полного паросочетания не существует")
        return
    weight, matching = outcome
    print("Минимальный вес полного паросочетания:", weight)
    for a, b, c in sorted(matching):
        print(f"L{a} - R{b} (вес {c})")


def run_general():
    n = read_ints("Число вершин (n): ", 1)[0]
    print("Матрица смежности с весами (- означает отсутствие ребра, диагональ игнорируется):")
    matrix = read_matrix(n, n)
    edges = [
        (i, j, matrix[i][j])
        for i in range(n)
        for j in range(n)
        if i != j and matrix[i][j] is not None
    ]
    result = general_graph_matching(n, edges)
    print()
    if result is None:
        print("Граф не двудольный: венгерский алгоритм неприменим")
        return
    best, outcome = result
    dot = to_dot(n, best, outcome)
    print(dot)
    with open("matching.dot", "w", encoding="utf-8") as f:
        f.write(dot + "\n")
    print()
    print("DOT сохранён в файл matching.dot")


def main():
    print("1 - двудольный граф (минимальный вес полного паросочетания)")
    print("2 - произвольный граф (паросочетание в формате DOT)")
    while True:
        choice = input("Выберите режим (1/2): ").strip()
        if choice == "1":
            run_bipartite()
            break
        if choice == "2":
            run_general()
            break
        print("Введите 1 или 2")


if __name__ == "__main__":
    main()