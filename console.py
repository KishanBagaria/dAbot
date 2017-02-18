from ctypes import *

STD_OUT = -11
console_handle = windll.kernel32.GetStdHandle(STD_OUT)

LF_FACESIZE = 32
class CONSOLE_FONT_INFOEX(Structure):
    _fields_ = [('cbSize'    , c_ulong),
                ('nFont'     , c_ulong),
                ('dwFontSize', wintypes._COORD),
                ('FontFamily', c_uint),
                ('FontWeight', c_uint),
                ('FaceName'  , c_wchar * LF_FACESIZE)]
    
    def __str__(self):
        return 'Font {0.nFont}, {0.dwFontSize.X}, {0.dwFontSize.Y}, {0.FontFamily}, {0.FontWeight}, "{0.FaceName}")'.format(self)
SIZEOF_CONSOLE_FONT_INFOEX = sizeof(CONSOLE_FONT_INFOEX)

def Font(number, width, height, family, weight, name):
    s = CONSOLE_FONT_INFOEX()
    s.cbSize = SIZEOF_CONSOLE_FONT_INFOEX
    s.nFont = number
    s.dwFontSize.X = width
    s.dwFontSize.Y = height
    s.FontFamily = family
    s.FontWeight = weight
    s.FaceName = name
    return s

CONSOLAS = Font(number=9, width=7, height=14, family=0, weight=400, name='Consolas')

class Console(object):
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, value):
        windll.kernel32.SetConsoleTitleA(value)
        self._title = value

    @property
    def font(self):
        s = CONSOLE_FONT_INFOEX()
        s.cbSize = SIZEOF_CONSOLE_FONT_INFOEX
        if windll.kernel32.GetCurrentConsoleFontEx(console_handle, False, pointer(s)) == 0:
            raise Exception('GetCurrentConsoleFontEx failed')
        return s
    @font.setter
    def font(self, value):
        if windll.kernel32.SetCurrentConsoleFontEx(console_handle, False, pointer(value)) == 0:
            raise Exception('SetCurrentConsoleFontEx failed')

    @staticmethod
    def get_largest_window_size():
        windll.kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
        return windll.kernel32.GetLargestConsoleWindowSize(console_handle)

    @staticmethod
    def set_window_info(width, height, left=0, top=0):
        rect = wintypes.SMALL_RECT(left, top, width + left - 1, height + top - 1)
        ret = windll.kernel32.SetConsoleWindowInfo(console_handle, True, byref(rect))
        if ret == 0:
            raise Exception('set_window_info(width={}, height={}, left={}, top={}) failed'.format(width, height, left, top))

    @staticmethod
    def set_buffer_size(width, height):
        coord = wintypes._COORD(width, height)
        ret = windll.kernel32.SetConsoleScreenBufferSize(console_handle, coord) != 0
        if ret == 0:
            raise Exception('set_buffer_size(width={}, height={}) failed'.format(width, height))

console = Console()