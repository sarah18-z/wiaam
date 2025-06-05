import random
import copy
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math

# --- Données machines (Complétées) ---
machines_template = {
    "Usinage": [{"nom": "M1-Usinage", "libre": 0}, {"nom": "M2-Usinage", "libre": 0}],
    "Culasse": [{"nom": "M1-Culasse", "libre": 0}, {"nom": "M2-Culasse", "libre": 0}],
    "Injection": [{"nom": "M1-Inj", "libre": 0}, {"nom": "M2-Inj", "libre": 0}],
    "BEM": [{"nom": "M1-BEM", "libre": 0}, {"nom": "M2-BEM", "libre": 0}],
    "Peinture": [{"nom": "M1-Peinture", "libre": 0}, {"nom": "M2-Peinture", "libre": 0}]
}

# --- Données ORs (Complétées) ---
# Note: J'ai ajouté des poids 'poids' par défaut à 1 pour chaque OR.
# Ce poids est utilisé dans la fonction de fitness pour les retards pondérés (Wj * Tj).
ORs_data_full = [
    {
        "nom": "OR1", "delai": 20, "poids": 1,
        "taches": [
            {"nom": "Demontage", "duree": 2, "machine": None},
            {"nom": "Usinage", "duree": 3, "machine": "Usinage"},
            {"nom": "Preparation", "duree": 1, "machine": None},
            {"nom": "Culasse", "duree": 3, "machine": "Culasse"},
            {"nom": "Injection", "duree": 2, "machine": "Injection"},
            {"nom": "Sous-Organe", "duree": 1, "machine": None},
            {"nom": "Montage", "duree": 2, "machine": None},
            {"nom": "BEM", "duree": 3, "machine": "BEM"},
            {"nom": "Peinture", "duree": 2, "machine": "Peinture"}
        ]
    },
    {
        "nom": "OR2", "delai": 15, "poids": 1,
        "taches": [
            {"nom": "Demontage", "duree": 2, "machine": None},
            {"nom": "Usinage", "duree": 3, "machine": "Usinage"},
            {"nom": "Preparation", "duree": 1, "machine": None},
            {"nom": "Culasse", "duree": 3, "machine": "Culasse"},
            {"nom": "Injection", "duree": 2, "machine": "Injection"},
            {"nom": "Sous-Organe", "duree": 1, "machine": None},
            {"nom": "Montage", "duree": 2, "machine": None},
            {"nom": "BEM", "duree": 3, "machine": "BEM"},
            {"nom": "Peinture", "duree": 2, "machine": "Peinture"}
        ]
    },
    {
        "nom": "OR3", "delai": 22, "poids": 1,
        "taches": [
            {"nom": "Demontage", "duree": 3, "machine": None},
            {"nom": "Usinage", "duree": 4, "machine": "Usinage"},
            {"nom": "Preparation", "duree": 2, "machine": None},
            {"nom": "Culasse", "duree": 4, "machine": "Culasse"},
            {"nom": "Injection", "duree": 3, "machine": "Injection"},
            {"nom": "Sous-Organe", "duree": 1, "machine": None},
            {"nom": "Montage", "duree": 3, "machine": None},
            {"nom": "BEM", "duree": 4, "machine": "BEM"},
            {"nom": "Peinture", "duree": 3, "machine": "Peinture"}
        ]
    },
    {
        "nom": "OR4", "delai": 18, "poids": 1,
        "taches": [
            {"nom": "Demontage", "duree": 2, "machine": None},
            {"nom": "Usinage", "duree": 3, "machine": "Usinage"},
            {"nom": "Preparation", "duree": 1, "machine": None},
            {"nom": "Culasse", "duree": 3, "machine": "Culasse"},
            {"nom": "Injection", "duree": 2, "machine": "Injection"},
            {"nom": "Sous-Organe", "duree": 1, "machine": None},
            {"nom": "Montage", "duree": 2, "machine": None},
            {"nom": "BEM", "duree": 3, "machine": "BEM"},
            {"nom": "Peinture", "duree": 2, "machine": "Peinture"}
        ]
    },
    {
        "nom": "OR5", "delai": 25, "poids": 1,
        "taches": [
            {"nom": "Demontage", "duree": 1, "machine": None},
            {"nom": "Usinage", "duree": 3, "machine": "Usinage"},
            {"nom": "Preparation", "duree": 1, "machine": None},
            {"nom": "Culasse", "duree": 2, "machine": "Culasse"},
            {"nom": "Injection", "duree": 1, "machine": "Injection"},
            {"nom": "Sous-Organe", "duree": 1, "machine": None},
            {"nom": "Montage", "duree": 2, "machine": None},
            {"nom": "BEM", "duree": 2, "machine": "BEM"},
            {"nom": "Peinture", "duree": 2, "machine": "Peinture"}
        ]
    }
]

