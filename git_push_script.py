#!/usr/bin/env python3
"""
Git push automation script
"""
import subprocess
import sys
import os

os.chdir('C:\\ParisCred_Intelligence')

print("Starting git push...")
print("Current directory:", os.getcwd())
print()

# Check git status
print("=== Git Status ===")
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr if result.stderr else "")

# Check remote
print("\n=== Git Remote ===")
result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr if result.stderr else "")

# Check branch
print("\n=== Git Branch ===")
result = subprocess.run(['git', 'branch', '-avv'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr if result.stderr else "")

# Attempt push
print("\n=== Attempting Git Push ===")
try:
    result = subprocess.run(
        ['git', 'push', '-u', 'origin', 'main', '--verbose'],
        capture_output=True,
        text=True,
        timeout=60
    )
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode == 0:
        print("\n✅ Push successful!")
    else:
        print(f"\n❌ Push failed with return code {result.returncode}")
        
except subprocess.TimeoutExpired:
    print("❌ Push command timed out after 60 seconds")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== Final Status ===")
result = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True)
print(result.stdout)
