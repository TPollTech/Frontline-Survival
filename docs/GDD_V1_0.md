# GDD mestre — Frontline Survival v1.0

**Documento:** GDD-001 • Versão 1.0 do planejamento • 11/11/2026  
**Produto:** Frontline Survival • **Stack:** Godot 4 Compatibility, GDScript, Windows x64 offline  
**Público-alvo:** jogador solo de FPS militares/Survival, com notebook de entrada  
**Hardware de referência:** Ryzen 5 7530U / Radeon integrada / 8 GB RAM  
**Direção:** espírito do Survival de MW3 (2011) em experiência original, **não uma cópia de assets, textos, mapas ou identidade**.  
**Situação:** **escopo proposto para fechamento de 1.0**; regras já aprovadas separadas das escolhas que precisam de aprovação do usuário. **Não corresponde a conteúdo atualmente implementado ou testado.**

> **Definição de 1.0:** jogo offline que abre com EXE próprio e pode ser jogado indefinidamente, com curva de ondas, dinheiro, três estações, armamento distinto, apoio funcional, um mapa definitivo otimizado, morte/recordes, menus/configurações, sons e identidade próprios. **Não existe última onda**: o objetivo final do jogador é o recorde; o objetivo final do projeto é passar no checklist e lançar uma build estável.

[Pesquisa MW3 2011](PESQUISA_MW3_SURVIVAL_2011.md) • [Plano de implementação 1.0](PLANO_ENTREGA_V1_0.md) • [Roadmap geral](../ROADMAP.md) • [Registro de decisões](REGISTRO_DECISOES.md)

---

## 1. A experiência: início, meio e fim

### 1.1 A partida (jogador)

**Início — ondas 1 a 5 (referência de onboarding, NÃO fim de fase).** O jogador começa com arma simples, pouca munição extra e dinheiro limitado; aprende atirar e recarregar, alterna cobertura, compra em estações físicas e experimenta o suporte básico. Inimigos comuns com avanço legível e kits curtos. A primeira compra útil deve ser possível sem grind desnecessário. Introdução contextual mínima somente na primeira partida; sem tutoriais cobrindo a tela constantemente.

**Meio — ondas 6 a 15.** Aumentam as combinações de armas inimigas, direções de chegada e pressão espacial; a gestão de dinheiro passa a exigir escolher entre armamento, proteção e reforço. A primeira ameaça blindada terrestre em onda-marco é anunciada e deve ter contra-jogo. O jogador começa a comprar uma arma principal de maior capacidade ou acessórios.

**Fim da curva introdutória — ondas 16 a 20.** Todas as famílias de combate e compras relevantes da 1.0 já foram apresentadas. Ondas-marco exigem movimentação, proteção e compras planejadas. Passar da onda 20 significa que o jogador domina as regras; **NÃO é conclusão ou créditos**.

**Endgame — ondas 21+.** Recombina as famílias, setores, avanços de armamento, blindados e pressão territorial de forma ilimitada, mantendo limites simultâneos de NPC e escalada com teto/curva justa. A única conclusão da sessão clássica é quando o jogador morre. Recordes e XP persistentes motivam voltar.

### 1.2 A produção (desenvolvimento)

- **Começo:** estabilizar o protótipo 0.9.3, homologar FPS/armas e eliminar defeitos P0.
- **Meio:** implementar diretor e IA de ondas, economia e suporte, mapa definitivo, progressão e qualidade audiovisual.
- **Fim:** testes integrados, otimização no notebook real, bugs P0/P1 resolvidos, build Windows, versão v1.0.0 em GitHub Releases e checklist de lançamento aprovado.

Esse é o **fim concreto do projeto base**. O que vier depois vira atualização 1.1/1.2 ou expansão 2.0, não bloqueia a 1.0.

---

## 2. Premissas não negociáveis (já estabelecidas)

