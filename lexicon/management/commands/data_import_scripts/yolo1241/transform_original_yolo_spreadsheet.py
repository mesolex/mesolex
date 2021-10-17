import pandas as pd
from bs4 import BeautifulSoup
import re

PATH_TO_ORIGINAL_CSV = "Excel-nombres-indigenas_2021-10-07_Simplified-for-upload.csv"
PATH_TO_TOOLBOX_XML = "Descriptions-YM_2021-10-10.xml"
colnamepattern = re.compile("_([0-9]{5})[-_]")

with open(PATH_TO_TOOLBOX_XML) as f:
    soup = BeautifulSoup(f.read(), "lxml")

df = pd.read_csv(PATH_TO_ORIGINAL_CSV)
df = df.drop("Field recording UID", axis=1)
df = df.drop("Field recording summary (text from accompany archive)", axis=1)


rows = []
rejects = []

for soundgroup in soup.find_all("fn_soundgroup"):
    uid = soundgroup.find("uid").text
    summary = soundgroup.find("descrip")
    if summary is None:
        summary = ""
    else:
        summary = summary.text
    try:
        colname = re.findall(colnamepattern, soundgroup.find("fn_sound").text)[0]
    except Exception:
        rejects.append(soundgroup)
        continue
    row = {"Field recording UID": uid, "Field recording summary": summary, "Col. num.": colname}
    rows.append(row)

extra_df = pd.DataFrame(rows, columns=rows[0].keys())
df = df.merge(extra_df, how="left", on="Col. num.")

cols_rename = {}
for orig_col in df.columns:
    col = re.sub("( *\([^)]+\) *)|\.", "", orig_col)
    col = col.replace(" ", "_").lower()
    cols_rename[orig_col] = col

df = df.rename(columns=cols_rename)

genus_col = df.genus.tolist()
species_col = df.species.tolist()
genus_species_col = []
for g, s in zip(genus_col, species_col):
    if pd.isnull(s):
        gs = g
    elif pd.isnull(g):
        gs = s
    else:
        gs = ' '.join([g, s]).strip()
    genus_species_col.append(gs)

df['genus_species'] = genus_species_col

df.to_csv("yolo_data_ready_for_import.csv", index=False)