import pymongo
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING, TEXT
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import json
import datetime

def actual():
    '''
    Zmiana wyświetlania pojazdów na aktualnie znajdujące się w komisie
    '''
    
    global mode
    listbox_text.set('Lista pojazdów w komisie:')
    mode = False
    c_osobowe()

def sold():
    '''
    Zmiana wyświetlania pojazdów na sprzedane
    '''
    global mode
    listbox_text.set('Lista pojazdów sprzedanych:')
    mode = True
    c_osobowe()
#--- funkcje przycisków wyboru typu pojazdu---
def c_osobowe():
    show_listbox('Osobowe')
    reset_search()
def c_uzytkowe():
    show_listbox('Uzytkowe')
    reset_search()
def c_motocykle():
    show_listbox('Motocykle')
    reset_search()
def c_przyczepy():
    show_listbox('Przyczepy')
    reset_search()

def reset_search():
    global szukane
    szukane = False
def create_indexes():
    for name in ('Osobowe','Uzytkowe', 'Motocykle', 'Przyczepy'):
        db[str(name)].create_index([('Marka', TEXT),
                                     ('Rok', TEXT),
                                     ('Cena', ASCENDING),
                                     ('Sprzedane',ASCENDING)])
#--- wyświetlanie listy pojazdów---
def show_listbox(collection):
    ct_listbox.delete(0, END)
    global coll
    coll=collection
    items = db[str(collection)].find({'Sprzedane':mode})

    for item in items:
        keys = list(item.keys())
        x1 = item[str(keys[1])]
        x2 = item[str(keys[2])]
        x3 = item[str(keys[3])]
        x4 = item[str(keys[4])]
        ct_listbox.insert(END, "{} {} {} {} ".format(x1, x2, x3, x4))
    global itemss
    itemss = db[str(coll)].find({'Sprzedane':mode})

#---wyszukiwanie---
def pack_search_labels(crit_window):
    '''Przyklejenie kontrolek do okna wyszukiwania'''
    global marka, rok, c1, c2
    marka = StringVar()
    rok = StringVar()
    c1 = StringVar()
    c2 = StringVar()
    t_font = ("Calibri",16)
    _font = ("Arial",16)
    mlabel = Label(crit_window,text='Marka')
    mlabel.pack()
    mlabel.place(x=25,y=15)
    mlabel.config(font=_font)
    mentry = Entry(crit_window, font=t_font,textvariable=marka)
    mentry.pack()
    mentry.place(x=105,y=15)
    
    rlabel = Label(crit_window,text='Rok')
    rlabel.pack()
    rlabel.place(x=25, y=65)
    rlabel.config(font=_font)
    rentry=Entry(crit_window, font=t_font,textvariable=rok)
    rentry.pack()
    rentry.place(x=105,y=65)
    
    c1_label = Label(crit_window,text='Cena od')
    c1_label.pack()
    c1_label.place(x=15,y=115)
    c1_label.config(font=_font)
    c1_entry = Entry(crit_window, font=t_font,textvariable=c1)
    c1_entry.pack()
    c1_entry.place(x=105,y=115)
    
    c2_label = Label(crit_window,text='Cena do')
    c2_label.pack()
    c2_label.place(x=15, y=165)
    c2_label.config(font=_font)
    c2_entry=Entry(crit_window, font=t_font,textvariable=c2)
    c2_entry.pack()
    c2_entry.place(x=105,y=165)
    
def criteria():
    '''Definicja okna wyszukiwania oraz przycisków'''
    global crit_window
    crit_window = Toplevel(root)
    crit_window.geometry('400x300')
    crit_window.resizable(0,0)
    
    
    pack_search_labels(crit_window)
    s_button = Button(crit_window,text='Szukaj',command=wyszukiwanie)
    s_button.place(x=50,y=215)
    s_button.pack(side='bottom',pady=30)
    
