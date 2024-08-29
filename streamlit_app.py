import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px

st.title("🎈 Hernieuwbare Brandstof Eenheden")
st.write(
    """### Welke regels gelden voor het aantonen van levering van 100% hernieuwbare elektriciteit aan vervoer?

Alleen elektriciteit die aan vervoer is geleverd, wordt beloond met HBE’s. Hernieuwbare elektriciteit die is terug geleverd aan het net of aan andere installaties op de aansluiting, komt niet in aanmerking voor HBE’s.

De inboeker moet door middel van meetgegevens aantonen hoeveel elektriciteit er is opgewekt en dat de opgewekte elektriciteit daadwerkelijk naar vervoer is gegaan. Voor de meters die de opwek van hernieuwbare elektriciteit meten, zijn momenteel geen aparte vereisten opgenomen in de regelgeving.

- Indien de opwekinstallatie ook is aangesloten op andere installaties of aan het net teruglevert, dient de inboeker per tijdsinterval van één uur (of nauwkeuriger) gelijktijdigheid van opwek/ levering aan vervoer aan te tonen.
- Indien er gebruik gemaakt wordt van tussentijdse batterijopslag die niet is aangesloten op het net of aan andere installaties levert, kan de inboeker aantonen dat hernieuwbare elektriciteit de batterij in ging en vervolgens op een later moment aan vervoer is geleverd.
- Indien er gebruik gemaakt wordt van een batterij die ook op het net en/of ander verbruik is aangesloten, kan de levering als 100% hernieuwbaar worden ingeboekt als op uurbasis wordt bijgehouden welk deel van de inhoud van de batterij bestaat uit opgewekte hernieuwbare elektriciteit en ook aan vervoer is geleverd. Zie onderstaand voorbeeld.

![alt text](<Schermafbeelding 2024-08-09 093717.png>)

nboeken voor deze situatie kan als volgt:

- De zonne-elektriciteit (100% hernieuwbaar) die direct geleverd wordt aan vervoer, mag voor 100% hernieuwbaar worden ingeboekt, waarbij gelijktijdigheid op uurbasis (of nauwkeuriger) moet kunnen worden aangetoond..
- De netstroom geleverd aan vervoer mag worden ingeboekt voor het netgemiddelde.
- Om de levering van de batterij naar vervoer (D) gedeeltelijk als 100% hernieuwbaar te kunnen inboeken, zullen per uur ook alle overige stromen die de batterij in en uitgaan (A, B en C) gemeten moeten worden. Dit om te bepalen welk aandeel in de batterij hernieuwbaar is. (Indien dat niet mogelijk is kan D als netstroom ingeboekt worden.)
Per uur moet bijgehouden worden wat de energiemix (groen/grijs) in de batterij is. Binnen dat uur mag het groene gedeelte in de batterij worden gealloceerd aan stroom D. De hoeveelheid in een uur ingeboekte 100% hernieuwbare elektriciteit kan nooit meer zijn dan wat er in dat uur daadwerkelijk aan vervoer is geleverd."""
)




uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_excel(uploaded_file)
    st.write(dataframe)

# Pivot the data
pivot_df = dataframe.pivot_table(
    index=[ 'Tijdstip'], 
    columns=['Meetpunt','Kanaal'], values='Waarde').reset_index()

# Display the transformed data
pivot_df

# Kolomen verwijzen
kolom_Tijdstip = pivot_df[('Tijdstip', '')]
kolom_Windturbines = pivot_df[('Bruto Opwek Micro-Windturbines', 'Elektra Teruglevering (kWh)')]
kolom_Zonnepark = pivot_df[('Bruto Opwek PV 1', 'Elektra Teruglevering (kWh)')]
kolom_Laadpalenauto = pivot_df[('Laadpalen Cars','Elektra verbruik (kWh)')]
kolom_Net_Teruglevering = pivot_df[('Primair Allocatiepunt (PAP)', 'Elektra Teruglevering (kWh)')]
kolom_Net_Verbruik = pivot_df[('Primair Allocatiepunt (PAP)','Elektra verbruik (kWh)')]
kolom_Batterij_Teruglevering = pivot_df[( 'Secundair Allocatiepunt (SAP)', 'Elektra Teruglevering (kWh)')]
kolom_Batterij_Verbruik = pivot_df[( 'Secundair Allocatiepunt (SAP)','Elektra verbruik (kWh)')]
kolom_LaadpalenTrucks = pivot_df[('laadpalen trucks','Elektra verbruik (kWh)')]


