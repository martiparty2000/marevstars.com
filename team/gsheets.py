import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Добавяме # type: ignore за да спрем грешките на Pylance
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope) # type: ignore
    client = gspread.authorize(creds) # type: ignore
    
    sheet = client.open_by_key('1fhwdx7ug04xDHu2YdZzu0SuRKq2RtbHdEhzLP-eQQ0c').sheet1
    return sheet

def add_user_to_sheet(child_name, parent_email):
    sheet = get_sheet()
    sheet.append_row([child_name, parent_email, "0", "He"])