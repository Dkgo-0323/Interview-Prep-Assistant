# core/analyzers/exceptions.py

class AnalyzerError(Exception):
    """分析器层的基础异常"""
    pass

class JDAnalysisError(AnalyzerError):
    """JD分析失败时抛出的异常"""
    pass

class ResumeAnalysisError(AnalyzerError):
    """简历分析失败时抛出的异常"""
    pass

class GapAnalysisError(AnalyzerError):
    """Gap分析失败时抛出的异常"""
    pass