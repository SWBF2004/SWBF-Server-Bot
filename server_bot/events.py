from util.process import Process


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
        return new_value.decode(encoding='latin-1').rstrip('\x00')
