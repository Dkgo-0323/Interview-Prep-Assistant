"""Storage outcomes shared by optional HTTP routes and PostgreSQL adapters."""


class HistoryMissing(Exception):
    """Missing and foreign records deliberately have the same outcome."""


class HistoryFull(Exception):
    pass


class HistoryConflict(Exception):
    pass
