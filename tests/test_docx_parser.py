"""
DOCX 解析器测试
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.parsers.docx_parser import parse_docx, _extract_table_text, MAX_CHARACTERS
from core.parsers.exceptions import FileParseError


class TestParseDocxBasic:
    """基础功能测试"""

    def test_file_not_exists(self, tmp_path):
        """测试文件不存在时抛出 FileParseError"""
        fake_path = tmp_path / "nonexistent.docx"
        
        with pytest.raises(FileParseError) as exc_info:
            parse_docx(fake_path)
        
        assert "文件不存在" in str(exc_info.value)

    def test_path_object_accepted(self, tmp_path):
        """测试接受 Path 对象"""
        fake_path = tmp_path / "test.docx"
        
        with pytest.raises(FileParseError) as exc_info:
            parse_docx(fake_path)
        
        # 只要不是类型错误就行
        assert "文件不存在" in str(exc_info.value)

    def test_string_path_accepted(self, tmp_path):
        """测试接受字符串路径"""
        fake_path = str(tmp_path / "test.docx")
        
        with pytest.raises(FileParseError) as exc_info:
            parse_docx(fake_path)
        
        assert "文件不存在" in str(exc_info.value)


class TestEncryptedDocx:
    """加密文件测试"""

    def test_encrypted_docx_error_message(self, tmp_path):
        """测试加密文件的错误消息"""
        # 创建一个假的非 zip 文件来模拟加密 DOCX
        fake_docx = tmp_path / "encrypted.docx"
        fake_docx.write_bytes(b"not a zip file content")
        
        with pytest.raises(FileParseError) as exc_info:
            parse_docx(fake_docx)
        
        error_msg = str(exc_info.value)
        assert any(keyword in error_msg for keyword in ["加密", "无法打开", "zip file"])


class TestCorruptedDocx:
    """损坏文件测试"""

    def test_corrupted_file(self, tmp_path):
        """测试损坏的文件"""
        corrupted = tmp_path / "corrupted.docx"
        corrupted.write_bytes(b"random corrupted content here")
        
        with pytest.raises(FileParseError):
            parse_docx(corrupted)


class TestConstants:
    """常量测试"""

    def test_max_characters_value(self):
        """验证最大字符数常量"""
        assert MAX_CHARACTERS == 50000


class TestExtractTableText:
    """表格提取辅助函数测试"""

    def test_extract_table_text_with_mock(self):
        """测试表格文本提取逻辑"""
        # 创建 mock 表格结构
        mock_cell1 = MagicMock()
        mock_cell1.paragraphs = [MagicMock(text="姓名")]
        
        mock_cell2 = MagicMock()
        mock_cell2.paragraphs = [MagicMock(text="张三")]
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        result = _extract_table_text(mock_table)
        
        assert "姓名" in result
        assert "张三" in result
        assert "\t" in result  # 制表符分隔

    def test_empty_cells_handling(self):
        """测试空单元格处理"""
        # 创建包含空单元格的 mock
        mock_cell1 = MagicMock()
        mock_cell1.paragraphs = [MagicMock(text="数据")]
        
        mock_cell2 = MagicMock()
        mock_cell2.paragraphs = [MagicMock(text="")]  # 空单元格
        
        mock_cell3 = MagicMock()
        mock_cell3.paragraphs = [MagicMock(text="更多数据")]
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2, mock_cell3]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        result = _extract_table_text(mock_table)
        
        # 不应有连续制表符
        assert "\t\t" not in result
        assert "数据" in result
        assert "更多数据" in result

    def test_empty_row_skipped(self):
        """测试空行被跳过"""
        mock_cell = MagicMock()
        mock_cell.paragraphs = [MagicMock(text="   ")]  # 只有空白
        
        mock_row = MagicMock()
        mock_row.cells = [mock_cell]
        
        mock_table = MagicMock()
        mock_table.rows = [mock_row]
        
        result = _extract_table_text(mock_table)
        
        assert result == ""


class TestDocxParserIntegration:
    """集成测试（需要 fixtures）"""

    @pytest.mark.skip(reason="需要 tests/fixtures/sample_resume.docx")
    def test_parse_valid_docx(self):
        """测试解析正常的 DOCX 文件"""
        result = parse_docx("tests/fixtures/sample_resume.docx")
        
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.skip(reason="需要 tests/fixtures/encrypted.docx")
    def test_parse_encrypted_docx(self):
        """测试解析加密的 DOCX 文件"""
        with pytest.raises(FileParseError) as exc_info:
            parse_docx("tests/fixtures/encrypted.docx")
        
        assert "加密" in str(exc_info.value)


class TestTruncation:
    """截断测试"""

    def test_truncation_warning_logged(self, tmp_path):
        """测试超长文档截断时记录 warning"""
        # 这个测试需要 mock Document 和大量内容
        # 留作集成测试或手动测试
        pass