# --- Fonctions utilitaires ---

def calculer_makespan_et_retards(or_sequence_dict_list, machines_template_arg):
    """
    Calcule le makespan et les retards pour une séquence d'ORs donnée.
    Renvoie également le temps de fin de chaque OR pour le calcul des retards.
    """
    machines = copy.deepcopy(machines_template_arg)
    temps_manuelles = {"Demontage": 0, "Preparation": 0, "Sous-Organe": 0, "Montage": 0, 
                    "Essai": 0, "Confection": 0, "Controle": 0}   
    makespan = 0
    retards_values = {} # {OR_nom: retard_valeur}
    OR_fin_times = {} # {OR_nom: temps_fin}

    for OR in or_sequence_dict_list:
        current_time_for_OR = 0 # Temps écoulé pour cet OR
        for tache in OR["taches"]:
            task_start_time = 0
            task_end_time = 0
           
            if tache["machine"]:
                machines_dispo = machines[tache["machine"]]
                # Trouver la machine la plus tôt disponible
                # C'est la machine dont le temps libre est le plus faible, mais doit aussi être >= current_time_for_OR
                machine_found = min(machines_dispo, key=lambda m: max(m["libre"], current_time_for_OR))
               
                task_start_time = max(machine_found["libre"], current_time_for_OR)
                task_end_time = task_start_time + tache["duree"]
                machine_found["libre"] = task_end_time # Mettre à jour le temps libre de la machine
            else: # Tâches manuelles
                task_start_time = max(temps_manuelles[tache["nom"]], current_time_for_OR)
                task_end_time = task_start_time + tache["duree"]
                temps_manuelles[tache["nom"]] = task_end_time # Mettre à jour le temps libre de la ressource manuelle
           
            current_time_for_OR = task_end_time # Le temps de fin de la tâche devient le temps de début de la suivante pour cet OR
       
        OR_fin_times[OR["nom"]] = current_time_for_OR
        retard = max(0, current_time_for_OR - OR["delai"]) # Retard est 0 si en avance
        retards_values[OR["nom"]] = retard
       
        makespan = max(makespan, current_time_for_OR)
           
    return makespan, retards_values, OR_fin_times

def evaluer_sequence(or_sequence_dict_list, machines_template_arg):
    """
    Évalue une séquence d'ORs et renvoie le makespan et l'ordonnancement détaillé.
    Similaire à calculer_makespan_et_retards mais capture plus de détails.
    """
    machines = copy.deepcopy(machines_template_arg)
    temps_manuelles = {"Demontage": 0, "Preparation": 0, "Sous-Organe": 0, "Montage": 0,
                    "Essai": 0, "Confection": 0, "Controle": 0}
    makespan = 0
    ordonnancement_detail = []
   
    for OR in or_sequence_dict_list:
        current_time_for_OR = 0
        for tache in OR["taches"]:
            debut = 0
            fin = 0
            nom_machine = ""

            if tache["machine"]:
                machines_dispo = machines[tache["machine"]]
                machine = min(machines_dispo, key=lambda m: max(m["libre"], current_time_for_OR))
                debut = max(machine["libre"], current_time_for_OR)
                fin = debut + tache["duree"]
                machine["libre"] = fin
                nom_machine = machine["nom"]
            else:
                debut = max(temps_manuelles[tache["nom"]], current_time_for_OR)
                fin = debut + tache["duree"]
                temps_manuelles[tache["nom"]] = fin
                nom_machine = "Manuelle"
           
            ordonnancement_detail.append({
                "OR": OR["nom"],
                "Tache": tache["nom"],
                "Machine": nom_machine,
                "Debut": debut,
                "Fin": fin
            })
            current_time_for_OR = fin
        makespan = max(makespan, current_time_for_OR)
   
    return makespan, ordonnancement_detail