def verbruik_gebouw(row):
    # Berekeningen voor verbruik en teruglevering
    Verbruik = row['Net_Verbruik'] - row['Batterij_Verbruik']
    Teruglevering = row["Batterij_Teruglevering"] - row["Net_Teruglevering"]
    GroeneStroom = row["Groene_Stroom"]
    Laadpalen = row["laadpalen"]

    if Verbruik <= 0 and Teruglevering <= 0:
        VerbruikGebouw = GroeneStroom - abs(Verbruik) - abs(Teruglevering) - Laadpalen
    elif Verbruik <= 0 and Teruglevering > 0:
        VerbruikGebouw = GroeneStroom - abs(Verbruik) + abs(Teruglevering) - Laadpalen
    elif Verbruik > 0 and Teruglevering <= 0:
        VerbruikGebouw = GroeneStroom + abs(Verbruik) - abs(Teruglevering) - Laadpalen
    else:  # Verbruik > 0 and Teruglevering > 0
        VerbruikGebouw = GroeneStroom + abs(Verbruik) + abs(Teruglevering) - Laadpalen

    return VerbruikGebouw

# Combineer deze kolommen in een nieuwe DataFrame
df = pd.DataFrame({
    'Tijdstip': kolom_Tijdstip,
    'Windturbines': kolom_Windturbines.values,
    'Zonnepark': kolom_Zonnepark.values,
    'Laadpalenauto': kolom_Laadpalenauto.values,
    'Laadpalen_Trucks': kolom_LaadpalenTrucks.values,
    'Net_Teruglevering': kolom_Net_Teruglevering.values,
    'Net_Verbruik': kolom_Net_Verbruik.values,
    'Batterij_Teruglevering': kolom_Batterij_Teruglevering.values,
    'Batterij_Verbruik': kolom_Batterij_Verbruik.values
    
})

df.set_index(['Tijdstip'],inplace=True)

df["Groene_Stroom"] = df["Windturbines"]+ df["Zonnepark"]
df["laadpalen"] = df["Laadpalenauto"]+ df["Laadpalen_Trucks"]
df["Verbruik"] = (df["Batterij_Verbruik"] - df["Net_Verbruik"])
df["Levering"] = (df["Batterij_Teruglevering"] - df["Net_Teruglevering"])

# Apply the function to the DataFrame
df['Verbruik_Gebouw'] = df.apply(verbruik_gebouw, axis=1)



# Maak de figuur
fig = go.Figure()

# Voeg elke lijn toe aan de figuur
for column in df.columns[6:13]:
    fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name=column))

# Figuur titel en labels
fig.update_layout(title='Lijn plot van meerdere variabelen over de tijd',
                  xaxis_title='Tijd',
                  yaxis_title='kWh')

st.write(fig)

