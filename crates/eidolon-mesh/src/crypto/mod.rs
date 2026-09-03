use ed25519_dalek::{Signature, Signer, SigningKey, Verifier, VerifyingKey};
use rand::RngCore;
use rand::rngs::OsRng;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum CryptoError {
    #[error("signing error: {0}")]
    Signing(String),
    #[error("verification failed")]
    VerificationFailed,
    #[error("key error: {0}")]
    Key(String),
}

pub type Result<T> = std::result::Result<T, CryptoError>;

// --- Mesh Crypto ---

pub struct MeshCrypto {
    signing_key: SigningKey,
    verifying_key: VerifyingKey,
}

impl MeshCrypto {
    pub fn generate() -> Self {
        let mut secret_bytes = [0u8; 32];
        OsRng.fill_bytes(&mut secret_bytes);
        let signing_key = SigningKey::from_bytes(&secret_bytes);
        let verifying_key = signing_key.verifying_key();
        Self {
            signing_key,
            verifying_key,
        }
    }

    pub fn sign(&self, data: &[u8]) -> Result<Signature> {
        Ok(self.signing_key.sign(data))
    }

    pub fn verify(verifying_key: &VerifyingKey, data: &[u8], signature: &Signature) -> Result<()> {
        verifying_key.verify(data, signature).map_err(|_| CryptoError::VerificationFailed)
    }

    pub fn public_key(&self) -> &VerifyingKey {
        &self.verifying_key
    }
}
