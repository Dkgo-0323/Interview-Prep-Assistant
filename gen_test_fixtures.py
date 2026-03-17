import os
from pathlib import Path
from fpdf import FPDF
from PIL import Image
from pypdf import PdfReader, PdfWriter

def ensure_dir():
    fixture_path = Path(__file__).parent / "tests" / "fixtures"
    fixture_path.mkdir(parents=True, exist_ok=True)
    return fixture_path

def gen_normal_pdf(path):
    """生成普通的文本 PDF"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a sample resume text for testing.", ln=True)
    pdf.multi_cell(0, 10, txt="Experience:\n- Python Developer at Tech Corp\n- Data Scientist at AI Lab")
    pdf.output(str(path / "sample_resume.pdf"))
    print(f"Created: sample_resume.pdf")

def gen_encrypted_pdf(path):
    """生成加密的 PDF"""
    # 先创建一个普通 PDF
    temp_pdf = path / "temp_enc.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Secret content", ln=True)
    pdf.output(str(temp_pdf))

    # 使用 pypdf 加密
    reader = PdfReader(temp_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    
    writer.encrypt("password123")
    with open(path / "encrypted.pdf", "wb") as f:
        writer.write(f)
    
    temp_pdf.unlink() # 删除临时文件
    print(f"Created: encrypted.pdf (password: password123)")

def gen_scanned_pdf(path):
    """生成扫描件 PDF (纯图片，无文本或文本极少)"""
    # 1. 创建一张图片
    img_path = path / "test_image.png"
    img = Image.new('RGB', (800, 600), color = (255, 255, 255))
    img.save(img_path)

    # 2. 将图片放入 PDF
    pdf = FPDF()
    pdf.add_page()
    # 放入图片占满页面，且不添加任何文字
    pdf.image(str(img_path), x=0, y=0, w=210) 
    # 按照代码逻辑：len(page_text) < 50 且有图片会被判定为扫描件
    pdf.output(str(path / "scanned.pdf"))
    
    img_path.unlink()
    print(f"Created: scanned.pdf")

def gen_long_pdf(path):
    """生成超过 MAX_PAGES (20页) 的 PDF"""
    pdf = FPDF()
    for i in range(25): # 生成 25 页
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"This is page {i+1}", ln=True)
    pdf.output(str(path / "long_file.pdf"))
    print(f"Created: long_file.pdf")

if __name__ == "__main__":
    base_path = ensure_dir()
    gen_normal_pdf(base_path)
    gen_encrypted_pdf(base_path)
    gen_scanned_pdf(base_path)
    gen_long_pdf(base_path)
    print("\n所有测试固件已准备就绪！")