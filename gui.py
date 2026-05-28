import tkinter as tk
from tkinter import messagebox, ttk

import model

try:
    import tkintermapview
except ImportError:
    tkintermapview = None


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Logowanie do systemu")
        self.geometry("320x230")
        self.resizable(False, False)

        tk.Label(self, text="Login:").pack(pady=(20, 5))
        self.e_login = tk.Entry(self, width=28)
        self.e_login.pack()

        tk.Label(self, text="Haslo:").pack(pady=5)
        self.e_haslo = tk.Entry(self, show="*", width=28)
        self.e_haslo.pack()

        tk.Button(self, text="Zaloguj", command=self.zaloguj).pack(pady=8)
        tk.Button(self, text="Zarejestruj sie", command=self.otworz_rejestracje).pack()
        tk.Label(self, text="Konto testowe: admin / admin").pack(pady=8)

        self.e_haslo.bind("<Return>", lambda event: self.zaloguj())
        self.e_login.focus()

    def zaloguj(self):
        login = self.e_login.get().strip()
        haslo = self.e_haslo.get().strip()

        if login in model.konta and model.konta[login] == haslo:
            self.destroy()
            app = MainWindow()
            app.mainloop()
        else:
            messagebox.showerror("Blad", "Nieprawidlowy login lub haslo!")

    def otworz_rejestracje(self):
        okno_rej = tk.Toplevel(self)
        okno_rej.title("Rejestracja")
        okno_rej.geometry("280x190")
        okno_rej.resizable(False, False)

        tk.Label(okno_rej, text="Podaj nowy login:").pack(pady=5)
        nowy_login = tk.Entry(okno_rej, width=26)
        nowy_login.pack()

        tk.Label(okno_rej, text="Podaj nowe haslo:").pack(pady=5)
        nowe_haslo = tk.Entry(okno_rej, show="*", width=26)
        nowe_haslo.pack()

        def zapisz_konto():
            log = nowy_login.get().strip()
            has = nowe_haslo.get().strip()

            if log == "" or has == "":
                messagebox.showwarning("Blad", "Wypelnij oba pola!", parent=okno_rej)
                return
            if log in model.konta:
                messagebox.showwarning("Blad", "Taki uzytkownik juz istnieje!", parent=okno_rej)
                return

            model.konta[log] = has
            messagebox.showinfo("Sukces", "Konto utworzone. Mozesz sie zalogowac.", parent=okno_rej)
            okno_rej.destroy()

        tk.Button(okno_rej, text="Utworz konto", command=zapisz_konto).pack(pady=10)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zarzadzanie restauracjami i rezerwacjami")
        self.geometry("1050x820")
        self.minsize(950, 720)

        self.listboxy = {}
        self.lista_id = {}
        self.formularze = {}
        self.odswiezacze = {}
        self.map_widget = None
        self.markery = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 4))

        self.tab_lokale = ttk.Frame(self.notebook)
        self.tab_klienci = ttk.Frame(self.notebook)
        self.tab_pracownicy = ttk.Frame(self.notebook)
        self.tab_raport = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_lokale, text="Lokale")
        self.notebook.add(self.tab_klienci, text="Klienci")
        self.notebook.add(self.tab_pracownicy, text="Pracownicy")
        self.notebook.add(self.tab_raport, text="Widok lokalu")

        self.buduj_crud(self.tab_lokale, "lokale")
        self.buduj_crud(
            self.tab_klienci,
            "klienci",
            wymaga_lokalu=True,
            dodatkowe_pola=[("telefon", "Telefon:"), ("stolik", "Numer stolika:")],
        )
        self.buduj_crud(
            self.tab_pracownicy,
            "pracownicy",
            wymaga_lokalu=True,
            dodatkowe_pola=[("stanowisko", "Stanowisko:")],
        )
        self.buduj_raport()
        self.buduj_mape()
        self.odswiez_wszystko()

    def buduj_crud(self, parent, kategoria, wymaga_lokalu=False, dodatkowe_pola=None):
        if dodatkowe_pola is None:
            dodatkowe_pola = []

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.rowconfigure(0, weight=1)

        list_frame = ttk.LabelFrame(parent, text="Lista", padding=8)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        listbox = tk.Listbox(list_frame, width=65, exportselection=False)
        listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        listbox.config(yscrollcommand=scrollbar.set)

        form = ttk.LabelFrame(parent, text="Formularz", padding=10)
        form.grid(row=0, column=1, sticky="ns", padx=10, pady=10)

        pola = {
            "nazwa": self.dodaj_pole(form, "Nazwa:", 0),
            "adres": self.dodaj_pole(form, "Adres:", 1),
            "lat": self.dodaj_pole(form, "Szerokosc geogr.:", 2),
            "lon": self.dodaj_pole(form, "Dlugosc geogr.:", 3),
        }

        row = 4
        if wymaga_lokalu:
            pola["lokal_id"] = self.dodaj_pole(form, "ID lokalu:", row)
            row += 1

        for klucz, etykieta in dodatkowe_pola:
            pola[klucz] = self.dodaj_pole(form, etykieta, row)
            row += 1

        self.listboxy[kategoria] = listbox
        self.lista_id[kategoria] = []
        self.formularze[kategoria] = pola

        ttk.Button(form, text="Dodaj", command=lambda: self.dodaj(kategoria, wymaga_lokalu, dodatkowe_pola)).grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 3),
        )
        ttk.Button(
            form,
            text="Aktualizuj zaznaczone",
            command=lambda: self.aktualizuj(kategoria, wymaga_lokalu, dodatkowe_pola),
        ).grid(row=row + 1, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(form, text="Usun zaznaczone", command=lambda: self.usun(kategoria)).grid(
            row=row + 2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=3,
        )
        ttk.Button(form, text="Wyczysc formularz", command=lambda: self.wyczysc_formularz(kategoria)).grid(
            row=row + 3,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=3,
        )

        listbox.bind("<<ListboxSelect>>", lambda event: self.wczytaj_zaznaczone(kategoria))
        self.odswiezacze[kategoria] = lambda: self.odswiez_liste(kategoria, wymaga_lokalu, dodatkowe_pola)

    def dodaj_pole(self, parent, tekst, row):
        ttk.Label(parent, text=tekst).grid(row=row, column=0, sticky="w", pady=3)
        entry = ttk.Entry(parent, width=28)
        entry.grid(row=row, column=1, sticky="ew", pady=3)
        return entry

    def odswiez_liste(self, kategoria, wymaga_lokalu, dodatkowe_pola):
        listbox = self.listboxy[kategoria]
        listbox.delete(0, tk.END)
        self.lista_id[kategoria] = []

        for obiekt in model.data[kategoria]:
            self.lista_id[kategoria].append(obiekt["id"])
            opis = f"ID: {obiekt['id']} | {obiekt['nazwa']} | {obiekt['adres']}"
            if wymaga_lokalu:
                opis += f" | Lokal: {model.nazwa_lokalu(obiekt['lokal_id'])}"
            if "stolik" in obiekt:
                opis += f" | Stolik: {obiekt['stolik']}"
            if "stanowisko" in obiekt:
                opis += f" | {obiekt['stanowisko']}"
            listbox.insert(tk.END, opis)

    def dodaj(self, kategoria, wymaga_lokalu, dodatkowe_pola):
        try:
            nowy = self.zbuduj_obiekt_z_formularza(kategoria, wymaga_lokalu, dodatkowe_pola)
        except ValueError:
            return

        nowy["id"] = model.nastepne_id(kategoria)
        model.data[kategoria].append(nowy)
        self.wyczysc_formularz(kategoria)
        self.odswiez_wszystko()

    def aktualizuj(self, kategoria, wymaga_lokalu, dodatkowe_pola):
        obiekt_id = self.pobierz_zaznaczone_id(kategoria)
        if obiekt_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz obiekt do aktualizacji.")
            return

        try:
            nowe_dane = self.zbuduj_obiekt_z_formularza(kategoria, wymaga_lokalu, dodatkowe_pola)
        except ValueError:
            return

        obiekt = model.znajdz_po_id(kategoria, obiekt_id)
        if obiekt is None:
            return
        nowe_dane["id"] = obiekt_id
        obiekt.clear()
        obiekt.update(nowe_dane)
        self.odswiez_wszystko()

    def usun(self, kategoria):
        obiekt_id = self.pobierz_zaznaczone_id(kategoria)
        if obiekt_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz obiekt do usuniecia.")
            return

        if kategoria == "lokale":
            if not messagebox.askyesno("Usun lokal", "Usunac lokal razem z klientami i pracownikami?"):
                return
            model.usun_lokal_z_powiazanymi(obiekt_id)
        else:
            model.data[kategoria] = [
                obiekt for obiekt in model.data[kategoria] if obiekt["id"] != obiekt_id
            ]

        self.wyczysc_formularz(kategoria)
        self.odswiez_wszystko()

    def zbuduj_obiekt_z_formularza(self, kategoria, wymaga_lokalu, dodatkowe_pola):
        pola = self.formularze[kategoria]
        nazwa = pola["nazwa"].get().strip()
        adres = pola["adres"].get().strip()

        if nazwa == "" or adres == "":
            messagebox.showwarning("Brak danych", "Uzupelnij nazwe i adres.")
            raise ValueError

        lat = self.pobierz_liczbe(pola["lat"], "szerokosc")
        lon = self.pobierz_liczbe(pola["lon"], "dlugosc")

        obiekt = {
            "nazwa": nazwa,
            "adres": adres,
            "lat": lat,
            "lon": lon,
        }

        if wymaga_lokalu:
            try:
                lokal_id = int(pola["lokal_id"].get())
            except ValueError:
                messagebox.showwarning("Blad danych", "ID lokalu musi byc liczba.")
                raise ValueError
            if not model.lokal_istnieje(lokal_id):
                messagebox.showwarning("Blad danych", "Nie ma lokalu o takim ID.")
                raise ValueError
            obiekt["lokal_id"] = lokal_id

        for klucz, _etykieta in dodatkowe_pola:
            obiekt[klucz] = pola[klucz].get().strip()

        return obiekt

    def pobierz_liczbe(self, entry, nazwa_pola):
        tekst = entry.get().strip().replace(",", ".")
        try:
            return float(tekst)
        except ValueError as error:
            messagebox.showwarning("Blad danych", f"Pole {nazwa_pola} musi byc liczba.")
            raise ValueError from error

    def wczytaj_zaznaczone(self, kategoria):
        obiekt_id = self.pobierz_zaznaczone_id(kategoria)
        if obiekt_id is None:
            return

        obiekt = model.znajdz_po_id(kategoria, obiekt_id)
        if obiekt is None:
            return

        for klucz, entry in self.formularze[kategoria].items():
            entry.delete(0, tk.END)
            entry.insert(0, str(obiekt.get(klucz, "")))

        self.ustaw_mape_na_obiekcie(obiekt)

    def pobierz_zaznaczone_id(self, kategoria):
        zaznaczenie = self.listboxy[kategoria].curselection()
        if not zaznaczenie:
            return None
        indeks = zaznaczenie[0]
        return self.lista_id[kategoria][indeks]

    def wyczysc_formularz(self, kategoria):
        self.listboxy[kategoria].selection_clear(0, tk.END)
        for entry in self.formularze[kategoria].values():
            entry.delete(0, tk.END)

    def buduj_raport(self):
        ramka = ttk.Frame(self.tab_raport, padding=12)
        ramka.pack(fill="both", expand=True)

        ttk.Label(ramka, text="Wybierz lokal:").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_lokal = ttk.Combobox(ramka, state="readonly", width=40)
        self.combo_lokal.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Button(ramka, text="Pokaz osoby", command=self.pokaz_osoby_lokalu).grid(
            row=0,
            column=2,
            padx=8,
            pady=5,
        )

        ttk.Label(ramka, text="Klienci wybranego lokalu:").grid(row=1, column=0, sticky="w", pady=(15, 3))
        ttk.Label(ramka, text="Pracownicy wybranego lokalu:").grid(row=1, column=1, sticky="w", pady=(15, 3))

        self.lista_klientow_lokalu = tk.Listbox(ramka, width=42, height=12)
        self.lista_pracownikow_lokalu = tk.Listbox(ramka, width=42, height=12)
        self.lista_klientow_lokalu.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        self.lista_pracownikow_lokalu.grid(row=2, column=1, sticky="nsew")

    def odswiez_combo_lokali(self):
        self.combo_lokal["values"] = [
            f"{lokal['id']} - {lokal['nazwa']}" for lokal in model.data["lokale"]
        ]

    def pokaz_osoby_lokalu(self):
        self.lista_klientow_lokalu.delete(0, tk.END)
        self.lista_pracownikow_lokalu.delete(0, tk.END)

        try:
            lokal_id = int(self.combo_lokal.get().split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Brak wyboru", "Wybierz lokal z listy.")
            return

        for klient in model.klienci_lokalu(lokal_id):
            self.lista_klientow_lokalu.insert(
                tk.END,
                f"{klient['nazwa']} | stolik {klient.get('stolik', '')}",
            )

        for pracownik in model.pracownicy_lokalu(lokal_id):
            self.lista_pracownikow_lokalu.insert(
                tk.END,
                f"{pracownik['nazwa']} | {pracownik.get('stanowisko', '')}",
            )

    def buduj_mape(self):
        ramka_mapa = ttk.LabelFrame(self, text="Mapa obiektow", padding=6)
        ramka_mapa.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        if tkintermapview is None:
            ttk.Label(
                ramka_mapa,
                text="Brakuje biblioteki tkintermapview. Zainstaluj ja, aby zobaczyc mape w oknie.",
            ).pack(padx=20, pady=30)
            return

        self.map_widget = tkintermapview.TkinterMapView(
            ramka_mapa,
            width=1000,
            height=300,
            corner_radius=4,
        )
        self.map_widget.pack(fill="x", expand=True)
        self.map_widget.set_position(52.0, 19.0)
        self.map_widget.set_zoom(6)

    def odswiez_mape(self):
        if self.map_widget is None:
            return

        for marker in self.markery:
            marker.delete()
        self.markery = []

        self.dodaj_markery("lokale", "Lokal", "red")
        self.dodaj_markery("klienci", "Klient", "blue")
        self.dodaj_markery("pracownicy", "Pracownik", "green")

    def dodaj_markery(self, kategoria, etykieta, kolor):
        for obiekt in model.data[kategoria]:
            marker = self.map_widget.set_marker(
                obiekt["lat"],
                obiekt["lon"],
                text=f"{etykieta}: {obiekt['nazwa']}",
                marker_color_circle=kolor,
                marker_color_outside="white",
                command=lambda marker, kat=kategoria, obj_id=obiekt["id"]: self.wybierz_z_mapy(kat, obj_id),
            )
            self.markery.append(marker)

    def wybierz_z_mapy(self, kategoria, obiekt_id):
        zakladki = {
            "lokale": self.tab_lokale,
            "klienci": self.tab_klienci,
            "pracownicy": self.tab_pracownicy,
        }
        self.notebook.select(zakladki[kategoria])
        self.zaznacz_na_liscie(kategoria, obiekt_id)
        self.wczytaj_zaznaczone(kategoria)

    def zaznacz_na_liscie(self, kategoria, obiekt_id):
        if obiekt_id not in self.lista_id[kategoria]:
            return
        indeks = self.lista_id[kategoria].index(obiekt_id)
        listbox = self.listboxy[kategoria]
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(indeks)
        listbox.activate(indeks)
        listbox.see(indeks)

    def ustaw_mape_na_obiekcie(self, obiekt):
        if self.map_widget is None:
            return
        self.map_widget.set_position(obiekt["lat"], obiekt["lon"])
        self.map_widget.set_zoom(13)

    def odswiez_wszystko(self):
        for odswiez in self.odswiezacze.values():
            odswiez()
        self.odswiez_combo_lokali()
        self.pokaz_osoby_lokalu_bez_bledu()
        self.odswiez_mape()

    def pokaz_osoby_lokalu_bez_bledu(self):
        if self.combo_lokal.get() == "":
            return
        try:
            self.pokaz_osoby_lokalu()
        except tk.TclError:
            return
