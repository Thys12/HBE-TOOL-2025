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

# Uitleg over de werking van HBE-O Elektriciteit
st.markdown("""
### Hoe werkt HBE-O Elektriciteit?

1. **Productie van Hernieuwbare Elektriciteit**: Elektriciteit die wordt opgewekt uit hernieuwbare bronnen zoals wind, zon, waterkracht of biomassa komt in aanmerking voor HBE's. Elektriciteitsproducenten kunnen hun duurzame energieproductie aanmelden bij de Nederlandse Emissieautoriteit (NEa) om in aanmerking te komen voor HBE-O Elektriciteit.

2. **Toekenning van HBE's**: Voor elke eenheid (bijvoorbeeld megawattuur, MWh) hernieuwbare elektriciteit die wordt geleverd aan elektrische voertuigen, ontvangen de producenten HBE-O Elektriciteit. Deze eenheden kunnen worden toegekend aan laadstations, leveranciers van stroom aan EV's, of partijen die betrokken zijn bij de opslag en distributie van elektriciteit voor transport.

3. **Handel in HBE's**: Net als andere HBE's kunnen HBE-O Elektriciteit-certificaten worden verhandeld op de markt. Bedrijven zoals olie- en gasmaatschappijen, die wettelijk verplicht zijn om een bepaald percentage hernieuwbare energie in hun brandstofmix te hebben, kunnen deze certificaten kopen om te voldoen aan hun verplichtingen.

4. **Stimulering van Elektrisch Rijden**: Het verkrijgen van HBE-O Elektriciteit moedigt investeringen aan in hernieuwbare energie-infrastructuur, zoals laadpalen en slimme netwerken, die nodig zijn om de groei van elektrisch rijden te ondersteunen.
""")

# Conclusie
st.markdown("### Data exporteren uit fudura")

uploaded_file = st.file_uploader("Upload je dataset (CSV of Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Stap 1: Inlezen van dataset
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Voorbeeld van de dataset:")
    st.dataframe(df.head())

    # Stap 2: Kolommen selecteren
    st.write("### Toewijzing van kolommen")
    df.columns = df.columns.str.strip().str.replace("\n", " ", regex=True)
    kolommen = df.columns.tolist()

    tijdstip = st.selectbox("Kolom voor tijdstip:", kolommen)
    groene_stroom = st.multiselect("Kolommen voor groene stroom:", kolommen)
    net_in = st.selectbox("Kolom voor net verbruik:", kolommen)
    net_uit = st.selectbox("Kolom voor net teruglevering:", kolommen)
    batterij_verbruik = st.selectbox("Kolom voor batterij verbruik:", kolommen)
    batterij_teruglevering = st.selectbox("Kolom voor batterij teruglevering:", kolommen)
    laadpalen = st.multiselect("Kolommen voor laadpalen:", kolommen)

    # Tijd kolom   
    df1 = df[[tijdstip]].copy()
    df[tijdstip] = pd.to_datetime(df[tijdstip], errors='coerce')

    # Groene stroom en laadpalen sommeren
    df1["Groene_Stroom"] = df[groene_stroom].sum(axis=1) if groene_stroom else 0    
    df1["Laadpalen"] = df[laadpalen].sum(axis=1) if laadpalen else 0

    # Enkele kolommen toewijzen
    df1["Net_Verbruik"] = df[net_in] if net_in in df.columns else 0
    df1["Net_Teruglevering"] = df[net_uit] if net_uit in df.columns else 0
    df1["Batterij_Verbruik"] = df[batterij_verbruik] if batterij_verbruik in df.columns else 0
    df1["Batterij_Teruglevering"] = df[batterij_teruglevering] if batterij_teruglevering in df.columns else 0

    df1.set_index(tijdstip, inplace=True)
    # Debugging: Toon df1 na toewijzing
    st.write("Data na kolomtoewijzing:")
    df1 = df1.drop(df1.index[-1])
    df1 = df1.drop(df1.index[-1])
    df1 = df1.drop(df1.index[-1])
    
    st.dataframe(df1.head(10))

    # Verbruik gebouw berekenen
    def verbruik_gebouw(row):
        Verbruik = row["Net_Verbruik"] - row["Batterij_Verbruik"]
        Teruglevering = row["Batterij_Teruglevering"] - row["Net_Teruglevering"]
        GroeneStroom = row["Groene_Stroom"]
        Laadpalen = row["Laadpalen"]

        if Verbruik <= 0 and Teruglevering <= 0:
            return GroeneStroom - abs(Verbruik) - abs(Teruglevering) - Laadpalen
        elif Verbruik <= 0 and Teruglevering > 0:
            return GroeneStroom - abs(Verbruik) + abs(Teruglevering) - Laadpalen
        elif Verbruik > 0 and Teruglevering <= 0:
            return GroeneStroom + abs(Verbruik) - abs(Teruglevering) - Laadpalen
        else:
            return GroeneStroom + abs(Verbruik) + abs(Teruglevering) - Laadpalen

    df1["Verbruik_Gebouw"] = df1.apply(verbruik_gebouw, axis=1)

    # Maak de figuur
    fig = go.Figure()

    # Voeg elke lijn toe aan de figuur
    for column in df1.columns:
        fig.add_trace(go.Scatter(x=df1.index, y=df1[column], mode='lines', name=column))

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
        laadpalen = row['Laadpalen']
        
        # Directe zonne-energie HBE's
        HBE_direct = min(groene_stroom, laadpalen)

        return HBE_direct

    df1['HBE'] = df1.apply(calculate_HBEs, axis=1)

    # Resultaten tonen in een verticale tabel zonder index
    st.write("### Resultaten")
    df1.index = pd.to_datetime(df1.index)
    option = st.selectbox(
        'Hoe wil je de data zien?',
        ('Totaal', 'Per Jaar', 'Per Kwartaal', 'Per Maand')
    )

    print(df1.index)
    lijst = [7.200,7.200,21.600,21.600,21.600,28.800,14.400]# maand 4/10
    lijst_mwh = [0,0,0,2,2,6,6,6,8,4,13,5]

    # Functie om data te berekenen en te tonen
    def calculate_data(option):
        if option == 'Totaal':
            # Berekeningen
            somkWh = df1['HBE'].sum()
            somkWk_Net = (df1['Laadpalen'].sum() - somkWh)
            HBE_Groen = somkWh * kWh_to_GJ * 4
            HBE_Net = somkWk_Net * kWh_to_GJ * 4 * 0.399
            Totaal = (HBE_Groen + HBE_Net) * prijs_HBE

            # Resultaten samenvatten in een dataframe
            results = {
                "Omschrijving": [
                    "Totale kWh aan GVO",
                    "Totale kWh Groen",
                    "Totale kWh Netlevering",
                    "Totale HBE Groen",
                    "Totale HBE Netlevering",
                    "Prijs per HBE",
                    "Totale winst (€)"
                ],
                "Waarde": [
                    f"{52000:0,.0f}",
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
                df_grouped = df1.resample('Y').sum()
            elif option == 'Per Kwartaal':
                df_grouped = df1.resample('Q').sum()
            elif option == 'Per Maand':
                df_grouped = df1.resample('M').sum()

            # Berekeningen per periode
            df_grouped['Totale kWh Groen'] = df_grouped['HBE']
            df_grouped['Totale kWh Net'] = df_grouped['Laadpalen'] - df_grouped['HBE']
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


