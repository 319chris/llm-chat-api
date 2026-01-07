#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"  
DIST_DIR="${ROOT_DIR}/dist"
ZIP_PATH="${DIST_DIR}/lambda.zip"

rm -rf "${BUILD_DIR}" "${DIST_DIR}"
mkdir -p "${BUILD_DIR}" "${DIST_DIR}"

# Install runtime deps into build/
python -m pip install --upgrade pip >/dev/null
pip install -r "${ROOT_DIR}/requirements.txt" -t "${BUILD_DIR}" >/dev/null

# Copy source code
cp -R "${ROOT_DIR}/src" "${BUILD_DIR}/src"

# Zip
(
  cd "${BUILD_DIR}"
  zip -qr "${ZIP_PATH}" .
)

echo "Built: ${ZIP_PATH}"