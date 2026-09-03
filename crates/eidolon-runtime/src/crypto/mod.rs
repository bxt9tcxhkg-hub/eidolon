use ed25519_dalek::{Signer, Verifier, SigningKey, VerifyingKey, Signature};
use rand::rngs::OsRng;
use sha2::{Sha256, Digest};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct KeyPair {
    pub signing_key: SigningKey,
    pub verifying_key: VerifyingKey,
}

impl KeyPair {
    pub fn generate() -> Self {
        let mut csprng = OsRng;
        let signing_key = SigningKey::generate(&mut csprng);
        let verifying_key = signing_key.verifying_key();
        Self { signing_key, verifying_key }
    }

    pub fn sign(&self, message: &[u8]) -> Signature {
        self.signing_key.sign(message)
    }

    pub fn public_key_hex(&self) -> String {
        hex::encode(self.verifying_key.to_bytes())
    }

    pub fn save_to_file(&self, path: &Path) -> Result<(), anyhow::Error> {
        let bytes = self.signing_key.to_bytes();
        std::fs::write(path, hex::encode(bytes))?;
        Ok(())
    }

    pub fn load_from_file(path: &Path) -> Result<Self, anyhow::Error> {
        let hex_str = std::fs::read_to_string(path)?;
        let bytes = hex::decode(hex_str.trim())?;
        let signing_key = SigningKey::try_from(bytes.as_slice())
            .map_err(|e| anyhow::anyhow!("Invalid key: {}", e))?;
        let verifying_key = signing_key.verifying_key();
        Ok(Self { signing_key, verifying_key })
    }
}

pub fn hash_sha256(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hex::encode(hasher.finalize())
}

pub fn verify_signature(message: &[u8], signature: &Signature, public_key: &str) -> bool {
    let pk_bytes = match hex::decode(public_key) {
        Ok(b) => b,
        Err(_) => return false,
    };
    let pk_array: [u8; 32] = match pk_bytes.try_into() {
        Ok(b) => b,
        Err(_) => return false,
    };
    let verifying_key = match VerifyingKey::from_bytes(&pk_array) {
        Ok(k) => k,
        Err(_) => return false,
    };
    verifying_key.verify(message, signature).is_ok()
}
