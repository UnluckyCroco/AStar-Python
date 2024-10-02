import tkinter as tk

from colorama import Fore
from math import *

root = tk.Tk()
canvas = tk.Canvas(height=300, width=300, highlightthickness=1, highlightbackground="black")
canvas.grid(row=0, column=2, rowspan=6, columnspan=2, padx=10, pady=10)
cell_height = 15
cell_width = 15


def print_3d_array(three_d_array):
    width = len(three_d_array[0])
    print(Fore.RED + "_" * (width * 3 + 3))
    for array in three_d_array:
        print(Fore.RED + "| ", end="")
        for value in array:
            if type(value) == Cell:
                text = str(value.value)
                print(Fore.WHITE + (text if len(text) == 2 else f" {text}"), end=" ")
        print(Fore.RED + "|")
    print(Fore.RED + "-" * (width * 3 + 3))


def subtract_weight(x):
    return x - 1 if x > 1 else x


def add_weight(x):
    return x + 1 if 9 > x > 0 else x


def set_wall(x):
    return -1


def reset_tile(x):
    return 1


def set_start(x):
    return 0


def set_end(x):
    return -2


def get_color(value):
    if value == -1:
        return "black"
    if value == 0:
        return "green"
    if value == -2:
        return "red"
    return "gray92"


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented

        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Cell:
    def __init__(self, value=1, text=None, rectangle=None, x=0, y=0):
        self.value = value
        self.text = text
        self.rectangle = rectangle
        self.cords = Point(x, y)

    def set_value(self, selected_option):
        match selected_option:
            case "add_weight":
                self.value = self.value + 1 if 9 > self.value > 0 else self.value
            case "subtract_weight":
                self.value = self.value - 1 if self.value > 1 else self.value
            case "set_wall":
                self.value = -1
            case "reset_tile":
                self.value = 1
            case "set_start":
                if not field.find_first(0):
                    self.value = 0
            case "set_end":
                if not field.find_first(-2):
                    self.value = -2
        self.set_text()
        self.set_color()

    def set_text(self):
        if self.text:
            if self.value < 2:
                canvas.delete(self.text)
                self.text = None
            else:
                canvas.itemconfig(self.text, text=self.value)
        elif self.value > 1:
            self.text = canvas.create_text(self.cords.x * cell_width + cell_width / 2, self.cords.y * cell_height +
                                           cell_height / 2, text=f"{self.value}")

    def set_color(self, color=None):
        if color:
            canvas.itemconfig(self.rectangle, fill=color)
        else:
            canvas.itemconfig(self.rectangle, fill=get_color(self.value))


class Field:
    def __init__(self):
        self.selected_option = add_weight
        self.cells = []
        self.width = 0
        self.height = 0

    def clicked(self, x, y):
        self.cells[y][x].set_value(self.selected_option.__name__)

    def find_values(self, value):
        temp_array = []
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    temp_array.append(cell)

        return temp_array

    def find_first(self, value) -> Cell or None:
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    return cell

        return None

    def reset_colors(self):
        if not len(self.cells):
            return
        for cell_row in self.cells:
            for cell in cell_row:
                cell.set_color()

    def reset_field(self):
        for cell_row in self.cells:
            for cell in cell_row:
                cell.set_value("reset_tile")


field = Field()


def set_function(function):
    field.selected_option = function


def clicked(event):
    x = floor(event.x / cell_width)
    y = floor(event.y / cell_height)
    # print(f"{x} {y}")
    if len(field.cells):
        field.clicked(x, y)


def generate_field():
    new_height = height_entry_text.get()
    new_width = width_entry_text.get()
    if not (new_height.isdigit() and new_width.isdigit()):
        return
    height = int(new_height)
    width = int(new_width)
    if not (height > 0 and width > 0):
        return

    existing_height = 0
    existing_width = 0

    field.width = width
    field.height = height
    if len(field.cells):
        existing_height = len(field.cells)
        existing_width = len(field.cells[0])

    if existing_height > height:
        field.cells = field.cells[:height]

    if existing_width > width:
        field.cells = [i[:width] for i in field.cells]

    canvas.config(width=width * cell_width - 1, height=height * cell_height - 1)
    for y in range(0, height):
        y_coord = y * cell_height
        if y > existing_height - 1:
            field.cells.append([])
        for x in range(0, width):
            if not ((y > existing_height - 1) or (x > existing_width - 1)):
                continue
            x_coord = x * cell_width
            cell = canvas.create_rectangle(x_coord, y_coord, x_coord + cell_width, y_coord + cell_height,
                                           outline="black")
            field.cells[y].append(Cell(rectangle=cell, x=x, y=y))

    field.reset_colors()


class AStarQueueItem:
    def __init__(self, cords: Point, total_cost: float, prev_cords, end_cords: Point):
        self.cords = cords
        self.total_cost = total_cost
        self.heuristic = sqrt(abs(cords.x - end_cords.x) ** 2 + abs(cords.y - end_cords.y) ** 2) + total_cost
        self.prev_cords = prev_cords


