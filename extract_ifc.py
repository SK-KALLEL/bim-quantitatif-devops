import ifcopenshell
import psycopg2

# Chemin vers ton fichier IFC
ifc_path = r"C:\Users\Skander\Desktop\FOMRMATION DATA-BIM\EXERCICES\Automatisation AI - Autoformation\EX 1 refaire\AC20-FZK-Haus.ifc"

# Connexion à PostgreSQL
conn = psycopg2.connect(
    dbname="bim_ifc de GITHUB",
    user="postgres",
    password="147",  # ton mot de passe
    host="localhost",
    port="5432"
)
cur = conn.cursor()

print("Connexion à PostgreSQL réussie !")
print("Fichier IFC chargé :", ifc_path)
# Ouverture du fichier IFC
ifc_file = ifcopenshell.open(ifc_path)

# Insertion du projet dans la table tab_projets
cur.execute("""
    INSERT INTO tab_projets (name, description, file_name)
    VALUES ('FZK-Haus Test', 'Maquette test pour exercice BIM', 'AC20-FZK-Haus.ifc')
    RETURNING id
""")

# Récupération de l'ID du projet qu'on vient d'insérer
project_id = cur.fetchone()[0]
# Vide la table tab_elements pour éviter les doublons (pour les tests)
cur.execute("DELETE FROM tab_elements WHERE project_id = %s", (project_id,))
conn.commit()
print("Table tab_elements vidée pour ce projet")

# Validation de l'insertion
conn.commit()

print(f"Projet inséré avec succès ! ID = {project_id}")
# Extraction de TOUS les éléments physiques (version complète)
# Fonction pour récupérer les quantités du Qto (plus fiable)
def get_quantity(elem, qty_names):
    for rel in elem.IsDefinedBy:
        if rel.is_a("IfcRelDefinesByProperties"):
            prop_set = rel.RelatingPropertyDefinition
            if prop_set.is_a("IfcElementQuantity"):
                for qty in prop_set.Quantities:
                    if qty.Name in qty_names:
                        if qty.is_a("IfcQuantityVolume"):
                            return qty.VolumeValue or 0
                        if qty.is_a("IfcQuantityArea"):
                            return qty.AreaValue or 0
    return 0

# Extraction de TOUS les éléments avec quantités du Qto
elements = ifc_file.by_type("IfcElement")
print(f"{len(elements)} éléments physiques trouvés")

for elem in elements:
    elem_type = elem.is_a()
    
    # Niveau
    level = "Niveau inconnu"
    if elem.ContainedInStructure and elem.ContainedInStructure[0].RelatingStructure:
        level = elem.ContainedInStructure[0].RelatingStructure.Name or "Niveau inconnu"
    
    # Quantités (plusieurs noms possibles)
    volume = get_quantity(elem, ["NetVolume", "GrossVolume"])
    surface = get_quantity(elem, ["NetSideArea", "GrossSideArea", "NetFloorArea", "GrossFootprintArea"])
    
    cur.execute("""
        INSERT INTO tab_elements (project_id, global_id, name, type, level, volume_m3, surface_m2, corps_etat)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'À définir')
    """, (
        project_id,
        elem.GlobalId,
        elem.Name or "Sans nom",
        elem_type,
        level,
        volume,
        surface
    ))

conn.commit()
print("Tous les éléments insérés avec quantités réelles !")

# Fermeture propre
cur.close()
conn.close()
print("Connexion fermée. Script terminé.")