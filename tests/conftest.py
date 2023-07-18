import pytest
from supacrud import Supabase

@pytest.fixture
def supabase():
    base_url = 'http://example.com'
    service_role_key = 'key'
    return Supabase(base_url, service_role_key)
