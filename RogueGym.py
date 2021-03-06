import time
import os
import copy
import numpy as np
import random

directions = [np.asarray([-1, 0]), np.asarray([0, -1]), np.asarray([1, 0]), np.asarray([0, 1])]

class Block:
    def __init__(self, block_id=-1, indicator="?", name="unknown", movable=False):
        self.block_id = block_id
        self.indicator = indicator
        self.name = name
        self.movable = movable

class Map:
    def __init__(self, size=(10, 10), data=[Block() for _ in range(100)]):
        self.size = size
        self.data = data

    def _index(self, pos):
        # x + y*w
        return pos[1] + pos[0]*self.size[1]

    def get_block(self, pos):
        return self.data[self._index(pos)]

    def set_block(self, pos, block):
        self.data[self._index(pos)] = copy.copy(block)

    def print(self):
        for y in range(self.size[0]):
            for x in range(self.size[1]):
                indicator = self.get_block((y, x)).indicator
                print(indicator, end="")
            print()


def load_map(block_set, block_list):
    data = []
    positions = [None for _ in range(10)]
    for y, line in enumerate(block_list):
        for x, block in enumerate(line):
            if block in [str(i) for i in range(10)]:
                positions[int(block)] = (y, x)
                data.append(Block())
            else:
                #print(block)
                data.append(copy.copy(block_set[block]))
    size = (len(block_list), len(block_list[0]))
    while positions[-1] == None:
        positions.pop()
    return (size, data), positions

def map_to_ob(map_, pos, direction):
    look_dict = {}
    look_dict[(-1, 0)] = [
        np.asarray([-2,-1]), np.asarray([-2, 0]), np.asarray([-2, 1]),
        np.asarray([-1,-1]), np.asarray([-1, 0]), np.asarray([-1, 1]),
        np.asarray([ 0,-1]), np.asarray([ 0, 1]),
    ]
    look_dict[(0, -1)] = [
        np.asarray([1, -2]), np.asarray([0, -2]), np.asarray([-1, -2]),
        np.asarray([1, -1]), np.asarray([0, -1]), np.asarray([-1, -1]),
        np.asarray([1,  0]), np.asarray([-1, 0]),
    ]
    look_dict[(1, 0)] = [
        np.asarray([2,  1]), np.asarray([2,  0]), np.asarray([2, -1]),
        np.asarray([1,  1]), np.asarray([1,  0]), np.asarray([1, -1]),
        np.asarray([0,  1]), np.asarray([0, -1]),
    ]
    look_dict[(0, 1)] = [
        np.asarray([-1, 2]), np.asarray([0, 2]), np.asarray([1, 2]),
        np.asarray([-1, 1]), np.asarray([0, 1]), np.asarray([1, 1]),
        np.asarray([-1, 0]), np.asarray([1, 0]),
    ]

    blocks = []
    for look in look_dict[tuple(direction)]:
        block_id = map_.get_block(look+pos).block_id
        blocks.append(block_id)
    return blocks

def print_ob(ob):
    for i in range(len(ob)):
        if i%3 == 0:
            print()
        if i == 7:
            print("^", end="")
        print(ob[i], end="")

def ob_to_hot_vectors(ob, block_type_num):
    hot_vectors = np.zeros((3*3-1, block_type_num), dtype=np.float32)
    for i in range(len(ob)):
        hot_vectors[i][ob[i]] = 1.0
    return hot_vectors

