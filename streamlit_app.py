import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.title("Hernieuwbare Brandstof Eenheden")
st.markdown("""
### Wat zijn Hernieuwbare Brandstof Eenheden (HBE's)?

Hernieuwbare Brandstof Eenheden (HBE's) zijn digitale certificaten die worden gebruikt om de productie en het gebruik van hernieuwbare energie te bevorderen, specifiek binnen de transportsector. In Nederland vallen deze certificaten onder het systeem van de **Wet milieubeheer** en de **Europese Richtlijn Hernieuwbare Energie (RED II)**. Ze fungeren als bewijs dat een bepaalde hoeveelheid hernieuwbare energie, zoals biobrandstof, waterstof of elektriciteit, is geproduceerd of gebruikt. Bedrijven kunnen HBE's verhandelen om te voldoen aan hun verplichtingen voor de inzet van hernieuwbare energie en om bij te dragen aan de vermindering van CO₂-uitstoot.
""")

# Sectie over HBE-O Elektriciteit
st.markdown("""
### Wat is HBE-O Elektriciteit?

Binnen het HBE-systeem is er een specifieke categorie voor elektriciteit: **HBE-O Elektriciteit** (Hernieuwbare Brandstof Eenheden - Overig Elektriciteit). Dit type HBE is gericht op de bevordering van hernieuwbare elektriciteit die wordt gebruikt in elektrische voertuigen (EV's) voor transportdoeleinden. Het idee is om de transitie naar elektrisch rijden te ondersteunen door producenten en leveranciers van hernieuwbare elektriciteit te belonen met HBE's, die zij vervolgens kunnen verhandelen.
""")

# Uitleg over de werking van HBE-O Elektriciteit
st.markdown("""
### Hoe werkt HBE-O Elektriciteit?

1. **Productie van Hernieuwbare Elektriciteit**: Elektriciteit die wordt opgewekt uit hernieuwbare bronnen zoals wind, zon, waterkracht of biomassa komt in aanmerking voor HBE's. Elektriciteitsproducenten kunnen hun duurzame energieproductie aanmelden bij de Nederlandse Emissieautoriteit (NEa) om in aanmerking te komen voor HBE-O Elektriciteit.

2. **Toekenning van HBE's**: Voor elke eenheid (bijvoorbeeld megawattuur, MWh) hernieuwbare elektriciteit die wordt geleverd aan elektrische voertuigen, ontvangen de producenten HBE-O Elektriciteit. Deze eenheden kunnen worden toegekend aan laadstations, leveranciers van stroom aan EV's, of partijen die betrokken zijn bij de opslag en distributie van elektriciteit voor transport.

3. **Handel in HBE's**: Net als andere HBE's kunnen HBE-O Elektriciteit-certificaten worden verhandeld op de markt. Bedrijven zoals olie- en gasmaatschappijen, die wettelijk verplicht zijn om een bepaald percentage hernieuwbare energie in hun brandstofmix te hebben, kunnen deze certificaten kopen om te voldoen aan hun verplichtingen.

4. **Stimulering van Elektrisch Rijden**: Het verkrijgen van HBE-O Elektriciteit moedigt investeringen aan in hernieuwbare energie-infrastructuur, zoals laadpalen en slimme netwerken, die nodig zijn om de groei van elektrisch rijden te ondersteunen.
""")

# Mogelijkheden voor het gebruik van HBE-O Elektriciteit
st.markdown("""
### Wat kun je doen met HBE-O Elektriciteit?

- **Voor Producenten van Hernieuwbare Elektriciteit**: Deze producenten, zoals exploitanten van wind- en zonneparken, kunnen extra inkomsten genereren door HBE-O Elektriciteit te verkrijgen voor de hernieuwbare elektriciteit die ze leveren aan de transportsector. Dit maakt investeringen in duurzame energiebronnen aantrekkelijker.

- **Voor Exploitanten van Laadinfrastructuur**: Bedrijven die laadstations exploiteren en elektriciteit leveren aan EV's kunnen HBE-O Elektriciteit verkrijgen en verhandelen, wat een extra inkomstenstroom biedt. Dit helpt bij het verbeteren van de rentabiliteit van investeringen in laadinfrastructuur.

- **Voor Brandstofleveranciers en Energiebedrijven**: Bedrijven die fossiele brandstoffen leveren, kunnen HBE-O Elektriciteit kopen om hun verplichtingen met betrekking tot hernieuwbare energie in transport na te komen. Dit biedt flexibiliteit en stimuleert hen om bij te dragen aan de elektrificatie van transport.

- **Voor Overheden en Beleidsmakers**: HBE-O Elektriciteit speelt een sleutelrol in het behalen van nationale en Europese doelstellingen voor emissiereductie en verduurzaming van de transportsector.
""")

