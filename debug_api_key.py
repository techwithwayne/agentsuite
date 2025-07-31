import os
import sys
import django

# Add your project to Python path
sys.path.append('C:/Users/wayne/Desktop/techwithwayne/agentsuite')  # Adjust path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agentsuite.settings')  # Adjust module

django.setup()

from django.conf import settings
from webdoctor.ai_agent import get_openai_client

print("=== API Key Debug ===")
print(f"Environment OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')[-20:]}")
print(f"Settings OPENAI_API_KEY: {getattr(settings, 'OPENAI_API_KEY', 'NOT SET')[-20:]}")

try:
    client = get_openai_client()
    print("✅ OpenAI client created successfully")
except Exception as e:
    print(f"❌ OpenAI client failed: {str(e)}")