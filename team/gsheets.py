import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # ПРОВЕРКА: Ако сме в Render, взимаме файла от тайната папка, иначе локално
    if os.path.exists('/etc/secrets/credentials.json'):
        creds_path = '/etc/secrets/credentials.json'
    else:
        creds_path = 'credentials.json'
        
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope) # type: ignore
    client = gspread.authorize(creds) # type: ignore
    
    sheet = client.open_by_key('1fhwdx7ug04xDHu2YdZzu0SuRKq2RtbHdEhzLP-eQQ0c').sheet1
    return sheet

def add_user_to_sheet(child_name, parent_email):
    sheet = get_sheet()
    sheet.append_row([child_name, parent_email, "0", "He"])