st.write(""" ## HBE berekenen

### HBE's voor hernieuwbaar deel
Alleen voor het hernieuwbare deel van de elektriciteit schrijft het register een aantal HBE’s bij. Voor leveringen van elektriciteit uit het net wordt het Nederlandse aandeel hernieuwbare elektriciteit (van twee jaar voor het leverjaar) gebruikt. Voor 2024 is dit percentage 39,9%.

In twee scenario’s kan de volledige (100%) levering van elektriciteit aan vervoer met HBE’s beloond worden:

1. elektriciteit die op de leveringslocatie (op hetzelfde kadastrale adres) uit hernieuwbare bronnen opgewekt wordt en rechtstreeks aan vervoer is geleverd met behulp van een bemeterd leverpunt;
2. elektriciteit uit hernieuwbare bronnen, opgewekt op een andere locatie (adres), die met een directe lijn aan de leverlocatie is geleverd en met een bemeterd leverpunt aan vervoer geleverd is. 
De inboeker moet over een niet-net Garantie van Oorsprong (GvO) ter grootte van de inboeking beschikken, die naar de NEa overgemaakt dient te worden. Ook mag er voor de elektriciteit geen exploitatiesubsidie betaald zijn.

De inboeker moet altijd kunnen aantonen dat de hernieuwbare elektriciteit (al dan niet na tussenopslag in een accu) aan voertuigen is geleverd. Elektriciteit die terug geleverd is aan het net of aan andere installaties op de aansluiting is geleverd, kan niet ingeboekt worden.

Voor de berekening van het aantal HBE’s wordt een weegfactor 4 gebruikt, vanwege de energie-efficiëntie van elektrisch rijden. De berekening van het aantal HBE’s gebeurt automatisch in het REV. De formules zijn als volgt:

- $Aantal\ HBE-O\ voor\ leveringen\ uit\ het\ net (2024) = omvang\ levering\ in\ kWh\ * 0,0036 * 4 * 0,399$
- $Aantal\ HBE-O\ voor\ 100\% hernieuwbare\ elektriciteit = omvang\ levering\ in\ kWh\ * 0,0036 * 4$ """)

kWh_to_GJ = 0.0036  # 1 kWh = 0.0036 GigaJoule
percentage_groene_net_stroom = 0.399 
prijs_HBE = 12

# Initialisatie van globale variabelen
groene_stroom_batterij = 0
grijze_stroom_batterij = 0

def bereken_HBE(row):
    global groene_stroom_batterij
    global grijze_stroom_batterij

    groene_stroom = row['Groene_Stroom']
    laadpalen = row['laadpalen']
    batterij_in = row['Batterij_Verbruik']
    batterij_uit = row['Batterij_Teruglevering']

    # Directe zonne-energie naar laadpalen
    stroom_aan_laadpalen = min(groene_stroom, laadpalen)

    # Resterende groene stroom na het voeden van laadpalen
    resterende_groene_stroom = max(groene_stroom, laadpalen) - min(groene_stroom, laadpalen)

    # Laad groene stroom in de batterij
    groene_stroom_batterij += min(batterij_in, resterende_groene_stroom)
    grijze_stroom_batterij += max(0, batterij_in - resterende_groene_stroom)
    
    # Bereken hoeveel stroom er nog nodig is voor de laadpalen
    resterende_laadpalen = laadpalen - stroom_aan_laadpalen
    
    # Gebruik stroom uit de batterij voor de laadpalen
    stroom_uit_batterij = min(resterende_laadpalen, groene_stroom_batterij)
    groene_stroom_batterij -= stroom_uit_batterij
    resterende_laadpalen -= stroom_uit_batterij
    
    if grijze_stroom_batterij > 0 and batterij_uit < grijze_stroom_batterij:
        grijze_stroom_batterij -= batterij_uit
    else:
        groene_stroom_batterij -= batterij_uit

    # Totale HBE groen is de som van groene stroom direct naar laadpalen
    # en groene stroom uit de batterij
    HBE_groen = stroom_aan_laadpalen + stroom_uit_batterij

    return HBE_groen

# Bereken HBE's voor elke rij in de DataFrame
df['HBE'] = df.apply(bereken_HBE, axis=1)

somkWh = df['HBE'].sum()
somkWk_grijs = (df['laadpalen'].sum() - somkWh)
HBE_Groen = df['HBE'].sum()* kWh_to_GJ * 4 
HBE_Grijs = somkWk_grijs * kWh_to_GJ * 4 *0.399
Totaal = (HBE_Groen + HBE_Grijs) * prijs_HBE

st.write(f"Totale kWh Groen: {somkWh:0,.0f}")
st.write(f"Totale kWh Grijs: {somkWk_grijs:0,.0f}")
st.write(f"Totale HBE Groen: {HBE_Groen:0,.0f}")
st.write(f"Totale HBE Grijs: {HBE_Grijs:0,.0f}")
st.write(f"Prijs per HBE : {prijs_HBE}")
st.write(f"Totale winst : €{Totaal:0,.2f}")