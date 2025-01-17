import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("btw25.tsv", sep="\t", quoting=3)

st.write("### Wahlprogramm-Heatmap")

# Dropdown for part-of-speech selection
pos_options = ["NN", "ADJ", "VV"]
selected_pos = st.selectbox("Wähle die Wortart aus:", pos_options)

st.write("Legende: NN = Substantiv, ADJ = Adjektiv, VV = Verb")

# Filter data based on the selected POS
df_filtered = df[df.pos.str.contains(selected_pos)]
df_grouped = df_filtered.groupby(by=["lemma", "party"]).size().reset_index(name="freq")
df_filtered = df_grouped[~df_grouped['lemma'].isin(["Freie", "Demokrat"])].copy()
df_filtered['relative_freq'] = df_filtered.groupby('party')['freq'].transform(lambda x: x / x.sum())

# Get top lemmas
top_lemmas_list = df_filtered.groupby('lemma')['relative_freq'].sum().nlargest(25).index
top_df = df_filtered[df_filtered['lemma'].isin(top_lemmas_list)]

# Create pivot table for heatmap
matrix = top_df.pivot_table(index='lemma', columns='party', values='relative_freq')
matrix = matrix.fillna(0)

# Plot heatmap
plt.figure(figsize=(3, 6))
sns.set_theme(style="whitegrid")
chart = sns.heatmap(data=matrix, annot=False, cmap="Reds")
st.pyplot(plt)

st.write("Die Heatmap zeigt die relativen Häufigkeiten für die 25 häufigsten Substantive je nach Partei.\nGerechnet wurde auf lemmatisierter Basis.\nDatengrundlage sind die Wahlprogramme zur Bundestagswahl 2025.")
st.write("Entwickelt von [Simon Meier-Vieracker](https://tu-dresden.de/gsw/slk/germanistik/al/die-professur/inhaber), Januar 2025.")
