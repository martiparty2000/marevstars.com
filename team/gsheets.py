import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

def get_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Ако файлът съществува в тайните папки на Render, го взимаме от там, иначе локално
    if os.path.exists('/etc/secrets/credentials.json'):
        creds_path = '/etc/secrets/credentials.json'
    else:
        creds_path = 'credentials.json'
        
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope) # type: ignore
    client = gspread.authorize(creds) # type: ignore
    
    # Твоят точен ключ на Google таблицата
    sheet = client.open_by_key('1fhwdx7ug04xDHu2YdZzu0SuRKq2RtbHdEhzLP-eQQ0c').sheet1    
    return sheet

def add_user_to_sheet(child_name, parent_email):
    try:
        print(f"--- Опит за запис в Google Sheets на: {child_name} ({parent_email}) ---")
        sheet = get_sheet()
        sheet.append_row([child_name, parent_email, "0", "He"])
        print("--- УСПЕШЕН ЗАПИС В GOOGLE SHEETS! ---")
    except Exception as e:
        import traceback
        print("!!! ГРЕШКА ВЪТРЕ В GSHEETS.PY !!!")
        traceback.print_exc()  # Това ще изкара целия трасировъчен лог
        raise e