import heapq
import math


class AStarPlanner:

    def __init__(self, width=20, height=16):
        self.width = width
        self.height = height

    def heuristic(self, a, b):
        return math.hypot(
            a[0] - b[0],
            a[1] - b[1]
        )

    def get_neighbors(self, node):

        x, y = node

        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1)
        ]

        neighbors = []

        for dx, dy in directions:

            nx = x + dx
            ny = y + dy

            if 1 <= nx <= 18 and 1 <= ny <= 14:
                neighbors.append((nx, ny))

        return neighbors

    def is_blocked(self, node, obstacles):

        x, y = node

        for ox, oy, width, height in obstacles:

            ox *= 2
            oy *= 2
            width *= 2
            height *= 2

            if (
                ox - 1 <= x <= ox + width + 1
                and
                oy - 1 <= y <= oy + height + 1
            ):
                return True

        return False

    def plan(self, start, goal, obstacles):

        start = (
            round(start[0] * 2),
            round(start[1] * 2)
        )

        goal = (
            round(goal[0] * 2),
            round(goal[1] * 2)
        )

        open_set = [(0, start)]

        came_from = {}

        g_score = {
            start: 0
        }

        while open_set:

            _, current = heapq.heappop(open_set)

            if current == goal:

                path = [current]

                while current in came_from:

                    current = came_from[current]

                    path.append(current)

                path.reverse()

                return [
                    (x / 2, y / 2)
                    for x, y in path
                ]

            for neighbor in self.get_neighbors(current):

                if self.is_blocked(
                    neighbor,
                    obstacles
                ):
                    continue

                new_cost = (
                    g_score[current]
                    + self.heuristic(
                        current,
                        neighbor
                    )
                )

                if (
                    neighbor not in g_score
                    or new_cost < g_score[neighbor]
                ):

                    came_from[neighbor] = current

                    g_score[neighbor] = new_cost

                    priority = (
                        new_cost
                        + self.heuristic(
                            neighbor,
                            goal
                        )
                    )

                    heapq.heappush(
                        open_set,
                        (
                            priority,
                            neighbor
                        )
                    )

        return []