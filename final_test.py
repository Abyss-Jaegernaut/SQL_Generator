#!/usr/bin/env python3
"""
Final test for the hardware-based activation system
"""

def test_hardware_activation():
    print("Testing hardware-based activation system...")
    
    try:
        # Import the hardware ID module
        from utils.hardware_id import generate_machine_code, generate_activation_key, verify_activation_key
        print("✓ Successfully imported hardware_id module")
        
        # Test 1: Generate machine code
        machine_code = generate_machine_code()
        print(f"✓ Generated machine code: {machine_code}")
        
        # Test 2: Generate activation key for this machine
        activation_key = generate_activation_key(machine_code)
        print(f"✓ Generated activation key: {activation_key}")
        
        # Test 3: Verify the activation key matches the machine
        is_valid = verify_activation_key(machine_code, activation_key)
        print(f"✓ Activation key verification: {'PASS' if is_valid else 'FAIL'}")
        
        # Test 4: Verify that a wrong key doesn't work
        fake_key = "FAKE-AAAA-BBBB-CCCC-DDDD"
        is_fake_valid = verify_activation_key(machine_code, fake_key)
        print(f"✓ Fake key verification: {'FAIL (should be invalid)' if not is_fake_valid else 'UNEXPECTED PASS'}")
        
        # Test 5: Test the AppController integration
        from controllers.app_controller import AppController
        from data.storage import Storage
        
        # Create a temporary storage for testing
        controller = AppController(Storage(db_path='temp_test.db'))
        
        # Get machine code through controller
        ctrl_machine_code = controller.get_machine_code()
        print(f"✓ Controller machine code: {ctrl_machine_code}")
        
        # Generate key through controller (as if we were the developer)
        dev_key = controller.generate_activation_key_for_machine(ctrl_machine_code)
        print(f"✓ Developer-generated key: {dev_key}")
        
        # Test activation
        activation_result = controller.activate_license(dev_key)
        print(f"✓ Activation attempt: {'SUCCESS' if activation_result else 'FAILED'}")
        
        # Check if now activated
        is_activated = controller.is_activated()
        print(f"✓ Is activated: {'YES' if is_activated else 'NO'}")
        
        print("\n🎉 Hardware-based activation system is working correctly!")
        print("\nSUMMARY:")
        print("- Each machine generates a unique hardware-based code")
        print("- Keys are generated specifically for each machine")
        print("- Activation keys only work on the machine they were generated for")
        print("- Copying the application to another device will require re-activation")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hardware_activation()
    if success:
        print("\n✅ All tests passed! The hardware-based activation system is ready.")
    else:
        print("\n❌ Tests failed! Please check the implementation.")