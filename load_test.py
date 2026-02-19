import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
ANALYZE_URL = f"{BASE_URL}/api/analyze"

# 1. Identifiants pour le test
payload = {
    "username": "cia@example.com", # Remplace par un compte existant
    "password": "1234"
}

def run_load_test():
    #  ÉTAPE 1 : Connexion pour récupérer le Token 
    print("Connexion en cours...")
    response = requests.post(LOGIN_URL, data=payload)
    if response.status_code != 200:
        print("Erreur de connexion. Vérifiez vos identifiants.")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #  ÉTAPE 2 : Simulation de 10 analyses 
    print(f"Lancement de 10 analyses sur {ANALYZE_URL}...")
    latencies = []
    
    # Prépare l'image 
    files = {'image': ('test.jpg', open('test.jpg', 'rb'), 'image/jpeg')}
    data = {
        "duration": "1 mois",
        "pain": 2,
        "itching": 1,
        "bleeding": 0
    }

    for i in range(1, 11):
        start = time.time()

        # On réouvre le fichier à chaque fois pour le flux
        with open('test.jpg', 'rb') as img:
            files['image'] = ('test.jpg', img, 'image/jpeg')
            res = requests.post(ANALYZE_URL, headers=headers, data=data, files=files)
        
        duration = time.time() - start
        latencies.append(duration)
        
        if res.status_code == 200:
            print(f"Requête {i}: Succès en {duration:.2f}s")
        else:
            print(f"Requête {i}: Échec ({res.status_code})")

    # ÉTAPE 3 : Résultats finaux 
    avg = sum(latencies) / len(latencies)
    print("\n--- RAPPORT DE TEST DE CHARGE ---")
    print(f"Temps moyen : {avg:.2f} secondes")
    
    if avg < 5:
        print(" CRITÈRE DE SUCCÈS VALIDÉ (< 5s)") #[cite: 187]
    else:
        print(" CRITÈRE DE SUCCÈS ÉCHOUÉ (> 5s)")

if __name__ == "__main__":
    run_load_test()