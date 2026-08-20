# pour installer mysql-connector
# pip install mysql-connector-python
import mysql.connector
import random
import string
import math
import time
import sys
# pour installer matplotlib :
# pip install matplotlib
import matplotlib.pyplot as plt

def connexion_mysql():
    # Fonction permettant d'établir la connexion à la base
    
    DB_CONFIG = {
        'host': 'le host de votre base',
        'user': 'le user de votre base',
        'password': 'le mot de passe de votre base',
        'database': 'le nom de votre base'
    }

    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        print(f"Connexion MySQL : OK")

    except mysql.connector.Error as err:
        print(f"connexion_mysql : Erreur MySQL : {err}")
        if conn and conn.is_connected():
            conn.close()    

    return conn

def calculer_score(texte, scores_bdd):
    score = 0.0
    
    #On découpe le texte en quadgrammes
    quadgrammes = [texte[i:i+4] for i in range(len(texte) - 3)]
    
    # pour chaque quadgramme du texte, on ajoute son score lu en mémoire dans scores_bdd
    # si le quadgramme n'existe pas en base et donc n'a pas été chargé en mémoire, on lui met une pénalité
    penalite = -8
    for q in quadgrammes:
        score += scores_bdd.get(q, penalite)
    
    return score

def trouver_position(grille, lettre):
    """ PLUS UTILISE """
    # Trouve la ligne et la colonne d'une lettre dans la grille.
    for l in range(5):
        for c in range(5):
            if grille[l][c] == lettre:
                return l, c
    return None

def supprimer_caractere_bourrage(texte):
    # Fonction pour enlever les caractères de bourrage (X) qui on été insérés
    # dans les digrammes contenants 2 fois la même lettre au moment du chiffrement
    resultat = []
    i = 0
    
    while i < len(texte):
        if (i+2 < len(texte) and texte[i] == texte[i+2] and texte[i+1] == 'X'):
            resultat.append(texte[i])
            resultat.append(texte[i+2])
            i += 3
        else:
            resultat.append(texte[i])
            i += 1
            
    return ''.join(resultat)

def dechiffrer_playfair(texte_chiffre, cle, alphabet):
    # Fonction de déchiffrement d'un message chiffré par Playfair.
    
    # On reconstruit la grile 5x5
    grille = [cle[i:i+5] for i in range(0, 25, 5)]
   
    # Découpage texte chiffré en digrammes
    digrammes = [texte_chiffre[i:i+2] for i in range(0, len(texte_chiffre), 2)]
    
    # Initialisation du texte déchiffré
    texte_dechiffre = []
    
    # Pour optimiser, on charge une fois les positions (lign, colonne) des lettres de la grille dans un dictionnaire
    positions = {}
    for lettre in alphabet:
        for l in range(5):
            for c in range(5):
                if grille[l][c] == lettre:
                    positions[lettre] = (l, c)

    # On parcourt chaque digramme
    for char1, char2 in digrammes:

        # On récupère les coordonnées ligne, colonne des 2 lettres du digramme
        l1, c1 = positions[char1]
        l2, c2 = positions[char2]

        # On applique les règle de Playfair pour déchiffrer
        if l1 == l2:
            # Même ligne -> Décalage vers la GAUCHE (-1)
            texte_dechiffre.append(grille[l1][(c1 - 1) % 5] + grille[l2][(c2 - 1) % 5])
        elif c1 == c2:
            # Même colonne -> Décalage vers le HAUT (-1)
            texte_dechiffre.append(grille[(l1 - 1) % 5][c1] + grille[(l2 - 1) % 5][c2])
        else:
            # Rectangle -> Identique au chiffrement (échange des colonnes)
            texte_dechiffre.append(grille[l1][c2] + grille[l2][c1])

    # Suppression des X de bourrage
    texte_clair = supprimer_caractere_bourrage("".join(texte_dechiffre))
    
    # Suppression du X final eventuel
    if texte_clair[-1] == 'X':
        texte_clair = texte_clair[:-1]
    
    return texte_clair

