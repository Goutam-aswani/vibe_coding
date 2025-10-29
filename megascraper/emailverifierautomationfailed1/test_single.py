"""Quick single email test"""
from email_verifier_http import EmailVerifierHTTP

# Your session cookie
SESSION_COOKIE = "5dc7jcltfl2gvuoo9h59u973mf"

# Create verifier
verifier = EmailVerifierHTTP(
    session_cookie=SESSION_COOKIE,
    timeout=10
)

# Test single email
print("Testing email verification...")
result = verifier.check_email("goutamaswani43@gmail.com")

print("\n" + "="*60)
print("RESULT:")
print("="*60)
print(f"Status: {result.get('status')}")
print(f"Safe to Send: {result.get('safetosend')}")
print(f"Type: {result.get('type')}")
print(f"Reason: {result.get('reasons')}")
print("="*60)
