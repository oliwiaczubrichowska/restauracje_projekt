konta = {"admin": "admin",}


data = {
"lokale": [
        {
            "id": 1,
            "nazwa": "Pizza u Janka",
            "adres": "Warszawa, Centrum",
            "lat": 52.2297,
            "lon": 21.0122,
        },
        {
            "id": 2,
            "nazwa": "Zielony Talerz",
            "adres": "Skierniewice, Rynek",
            "lat": 51.9549,
            "lon": 20.1583,
        },
    ],
    "klienci": [
        {
            "id": 1,
            "nazwa": "Anna Nowak",
            "telefon": "500100200",
            "godzina_rezerwacji": "18:00",
            "czas_rezerwacji": "2 godziny",
            "adres": "Warszawa, Wola",
            "lat": 52.2319,
            "lon": 20.9822,
            "lokal_id": 1,
        },
        {
            "id": 2,
            "nazwa": "Ola Wisniewska",
            "telefon": "501200300",
            "godzina_rezerwacji": "19:30",
            "czas_rezerwacji": "90 minut",
            "adres": "Skierniewice",
            "lat": 51.9554,
            "lon": 20.1592,
            "lokal_id": 2,
        },
    ],
    "pracownicy": [
        {
            "id": 1,
            "nazwa": "Piotr Kowalski",
            "stanowisko": "kelner",
            "adres": "Warszawa, Praga",
            "lat": 52.2536,
            "lon": 21.0335,
            "lokal_id": 1,
        },
        {
            "id": 2,
            "nazwa": "Marta Zielinska",
            "stanowisko": "manager",
            "adres": "Skierniewice",
            "lat": 51.9539,
            "lon": 20.1570,
            "lokal_id": 2,
        },
    ],
}


def nastepne_id(kategoria):
    if len(data[kategoria]) == 0:
        return 1
    return max(obiekt["id"] for obiekt in data[kategoria]) + 1


def znajdz_po_id(kategoria, obiekt_id):
    for obiekt in data[kategoria]:
        if obiekt["id"] == obiekt_id:
            return obiekt
    return None


def lokal_istnieje(lokal_id):
    return znajdz_po_id("lokale", lokal_id) is not None


def nazwa_lokalu(lokal_id):
    lokal = znajdz_po_id("lokale", lokal_id)
    if lokal is None:
        return "brak lokalu"
    return lokal["nazwa"]


def klienci_lokalu(lokal_id):
    return [klient for klient in data["klienci"] if klient["lokal_id"] == lokal_id]


def pracownicy_lokalu(lokal_id):
    return [pracownik for pracownik in data["pracownicy"] if pracownik["lokal_id"] == lokal_id]


def usun_lokal_z_powiazanymi(lokal_id):
    data["lokale"] = [lokal for lokal in data["lokale"] if lokal["id"] != lokal_id]
    data["klienci"] = [klient for klient in data["klienci"] if klient["lokal_id"] != lokal_id]
    data["pracownicy"] = [
        pracownik for pracownik in data["pracownicy"] if pracownik["lokal_id"] != lokal_id
    ]