# --- Affichage et Tracé ---
def afficher_ordonnancement(ordonnancement_detail):
    """Affiche l'ordonnancement détaillé dans un tableau textuel."""
    print(f"\n{'OR':<5} | {'Tâche':<12} | {'Machine':<15} | {'Début':<6} | {'Fin':<6} | {'Durée':<6}")
    print("-"*70)
    current_or = None
    for t in ordonnancement_detail:
        if t["OR"] != current_or:
            if current_or is not None:
                print("-"*70)
            current_or = t["OR"]
        duree = t["Fin"] - t["Debut"]
        print(f"{t['OR']:<5} | {t['Tache']:<12} | {t['Machine']:<15} | {t['Debut']:<6} | {'%s' % t['Fin'] if t['Fin'] is not None else '':<6} | {duree:<6}")
    print("-"*70)

def tracer_diagramme_gantt(ordonnancement_detail):
    """Trace le diagramme de Gantt pour l'ordonnancement détaillé."""
    ORs_unique = sorted(list(set(t['OR'] for t in ordonnancement_detail)))
    or_to_y = {or_name: i for i, or_name in enumerate(ORs_unique)}

    taches_unique = list(set(t['Tache'] for t in ordonnancement_detail))
    couleurs = {}
    random.seed(42) # Pour des couleurs reproductibles
    for tache in taches_unique:
        couleurs[tache] = (random.random(), random.random(), random.random())
   
    fig, ax = plt.subplots(figsize=(12, 6))
   
    for t in ordonnancement_detail:
        y = or_to_y[t['OR']]
        start = t['Debut']
        duree = t['Fin'] - t['Debut']
        couleur = couleurs[t['Tache']]
       
        ax.barh(y, duree, left=start, height=0.4, color=couleur, edgecolor='black')
        ax.text(start + duree/2, y, t['Tache'], va='center', ha='center', fontsize=8, color='black')
   
    ax.set_yticks(range(len(ORs_unique)))
    ax.set_yticklabels(ORs_unique)
    ax.invert_yaxis()
    ax.set_xlabel('Temps')
    ax.set_title('Diagramme de Gantt des ORs et Tâches')
    ax.grid(axis='x', linestyle='--', alpha=0.7)
   
    patches = [mpatches.Patch(color=couleurs[t], label=t) for t in taches_unique]
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')
   
    plt.tight_layout()
    plt.show()


# ---
# ## Classe Algorithme Génétique
# ---

