# Frontline Survival — Etapa 1: Sensação de FPS, Armas e Apresentação

**Estado:** proposta detalhada de design; NÃO implementada e NÃO aprovada em bloco.  
**Data:** 10/11/2026  
**Dependência obrigatória:** [Etapa 0 — Estabilização](ETAPA_0_ESTABILIZACAO.md) aprovada e testada.  
**Documento pai:** [ROADMAP.md](../ROADMAP.md).

## 1. Objetivo da etapa

Substituir a sensação de "arma formada por caixas e uma bolinha amarela na ponta" por um FPS 3D militar original, legível e satisfatório, preservando fluidez no Ryzen 5 7530U / 8 GB. Primeiro acertar a sensação de apontar, disparar e recarregar; só depois investir em fidelidade visual mais alta.

### Não negociável — decisões da experiência já estabelecidas

- Jogo em primeira pessoa, armas modernas e progressão por ondas.
- Cinco famílias já presentes: pistola, submetralhadora (SMG), fuzil, escopeta e metralhadora leve (LMG).
- Disparo com mouse esquerdo, mira com direito, recarga R, armas 1/2, corpo a corpo E e granada G.
- Compras por F em estações; 3 para esquadrão comprado e 4 para suporte aéreo comprado; sem loja pelo B.
- Mapa de testes preservado, ondas contínuas e 75s de preparação.
- Visual e áudio próprios; não reutilizar recursos protegidos do MW3.
- Renderização com Godot Compatibility e foco no notebook de referência.

## 2. Direção artística — PROPOSTA a validar

**Estilo sugerido:** realismo estilizado militar da era PS3/Xbox 360, com proporções críveis, texturas limpas, detalhes concentrados nos objetos que ficam perto da câmera e orçamento baixo para objetos distantes. Não é visual cartunesco, mas também não pretende fotorrealismo moderno.

### Prioridade visual

1. Arma em primeira pessoa: silhueta, proporção, material, mira, coronha, cano, carregador e mãos.
2. Alvo e ambiente imediato: leitura do inimigo, posição, danos e cobertura.
3. Efeito de tiro: clarão breve, movimento do mecanismo, ejeção de estojo, fumaça discreta e impacto coerente.
4. Mundo e objetos distantes: bons materiais e silhuetas, sem geometria inútil.

### Regra de desempenho proposta

- Meta de teste: 1280×720 baixo e FPS mínimo desejado de 30 sob carga, tentando chegar a 60 nas cenas comuns; **não é benchmark medido**.
- Texturas de 1K como ponto de partida para arma em primeiro plano; usar menor resolução quando não houver ganho visual.
- Uma fonte principal de luz e efeitos transitórios de curta duração; evitar dezenas de luzes dinâmicas.
- Efeitos de impacto reaproveitáveis, com limite de instâncias e tempo de vida.
- Verificar o custo de material, transparência, sombras e draw calls no Compatibility, não confiar apenas na contagem de polígonos.

## 3. Armas — identidade por classe

Os valores abaixo são **hipóteses de balanceamento** para testes; NÃO refletem necessariamente a versão 0.7 e NÃO são regras aprovadas. Unidades de dano dependem da vida padrão escolhida na etapa de balanceamento.

| Classe | Papel pretendido | Capacidade sugerida | Cadência sugerida | Característica perceptível |
| --- | --- | --- | --- | --- |
| Pistola | Reserva confiável | 12 | Semiautomática, até 300–400 RPM | Controle simples, recarga rápida, dano moderado |
| SMG | Combate próximo e movimentação | 30 | 700–850 RPM | Baixo alcance, pouco peso, dispersão crescente |
| Fuzil | Uso versátil | 30 | 600–750 RPM | Controle intermediário, melhor precisão em média distância |
| Escopeta | Curtíssima distância | 6 | 60–100 RPM | Vários chumbos por tiro, ação mecânica evidente |
| LMG | Supressão e dano sustentado | 75 | 550–700 RPM | Mais recuo e lentidão, recarga longa |

### Parâmetros que cada arma deverá possuir (proposta técnica)

- ID, nome próprio, classe, preço, capacidade, munição reserva e tipo de disparo.
- Cadência, dano base, multiplicador de cabeça, alcance efetivo e queda de dano.
- Dispersão em movimento, em posição normal e mirando; padrão de recuo controlável.
- Velocidade de troca, tempo de recarga, velocidade ao correr, tempo para apontar (ADS).
- Recurso visual: modelo, mãos compatíveis, animações, som, clarão e ponto de ejeção.
- Regras de estoque/compras e compatibilidade com upgrades futuros.

