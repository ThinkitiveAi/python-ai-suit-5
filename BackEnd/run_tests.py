#!/usr/bin/env python3
"""
Comprehensive test runner for the FastAPI authentication backend.
Runs unit tests, integration tests, and API tests.
"""
import subprocess
import sys
import os
from pathlib import Path


def print_separator(title):
    """Print a separator with title."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    try:
        print(f"\n🔄 {description}...")
        # Replace 'python' with 'python3' for compatibility
        command = command.replace('python ', 'python3 ')
        print(f"Command: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print_separator("CHECKING DEPENDENCIES")
    
    required_packages = [
        "pytest",
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "python-jose",
        "bcrypt",
        "slowapi",
        "phonenumbers"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Special case for python-jose which imports as 'jose'
            if package == "python-jose":
                __import__("jose")
            else:
                __import__(package.replace("-", "_"))
            print(f"✅ {package} - installed")
        except ImportError:
            print(f"❌ {package} - missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True


def run_unit_tests():
    """Run unit tests."""
    print_separator("RUNNING UNIT TESTS")
    
    test_files = [
        "tests/test_auth_service.py",
        "tests/test_jwt_utils.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_command(
                f"python -m pytest {test_file} -v --tb=short",
                f"Unit tests: {test_file}"
            )
            all_passed = all_passed and success
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    return all_passed


def run_integration_tests():
    """Run integration tests."""
    print_separator("RUNNING INTEGRATION TESTS")
    
    test_files = [
        "tests/test_auth_endpoints.py"
    ]
    
    all_passed = True
    
    for test_file in test_files:
        if os.path.exists(test_file):
            success = run_command(
                f"python -m pytest {test_file} -v --tb=short",
                f"Integration tests: {test_file}"
            )
            all_passed = all_passed and success
        else:
            print(f"⚠️ Test file not found: {test_file}")
    
    return all_passed


def run_api_tests():
    """Run API tests (requires running server)."""
    print_separator("RUNNING API TESTS")
    
    print("⚠️ API tests require a running server at http://localhost:8000")
    print("Start the server with: python main.py")
    print("Then run: python test_auth.py")
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            success = run_command(
                "python test_auth.py",
                "API authentication tests"
            )
            return success
        else:
            print("❌ Server is not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server with: python main.py")
        return False


def run_all_tests():
    """Run all tests."""
    print_separator("FASTAPI AUTHENTICATION BACKEND - TEST SUITE")
    print("Testing comprehensive authentication functionality")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install required packages.")
        return False
    
    # Run tests
    results = {
        "Unit Tests": run_unit_tests(),
        "Integration Tests": run_integration_tests(),
        "API Tests": run_api_tests()
    }
    
    # Summary
    print_separator("TEST RESULTS SUMMARY")
    
    all_passed = True
    for test_type, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type}: {status}")
        all_passed = all_passed and passed
    
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Authentication backend is working correctly!")
        print("Features tested:")
        print("- Provider login with email/phone")
        print("- JWT token creation and validation")
        print("- Token refresh functionality")
        print("- Account lockout after failed attempts")
        print("- Rate limiting on auth endpoints")
        print("- Protected endpoint access")
        print("- Logout and logout-all functionality")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return all_passed


def run_specific_test():
    """Run a specific test file."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [test_file]")
        print("Available test files:")
        print("- tests/test_auth_service.py")
        print("- tests/test_jwt_utils.py")
        print("- tests/test_auth_endpoints.py")
        print("- test_auth.py (API tests)")
        return
    
    test_file = sys.argv[1]
    
    if test_file.endswith(".py") and os.path.exists(test_file):
        if test_file == "test_auth.py":
            run_api_tests()
        else:
            run_command(
                f"python -m pytest {test_file} -v --tb=long",
                f"Running {test_file}"
            )
    else:
        print(f"Test file not found: {test_file}")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        run_specific_test()
    else:
        run_all_tests()


if __name__ == "__main__":
    main()
