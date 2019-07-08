from bearlibterminal import terminal
import time
import random

CELL = "O"
DEAD_CELL = "."
EMPTY = " "
TERMINAL_WIDTH = 100
TERMINAL_HEIGHT = 45
MAP_WIDTH = 100
MAP_HEIGHT = 40
#String for the terminal configuration. Terminal is 5 Tiles higher as the game to allow stats to be
#displayed.
TERMINAL_SET_STRING = f"window.size = {TERMINAL_WIDTH}x{TERMINAL_HEIGHT}"
NUM_UNDERPOP = 2
NUM_STAY_ALIVE = [2, 3]
NUM_OVERPOP = 3
NUM_REPRO = 3


class MapManager():
    """
    As the name suggests, this class manages the maps used in the game, especially the switching
    between the maps. the active map represents the current state, while the buffer map represents the
    state in the next turn.
    A map is a list of lists of strings.
    """
    active_map = []
    buffer_map = []
    temp_map = []
    def __init__(self):
        for x in range(MAP_WIDTH):
            self.active_map.append([EMPTY]* MAP_HEIGHT)
            self.buffer_map.append([EMPTY]* MAP_HEIGHT)
    def switch_map(self):
        self.temp_map = self.active_map
        self.active_map = self.buffer_map
        self.buffer_map = self.temp_map
        

class StatCounter():
    """
    This class keeps track of various ingame variables.
    cell_count: Number of currently alive cells.
    instance_count: Number of times the game was started in the current run.
    turn_count: Number of turns elapsed in this instance.
    still_alive: returns True if there are living cells left. -> End-condition.
    """
    cell_count = 0
    instance_count = 0
    turn_count = 0
    def still_alive(self):
        if self.cell_count <= 0:
            return False
        else:
            return True


map_manager = MapManager()

stat_counter = StatCounter()


def get_num_neighbor(test_x, test_y, active_map):
    """
    This Function returns the number of living cells on the 8 tiles surrounding the input coordinates.
    The function tests the active map.
    This function is also responsible for the 'wrapping around' of the map, since it checks the opposite
    site of the map if the neighbouring tile would be outside the map.
    """
    counter = 0
    for x in range(test_x - 1, test_x + 2):
        for y in range(test_y - 1, test_y + 2):
            copy_x = x
            copy_y = y
            if copy_x == MAP_WIDTH:
                copy_x = 0
            if copy_x == -1:
                copy_x = MAP_WIDTH - 1
            if copy_y == MAP_HEIGHT:
                copy_y = 0
            if copy_y == -1:
                copy_y = MAP_HEIGHT - 1
            if copy_x == test_x and copy_y == test_y:
                continue
            else:
                tile_content = active_map[copy_x][copy_y]
                if active_map[copy_x][copy_y] == CELL:
                    counter += 1
                else:
                    continue
    return counter
                




def seed_map():
    """
    This function creates the initial population for the game. Only a area in the center is seeded.
    This is not necessary but seems to produce more interesting games.
    For each tile in the area, if a rando number exceeds a threshold, a cell is placed. (The string'O').
    Otherwise an empty TIle is placed (' ').
    """
    #Clears the map before seeding
    terminal.clear()
    #Goes over each tile in the map, top to bottom, left to right.
    for x in range(int(MAP_WIDTH / 2 - 10), int(MAP_WIDTH / 2 + 10)):
        for y in range(int(MAP_HEIGHT / 2 - 10), int(MAP_HEIGHT / 2 + 10)):
            if random.random() >= 0.2:
                map_manager.active_map[x][y] = CELL
                terminal.put(x, y, CELL)
                #count cells placed, i.e. alive cells.
                stat_counter.cell_count += 1
            else:
                map_manager.active_map[x][y] = EMPTY
    
def game_loop():
    """
    The main loop of the game.
    """
    #If the Escape key was not pressed, proceed. peek() is not bloccking
    #and does not remove the input from the queue
    while not terminal.peek() == terminal.TK_ESCAPE:
        #Remove any input from the queue
        terminal.read()
        #set counters to zero
        stat_counter.turn_count = 0
        stat_counter.cell_count = 0
        #seed the map
        seed_map()
        #Making the seeded map visible
        terminal.refresh()
        stat_counter.instance_count += 1
        #Display the instance count below the actual game.
        terminal.print_(0, 41, f"Instance: {stat_counter.instance_count}")
        #As long as there are still cells alive:
        while stat_counter.still_alive():
            #increment turn count and display it.
            stat_counter.turn_count += 1
            terminal.print_(0, 42, f"Turn: {stat_counter.turn_count}")
            #Nested For-Loops to go over every tie in the map, top to bottom, left to right.
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    #save the string currently in this tile
                    temp_char = terminal.pick(x, y)
                    #Debug variables
                    is_cell = False
                    is_killed = False
                    is_born = False
                    stays_alive = False
                    stays_dead = False
                    #get Number of neighbors
                    num_neighbor = get_num_neighbor(x, y, map_manager.active_map)
                    #FIrst check if tile already contains a cell
                    if map_manager.active_map[x][y] == CELL:
                        is_cell = True
                        #Conditions for dying and staying alive
                        if not num_neighbor in NUM_STAY_ALIVE:
                            is_killed = True
                            map_manager.buffer_map[x][y] = DEAD_CELL
                            terminal.put(x, y, DEAD_CELL)
                            stat_counter.cell_count -= 1
                        else:
                            map_manager.buffer_map[x][y] = CELL
                            stays_alive = True
                            terminal.put(x, y, temp_char)
                    #If not already a cell:
                    else:
                        #Conditions for staying dead or a new cell being born
                        if num_neighbor == 3:
                            is_born = True
                            map_manager.buffer_map[x][y] = CELL
                            terminal.put(x, y, CELL)
                            stat_counter.cell_count += 1
                        else:
                            map_manager.buffer_map[x][y] = temp_char
                            stays_dead = True
                            terminal.put(x, y, temp_char)
                    #Display the cell counter
                    terminal.print_(0, 43, f"Cells: {stat_counter.cell_count}")
            #Make window visible
            terminal.refresh()
            #switch the active and the buffer map
            map_manager.switch_map()
            #Check for key Press: Escape quits the game, space starts a new run
            if terminal.peek() == terminal.TK_SPACE:
                break
            if terminal.peek() == terminal.TK_ESCAPE:
                break
#Initialize the terminal
terminal.open()
#Configure the terminal
terminal.set(TERMINAL_SET_STRING)
game_loop()
#Deinitialize the terminal for a n orderly exit.
terminal.close()


