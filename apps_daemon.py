import socket
import mysql.connector
import time
import wmi

from contextlib import contextmanager
from os import system, listdir
from distutils.dir_util import copy_tree


"""This funtion initializes connection with network drive and kills it after specific instructions have been executed"""
@contextmanager
def network_share_auth(share, username=None, password=None, drive_letter='U'):
    cmd_parts = ["NET USE %s: %s" % (drive_letter, share)]
    if password:
        cmd_parts.append(password)
    if username:
        cmd_parts.append("/USER:%s" % username)
    system(" ".join(cmd_parts))
    try:
        yield
    finally:
        system("NET USE %s: /DELETE" % drive_letter)


"""This functions copies files from network drive to local directory"""
def copy_files():
    with network_share_auth(r"\\192.168.72.10\Aktualizacje", "aktualizacja", "Start123"): # Argumenty od lewej: adres dysku; nazwa uzytkownika synology, hasło uzytkownika synology.
        copy_tree(r"U:\m13", r"C:\apps\appfiles") #Kopiuje katalog. Argumenty od lewej: ścieżka do katalogu, sciezka do katalogu docelowego.


"""This function fetches value from database"""
def db_get():
    return
    try:   
        connection = mysql.connector.connect(host='192.168.72.41',
                                                    database='aktualizacje',
                                                    user='Python',
                                                    password='python') 
        print("Connection with database has been established")  
        h_name = socket.gethostname()     
        sql_select_Query = ("select * from updatem13outbound where %s = '1' LIMIT 1" % (h_name))
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        print("Total number of rows in table: ", cursor.rowcount)
        """Copies data to specific variabales"""
        for row in records:
            result = row[1]
    except mysql.connector.Error as e:
        print("Error reading data from MySQL table: ", e)
    try:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection has been closed")
            gui_operator(name, title, message, mtime)
            return result
    except:
        print("Connection has not been established")
        return 0


"""This function sends value to database"""
def db_set():
    return
    try:
        connection = mysql.connector.connect(host='192.168.72.41',
                                            database='akutalizacje',
                                            user='Python',
                                            password='python')
        print("Connection with database has been established")
        h_name = socket.gethostname()                    
        sql_update_Query = ("UPDATE updatem13outbound SET %s = '0' WHERE time = '%s'" % (h_name))
        cursor = connection.cursor()
        cursor.execute(sql_update_Query)
        connection.commit()
    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)
    try:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection has been closed")
    except:
        print("Connection variable has not been declared")


"""Launches all files in a specific directory"""
def app_launcher():
    file_list = listdir(r"C:\apps\fileapps") #Wpisuje nazwy plików z katalogu do listy
    for i in file_list: #Przechodzi przez listę plików
        try:
            system("start /I C:\\Users\\g.spunda\\Desktop\\testy\\gdzies_na_dysku_c\\python_apps\\apps\\%s" % i) #Uruchamia plik z listy
            print("Proces %s został włączony!" % i)
        except:
            print("Problem z otwarciem pliku!")


"""Kills processes from given directory"""
def app_killer():
    file_list = listdir(r"C:\apps\fileapps") #Wpisuje nazwy plików z katalogu do listy
    for i in file_list: #Przechodzi przez listę plików
        try:
            f = wmi.WMI()
            for process in f.Win32_Process(): #Przechodzi przez wszystke procesy, chwilę to trwa
                if process.name == i: #Porównuje nazwę szukanego procesu z nazwą obecnie przeglądaneg.
                    process.Terminate() #Zabija proces jeśli nazwy są takie same.
                    print("Proces zamknięty!")
        except:
            print("Problem z zamknięciem procesu!")


"""This function contains main logic of a program. The if statement acts accordingly to information given by database."""
def update_seeker():
    #database_info = db_get() #Pobiera info z bazy i przypisuje do zmiennej
    database_info = 2 #Linijka do testowania programu offline. Należy odkomentować ją i skomentować linijkę wyżej.

    if database_info == 0:
        pass #Nic nie robi jeśli wartośc z bazy jest równa zero (bądź nastąpił problem z baza danych). 
             #Warto dać ten przypadek na początku, ponieważ będzie wsyępował najczęsciej i nie będzie pochłaniał mocy obliczeniowej na sprawdzanie pozostałych warunków.
    elif database_info == 1: #Jeśli baza wysłała 1 to wykona się update aplikacji
        app_killer() #Wyłącza działające aplikacje
        copy_files() #Dokonuje aktualizacji aplikacji
        app_launcher() #Odpala aplikacje po aktualizacji
        db_set() #Wysyła do bazy informacje, że aktualizacje sie wykonały.
    elif database_info == 2: #Jesli baza wysłała 2 to wykonuje się update apki do updatów
        try:
            app_killer() #Wyłącza działające aplikacje
            system(r"start /I C:\apps\self_update") #Odpala program do nadpisania tej apki.
            print("apka do nadpisania wlaczona")
        except:
            print("Nie można otworzyć pliku")
        finally:
            print("wyłacza się")
            exit() #Po odpaleniu self_update program się wyłącza, żeby mógł zostać nadpisany.



def main():
    time.sleep(15) #15 sekund na rozruch systemu zanim program zacznie działać.
    print("koniec czekania")
    app_launcher() #Na początku pracy programu włącza wszystkie aplikacje.
    while True: #Nieskończona pętla, która wykonuje sprawdzanie aktualizacji.
        update_seeker() #Tutaj się dużo dzieje...
        time.sleep(60) #Ten sleep odpowiada za częstotliwość sprawdzania bazy danych.

       
if __name__ == "__main__":
    main()
