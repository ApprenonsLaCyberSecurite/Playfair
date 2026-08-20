from collections import Counter
import mysql.connector
import unicodedata
import re


def connexion_mysql():
    conn = None
    
    DB_CONFIG = {
        'host': 'le host de votre base',
        'user': 'le user de votre base',
        'password': 'le mot de passe de votre base',
        'database': 'le nom de votre base'
    }
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Connexion Mysql OK !")
        
    except mysql.connector.Error as erreur:
        print(f"Connexion Mysql KO : {erreur}")
        if conn and conn.is_connected():
            conn.close()
            
    return conn


def nettoyer_texte(texte):
    texte = texte.upper().replace('Œ', 'OE').replace('Æ', 'AE').replace('Ç', 'C')

    texte_normalise = unicodedata.normalize('NFD', texte)
    sans_accent = ''.join(
        c for c in texte_normalise
        if unicodedata.category(c) != 'Mn'
    )
    
    return re.sub(r'[^A-Z]', '', sans_accent)

    
def analyser_livre(chemin_fichier, connexion_base):
    print(f"Analyse du fichier : {chemin_fichier}")
    
    with open(chemin_fichier, 'r', encoding='utf-8') as livre:
        texte = livre.read()
        texte_propre = nettoyer_texte(texte)
        quadgrammes = [texte_propre[i:i+4] for i in range(len(texte_propre)-3)]
        compteur = Counter(quadgrammes)
        
        sql_insert = """
        INSERT INTO quadgramme (quadgramme, occurrences)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE occurrences = occurrences + VALUES(occurrences);        
        """

        cursor = None
        
        try:
            cursor = connexion_base.cursor()
            donnees = list(compteur.items())
            cursor.executemany(sql_insert, donnees)
            connexion_base.commit()
            print(f"Succès : {len(donnees)} ont été insérées ou mises à jour")
        except mysql.connector.Error as erreur:
            print(f"Erreur MySQL : {erreur}")
        finally:
            if cursor:
                cursor.close()


def calculer_frequence_score(connexion_base):
    
    sql = """
        UPDATE quadgramme q
        CROSS JOIN (
            SELECT SUM(occurrences) AS total FROM quadgramme
        ) t
        SET
            q.frequence = q.occurrences / t.total,
            q.score = LOG10(q.occurrences / t.total)
     """

    cursor = None
        
    try:
        cursor = connexion_base.cursor()
        cursor.execute(sql)
    except mysql.connector.Error as erreur:
        print(f"Erreur MySQL : {erreur}")
    finally:
        if cursor:
            cursor.close()    
        
        
        

# Debut du programme

# connexion a Mysql
connexion_base = connexion_mysql()

analyser_livre("corpus/Balzac_LaComedieHumaine.txt", connexion_base)
analyser_livre("corpus/Flaubert_MadameBovary.txt", connexion_base)
analyser_livre("corpus/Gide_SouvenirsDeLaCoursDAssise.txt", connexion_base)
analyser_livre("corpus/Hugo_LesMiserables_Tome1.txt", connexion_base)
analyser_livre("corpus/Maupassant_BouleDeSuif.txt", connexion_base)
analyser_livre("corpus/Rathenau_OuVaLeMonde.txt", connexion_base)

calculer_frequence_score(connexion_base)

# deconnexion de Mysql
if connexion_base and connexion_base.is_connected():
    connexion_base.close()