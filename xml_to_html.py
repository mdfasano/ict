import argparse
import xml.etree.ElementTree as ET
import html

# ===== Command-line setup =====
parser = argparse.ArgumentParser(description="Convert XML to interactive HTML report")
parser.add_argument("-i", "--input", required=True, help="Input XML file path")
parser.add_argument("-o", "--output", default="output.html", help="Output HTML file path")
args = parser.parse_args()

# ===== Load XML =====
tree = ET.parse(args.input)
root = tree.getroot()

# ===== Build HTML content =====
html_parts = []

html_parts.append("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Test Report</title>
<link rel="stylesheet" href="report.css">
<style>
    /* Navigation controls */
    .page { display: none; }
    .page.active { display: block; }

    .nav-buttons {
        text-align: center;
        margin: 20px 0;
    }

    .nav-buttons button {
        background-color: #007BFF;
        color: white;
        border: none;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 1em;
        cursor: pointer;
        margin: 0 5px;
        transition: background 0.2s ease;
    }

    .nav-buttons button:hover {
        background-color: #0056b3;
    }

    .nav-buttons button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
</style>
</head>
<body>

<div class="nav-buttons">
    <button id="prevBtn">Previous Page</button>
    <button id="nextBtn">Next Page</button>
</div>

<div id="report-container">
""")

# ===== Generate page content =====
for page in root.findall("page"):
    html_parts.append('<div class="page">')

    # Metadata header bar
    date = html.escape(page.findtext("date") or "")
    tech = html.escape(page.findtext("technician") or "")
    board = html.escape(page.findtext("board_s_n") or "")
    html_parts.append('<div class="header-bar"><div class="metadata">')
    html_parts.append(f'<div>Date: {date}</div>')
    html_parts.append(f'<div>Technician: {tech}</div>')
    html_parts.append(f'<div>Board S/N: {board}</div>')
    html_parts.append('</div></div>')

    # Page title
    title = html.escape(page.findtext("title") or "")
    html_parts.append(f'<div class="title">{title}</div>')

    # Test Summary
    ts_elem = page.find("test_summary")
    if ts_elem is not None:
        header = html.escape(ts_elem.findtext("header") or "")
        tests = [html.escape(t.text or "") for t in ts_elem.findall("test")]
        html_parts.append('<div class="section test-summary">')
        html_parts.append(f'<div class="header">{header}</div>')
        for t in tests:
            html_parts.append(f'<div class="test">{t}</div>')
        html_parts.append('</div>')

    # Report
    report_elem = page.find("report")
    if report_elem is not None:
        lines = [html.escape(l.text or "") for l in report_elem.findall("line")]
        html_parts.append('<div class="section report">')
        html_parts.append('<div class="header">Report</div>')
        for l in lines:
            html_parts.append(f'<div class="line">{l}</div>')
        html_parts.append('</div>')

    # Generic lines
    generic_lines = [html.escape(l.findtext("value") or l.text or "") for l in page.findall("line")]
    for gl in generic_lines:
        if gl.strip():
            html_parts.append(f'<div class="generic-line">{gl}</div>')

    html_parts.append('</div>')  # close page

# ===== Add JavaScript for navigation =====
html_parts.append("""
</div> <!-- end report-container -->

<script>
let currentPage = 0;
const pages = document.querySelectorAll(".page");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

function showPage(index) {
    pages.forEach((page, i) => {
        page.classList.toggle("active", i === index);
    });
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === pages.length - 1;
}

prevBtn.addEventListener("click", () => {
    if (currentPage > 0) {
        currentPage--;
        showPage(currentPage);
    }
});

nextBtn.addEventListener("click", () => {
    if (currentPage < pages.length - 1) {
        currentPage++;
        showPage(currentPage);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft" && currentPage > 0) {
        currentPage--;
        showPage(currentPage);
    } else if (event.key === "ArrowRight" && currentPage < pages.length - 1) {
        currentPage++;
        showPage(currentPage);
    }
});

showPage(currentPage);
</script>

</body>
</html>
""")

# ===== Write to output =====
with open(args.output, "w", encoding="utf-8") as f:
    f.write("\n".join(html_parts))

print(f"✅ Interactive HTML report generated: {args.output}")
