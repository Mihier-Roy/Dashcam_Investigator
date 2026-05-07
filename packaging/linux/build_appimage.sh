#!/usr/bin/env bash
# Wrap the PyInstaller onedir bundle in an AppImage.
#
# Prereqs:
#   - PyInstaller has already produced dist/DashcamInvestigator/
#   - appimagetool is on PATH (download from
#     https://github.com/AppImage/AppImageKit/releases)
#   - Run from the repo root.
#
# Output: dist/DashcamInvestigator-x86_64.AppImage

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"
ONEDIR="${DIST_DIR}/DashcamInvestigator"
APPDIR="${DIST_DIR}/DashcamInvestigator.AppDir"
PACKAGING_DIR="${REPO_ROOT}/packaging/linux"

if [[ ! -d "${ONEDIR}" ]]; then
  echo "error: ${ONEDIR} not found. Run pyinstaller first." >&2
  exit 1
fi

if ! command -v appimagetool >/dev/null 2>&1; then
  echo "error: appimagetool not on PATH." >&2
  echo "Install: https://github.com/AppImage/AppImageKit/releases" >&2
  exit 1
fi

rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/share/applications" \
  "${APPDIR}/usr/share/icons/hicolor/scalable/apps"

# Copy the entire PyInstaller bundle into AppDir/usr/bin so the binary,
# its dynamically-linked Qt libs, and the bundled assets all stay together.
cp -r "${ONEDIR}/." "${APPDIR}/usr/bin/"

# Desktop entry + icon (top-level copies are required by the AppImage spec).
cp "${PACKAGING_DIR}/DashcamInvestigator.desktop" "${APPDIR}/"
cp "${PACKAGING_DIR}/DashcamInvestigator.desktop" \
  "${APPDIR}/usr/share/applications/DashcamInvestigator.desktop"

cp "${PACKAGING_DIR}/DashcamInvestigator.svg" "${APPDIR}/DashcamInvestigator.svg"
cp "${PACKAGING_DIR}/DashcamInvestigator.svg" \
  "${APPDIR}/usr/share/icons/hicolor/scalable/apps/DashcamInvestigator.svg"
# .DirIcon is what file managers pick up for the AppImage thumbnail.
cp "${PACKAGING_DIR}/DashcamInvestigator.svg" "${APPDIR}/.DirIcon"

# AppRun is the entrypoint AppImage exec()s. Forward all args, set HERE so
# the binary can find its sibling libs even when launched via a desktop file.
cat > "${APPDIR}/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/DashcamInvestigator" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

ARCH="${ARCH:-$(uname -m)}"
OUTPUT="${DIST_DIR}/DashcamInvestigator-${ARCH}.AppImage"

ARCH="${ARCH}" appimagetool --no-appstream "${APPDIR}" "${OUTPUT}"

echo "Built: ${OUTPUT}"
