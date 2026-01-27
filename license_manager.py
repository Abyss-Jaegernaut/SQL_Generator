import hashlib
import sys

def generate_key(machine_code, secret_phrase="SQL_GENERATOR_SECRET"):
    """
    Génère une clé d'activation basée sur le code machine.
    """
    clean_code = machine_code.replace('MACH-', '').strip().upper()
    combined = clean_code + secret_phrase
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    
    # Format: XXXX-XXXX-XXXX-XXXX-XXXX
    formatted_key = "{0}-{1}-{2}-{3}-{4}".format(
        hashed[:4].upper(), 
        hashed[4:8].upper(), 
        hashed[8:12].upper(), 
        hashed[12:16].upper(), 
        hashed[16:20].upper()
    )
    return formatted_key

def main():
    print("=== SQL Generator - Gestionnaire de Licences ===")
    if len(sys.argv) > 1:
        machine_code = sys.argv[1]
    else:
        machine_code = input("Entrez le code machine (ex: MACH-A1B2-C3D4-E5F6) : ")
    
    if not machine_code.startswith("MACH-"):
        print("Erreur : Le code machine doit commencer par 'MACH-'")
        return

    key = generate_key(machine_code)
    print(f"\nCode Machine : {machine_code}")
    print(f"Clé d'Activation : {key}")
    print("\nCopiez cette clé pour l'activer dans l'application.")

if __name__ == "__main__":
    main()
