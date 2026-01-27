try:
    from utils.hardware_id import generate_machine_code
    code = generate_machine_code()
    print(f'Machine code: {code}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