class GeneticAlgorithmORs:
    def __init__(self, ORs_data, machines_template, alpha=0.5,
                 pop_size=50, generations=200, elitism_rate=0.1,
                 crossover_prob=0.8, mutation_prob=0.1, max_k_mutations=2,
                 max_stagnation_generations=50, epsilon_stagnation=0.1):
       
        self.ORs_data = ORs_data
        self.machines_template = machines_template
        self.alpha = alpha # Paramètre pour la fonction de fitness
       
        self.pop_size = pop_size
        self.generations = generations
        self.elitism_rate = elitism_rate
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.max_k_mutations = max_k_mutations
       
        self.max_stagnation_generations = max_stagnation_generations
        self.epsilon_stagnation = epsilon_stagnation # Seuil d'amélioration minimale
       
        self.best_overall_solution = None
        self.best_overall_fitness = -float('inf') # Maximisation du fitness
        self.best_overall_makespan = float('inf') # Minimisation du makespan

    def _calculate_fitness(self, or_sequence_dict_list):
        """
        Calcule la valeur de fitness pour une séquence donnée.
        Fitness = 1 / (alpha * Makespan + (1 - alpha) * somme(Wj * Tj))
        """
        makespan, retards_values, _ = calculer_makespan_et_retards(or_sequence_dict_list, self.machines_template)
       
        sum_wj_tj = 0
        for OR_item in or_sequence_dict_list:
            or_name = OR_item["nom"]
            weight = OR_item.get("poids", 1) # Récupérer le poids, par défaut 1 si non spécifié
            retard = retards_values.get(or_name, 0)
            sum_wj_tj += weight * retard
           
        denominator = (self.alpha * makespan) + ((1 - self.alpha) * sum_wj_tj)
       
        # Éviter la division par zéro ou un dénominateur très petit
        # Un makespan nul avec des retards nuls (dénominateur 0) est une solution parfaite
        if denominator == 0:
            return float('inf') # Fitness infinie pour une solution parfaite
        return 1 / denominator

    def _generate_initial_population(self):
        """
        Génère la population initiale en mélangeant aléatoirement les ORs.
        Pour une petite instance, on peut utiliser des permutations.
        Pour une grande instance, des mélanges aléatoires ou une heuristique de départ seraient préférables.
        """
        population = []
        num_generated = 0
        seen_sequences = set()

        # Ajouter l'ordre initial comme première solution si elle est valide
        initial_solution_names = tuple(or_item["nom"] for or_item in self.ORs_data)
        if initial_solution_names not in seen_sequences:
            population.append(self.ORs_data)
            seen_sequences.add(initial_solution_names)
            num_generated += 1
           
        while num_generated < self.pop_size:
            shuffled_ors = self.ORs_data[:] # Copie pour éviter de modifier l'original
            random.shuffle(shuffled_ors)
           
            # Convertir la liste d'objets ORs en tuple de noms d'ORs pour le set
            shuffled_names_tuple = tuple(or_item["nom"] for or_item in shuffled_ors)

            if shuffled_names_tuple not in seen_sequences:
                population.append(shuffled_ors)
                seen_sequences.add(shuffled_names_tuple)
                num_generated += 1
       
        return population


    def _selection_tournament(self, population_with_fitness, k=3):
        """
        Sélectionne les parents par tournoi.
        `population_with_fitness` est une liste de (solution, fitness).
        """
        selected_parents = []
        num_to_select = int(self.pop_size * (1 - self.elitism_rate)) # Le reste sera des enfants
       
        # S'assurer qu'il y a au moins 2 parents pour le croisement
        if num_to_select < 2:
            num_to_select = 2

        for _ in range(num_to_select):
            # Choisir k candidats au hasard
            candidats = random.sample(population_with_fitness, k)
            # Le meilleur candidat du tournoi est sélectionné
            best_candidate = max(candidats, key=lambda item: item[1])
            selected_parents.append(best_candidate[0]) # Ajouter la solution (pas le fitness)
        return selected_parents

    def _crossover_partial_order(self, parent1_solution, parent2_solution):
        """
        Croisement ordre partiel (PMX-like pour conserver les ORs).
        Prend des listes d'objets ORs.
        """
        n = len(parent1_solution)
       
        r = random.random()
        if r >= self.crossover_prob:
            return parent1_solution.copy(), parent2_solution.copy()

        # S'assurer que les points de coupure sont distincts et dans le bon ordre
        # Pour n=5, range(n) est [0, 1, 2, 3, 4]. Deux points distincts dans ce range.
        # Par exemple, si n=5, on peut avoir 0, 1 ou 0, 2 ou 1, 3 etc.
        # On veut au moins un élément en dehors du segment, donc start et end ne peuvent pas couvrir tout n.
        # C'est implicitement géré par random.sample(range(n), 2) puis sorted.
       
        # Ajustement pour garantir que le segment n'est pas toute la séquence
        if n < 2: # Pas de croisement possible pour 0 ou 1 élément
             return parent1_solution.copy(), parent2_solution.copy()
       
        if n == 2: # Seulement deux options: (0,1) ou (1,0) pour les indices.
            start, end = 0, 1 # Le segment sera [0:2], couvrant les deux éléments. Pas idéal pour un PMX.
            # Pour n=2, un simple swap ou un croisement à un point est plus sensé.
            # Ici, on peut juste échanger les positions pour un simple croisement.
            child1 = [parent1_solution[0], parent2_solution[1]]
            child2 = [parent2_solution[0], parent1_solution[1]]
            return child1, child2

        # For n > 2, we can have a true segment
        idx1, idx2 = random.sample(range(n), 2)
        start, end = min(idx1, idx2), max(idx1, idx2)

        # Copie profonde pour les enfants car ils contiennent des objets ORs dict
        child1 = [None] * n
        child2 = [None] * n

        # Copier les segments des parents
        child1[start:end+1] = parent1_solution[start:end+1]
        child2[start:end+1] = parent2_solution[start:end+1]

        # Fonction utilitaire pour remplir les gènes manquants
        def fill_missing(child, source_parent, segment_from_other_parent_names):
            current_source_idx = 0
            for i in range(n):
                if child[i] is None: # Si la position est vide (pas dans le segment copié)
                    # Trouver le prochain OR du parent source qui n'est pas déjà dans le segment copié
                    while source_parent[current_source_idx]["nom"] in segment_from_other_parent_names:
                        current_source_idx += 1
                    child[i] = source_parent[current_source_idx]
                    current_source_idx += 1
            return child

        # Récupérer les noms des ORs des segments croisés
        segment1_names = {or_item["nom"] for or_item in parent1_solution[start:end+1]}
        segment2_names = {or_item["nom"] for or_item in parent2_solution[start:end+1]}
       
        child1 = fill_missing(child1, parent2_solution, segment1_names)
        child2 = fill_missing(child2, parent1_solution, segment2_names)
       
        return child1, child2

    def _mutation_swap(self, solution_list_of_ors):
        """
        Mutation par échange de deux ORs dans la séquence.
        Prend une liste d'objets ORs.
        """
        mutated_solution = solution_list_of_ors.copy()
        n = len(mutated_solution)
       
        if n < 2: # Pas de mutation possible pour 0 ou 1 élément
            return mutated_solution

        # Appliquer la mutation avec une probabilité
        if random.random() < self.mutation_prob:
            num_mutations = random.randint(1, self.max_k_mutations) # Nombre aléatoire d'échanges
            for _ in range(num_mutations):
                # Choisir deux positions aléatoires distinctes
                idx1, idx2 = random.sample(range(n), 2)
                mutated_solution[idx1], mutated_solution[idx2] = mutated_solution[idx2], mutated_solution[idx1]
       
        return mutated_solution

    def run(self):
        """
        Exécute l'algorithme génétique.
        """
        population = self._generate_initial_population()
        current_best_fitness = -float('inf')
        stagnation_counter = 0

        print(f"Démarrage de l'algorithme génétique avec {self.pop_size} individus et {self.generations} générations.")
       
        for generation in range(self.generations):
            # Évaluation de la population
            population_with_fitness = []
            for individual in population:
                fitness_val = self._calculate_fitness(individual)
                population_with_fitness.append((individual, fitness_val))
               
                # Mise à jour de la meilleure solution globale
                if fitness_val > self.best_overall_fitness:
                    self.best_overall_fitness = fitness_val
                    self.best_overall_solution = individual
                    current_makespan, _, _ = calculer_makespan_et_retards(individual, self.machines_template)
                    self.best_overall_makespan = current_makespan
           
            # --- Critère d'arrêt par stagnation ---
            # Après avoir calculé le fitness de tous les individus
            if generation > 0 and abs(self.best_overall_fitness - current_best_fitness) < self.epsilon_stagnation:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
            current_best_fitness = self.best_overall_fitness

            if stagnation_counter >= self.max_stagnation_generations:
                print(f"Arrêt prématuré à la génération {generation} : Stagnation détectée.")
                break

            # Sélection des parents (élitisme + tournoi)
            # Tri par fitness décroissant pour l'élitisme
            population_with_fitness.sort(key=lambda x: x[1], reverse=True)
           
            num_elitism = int(self.pop_size * self.elitism_rate)
            new_population = [copy.deepcopy(ind) for ind, _ in population_with_fitness[:num_elitism]] # Deepcopy for elitism
           
            # Sélection des parents pour le croisement/mutation (le reste de la population)
            parents_for_reproduction = self._selection_tournament(population_with_fitness)
           
            # Croisement et Mutation
            random.shuffle(parents_for_reproduction) # Mélanger pour des paires aléatoires
           
            # S'assurer que nous avons un nombre pair de parents pour le croisement
            num_parents_to_cross = len(parents_for_reproduction) - (len(parents_for_reproduction) % 2)

            for i in range(0, num_parents_to_cross, 2):
                p1 = parents_for_reproduction[i]
                p2 = parents_for_reproduction[i+1]
               
                child1, child2 = self._crossover_partial_order(p1, p2)
               
                new_population.append(self._mutation_swap(child1))
                new_population.append(self._mutation_swap(child2))

            # S'assurer que la population reste à la taille désirée
            # Si new_population est plus grand que pop_size, tronquer.
            # Si plus petit (ex: pas assez de paires pour croisement), laisser tel quel ou compléter.
            # Ici, on tronque si trop grand.
            population = new_population[:self.pop_size]

            if (generation + 1) % 10 == 0:
                print(f"Génération {generation+1}/{self.generations} - Meilleur Makespan: {self.best_overall_makespan:.2f}")

        print(f"\nAlgorithme génétique terminé.")
        print(f"Meilleure solution trouvée (Makespan) : {self.best_overall_makespan:.2f}")
        print(f"Fitness de la meilleure solution : {self.best_overall_fitness:.4f}")
       
        return self.best_overall_solution, self.best_overall_makespan

