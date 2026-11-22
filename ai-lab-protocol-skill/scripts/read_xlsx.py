"""Extract original cells alongside formulas and stored results without editing."""
import argparse
import json
import openpyxl

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--sheet')
    parser.add_argument('--range', dest='cell_range')
    args = parser.parse_args()
    formulas = openpyxl.load_workbook(args.input, data_only=False, read_only=True)
    values = openpyxl.load_workbook(args.input, data_only=True, read_only=True)
    try:
        for sheet in formulas:
            if args.sheet and args.sheet != sheet.title:
                continue
            rows = sheet[args.cell_range] if args.cell_range else sheet.iter_rows()
            for row in rows:
                for cell in row:
                    if cell.value is not None:
                        record = {'sheet': sheet.title, 'cell': cell.coordinate,
                                  'input': cell.value, 'stored_result': values[sheet.title][cell.coordinate].value,
                                  'is_formula': cell.data_type == 'f', 'number_format': cell.number_format}
                        print(json.dumps(record, ensure_ascii=False, default=str))
    finally:
        formulas.close()
        values.close()

if __name__ == '__main__':
    main()
