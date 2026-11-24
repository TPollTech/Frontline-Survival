# Novo sistema de modelagem 3D e Asset Studio — especificação obrigatória

Solicitação do responsável pelo projeto em 24/11/2026. Estado: requisitos aprovados para planejamento; implementação e homologação pendentes. Aplica-se a **todo o conteúdo tridimensional**, sem exceção: armas e acessórios, personagens, mãos, roupas, equipamentos, NPCs, aliados, objetos, vegetação, veículos, construções, estações, terreno, mapas completos, cenas compostas e geometria criada em runtime. Preservar a jogabilidade atual e migrar por lotes verificáveis.

## Objetivo e referências

Criar uma biblioteca profissional, centralizada, reutilizável e extensível de modelagem procedural paramétrica, inspirada nos projetos [SNC Energies](https://github.com/TPollTech/snc-energies) e [SNC Adventures](https://github.com/TPollTech/SNC-Adventures), evoluída para um FPS com gráficos realistas, sem copiar limitações geométricas ou estética Minecraft.

Auditar nos dois repositórios, conforme existência, os arquivos:
- `tools/vehicle_library.py`
- `previews/vehicle-studio.js`
- `previews/vehicle-studio.css`
- `tools/vehicle_texture_kit.py`
- `tools/vehicle_verify_library.py`
- `tools/gen_estudio_armas.py`
- `AGENTS.md`

Registrar caminhos efetivamente encontrados, commits, arquitetura reutilizável e limites. Não presumir que os sete arquivos existem nos dois projetos. Auditar primeiro o Frontline Survival, incluindo GLB atuais, ModelSurface, scripts geradores, cenas Godot, materiais e assets em runtime.

## 1. Motor de modelagem

Biblioteca central em Python e integração com API do Blender quando necessário. Suportar primitivas avançadas, geometrias personalizadas, extrusão e revolução, operações booleanas, bevels e arredondamentos, curvas e superfícies orgânicas, normais suavizadas e ponderadas, UV mapping, materiais PBR, hierarquias, pivôs e encaixes, rigging/skeleton, colisões separadas da malha visual, LOD, exportação GLB/glTF 2.0 e geração reproduzível e determinística. Não limitar a modelagem a caixas, cilindros e primitivas simples. Criar formas apropriadas à silhueta, anatomia, materiais e referências visuais de cada asset.

## 2. Fonte canônica e contrato de integração

Cada modelo tem fonte principal editável (receita paramétrica, fonte Blender ou cena/procedimento canônico), responsável pela geometria e recursos. Corrigir sempre a fonte, nunca somente o exportado. Metros reais, coordenadas e convenções compatíveis com Godot (Y para cima, frente conforme o contrato de cada categoria). Manifesto com identificador estável, categoria, fonte, versão/hash, arquivos efetivamente usados pelo jogo, materiais/texturas, hierarquia, pivôs, colisões, LOD, animações, dimensões, orçamento e estado de validação. Geração repetível com dependências fixadas, sem fontes divergentes entre engine e Studio. Para cenas compostas, mapas e geometria gerada em runtime, exportar ou serializar a composição real e os parâmetros de geração em formato que o Studio possa reproduzir e verificar, mantendo as referências canônicas e transformações da engine. Não criar modelos substitutos apenas para preview; se uma representação de física ou efeito não for diretamente representável em glTF, documentar a limitação e fornecer o dado real de inspeção e evidência Godot.

## 3. Asset Studio

Estúdio independente em HTML, CSS, JavaScript, Three.js e WebGL. Descoberta automática dos assets reais do projeto pelo manifesto; adicionar modelos sem editar o núcleo do Studio.

Requisitos:
- catálogo por categorias, pesquisa e navegação; carregar GLBs reais e composições reais;
- antialiasing, sombras suaves, sRGB, ACES Filmic Tone Mapping, luz profissional e HDRI, piso neutro com grade técnica;
- OrbitControls com damping, enquadramento por bounding box, rotação, zoom, pan;
- vistas frontal, traseira, esquerda, direita, superior e perspectiva; vistas reais de primeira e terceira pessoa; mapas completos;
- materiais, texturas e UVs; wireframe, sólido, texturizado; normais, pivôs, colisões e LOD;
- contagem de vértices, triângulos, materiais e dimensões reais;
- reprodução de animações, poses e componentes articulados;
- screenshots, tela cheia, reset e versão offline (dependências e HDRI locais, sem dependência obrigatória de CDN);
- mesmas malhas, materiais, hierarquias e configurações da engine. Diferenças de shader/renderização entre Three.js e Godot devem ser documentadas e conferidas no Godot, não mascaradas por geometria independente.

## 4. Validação automática

Verificar geometria inválida, texturas ausentes, materiais incorretos, normais invertidas, escala e orientação, UVs, hierarquias quebradas, pivôs, referências inexistentes, exportação, excesso de polígonos e compatibilidade/importação Godot. Verificar correspondência entre catálogo, fontes, exports e recursos em uso. Testar reprodutibilidade e regressões. Definir orçamentos por categoria e nível de detalhe com benchmark no hardware-alvo Ryzen 5 7530U, GPU integrada, 8 GB RAM; preservar Godot Compatibility. Falhas e exceções precisam ser explícitas.

## 5. Portão obrigatório de qualidade visual

Cada modelagem:
1. Analisar referências visuais.
2. Definir proporções e dimensões.
3. Modelar a silhueta principal.
4. Desenvolver geometrias e detalhes secundários.
5. Aplicar materiais e texturas.
6. Exportar o modelo.
7. Executar verificações automáticas.
8. Abrir o modelo no Asset Studio.
9. Inspecionar visualmente todas as perspectivas relevantes.
10. Corrigir problemas diretamente na fonte e repetir exportação e verificações.
11. Integrar ao jogo.
12. Abrir o jogo e testar visualmente na escala, câmera, iluminação e animação normais.
13. Registrar evidências de validação, plataforma, versão/commit e resultados.

Para armas, verificar repouso, mira, recarga e partes móveis; para personagens, anatomia, deformação e animações; para mapas, composição completa, escala, colisões, iluminação, navegação e desempenho. Teste automatizado ou execução sem erro não significa aprovação visual. Sem Studio/renderização/inspeção efetiva, marcar parcial, explicar o bloqueio e não declarar homologação ou publicar como modelo aprovado. Captura gerada não equivale a captura inspecionada.

## 6. Integração e manutenção

Trabalhar na main, sem force push, preservar funcionalidades e aproveitar componentes adequados. Fazer migração incremental: inventário → fundação → Studio/validação → pilotos → categorias completas → integração/benchmark. Não remover legado antes de paridade e validação. Registrar testes, commits, limitações e documentação; atualizar [checklist mestre](CHECKLIST_MESTRE.md). O AGENTS.md torna este padrão obrigatório em todas as tarefas futuras. Correções urgentes de regressão podem ocorrer antes do novo pipeline, mas não dispensam registro da validação pendente. 
