import os
import sys
import time
import pdfplumber
import csv

def extract_and_write_tables(pdf_path, output_path, max_pages=None, batch_size=100):
    total_page_processed = 0
    first_write = not os.path.exists(output_path)
    headers = ["date", "transaction_code", "amount", "transaction_detail"]

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        if max_pages is not None:
            total_pages = min(total_pages, max_pages)
        print(f"File PDF có tổng cộng {total_pages} trang.")


        for i in range(0, total_pages, batch_size):
            batch_tables = []
            end_page = min(i + batch_size, total_pages)

            for page_num in range(i, end_page):
                print(f"Đang xử lý trang {page_num + 1}/{total_pages} ...")
                page = pdf.pages[page_num]
                tables = page.extract_tables()

                for table in tables:
                    # print("#TABLE:", table)
                    for row in table[1:]:
                        dates, transaction_codes, amounts, contents = [], [], [], []

                        for j, cell in enumerate(row):
                            # print("### ROWS :", row)
                            # print(type(row))
                            lines = cell.split("\n")
                            # print("### lines: ", lines)
                            if j == 0:
                                dates.extend(lines[::2])
                                # print("dates:", dates)
                                transaction_codes.extend(lines[1::2])
                                # print("transaction_codes:", transaction_codes)
                            elif j == 2:
                                amounts.extend(lines)
                                # print("amounts:", amounts)
                            elif j == 4:
                                contents.extend(lines)
                                # print("contents:", contents)
                        # print("LEN DATE:", len(dates))
                        # print("LEN CONTENT:", len(contents))
                        # exit(1)

                        for k in range(len(dates)):
                            batch_tables.append([
                                f"'{dates[k]}'",
                                transaction_codes[k],
                                amounts[k].replace('.','') if k < len(amounts) else ' ',
                                contents[k] if k < len(contents) else ' ',
                            ])

            write_to_csv(batch_tables, output_path, headers, first_write)
            first_write = False
            total_page_processed += len(range(i, end_page))
            print(f"Đã xử lý và ghi {total_page_processed}/{total_pages}")

    print(f"Hoàn thành việc trích xuất và ghi dữ liệu từ {total_pages} trang")


def write_to_csv(data, output_path, headers, first_write):
    mode = 'w' if first_write else 'a'
    with open(output_path, mode=mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if first_write:
            writer.writerow(headers)
        writer.writerows(data)


def main():
    if len(sys.argv) not in [2, 3]:
        print("Sử dụng: python tools/pdf_to_csv.py <path_to_pdf> [max_pages]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Không tìm thấy file: {pdf_path}")
        sys.exit(1)

    max_pages = None
    if len(sys.argv) == 3:
        try:
            max_pages = int(sys.argv[2])
        except ValueError:
            print("max_pages phải là một số nguyên.")
            sys.exit(1)


    output_path = "data/ThongTinUngHo.csv"


    print("Bắt đầu trích xuất dữ liệu từ file PDF ...")
    start_time = time.time()

    extract_and_write_tables(pdf_path, output_path, max_pages)
    end_time = time.time()
    print(f"Tổng thời gian xử lý {end_time - start_time}s")
    print(f"Dữ liệu đã được lưu vào {output_path}")


if __name__ == "__main__":
    main()