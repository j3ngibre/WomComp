#!/bin/bash

# WomComp Installer Script - Versión Corregida
# Instala WomComp como comando global

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           WomComp Installer v2.0                 ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

SCRIPT_DIR="$(pwd)"
LAUNCHER_FILE="launcher.py"


if [ ! -f "$LAUNCHER_FILE" ]; then
    echo -e "${RED}✗ Error: $LAUNCHER_FILE no encontrado en $SCRIPT_DIR${NC}"
    echo -e "${YELLOW}Ejecuta este instalador desde el directorio que contiene launcher.py${NC}"
    exit 1
fi


if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 no encontrado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3: $(python3 --version)${NC}"


if ! python3 -c "import yaml" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Instalando PyYAML...${NC}"
    pip3 install pyyaml --user
fi


if ! head -n 1 "$LAUNCHER_FILE" | grep -q "python3"; then
    echo -e "${YELLOW}⚠ Añadiendo shebang a launcher.py...${NC}"
    sed -i '1i#!/usr/bin/env python3' "$LAUNCHER_FILE"
fi


chmod +x "$LAUNCHER_FILE"
echo -e "${GREEN}✓ $LAUNCHER_FILE es ejecutable${NC}"


echo -e "${BLUE}Creando comando womcomp...${NC}"


if [ -f "/usr/local/bin/womcomp" ] || [ -L "/usr/local/bin/womcomp" ]; then
    echo -e "${YELLOW}⚠ Eliminando instalación anterior...${NC}"
    sudo rm -f /usr/local/bin/womcomp
fi


sudo tee /usr/local/bin/womcomp > /dev/null << EOF
#!/bin/bash
# WomComp - Linux Compliance Scanner

# Directorio donde está launcher.py
WOMPCOMP_HOME="$SCRIPT_DIR"

# Ejecutar con Python
exec python3 "\$WOMPCOMP_HOME/$LAUNCHER_FILE" "\$@"
EOF


sudo chmod +x /usr/local/bin/womcomp

echo -e "${GREEN}✓ Comando womcomp creado en /usr/local/bin/womcomp${NC}"


echo ""
echo -e "${BLUE}Verificando instalación...${NC}"
if command -v womcomp &> /dev/null; then
    echo -e "${GREEN}✓ WomComp instalado exitosamente en: $(which womcomp)${NC}"
else
    echo -e "${YELLOW}⚠ WomComp no está en PATH. Ejecuta:${NC}"
    echo "export PATH=\$PATH:/usr/local/bin"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Instalación completada${NC}"
echo ""
echo -e "${YELLOW}Prueba los siguientes comandos:${NC}"
echo -e "  womcomp -h          # Mostrar ayuda"
echo -e "  womcomp -c -v       # Usar cconf.yaml con verbosidad"
echo -e "  womcomp -b -s       # Usar bconf.yaml en modo silencioso"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
