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

### Validação da iluminação

CI 45473901798 no commit 770971373f355d140a9eb93c35e061e663ad6fc1: 32/32 GLBs e parâmetros HDRI/ACES/sRGB/MSAA/PCFSoft, controles de grade, sombras e exposição aprovados no Chromium. Artefato 14959001472, SHA-256 conferido 22f58bb3016bd50ba17885bc1a73ba50e4dda8df9e41d2639a82a89a8c5a773e. Duas capturas 1440×900 inspecionadas: modelo experimental Quaternius visível, grade e sombra presentes na configuração padrão e ausentes na alternativa, exposição alterada. Piso relativamente claro e enquadramento com margem ampla; sem aprovação artística do personagem, comparação fotométrica Godot ou benchmark. Fundação da iluminação concluída; revisão de assets permanece nas tarefas de homologação.

## Navegação da câmera

camera-navigation.js encapsula OrbitControls, damping 0.09, mouse esquerdo gira, scroll/botões zoom, direito pan, toque de um dedo gira e dois dedos zoom/pan. Enquadramento analítico pelos oito cantos AABB na base da câmera perspectiva, margem 1.16, usando aspecto real. Preserva a geometria/transformações do asset; limites de zoom e pan proporcionais à escala e clipping baseado no raio. Reset recria OrbitControls para eliminar inércia residual. Resize reenquadra quando câmera está na posição inicial; caso contrário preserva navegação. Sem malha, controles desativados. Testes verificam projeção NDC de todos os GLBs, eventos reais mouse, zoom, pan, reset e viewport estreito. Vistas ortográficas, FPS/TPS reais e tela cheia seguem tarefas próprias. Não altera gameplay. CI pendente.

## Vistas ortográficas e tela cheia

Seis vistas em câmera OrthographicCamera real: frontal -Z, traseira +Z, esquerda -X, direita +X, superior +Y, inferior -Y. São eixos mundiais de inspeção, não uma inferência da frente anatômica do asset. Up explícito nos polos; rotação bloqueada nas ortográficas, zoom e pan mantidos. Fit por projeção AABB no plano da câmera e aspecto, reset na vista selecionada. Piso e grade ocultos somente na vista inferior, sem alterar preferências. Perspectiva restaurada pelo seletor. Tela cheia usa Fullscreen API no workspace, botão de saída e Escape nativo; falhas explícitas. CSS canvas absoluto evita realimentação de tamanho intrínseco. QA anterior 45474481782 falhou no resize (timeout linha 66), após interação e reset; deploy 45474481619 bloqueado. Novo teste usa largura 520 e compara aspecto medido do viewport, sem remover critérios de fit, além de validar eixos, projeções e fullscreen com capturas. CI novo pendente; sem alterações no jogo ou homologação visual.