class AStarQueue:
    def __init__(self, start: Point, end: Point):
        self.queue = []
        self.path = []
        self.start = start
        self.end = end
        self.queue.append(AStarQueueItem(start, 0, None, end))
        self.steps = 0

    def find_cords_in_path(self, cords: Point) -> AStarQueueItem or None:
        return next((item for item in self.path if item.cords == cords), None)

    def find_cords_in_queue(self, cords: Point) -> AStarQueueItem or None:
        return next((item for item in self.queue if item.cords == cords), None)

    def insert_item(self, new_item: AStarQueueItem):
        for i, item in enumerate(self.queue):
            if new_item.heuristic < item.heuristic:
                self.queue.insert(i, new_item)
                return
        self.queue.append(new_item)


def draw_path(head: AStarQueueItem, start: Point, end: Point, color="yellow", step: bool = False):
    while head:
        if head.cords != start and head.cords != end:
            field.cells[head.cords.y][head.cords.x].set_color(color)
            if step:
                stepped_astar.prev_path.append(head.cords)
        head = head.prev_cords


def solve_astar(astar, step: bool = False):
    width = len(field.cells[0])
    height = len(field.cells)

    head: AStarQueueItem = astar.queue[0]
    # print(f"Head {head.cords}")
    if head.cords == astar.end:
        astar.path.append(head)
        if step:
            stepped_astar.reset_prev_path()
        return astar

    if head.cords != astar.start:
        field.cells[head.cords.y][head.cords.x].set_color("gray50")

    if step:
        stepped_astar.reset_prev_path()
        draw_path(head, astar.start, astar.end, "light yellow", True)

    for y in range(-1, 2):
        for x in range(-1, 2):
            # new cords same as current
            if x == 0 and y == 0:
                continue

            curr_cords: Point = head.cords
            new_cords = Point(curr_cords.x + x, curr_cords.y + y)

            # out of bounds check
            if new_cords.x > width - 1 or new_cords.x < 0 or new_cords.y > height - 1 or new_cords.y < 0:
                continue

            # previous coordinates are skipped
            if new_cords == head.prev_cords:
                continue

            curr_cell: Cell = field.cells[curr_cords.y + y][curr_cords.x + x]

            # wall
            if curr_cell.value == -1:
                continue

            # diagonal movement will take the pythagorean formula of the value of the tile itself + avg of diagonal
            # ______
            # | 42 |
            # | x3 |
            # ------
            # movement to 2 from x costs root(avg(3, 4)**2 + 2**2) = root(16.25) = 4.0~
            if abs(y) + abs(x) == 2:
                vert_value = field.cells[curr_cords.y + y][curr_cords.x].value
                hori_value = field.cells[curr_cords.y][curr_cords.x + x].value

                # diagonal is wall -> skip
                if vert_value == -1 or hori_value == -1:
                    continue

                vert_value = vert_value if vert_value > 0 else 1
                hori_value = hori_value if hori_value > 0 else 1
                adj_value = curr_cell.value if curr_cell.value > 0 else 1
                avg_value = (vert_value + hori_value) / 2
                new_cost = sqrt(avg_value ** 2 + adj_value ** 2)
            else:
                new_cost = curr_cell.value if curr_cell.value > 0 else 1

            new_item = AStarQueueItem(new_cords, head.total_cost + new_cost, head, astar.end)

            # there's only ever 1 of a given coordinate in the queue or path
            queue_item = astar.find_cords_in_queue(new_cords)
            path_item = astar.find_cords_in_path(new_cords)

            # print(f"{new_item.cords}:")
            # check if old item in path and queue heuristic is higher than the new heuristic, if so, delete the old item
            if path_item:
                # print(f"Path: {path_item.cords} - {path_item.heuristic} and {new_item.cords} - {new_item.heuristic}")
                if new_item.heuristic < path_item.heuristic:
                    # print(f"Not skipped {new_item.cords} from path")
                    astar.path.remove(path_item)
                else:
                    continue
                # print(f"Skipped {new_item.cords} from path")

            if queue_item:
                # print(f"Queue: {queue_item.cords}")
                if new_item.heuristic < queue_item.heuristic:
                    # print(f"Not skipped {new_item.cords} from queue")
                    astar.queue.remove(queue_item)
                else:
                    continue
                # print(f"Skipped {new_item.cords} from queue")

            # print(f"Point: {new_item.cords} with heuristic of {new_item.heuristic}")
            astar.insert_item(new_item)
            if new_item.cords != astar.end:
                field.cells[new_item.cords.y][new_item.cords.x].set_color("gray70")
            # print()

    astar.path.append(head)
    astar.queue.remove(head)
    astar.steps += 1
    # print()


def astar_loop(astar):
    while len(astar.queue):
        solve_astar(astar)
        if astar.path[-1].cords == astar.end:
            return astar

    # no solution
    print(f"No solution found! It took {astar.steps} steps to figure this out")
    return False


def start_astar():
    print_3d_array(field.cells)

    start = field.find_first(0)
    end = field.find_first(-2)
    if not (start and end):
        return
    astar = AStarQueue(start.cords, end.cords)
    field.reset_colors()

    solution = astar_loop(astar)

    if not type(solution) == AStarQueue:
        return False

    print(f"This solution took {astar.steps} steps")
    draw_path(solution.path[-1], start.cords, end.cords)


    # point: Point
    # for point in path:
    #     if point != start.cords and point != end.cords:
    #         field.cells[point.y][point.x].set_color("yellow")
    #     print(point)