# Conclusie
st.markdown("""
### Data ophalen

De data wordt opgehaald uit fudura.
""")


# File uploader
uploaded_file = st.file_uploader("Kies een bestand")

# If a file is uploaded, proceed with processing
if uploaded_file is not None:
    # Read the file into a dataframe
    dataframe = pd.read_excel(uploaded_file)
    st.write(dataframe)

# Pivot the data
    pivot_df = dataframe.pivot_table(
        index=[ 'Tijdstip'], 
        columns=['Meetpunt','Kanaal'], values='Waarde').reset_index()
    st.write(pivot_df)


    # Kolomen verwijzen
    kolom_Tijdstip = pivot_df[('Tijdstip', '')]
    kolom_Windturbines = pivot_df[('Bruto Opwek Micro-Windturbines', 'Elektra Teruglevering (kWh)')]
    kolom_Zonnepark = pivot_df[('Bruto Opwek PV 1', 'Elektra Teruglevering (kWh)')]
    kolom_Laadpalenauto = pivot_df[('Laadpalen Cars','Elektra verbruik (kWh)')]
    kolom_Net_Teruglevering = pivot_df[('Primair Allocatiepunt (PAP)', 'Elektra Teruglevering (kWh)')]
    kolom_Net_Verbruik = pivot_df[('Primair Allocatiepunt (PAP)','Elektra verbruik (kWh)')]
    kolom_Batterij_Teruglevering = pivot_df[('Secundair Allocatiepunt (SAP)', 'Elektra Teruglevering (kWh)')]
    kolom_Batterij_Verbruik = pivot_df[('Secundair Allocatiepunt (SAP)','Elektra verbruik (kWh)')]
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

    df["Groene_Stroom"] = df["Windturbines"] + df["Zonnepark"]
    df["laadpalen"] = df["Laadpalenauto"] + df["Laadpalen_Trucks"]
    df["Verbruik"] = (df["Batterij_Verbruik"] - df["Net_Verbruik"])
    df["Levering"] = (df["Batterij_Teruglevering"] - df["Net_Teruglevering"])

    # Apply the function to the DataFrame
    df['Verbruik_Gebouw'] = df.apply(verbruik_gebouw, axis=1)

    df = df.drop(df.index[-1])

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
    prijs_HBE = st.number_input("Vul De prijs van de  HBE's in:")
    st.write("De HBE prijs is: ", prijs_HBE)

    # Initialisatie van globale variabelen
    groene_stroom_batterij = 0
    grijze_stroom_batterij = 0

    def calculate_HBEs(row):
        
        groene_stroom = row['Groene_Stroom']
        laadpalen = row['laadpalen']
        
        # Directe zonne-energie HBE's
        HBE_direct = min(groene_stroom, laadpalen)

        return HBE_direct

    df['HBE'] = df.apply(calculate_HBEs, axis=1)

    # def bereken_HBE(row):
    #     global groene_stroom_batterij
    #     global grijze_stroom_batterij
        
    #     # Inputwaarden van de rij
    #     groene_stroom = row['Groene_Stroom']
    #     laadpalen = row['laadpalen']
    #     batterij_in = row['Batterij_Verbruik']
    #     batterij_uit = row['Batterij_Teruglevering']
        
    #     # **Stap 1**: Directe zonne-energie naar laadpalen
    #     stroom_aan_laadpalen = min(groene_stroom, laadpalen)
    #     resterende_groene_stroom = groene_stroom - stroom_aan_laadpalen  # Overgebleven groene stroom

    #     # **Stap 2**: Resterende groene stroom naar de batterij
    #     groene_stroom_naar_batterij = min(batterij_in, resterende_groene_stroom)
    #     groene_stroom_batterij += groene_stroom_naar_batterij

    #     # **Stap 3**: Aanvullen batterij met grijze stroom als er meer nodig is
    #     resterende_batterij_in = batterij_in - groene_stroom_naar_batterij
    #     grijze_stroom_naar_batterij = max(0, resterende_batterij_in)
    #     grijze_stroom_batterij += grijze_stroom_naar_batterij

    #     # **Stap 4**: Gebruik batterij (groen eerst, daarna grijs) voor teruglevering
    #     groene_stroom_uit_batterij = min(batterij_uit, groene_stroom_batterij)
    #     groene_stroom_batterij -= groene_stroom_uit_batterij

    #     resterende_batterij_uit = batterij_uit - groene_stroom_uit_batterij
    #     grijze_stroom_uit_batterij = min(resterende_batterij_uit, grijze_stroom_batterij)
    #     grijze_stroom_batterij -= grijze_stroom_uit_batterij

    #     # **Stap 5**: Gebruik batterij (groen eerst, dan grijs) voor laadpalen
    #     resterende_laadpalen = laadpalen - stroom_aan_laadpalen
    #     groene_stroom_uit_batterij_voor_laadpalen = min(resterende_laadpalen, groene_stroom_batterij)
    #     groene_stroom_batterij -= groene_stroom_uit_batterij_voor_laadpalen

    #     resterende_laadpalen -= groene_stroom_uit_batterij_voor_laadpalen
    #     grijze_stroom_uit_batterij_voor_laadpalen = min(resterende_laadpalen, grijze_stroom_batterij)
    #     grijze_stroom_batterij -= grijze_stroom_uit_batterij_voor_laadpalen

    #     # **Stap 6**: Bereken HBE (Groene energie gebruikt voor laadpalen)
    #     HBE_groen = stroom_aan_laadpalen + groene_stroom_uit_batterij_voor_laadpalen

    #     return HBE_groen

    # # Toepassen op de DataFrame
    # df['HBE'] = df.apply(bereken_HBE, axis=1)

    # Resultaten tonen in een verticale tabel zonder index
    st.write("### Resultaten")
    


    option = st.selectbox(
        'Hoe wil je de data zien?',
        ('Totaal', 'Per Jaar', 'Per Kwartaal', 'Per Maand')
    )


    # Functie om data te berekenen en te tonen
    def calculate_data(option):
        if option == 'Totaal':
            # Berekeningen
            somkWh = df['HBE'].sum()
            somkWk_Net = (df['laadpalen'].sum() - somkWh)
            HBE_Groen = somkWh * kWh_to_GJ * 4
            HBE_Net = somkWk_Net * kWh_to_GJ * 4 * 0.399
            Totaal = (HBE_Groen + HBE_Net) * prijs_HBE

            # Resultaten samenvatten in een dataframe
            results = {
                "Omschrijving": [
                    "Totale kWh Groen",
                    "Totale kWh Netlevering",
                    "Totale HBE Groen",
                    "Totale HBE Netlevering",
                    "Prijs per HBE",
                    "Totale winst (€)"
                ],
                "Waarde": [
                    f"{somkWh:0,.0f}",
                    f"{somkWk_Net:0,.0f}",
                    f"{HBE_Groen:0,.0f}",
                    f"{HBE_Net:0,.0f}",
                    f"{prijs_HBE:0,.2f}",
                    f"€{Totaal:0,.2f}"
                ]
            }
            # Resultaten tonen
            results_df = pd.DataFrame(results)
            st.write("Resultaten voor Totaal:")
            st.table(results_df)

        else:
            # Groeperen en berekenen per gekozen tijdsperiode
            if option == 'Per Jaar':
                df_grouped = df.resample('Y').sum()
            elif option == 'Per Kwartaal':
                df_grouped = df.resample('Q').sum()
            elif option == 'Per Maand':
                df_grouped = df.resample('M').sum()

            # Berekeningen per periode
            df_grouped['Totale kWh Groen'] = df_grouped['HBE']
            df_grouped['Totale kWh Net'] = df_grouped['laadpalen'] - df_grouped['HBE']
            df_grouped['Totale HBE Groen'] = df_grouped['Totale kWh Groen'] * kWh_to_GJ * 4
            df_grouped['Totale HBE Net'] = df_grouped['Totale kWh Net'] * kWh_to_GJ * 4 * 0.399
            df_grouped['Totale winst (€)'] = (df_grouped['Totale HBE Groen'] + df_grouped['Totale HBE Net']) * prijs_HBE

            # Afronden naar beneden
            df_grouped = round(df_grouped[['Totale kWh Groen', 'Totale kWh Net', 'Totale HBE Groen', 'Totale HBE Net', 'Totale winst (€)']].apply(np.floor),1)

            st.write(f"Resultaten per {option.lower()}:")
            st.write(df_grouped)



    # Berekening uitvoeren op basis van de keuze
    calculate_data(option)
else:
    # If no file is uploaded, show a message
    st.write("")


