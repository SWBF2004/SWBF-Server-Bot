from time import time
from discord import Client, Intents
from discord.ext import tasks
from util.process import Process
from swbf.maps import Map
from server_bot.events import *


class Server:
    def __init__(self):
        self.players = 0


class EventNames:
    PLAYER_JOINING = 'player_joining'
    PLAYER_JOINED = 'player_joined'
    PLAYER_NAMES = 'player_names'
    MAP_CHANGED = 'map_changed'


class ServerBot(Client):
    def __init__(self, pid: int, config: dict):
        super().__init__(intents=Intents.default())

        self.__server = Server()
        self.__process = Process(pid)
        self.__config = config
        self.__offsets = config['OFFSETS']
        self.__player_joining = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINING])
        self.__player_joined = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINED])
        self.__player_names = StringProperty(ChangeEvent(), **self.__offsets[EventNames.PLAYER_NAMES])
        self.__map_changed = StringProperty(ChangeEvent(), **self.__offsets[EventNames.MAP_CHANGED])

        self.__timeout = 0

        @self.event
        async def on_ready():
            self.scan.start()

        @self.event
        async def on_player_joining(old: int, new: int):
            channel = self.get_channel(self.__config['channel'])
            await channel.send(f'New Player is joining!')

        @self.event
        async def on_player_joined(old: int, new: int):
            channel = self.get_channel(self.__config['channel'])
            self.__server.players = new
            names = '\n'.join(self.get_player_names())
            await channel.send(f'New Player joined! Player count: {new}')
            await channel.send(f'Players: >>> {names}')

        @self.event
        async def on_map_changed(old: str, new: str):
            channel = self.get_channel(self.__config['channel'])
            if not old:
                await channel.send(f'Server is up! Current map: `{Map.from_id_name(new)}`')
            else:
                await channel.send(f'Map is over. Next map is: `{Map.from_id_name(new)}`')

    @tasks.loop(seconds=3)
    async def scan(self):
        # if self.__player_joining.read(self.__process):
        #     self.dispatch(EventNames.PLAYER_JOINING, *self.__player_joining.get())

        if self.__map_changed.read(self.__process):
            self.__timeout = time()
            self.dispatch(EventNames.MAP_CHANGED, *self.__map_changed.get())

        if time() - self.__timeout > 10:
            if self.__player_joined.read(self.__process):
                self.__timeout = 0
                self.dispatch(EventNames.PLAYER_JOINED, *self.__player_joined.get())

    def get_player_names(self):
        addr = int(self.__offsets[EventNames.PLAYER_NAMES]["address"], 16)
        length = max(1, self.__server.players) * 456
        players = self.__process.read(addr, length)

        if players[0] == 0x00:
            return

        names = []
        for idx in range(self.__server.players):
            name = players[idx * 456:idx * 456 + 32].decode(encoding='utf-8').rstrip('\x00')
            if name[0] != 0x00:
                names.append(name)

        return names
