import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Load data
df = pd.read_csv("btw25_corrected.tsv", sep="\t", quoting=3)

today_date = datetime.today().strftime("%d.%m.%Y")

st.write("### Wahlprogramm-Heatmaps zur Bundestagswahl 2025")

st.write("Diese Heatmaps zeigen für verschiedene Wortarten die relativen Häufigkeiten für die 25 häufigsten Wörter in den Wahlprogrammen der jeweiligen Partei.")

st.caption(f"Ein Tool von [Simon Meier-Vieracker](https://tu-dresden.de/gsw/slk/germanistik/al/die-professur/inhaber), Stand {today_date}. Bitte beachten Sie die Infobox am Ende dieser Seite.")

number_of_rows = st.slider("Wieviele Wörter sollen angezeigt werden?", 25, 50, 25)

pos_dict = {
	"Substantive":"NN",
	"Adjektive":"ADJ",
	"Verben":"VV"
}

def create_heatmap(df, selected_pos, number_of_rows):
	df_filtered = df[df.pos.str.contains(pos_dict[selected_pos])]
	df_grouped = df_filtered.groupby(by=["lemma", "party"]).size().reset_index(name="freq")
	df_filtered = df_grouped[~df_grouped['lemma'].isin(["Freie", "Demokrat"])].copy()
	df_filtered['rel_freq'] = df_filtered.groupby('party')['freq'].transform(lambda x: x / x.sum() * 100)

	# Get top lemmas
	top_lemmas_list = df_filtered.groupby('lemma')['rel_freq'].sum().nlargest(number_of_rows).index
	top_df = df_filtered[df_filtered['lemma'].isin(top_lemmas_list)]

	# Create pivot table for heatmap
	matrix = top_df.pivot_table(index='lemma', columns='party', values='rel_freq')
	matrix = matrix.fillna(0)

	matrix_table = top_df.pivot_table(index='lemma', columns='party', values='freq')
	matrix_table = matrix_table.fillna(0)

	plot_height = .24 * number_of_rows
	
	plt.figure(figsize=(3, plotheight))
	sns.set_theme(style="whitegrid")
	chart = sns.heatmap(data=matrix, annot=False, cmap="Reds")
	chart.set_xlabel('')
	chart.set_ylabel('')
	st.pyplot(plt)

	with st.expander("Absolute Frequenzen anzeigen"):
		st.dataframe(matrix_table)

#	return matrix, matrix_table 

tabs = ["Substantive", "Adjektive", "Verben"]
tab_objects = st.tabs(tabs)

for tab, pos in zip(tab_objects, tabs):
    with tab:
        create_heatmap(df, pos, number_of_rows)

with st.expander("Für Informationen zu diesem Tool hier klicken!"):
    st.write("""
    ### Daten und Methode

    Die Heatmaps zeigen die relativen Häufigkeiten jener 25 Wörter, die über alle Wahlprogramme zur Bundestagswahl 2025 hinweg am häufigsten vorkommen. Datengrundlage sind die (im Falle der AfD und der Linken vorläufigen) Wahlprogramme im PDF-Format, die in ein txt-Format überführt und manuell bereinigt wurden. Für die Korrektheit dieser Aufbereitung wird keine Garantie übernommen. Berücksichtigt wurden nur Parteien, die im letzten Bundestag vertreten waren und/oder realistische Chancen auf Einzug in den nächsten haben. 

    Für die linguistische Vorverarbeitung (Tokenisierung, Lemmatisierung und Part-of-Speech-Tagging) wurde der TreeTagger genutzt. Die Auswertung beruht auf lemmatisierter Basis, d.h. flektierte Formen wurden in die Grundform überführt. Abgetrennte Partikelverbzusätze (etwa in "lehnen wir ab") wurden nachträglich wieder angefügt.

    **Warum relative Häufigkeiten?**

    Um die unterschiedlich langen Wahlprogramme untereinander vergleichbar zu machen, werden für die Heatmap die absoluten Häufigkeiten normalisiert und in Prozentwerten angegeben. Unter der Heatmap lassen sich aber auch die absoluten Häufigkeiten in Tabellenform anzeigen.

    **Wichtig**: Bei der Interpretation muss man beachten, dass die Häufigkeit von *Wörtern* nur zum Teil etwas über die Relevanz der mit diesen Wörtern bezeichneten *Themen* in den jeweiligen Wahlprogrammen aussagen kann. Natürlich ist auch der Kontext wichtig, in dem eine Partei ein Wort jeweils verwendet. [In einem anderen Tool](https://btw25frequencies.streamlit.app/) können für einzelne Wörter gezielt die Häufigkeiten abgefragt und Belege für die Verwendung im Kontext angezeigt werden. Für ein abschließendes Urteil ist außerdem ein Blick in die originalen Wahlprogramme unumgänglich.

    **Es handelt sich um eine Testversion!** Feedback gerne an [simon.meier-vieracker@tu-dresden.de](mailto:simon.meier-vieracker@tu-dresden.de). Das Analyseskript kann auf GitHub eingesehen werden, Anpassungs- und Erweiterungsvorschläge sind sehr willkommen.
    """)
