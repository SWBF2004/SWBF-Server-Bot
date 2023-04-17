import ctypes
from ctypes import wintypes
import win32process


class ProcessReadError(BaseException):
    def __int__(self):
        super().__init__('Read Error')

class ProcessPermission:
    ERROR_PARTIAL_COPY = 0x00000012B
    PROCESS_VM_READ = 0x00000010
    PROCESS_ALL_ACCESS = 0x0001F0FFF


class Process:
    SIZE_T = ctypes.c_size_t
    PSIZE_T = ctypes.POINTER(SIZE_T)

    def __init__(self, pid: int):
        self.__pid = pid

        self.__kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        def _check_zero(result, func, args):
            if not result:
                raise ctypes.WinError(ctypes.get_last_error())
            return args

        self.__kernel32.OpenProcess.errcheck = _check_zero
        self.__kernel32.OpenProcess.restype = wintypes.HANDLE
        self.__kernel32.OpenProcess.argtypes = (
            wintypes.DWORD,  # _In_ dwDesiredAccess
            wintypes.BOOL,  # _In_ bInheritHandle
            wintypes.DWORD)  # _In_ dwProcessId

        self.__kernel32.ReadProcessMemory.errcheck = _check_zero
        self.__kernel32.ReadProcessMemory.argtypes = (
            wintypes.HANDLE,  # _In_  hProcess
            wintypes.LPCVOID,  # _In_  lpBaseAddress
            wintypes.LPVOID,  # _Out_ lpBuffer
            Process.SIZE_T,  # _In_  nSize
            Process.PSIZE_T)  # _Out_ lpNumberOfBytesRead

        self.__kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

        self._open()

    def _open(self):
        self.__process = self.__kernel32.OpenProcess(ProcessPermission.PROCESS_ALL_ACCESS, False, self.__pid)
        modules = win32process.EnumProcessModules(self.__process)
        self.__base_addr = modules[0]

    def _close(self):
        self.__kernel32.CloseHandle(self.__process)

    def read(self, address: int, size: int):
        buf = (ctypes.c_char * size)()
        read = Process.SIZE_T()

        try:
            self.__kernel32.ReadProcessMemory(self.__process, self.__base_addr + address, buf, size, ctypes.byref(read))
        except WindowsError as e:
            if e.winerror != ProcessPermission.ERROR_PARTIAL_COPY:
                self._close()
                raise

        return buf[:read.value]
