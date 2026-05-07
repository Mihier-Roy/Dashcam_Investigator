#!/usr/bin/env bash
# Wrap the PyInstaller onedir bundle in an AppImage.
#
# We assemble the AppImage manually rather than calling appimagetool, because
# appimagetool ships as an AppImage itself and its runtime is unreliable on
# GitHub Actions runners (no FUSE kernel module; AppArmor user-namespace
# restrictions on Ubuntu 24.04 break extract-and-run mode too). Concatenating
# a type-2 runtime with an mksquashfs-built filesystem is the same on-disk
# format and has no runtime dependencies at build time.
#
# Prereqs:
#   - PyInstaller has already produced dist/DashcamInvestigator/
#   - mksquashfs is on PATH (apt: squashfs-tools)
#   - curl is on PATH (used to fetch the type-2 runtime if RUNTIME is unset)
#   - Run from the repo root.
#
# Output: dist/DashcamInvestigator-<arch>.AppImage

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

if ! command -v mksquashfs >/dev/null 2>&1; then
  echo "error: mksquashfs not on PATH (install squashfs-tools)." >&2
  exit 1
fi

ARCH="${ARCH:-$(uname -m)}"
RUNTIME="${RUNTIME:-${DIST_DIR}/appimage-runtime-${ARCH}}"

if [[ ! -s "${RUNTIME}" ]]; then
  echo "Fetching AppImage type-2 runtime for ${ARCH}..."
  curl -fSL -o "${RUNTIME}" \
    "https://github.com/AppImage/type2-runtime/releases/download/continuous/runtime-${ARCH}"
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

OUTPUT="${DIST_DIR}/DashcamInvestigator-${ARCH}.AppImage"
SQUASHFS="${DIST_DIR}/DashcamInvestigator.squashfs"

rm -f "${SQUASHFS}" "${OUTPUT}"
# gzip is the safest compressor: every type-2 runtime build supports it,
# regardless of whether libsquashfuse was compiled with zstd.
mksquashfs "${APPDIR}" "${SQUASHFS}" \
  -root-owned -noappend -mkfs-time 0 -comp gzip -no-progress -quiet

cat "${RUNTIME}" "${SQUASHFS}" > "${OUTPUT}"
chmod +x "${OUTPUT}"
rm -f "${SQUASHFS}"

echo "Built: ${OUTPUT}"