def wyszukiwanie():
    '''Wyszukanie według kryterium oraz przyklejenie wyników na listę'''
    crit_window.destroy()
    global dic
    global szukane
    szukane = True
    dic = {}
    cen = {}
    if len(marka.get()) > 0:
        dic["Marka"] = marka.get()
    if len(rok.get()) > 0:
        dic["Rok"] = rok.get()
    if len(c1.get()) == 0:
        c_1 = 0
    else: 
        c_1 = int(c1.get())
    if len(c2.get()) > 0:
        cen["$lt"] = int(c2.get())
        
    cen["$gt"] = c_1
    dic["Cena"] = cen
    dic["Sprzedane"] = mode
    print(dic)
    ct_listbox.delete(0, END)
    detail.delete(0, END)
    global _items
    _items = db[str(coll)].find(dic)
    
    
    print(str(_items.count()))
    for item in _items:
        keys = list(item.keys())
        x1 = item[str(keys[1])]
        x2 = item[str(keys[2])]
        x3 = item[str(keys[3])]
        x4 = item[str(keys[4])]
        ct_listbox.insert(END, "{} {} {} {} ".format(x1, x2, x3, x4))
        
    if _items.count == 0:
        ct_listbox.delete(0,END)
        detail.delete(0, END)
        
    

#---edycja pojazdu---
def edit(event):
    '''Reakcja na podwójne klinięcie, zdefiniowanie okna edytowania 
        oraz znalezienie pojazdu do edycji według _id'''
    if event.widget.curselection()!=():
        edit_window = Tk()
        edit_window.title("Edycja pojazdu")  # ustawienie tytułu okna głównego
        edit_window.geometry('450x600')
        edit_window.resizable(0, 0)
        dic = {"_id":ind}
        item = db[str(coll)].find_one(dic)
        display_edit(item, edit_window)
    else:
        messagebox.showerror(title='Błąd edycji',message='Edycja jest niemożliwa, gdyż lista pojazdów jest pusta.')

def display_edit(item, edit_window):
    '''Wyświetlenie kontrolek edytowania pojazdu
        wraz z pobraniem nowych wartości'''
    t_font = ("Calibri",10)
    _font = ("Arial",10)
    keys = list(item.keys())
    labels = {}
    entries = {}
    values = {}
    i = 0
    for key in item:
        if key == '_id' or key == 'Sprzedane':
            continue
        if type(item[key]) is list:
            values[key] = display_list(item[key],edit_window,key,(i+1)*30)
            continue
        values[key]=item[key]
        labels[key] = Label(edit_window,text=str(key))
        labels[key].pack()
        labels[key].place(x=25,y=25+i*30)
        labels[key].config(font=_font)
        values[key] = StringVar(edit_window,value=item[key])
        entries[key] = Entry(edit_window, font=t_font, textvariable=values[key])
        entries[key].pack()
        entries[key].place(x=125,y=25+i*30)
        i = i+1
    
    save_button = Button(edit_window, text='Zapisz', command=lambda: is_valid(values,edit_window))
    save_button.pack(side=RIGHT,anchor=SE,padx=10,pady=10)
    back_button = Button(edit_window, text='Anuluj', command=edit_window.destroy)
    back_button.pack(side=RIGHT,anchor=SE,padx=10,pady=10)
    
def display_list(array,edit_window,name="",place=1):
    '''Wyświetlenie tych elementów dokumentu, które są typu array'''
    
    t_font = ("Calibri",10)
    _font = ("Arial",10)
    print(len(array))
    array_values = []
    label = Label(edit_window, text=name)
    label.pack()
    label.place(x=25,y=place)
    _entries = []
    i = 0
    for item in array:
        print(str(i))
        array_values.append(StringVar(edit_window,value=item))
        _entries.append(Entry(edit_window, font=t_font, textvariable=array_values[i]))
        _entries[i].pack()
        _entries[i].place(x=135,y=15+place+i*23)
        i = i+1
    return array_values
    
def is_valid(values,edit_window):
    '''Sprawdzenie poprawności danych oraz ich ewentualna aktualizacja dokumentu'''
    edit_window.destroy()
    if not (values['Uszkodzony'].get() == 'Tak' or values['Uszkodzony'].get() == 'Nie'): 
        messagebox.showerror(title='Błąd edycji',message='Uzupełnij pola odpowiednimi wartościami.')
    else:
        where = {}
        where['_id'] = ind
        _up = {}
        for key, value in values.items():
            print(type(value))
            if type(value) is list:
                _up[key] = item_to_list(value)
            elif key in ('Przebieg', 'Cena', 'Rok', 'Pojemnosc'):
                _up[key] = int(values[key].get())
            else:
                _up[key] = values[key].get()
        
        print(_up)
        result = db[str(coll)].update_one({'_id':where['_id']},{'$set': _up}, upsert=False)
        print(str(result.modified_count))

def item_to_list(array):
    '''Sprowadzenie przedmiotu z kontrolki do listy'''
    text = []
    for item in array:
        text.append(item.get())
    print(text)
    return text

