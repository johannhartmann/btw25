import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime

today_date = datetime.today().strftime("%d.%m.%Y")

st.write("### Abfrage zur Worthäufigkeit in Wahlprogrammen (Beta)")
st.write(f"Ein Tool von [Simon Meier-Vieracker](https://tu-dresden.de/gsw/slk/germanistik/al/die-professur/inhaber), Stand {today_date}")

# UI for input
lemma = st.text_input("Suchwort eingeben (unflektierte Grundform): ")

# Load data
df = pd.read_csv("btw25.tsv", sep="\t", quoting=3)

# Group data by lemma and party
df_grouped = df.groupby(['lemma', 'party']).size().reset_index(name='freq')

def generate_kwic(df, query_lemma, selected_party, context_size=15, max_examples=10):
    # Filter the DataFrame for the query lemma and party
    filtered_df = df[(df["lemma"] == query_lemma) & (df["party"] == selected_party)].reset_index()

    # If there are fewer examples than max_examples, adjust the number of examples to the available count
    num_examples_to_select = min(len(filtered_df), max_examples)

    # Randomly sample the rows
    sampled_rows = filtered_df.sample(n=num_examples_to_select)

    kwic_examples = []
    for _, row in sampled_rows.iterrows():
        index = row['index']  # Get the current row index
        start = max(index - context_size, 0)  # Start of the context
        end = min(index + context_size + 1, len(df))  # End of the context

        # Extract tokens and indices for the context
        context_tokens = df.iloc[start:end]["token"].tolist()
        context_indices = df.iloc[start:end].index.tolist()

        # Highlight the query token
        kwic_line = " ".join(
            [f"**{token}**" if idx == index else token for token, idx in zip(context_tokens, context_indices)]
        )
        kwic_examples.append(kwic_line)

    return kwic_examples

if lemma:
    # Filter data for the input lemma
    df_lemma = df_grouped[df_grouped["lemma"] == lemma].reset_index(drop=True)
    df_size = pd.DataFrame(df["party"].value_counts(normalize=False))
    df_size = df_size.rename(columns={"party": "count"})
    df_lemma = pd.merge(df_lemma, df_size, on='party', how='outer')
    df_lemma["relfreq"] = df_lemma["freq"] / df_lemma["count"] * 1000000

    mean = (df_lemma["freq"].sum() / df_lemma["count"].sum() * 1000000)

    # Adjust the relfreq column to center around the mean
    df_lemma['relfreq_centered'] = df_lemma['relfreq'] - mean

    # Define party colors
    party_colors = {
        'AfD': '#00ccff',
        'BSW': '#cc1953',
        'CDU': '#2d3c4b',
        'FDP': '#ffed00',
        'Gruene': '#008939',
        'Linke': '#D675D8',
        'SPD': '#E3000F'
    }

    # Create an interactive bar plot using Plotly
    fig = px.bar(
        df_lemma,
        x="party",
        y="relfreq_centered",
        color="party",
        color_discrete_map=party_colors,
        labels={"relfreq_centered": "Differenz der relativen Häufigkeit"},
        title=f"Relative Häufigkeiten von '{lemma}'",
        hover_data={"freq": True, "relfreq": True, "relfreq_centered": False},
        custom_data=["relfreq","freq"]
    )

    fig.update_layout(
        #autosize=True,
        margin={"l": 40, "r": 40, "t": 60, "b": 00},
        title_y=.9,
        showlegend=False,
        xaxis=dict(
           tickangle=-45,
           title=""
        )
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"  # Party name
            "Relative Häufigkeit: %{customdata[0]:.2f}<br>"  # 'relfreq' formatted to 2 decimals
            "Absolute Häufigkeit: %{customdata[1]}"  # 'freq' displayed normally
        )
    )
    
    # Display the interactive plot
    st.plotly_chart(fig, use_container_width=True)

    party_options = list(df_lemma["party"].unique())

    default_party = "Gruene"  # Replace with your preferred default party

    # Capture user interaction
    clicked_party = st.selectbox(
        "Partei auswählen für eine Zufallsauswahl von max. 10 Belegen:",
        party_options,
        index=party_options.index(default_party))

    default_message = f"Showing KWIC examples for default party: {default_party}"

    kwic_output = generate_kwic(df, query_lemma=lemma, selected_party=clicked_party)

    if len(kwic_output) > 0:
        for example in kwic_output:
            st.write(example)
    else:
        st.write(f'Im Wahlprogramm dieser Partei kommt das Wort "{lemma}" nicht vor.')

with st.expander("Für Informationen zu diesem Tool hier klicken!"):
    st.write("""
    ## Daten und Methode

    Dieses interaktive Tool erlaubt die Abfrage von Worthäufigkeiten in den Wahlprogrammen zur Bundestagswahl 2025. Datengrundlage sind die (im Falle der AfD und der Linken vorläufigen) Wahlprogramme im PDF-Format, die in ein txt-Format überführt und manuell bereinigt wurden. Für die Korrektheit dieser Aufbereitung wird keine Garantie übernommen. Für die linguistische Vorverarbeitung (Tokenisierung und Lemmatisierung) wurde der TreeTagger genutzt.

    ### Wie zeigt das Diagramm und wie ist es zu lesen?
    
    Das Balkendiagramm zeigt die Differenz der relativen Häufigkeiten im Vergleich zum parteiübergreifenden Mittelwert. Zeigt also ein Balken beispielsweise nach oben, verwendet die Partei das Wort häufiger als der parteiübergreifende Durchschnitt; zeigt er nach unten, verwendet es das Wort seltener. 

    Es wird mit relativen Häufigkeiten (Treffer pro Millionen Wörter) gerechnet, um die Häufigkeiten auf die jeweils unterschiedlichen Umfänge der Wahlprogramme zu skalieren und so vergleichbar zu machen. Durch Anklicken der Balken kann aber auch die absolute Häufigkeit angezeigt werden.

    Bei der Interpretation muss man beachten, dass die An- und Abwesenheit von *Wörtern* nur zum Teil etwas über die Relevanz der mit diesen Wörtern bezeichneten *Themen* im jeweiligen Parteiprogramm aussagen kann. Für ein abschließendes Urteil ist ein Blick in die Originaltexte unumgänglich.

    **Es handelt sich um eine Testversion!** Feedback gerne an [simon.meier-vieracker@tu-dresden.de](mailto:simon.meier-vieracker@tu-dresden.de). Das Analyseskript kann auf GitHub eingesehen werden, Anpassungs- und Erweiterungsvorschläge sind sehr willkommen.
    """)
