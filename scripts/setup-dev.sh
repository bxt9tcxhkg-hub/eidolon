#!/usr/bin/env bash
# Eidolon Development Setup
# Installiert Rust, Python-Deps und richtet das Projekt ein

set -e

echo "🦀 Eidolon Development Setup"
echo "=============================="

# 1. Rust installieren
if ! command -v cargo &> /dev/null; then
    echo "📦 Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
    source "$HOME/.cargo/env"
else
    echo "✓ Rust already installed: $(rustc --version)"
fi

# 2. Python venv einrichten
echo "🐍 Setting up Python environment..."
cd python
python -m venv venv 2>/dev/null || python3 -m venv venv
source venv/Scripts/activate  # Windows
pip install --upgrade pip
pip install faster-whisper piper-tts pyo3-build 2>/dev/null || true
cd ..

# 3. Rust Dependencies bauen
echo "🔨 Building Rust workspace..."
cargo build --workspace 2>&1 | tail -5

# 4. Git konfigurieren
if [ ! -d .git ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "feat: initial project structure"
fi

# 5. Pre-commit Hook (optional)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install 2>/dev/null || true
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Install Ollama: https://ollama.ai"
echo "  2. Run: ollama pull llama3.3:70b    # or your preferred model"
echo "  3. Start: cargo run --bin eidolon -- chat"
echo ""
