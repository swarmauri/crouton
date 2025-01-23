import os
from hashlib import sha256
from uuid import UUID, uuid4, uuid5
from pydantic import BaseModel

# Define a default valid UUID string if the environment variable is not set
DEFAULT_NAMESPACE_UUID = "12345678-1234-5678-1234-567812345678"
NAMESPACE_URL_UUID = os.getenv("NAMESPACE_URL_UUID", DEFAULT_NAMESPACE_UUID)

class UUIDGenerator(BaseModel):
    namespace: UUID = UUID(NAMESPACE_URL_UUID)

    def create(self):
        name = str(uuid4())  # Generate a random UUID for the name
        return str(uuid5(self.namespace, name))