1. FPS 3D **solo/offline**; sem campanha, multiplayer, co-op, sistema de contas ou monetização.
2. **Ondas contínuas**, com preparação após concluir a onda e avanço automático, nunca tela de vitória por limpar o mapa.
3. Preparação **ATUALMENTE 75 s**, opções **45–120 s** no código. **Revisão solicitada:** MW3 Survival (2011) usa 30 s; adotar **30 s como novo padrão proposto** com opções 30/45/60/75/90/120 s, sem sobrescrever configurações antigas; N antecipa somente na preparação. Ver adendo da pesquisa.
4. Estações físicas distintas: **armas, equipamentos e suporte**, acessadas por **F** ao se aproximar. Sem compras pelo B de qualquer posição.
5. Campo de Testes preservado para QA, inclusive textura de asfalto; mapa definitivo separado.
6. Reforços pagos e acionados depois: teclas **3 = esquadrão; 4 = aéreo**, desde que comprado.
7. Treino com reanimação opcional preserva dinheiro/onda/armas; clássico termina com morte e registra recorde.
8. **Sem crosshair 2D por padrão**; mira física alinhada ao disparo. Feedback de dano legível.
9. Configurações persistentes de áudio com volumes separados, sem apitos irritantes ou efeitos estourados.
10. Alvo mínimo: portátil Ryzen 5 7530U/8GB, compatibilidade/otimização desde o começo.
11. Entregar builds via **GitHub Releases**, jamais depender de anexos de chat; commits e status **CONCLUÍDO (CI), PARCIAL, PENDENTE, CONCLUÍDO (JOGO)**.

---

## 3. Escopo exato da versão 1.0 (proposta de congelamento)

| Sistema | Entra na 1.0 | Limite de escopo |
| --- | --- | --- |
| Modo de jogo | Survival clássico e Campo de Testes/treino | Sem missão narrativa/campanha |
| Mapas | **1 mapa definitivo: Complexo Industrial**, mais Campo de Testes separado | Não tentar 16 mapas na 1.0 |
| Ondas | Loop 1 a infinito; composição por 4 faixas e ondas-marco | Sem roteiro fixo de todas as ondas 1–100 |
| Inimigos | Soldado escopeta, operador SMG, fuzileiro, pesado com LMG e corredor leve (variação) | Sem helicóptero ou cão-bomba por padrão |
| Armas de jogador | **5 famílias base:** pistola, SMG, fuzil, escopeta e LMG | Uma arma representativa por família primeiro; sem arsenal com dezenas |
| Personalização de arma | **Obrigatório:** toda arma começa sem acessórios e pode comprar **Red Dot + Silenciador** simultaneamente; alternativas como holográfica/empunhadura | Sem gunsmith com dezenas de peças; valores/compatibilidade exatos sujeitos a balanceamento |
| Granadas | Granada de fragmentação e 1 equipamento tático simples | Sem física de destruição extensiva |
| Economia | Dinheiro por abate e habilidade, bônus de onda e compras seguras | Preços configuráveis; sem microtransações |
| Suporte | 1 tipo de torreta, esquadrão aliado pequeno e ataque aéreo/setorial | Sem drone pilotável, IA de equipe complexa ou dezenas de suportes |
| Progressão persistente | Até **20 patentes autorais**, desbloqueios de opções cosméticas/armamento e recordes | Nunca exigir online ou grinding extremo |
| Interface | Menu, mapa/modo, HUD leve, compras, pausa, controles, opções, fim da partida | Sem árvore de telas desnecessária |
| Áudio | Sons por arma, recarga mecânica, impacto, avisos de ondas e ambiência, mixagem | Sem usar arquivos sonoros de MW3 |
| Gráficos | Materiais e rig adequados, iluminação e efeitos controlados; LOD quando necessário | Sem metas fotorrealistas inviáveis no 7530U |
| Entrega | Windows x64 por GitHub Releases, ZIP com EXE/PCK e SHA-256, documentação de QA | Sem Android, Linux, Steam ou launcher próprio nesta versão |

**Critério de corte:** se uma função não reforçar sobrevivência, progressão, compras, combate ou legibilidade no 1.0, deslocar para backlog 1.1+.

### 3.1 Qualidade mínima visual

