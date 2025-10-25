import argparse
from fpdf import FPDF
import xml.etree.ElementTree as ET

# ====== Parse command line arguments ======
parser = argparse.ArgumentParser(description="Generate PDF from XML")
parser.add_argument(
    "-i", "--input", required=True, help="Input XML file path"
)
parser.add_argument(
    "-o", "--output", default="output.pdf", help="Output PDF file path (default: output.pdf)"
)
args = parser.parse_args()

# ====== Load XML ======
tree = ET.parse(args.input)
root = tree.getroot()

# ====== Create PDF object ======
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=12)

# ====== Helper function to add a page ======
def add_page(title):
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)

# ====== Iterate through pages ======
for page in root.findall("page"):
    title = page.findtext("title", default="Page")
    add_page(title)

    # Special tags
    for tag in ["date", "technician", "board_s_n"]:
        text = page.findtext(tag)
        if text:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(30, 8, f"{tag.replace('_',' ').title()}: ", ln=False)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, text)
            pdf.ln(2)

    # Test summary
    ts_elem = page.find("test_summary")
    if ts_elem is not None:
        header = ts_elem.findtext("header")
        tests = [t.text for t in ts_elem.findall("test")]
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Test Summary:", ln=True)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"- {header}", ln=True)
        pdf.set_font("Arial", size=12)
        for t in tests:
            pdf.cell(0, 8, f"  - {t}", ln=True)
        pdf.ln(3)

    # Report
    report_elem = page.find("report")
    if report_elem is not None:
        lines = [line.text for line in report_elem.findall("line")]
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Report:", ln=True)
        pdf.set_font("Arial", size=12)
        for line in lines:
            pdf.cell(0, 8, f"  - {line}", ln=True)
        pdf.ln(3)

    # Generic lines
    for line_elem in page.findall("line"):
        text = line_elem.findtext("value") or line_elem.text
        if text:
            pdf.multi_cell(0, 8, text)

# ====== Save PDF ======
pdf.output(args.output)
print(f"PDF generated as {args.output}")
