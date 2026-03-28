import os
try:
    from google.cloud import secretmanager
except ImportError:
    pass

def get_secret(secret_id: str, project_id: str = None) -> str:
    """Fetches a secret from Google Cloud Secret Manager or OS env as fallback."""
    if secret_id in os.environ:
        return os.environ[secret_id]
        
    if not project_id:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        
    if not project_id:
        print(f"No GCP project configured. Skipping GCP fetch for {secret_id}.")
        return ""

    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        os.environ[secret_id] = secret_value
        return secret_value
    except Exception as e:
        print(f"Error fetching secret '{secret_id}': {e}")
        return ""
