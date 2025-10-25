#!/usr/bin/env python3
"""
txt2xml_pages_tags_dynamic.py
Convert plaintext to XML grouped by Page sections.

Rules:
- The first line of the file is used to determine the page prefix.
- Any line starting with that prefix up to the word 'Page' signals a new <page>.
- Lines beginning with certain keywords become special tags.
- Lines starting with ---- or ****** are ignored.
- Lines starting with "test summary" create a <test_summary> tag;
    first line becomes <header>, remaining lines become <test>.
- Lines starting with "failed" create a <report> tag;
    all following lines until next page are included as <line>.
"""

import argparse
import sys
import re
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ======== CONFIGURATION =========
SPECIAL_TAGS = {
    r"^board\s*s/n:?\s*(.*)$": "board_s_n",
    r"^date/time:?\s*(.*)$": "date",
    r"^technician:?\s*(.*)$": "technician",
}
# =================================


def parse_args():
    p = argparse.ArgumentParser(description="Convert plaintext to XML, grouped by Page sections.")
    p.add_argument("-i", "--input", required=True, help="Input file path or '-' for stdin")
    p.add_argument("-o", "--output", help="Output XML file path. If omitted, prints to stdout.")
    p.add_argument("-r", "--root", default="document", help="Root element name (default: document)")
    p.add_argument("-e", "--element", default="line", help="Element name for generic lines (default: line)")
    p.add_argument("-s", "--split-char", default=None,
                   help="Split each line on first occurrence of this char into <key>/<value>")
    p.add_argument("--preserve-empty", action="store_true", help="Preserve empty lines as elements")
    return p.parse_args()


def pretty_xml_str(elem: ET.Element) -> str:
    rough = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


def make_line_element(parent, tag, line, split_char=None, preserve_empty=False):
    if line.strip() == "" and not preserve_empty:
        return None
    rec = ET.SubElement(parent, tag)
    if split_char and split_char in line:
        key, value = line.split(split_char, 1)
        ET.SubElement(rec, "key").text = key.strip()
        ET.SubElement(rec, "value").text = value.strip()
    else:
        rec.text = line
    return rec


def main():
    args = parse_args()

    # Read input
    if args.input == "-":
        raw = sys.stdin.read()
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = f.read()

    lines = raw.splitlines()

    # Remove leading empty/whitespace lines
    while lines and not lines[0].strip():
        lines.pop(0)

    if not lines:
        print("Empty input file.")
        return

    first_line = lines[0].strip()
    print(first_line)
    page_match = re.match(r"^(.*Page)\b", first_line, re.IGNORECASE)
    if page_match:
        page_prefix = page_match.group(1)
    else:
        # fallback: entire first line
        page_prefix = first_line

    root = ET.Element(args.root)
    compiled_specials = [(re.compile(pat, re.IGNORECASE), tag) for pat, tag in SPECIAL_TAGS.items()]

    current_page = None
    collecting_test_summary = False
    test_summary_elem = None
    first_line_in_summary = True
    collecting_report = False
    report_elem = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Ignore lines starting with ---- or ******
        if stripped.startswith("----") or stripped.startswith("******"):
            continue

        # Page header (dynamic, based on prefix)
        if stripped.startswith(page_prefix):
            current_page = ET.SubElement(root, "page")
            title = ET.SubElement(current_page, "title")
            title.text = stripped
            collecting_test_summary = False
            first_line_in_summary = True
            collecting_report = False
            continue

        # If file starts without a page (shouldn't happen), create one automatically
        if current_page is None:
            current_page = ET.SubElement(root, "page")
            title = ET.SubElement(current_page, "title")
            title.text = stripped

        # Start collecting test summary
        if stripped.lower().startswith("test summary"):
            test_summary_elem = ET.SubElement(current_page, "test_summary")
            content = stripped[len("test summary"):].lstrip(": ").strip()
            if content:
                ET.SubElement(test_summary_elem, "header").text = content
                first_line_in_summary = False
            else:
                first_line_in_summary = True
            collecting_test_summary = True
            collecting_report = False
            continue

        # Collect test summary lines
        if collecting_test_summary:
            tagname = "header" if first_line_in_summary else "test"
            ET.SubElement(test_summary_elem, tagname).text = stripped
            first_line_in_summary = False
            continue

        # Start collecting report
        if stripped.lower().startswith("failed"):
            report_elem = ET.SubElement(current_page, "report")
            ET.SubElement(report_elem, "line").text = stripped
            collecting_report = True
            collecting_test_summary = False
            continue

        # Collect report lines
        if collecting_report:
            ET.SubElement(report_elem, "line").text = stripped
            continue

        # Check for special tags
        matched_special = False
        for pattern, tagname in compiled_specials:
            m = pattern.match(stripped)
            if m:
                elem = ET.SubElement(current_page, tagname)
                elem.text = m.group(1).strip()
                matched_special = True
                break

        if matched_special:
            continue

        # Otherwise, normal handling
        make_line_element(current_page, args.element, stripped,
                          args.split_char, args.preserve_empty)

    xml_out = pretty_xml_str(root)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml_out)
        print(f"Wrote XML to {args.output}")
    else:
        print(xml_out)


if __name__ == "__main__":
    main()
