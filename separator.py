import shutil

class _Separator:
    """Singleton separator manager"""
    
    def _get_width(self):
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    @property
    def major(self):
        return "=" * self._get_width()
    
    @property
    def minor(self):
        return "–" * self._get_width()

# Singleton instance
separator = _Separator()