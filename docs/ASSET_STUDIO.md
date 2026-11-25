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

## Validação de câmera e vistas

CI Pages 45475002613 (commit 3bcb7abcd57d0e6a5b2732f97de69a7eb7e27abd) aprovou STUDIO_CAMERA_PASS, STUDIO_VIEWS_PASS e 32 GLBs; deploy confirmado. Artefato 14959456264 SHA-256 conferido 8c81c9cd1e507c4c2f8bb6ff2da33ab3a04d08f2f13c8c3fa3feb78eb6c8a893. Inspecionadas as seis vistas, fullscreen, interação e janela estreita; a frente anatômica do modelo experimental está em +Z, diferente da convenção de inspeção frontal -Z, rótulos explicitam eixos. Não homologação de modelos.

## Capturas reais de runtime

capture_views.gd instancia scenes/main.tscn no Godot 4.4.1 Compatibility em perfil QA isolado e captura quatro PNGs reais: câmera FPS nativa após iniciar partida (HUD oculto), mapa inteiro ortográfico superior e perspectiva calculados a partir da AABB dos MeshInstance3D visíveis, e câmera externa QA de aliado real. O jogador possui somente rig FPS; não existe modelo completo do jogador ou modo TPS nativo. A câmera externa é explicitamente de inspeção do aliado. Piso, materiais, objetos, iluminação e shaders são da cena real, não reconstruídos em Three.js. O mapa captura estado inicial e não inclui todas as variações de partida. Não é mapa interativo 3D; exportação de buffers, animações e navegação real continuam pendentes. attach_runtime_views.py vincula os PNGs à revisão do catálogo, valida dimensões e hashes, mapeia IDs existentes e rejeita evidência incompleta. O Studio mostra as capturas em seletor separado, verifica SHA-256 e não habilita orbit/zoom 3D em imagem. O pipeline Pages e QA Chromium exige as quatro capturas, testa a seleção e o hash antes de publicar. CI e inspeção visual da nova entrega pendentes. Não houve alteração de gameplay ou geometria de produção.


## Revisão 00-13 — 24/11/2026

O carregador GLTFLoader utiliza um LoadingManager por modelo. Dependências externas declaradas pelo catálogo são verificadas com SHA-256, resolvidas a partir dos caminhos originais e entregues via URLs de objeto dos bytes verificados, sem download redundante. Recursos não catalogados são recusados; URLs de objeto temporárias são revogadas ao concluir ou falhar. O painel lista dependências do arquivo selecionado. Nenhuma malha de produção ou preview substituto foi criado. A regressão Chromium usa uma fixture neutra interceptada apenas no teste para verificar carregamento de buffer externo e recusa de bytes adulterados. O [CI 45501123164](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501123164) está em execução ao registrar esta revisão; não se afirma aprovação deste novo teste. Permanecem pendentes a inspeção visual manual, composições 3D runtime e homologação de modelos. A tarefa 00-13 fica parcial.


## Inspeção técnica 00-18 a 00-22 — 24/11/2026

