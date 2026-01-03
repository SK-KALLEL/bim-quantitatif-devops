import pandas as pd

# Chargement des données (utilise ton Excel ou un CSV)
df = pd.read_csv("tab_elements.SQL.csv")  # ou le nom de ton CSV

print(f"{len(df)} lignes chargées")

# Test 1 : total volume gros-œuvre > 100 m³
gros_oeuvre = df[df['type'].isin(['IfcWallStandardCase', 'IfcSlab'])]
total_volume_go = gros_oeuvre['volume_m3'].sum()
print(f"Total volume gros-œuvre : {total_volume_go:.2f} m³")
assert total_volume_go > 50, f"ERREUR : volume gros-œuvre trop faible ({total_volume_go:.2f} m³)"

# Test 2 : IfcSlab a la plus grande surface moyenne
surface_par_type = df.groupby('type')['surface_m2'].mean()
print("Surface moyenne par type :")
print(surface_par_type.round(2))
assert surface_par_type.get('IfcSlab', 0) == surface_par_type.max(), "ERREUR : IfcSlab n'a pas la plus grande surface moyenne"

# Test 3 : au moins 10 éléments avec volume > 0
elements_avec_volume = len(df[df['volume_m3'] > 0])
print(f"Éléments avec volume > 0 : {elements_avec_volume}")
assert elements_avec_volume >= 10, f"ERREUR : moins de 10 éléments avec volume ({elements_avec_volume})"

print("TOUS LES TESTS QUANTITATIFS PASSENT ✅")