def initialiser_population(taille, alphabet, texte_chiffre, scores_bdd):
    # Fonction permettant de créer la première génération
    # en tirant les individus au hasard
    
    print("---> INITIALISATION DE LA POPULATION")
    
    # Chaque individu est stocké dans un dictionnaire avec son score
    population = {}
    
    # On boucle jusqu'à obtenir le nombre voulu de permutations uniques de 25 lettres (=1 individu)
    while len(population) < taille:
        # Génère une permutation aléatoire des lettres de l'alphabet
        # la fonction "sample" garantit qu'il n'y a pas 2 fois la même lettre
        candidat = "".join(random.sample(alphabet, len(alphabet)))
        
        # On vérifie si on n'a pas déjà ce candidat dans la population
        if candidat not in population:
            # On stocke la grille pour éviter les doublons
            # CE sera utile pour éviter d'explorer les mêmes individus au fil des générations
            historique_candidat.add(candidat)
        
            # On déchiffre le texte chiffré avec la grille candidate
            text_dechiffre = dechiffrer_playfair(texte_chiffre, candidat, alphabet)
        
            # On stocke le score du texte déchiffré dans le dictionnaire représentant la population
            population[candidat] = calculer_score(text_dechiffre, scores_bdd)
    
    return population

def calculer_ecart_type(generation, moyenne):
    # juste pour les stats ;)
    variance = sum((score - moyenne) ** 2 for score in generation.values()) / len(generation)
    return round(math.sqrt(variance), 2)

def afficher_info(index, generation, texte_chiffre, texte_clair, score_clair, alphabet):
    # Récupération du champion de la population :
    # on trie les items de la génération selon le score qui est le deuxième élément de l'item (donc index = 1)
    # Comme on trie en ordre décroissant (reverse=True) sur le score, il suffit de prendre le premier de la liste pour avoir le meilleur !
    meilleur_element, meilleur_score = sorted(generation.items(), key=lambda item: item[1], reverse=True)[:1][0]
    
    # On déchiffre pour avoir le texte clair correspondant au champion
    meilleur_texte_clair = dechiffrer_playfair(texte_chiffre, meilleur_element, alphabet)
    
    # Quelques mesures complémentaires... 
    score_population = round(sum(generation.values()), 2)
    moyenne_population = score_population / len(generation)
    ecart_type = calculer_ecart_type(generation, moyenne_population)
    pire_element, pire_score = sorted(generation.items(), key=lambda item: item[1])[:1][0]
    
    # Et on affiche tout ça
    print(f"Generation {i} : meilleur élément {meilleur_element}, meilleur score = {meilleur_score} ")
    print(f"population  : {len(generation)} score global = {score_population} score moyen = {round(moyenne_population,2)} pire score = {pire_score:2f} ecart-type = {ecart_type}")
    
    # On se limite à l'affichage des 30 premiers caractères pour éviter de remplir des écrans !!
    longueur_max_affichee = 30
    if len(texte_clair) > longueur_max_affichee:
        texte_clair = texte_clair[0:longueur_max_affichee] + "..."
    print(f"texte clair attendu  : {texte_clair} {score_clair}")
    
    if len(meilleur_texte_clair) > longueur_max_affichee:
        meilleur_texte_clair = meilleur_texte_clair[0:longueur_max_affichee] + "..."    
    print(f"meilleur texte clair : {meilleur_texte_clair}")
    
    # Enregistrement des données pour l'affichage graphique
    historique_gen.append(index)
    historique_max.append(meilleur_score)
    historique_std.append(ecart_type)
    
    # Mise à jour du graphique en direct (toutes les 5 générations pour ne pas ralentir) ---
    if i % 5 == 0:  # Mise à jour toutes les 5 générations
        line_max.set_data(historique_gen, historique_max)
        line_std.set_data(historique_gen, historique_std)
        
        # Réajustement automatique des échelles des axes
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
        
        # Pause minimale pour forcer le rafraîchissement d'affichage
        plt.pause(0.01)

