import csv

class CsvReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_csv(self):
        data = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    data.append(row)
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return data

    def get_companies(self):
        companies = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if 'Company' in row:
                        companies.append(row['Company'])
                    else:
                        print("No 'Company' column found in the CSV file.")
                        break
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return companies

# Örnek kullanım
# csvReader = CsvReader("/Users/batuhanokmen/Documents/yazilim/bionluk/Apollo/Web-scraping/files/Companies.csv")
# companies = csvReader.get_companies()
# print(companies)