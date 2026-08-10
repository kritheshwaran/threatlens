#!/bin/bash

set -e

echo "🚀 Creating ThreatLens project structure..."

# =========================
# DIRECTORIES
# =========================

mkdir -p \
  .github/workflows \
  frontend/public \
  frontend/src/assets \
  frontend/src/components/ui \
  frontend/src/components/dashboard \
  frontend/src/components/scanner \
  frontend/src/components/charts \
  frontend/src/pages \
  frontend/src/services \
  frontend/src/hooks \
  frontend/src/context \
  frontend/src/utils \
  backend/app/api/routes \
  backend/app/core \
  backend/app/models \
  backend/app/schemas \
  backend/app/services \
  backend/app/ml \
  backend/app/database/migrations \
  backend/tests \
  ml/data/raw \
  ml/data/processed \
  ml/notebooks \
  ml/scripts \
  ml/models \
  docs/screenshots

# =========================
# GITHUB
# =========================

touch .github/workflows/ci.yml

# =========================
# FRONTEND
# =========================

touch \
  frontend/src/pages/Dashboard.jsx \
  frontend/src/pages/Scanner.jsx \
  frontend/src/pages/History.jsx \
  frontend/src/pages/Analytics.jsx \
  frontend/src/pages/Report.jsx \
  frontend/src/pages/Login.jsx \
  frontend/src/pages/Settings.jsx \
  frontend/src/services/api.js \
  frontend/src/App.jsx \
  frontend/src/main.jsx \
  frontend/src/index.css

# =========================
# BACKEND - API
# =========================

touch \
  backend/app/api/routes/scan.py \
  backend/app/api/routes/auth.py \
  backend/app/api/routes/history.py \
  backend/app/api/routes/analytics.py \
  backend/app/api/router.py

# =========================
# BACKEND - CORE
# =========================

touch \
  backend/app/core/config.py \
  backend/app/core/security.py

# =========================
# BACKEND - MODELS
# =========================

touch \
  backend/app/models/scan.py \
  backend/app/models/user.py

# =========================
# BACKEND - SCHEMAS
# =========================

touch \
  backend/app/schemas/scan.py \
  backend/app/schemas/user.py

# =========================
# BACKEND - SERVICES
# =========================

touch \
  backend/app/services/url_analyzer.py \
  backend/app/services/domain_analyzer.py \
  backend/app/services/dns_analyzer.py \
  backend/app/services/ssl_analyzer.py \
  backend/app/services/reputation.py \
  backend/app/services/feature_extractor.py \
  backend/app/services/risk_engine.py \
  backend/app/services/explanation.py

# =========================
# BACKEND - ML
# =========================

touch \
  backend/app/ml/model.py \
  backend/app/ml/predictor.py \
  backend/app/ml/preprocessing.py

# =========================
# BACKEND - DATABASE
# =========================

touch backend/app/database/database.py

# =========================
# BACKEND - MAIN
# =========================

touch backend/app/main.py

# =========================
# BACKEND - TESTS
# =========================

touch \
  backend/tests/test_url_analyzer.py \
  backend/tests/test_risk_engine.py \
  backend/tests/test_api.py

touch backend/requirements.txt

# =========================
# ML
# =========================

touch \
  ml/notebooks/model_training.ipynb \
  ml/scripts/preprocess.py \
  ml/scripts/train.py \
  ml/scripts/evaluate.py \
  ml/models/.gitkeep

# =========================
# DOCS
# =========================

touch \
  docs/architecture.md \
  docs/api.md

# =========================
# ROOT FILES
# =========================

touch \
  .env.example \
  .gitignore \
  docker-compose.yml \
  Dockerfile \
  README.md \
  LICENSE

echo ""
echo "✅ ThreatLens project structure created successfully!"
echo ""
echo "📁 Structure:"
find . -not -path './.git/*' -not -path './.git' | sort
echo ""
echo "🎯 ThreatLens setup complete!"