**Proposta de implementação futura:** dados separados da lógica da arma. Evitar cinco cópias do mesmo script com números espalhados.

## 4. Sensação de tiro e movimentação

### 4A. Disparo

- Disparo instantâneo do ponto de vista da câmera para armas comuns; validar alinhamento entre centro da mira e ponto de impacto.
- Arma move e retorna após o tiro, com recuo vertical/horizontal coerente para cada classe.
- Modo automático mantém cadência estável, independentemente de pequenas oscilações de FPS.
- Mira em ADS modifica FOV e posição sem "pular" na tela; a arma nunca bloqueia o centro de mira.
- Marcadores de acerto e headshot discretos; não poluir HUD com texto permanente.
- Feedback de munição vazia visual e sonoro, sem gerar projéteis fantasmas.

### 4B. Movimento

- Caminhada, corrida, agachamento e salto com acelerações consistentes; sem sensação de flutuar.
- Bob/sway leve e parametrizado para não prejudicar mira nem provocar tontura.
- Transições separadas para parado, andando, correndo, mirando, atirando e recarregando.
- Prioridade de ações definida: recarga não pode criar tiro duplicado; pausa e compra devem interromper captura da câmera com segurança.
- Proposta ainda aberta: permitir ou não interrupção da recarga por troca de arma/corrida. Decidir após teste de sensação.

### 4C. Feedback ao receber dano

- Indicador direcional breve, diferença clara entre dano na vida e no colete.
- Sem flashes de tela intensos e contínuos; efeitos opcionais e discretos.
- O jogador precisa saber quando é atingido sem deixar de enxergar os inimigos.

## 5. Armas e mãos 3D: proposta de produção

### Modelo em primeira pessoa

- Criar modelos de armas originais com proporções e materiais coerentes. Usar nomes fictícios próprios, mesmo que a categoria lembre armamentos conhecidos.
- Mãos e antebraços devem ter anatomia reconhecível, luvas com separação visível dos dedos, punho e manga; evitar esferas e braços sem juntas.
- Usar esqueleto simples/rig para mãos e animações curtas, exportado de Blender para GLB.
- Separar mecanismos que se movem de verdade: slide de pistola; carregador; ferrolho; guarda-mão da escopeta.
- A mão de apoio deve acompanhar a arma; sem atravessar carregador ou cano nos movimentos.
- Definir ponto de câmera, ponto de mira, muzzle, ejeção e sockets de mão antes de animar.
- Se forem usados assets de terceiros no futuro, registrar autor, URL de origem, licença e alterações; nunca usar arquivos extraídos de outra franquia sem permissão.

### Biblioteca mínima de animações para cada arma

| Estado | Exigência visual |
| --- | --- |
| Equipada / idle | Pegada convincente, micro movimento sem exagero |
| Caminhar | Oscilação curta, sincronizada com passos |
| Correr | Arma em posição baixa e retorno controlado |
| ADS | Alinhamento nítido da mira com a câmera |
| Disparar | Recuo e movimento do mecanismo |
| Recarregar | Manipulação plausível do carregador/munição |
| Trocar | Saída e entrada sem sumiço instantâneo |
| Corpo a corpo | Golpe curto sem atravessar a câmera |

**Regra de escopo:** primeiro realizar esse conjunto inteiro em UMA arma piloto (fuzil); aprovar resultado antes de reproduzir nas outras quatro. Isso evita retrabalho.

## 6. Efeitos visuais — proposta

| Efeito | Comportamento desejado | Evitar |
| --- | --- | --- |
| Clarão de boca | Muito breve e proporcional à arma | Esfera amarela grande, luz permanente |
| Fumaça | Pequena, curta e opcional em qualidade baixa | Nuvem ocultando mira |
| Estojo | Ejeção discreta e breve; limitar objetos físicos | Dezenas de estojos permanentes |
| Tracer | Ocasional e curto; orientação correta | Lasers contínuos pela tela |
| Impacto em concreto/metal | Partículas e marca discretas, som por superfície | Mesmo efeito em todas as superfícies |
| Hitmarker / headshot | Informação curta de acerto | Popup excessivo em cada tiro |
| Dano recebido | Aviso direcional leve | Tela toda vermelha e opaca |

## 7. Áudio de combate — proposta

