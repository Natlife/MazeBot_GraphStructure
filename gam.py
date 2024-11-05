import pygame
import random
import sys
from collections import deque

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 600,600
GRID_SIZE = 60
CELL_SIZE = WIDTH // GRID_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)    # đích
BLUE = (0, 0, 255)   # bot
YELLOW = (255, 255, 0)  # màu line đường đi
LINEShortest=(0,255,255)
LINELonggest=(51,255,153)

# đỉnh me cung
class Node:
    def __init__(self, x, y):#constructor như trong jaav
        #x,y như đồ thị tọa độ 2D
        self.x = x
        self.y = y
        self.neighbors = []#lưu trữ các node cạnh current

    def add_neighbor(self, neighbor): #add node mới vào list(như .next của thầy)
        self.neighbors.append(neighbor)

# graph structure
class Graph:
    def __init__(self, width, height): #kích thước đồ thị được tạo
        self.nodes = {}# tạo dictionary(như hash)
        for x in range(width):
            for y in range(height):
                self.nodes[(x, y)] = Node(x, y) #key: value

    def add_edge(self, from_node, to_node):
        self.nodes[from_node].add_neighbor(to_node)
        self.nodes[to_node].add_neighbor(from_node)
        #khiến đồ thị vô hướng

#Tạo mê cung
class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for i in range(width)] for i in range(height)]#tạo đồ matrix WxH #1 coi là biến của Wall để tí dùng cho bot check đường rẽ
        # default tất cả block =1
        self.graph = Graph(width, height)
        self.generate_maze(0, 0) #0,0 là tọa độ bắt đầu khởi tạo maze
        self.add_intersections() #thêm ngã tư
    
    def add_intersections(self):
            
            for i in range(self.width//5 ):
                x = random.randint(2, self.width-3)
                y = random.randint(2, self.height -3)
                # Create cross intersections
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.grid[ny][nx] = 0
                        self.graph.add_edge((x, y), (nx, ny))


    def generate_maze(self, x, y):
        self.grid[y][x] = 0 #0 coi là line đường có thể đi
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)] #các option hướng đi từ tọa độ 0,0
        random.shuffle(directions) # hàm random list direction để kiểu đảo vị trí các hướng khi gọi sẽ ngẫu nhiên
        for dx, dy in directions:
            nx, ny = x + dx*2 , y + dy*2
            if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 1:#==1 là Wall 
                self.grid[y + dy][x + dx] = 0 # set thành line có thể di
                self.graph.add_edge((x, y), (nx, ny)) 
                self.generate_maze(nx, ny)
        
    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1 : color = WHITE
                else: color=BLACK
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))#vẽ các block 

