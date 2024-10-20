import ssl
import nltk

# Bypass SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Download 'punkt'
nltk.download('punkt')