- Cinco timbres de arma distintos (pistola, SMG, fuzil, escopeta e LMG), incluindo disparo, eco/cauda, mecanismo e recarga.
- Mixagem sem clipping, respeitando volume geral e SFX independentes.
- Sons inimigos posicionados espacialmente, com distância audível e balanceamento que permita localizar perigo.
- Priorizar som de arma do jogador sobre tiros longínquos, sem estourar ou abafar avisos críticos.
- Estabelecer um limite de vozes simultâneas e fazer teste com 10+ inimigos e dois reforços.
- Sem música constante obrigatória; trilha e ambiência opcionais poderão entrar em etapa posterior.

## 8. Inimigos — interface com a Etapa 2

A Etapa 1 **não** substituirá toda a IA; só precisa assegurar que os tiros nos inimigos tenham efeitos coerentes. A Etapa 2 será responsável por arquétipos, modelos completos, cobertura, grupos e composição de ondas.

Nesta etapa, validar:
- Reação curta ao receber tiro que não "congele" permanentemente a IA.
- Morte e desaparecimento sem travar o contador de inimigos.
- Ponto de acerto de cabeça/corpo alinhado ao modelo visível.
- Nenhum ganho grande de qualidade nas armas à custa de quedas de FPS em múltiplos inimigos.

## 9. Entregas incrementais propostas

### 1A — Vertical slice do fuzil

- Um modelo/rig de mãos original, uma arma piloto e estados mínimos completos.
- ADS, recuo, disparo, recarga, troca, corrida e áudio do fuzil.
- Captura de referência na mesma área do Campo de Testes.
- **Aceite:** arma piloto claramente crível na câmera e sem regressões em compra/onda.

### 1B — Família de armas

- Aplicar o padrão visual/animação às quatro classes restantes.
- Cadência, dispersão, recarga e papel de combate diferentes.
- **Aceite:** identificar a categoria jogando, sem ler o HUD.

### 1C — Feedback e otimização

- Efeitos por superfície, áudio espacial, danos, hitmarkers e orçamento de partículas.
- Medir combate na onda 5, 10 e 15, comparando com os testes da Etapa 0.
- **Aceite:** efeitos legíveis, sem clipping ou regressão séria de FPS.

### 1D — Revisão e entrega

- Revisar controles, compra de armas, animações, acessibilidade básica e regressão.
- Atualizar README, changelog, vídeos/capturas de referência e relatório de QA.
- **Aceite:** todos os critérios abaixo medidos e aprovados; sem P0 abertos.

## 10. Critérios de conclusão da Etapa 1

- [ ] Cada uma das cinco classes tem silhueta e comportamento distintos.
- [ ] Armas não parecem blocos simples na visão em primeira pessoa.
- [ ] Mãos, luvas e antebraços acompanham recuo, recarga, ADS e troca sem atravessamentos gritantes.
- [ ] Não existe a bola amarela permanente nos disparos.
- [ ] Áudio é regulável e não apresenta clipping observável nos testes.
- [ ] Headshot, dano e munição fornecem feedback claro e discreto.
- [ ] Não ocorre bloqueio de tiro ou mira após usar menus, lojas ou recarregar.
- [ ] Ondas 1–15, estação F, suportes 3/4 e ambos modos de morte seguem funcionando.
- [ ] FPS foi medido no notebook e comparado à linha de base, sem queda inaceitável.
- [ ] Modelos e áudios são próprios ou têm licenças verificadas e registradas.

## 11. Fora de escopo desta etapa

- Primeiro mapa definitivo e sistema de seleção de mapas.
- Cooperativo/multiplayer.
- Árvores extensas de acessórios, skins e progressão de conta.
- Nova IA tática avançada e chefes especiais.
- Clima dinâmico, ray tracing e fotorrealismo.
- Refatoração grande sem relação com bugs ou com a nova apresentação.

## 12. Decisões pendentes de aprovação

| Tema | Proposta inicial | Situação |
| --- | --- | --- |
| Padrão visual | Realismo estilizado militar leve | A aprovar |
| Arma piloto | Fuzil como primeiro vertical slice | A aprovar |
| Mãos | Rig leve e animações de recarga reais | A aprovar |
| Modo de tiro | Hitscan para armas comuns, pellets na escopeta | A aprovar |
| Números de armas | Faixas de capacidade e cadência da seção 3 | A balancear |
| ADS / sway | Suave, sem excesso de câmera | A aprovar |
| Interrupção de recarga | Avaliar após testar o fuzil | Em aberto |
| Modelos externos | Apenas originais ou licenciados com registro | Regra de produção proposta |