def muter(individu):
    # Fonction en charge de faire muter un individu
    
    # Tirage au sort des 2 lettres à échanger
    lettres = random.sample(range(25), 2)    
    
    # Inversion des lettres
    individu_liste = list(individu)
    individu_liste[lettres[0]], individu_liste[lettres[1]] = individu_liste[lettres[1]], individu_liste[lettres[0]]
    individu_mute = "".join(individu_liste)
    
    return individu_mute
    
def echanger_lignes(individu): 
    # Fonction en charge d'échanger 2 lignes d'un individu
    
    # Tirage au sort des 2 lignes à échanger
    lignes = random.sample(range(5), 2)
    index_1 = lignes[0]*5
    index_2 = lignes[1]*5
    
    # Inversion des lignes
    individu_liste = list(individu)
    individu_liste[index_1:index_1 + 5], individu_liste[index_2:index_2 + 5] = individu_liste[index_2:index_2 + 5], individu_liste[index_1:index_1+ 5]
    individu_modifie = "".join(individu_liste)
    
    return individu_modifie
    
def echanger_colonnes(individu):   
    # Fonction en charge d'échanger 2 colonnes d'un individu
    
    # Tirage au sort des 2 colonnes a échanger
    colonnes = random.sample(range(5), 2)
    c1 = colonnes[0]
    c2 = colonnes[1]
    
    # Inversion des colonnes
    individu_liste = list(individu)
    individu_liste[c1], individu_liste[5+c1], individu_liste[10+c1], individu_liste[15+c1], individu_liste[20+c1], individu_liste[c2], individu_liste[5+c2], individu_liste[10+c2], individu_liste[15+c2], individu_liste[20+c2] = individu_liste[c2], individu_liste[5+c2], individu_liste[10+c2], individu_liste[15+c2], individu_liste[20+c2], individu_liste[c1], individu_liste[5+c1], individu_liste[10+c1], individu_liste[15+c1], individu_liste[20+c1]
    
    individu_modifie = "".join(individu_liste)
    
    return individu_modifie

# Activation du mode interactif de Matplotlib 
plt.ion()
fig, ax1 = plt.subplots(figsize=(10, 5))

# Axe 1 (Gauche) : Score Max
ax1.set_xlabel('Générations')
ax1.set_ylabel('Score Max', color='tab:blue')
line_max, = ax1.plot([], [], color='tab:blue', label='Score Max', linewidth=2)
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Axe 2 (Droite) : Écart-type (Partage le même axe X)
ax2 = ax1.twinx()
ax2.set_ylabel('Écart-type (Diversité)', color='tab:red')
line_std, = ax2.plot([], [], color='tab:red', label='Écart-type', linewidth=2) #linestyle='--')
ax2.tick_params(axis='y', labelcolor='tab:red')

plt.title("Progression de la convergence - Cryptanalyse Playfair")
fig.tight_layout()

# Listes pour stocker les données du graphique
historique_gen = []
historique_max = []
historique_std = []

# Connexion a la base de donnees
connexion_mysql = connexion_mysql()

# Chargement des scores des quadgrammes une seule fois et stockage en memoire
scores_bdd = {}

try:
    requete = "SELECT quadgramme, score FROM quadgramme"
    curseur = connexion_mysql.cursor(dictionary=True)
    curseur.execute(requete)
    
    # On lit toutes les données
    resultats = curseur.fetchall()
    
    # Et on les range dans un dictionnaire pratique à utiliser
    # grâce au "dictionary=True", on peut accéder aux colonnes de la table par leur nom
    scores_bdd = {ligne["quadgramme"]: ligne["score"] for ligne in resultats}

except mysql.connector.Error as err:
    print(f"Erreur MySQL : {err}")
    if curseur:
        curseur.close()
    if conn and conn.is_connected():
        conn.close()    

# Deconnexion de la base
if connexion_mysql and connexion_mysql.is_connected():
    connexion_mysql.close() 

if len(scores_bdd) == 0:
    print("Erreur au chargement des scores")
    sys.exit(0)

