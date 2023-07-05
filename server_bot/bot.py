import logging
from time import time
from discord import Client, Intents
from discord.ext import tasks
from util.process import ProcessReadError
from swbf.maps import Map
from server_bot.events import *


class Server:
    def __init__(self):
        self.players = 0


class EventNames:
    PLAYER_JOINING = 'player_joining'
    PLAYER_JOINED = 'player_joined'
    MAP_CHANGED = 'map_changed'
    SERVER_DOWN = 'server_down'


class ServerBot(Client):
    def __init__(self, pid: int, config: dict, quiet_start: bool = False):
        super().__init__(intents=Intents.default())

        self.__quiet_start = quiet_start

        self.__server = Server()
        self.__process = Process(pid)
        self.__config = config

        # Offsets
        self.__offsets = config['OFFSETS']
        self.__names = self.__offsets['names']
        self.__stats = self.__offsets['stats']

        # Events
        self.__player_joining = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINING])
        self.__player_joined = BitCountProperty(PostiveChangeEvent(), **self.__offsets[EventNames.PLAYER_JOINED])
        self.__map_changed = StringProperty(ChangeEvent(), **self.__offsets[EventNames.MAP_CHANGED])

        self.__join_timer = 0
        self.__join_timeout = int(config['join-timeout'])
        self.__tag_timer_3 = 0
        self.__tag_timeout_3 = int(config['tag-timeout-3'])
        self.__tag_timer_5 = 0
        self.__tag_timeout_5 = int(config['tag-timeout-5'])

        @self.event
        async def on_ready():
            self.scan.start()

        @self.event
        async def on_player_joining(old: int, new: int):
            channel_count = self.get_channel(self.__config['channel-count'])
            await channel_count.send(f'New Player is joining!')

        @self.event
        async def on_player_joined(old: int, new: int):
            self.__server.players = new

            if time() - self.__join_timer > self.__join_timeout:
                self.__join_timer = time()

                tag = ''
                if time() - self.__tag_timer_3 > self.__tag_timeout_3:
                    if self.__server.players == 3:
                        self.__tag_timer_3 = time()
                        tag += f' <@&{self.__config["role-players=3"]}> '

                if time() - self.__tag_timer_5 > self.__tag_timeout_5:
                    if self.__server.players == 5:
                        self.__tag_timer_5 = time()
                        tag += f' <@&{self.__config["role-players=5"]}> '

                channel_count = self.get_channel(self.__config['channel-count'])
                await channel_count.send(f'New Player joined! Player count: {new} {tag}')

            player_names = self.format_player_names()
            if player_names:
                channel_names = self.get_channel(self.__config['channel-names'])
                await channel_names.send(f'{player_names}')

        @self.event
        async def on_map_changed(old: str, new: str):
            if not new:
                self.dispatch(EventNames.SERVER_DOWN)

            channel_map = self.get_channel(self.__config['channel-map'])
            if not old and not self.__quiet_start:
                await channel_map.send(f'Server is up! Current map: `{Map.from_id_name(new)}`')
            else:
                # Update timeout after map change
                self.__join_timer = time()

                await channel_map.send(f'Map is over. Next map is: `{Map.from_id_name(new)}`')

                names = self.format_player_names()
                if names:
                    channel_names = self.get_channel(self.__config['channel-names'])
                    await channel_names.send(f'{names}')

        @self.event
        async def on_server_down():
            channel_status = self.get_channel(self.__config['channel-status'])
            await channel_status.send(f'ALAAAAAARM!!! SERVER DOOOOOOOWN!!!')

    @tasks.loop(seconds=3)
    async def scan(self):
        try:

            # if self.__player_joining.read(self.__process):
            #     self.dispatch(EventNames.PLAYER_JOINING, *self.__player_joining.get())

            if self.__map_changed.read(self.__process):
                self.dispatch(EventNames.MAP_CHANGED, *self.__map_changed.get())

            if self.__player_joined.read(self.__process):
                self.dispatch(EventNames.PLAYER_JOINED, *self.__player_joined.get())

        except ProcessReadError as e:
            self.dispatch(EventNames.SERVER_DOWN)

    def format_player_names(self, with_stats=True):
        stats = f''

        if with_stats:
            for name, stat in zip(self.get_player_names(), self.get_player_stats()):
                ping, kill, death, cp = stat.values()
                mod = 1000
                stats += f'{name:32s}  P:{ping % mod:4d}  K:{kill % mod:3d}  D:{death % mod:3d}  C:{cp % mod:3d}\n'

            if stats:
                return f'```{stats}```'
            return ''

        else:
            names = self.get_player_names()
            if names:
                names = "\n".join(names)
                stats = f'>>> {names}'

        return stats

    def get_player_names(self):
        addr = int(self.__names['address'], 16)
        length = int(self.__names['length'])

        size = max(1, self.__server.players) * length
        buffer = self.__process.read(addr, size)

        # Parts of the name (after the first character) remain in memory.
        # However, the first character is set to 0.
        if buffer[0] == 0x00:
            return []

        max_name_len = 32
        names = []
        for idx in range(self.__server.players):
            start = idx * length

            name_start = start
            name_stop = start + max_name_len
            name = buffer[name_start:name_stop].decode(encoding='latin-1').rstrip('\x00')
            if name[0] != 0x00:
                names.append(name)

        return names

    def get_player_stats(self):
        addr = int(self.__stats['address'], 16)
        length = int(self.__stats['length'])
        
        size = max(1, self.__server.players) * length
        buffer = self.__process.read(addr, size)

        l = logging.getLogger()
        l.debug(buffer)

        stats = []
        for idx in range(self.__server.players):
            start = idx * length

            ping_start = start
            ping_stop = ping_start + 4
            ping = int.from_bytes(buffer[ping_start:ping_stop], byteorder='little', signed=True)

            kill_start = ping_stop
            kill_stop = kill_start + 4
            kill = int.from_bytes(buffer[kill_start:kill_stop], byteorder='little', signed=True)

            death_start = kill_stop
            death_stop = death_start + 4
            death = int.from_bytes(buffer[death_start:death_stop], byteorder='little', signed=True)

            cp_start = death_stop
            cp_stop = cp_start + 4
            cp = int.from_bytes(buffer[cp_start:cp_stop], byteorder='little', signed=True)

            stats.append({
                'ping': ping,
                'kill': kill,
                'death': death,
                'cp': cp,
            })

        return stats
