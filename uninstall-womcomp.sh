#!/bin/bash
# uninstall-womcomp.sh
# Desinstalador para WomComp (Instalación con install.sh)

set -e


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         WomComp Uninstaller v1.0                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""



SCRIPT_NAME="womcomp"
INSTALL_DIR="/usr/local/bin"
CONF_DIR="/etc/womcomp"
SHARE_DIR="/usr/share/womcomp"
LOG_DIR="/var/log/womcomp"
CACHE_DIR="/var/cache/womcomp"
TEMP_DIR="/tmp/womcomp"

echo -e "${YELLOW}Este script eliminará completamente WomComp del sistema.${NC}"
echo -e "${YELLOW}Los siguientes elementos serán eliminados:${NC}"
echo -e "  • Comando: ${INSTALL_DIR}/${SCRIPT_NAME}"
echo -e "  • Configuración: ${CONF_DIR}"
echo -e "  • Archivos compartidos: ${SHARE_DIR}"
echo -e "  • Logs: ${LOG_DIR}"
echo -e "  • Cache: ${CACHE_DIR}"
echo -e "  • Archivos temporales: ${TEMP_DIR}"
echo ""

read -p "¿Estás seguro de que deseas continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Desinstalación cancelada.${NC}"
    exit 0
fi


echo -e "${BLUE}[1/7]${NC} Verificando instalación..."

if [ -f "${INSTALL_DIR}/${SCRIPT_NAME}" ] || [ -L "${INSTALL_DIR}/${SCRIPT_NAME}" ]; then
    echo -e "${GREEN}✓ WomComp encontrado en ${INSTALL_DIR}/${SCRIPT_NAME}${NC}"
else
    echo -e "${YELLOW}⚠ WomComp no parece estar instalado en ${INSTALL_DIR}${NC}"
    echo -e "${YELLOW}  Continuando con la limpieza...${NC}"
fi

# 2. Detener procesos en ejecución
echo -e "${BLUE}[2/7]${NC} Verificando procesos en ejecución..."

if pgrep -f "launcher.py" > /dev/null; then
    echo -e "${YELLOW}⚠ WomComp está en ejecución. Deteniendo...${NC}"
    pkill -f "launcher.py" 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✓ Procesos detenidos${NC}"
else
    echo -e "${GREEN}✓ No hay procesos en ejecución${NC}"
fi

echo -e "${BLUE}[3/7]${NC} Eliminando comando ${SCRIPT_NAME}..."

if [ -f "${INSTALL_DIR}/${SCRIPT_NAME}" ] || [ -L "${INSTALL_DIR}/${SCRIPT_NAME}" ]; then
    sudo rm -f "${INSTALL_DIR}/${SCRIPT_NAME}"
    echo -e "${GREEN}✓ Comando eliminado: ${INSTALL_DIR}/${SCRIPT_NAME}${NC}"
else
    echo -e "${YELLOW}⚠ Comando no encontrado${NC}"
fi

if [ -f "/usr/bin/${SCRIPT_NAME}" ] || [ -L "/usr/bin/${SCRIPT_NAME}" ]; then
    sudo rm -f "/usr/bin/${SCRIPT_NAME}"
    echo -e "${GREEN}✓ Enlace eliminado: /usr/bin/${SCRIPT_NAME}${NC}"
fi


echo -e "${BLUE}[4/7]${NC} Eliminando archivos de configuración..."

if [ -d "$CONF_DIR" ]; then
    echo -e "${YELLOW}⚠ Eliminando directorio: $CONF_DIR${NC}"

    # Mostrar contenido antes de eliminar (opcional)
    echo "Contenido a eliminar:"
    ls -la "$CONF_DIR" 2>/dev/null || echo "  (vacío)"

    read -p "¿Eliminar configuración? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo rm -rf "$CONF_DIR"
        echo -e "${GREEN}✓ Configuración eliminada${NC}"
    else
        echo -e "${YELLOW}⚠ Configuración conservada en $CONF_DIR${NC}"
    fi
else
    echo -e "${GREEN}✓ No hay configuración que eliminar${NC}"
fi


echo -e "${BLUE}[5/7]${NC} Eliminando archivos compartidos..."

if [ -d "$SHARE_DIR" ]; then
    echo -e "${YELLOW}⚠ Eliminando directorio: $SHARE_DIR${NC}"
    sudo rm -rf "$SHARE_DIR"
    echo -e "${GREEN}✓ Archivos compartidos eliminados${NC}"
else
    echo -e "${GREEN}✓ No hay archivos compartidos que eliminar${NC}"
fi


echo -e "${BLUE}[6/7]${NC} Eliminando logs y cache..."


if [ -d "$LOG_DIR" ]; then
    sudo rm -rf "$LOG_DIR"
    echo -e "${GREEN}✓ Logs eliminados: $LOG_DIR${NC}"
fi


if [ -d "$CACHE_DIR" ]; then
    sudo rm -rf "$CACHE_DIR"
    echo -e "${GREEN}✓ Cache eliminada: $CACHE_DIR${NC}"
fi


if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR" 2>/dev/null || sudo rm -rf "$TEMP_DIR"
    echo -e "${GREEN}✓ Archivos temporales eliminados: $TEMP_DIR${NC}"
fi


echo -e "${BLUE}[7/7]${NC} Buscando archivos residuales..."

FOUND_FILES=$(find /home -name "*womcomp*" -o -name "*launcher.py*" 2>/dev/null | grep -v "\.pyc$" | head -20)

if [ -n "$FOUND_FILES" ]; then
    echo -e "${YELLOW}⚠ Se encontraron archivos residuales:${NC}"
    echo "$FOUND_FILES"
    echo ""
    read -p "¿Eliminar estos archivos? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$FOUND_FILES" | while read -r file; do
            rm -f "$file" 2>/dev/null || sudo rm -f "$file" 2>/dev/null
        done
        echo -e "${GREEN}✓ Archivos residuales eliminados${NC}"
    else
        echo -e "${YELLOW}⚠ Archivos residuales conservados${NC}"
    fi
else
    echo -e "${GREEN}✓ No se encontraron archivos residuales${NC}"
fi


echo ""
echo -e "${BLUE}Verificando dependencias Python...${NC}"

if pip3 list 2>/dev/null | grep -q "pyyaml"; then
    echo -e "${YELLOW}⚠ PyYAML está instalado en el sistema.${NC}"
    echo -e "${YELLOW}  Si fue instalado exclusivamente para WomComp, puedes eliminarlo con:${NC}"
    echo -e "    pip3 uninstall pyyaml -y"
    echo -e "    o"
    echo -e "    pip3 uninstall pyyaml --user -y"
    echo ""
fi


echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ WomComp ha sido desinstalado del sistema${NC}"
echo ""


if command -v womcomp &> /dev/null; then
    echo -e "${RED}⚠ ADVERTENCIA: El comando 'womcomp' todavía existe:${NC}"
    echo -e "  $(which womcomp)"
    echo -e "${YELLOW}  Es posible que necesites recargar tu shell:${NC}"
    echo -e "    exec bash"
    echo -e "    o"
    echo -e "    exec zsh"
else
    echo -e "${GREEN}✓ Comando 'womcomp' ya no está disponible${NC}"
fi

echo ""
echo -e "${YELLOW}Para una limpieza completa:${NC}"
echo -e "  1. Recarga tu shell: exec bash"
echo -e "  2. Limpia el cache de Python: find ~ -name '*pycache*' -type d -exec rm -rf {} + 2>/dev/null || true"
echo -e "  3. Elimina variables de entorno si las configuraste"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