texte_chiffre = "PVNJPVADAEJZDFMOJZKZHMCZDOFAAXODKCSNCTABAKKOCNCOAEADBTZAOKYPBUKOPDPCEMOSCTGNODTPTAZPJZTCUFYNKYSJOBODKAREBTZATKXPJZTCCZBDZJOSKZSENSINPVCTHDGNDTCQYFPTJZOBTQTMTKTRYFBUDFDOREKZPXPYSTKOEMKRZJFANKOCOSKZGNJZDFPEXCSHZBEBSYOBINMEDTBZPCJNAKFACHBTZKSIJSEARIKNOCTPJDOSTNVXDOPEZPDKSEATKBDAEBSYOBXPYGCZJZPYSPKZSEDKQNAZSCDTSJODBTZADAPVGNPIKORONXSHBOJZDFPJGNYIYKEMSYDJMVOBPCAUCPOBOCOSEBHYOKGQDTTDEATMCAKOEMOSDFSEBOYFPVDTKOTATCOBTCTDQXDKPQKZXMCTJSCTEAPDHMCPJBKBUBJSKCSHAEAJMTQEKOODJCXPABINCMYFZTVXNSJQDKRYPYGYDKPZKYPDJBDPTDXTATDKAYEBSYOBPICKGNOBTQCPOBOCOSDFTCRDFCQMDTNXSHBOOKOKDQPEOSDAKCSHBFABUBJSINPDJSKOCAFAEMAUKFJSUFQMCTEAKVHY"

texte_clair = "QUOIQUECEDETAILNETOUCHEENAUCUNEMANIEREAUFONDMEMEDECEQUENOUSAVONSARACONTERILNESTPEUTETREPASINUTILENEFUTCEQUEPOURETREEXACTENTOUTDINDIQUERICILESBRUITSETLESPROPOSQUIAVAIENTCOURUSURSONCOMPTEAUMOMENTOUILETAITARRIVEDANSLEDIOCESEVRAIOUFAUXCEQUONDITDESHOMMESTIENTSOUVENTAUTANTDEPLACEDANSLEURVIEETSURTOUTDANSLEURDESTINEEQUECEQUILSFONTMMYRIELETAITFILSDUNCONSEILLERAUPARLEMENTDAIXNOBLESSEDEROBEONCONTAITDELUIQUESONPERELERESERVANTPOURHERITERDESACHARGELAVAITMARIEDEFORTBONNEHEUREADIXHUITOUVINGTANSSUIVANTUNUSAGEASSEZREPANDUDANSLESFAMILLESPARLEMENTAIRESCHARLESMYRIELNONOBSTANTCEMARIAGEAVAITDISAITONBEAUCOUPFAITPARLERDELUI"

# On stocke dans cette variable tous les candidats qui ont été essayés dans des générations passées
# histoire de ne pas explorer plusieurs fois le même élément
historique_candidat = set()

# On le calcule justre une fois dans un but d'affichage pour mesurer la progression de l'agorithme
score_clair = calculer_score(texte_clair, scores_bdd)

# PARAMETRES GENERAUX
taille_population = 600
max_generation = 400
max_stagnation = 10         # valeur à partir de laquelle on considère que la stagnation est grave et qu'il faut faire qq chose
taux_conservation = 0.3     # taux d'individu conservé lors des reset de population
alphabet = "ABCDEFGHIJKLMNOPQRSTUVXYZ"
taux_selection = 0.1        # taux d'individus conservés inchangés d'une génération à l'autre
taux_elite = 0.25 
taux_croisement = 1 - taux_selection - 3*taux_elite # On multiplie par 3 parce qu'un individu elite va donner 3 nouveaux individus

# Initialisation de la population
generation_courante = initialiser_population(taille_population, alphabet, texte_chiffre, scores_bdd)

# On mémorise le meilleurs score pour détecter les stagnations.
meilleur_score_precedent = max(generation_courante.values())

# On initialise le compteur de stagnation à 0
# Si on dépasse max_stagnation alors il faudra agir !!
nb_stagnation = 0

# Pour stocker la durée de création de chaque génération
durees = []

