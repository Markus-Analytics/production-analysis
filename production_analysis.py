# Production Analysis Project
# Ziel: Analyse von Ausschuss, Kosten und Stillstand in der Produktion

import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv("Produktion_Case2.csv")
pd.options.display.float_format = "{:,.2f}".format

# ======================
# Datenqualität prüfen
# ======================
negativ_anteil=(df["Ausschuss"]<0).mean()*100
print(f"Anteil negativer Ausschusswerte: {negativ_anteil:.2f}%")

df['Ausschuss']=df['Ausschuss'].clip(lower=0)
# Hinweis:
# Ein kleiner Anteil der Daten enthielt negative Ausschusswerte (Datenfehler).
# Diese wurden auf 0 gesetzt, da negativer Ausschuss nicht möglich ist.

# Datum umwandeln
df["Datum"] = pd.to_datetime(df["Datum"])

# Stunde extrahieren
df["Stunde"] = df["Datum"].dt.hour

# Schichten bestimmen
def schicht_bestimmen(stunde):
    if 6 <= stunde < 14:
        return "Früh"
    elif 14 <= stunde < 22:
        return "Spät"
    else:
        return "Nacht"

df["Schicht"] = df["Stunde"].apply(schicht_bestimmen)

# ======================
# KPIs
# ======================
gesamtproduktion = df["Produktion"].sum()
gesamtausschuss = df["Ausschuss"].sum()
ausschussquote = gesamtausschuss / gesamtproduktion * 100

# ======================
# Maschinenanalyse
# ======================

maschinen = df.groupby("Maschine").agg({
    "Produktion": "sum",
    "Ausschuss": "sum",
    "Stillstand_min": "sum"
})

maschinen["Ausschussquote"] = (
    maschinen["Ausschuss"] / maschinen["Produktion"] * 100
)

# ======================
# Kostenanalyse
# ======================

df["Ausschusskosten"] = df["Ausschuss"] * df["Kosten_pro_Einheit"]
df["Echte_Kosten"] = df["Gesamtkosten"] + df["Ausschusskosten"]

echte_gesamtkosten_maschine = df.groupby("Maschine")["Echte_Kosten"].sum()
echte_durchschnittskosten = df.groupby("Maschine")["Echte_Kosten"].mean()

kosten_stunde = df.groupby("Maschine")["Gesamtkosten"].mean()

stillstand_schaden = (
    df.groupby("Maschine")["Stillstand_min"].sum() / 60
) * kosten_stunde

# ======================
# Visualisierung
# ======================

maschinen["Ausschussquote"].sort_values(ascending=False).plot(kind="bar")
plt.title("Ausschussquote pro Maschine")
plt.ylabel("Prozent")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

echte_durchschnittskosten.sort_values(ascending=False).plot(kind="bar")
plt.title("Durchschnittliche Kosten pro Maschine")
plt.ylabel("€")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

stillstand_schaden.sort_values(ascending=False).plot(kind="bar")
plt.title("Kosten durch Stillstand pro Maschine")
plt.ylabel("€")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# ======================
# Ergebnisse
# ======================

print("\n=== KPIs ===")
print(f"Gesamtproduktion: {gesamtproduktion:,.0f}")
print(f"Ausschussquote: {ausschussquote:.2f}%")
print(f"Gesamtausschuss: {gesamtausschuss:,.0f}")

print("\n=== Maschinen nach Ausschussquote ===")
print(maschinen.sort_values("Ausschussquote", ascending=False).round(2))

print("\n=== Durchschnittskosten ===")
print(echte_durchschnittskosten.sort_values(ascending=False).round(2))

print("\n=== Stillstandskosten ===")
print(stillstand_schaden.sort_values(ascending=False).round(2))

# ======================
# Fazit
# ======================
# M1: Höchste Gesamtkosten durch hohe Produktion
# M2: Höchster finanzieller Schaden durch Stillstand
# M3: Höchste Ausschussquote - ineffizienteste Maschine (höchste Durchschnittskosten)
