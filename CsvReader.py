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
#ex
"""
csvReader = CsvReader("/Users/batuhanokmen/Documents/yazilim/bionluk/Apollo/Web-scraping/files/Companies.csv")
data = csvReader.read_csv()
print(data)
"""