class RogueEnv:
    def __init__(self, action_set=[("move", 1), ("move", -1), ("turn", 1), ("turn", -1)]):
        self.action_set = action_set

    #    N=(-1,0)
    # W=(0,-1) E=(0,1)
    #    S=(1,0)
    def reset(self, map_, start_direction, start_position):
        self.map_ = map_
        self.agent_direction = start_direction
        self.agent_position = start_position

    def print_map(self):
        map_ = copy.deepcopy(self.map_)
        if self.agent_direction[0] == -1 and self.agent_direction[1] == 0:
            indicator = "^"
        elif self.agent_direction[0] == 0 and self.agent_direction[1] == -1:
            indicator = "<"
        elif self.agent_direction[0] == 1 and self.agent_direction[1] == 0:
            indicator = "v"
        elif self.agent_direction[0] == 0 and self.agent_direction[1] == 1:
            indicator = ">"
        map_.set_block(self.agent_position,
                Block(block_id=-1, indicator=indicator, name="agent", movable=False))
        map_.print()

    def step(self, action):
        if self.action_set[action] == ("move", 1):
            new_pos = self.agent_position + self.agent_direction
            if self.map_.get_block(new_pos).movable:
                self.agent_position = new_pos
        elif self.action_set[action] == ("move", -1):
            new_pos = self.agent_position - self.agent_direction
            if self.map_.get_block(new_pos).movable:
                self.agent_position = new_pos
        elif self.action_set[action] == ("turn", 1):
            if self.agent_direction[0] == -1 and self.agent_direction[1] == 0:
                self.agent_direction = np.asarray([0, -1])
            elif self.agent_direction[0] == 0 and self.agent_direction[1] == -1:
                self.agent_direction = np.asarray([1, 0])
            elif self.agent_direction[0] == 1 and self.agent_direction[1] == 0:
                self.agent_direction = np.asarray([0, 1])
            elif self.agent_direction[0] == 0 and self.agent_direction[1] == 1:
                self.agent_direction = np.asarray([-1, 0])
        elif self.action_set[action] == ("turn", -1):
            if self.agent_direction[0] == -1 and self.agent_direction[1] == 0:
                self.agent_direction = np.asarray([0, 1])
            elif self.agent_direction[0] == 0 and self.agent_direction[1] == -1:
                self.agent_direction = np.asarray([-1, 0])
            elif self.agent_direction[0] == 1 and self.agent_direction[1] == 0:
                self.agent_direction = np.asarray([0, -1])
            elif self.agent_direction[0] == 0 and self.agent_direction[1] == 1:
                self.agent_direction = np.asarray([1, 0])
        else:
            raise

def main():
    block_set = {}
    block_set["."] = Block(block_id=0, indicator=".", name="air", movable=True)
    block_set["#"] = Block(block_id=1, indicator="#", name="stone", movable=False)
    block_set["R"] = Block(block_id=2, indicator="R", name="red_tile", movable=True)
    block_set["B"] = Block(block_id=3, indicator="B", name="blue_tile",
            movable=True)
    block_set["Y"] = Block(block_id=4, indicator="Y", name="yellow_tile",
            movable=True)
    block_set["G"] = Block(block_id=5, indicator="G", name="green_tile",
            movable=True)


    map_str = [
        "#########",
        "#########",
        "#########",
        "###2.3###",
        "####.####",
        "####.####",
        "###.01###",
        "#########",
        "#########",
        "#########",
    ]
    map_data, positions = load_map(block_set, map_str)
    map_ = Map(*map_data)
    for pos in positions:
        map_.set_block(pos, block_set["."])
    action_set = [("move", 1), ("move", -1), ("turn", 1), ("turn", -1)]

    env = RogueEnv(action_set=action_set)
    indicator = np.random.choice(("G", "Y"))
    map_.set_block(positions[2], block_set["B"])
    map_.set_block(positions[3], block_set["R"])
    map_.set_block(positions[1], block_set[indicator])
    env.reset(map_=map_, start_direction=np.asarray([-1,0]), start_position=np.asarray(positions[0]))
    print(env.agent_position)
    for step in range(5000):
        os.system("clear")
        env.print_map()
        print(env.agent_direction)
        ob = map_to_ob(map_, direction=env.agent_direction, pos=env.agent_position)
        print_ob(ob)
        hv = ob_to_hot_vectors(ob, block_type_num=6)
        print_ob(hv)
        action = random.randrange(len(action_set))
        env.step(action)
        time.sleep(0.1)
        input()
    m = Map()
    m.print()

if __name__ == "__main__":
    main()