for i in range(max_generation):
    
    debut = time.perf_counter()
    
    # Affichage des infos de la population
    afficher_info(i, generation_courante, texte_chiffre, texte_clair, score_clair, alphabet)
    
    """ sélection des plus adaptés pour initialiser la prochaine génération """
    nb_selection = int(taille_population * taux_selection)
    liste_selectionnes = sorted(generation_courante.items(), key=lambda item: item[1], reverse=True)[:nb_selection]
    # par defaut, sort utilise le premier attribut pour trier 
    # mais on veut trier selon le score qui est le deuxieme attribut
    # donc on est obligé de préciser le paramètre key et de calculer la valeur avec une fonction anonyme (lambda)
    # cette fonction anonyme prend en paramètre l'item et renvoie le score (le deuxième attribut de l'item)
    
    # Initialisation de la generation suivante : transformation de la liste en dictionnaire
    generation_suivante = dict(liste_selectionnes)
    
    """ Gestion des mutations appliquées seulement sur l'élite de la population """
    # Les mutations et transformations "créatives" sont restreintes à l'élite
    # de façon à essayer de les améliorer
    nb_elite = int(taille_population * taux_elite)
    
    # On récupère juste l'élite en triant sur les meilleurs scores
    elites = sorted(generation_courante.items(), key=lambda item: item[1], reverse=True)[:nb_elite]
    
    # Chaque individu de l'élite va être muté et/ou transformé pour donner 3 nouveaux individus
    for individu_elite in elites:
        
        cle_elite = individu_elite[0]
        
        # On commence par la mutation
        mutation_terminee = False
        nb_tentative = 0
        while not mutation_terminee:
            nb_tentative += 1
            if nb_tentative == 20:
                # On a essayé 20 fois de créer un nouvel individu à partir de cle_elite
                # Mais malgré tous nos effort, on retombe à chaque fois sur un individus déjà exploré
                # dans une génération précédent... bon ben pour éviter de tourner en rond ad vitam,
                # on laisse tomber cet individu et on passe au suivant...
                
                print("risque de boucle mutation")
                
                # on abandonne cet individu
                break
            
            # Inversion des lettres
            cle_elite_mute = muter(cle_elite)
            
            # Vérification de l'existence de l'individu dans l'historique des individus déjà explorés
            if cle_elite_mute not in historique_candidat:
                
                # Puisqu'il n'y est pas, ben... on l'ajoute !
                historique_candidat.add(cle_elite_mute)
                
                # Calcul du score du nouvel individu
                texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_mute, alphabet)
                score = calculer_score(texte_dechiffre, scores_bdd) 
                
                # Ajout de l'individu muté dans la prochaine génération
                generation_suivante[cle_elite_mute] = score
                mutation_terminee = True
            else:
                # L'individu muté a déjà été exploré.
                # On le transforme à nouveau et lui appliquant au hasard une inversion de ligne ou de colonne
                if random.randint(0, 100) > 50:
                    # On échange les lignes
                    cle_elite_mute = echanger_lignes(cle_elite_mute)
                else:
                    # On échange les collonne
                    cle_elite_mute = echanger_colonnes(cle_elite_mute)
                
                # On vérifie à nouveau si l'individu obtenu a déjà été exploré                
                if cle_elite_mute not in historique_candidat:
                    # cool, il n'a pas encore été exploré
                    historique_candidat.add(cle_elite_mute)
                    
                    # Calcul du score du nouvel individu
                    texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_mute, alphabet)
                    score = calculer_score(texte_dechiffre, scores_bdd) 
                    
                    # Ajout de l'individu muté dans la prochaine generation
                    generation_suivante[cle_elite_mute] = score
                    mutation_terminee = True    

        # On applique l'échange de lignes sur l'élite
        echange_ligne_termine = False
        nb_tentative = 0
        while not echange_ligne_termine:
            nb_tentative += 1
         
            # Inversion de 2 lignes
            cle_elite_modifie = echanger_lignes(cle_elite)
            
            # Vérification de l'existence de l'individu dans l'historique des individus déjà explorés
            if cle_elite_modifie not in historique_candidat:
                # Il n'a pas encoré été exploré
                historique_candidat.add(cle_elite_modifie)

                # Calcul du score du nouvel individu
                texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_modifie, alphabet)
                score = calculer_score(texte_dechiffre, scores_bdd) 
                
                # Ajout de l'individu muté dans la prochaine generation
                generation_suivante[cle_elite_modifie] = score
                echange_ligne_termine = True
            else:
                # L'individu a déjà été exploré.
                # On le transforme à nouveau et lui appliquant au hasard une inversion de colonne ou une mutation
                if random.randint(0, 100) > 50:
                    # On fait une mutatiton
                    cle_elite_modifie = muter(cle_elite_modifie)
                else:
                    # On échange les collonnes
                    cle_elite_modifie = echanger_colonnes(cle_elite_modifie)
                
                    if cle_elite_modifie not in historique_candidat:
                        # Cette fois, c'est bon, il n'a pas été exploré
                        historique_candidat.add(cle_elite_modifie)

                        # Calcul du score du nouvel individu
                        texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_modifie, alphabet)
                        score = calculer_score(texte_dechiffre, scores_bdd) 
                        
                        # Ajout de l'individu muté dans la prochaine generation
                        generation_suivante[cle_elite_modifie] = score
                        echange_ligne_termine = True
          
            if nb_tentative == 20:
                # On a essayé 20 et on retombe à chaque fois sur un individu déjà exploré
                # On abandonne cet individu
                break

        # On applique l'échange de colonnes sur l'élite
        echange_colonne_termine = False
        nb_tentative = 0
        while not echange_colonne_termine:
            nb_tentative += 1
         
            # Inversion de 2 colonnes
            cle_elite_modifie = echanger_colonnes(cle_elite)
            
            # Vérification de l'existence de l'individu dans l'historique des individus déjà explorés
            if cle_elite_modifie not in historique_candidat:
                # Il n'a pas encoré été exploré
                historique_candidat.add(cle_elite_modifie)

                # Calcul du score du nouvel individu
                texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_modifie, alphabet)
                score = calculer_score(texte_dechiffre, scores_bdd) 
                
                # Ajout de l'individu muté dans la prochaine generation
                generation_suivante[cle_elite_modifie] = score
                echange_colonne_termine = True
            else:
                # L'individu a déjà été exploré.
                # On le transforme à nouveau et lui appliquant au hasard une inversion de lignes ou une mutation
                if random.randint(0, 100) > 50:
                    # On fait une mutatiton
                    cle_elite_modifie = muter(cle_elite_modifie)
                else:
                    # On échange les collonne
                    cle_elite_modifie = echanger_lignes(cle_elite_modifie)
                
                    if cle_elite_modifie not in historique_candidat:
                        # Il n'a pas encoré été exploré
                        historique_candidat.add(cle_elite_modifie)

                        # Calcul du score du nouvel individu
                        texte_dechiffre = dechiffrer_playfair(texte_chiffre, cle_elite_modifie, alphabet)
                        score = calculer_score(texte_dechiffre, scores_bdd) 
                        
                        # Ajout de l'individu muté dans la prochaine generation
                        generation_suivante[cle_elite_modifie] = score
                        echange_colonne_termine = True
          
            if nb_tentative == 20:
                 # On a essayé 20 et on retombe à chaque fois sur un individu déjà exploré
                # On abandonne cet individu
                break
    
    """ Gestion des croisements """
    nb_croisements = int(taille_population * taux_croisement)
    
    # on initialise un compteur des croisements effectués
    # un croisement peut être ignoré si l'enfant existe déjà dans l'historique des individus déjà explorés
    c = 0
    while c < nb_croisements:
        # Tirage au sort des parents
        mere, pere = random.sample(list(generation_courante.keys()), 2)
        
        # Creation de l'enfant
        enfant = ""
        
        # Recopie des 13 premières lettres de la mère
        for m in range(13):
            enfant += mere[m]
        
        # On complète avec les 12 dernières lettres dans l'ordre des lettres du père
        for p in range(len(pere)):
            if pere[p] not in enfant:
                enfant += pere[p]
 
        # Vérification de l'existence de l'enfant dans l'historique des individus déjà explorés
        if enfant not in historique_candidat:
            # L'enfant est bien un nouvel individu
            historique_candidat.add(enfant)
        else:
            # L'enfant a déjà un frère jumeau qui a été exploré
            # On passe au croisement suivant
            continue
            
        # Calcul du score de l'enfant
        texte_dechiffre = dechiffrer_playfair(texte_chiffre, enfant, alphabet)
        score = calculer_score(texte_dechiffre, scores_bdd) 
        
        # Ajout de l'enfant dans la prochaine génération
        generation_suivante[enfant] = score
        
        # Le croisement a été accepté, on incrémente le compteur
        c += 1
        
    """ Detection d'une stagnation """
    meilleur_score_courant = max(generation_suivante.values())
    if meilleur_score_courant > meilleur_score_precedent:
        # On progresse puisque le meilleur score augmente
        nb_stagnation = 0
        
        # Du coup, il faut mettre à jour le nouveau meilleur score
        meilleur_score_precedent = meilleur_score_courant
    else:
        # pas de progression : on stagne car le meilleur score reste inchangé
        nb_stagnation += 1
        
    if nb_stagnation >= max_stagnation:
        # On a atteint le nb max de stagnations tolérable, il faut prendre des mesures !!!
        print("STAGNATION DETECTEE !!!")
        
        # Et si on tuait une bonne partie de la population : reset de population ;)
        # Bon, on va quand même garder quelques individus : ceux avec le plus haut score bien sûr !
        nb_individus_conserves = int(taille_population * taux_conservation)
        liste_individus_conserves = sorted(generation_courante.items(), key=lambda item: item[1], reverse=True)[:nb_individus_conserves]
    
        # Initialisation de la génération suivante avec les individus conservés.
        generation_suivante = dict(liste_individus_conserves)

        # On augmente la taille de la population pour réduire le risque de stagnations futures. 
        # Peut-être qu'avec plus de monde à la recherche de la solution, l'algorithme convergera plus vite
        taille_population += 10
        
        # Remplissage du reste de la population avec des individus 100 % aléatoires -> ça c'est c'est du reset partiel de population !!
        while len(generation_suivante) < taille_population:
            # On tire au sort un candidat
            candidat = "".join(random.sample(alphabet, len(alphabet)))
   
            # On vérifie qu'on ne l'a pas déjà exploré
            if candidat not in historique_candidat:
                # c'est bon, on peut le conserver
                texte_dechiffre = dechiffrer_playfair(texte_chiffre, candidat, alphabet)
                generation_suivante[candidat] = calculer_score(texte_dechiffre, scores_bdd)
                historique_candidat.add(candidat)
            else:
                # Non déjà exploré -> bye !
                continue
        
        # Remise à zéro du compteur
        nb_stagnation = 0
    
    """ Passage a la prochaine generation """
    generation_courante = generation_suivante
    
    # Calcul du tempes de traitement
    fin = time.perf_counter()
    duree = fin - debut
    durees.append(duree)
    print(f"Temps d'exécution : {duree:.6f} secondes")
    print()

i += 1
afficher_info(i, generation_courante, texte_chiffre, texte_clair, score_clair, alphabet)

# Pour finir on veut afficher le texte clair obtenu avec le champion de la dernière génération
# donc d'abord, il faut trouvé le champion de la dernière génération
meilleur_element, meilleur_score = sorted(generation_courante.items(), key=lambda item: item[1], reverse=True)[:1][0]

# Et obtenir le text clair correspondant 
meilleur_texte_clair = dechiffrer_playfair(texte_chiffre, meilleur_element, alphabet)
print()
# Et l'afficher :)
print("Texte final déchiffré :")
print(meilleur_texte_clair)

temps_moyen = sum(durees) / len(durees)
print()
print(f"Temps moyen par génération : {temps_moyen}")

# Désactivation du mode interactif à la fin pour garder la fenêtre ouverte
plt.ioff()
plt.show()