# --- Exécution principale ---
if __name__ == "__main__":
    # ORs_data_full et machines_template sont définis plus haut

    # Création de l'instance de l'algorithme génétique
    ga = GeneticAlgorithmORs(
        ORs_data=ORs_data_full, # Utilisation des données complètes
        machines_template=machines_template,
        alpha=0.5,             # Poids Makespan vs Retards (0.0 à 1.0)
        pop_size=50,
        generations=200,
        elitism_rate=0.1,      # Garde 10% des meilleurs individus sans modification
        crossover_prob=0.8,
        mutation_prob=0.15,    # Légèrement augmenté pour plus d'exploration
        max_k_mutations=2,
        max_stagnation_generations=40, # Arrêt si pas d'amélioration significative pendant 40 générations
        epsilon_stagnation=0.01 # Seuil d'amélioration de fitness
    )

    # Lancer l'algorithme
    meilleure_sequence_ors, meilleur_makespan = ga.run()

    print("\n--- Résultat de l'Algorithme Génétique ---")
    print("Ordre des ORs optimal :")
    for or_item in meilleure_sequence_ors:
        print(f"- {or_item['nom']}")

    print(f"\nMeilleur Makespan obtenu : {meilleur_makespan:.2f}")

    # Affichage détaillé et diagramme de Gantt pour la meilleure solution
    _, ordonnancement_detail = evaluer_sequence(meilleure_sequence_ors, machines_template)
   
    afficher_ordonnancement(ordonnancement_detail)
    tracer_diagramme_gantt(ordonnancement_detail)