**Próximo passo após Etapa 0:** aprovar estética, arma piloto e lista de estados de animação antes de criar modelos ou alterar scripts.


---

## 13. Revisão de escopo — attachments e posturas (11/11/2026)

**Solicitação expressa:** personalização das cinco armas por compras individuais na estação física do arsenal, Red Dot/Silenciador inicialmente ausentes, além de agachar e deitar realmente. A aparência de arma "quadrada" e as deformações de humanoide ainda exigem qualidade antes de expandir mapas. [Especificação integral](NUCLEO_SURVIVAL_PERKS_ATTACHMENTS_MOVIMENTO.md).

### Attachments obrigatórios no núcleo

1. Toda arma comprada e toda arma básica recolhida inicia **sem attachment**.
2. **Todas as cinco famílias** (pistola, SMG, fuzil, shotgun, LMG) precisam suportar *Red Dot + Silenciador* comprados separadamente e equipáveis juntos.
3. Holográfica, grip, compensador ou choke podem ser alternativas compatíveis por classe; não é necessário um gunsmith complexo.
4. A mira adicional existe como **modelo 3D**, alinhado ao disparo em ADS. Proibida retícula fixa no centro da tela, conforme decisão anterior.
5. Silenciador com modelo próprio, **efeito e áudio WAV apropriado**; não reutilizar som sintetizado inadequado ou apenas reduzir volume sem verificar o resultado.
6. Trocar arma preserva os attachments dessa arma na sessão, sem multiplicar estatísticas. Arma do chão não herda acessório do jogador por engano.
7. Preços/atributos numéricos são **propostas** até balanceamento real.

### Agachado / deitado

- \`C\`/\`Ctrl\` agachar, \`Z\` deitar como configuração proposta. Implementação atual de \`C\`/\`Ctrl\` só altera velocidade — **incompleta**.
- A postura deve reconfigurar altura da câmera e da \`CapsuleShape3D\`, a origem do tiro e ADS, com interpolação suave e teste de teto para levantar.
- Deitar não permite correr/saltar; rastejamento lento, recoil e visão específicos. Não escalar colisor global nem atravessar sólidos.
- Validar cinco armas e anexos em pé/agachado/deitado.

### Critérios de aceite adicionais

| ID | Verificação | Status |
| --- | --- | --- |
| A1-13 | cinco armas básicas sem mira extra/silenciador no início | **CONCLUÍDO (CI)** — inicial sem acessórios, testes em cinco armas |
| A1-14 | Red Dot + Silenciador juntos por arma; compra sem saldo, troca e drop | **PARCIAL** — Red Dot + Silenciador juntos, compra e troca no CI; testar coleta e saldo em jogo |
| A1-15 | visor e ponto de tiro alinhados em ADS para cada arma e acessório | **PARCIAL** — ótica 3D da v0.9.17, alinhamento balístico não homologado visualmente |
| A1-16 | sons e visual do disparo com silenciador coerentes, sem beep | **PARCIAL** — WAV com bus SUPPRESSED, som/visual exigem avaliação no Windows |
| A1-17 | agachar muda altura física, não só movimento | **CONCLUÍDO (CI)** — altura da cápsula do agachamento verificada |
| A1-18 | deitar/rastejar e levantar sem atravessar teto ou atravessar obstáculos | **PARCIAL** — prone, rastejamento e colisor existem; teto/ADS exigem teste |
| A1-19 | FPS e estabilidade com os acessórios equipados + NPCs no Campo de Testes | **PENDENTE** — sem benchmark de FPS no notebook |

**Ordem:** CT-03 (posturas) e CT-04 (attachments), depois de garantir o básico do Campo de Testes; sem implementar nova arena nesta etapa. **Nenhuma mudança de código nesta rodada documental.**

---

## Auditoria de progresso — 12/11/2026

Na checklist principal desta etapa há **2 critérios concluídos em código/CI, 4 parciais e 4 pendentes**. Os sete critérios adicionais de attachments e posturas foram atualizados na própria tabela. A Etapa 1 continua **PARCIAL**: há cinco armas e mecânicas funcionais, porém ainda faltam modelos de mãos com rig anatômico, aceitação visual do ADS/Red Dot e FPS medido no Ryzen 5 7530U. [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md) · [Build v0.9.17](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.17).