def list_to_str(array):
    '''Formatuje wyświetlenie listy wartości'''
    text = ''
    for item in array:
        text += ' {},'.format(item)
    return text
    
#---szczegóły
def listboxselect(event):
    '''Wyświetlenie listy pojazdów, wraz z eventem kliknięcia na rekord'''
    w = event.widget
    if w.curselection()!=():
        global ind
        index = int(w.curselection()[0])
        item = itemss[index]
        if szukane:
            _szukane = db[str(coll)].find(dic)
            item = _szukane[index]
        detail.configure(state="normal")
        detail.delete('1.0', END)
        keys = list(item.keys())
        ind = item[keys[0]]
        for i in range(1,len(keys)):
            if item[keys[i]] == False:
                text = "{}: Nie \n".format(str(keys[i]))
            elif item[keys[i]] == True:
                text = '{}: Tak \n'.format(str(keys[i]))
            elif type(item[keys[i]]) is list:
                    text = '{}:'.format(str(keys[i]))
                    text += list_to_str(item[keys[i]])
            else:
                text=str(keys[i])+': '+str(item[str(keys[i])])+ '\n'
            detail.insert(END, text)
        detail.configure(state="disabled")
    else:
        detail.configure(state="normal")
        detail.delete('1.0', END)
        detail.configure(state="disabled")
    
#---Usuniecie---#
def check_def():
    ''' Sprawdza czy został wybrany samochód do usunięcia. '''
    try:
        ind
    except:
        messagebox.showerror(title='Błąd',message='Wybierz pojazd, który chcesz usunąć.')
    else:
        delete_window()

def delete_window():
    ''' Definicja okna do usuwania pojazdu. '''
    del_window = Toplevel(root)
    del_window.geometry('220x120')
    del_window.resizable(0,0)
    
    t=Button(del_window,text='Tak',width=10,command=lambda: delete(del_window))
    t.pack()
    t.place(x=20,y=90)

    n=Button(del_window,text='Nie',width=10,command=del_window.destroy)
    n.pack()
    n.place(x=120,y=90)
        
    label = Label(del_window,text='Czy napewno chcesz usunąć \n ten pojazd?')
    label.pack()
    label.place(x=25,y=15)
   
def delete(del_window):
    '''Usunięcie danej z bazy i wyłączenie okna.'''
    del_window.destroy()
    dic = {}
    dic['_id'] = ind
    db[str(coll)].delete_one(dic)
    ct_listbox.delete(0, END)
    
#--- Sprzedaz ---#
def check_sell():
    '''Sprawdza czy wybrano poprawny pojazd do sprzedania
     oraz tworzy okno sprzedazy'''
    
    cena = StringVar()
    try:
        ind
        to_sell = db[str(coll)].find_one({'_id': ind})
        if to_sell['Sprzedane'] == True:
            raise ValueError
    except:
        messagebox.showerror(title='Błąd',message="Wybierz pojazd z "+
                                "aktualnie znajdujących się w komisie.")
    else:
        sell_window = Toplevel(root)
        sell_window.geometry('220x120')
        sell_window.resizable(0,0)
        
        
        label = Label(sell_window,text='Podaj cenę sprzedaży: ')
        label.pack()
        label.place(x=47,y=15)
        
        entry=Entry(sell_window,textvariable=cena)
        entry.pack()
        entry.place(x=47,y=45)
        
        t=Button(sell_window,text='Zatwierdź',width=10,command=lambda: sell(cena,sell_window))
        t.pack()
        t.place(x=67,y=90)
    
def sell(cena,sell_window):
    '''Zmiana wartości 'Sprzedane' na True'''
    try:
        print(str(cena.get()))
        cen = int(cena.get())
    except:
         messagebox.showerror(title='Błąd',message="Wprowadź poprawną liczbę")
    else:
        db[str(coll)].update_one({'_id': ind},{'$set': {'Sprzedano dnia': datetime.datetime.now(),'Sprzedane': True, 'Cena': cen}})
        ct_listbox.delete(0, END)
    finally:
        sell_window.destroy()

