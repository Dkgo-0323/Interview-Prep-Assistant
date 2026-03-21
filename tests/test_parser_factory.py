"""
parser_factory 单元测试。
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.parsers import parse_file, FileParseError, UnsupportedFileError


class TestParseFileRouting:
    """测试文件路由功能。"""
    
    def test_routes_to_txt_parser(self, tmp_path: Path):
        """TXT 文件路由到 txt_parser。"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello World", encoding="utf-8")
        
        result = parse_file(txt_file)
        
        assert "Hello World" in result
    
    def test_routes_to_pdf_parser(self, tmp_path: Path):
        """PDF 文件路由到 pdf_parser。"""
        with patch("core.parsers.parser_factory.parse_pdf") as mock_parse:
            mock_parse.return_value = "PDF content"
            
            result = parse_file(tmp_path / "test.pdf")
            
            mock_parse.assert_called_once()
            assert result == "PDF content"
    
    def test_routes_to_docx_parser(self, tmp_path: Path):
        """DOCX 文件路由到 docx_parser。"""
        with patch("core.parsers.parser_factory.parse_docx") as mock_parse:
            mock_parse.return_value = "DOCX content"
            
            result = parse_file(tmp_path / "test.docx")
            
            mock_parse.assert_called_once()
            assert result == "DOCX content"


class TestCaseInsensitiveExtension:
    """测试后缀大小写兼容。"""
    
    def test_uppercase_pdf(self, tmp_path: Path):
        """.PDF 大写后缀正常识别。"""
        with patch("core.parsers.parser_factory.parse_pdf") as mock_parse:
            mock_parse.return_value = "content"
            
            parse_file(tmp_path / "resume.PDF")
            
            mock_parse.assert_called_once()
    
    def test_uppercase_docx(self, tmp_path: Path):
        """.DOCX 大写后缀正常识别。"""
        with patch("core.parsers.parser_factory.parse_docx") as mock_parse:
            mock_parse.return_value = "content"
            
            parse_file(tmp_path / "resume.DOCX")
            
            mock_parse.assert_called_once()
    
    def test_mixed_case_txt(self, tmp_path: Path):
        """.TxT 混合大小写正常识别。"""
        txt_file = tmp_path / "test.TxT"
        txt_file.write_text("content", encoding="utf-8")
        
        result = parse_file(txt_file)
        
        assert result == "content"


class TestUnsupportedExtension:
    """测试不支持的格式。"""
    
    def test_xlsx_raises_error(self, tmp_path: Path):
        """.xlsx 抛出 UnsupportedFileError。"""
        with pytest.raises(UnsupportedFileError) as exc_info:
            parse_file(tmp_path / "data.xlsx")
        
        assert ".xlsx" in str(exc_info.value)
        assert ".pdf" in str(exc_info.value)  # 提示支持的格式
    
    def test_jpg_raises_error(self, tmp_path: Path):
        """.jpg 抛出 UnsupportedFileError。"""
        with pytest.raises(UnsupportedFileError) as exc_info:
            parse_file(tmp_path / "image.jpg")
        
        assert ".jpg" in str(exc_info.value)
    
    def test_no_extension_raises_error(self, tmp_path: Path):
        """无后缀文件抛出 UnsupportedFileError。"""
        with pytest.raises(UnsupportedFileError) as exc_info:
            parse_file(tmp_path / "README")
        
        assert "不支持" in str(exc_info.value)


class TestErrorPropagation:
    """测试异常传递。"""
    
    def test_file_not_found_propagates(self, tmp_path: Path):
        """文件不存在时，FileParseError 从解析器传递。"""
        non_existent = tmp_path / "ghost.txt"
        
        with pytest.raises(FileParseError) as exc_info:
            parse_file(non_existent)
        
        assert "不存在" in str(exc_info.value) or "ghost.txt" in str(exc_info.value)
    
    def test_parse_error_propagates(self, tmp_path: Path):
        """解析失败时，FileParseError 从解析器传递。"""
        with patch("core.parsers.parser_factory.parse_pdf") as mock_parse:
            mock_parse.side_effect = FileParseError("PDF 损坏")
            
            with pytest.raises(FileParseError) as exc_info:
                parse_file(tmp_path / "bad.pdf")
            
            assert "损坏" in str(exc_info.value)


class TestPathHandling:
    """测试路径处理。"""
    
    def test_accepts_string_path(self, tmp_path: Path):
        """接受字符串路径。"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content", encoding="utf-8")
        
        result = parse_file(str(txt_file))  # 字符串路径
        
        assert result == "content"
    
    def test_accepts_path_object(self, tmp_path: Path):
        """接受 Path 对象。"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content", encoding="utf-8")
        
        result = parse_file(txt_file)  # Path 对象
        
        assert result == "content"