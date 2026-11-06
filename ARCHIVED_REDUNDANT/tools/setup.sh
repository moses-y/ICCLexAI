#!/bin/bash

# AI-ICC Evidence Platform Setup Script
echo "🇰🇪 Setting up AI-ICC Evidence Platform..."

# Check if running on GitHub Codespaces or local
if [ "$CODESPACES" = "true" ]; then
    echo "📡 Detected GitHub Codespaces environment"
    export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
    export STREAMLIT_SERVER_PORT="8501"
fi

# Create necessary directories
mkdir -p logs
mkdir -p uploads
mkdir -p tests

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pip install pre-commit
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔑 Creating .env file template..."
    cat > .env << EOF
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost

# Development Configuration
DEBUG=True
LOG_LEVEL=INFO
EOF
    echo "✏️  Please edit .env file with your actual API keys"
fi

# Run initial tests
echo "🧪 Running initial tests..."
python -m pytest tests/ -v || echo "⚠️  Some tests failed - this is expected without API keys"

# Check if Streamlit works
echo "🚀 Testing Streamlit installation..."
streamlit hello &
STREAMLIT_PID=$!
sleep 5
kill $STREAMLIT_PID 2>/dev/null || true

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Add your Groq API key to .env file"
echo "2. Run: streamlit run main_app.py"
echo "3. Open browser to http://localhost:8501"
echo ""
echo "🔗 Repository: https://github.com/Moses-y/ai-icc-evidence-platform"