#--- Dodawanie ---#
def show_add():
    '''Definiuje okienko dodawnia.'''
    if mode:
        messagebox.showerror(title='Błąd',message="Możesz dodać tylko niesprzedane auto")
        return
    add_window = Toplevel(root)
    add_window.geometry('350x400')
    add_window.resizable(0,0)
    
    labels = {}
    entries = {}
    values = {}
    i = 0
    for x in ('Marka', 'Model','Rok', 'Cena', 'Uszkodzony'):
        values[x] = StringVar()
        labels[x] = Label(add_window,text=x)
        labels[x].pack()
        labels[x].place(x=40,y=40*(i+1))
        entries[x] = Entry(add_window,textvariable=values[x])
        entries[x].pack()
        entries[x].place(x=115,y=40*(i+1))
        i = i+1

    zatwierdz = Button(add_window,text='Zatwierdź',width=30,command=lambda: check_new_doc(values,add_window))
    zatwierdz.pack(side=BOTTOM, pady=20, padx=30)
    
    d_p=Button(add_window,text='Dodaj tablicę',width=30,command=lambda: add_array(values))
    d_p.pack(side=BOTTOM, padx=30)
    
    d_t=Button(add_window,text='Dodaj pole',width=30,command=lambda: add_key_value(values))
    d_t.pack(side=BOTTOM, pady=10,padx=30)

def add_key_value(values):
    value_window = Toplevel(root)
    value_window.geometry('120x150')
    value_window.resizable(0,0)
    value = StringVar()
    key = StringVar()
    
    nazwa = Label(value_window,text='Nazwa')
    nazwa.pack()
    nazwa.place(x=35,y=5)
    
    wartosc = Label(value_window,text='Wartość')
    wartosc.pack()
    wartosc.place(x=35,y=55)
    
    nazwa_entry = Entry(value_window, textvariable=key,width=10)
    nazwa_entry.pack()
    nazwa_entry.place(x=30,y=30)
    
    wartosc_entry = Entry(value_window, textvariable=value,width=10)
    wartosc_entry.pack()
    wartosc_entry.place(x=30,y=80)
    
    d_t=Button(value_window,text='Zatwierdź',width=30,command=lambda: add_to_dict(key,value,values, value_window))
    d_t.pack(side=BOTTOM, pady=10,padx=30)

def add_to_dict(key,value,values,value_window):
    values[key.get()] = value.get()
    value_window.destroy()

def add_array(values):
    how_many_window = Toplevel(root)
    how_many_window.geometry('200x200')
    how_many_window.resizable(0,0)
    
    info = Label(how_many_window,text='Podaj ile pól ma zawierać tablica')
    info.pack()
    info.place(x=15,y=10)
    ile = StringVar()
    a_entry = Entry(how_many_window,textvariable=ile,width=10)
    a_entry.pack()
    a_entry.place(x=70,y=37)
    
    info2 = Label(how_many_window,text='Podaj nazwę tablicy')
    info2.pack()
    info2.place(x=50,y=77)
    array_name = StringVar()
    a_entry2 = Entry(how_many_window,textvariable=array_name,width=10)
    a_entry2.pack()
    a_entry2.place(x=70,y=104)
    
    
    d=Button(how_many_window,text='Zatwierdź',width=10,command=lambda: check_how_many(array_name.get(),ile.get(), how_many_window,values))
    d.pack(side=BOTTOM, pady=10)
    

def check_how_many(array_name, ile, how_many_window,values):
    try:
        ile = int(ile)
        if ile <= 0:
            raise ValueError
    except:
        messagebox.showerror(title='Błąd',message='Podaj liczbę większą od 0.')
        how_many_window.destroy()
    else:
        how_many_window.destroy()
        show_entries(array_name, ile,values)

def show_entries(array_name, ile,values):
    array_window = Toplevel(root)
    array_window.geometry('250x300')
    entries = {}
    labels = {}
    object_array = []
    for i in range(0,ile):
        object_array.append(StringVar())
        labels[i] = Label(array_window, text='{}:'.format(str(i)))
        labels[i].pack()
        labels[i].place(x=30, y=10+30*i)
        entries[i] = Entry(array_window, textvariable=object_array[i])
        entries[i].pack()
        entries[i].place(x=70,y=10+30*i)
    
    zat=Button(array_window,text='Zatwierdź',width=10,command=lambda: add_array_to_val(object_array,array_name,array_window,values))
    zat.pack(side=BOTTOM,pady=10)


def add_array_to_val(object_array,name,window,values):
    array = []
    for i in range(0,len(object_array)):
        array.append(object_array[i].get())
    values[name] = array
    window.destroy()
    
