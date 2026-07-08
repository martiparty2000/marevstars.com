import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    # Замени с ID-то от URL на твоята таблица
    sheet = client.open_by_key('1fhwdx7ugO4xDHu2YdZzuOSuRKq2RtbHdEhzLP-eQQOc').sheet1
    return sheet

def add_user_to_sheet(child_name, parent_email):
    sheet = get_sheet()
    sheet.append_row([child_name, parent_email, "0", "Не"])