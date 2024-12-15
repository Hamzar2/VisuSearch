<style>
/* Conteneur d'images */
.image-container {
    display: flex;             /* Utilisation de flexbox pour un agencement flexible */
    justify-content: space-around;  /* Espacement égal entre les images */
    align-items: center;       /* Alignement vertical des images */
    flex-wrap: wrap;           /* Les images se déplacent sur plusieurs lignes si nécessaire */
    gap: 20px;                 /* Espacement entre les images */
    padding: 20px;             /* Padding autour des images */
}

/* Style des images */
.image {
    width: 300px;              /* Largeur fixe pour chaque image */
    height: auto;              /* Hauteur automatique pour garder les proportions */
    border-radius: 8px;        /* Coins arrondis pour un effet esthétique */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Ombre légère autour des images */
    transition: transform 0.3s ease; /* Transition douce au survol */
}

.image:hover {
    transform: scale(1.05);     /* Agrandissement léger au survol */
}
</style>


# VisuSearch  

**Lien du projet :** [VisuSearch GitHub Repository](https://github.com/Hamzar2/VisuSearch/tree/main)  

---

## **Description du Projet**  
VisuSearch est une application web innovante dédiée à l’indexation et la recherche d’images par le contenu (CBIR - Content-Based Image Retrieval). Ce projet exploite des descripteurs visuels, tels que les histogrammes de couleurs, de textures (filtres de Gabor) et de formes (moments de Hu), pour analyser et retrouver des images similaires à une requête donnée. Il intègre également des fonctionnalités avancées de **retour de pertinence** (relevance feedback) pour affiner dynamiquement les résultats en fonction des préférences des utilisateurs.  

---

## **Fonctionnalités**  
1. **Gestion des Images** :  
   - Chargement, téléchargement et suppression d’images.  
   - Organisation automatique des images selon des catégories prédéfinies ou personnalisées.  

2. **Extraction de Descripteurs Visuels** :  
   - Histogrammes de couleurs, textures et formes.  
   - Calcul et stockage des descripteurs sous forme JSON dans une base de données.  

3. **Recherche d’Images** :  
   - **Recherche simple** : Basée sur des mesures de similarité.  
   - **Retour de pertinence** : Méthode bayésienne pour affiner les résultats en fonction des retours utilisateur.  

4. **Transformations des Images** :  
   - Recadrage et redimensionnement des images pour créer de nouvelles variantes.  

---

## **Technologies Utilisées**  
- **Backend** :  
   - Laravel pour la gestion de la base de données.  
   - Flask (avec Flask-RESTful) pour les calculs des descripteurs et la gestion des API REST.  

- **Frontend** :  
   - Framework MEAN (MongoDB, Express, Angular, Node.js) ou une alternative basée sur Vue.js.  

- **Base de Données** :  
   - MySQL pour le stockage des métadonnées des images.  

---

## **Installation et Déploiement**  
### **Pré-requis** :  
- PHP (>= 7.4) avec Composer.  
- Python (>= 3.8) avec Flask et Flask-RESTful.  
- Serveur MySQL ou équivalent.  

### **Étapes** :  
1. Clonez ce dépôt :  
   ```bash  
   git clone https://github.com/Hamzar2/VisuSearch.git  
   cd VisuSearch  

2. Installez les dépendances PHP et Python :  
   ```bash  
   composer install  
   pip install -r requirements.txt  

3. Configurez le fichier .env pour Laravel et Flask (base de données, clés d’API, etc.).

4. Lancer les serveurs backend et frontend.


<div class="image-container">
    <img src="frontend\src\assets\c.jpeg" alt="Image 1" class="image">
    <img src="frontend\src\assets\b.jpeg" alt="Image 2" class="image">
    <img src="frontend\src\assets\a.jpeg" alt="Image 3" class="image">
    <img src="frontend\src\assets\d.jpeg" alt="Image 3" class="image">
</div>
