#server.py
import Pyro4
import pygame
import threading
import copy
from random import randint, sample
from char import Char
from bomb import Bomb
from gift import Gift
from wall import Wall
from fire import Fire
from modelChar import ModelChar
from modelWall import ModelWall
from modelBomb import ModelBomb
from modelGift import ModelGift
from modelFire import ModelFire


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Server(object):

    wall_factor = 53

    def __init__(self):
        self.__n_players = 0
        self.__model_char = self.__read_model_char()
        self.__model_bomb = self.__read_model_bomb()
        self.__model_gift = self.__read_model_gift()
        self.__model_wall = self.__read_model_wall()
        self.__model_fire = self.__read_model_fire()

        self.__chars = {}
        self.__bombs = {}
        self.__gifts = {}
        self.__walls = self.__create_random_walls()
        self.__static_walls = []
        self.__fires = {}

        self.__put_static_walls()

    # PRIVATE METHODS
    def __read_model_char(self):
        model_chars_return = {}
        file_descriptor = open("modelsDescriptor/charDesc.txt", 'r')
        lines = file_descriptor.readlines()
        file_descriptor.close()
        columns = int(lines.pop(0).split()[1])
        lines.pop(0)
        for line in lines:
            if len(line.split()) == columns:
                s_id_bomb_model, s_speed, s_n_bomb_max, s_power_bomb_add = map(int, line.split()[:-1])
                path = line.split()[-1:][0]
                model_char = ModelChar(s_id_bomb_model, s_speed, s_n_bomb_max, s_power_bomb_add, path)
                model_chars_return[model_char.get_id()] = model_char
        return model_chars_return

    def __read_model_bomb(self):
        model_bombs_return = {}
        file_descriptor = open("modelsDescriptor/bombDesc.txt", 'r')
        lines = file_descriptor.readlines()
        file_descriptor.close()
        columns = int(lines.pop(0).split()[1])
        lines.pop(0)
        for line in lines:
            if len(line.split()) == columns:
                s_power, s_timer = map(int, line.split()[:-1])
                path = line.split()[-1:][0]
                model_bomb = ModelBomb(s_power, s_timer, path)
                model_bombs_return[model_bomb.get_id()] = model_bomb
        return model_bombs_return

    def __read_model_gift(self):
        model_gifts_return = {}
        file_descriptor = open("modelsDescriptor/giftDesc.txt", 'r')
        lines = file_descriptor.readlines()
        file_descriptor.close()
        columns = int(lines.pop(0).split()[1])
        lines.pop(0)
        for line in lines:
            if len(line.split()) == columns:
                s_more_speed, s_more_n_bombs, s_more_power = map(int, line.split()[:-1])
                path = line.split()[-1:][0]
                model_gift = ModelGift(s_more_speed, s_more_n_bombs, s_more_power, path)
                model_gifts_return[model_gift.get_id()] = model_gift
        return model_gifts_return

    def __read_model_wall(self):
        model_walls_return = {}
        file_descriptor = open("modelsDescriptor/wallDesc.txt", 'r')
        lines = file_descriptor.readlines()
        file_descriptor.close()
        columns = int(lines.pop(0).split()[1])
        lines.pop(0)
        for line in lines:
            if len(line.split()) == columns:
                path = line.split()[0]
                model_wall = ModelWall(path)
                model_walls_return[model_wall.get_id()] = model_wall
        return model_walls_return

    def __read_model_fire(self):
        model_fires_return = {}
        file_descriptor = open("modelsDescriptor/fireDesc.txt", 'r')
        lines = file_descriptor.readlines()
        file_descriptor.close()
        columns = int(lines.pop(0).split()[1])
        lines.pop(0)
        for line in lines:
            if len(line.split()) == columns:
                path = line.split()[0]
                model_fire = ModelFire(path)
                model_fires_return[model_fire.get_id()] = model_fire
        return model_fires_return

    def __create_random_gift(self):
        id_model_gift = randint(0, len(self.__model_gift))
        return id_model_gift

    def __create_random_walls(self):
        random_walls_return = {}
        reserved_spaces = [[1, 1], [1, 2], [2, 1],
                           [1, 6], [1, 7], [2, 7],
                           [12, 1], [13, 1], [13, 2],
                           [13, 6], [13, 7], [12, 7],
                           [7, 4]]
        x = 1
        y = 1
        n = 0
        n_walls = 25
        model_wall = self.__model_wall[2]
        while True:
            x = randint(1, 13)
            y = randint(1, 7)
            if x % 2 == 1 or y % 2 == 1:    # fixes walls
                if [x, y] not in reserved_spaces:
                    n += 1
                    reserved_spaces.append([x, y])
                    wall = Wall(0, [x*Server.wall_factor, y*Server.wall_factor], model_wall.get_id(), [55, 55], 255,
                                self.__create_random_gift())
                    random_walls_return[wall.get_id()] = wall
            if n == n_walls:
                break
        return random_walls_return

    def __put_static_walls(self):
        model_static_wall = self.__model_wall[1]
        for x in list(range(2, 13, 2)):
            for y in list(range(2, 7, 2)):
                wall = Wall(0, [x*Server.wall_factor, y*Server.wall_factor], model_static_wall.get_id(), [55, 55], 255, 0)
                self.__static_walls.append(wall)

    def __process_fire_collision(self, fire):
        id_chars_kill = []
        for char in self.__chars.values():
            if fire.check_collision(char):
                id_chars_kill.append(char.get_id())

        for id_char in id_chars_kill:
            self.exit(id_char)

        walls_kill = []
        for wall in self.__walls.values():
            if fire.check_collision(wall):
                walls_kill.append(wall)

        for wall in walls_kill:
            if wall.get_id_gift():
                model_gift = self.__model_gift[wall.get_id_gift()]
                gift = Gift(wall.get_orientation(), wall.get_position(), model_gift.get_id(), [54, 54], 155,
                            model_gift.get_s_more_speed(), model_gift.get_s_more_n_bombs(),
                            model_gift.get_s_more_power())
                self.__gifts[gift.get_id()] = gift
            del self.__walls[wall.get_id()]


    def __detect_char_wall_collision(self, char, direction):
        #detecting in static walls
        for wall in self.__static_walls:
            if char.check_collision_walk(wall, direction):
                return True

        # detecting in dinamics walls
        for wall in self.__walls.values():
            if char.check_collision_walk(wall, direction):
                return True

        # detecting collision with bombs:
        for bomb in self.__bombs.values():
            if char.get_id() == bomb.get_id_char():
                return False
            if char.check_collision_walk(bomb, direction):
                return True
        return False

    def __check_bombs(self):
        id_bombs_exploded = list()
        for bomb in self.__bombs.values():
            if bomb.exploded():
                self.__generate_fire(bomb)
                id_bombs_exploded.append(bomb.get_id())

        for id_bomb in id_bombs_exploded:
            bomb = self.__bombs[id_bomb]
            if bomb.get_id_char() in self.__chars:
                char = self.__chars[bomb.get_id_char()]
                char.bomb_exploded()
            del self.__bombs[id_bomb]

    def __check_fires(self):
        id_fires_to_remove = list()
        for fire in self.__fires.values():
            if fire.is_ended():
                id_fires_to_remove.append(fire.get_id())

        for id_fire in id_fires_to_remove:
            del self.__fires[id_fire]

    def __generate_fire(self, bomb):
        model_fire_base = self.__model_fire[1]
        model_fire_middle = self.__model_fire[2]
        model_fire_end = self.__model_fire[3]
        x, y = bomb.get_position()
        center = False
        if x % 2 and y % 2:
            center = True
            fire = Fire(bomb.get_orientation(), [x, y], model_fire_base.get_id(),
                        [54, 54], 100, 30)
            self.__fires[fire.get_id()] = fire

        start = 0
        if center:
            start = 1
        for n in range(start, bomb.get_power()+1, 1):
            if n == bomb.get_power():
                model = model_fire_end
            else:
                model = model_fire_middle
            if x % 2:
                fire = Fire(270, [x, y  + Server.wall_factor * n], model.get_id(),
                            [54, 54], 100, 30)
                self.__fires[fire.get_id()] = fire
                fire = Fire(90, [x , y  - Server.wall_factor * n], model.get_id(),
                            [54, 54], 100, 30)
                self.__fires[fire.get_id()] = fire
            if y % 2:
                fire = Fire(0, [x  + Server.wall_factor * n, y ], model.get_id(),
                            [54, 54], 100, 30)
                self.__fires[fire.get_id()] = fire
                fire = Fire(180, [x  - Server.wall_factor * n, y ], model.get_id(),
                            [54, 54], 100, 30)
                self.__fires[fire.get_id()] = fire

    # PUBLIC METHODS
    def get_model_chars(self):
        list_model_chars_return = list()
        for model_char in self.__model_char.values():
            list_model_chars_return.append([model_char.get_id(), model_char.get_path()])
        return list_model_chars_return

    def get_model_bombs(self):
        list_model_return = list()
        for model_bomb in self.__model_bomb.values():
            list_model_return.append([model_bomb.get_id(), model_bomb.get_path()])
        return list_model_return

    def get_model_gifts(self):
        list_model_return = list()
        for model_gift in self.__model_gift.values():
            list_model_return.append([model_gift.get_id(), model_gift.get_path()])
        return list_model_return

    def get_model_walls(self):
        list_model_return = list()
        for model_wall in self.__model_wall.values():
            list_model_return.append([model_wall.get_id(), model_wall.get_path()])
        return list_model_return

    def get_model_fires(self):
        list_model_return = list()
        for model_fire in self.__model_fire.values():
            list_model_return.append([model_fire.get_id(), model_fire.get_path()])
        return list_model_return

    def get_n_players(self):
        return self.__n_players

    def start_char(self, id_model_char, nick):
        initial_orientation = sample([0, 90, 180, 270], 1)[0]
        if self.__n_players == 0:
            initial_x, initial_y = [1, 1]
        elif self.__n_players == 1:
            initial_x, initial_y = [13, 1]
        elif self.__n_players == 2:
            initial_x, initial_y = [1, 7]
        elif self.__n_players == 3:
            initial_x, initial_y = [13, 7]
        else:
            initial_x, initial_y = [7, 4]
        model_char = self.__model_char[id_model_char]
        char = Char(initial_orientation,
                    [initial_x*Server.wall_factor, initial_y*Server.wall_factor],
                    model_char.get_id(), [54, 54], 255,
                    nick, model_char.get_s_id_bomb_model(),
                    model_char.get_s_speed(),
                    n_bomb_max=model_char.get_s_n_bomb_max(),
                    power_bomb_add=model_char.get_s_power_bomb_add())
        self.__chars[char.get_id()] = char
        self.__n_players += 1
        return char.get_id()

    def put_bomb(self, id_char):
        if id_char in self.__chars:
            char = self.__chars[id_char]
            if char.put_bomb():
                x, y = char.get_position()
                x = round(x / Server.wall_factor) * Server.wall_factor
                y = round(y / Server.wall_factor) * Server.wall_factor
                model_bomb = self.__model_bomb[char.get_id_bomb_model()]
                bomb = Bomb(char.get_orientation(), [x, y], model_bomb.get_id(), [53, 53], 255,
                            id_char, model_bomb.get_s_power() + char.get_power_bomb_add(),
                            model_bomb.get_s_timer())
                self.__bombs[bomb.get_id()] = bomb

    def move(self, id_char, direction):
        if id_char in self.__chars:
            char = self.__chars[id_char]
            if not self.__detect_char_wall_collision(char, direction):
                char.move(direction)

    def list_bombs(self):
        list_return = list()
        for bomb in self.__bombs.values():
            list_return.append([bomb.get_id_model(), bomb.get_position(), bomb.get_scale(), bomb.get_alpha()])
        return list_return

    def list_chars(self):
        list_return = list()
        for char in self.__chars.values():
            list_return.append([char.get_id_model(), char.get_orientation(),
                                char.get_position(), char.get_scale(),
                                char.get_alpha(), char.get_nick()])
        return list_return

    def list_walls(self):
        list_return = list()
        for wall in self.__walls.values():
            list_return.append([wall.get_id_model(), wall.get_position(), wall.get_scale(), wall.get_alpha()])

        for wall in self.__static_walls:
            list_return.append([wall.get_id_model(), wall.get_position(), wall.get_scale(), wall.get_alpha()])

        return list_return

    def list_gifts(self):
        list_return = list()
        for gift in self.__gifts.values():
            list_return.append([gift.get_id_model(), gift.get_position(), gift.get_scale(), gift.get_alpha()])
        return list_return

    def list_fires(self):
        list_return = list()
        for fire in self.__fires.values():
            list_return.append([fire.get_id_model(), fire.get_orientation(), fire.get_position(), fire.get_scale(),
                                fire.get_alpha()])
        return list_return

    def clock(self):
        for bomb in self.__bombs.values():
            bomb.bomb_clock()
        self.__check_bombs()

        for fire in self.__fires.values():
            self.__process_fire_collision(fire)
            fire.clock()
        self.__check_fires()

        for char in self.__chars.values():
            id_gift_remove = []
            for gift in self.__gifts.values():
                if gift.check_collision(char):
                    char.set_speed(char.get_speed() + gift.get_more_speed())
                    char.set_n_bomb_max(char.get_n_bomb_max() + gift.get_more_n_bombs())
                    char.set_power_bomb_add(char.get_power_bomb_add() + gift.get_more_power())
                    id_gift_remove.append(gift.get_id())

            for id_gift in id_gift_remove:
                del self.__gifts[id_gift]


    def exit(self, id_char):
        if id_char in self.__chars:
            self.__n_players -= 1
            del self.__chars[id_char]


def main():
    ipaddr = "192.168.102.134"
    port = 7777
    Pyro4.config.HOST = ipaddr
    Pyro4.config.NS_PORT = 7777
    clock = pygame.time.Clock()
    server = Server()
    daemon = Pyro4.Daemon()
    uri = daemon.register(server)
    ns = Pyro4.locateNS(host=ipaddr, port=port)
    ns.register("server.bombergame.sala1", uri)
    t = threading.Thread(target=daemon.requestLoop)
    t.start()
    while True:
       # if server.get_n_players():
        server.clock()

        clock.tick(30)  # 35 FPS


if __name__=="__main__":
    main()