A regressão anterior [45501123164](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501123164) terminou verde: 32 GLBs, quatro capturas Godot, navegação, verificação de dependência externa e recusa de adulteração. Pages [45501320706](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501320706) publicado. O build Windows [45501123202](https://github.com/TPollTech/Frontline-Survival/actions/runs/45501123202) falhou; não há nova release Windows homologada.

- 00-18: inspection.js preserva materiais originais, alterna sólido/wireframe/texturizado e canal de textura isolado do material selecionado; informa fatores PBR, resolução e espaço de cor. UV0/UV1 são desenhados dos índices e atributos reais, janela 0–1 e limite de 12 mil triângulos para manter responsividade. Ausência de UV/textura é explícita. Modo isolado é diagnóstico, não calibração fotométrica Godot.
- 00-19: VertexNormalsHelper em malhas estáticas (até 40 malhas e 50 mil vértices por malha); pivôs de até 100 nós reais. Captura adicional map_collision usa Shape3D.get_debug_mesh(), transform global real, colisores habilitados, sem teste de profundidade e sem sombras, somente em cena QA. As classes, caminhos, transforms e contagens são anexadas ao catálogo de capturas. O navegador mostra a captura estática e LOD bias real das instâncias; não há leitura de índices de LOD, troca de LOD real dos assets nem normais deformadas. Não inventar colisores ou tratar variantes de arquivo como LOD.
- 00-20: contagem de vértices/triângulos do buffer, geometria única versus instanciada, materiais, slots e texturas, dimensões AABB atual em metros e bounds. Métricas do arquivo original não mudam ao trocar o material de inspeção; bounds mudam com pose. Não representam custo de GPU, polígonos visíveis após culling ou medidas da composição Godot.
- 00-21: AnimationMixer reproduz clips reais; seleção, pausa, tempo e restauração; rotação local X/Y/Z em nós existentes, inclusive bones. Nenhum clip fabricado, nenhuma edição do GLB ou de gameplay. Animações de runtime, IK e limites articulares de produção não implementados. Auxiliares e sombras atualizam durante playback; métricas de pose limitadas a cerca de 8 Hz.
- 00-22: PNG do canvas renderizado sob comando do usuário. Workflow de QA empacota o diretório preparado em Frontline-Asset-Studio-offline.zip e SHA-256, inclui Three.js, licença, HDRI, catálogo e capturas; sem CDN. Após baixar e extrair o ZIP, executar `python serve_offline.py` na pasta e abrir http://127.0.0.1:8765/. Requer Python 3 e navegador WebGL2 já instalados; não é executável autônomo. O pacote é servido em loopback, não exige Git/npm após extração. O CI extrai o ZIP, inicia o launcher e verifica GLB e captura de colisão com conexões externas bloqueadas.

Implementação principal [adea181](https://github.com/TPollTech/Frontline-Survival/commit/adea181bf887bd44a67f614959dffc3c39426190); QA inicial [45502698035](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502698035) passou 32 GLBs e quatro capturas, antes dos testes dedicados. A etapa Godot e anexação das cinco capturas do [CI 45502851660](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502851660) passou; QA Chromium completo ainda em andamento no momento do registro. O [CI 45502974998](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502974998) cobre a revisão com testes de inspeção, fixture animada com contagens conhecidas, PNG, adulteração, zero rede externa e abertura do ZIP. Não afirmar aprovação até concluir e conferir logs. Não há inspeção visual manual confirmada, benchmark no hardware-alvo ou mudanças de modelos de produção; as cinco tarefas permanecem parciais até a validação necessária.


## Evidências posteriores e integração runtime — 24/11/2026

[CI 45502974998](https://github.com/TPollTech/Frontline-Survival/actions/runs/45502974998) aprovado: 32 GLBs, cinco capturas Godot, modos/UV/métricas/pivôs/pose/PNG, fixture de animação com contagens conhecidas, verificação de dependências e zero requisições HTTP externas. ZIP 10.563.017 bytes, extração e execução via serve_offline.py com rede externa bloqueada aprovadas. [Pages 45503148178](https://github.com/TPollTech/Frontline-Survival/actions/runs/45503148178) publicado. 00-22 concluída no escopo funcional de screenshot e pacote offline, não aprovação visual de modelos. 00-18/20/21 continuam parciais: revisão visual, cobertura de materiais/compostos e animação procedural pendentes; 00-19 sem índices reais de LOD.

O Studio agora seleciona estados reais do inventário por asset e mostra as métricas da subárvore, inclusive classes de colisão e bias. Pages/QA geram captura do inventário no mesmo checkout após import, validam e usam prepare.py --runtime antes de anexar as cinco vistas. O CI 45504658229 falhou no import por preload absoluto do seletor LOD; corrigido no commit 446f31eb, revalidação pendente. O build Windows anterior 45502975388 falhou no arsenal por compilação antecipada de GameSettings; o QA passa a carregar o script do jogador após verificar o autoload, sem alterar a lógica de combate ou remover asserts. A primeira tentativa 45504658424 foi bloqueada pelo preload LOD, logo não há evidência de correção definitiva do arsenal. Não houve revisão visual manual ou nova release homologada.

Revalidação 446f31eb: inventário e LOD aprovados (45504785941 e 45504785018). [CI de navegador 45504785180](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785180) e [Windows 45504785421](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785421) ainda em execução nesta verificação.


## 00-13 — Composições estáticas das superfícies reais do Godot

Preservados d2fa16a6 e sincronizações de evidências posteriores; alterações isoladas no coletor QA, preparação e interface do Studio, sem modificar gameplay/modelos de produção. CIs anteriores 45535950057, 45535950024, 45535950018 e 45535950052 aprovados; Pages confirmou f9fb9b1f em HTTP pós-deploy.

7f3eab79: `inventory_qa.gd` extrai arrays nativos de superfícies importadas e procedurais, com atributos packed em little-endian, base64 e SHA-256 de cada atributo. O hash da Variant original vincula os dados procedurais ao catálogo anterior. Pixels de texturas efetivas são extraídos como PNG do Image nativo, sem fabricar texturas. `runtime_composition.py` valida stride, contagens, índices, valores finitos, hashes e correspondência às métricas de todas as 86 amostras; `prepare.py` publica runtime_surfaces.json e sua revisão/hash. `runtime-composition.js` cria BufferGeometry dos atributos efetivos, inverte a ordem dos índices para converter clockwise Godot em counterclockwise Three, mantém matrizes mundiais capturadas, hierarquia e visibilidade, aplica materiais efetivos StandardMaterial3D com equivalências Three e texturas verificadas. Não cria geometria substituta. As normais ausentes são derivadas para visualização, explicitamente sinalizadas. A entrada "Reconstruir composição 3D" usa a amostra reconciliada selecionada; os GLBs originais e capturas nativas continuam acessíveis. 

[Inventário 45536901608](https://github.com/TPollTech/Frontline-Survival/actions/runs/45536901608) e [Studio 45536901798](https://github.com/TPollTech/Frontline-Survival/actions/runs/45536901798) aprovados. Artefatos 14986994630 e 14987413740 baixados; hashes dos arrays conferidos localmente, quatro capturas nativas e seis screenshots reais do navegador abertos. 199 buffers (165 procedurais de amostras + 34 importados), seis texturas, 86 composições/2996 registros de superfícies. Todas as superfícies capturadas são triângulos, com material StandardMaterial3D. Testes de navegador mediram:

| amostra | superfícies visíveis | triângulos visíveis | superfícies visíveis skinned sem pose |
|---|---:|---:|---:|
| map_briefing | 234 | 139656 | 0 |
| fps_rifle___hip | 33 | 82626 | 0 |
| enemy_soldier_rifle | 33 | 14426 | 0 |
| enemy_quaternius_experimental | 10 | 19852 | 3 |
| loot_ammo | 2 | 864 | 0 |
| turret | 2 | 1200 | 0 |

Contagens coincidem com relatório Godot; erro máximo de matriz mundial < 1e-5, na prática <= 6.67e-16. Comparação visual do mapa_overview nativo e map_briefing reconstruído: perímetro, contêineres, estações, barricadas e marcações reconhecíveis nas duas vistas. Câmeras e iluminação diferentes; sem equivalência pixel a pixel. Inimigos e luvas preservam o aspecto simplificado existente; experimental em repouso, não prova pose skinned. Detalhes triplanares na primeira revisão estavam pouco fiéis; título mostrava asset associado (p.ex. áudio) em vez da composição. A inspeção confirma identidade visual geral, não homologação artística. Browser também aprovou 32 GLBs e ZIP extraído offline (16.790.752 bytes); primeira revisão Windows 45536901596 aprovada.

0ac2a853 corrige o título, enquadra apenas geometria visível, bloqueia pose interativa em captura estática, inclui os dois buffers faltantes de LOD, acrescenta gate de contagem dos 12 níveis registrados de quatro barricadas e projeção triplanar aproximada de albedo usando escala/offset/normal capturados (não shader Godot completo; normal triplanar continua pendente). [Inventário final 45537702060](https://github.com/TPollTech/Frontline-Survival/actions/runs/45537702060) aprovado. Artefato 14988360598 baixado; 201 buffers portáveis, todos os 167 hashes procedurais incluídos, 942 atributos verificados localmente, seis texturas, 86 composições e 12 níveis com contagens corretas. O navegador 45537701973 ainda em execução ao registrar; capturas corrigidas não inspecionadas ainda. Publicação 45536901686 em execução, revisão final 45537701896 pendente; Windows 45537701885 cancelado após os testes iniciais (sincronização automática de imagens f8a02a34 posterior). Não afirmar novo deploy. Último deploy confirmado f9fb9b1f.

Limites: composição estática, não renderer Godot; não aplica skinning/blend shapes, shaders completos, triplanar de normal, ambiente/iluminação real ou composição de câmera/HUD da engine. Não promete paridade pixel a pixel; ângulos de comparação distintos. As 86 amostras foram validadas estruturalmente no staging, apenas seis renderizadas/inspecionadas nesta revisão. Ausências e aproximações são declaradas na interface. 00-13 permanece parcial; nenhum outro estado promovido. Próximos passos: conferir CI e publicação final, revisar novas imagens, comparar câmeras equivalentes, melhorar materiais e validar cobertura de renderização completa.


### Confirmação posterior da revisão 0ac2a853

[CI 45537701973](https://github.com/TPollTech/Frontline-Survival/actions/runs/45537701973) aprovado: STUDIO_SURFACE_STAGE_PASS 201 6 86, seis STUDIO_COMPOSITION_PASS com mesmas contagens/matrizes, STUDIO_OFFLINE_COMPOSITION_PASS 139656. Artefato [14988131278](https://github.com/TPollTech/Frontline-Survival/actions/runs/45537701973/artifacts/14988131278) baixado, seis capturas corrigidas abertas. Títulos/seleção de famílias coerentes; textura de concreto agora perceptível nas paredes, sem equivalência exata de iluminação ou triplanar; geometria e posições preservadas, personagem experimental em repouso. A prova de reconstrução estática offline é real, não equivalência à partida. Não promover homologação ou cobertura visual das outras 80 amostras. Pages 45536901686 ainda em teste de subrota na última consulta, revisão 0ac2a853 45537701896 não confirmada. 00-13 parcial.
