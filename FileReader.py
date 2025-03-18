import pandas as pd

class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        data = []
        try:
            if self.file_path.endswith('.csv'):
                data = pd.read_csv(self.file_path).values.tolist()
            elif self.file_path.endswith(('.xls', '.xlsx')):
                data = pd.read_excel(self.file_path).values.tolist()
            else:
                print("Unsupported file format. Please provide a CSV or Excel file.")
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return data

    def get_companies(self):
        companies = []
        try:
            if self.file_path.endswith('.csv'):
                df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(self.file_path)
            else:
                print("Unsupported file format. Please provide a CSV or Excel file.")
                return companies

            if 'Company' in df.columns:
                companies = df['Company'].dropna().tolist()
            else:
                print("No 'Company' column found in the file.")
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return companies

# Örnek kullanım
# fileReader = FileReader("/path/to/your/file.xlsx")
# companies = fileReader.get_companies()
# print(companies)