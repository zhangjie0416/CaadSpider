import openpyxl
import csv


def to_csv(data, file):
    with open(file, "w", newline='', encoding='utf-8-sig') as f:
        csvwriter = csv.writer(f)
        for row in data:
            csvwriter.writerow(row)


def to_excel(data, file):
    wb = openpyxl.Workbook()
    sheet = wb.active
    rows = len(data)
    cols = len(data[0])
    for row in range(0, rows):  # 写入数据
        for col in range(0, cols):
            sheet.cell(row=row + 1, column=col + 1, value=data[row][col])
    wb.save(filename=file)
