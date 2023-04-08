from logging import getLogger
from discord import Client, Intents
from util.process import Process
from discord.ext import tasks
from swbf.maps import Map


class Server:
    def __init__(self):
        self.players = 0


class ServerEvent:
    def check(self, old, new) -> bool:
        raise NotImplementedError('Please implement me!')


class ChangeEvent(ServerEvent):
    def check(self, old, new) -> bool:
        if old != new:
            return True
        return False


class PostiveChangeEvent(ServerEvent):
    def check(self, old, new) -> bool:
        if old < new:
            return True
        return False


class ServerProperty:
    def __init__(self, event: ServerEvent, address: str, length: str, value):
        self.event = event
        self.address = int(address, 16)
        self.length = int(length)
        self.value = value
        self.old = value

    def read(self, process: Process) -> bool:
        self.old = self.value
        self.value = self.convert(process.read(self.address, self.length))
        has_changed = self.event.check(self.old, self.value)

        return has_changed

    def get(self) -> tuple:
        return self.old, self.value

    def convert(self, new_value: bytes):
        raise NotImplementedError('Please implement me!')


class IntProperty(ServerProperty):
    def __init__(self, event: ServerEvent, address: str, length: str):
        super().__init__(event, address, length, 0)

    def convert(self, new_value: bytes) -> int:
        return int.from_bytes(new_value, byteorder='little')


class BitCountProperty(ServerProperty):
    def __init__(self, event: ServerEvent, address: str, length: str):
        super().__init__(event, address, length, 0)

    def convert(self, new_value: bytes) -> int:
        return bin(int.from_bytes(new_value, byteorder='little')).count('1')


class StringProperty(ServerProperty):
    def __init__(self, event: ServerEvent, address: str, length: str):
        super().__init__(event, address, length, "")

    def convert(self, new_value: bytes) -> str:
        return new_value.decode(encoding='utf-8').rstrip('\x00')


class EventNames:
    PLAYER_JOINING = 'player_joining'
    PLAYER_JOINED = 'player_joined'
    PLAYER_NAMES = 'player_names'
    MAP_CHANGED = 'map_changed'


class ServerBot(Client):
    def __init__(self, pid: int, config: dict):
        super().__init__(intents=Intents.default())

        self.__process = Process(pid)
        self.__config = config
        self.__offsets = config['OFFSETS']
        self.__player_joining = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINING])
        self.__player_joined = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINED])
        self.__player_names = StringProperty(ChangeEvent(), **self.__offsets[EventNames.MAP_CHANGED])
        self.__map_changed = StringProperty(ChangeEvent(), **self.__offsets[EventNames.MAP_CHANGED])

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
            await channel.send(f'New Player joined! Player count: {new}')

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

        if self.__player_joined.read(self.__process):
            self.dispatch(EventNames.PLAYER_JOINED, *self.__player_joined.get())

        if self.__map_changed.read(self.__process):
            self.dispatch(EventNames.MAP_CHANGED, *self.__map_changed.get())
