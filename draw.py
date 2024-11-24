import matplotlib.pyplot as plt
import numpy as np

class DiagramDrawer:
    def __init__(self, root_node):
        self.root_node = root_node
        self.points = {}

    def draw(self):
        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        for command in self.root_node.children:
            if command.type == "Command":
                action = command.value.lower()

                if action == "побудувати":
                    self.draw_triangle(command, ax)
                elif action == "провести":
                    self.draw_element(command, ax)

        plt.axis('equal')
        plt.show()

    def draw_triangle(self, command, ax):
        points = command.children[1].value

        for i, point in enumerate(points):
            if point not in self.points:
                self.points[point] = (np.random.uniform(0, 10), np.random.uniform(0, 10))

        triangle_coords = [self.points[point] for point in points]

        x_coords, y_coords = zip(*triangle_coords)

        x_coords += (x_coords[0],)
        y_coords += (y_coords[0],)

        ax.plot(x_coords, y_coords, marker='o', markersize=5, label=f"Triangle {points}")
        for point, (x, y) in zip(points, triangle_coords):
            ax.text(x, y, point, fontsize=12, ha='right')

    def draw_element(self, command, ax):
        element_node = next(child for child in command.children if child.type == "ElementWithPoints")
        triangle_node = next(child for child in command.children if child.type == "Triangle")
        points = [child.value for child in element_node.children] # ex. [C, K]
        element_type = element_node.value.lower()

        if element_type.startswith("медіан"):
            triangle_points = triangle_node.value
            vertex = points[0]
            opposite_side = [p for p in triangle_points if p != vertex]

            if opposite_side[0] not in self.points:
                self.points[opposite_side[0]] = (np.random.uniform(0, 10), np.random.uniform(0, 10))
            if opposite_side[1] not in self.points:
                self.points[opposite_side[1]] = (np.random.uniform(0, 10), np.random.uniform(0, 10))

            x1, y1 = self.points[opposite_side[0]]
            x2, y2 = self.points[opposite_side[1]]
            midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)

            midpoint_label = points[1]
            self.points[midpoint_label] = midpoint
            print(self.points)
            vertex_coords = self.points[vertex]
            x_coords, y_coords = zip(*[vertex_coords, midpoint])
            ax.plot(x_coords, y_coords, 'g--', label=f"Median {vertex}-{midpoint_label}")

            ax.plot(midpoint[0], midpoint[1], 'go')
            ax.text(midpoint[0], midpoint[1], points[1], fontsize=12, ha='right')
        else:
            pass
