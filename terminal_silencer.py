import platform
import signal
import sys

class TerminalSilencer:
    """Cross-platform terminal control character suppressor"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.original_settings = None
        self.original_handler = None
        
    def enable_silent_mode(self):
        """Enable silent mode (hide ^C)"""
        if not self.is_windows:
            # Unix approach
            import termios
            fd = sys.stdin.fileno()
            self.original_settings = termios.tcgetattr(fd)
            silent_settings = termios.tcgetattr(fd)
            silent_settings[3] &= ~termios.ECHOCTL
            termios.tcsetattr(fd, termios.TCSADRAIN, silent_settings)
        
        else:
            # Windows approach - intercept and suppress ^C display
            self.original_handler = signal.signal(signal.SIGINT, self._windows_silent_handler)
            
            # Try console API to also suppress visual echo (optional)
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                self.original_console_mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), 
                    ctypes.byref(self.original_console_mode))
                
                # Disable echo input
                new_mode = self.original_console_mode.value & ~0x0004  # ENABLE_ECHO_INPUT
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), new_mode)
            
            except:
                pass  # Fallback to signal only
    
    def _windows_silent_handler(self, signum, frame):
        """Custom handler that doesn't print ^C"""
        # Do nothing except raise the exception
        raise KeyboardInterrupt()
    
    def restore(self):
        """Restore original terminal settings"""
        if not self.is_windows:
            if self.original_settings:
                import termios
                fd = sys.stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, self.original_settings)
        else:
            # Restore original signal handler
            if self.original_handler:
                signal.signal(signal.SIGINT, self.original_handler)
            
            # Restore console mode if changed
            try:
                if hasattr(self, 'original_console_mode'):
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 
                        self.original_console_mode)
            except:
                pass