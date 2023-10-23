from random import random

for n in range(100, 1501, 100):
    # Generowanie grafu acyklicznego o n wierzchołkach
    graph = [[] for _ in range(n)]
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            if len(graph[i-1]) < n/2 and len(graph[j-1]) < n/2 and random() < 0.5:
                graph[i-1].append(j)
                graph[j-1].append(i)

    # Zapisywanie grafu do pliku
    with open(f"graf_{n}.txt", "w") as f:
        num_edges = sum(len(adj) for adj in graph)
        f.write(f"{n} {num_edges}\n")
        for i in range(1, n+1):
            for j in graph[i-1]:
                if i-1 < j:
                    f.write(f"{i} {j}\n")
