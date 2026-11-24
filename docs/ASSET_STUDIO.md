# Asset Studio — versão inicial

## Executar localmente

Requisitos: Git, Python 3.10+ (3.11 recomendado), Node 22/npm, navegador WebGL2. Na raiz do repo:
```powershell
npm --prefix tools/asset_studio install --ignore-scripts
python tools/asset_studio/prepare.py "$env:TEMP/frontline-studio"
python -m http.server 8765 --bind 127.0.0.1 --directory "$env:TEMP/frontline-studio"
```
Abra http://127.0.0.1:8765. Use um diretório vazio fora do checkout para cada preparação. Dependências Three.js 0.170.0 e Playwright 1.51.1 fixadas em package.json; instalação inicial requer internet, nenhuma CDN na execução. Não há instalador offline completo ainda. Em Linux substitua a pasta por /tmp/frontline-studio.

A interface apresenta os IDs reais do catálogo, pesquisa, filtro, variantes originais GLB e glTF, texturas/áudio, fontes, dependências, hash e estado de validação. Recurso é copiado e verificado, não reconstruído. Câmera perspectiva, OrbitControls e iluminação básica; próximos itens refinam controles, iluminação, métricas e inspeção. Sem prévia simulada para cenas procedurais; mostra aviso. O material do GLB não equivale aos overrides do Godot. Dependências glTF externas locais são permitidas, mas o hash de cada dependência ainda não é conferido no navegador; pacote verifica as cópias registradas. Teste Chromium carrega todos os GLBs existentes, confere caminho/hash e navegação; screenshots são evidência técnica, não aprovação manual. Sem alteração de modelos/gameplay. CI e revisão visual pendentes.