class AStarStep:
    def __init__(self):
        self.astar = None
        self.prev_path = []

    def reset_prev_path(self):
        for cord in self.prev_path:
            field.cells[cord.y][cord.x].set_color("gray50")
        self.prev_path.clear()


stepped_astar = AStarStep()


def step_astar():
    start = field.find_first(0)
    end = field.find_first(-2)
    if not (start and end):
        return
    if not stepped_astar.astar:
        stepped_astar.astar = AStarQueue(start.cords, end.cords)

    if len(stepped_astar.astar.queue) == 0:
        print(f"No solution found! It took {stepped_astar.astar.steps} steps to figure this out")
        return

    solution = solve_astar(stepped_astar.astar, True)

    if not type(solution) == AStarQueue:
        return False

    print(f"This solution took {stepped_astar.astar.steps} steps")
    draw_path(solution.path[-1], start.cords, end.cords)


def reset_colors():
    if stepped_astar.astar:
        stepped_astar.astar = None
        stepped_astar.prev_path.clear()
    field.reset_colors()


def reset_field():
    field.reset_field()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root.title('A*')

    # settings
    settings_frame = tk.Frame(root)
    settings_frame.grid(row=0, column=0, rowspan=3, pady=10, padx=(10, 0), sticky="N")

    width_label = tk.Label(settings_frame, text="Width:")
    width_entry_text = tk.StringVar()
    width_entry = tk.Entry(settings_frame, width=10, textvariable=width_entry_text)

    height_label = tk.Label(settings_frame, text="Height:")
    height_entry_text = tk.StringVar()
    height_entry = tk.Entry(settings_frame, width=10, textvariable=height_entry_text)

    generate_button = tk.Button(settings_frame, text='Generate', command=generate_field, width=10)

    width_label.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="W")
    height_label.grid(row=1, column=0, padx=(10, 0), pady=10, sticky="W")
    width_entry.grid(row=0, column=1, padx=10, pady=10)
    height_entry.grid(row=1, column=1, padx=10, pady=10)
    generate_button.grid(row=2, padx=10, pady=10, columnspan=2)

    # other options
    bottom_left_frame = tk.Frame(root)
    bottom_left_frame.grid(row=3, column=0, rowspan=3, pady=10, padx=(10, 0), sticky="N")

    load_field_button = tk.Button(bottom_left_frame, text='Load field', width=15)
    save_field_button = tk.Button(bottom_left_frame, text='Save field', width=15)
    reset_field_button = tk.Button(bottom_left_frame, text='Reset field', width=15, command=reset_field)

    load_field_button.grid(row=0, column=0, pady=10, padx=10)
    save_field_button.grid(row=1, column=0, pady=10, padx=10)
    reset_field_button.grid(row=2, column=0, pady=10, padx=10)

    # map buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=0, column=4, rowspan=3, pady=10, padx=(0, 10), sticky="N")

    add_weight_button = tk.Button(button_frame, text='Add weight', width=15, command=lambda: set_function(add_weight))
    subtract_weight_button = tk.Button(button_frame, text='Subtract weight', width=15,
                                       command=lambda: set_function(subtract_weight))
    set_wall_button = tk.Button(button_frame, text='Set wall', width=15, command=lambda: set_function(set_wall))
    reset_tile_button = tk.Button(button_frame, text='Reset tile', width=15, command=lambda: set_function(reset_tile))
    set_start_button = tk.Button(button_frame, text='Set start', width=15, command=lambda: set_function(set_start))
    set_end_button = tk.Button(button_frame, text='Set end', width=15, command=lambda: set_function(set_end))

    add_weight_button.grid(row=0, column=0, padx=10, pady=10)
    subtract_weight_button.grid(row=0, column=1, padx=10, pady=10)
    set_wall_button.grid(row=1, column=0, padx=10, pady=10)
    reset_tile_button.grid(row=1, column=1, padx=10, pady=10)
    set_start_button.grid(row=2, column=0, padx=10, pady=10)
    set_end_button.grid(row=2, column=1, padx=10, pady=10)

    # play buttons
    play_frame = tk.Frame(root)
    play_frame.grid(column=4, row=3, pady=10, rowspan=3, padx=(0, 10), sticky="NW")

    start_button = tk.Button(play_frame, text='Start', width=15, command=start_astar)
    step_button = tk.Button(play_frame, text='Step', width=15, command=step_astar)
    reset_path_button = tk.Button(play_frame, text='Reset path', width=15, command=reset_colors)

    start_button.grid(row=0, column=0, pady=10, padx=10)
    step_button.grid(row=1, column=0, columnspan=2, pady=10, padx=10)
    reset_path_button.grid(row=2, column=0, pady=10, padx=10)

    canvas.bind('<Button>', clicked)

    root.mainloop()


# TODO: save map
# TODO: load map
# TODO: drag functionality
