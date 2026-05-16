import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


class CryptoService:
    @staticmethod
    def generate_rsa_keys():
        """Generates a new pair of RSA keys."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def export_public_key(public_key):
        """Exports public key to PEM format."""
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

    @staticmethod
    def export_private_key_encrypted(private_key, password):
        """
        Exports private key to PEM format, encrypted with a key derived from password.
        Uses Fernet (AES) for the outer encryption layer for extra simplicity.
        """
        # 1. Export private key to PEM (unencrypted in memory)
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # 2. Derive a Fernet key from the user's password
        salt = b"artemus_fixed_salt"  # In production, use a unique salt per user
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)

        # 3. Encrypt the PEM
        encrypted_pem = f.encrypt(pem)
        return encrypted_pem.decode("utf-8")

    @staticmethod
    def decrypt_private_key(encrypted_pem_str, password):
        """Decrypts the private key using the password."""
        salt = b"artemus_fixed_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        f = Fernet(key)

        try:
            pem = f.decrypt(encrypted_pem_str.encode())
            return serialization.load_pem_private_key(pem, password=None)
        except Exception:
            return None

    @staticmethod
    def encrypt_with_public_key(content, public_key_pem_str):
        """Encrypts content with a recipient's public key."""
        public_key = serialization.load_pem_public_key(public_key_pem_str.encode())
        encrypted = public_key.encrypt(
            content.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode("utf-8")

    @staticmethod
    def decrypt_with_private_key(encrypted_base64_str, private_key):
        """Decrypts content with the current user's private key."""
        try:
            encrypted_data = base64.b64decode(encrypted_base64_str)
            decrypted = private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return decrypted.decode("utf-8")
        except Exception as e:
            return f"[Error al desencriptar: {str(e)}]"