# Xuất phát
class Start:
    def __init__(self,maze):
        self.x = 0
        self.y = 0
        self.maze = maze

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Đích
class Goal:
    def __init__(self, maze):
        self.x = random.randint(0, maze.width - 1)
        self.y = random.randint(0, maze.height - 1)
        while maze.grid[self.y][self.x] != 0:
            self.x = random.randint(0, maze.width - 1)
            self.y = random.randint(0, maze.height - 1)

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Bot tự di chuyển
class ShortestBot:
    def __init__(self, maze, goal):
        self.x = 0 # điểm bắt đầu
        self.y = 0
        self.goal = goal
        self.botColor=BLUE
        self.lineGo= LINEShortest
        self.visited = set()
        self.path = []  # lưu trữ hướng đi ngắn nhất
        

    def find_path(self, maze):
        # từ vị trí bot đến đích với đường đi ngắn nhất
        queue = deque([(self.x, self.y)])
        visited = set()
        visited.add((self.x, self.y))
        parent = {} #lưu block cha để sau khi scan có đường đi ngắn nhất
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            current = queue.popleft()
            if (current[0], current[1]) == (self.goal.x, self.goal.y):
                break

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < maze.width and 0 <= ny < maze.height:
                    if maze.grid[ny][nx] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = current
                        queue.append((nx, ny))

        #build đường từ vị trí bot đến đích
        self.path = []
        step = (self.goal.x, self.goal.y)
        while step in parent:
            self.path.append(step)
            step = parent[step]
        self.path.reverse()
    
    def move(self, maze):
        # có đường rẽ thì di chuyển 
        if not self.path:
            self.find_path(maze)

        if self.path:
                #Di chuyển đến ô tiếp theo trong đường đi
                if len(self.path) >1:
                    # Đổi màu ô mà bot đi qua
                    prev_x, prev_y = self.x, self.y
                    self.x, self.y = self.path[1]  # Di chuyển đến ô tiếp theo
                    self.path.pop(0)  # Xóa ô đã đi qua trong path
                    # Đổi màu ô đã đi qua 
                    #maze.grid[prev_y][prev_x] = 2  # 2 đại diện cho ô đã đi qua
                    self.visited.add((prev_x, prev_y))

    def draw(self, screen):
        pygame.draw.rect(screen, self.botColor, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class LongestBot:
    def __init__(self, maze, goal):
        self.x = 0 # điểm bắt đầu
        self.y = 0
        self.goal = goal
        self.botColor=GREEN
        self.lineGo= LINELonggest
        self.visited = set()
        self.path = []  # lưu trữ hướng đi ngắn nhất
    def find_path(self, maze):
        # DFS implementation for longest path
        stack = [(self.x, self.y, [])]
        visited = set()
        longest_path = []
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while stack:
            x, y, current_path = stack.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                current_path = current_path + [(x, y)]
                
                if (x, y) == (self.goal.x, self.goal.y):
                    if len(current_path) > len(longest_path):
                        longest_path = current_path
                    continue

                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < maze.width and 0 <= ny < maze.height:
                        if maze.grid[ny][nx] == 0 and (nx, ny) not in visited:
                            stack.append((nx, ny, current_path))

        self.path = longest_path[1:]
    def move(self, maze):
        # Di chuyển theo đường đi dài nhất
        if not self.path:
            self.find_path(maze)

        if self.path:
            if len(self.path) > 1:
                prev_x, prev_y = self.x, self.y
                self.x, self.y = self.path[1]  # Di chuyển đến ô tiếp theo
                self.path.pop(0)  # Xóa ô đã đi qua trong path
                #maze.grid[prev_y][prev_x] = 2  # 2 đại diện cho ô đã đi qua
                self.visited.add((prev_x, prev_y))

    def draw(self, screen):
        pygame.draw.rect(screen, self.botColor, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

# Hàm chính
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CSD Test")
    color=BLACK
    maze = Maze(GRID_SIZE, GRID_SIZE)
    startP = Start(maze)
    goal = Goal(maze)
    botShort = ShortestBot(maze, goal)  # Tạo bot với đích ngắn
    botLong= LongestBot(maze, goal) #Tạo bot với đích dài
    pygame.display.set_caption('Hello World!')
    clock = pygame.time.Clock()
    while True:
        

        # Di chuyển bot
        botShort.move(maze)
        botLong.move(maze)
        for event in pygame.event.get():
            if (botShort.x == goal.x and botShort.y == goal.y) :
                pygame.display.update()
                exit(1)
            if (botLong.x == goal.x and botLong.y == goal.y):
                pygame.display.update()
                exit(1)
        
        # Kiểm tra xem bot đã đến đích chưa
        
            

        screen.fill(BLACK)
        maze.draw(screen)
        # Vẽ mê cung với ô đã đi qua đè lên me me cung vua ve
        
        for y in range(maze.height):
            for x in range(maze.width):
                if (y==1 and x==0 and maze.grid[y][x]==0) or(y==0 and x==1 and maze.grid[y][x]==0) :
                        maze.grid[y][x]=2 
                if maze.grid[y][x] == 1: 
                    color = WHITE 
                elif maze.grid[y][x] == 2:
                    color = (255, 0, 127)  
                elif (x,y) in botShort.visited and (x,y) in botLong.visited:
                    color = (255, 0, 127)  
                elif (x,y) in botShort.visited:
                    color = LINEShortest  
                elif (x,y) in botLong.visited:
                    color = LINELonggest
                # elif maze.grid[y][x] == 2: # ô đã đi qua 
                #     if (x,y) in botShort.path and (x,y) in botLong.path:
                #         color = (255, 0, 127)  # Pink color for overlapping paths
                #     elif (x,y) in botLong.path:
                #         color = LINELonggest  # Green path for longest bot
                #     elif (x,y) in botShort.path:
                #         color = LINEShortest  # Cyan path for shortest bot
                #     else:
                #         color = YELLOW  # Default path color
                #     #color = LINEShortest
                #       # Đổi màu ô đã đi qua thành màu của mỗi bot đã setup
                else:
                    color=BLACK #white ở đây là wall, black là line đường đi
                pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        startP.draw(screen)
        botShort.draw(screen)
        botLong.draw(screen)
        goal.draw(screen)
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
