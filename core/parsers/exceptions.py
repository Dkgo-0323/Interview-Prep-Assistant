# core/parsers/exceptions.py

class FileParseError(Exception):
    """文件解析过程中发生的业务逻辑异常"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class UnsupportedFileError(FileParseError):
    """不支持的文件格式异常"""
    pass