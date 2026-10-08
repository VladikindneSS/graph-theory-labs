import networkx as nx
import matplotlib.pyplot as plt


def check_planarity_and_draw(edges):
    graph = nx.Graph() # Создаем граф
    graph.add_edges_from(edges) # Добавляем ребра в граф

    is_planar, embedding = nx.check_planarity(graph) # Проверяем на планарность и получаем комбинаторную укладку

    if not is_planar:
        print("Граф непланарен.")
        return

    print("Граф планарен.")
    print("\nКомбинаторная укладка:")

    for vertex in embedding: # Выводим соседей каждой вершины по часовой стрелке
        neighbors = list(embedding.neighbors_cw_order(vertex))
        print(f"{vertex}: {neighbors}")

    pos = nx.planar_layout(graph)  # Геометрическая укладка

    plt.figure(figsize=(8, 6)) # Рисуем граф

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_size=800,
        node_color="lightgreen",
        edge_color="black",
        font_size=12
    )

    plt.title("Геометрическая укладка планарного графа")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    edges = [
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 3),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 5)
    ]

    check_planarity_and_draw(edges)
