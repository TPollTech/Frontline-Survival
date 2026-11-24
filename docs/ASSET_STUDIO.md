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

## GitHub Pages

URL prevista: https://tpolltech.github.io/Frontline-Survival/. Em Settings → Pages → Source, selecionar GitHub Actions. O workflow Publish Asset Studio to GitHub Pages prepara uma pasta isolada com os recursos catalogados, dependências locais e interface; testa todos os GLBs em Chromium no subcaminho /Frontline-Survival/ antes de publicar, e confere HTML e revisão do catálogo após deploy. Executa a cada push na main e manualmente. Não publica a raiz do repositório. O catálogo publicado é gerado do checkout limpo (sem observações runtime da execução separada); composições procedurais continuam pendentes. A publicação é pública. Primeira execução pendente.

CI 45469214133: 32/32 GLBs carregados em Chromium/WebGL, 52 registros e 62 recursos do checkout limpo; artefato 14955803903. Revisão visual manual ainda pendente.

## Iluminação técnica

HDRI sintético original Radiance RGBE de 256×128, gerado localmente por generate_hdri.py e validado por SHA-256. Three.js RGBELoader decodifica o panorama linear HDR, PMREM gera iluminação/reflexos PBR. Não é fotografia HDRI externa. ACES Filmic, saída sRGB, MSAA solicitado, sombras PCFSoft de 1024², luz principal e piso neutro com grade de escala adaptativa 1/2/5×10^n metros; sem alterar transformações ou materiais dos modelos. Controles de exposição, grade e sombras. Piso/grade não pertencem ao asset; desaparecem sem malha. Shadow map recalculado ao trocar asset/controles, sem benchmark de GPU alvo. O CI de navegador verifica parâmetros reais, alternância e screenshots, além de carregar os GLBs originais. Sem equivalência fotométrica com Godot e sem homologação visual de modelos.

Pages anterior publicado e conferido no CI 45471098539 (commit ffa0a8dca1f08822640c806735d40b4b97507873). Nova iluminação aguarda testes e inspeção de capturas.
