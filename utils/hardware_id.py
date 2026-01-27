import hashlib
import platform
import subprocess
import uuid
import re


_cached_machine_code = None

def get_cpu_id():
    """Get CPU identifier based on platform"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['wmic', 'cpu', 'get', 'ProcessorId'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if line and line != 'ProcessorId':
                    return line
    except Exception:
        pass
    # Stable fallback based on MAC address
    return str(uuid.getnode())


def get_machine_id():
    """Get a unique machine identifier"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['wmic', 'baseboard', 'get', 'SerialNumber'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            for line in lines:
                line = line.strip()
                if line and line.lower() != 'serialnumber':
                    return line
    except Exception:
        pass
    return get_cpu_id()


def generate_machine_code():
    """Generate a readable machine code from hardware ID (cached)"""
    global _cached_machine_code
    if _cached_machine_code:
        return _cached_machine_code
        
    machine_id = get_machine_id()
    hashed = hashlib.sha256((machine_id or "unknown").encode()).hexdigest()
    _cached_machine_code = "MACH-{0}-{1}-{2}".format(hashed[:4].upper(), hashed[4:8].upper(), hashed[8:12].upper())
    return _cached_machine_code


def verify_activation_key(machine_code, activation_key, secret_phrase="SQL_GENERATOR_SECRET"):
    """Verify if the activation key matches the current machine"""
    expected_key = generate_activation_key(machine_code, secret_phrase)
    return activation_key.replace('-', '').replace(' ', '').upper() == expected_key.replace('-', '').replace(' ', '').upper()


def generate_activation_key(machine_code, secret_phrase="SQL_GENERATOR_SECRET"):
    """Generate an activation key for a given machine code"""
    # Important: Remove dashes and prefix to be robust against formatting
    clean_code = machine_code.replace('MACH-', '').replace('-', '').strip().upper()
    if not clean_code:
        return ""
        
    combined = clean_code + secret_phrase
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    formatted_key = "{0}-{1}-{2}-{3}-{4}".format(
        hashed[:4].upper(), 
        hashed[4:8].upper(), 
        hashed[8:12].upper(), 
        hashed[12:16].upper(), 
        hashed[16:20].upper()
    )
    return formatted_key