def check_new_doc(values,add_window):
    '''Formatowanie odpowiednich pól na int, usunięcie okna dodawania'''
    try:
        for key,value in values.items():
            if not (type(value) == str or type(value) == list):
                values[key] = value.get()
                if key in ('Cena', 'Rok'):
                    values[key] = int(values[key])
                elif key == 'Uszkodzony':
                    if values[key].upper() == 'TAK':
                        values[key] = True
                    elif values[key].upper() == 'NIE':
                        values[key] = False
                    else:
                        raise ValueError('Formatowanie uszkodzony {} != {}'.format(values[key].upper,values[key]))
            if len(str(values[key])) == 0:
                raise ValueError('Długość {}'.format(str(values[key])))
    except Exception as error:
        messagebox.showerror(title='Błąd',message='Wypełnij luki poprawnymi danymi.')# + repr(error))
    else:
        add_new_doc(values)
    finally:
        add_window.destroy()
        return
        

def add_new_doc(values):
    '''Dodanie nowego dokumentu do bazy'''
    values['Sprzedane'] = False
    print(values)
    idd = db[str(coll)].insert_one(values).inserted_id
    messagebox.showerror(title='Dodanie',message='Pomyślnie dodano dokument')
    ct_listbox.delete(0,END)

# * * * Okno * * *
root = Tk()
root.title("KomisDB")  # ustawienie tytułu okna głównego
root.geometry('1080x450')
root.resizable(0, 0)

# * * * Baza Danych * * *
client = MongoClient('localhost', 27017)
db = client['komis']
osobowe = db.Osobowe
uzytkowe = db.Uzytkowe
motocykle = db.Motocykle
przyczepy = db.Przyczepy
mode = False
create_indexes()

# * * * Menu * * *
menu = Menu(root)
root.config(menu=menu)
menu.add_cascade(label="Aktualny stan", command=actual)
menu.add_cascade(label="Sprzedane", command=sold)

# * * * Lista * * *

listbox_text = StringVar()
listbox_text.set('Lista pojazdów w komisie:')
list_label = Label(root, textvariable=listbox_text, padx=2, pady=7)
list_label.pack()
list_label.place(x=8, y=30)
ct_listbox = Listbox(root, width=60, height=20)  # tworzę kontrolkę listbox
ct_listbox.pack()  # wstawiam ją w oknie
ct_listbox.place(x=10, y=55)  # ustawienie położenia kontrolki
# --- Szczegoly pojazdu---
detail = Text(root, width=50, height=20, bg='white')
detail.pack()
detail.place(x=400, y=57)
detail.config(cursor="")
detail.configure(state="disabled")


# ---bindowanie---
ct_listbox.bind('<<ListboxSelect>>',listboxselect)
ct_listbox.bind('<Double-Button-1>', edit)



# * * * Toolbar * * *

toolbar = Frame(root, bg='#2e2e2e')
OsoboweButt = Button(toolbar, text="Osobowe", command=c_osobowe)
OsoboweButt.pack(side=LEFT, padx=2, pady=2)
UzytkoweButt = Button(toolbar, text="Użytkowe", command=c_uzytkowe)
UzytkoweButt.pack(side=LEFT, padx=2, pady=2)
MotocykleButt = Button(toolbar, text="Motocykle", command=c_motocykle)
MotocykleButt.pack(side=LEFT, padx=2, pady=2)
PrzyczepyButt = Button(toolbar, text="Przyczepy", command=c_przyczepy)
PrzyczepyButt.pack(side=LEFT, padx=2, pady=2)
toolbar.pack(side=TOP, fill=X)

#---wyszukiwanie--
c_osobowe()
#frame2=Frame(root)
#frame2.pack(fill=X,side=BOTTOM)
#search = Entry(frame2,bd=4,bg='#33FF99',width=30)

#search.pack()
#search.place(x=8)
#var=StringVar()
#kryt=Label(frame2,textvariable=var)
#var.set("Kryterium wyszukiwania:")
#kryt.pack()
#values = ['Marka','Rok','Cena','Skrzynia']
#combo= ttk.Combobox(frame2,values=values)
#combo.pack()

wyszuk=Button(root,text='Wyszukiwanie',width=30,command=criteria)
wyszuk.pack(side=TOP, anchor=NE, pady=30, padx=30)

dodaj=Button(root,text='Dodaj',width=30,command=show_add)
dodaj.pack(side=TOP, anchor=NE, pady=5, padx=30)

usun=Button(root,text='Usuń',width=30,command=check_def)
usun.pack(side=TOP, anchor=NE, pady=5, padx=30)

sprzedaj=Button(root,text='Sprzedaj',width=30,command=check_sell)
sprzedaj.pack(side=TOP, anchor=NE, pady=30, padx=30)


root.mainloop()
