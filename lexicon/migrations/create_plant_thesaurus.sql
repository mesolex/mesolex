create table plant_synonyms(id SERIAL PRIMARY KEY, scientific_name TEXT NOT NULL, synonym TEXT NOT NULL);
copy plant_synonyms(scientific_name, synonym) from '/home/rpugh/repos/mesolex_api/mixtec_plant_pairs.txt' delimiter ':' CSV HEADER; /* <-- update the absolute path to the file before running */

