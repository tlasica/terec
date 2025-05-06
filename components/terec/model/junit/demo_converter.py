"""
Demonstrate the JUnit XML to JSON converter with real pytest report.

Usage: python demo_converter.py <path_to_xml_file>
"""

import json
import sys
from pathlib import Path

from terec.model.junit.converter import JUnitConverter


def main():
    if len(sys.argv) != 2:
        print("Usage: python demo_converter.py <path_to_xml_file>")
        sys.exit(1)

    # Read the XML file
    xml_file = Path(sys.argv[1])
    if not xml_file.exists():
        print(f"Error: File not found: {xml_file}")
        sys.exit(1)

    xml_content = xml_file.read_text()

    # Create and use the converter
    converter = JUnitConverter(xml_content)
    result = converter.convert_to_json()

    # Print the result in pretty JSON format
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