- Nenhuma arma inteiramente branca, com faces faltantes, atravessando a câmera ou parecendo apenas blocos sem materiais.
- Visor e direção real do disparo alinhados; sem crosshair, ADS reconhecível.
- Mãos do jogador agarradas ao gatilho/guarda-mão durante tiro, transição e recarga.
- Aliados/inimigos não podem ter cabeça flutuante, braço invertido, rifle fora das mãos ou pés desconectados.
- Silhuetas diferentes para jogador/aliados e para leve/fuzileiro/pesado.
- Tiro e recarga precisam soar mecânicos e coerentes com FPS; sons UI discretos.
- Não bloquear a 1.0 por uma exigência vaga de “AAA” ou por modelos com milhões de polígonos.

---

## 4. Diretor de partida e ondas

### 4.1 Máquina de estados obrigatória

\`MENU -> CARREGANDO_MAPA -> PREPARAÇÃO_INICIAL -> ALERTA -> COMBATE -> ONDA_CONCLUÍDA -> PREPARAÇÃO -> ...\`

Estados transversais: \`PAUSADO\`, \`LOJA_ABERTA\` (não altera o estado da onda), \`MORTE_TREINO -> REVIVER\`, \`MORTE_CLÁSSICO -> FIM_DE_PARTIDA -> MENU\`.

Invariantes:
- Cada onda nasce uma vez; número nunca decrementa.
- Fila de spawns não negativa, contador de vivos corresponde a NPCs existentes e vivos.
- Onda acaba **somente** quando a fila é zero e vivos é zero; finalizar no máximo uma vez.
- Inimigos eliminados por aliados, ambiente, granada ou jogador devem cair na mesma regra de contagem sem pagar duas recompensas.
- A preparação tem tempo suficiente para lojas e deslocamento; nenhuma loja deve interromper automaticamente a sessão inteira.
- Descarregar mapa, morrer ou voltar ao menu deve eliminar NPCs, suportes, timers e sinais da sessão anterior.
- RNG determinístico opcional por seed para reprodução de bugs.
- Se não houver spawn seguro, aguardar e registrar diagnóstico; existe um limite de recuperação sem travar para sempre a onda.

### 4.2 Curva de ondas (proposta, valores sob balanceamento)

| Faixa | Inimigos e pressão | Aprendizado | Marcos |
| --- | --- | --- | --- |
| 1–3 | Soldados básicos, armas curtas; pequenos grupos | Tiro, recarga, movimentação | Nenhum boss |
| 4–6 | Mais SMG/escopeta, entradas por 2 setores | Comprar arma/proteção | Onda 5: primeiro teste de pressão **sem blindado** |
| 7–9 | Fuzileiros leves, 1 corredor ocasional | Cobertura e flancos | Onda 8: primeira transição de armamento |
| 10–14 | Misturas de fuzis; **1 pesado anunciado na 10** | Preparar suporte, conter heavy | Onda 10: marco |
| 15–19 | Fuzil e LMG, entradas simultâneas de vários setores, corredor | Investimento tático e munição | Onda 15: pesado + escolta |
| 20 | Onda difícil mas justa, com limitado nº de pesados | Domínio do loop | Onda 20: marco sem tela de vitória |
| 21+ | Recombinação por seed/tier, limites de HP/DPS, ondas-marco recorrentes | Endgame sem repetição óbvia | Ciclo que nunca finaliza o jogo |

Os intervalos exemplificativos são **nossos**, não dados originais MW3. A progressão especial depende de dificuldade, como ilustram guias de MW3 de 2011–2012.

### 4.3 Quantidade e escalada

- **Configuração de partida inicial sugerida:** total aproximado 5 + 2 × onda com teto 55, inspirado na configuração atual; **limite simultâneo de 12** até benchmark.
- Nunca aumentar de uma vez saúde + precisão + danos + quantidade em uma mesma faixa.
- Progressão de risco mais por kits, posicionamento e composição que por “esponja de bala”.
- Ondas-marco não exigem combater 3 pesados simultaneamente se a GPU/arena não suportar.
- Inimigo especial anunciado por som grave, texto discreto e silhueta; deve ter preparo e counterplay.
- A onda deve ficar difícil por decisões ruins do jogador, não por spawn às costas em 1 metro ou acerto perfeito de NPC.

### 4.4 Dificuldade

**Proposta 1.0:** duas dificuldades no mapa definitivo: **Normal** (padrão) e **Veterano** (variantes de composição/reação); preparação **75s em ambas**, para preservar opção de tempo como configuração separada. Campo de Testes com assistência/revive.

Não criar quatro tiers de mapas até existir mapa suficiente; tiers de MW3 servem de referência histórica, não obrigação de v1.0.

---

## 5. Jogador, armas, controles e combate

### 5.1 Controle base

WASD movimento; mouse olhar; botão esquerdo atirar; direito ADS; R recarga; Shift correr; **C/Ctrl agachar e Z deitar (atalho proposto)**; F interagir; 1/2 trocar armas; 3/4 suporte comprado; N antecipar preparação; Esc pausar. Agachamento/prone devem alterar altura física do jogador e tiro, não somente velocidade. Se houver conflitos, mapear no menu e documentar; nunca escrever lista fixa em todo o HUD.

### 5.2 Armas de lançamento

| Família | Papel e alcance | Contrajogo/risco | Requisito audiovisual |
| --- | --- | --- | --- |
| Pistola | Reserva inicial, recarga rápida, tiro preciso | Munição/cadência limitadas | Ferrolho, inserção de carregador e som curto |
| SMG | Curta distância e mobilidade | Queda em distância média | Rajada ágil, ferrolho e carregador distintos |
| Fuzil | Versátil em média distância | Controle de recuo e custo | ADS estável, tiro mecânico grave e recarga elaborada |
| Escopeta | Controle de corredor e proximidade | Dispersão/alcance ruim | Pump/recarga realmente identificáveis |
| LMG | Volume de fogo e blindados | Mobilidade e recarga lenta | Caixa/tambor de munição, peso visual e som encorpado |

**Qualidade > quantidade:** cinco armas realmente distintas e aprovadas em câmera valem mais que 25 “armas-bloco”. Procedural pode ser usado nos modelos originais, mas cada peça precisa de materiais, proporções e grip plausíveis.

### 5.3 Tiro justo

- Raycast/colisão coerentes com o visor antes do recoil; sem crosshair sobreposta.
- Headshot com multiplicador e bonus monetário sem exploit.
- Feedback de impacto visual/áudio que não vira “bip” irritante.
- ADS reduz dispersão mas não garante precisão impossível; tiro em movimento tem penalidade moderada.
- Recarregar não concede munição gratuita e não fica preso em loops; animação/foley por classe.
- Distância e cobertura válidas: tiros inimigos não atravessam contêiner/parede.

---

## 6. NPCs, navegação e aliados

### 6.1 Arquétipos de NPC

- **Assaltante leve:** escopeta/SMG, pressiona curtas distâncias.
- **Fuzileiro:** mira em distâncias médias, protege avanços, não rastreia jogador através de paredes.
- **Corredor:** frágil, pressão curta e flancos legíveis.
- **Pesado blindado:** baixa velocidade, alto perigo frontal, passos distintos, ponto de vulnerabilidade e aviso prévio.
- **Metralhador:** supressão moderada em ondas altas, sem dano impossível de antecipar.

A diversidade visual deve permitir identificar tipo pela silhueta mesmo sem HUD; “trocar cor do mesmo boneco” não basta.

### 6.2 IA funcional mínima

Estados: \`NASCER -> AVANÇAR -> INVESTIGAR_ÚLTIMA_POSIÇÃO -> ATACAR -> REPOSICIONAR -> MORRER\`.
- Alvos reconhecidos por visão, com delay/reação.
- Navegação por caminho válido, não atravessar obstáculos, evitar empilhar 12 NPCs em mesma rota.
- Recuperação se não avançar por tempo prolongado; sem teleportar visivelmente.
- Mudar de comportamento por classe de arma.
- Prioridade de desempenho: IA 12 ativos + aliados/torreta dentro da meta.
- Sem necessidade de IA de aprendizado, comportamento estratégico complexo ou integração online.

### 6.3 Reforços aliados e armamento

- **Esquadrão:** até dois aliados de duração limitada; seguem jogador, se reposicionam, disparam somente em inimigos com linha de visão; não bloqueiam porta/estação permanentemente.
- **Torreta:** fixa, campo de tiro, tempo/munição e limite máximo; jogador não pode explorar torreta infinita.
- **Ataque tático:** área telegráfica e tempo de preparação; não ferir o jogador sem aviso ou quebrar contadores de onda.
- **Arte/rig:** cabeça conectada ao pescoço, mãos no rifle, pés/colisão alinhados e identificação de aliado clara.

---

## 7. Economia, estações, upgrades e progressão

### 7.1 Economia da sessão

Fontes: abate básico, headshot, sequência limpa, bônus discreto ao terminar onda. Anti-exploit: premiar **uma vez por NPC** e limitar farming por instâncias/torretas. Evitar economia inflacionária na onda 20 que torne compras irrelevantes.

Gastos: armas, munição, acessórios, proteção, explosivos, torreta, esquadrão, ataque. Compra só consome dinheiro se a entrega for válida. Reembolso/erro sem perda de saldo.

### 7.2 Estações físicas

| Estação | Conteúdo | Restrição |
| --- | --- | --- |
| Arsenal | Cinco armas, munição, dois acessórios simples | Comprar de perto com F; sem abrir à distância |
| Equipamentos | Colete, cura, granada, torreta | Limites e efeito legíveis |
| Suporte | Equipe aliada, ataque tático | Comprar antes; ativar depois com 3/4 |

HUD da compra exibe preço, saldo, descrição curta, posse e falta de dinheiro; controla mouse e pausa corretamente ao abrir/fechar.

### 7.3 Patentes persistentes (proposta de v1.0)

Até **20 patentes** com nomes autorais, XP por partida calculado de maneira transparente e desbloqueios modestos. **O progresso de patente NÃO concede vantagem permanente de dano/HP**; desbloqueia opções para comprar na partida, classes cosméticas ou registros. O jogador ainda deve comprar os itens com dinheiro em cada nova sessão.

Salvo localmente: XP/patente, recordes por mapa/dificuldade, opções e controles; não salvar sessão ativa nem garantir cloud sync na v1.0. Arquivos com versão de schema, migração/backup e tratamento de corrupção.

**Proposta a aprovar:** posição exata dos desbloqueios e XP por onda/abate, usando testes da economia.

---

## 8. Mapas e design de nível

### 8.1 Campo de Testes

- Não apagar: manter como laboratório sempre selecionável.
- Preservar asfalto original e sistemas atuais úteis.
- Permitir reanimação e testes de armas/suporte; não usar resultados de treino para recorde clássico.

### 8.2 Complexo Industrial — mapa oficial de v1.0

**Cinco setores propostos:** pátio central, galpão, administração/passarela, oficina e perímetro/depósitos. Geometria/rotas em blockout primeiro, depois arte. **Tamanho 110×90m é hipótese**, não medida final. Três lojas distribuídas, pelo menos dois caminhos para cada ponto defensivo e sem camping invulnerável.

- Ambientação militar-industrial **original**, placas e símbolos próprios.
- Todos os setores acessíveis no início — proposta; sem economias de portas desbloqueáveis no núcleo.
- 12–18 spawns candidatos com validação física/linha de visão/navegação (proposta).
- Não investir em iluminação/props definitivos antes do playtest de rotas, IA, lojas e FPS.
- Uma visão geral tática e marcos de interesse. Não construir vários mapas incompletos.

### 8.3 Outro mapa

O segundo mapa definitivo só entra em **1.1+**, após 1.0 estabilizada. Essa escolha mantém o começo/meio/fim da produção fechados.

---

## 9. Experiência e audiovisual

**Menu:** Jogar → selecionar modo/mapa/dificuldade → iniciar; Equipamento (desbloqueios) → Estatísticas/recordes → Opções → Sair.

**HUD durante combate:** vida/colete, dinheiro, munição, onda/inimigos e aviso curto. Sem mira 2D; ADS físico. Ameaças direcionais ao receber dano, mas discretas. Opcional de tamanho de fonte/contraste legível.

**Sons:** disparos e recargas por arma, impactos, passos, voz/ruído de soldados original, alerta de blindado e conclusão de onda agradável; bus separado master/combate/UI/ambiente. Limites de vozes simultâneas e testes com fones e alto-falantes do notebook.

**Arte:** modelos autorais de baixo/médio custo, materiais legíveis (PBR simplificado), 1 esquema visual de facção militar original e variantes de classe. Não reutilizar marca, logos e interface de Call of Duty.

---

## 10. Performance, distribuição e manutenção

Metas de aceitação:
- **720p, qualidade baixa, mínimo de 30 FPS medidos** em cenas de combate com 12 NPCs e suporte no notebook-alvo; desejar média de 60 FPS em cenas típicas. Registrar método, 1% lows e FPS no pior setor, não citar screenshot isolado como benchmark.
- Sem acúmulo progressivo de RAM/spawns/timers em **15 ondas** consecutivas; teste de onda 20+ recomendado.
- Sem bugs P0; **0 bugs P1 abertos que prejudiquem core loop, compras, IA, controles ou salvamento**.
- Sem crash/softlock em inicializar, fechar, pausar, morrer/reviver, usar lojas ou trocar mapa.
- EXE Windows via GitHub Actions/Releases, zip/sha256, changelog e instruções de instalação.
- Testar em ambiente real Windows, não só Godot headless; guardar relatórios por build/commit.

**Distribuição 1.0:** tag \`v1.0.0\`, release pública no GitHub com ZIP + checksum, notas de jogo, requisitos mínimos, changelog e possíveis problemas conhecidos não bloqueantes.

---

## 11. Critérios objetivos da v1.0 — TODOS obrigatórios para declarar lançado

| ID | Gate | Evidência obrigatória |
| --- | --- | --- |
| G1 | Jogo inicia pelo EXE Windows e menu funciona | Vídeo/captura e log de uma máquina real |
| G2 | Campo de Testes e mapa definitivo selecionáveis | Dois cenários válidos, início/saída sem vazamento de estado |
| G3 | 15 ondas consecutivas, depois 20+ sem softlock | Registro de onda, contagem, preparação e transição |
| G4 | 5 armas jogáveis, modelos/recargas/ADS aprovados | Tabela de testes por classe + feedback visual/sonoro |
| G5 | Inimigos leves, médios, rápidos, pesados diferenciados | Capturas/observação e casos de IA |
| G6 | Sistema de IA não prende ondas nem atravessa paredes | Testes de rotas e recuperação em ambos os mapas |
| G7 | Três lojas físicas, compras e suporte completos | 30 testes de compra/sem dinheiro/equipamento/sessão |
| G8 | Vida, morte clássica, treino/revive e recordes corretos | Testes independentes por modo |
| G9 | Patentes e recordes persistem ao reiniciar o jogo | Testes de salvar/carregar, migração e arquivo danificado |
| G10 | HUD, áudio e menus profissionais o suficiente para uso | Revisão visual/sonora com jogo real |
| G11 | Performance medida no hardware-alvo | FPS/1% low/memória nos cenários definidos |
| G12 | Build/release v1.0.0, checksum, docs e backup do repo | CI verde, Windows validado, release publicado |

**Qualquer G1–G12 não cumprido:** estado **pré-1.0 / Release Candidate PARCIAL**, ainda que a compilação passe.

---

## 12. Defeitos inaceitáveis de lançamento

- Arma sumida, branca, vazada ou cortando a câmera em uso normal.
- Aliado com cabeça flutuante, braços invertidos ou armamento separado das mãos.
- Tiro não acertar próximo ao ponto de mira física com arma estável.
- Apitos repetitivos, áudio clipping, volume impossível de controlar ou recarga sonoramente incoerente.
- Rodada que encerra o jogo ou trava quando o último inimigo morre.
- Inimigo aparece dentro da parede/jogador ou trava permanentemente sem recuperação.
- Loja cobra dinheiro sem fornecer item; arma não recarrega, suporte não dispara.
- Perda de configuração/progresso ao fechar normalmente; arquivo de salvamento corrompendo sem tratamento.
- Travamento ou degradação sustentada abaixo do piso mínimo em combate padrão no equipamento-alvo.

---

## 13. Riscos e decisão de corte

| Risco | Impacto | Mitigação |
| --- | --- | --- |
| Renderização e rig de armas ainda com qualidade inadequada | Alto | Revisão visual a cada build, usar referências de armas originais e rig verificável |
| IA com geometria complexa prende ondas | Alto | Navegação por região + recovery, testes de stuck e rota |
| Complexo Industrial grande demais para iGPU | Alto | Blockout e benchmark antes da arte |
| Economia trivial após 10 ondas | Médio | Simulações de créditos/munição e playtest de 5/10/15/20 |
| Suporte aliado quebrado | Alto | Pose e tiro em condições reais, não apenas runtime headless |
| Escopo crescendo até nunca lançar | Crítico | **Uma arena definitiva, 5 armas, 1 pesado e 3 apoios** como limite do MVP 1.0 |
| Só CI, sem teste real | Crítico | G1/G3/G4/G10/G11 dependem de Windows e aprovação |

---

## 14. O que NÃO entra na v1.0 (backlog fechado)

- Multiplayer, coop local/online, servidores, contas, rankings online, skins pagas.
- Mundo aberto, campanha com história, missões especiais roteirizadas.
- 16 mapas; produção de múltiplos mapas definitivos.
- Helicópteros ou animais explosivos; podem ser propostos para atualização posterior.
- Sistema de customização extensa de armas, veículos pilotáveis, física de destruição integral.
- Portas desbloqueáveis com economia separada, lootboxes, passes, monetização.
- Dublagem de campanha, cutscenes, streaming, achievements de plataforma.
- Port Android, Linux, consoles, Steam ou instalador próprio.
- Arte fotorrealista AAA ou modelos/áudios protegidos de MW3.

Aumentos de escopo propostos após aprovar este GDD ficam em **BACKLOG_1_1_PLUS.md**, não no bloqueio da v1.0.

---

## 15. Decisões que ainda precisam ser formalmente aprovadas

| Código | Decisão | Proposta padrão para fechar |
| --- | --- | --- |
| V1-P01 | Um mapa definitivo + laboratório na 1.0 | Sim |
| V1-P02 | Cinco armas representativas, uma por família | Sim |
| V1-P03 | Até cinco arquétipos de ameaça incluindo um pesado terrestre | Sim |
| V1-P04 | Duas dificuldades no mapa oficial | Normal e Veterano |
| V1-P05 | 20 patentes persistentes, desbloqueios sem bônus permanente de dano | Sim |
| V1-P06 | Red Dot e Silenciador em todas as cinco armas, comprados separadamente e ativos juntos; expansão opcional a grip | **REQUISITO DO USUÁRIO** quanto a attachments; detalhes de slots/custos ainda em proposta |
| V1-P07 | Sem helicópteros/cães-bomba na 1.0 | Sim; expansão posterior |
| V1-P08 | Todos os setores do mapa definitivo abertos desde o início | Sim |
| V1-P09 | Alvo de 30 FPS piso a 720p baixo, buscando 60 média | Sim, validar em hardware |
| V1-P10 | Versão pronta com G1–G12 completos | Sim, sem exceção |

**Até aprovação**, isso é um **GDD de escopo fechado proposto**, não uma declaração de que tudo foi decidido ou codificado.

**Próximo documento:** [PLANO_ENTREGA_V1_0.md](PLANO_ENTREGA_V1_0.md), com milestones, rastreabilidade, ordem de execução e critérios de encerramento.


---

## 16. Adendo de fidelidade MW3 — perks, desafios, relatório, attachments e posturas (11/11/2026)

**Origem:** pedidos explícitos do usuário para o Campo de Testes; respaldados por [pesquisa histórica específica](PESQUISA_MW3_SURVIVAL_MECANICAS.md) e especificados tecnicamente em [núcleo de mecânicas](NUCLEO_SURVIVAL_PERKS_ATTACHMENTS_MOVIMENTO.md).

### 16.1 Requisitos adicionados ao núcleo da 1.0

| Requisito pedido | Nova obrigação de produto | Documento de especificação | Estado real |
| --- | --- | --- | --- |
| Perks compráveis | Perks funcionais, adquiridos na estação de suporte; um ativo por vez, substituição clara | Núcleo §3 | **PENDENTE** |
| Last Stand | Estado de queda com pistola e chance de recuperar; Kit de Reanimação comprável na estação de equipamentos | Núcleo §4 | **PENDENTE** |
| Metas por dinheiro | Rampage, Killstreak, headshots, quadkill e variantes elegíveis conforme mecânicas existentes | Núcleo §2 | **PENDENTE** |
| Resumo de onda | Precisão, eliminações, headshots, tempo, dano sofrido, detalhamento do dinheiro recebido | Núcleo §1 | **PENDENTE** |
| Preparação | **30 s como novo padrão proposto** para novos usuários, opções maiores e antecipação N | Núcleo §1 | **75 s no código; alteração PENDENTE** |
| Attachments | Todas as cinco armas são básicas ao comprar; Red Dot e Silenciador comprados e instalados, visual e funcionalmente | Núcleo §5 | **PENDENTE** |
| Agachamento real | C/Ctrl reduzem altura de câmera/colisão e mudam mobilidade/tiro | Núcleo §6 | **PARCIAL:** atualmente só reduz velocidade |
| Deitar / prone | Postura rastejando, câmera/colisor e ADS adequados, trava ao tentar levantar sob teto | Núcleo §6 | **PENDENTE** |

As palavras **perk**, *Última Chance*, attachment e modelo de economia são regras de jogo; usar visual e nomes próprios. Nos guias de MW3 2011, **Self Revive é equipamento**, separado dos perks recebidos via suporte; não misturar Last Stand multiplayer com o funcionamento de Survival. O silenciador universal das cinco classes é uma extensão original requerida pelo usuário, **não** um item historicamente comprovado no armário de MW3 Survival.

### 16.2 Gates extras da v1.0

Adicionar aos gates existentes do §11:

- **G4 (armas):** cinco armas com as duas compras de acessórios funcionando e miretas corretas em ADS/crouch/prone.
- **G7 (economia/lojas):** desafios remunerados sem duplicidade, perks funcionais com um slot, kits de reanimação e compras entregues uma vez.
- **G8 (vida/morte):** Última Chance, sangramento, retorno por eliminação ou kit, derrota clássica e treino com revival sem exploração.
- **G10 (HUD):** resumo detalhado de cada onda e temporizador 30 s configurável; controles de agachamento/deitar.
- **G11 (desempenho):** sem degradar FPS ao exibir estatísticas/perks/efeitos de postura em 12 inimigos.

**Não aprovar gates a partir de documentação.** Faltam código, CI de integração e teste no Windows.

### 16.3 Sequência sem expansão de escopo

1. Concluir correção visual do soldado humanoide Quaternius e inspecionar a v0.9.14.
2. **CT-01 a CT-07** no Campo de Testes, na ordem definida no documento de mecânicas.
3. Só depois retomar mapas, helicópteros, camburões, novos tipos de inimigo e complexidade de ondas.
4. As propostas antigas V1-P01–P10 não estão todas aprovadas automaticamente; o pedido atual aprova **o objetivo de ter acessórios/perks/posturas**, não os preços, atalhos e percentuais exatos apresentados para design.

**Esta rodada somente atualiza documentação.** O status da versão executável permanece v0.9.14 até existir nova compilação testada.
