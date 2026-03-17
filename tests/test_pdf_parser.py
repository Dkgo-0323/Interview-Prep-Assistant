"""
pdf_parser 单元测试
"""

import tempfile
from pathlib import Path

import pytest

from core.parsers.pdf_parser import parse_pdf, MAX_PAGES, SCANNED_PAGE_TEXT_THRESHOLD
from core.parsers.exceptions import FileParseError


class TestParsePdf:
    """parse_pdf 函数测试"""
    
    def test_file_not_exists(self):
        """测试文件不存在"""
        with pytest.raises(FileParseError, match="文件不存在"):
            parse_pdf("/nonexistent/path/to/file.pdf")
    
    def test_file_not_exists_message_contains_path(self):
        """测试错误消息包含路径"""
        fake_path = str(Path("/fake/path/resume.pdf"))
        with pytest.raises(FileParseError) as exc_info:
            parse_pdf(fake_path)
        assert fake_path in str(exc_info.value)
    
    def test_path_object_accepted(self, tmp_path):
        """测试接受 Path 对象"""
        # 创建一个假的 PDF（实际上会因为格式错误而失败，但能验证路径处理）
        fake_pdf = tmp_path / "test.pdf"
        fake_pdf.write_bytes(b"not a real pdf")
        
        with pytest.raises(FileParseError):
            # 会失败，但不是因为路径问题
            parse_pdf(fake_pdf)
    
    def test_string_path_accepted(self, tmp_path):
        """测试接受字符串路径"""
        fake_pdf = tmp_path / "test.pdf"
        fake_pdf.write_bytes(b"not a real pdf")
        
        with pytest.raises(FileParseError):
            parse_pdf(str(fake_pdf))


class TestParsePdfWithRealFiles:
    """
    使用真实 PDF 文件的集成测试
    
    注意：这些测试需要在 tests/fixtures/ 目录下有对应的测试文件
    如果没有测试文件，测试会被跳过
    """
    
    @pytest.fixture
    def fixtures_dir(self):
        """测试文件目录"""
        fixtures = Path(__file__).parent / "fixtures"
        fixtures.mkdir(exist_ok=True)
        return fixtures
    
    def test_parse_valid_pdf(self, fixtures_dir):
        """测试解析有效的 PDF 文件"""
        pdf_path = fixtures_dir / "sample_resume.pdf"
        
        if not pdf_path.exists():
            pytest.skip(f"测试文件不存在: {pdf_path}")
        
        result = parse_pdf(pdf_path)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_parse_encrypted_pdf(self, fixtures_dir):
        """测试解析加密的 PDF"""
        pdf_path = fixtures_dir / "encrypted.pdf"
        
        if not pdf_path.exists():
            pytest.skip(f"测试文件不存在: {pdf_path}")
        
        with pytest.raises(FileParseError, match="加密"):
            parse_pdf(pdf_path)
    
    def test_parse_scanned_pdf(self, fixtures_dir):
        """测试解析扫描件 PDF"""
        pdf_path = fixtures_dir / "scanned.pdf"
        
        if not pdf_path.exists():
            pytest.skip(f"测试文件不存在: {pdf_path}")
        
        with pytest.raises(FileParseError, match="扫描件"):
            parse_pdf(pdf_path)


class TestConstants:
    """测试模块常量配置"""
    
    def test_max_pages_value(self):
        """验证最大页数配置"""
        assert MAX_PAGES == 20
    
    def test_scanned_threshold_value(self):
        """验证扫描页检测阈值"""
        assert SCANNED_PAGE_TEXT_THRESHOLD == 50


class TestEdgeCases:
    """边缘情况测试"""
    
    def test_empty_path_string(self):
        """测试空路径字符串"""
        with pytest.raises(FileParseError):
            parse_pdf("")
    
    def test_directory_path(self, tmp_path):
        """测试传入目录路径而非文件"""
        with pytest.raises(FileParseError):
            parse_pdf(tmp_path)