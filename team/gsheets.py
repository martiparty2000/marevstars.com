import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Проверяваме дали сме в Render (/etc/secrets/) или на твоя компютър
    creds_path = '/etc/secrets/credentials.json' if os.path.exists('/etc/secrets/credentials.json') else 'credentials.json'
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope) # type: ignore
    client = gspread.authorize(creds) # type: ignore
    
    sheet = client.open_by_key('1fhwdx7ug04xDHu2YdZzu0SuRKq2RtbHdEhzLP-eQQ0c').sheet1
    return sheet

def add_user_to_sheet(child_name, parent_email):
    sheet = get_sheet()
    sheet.append_row([child_name, parent_email, "0", "He"])