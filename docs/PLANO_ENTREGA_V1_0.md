# Plano de produção — Frontline Survival 1.0 (milestones e critérios)

**Planejamento realizado em 11/11/2026.** **Estado: PROPOSTO**, com pontos aprovados identificados no [GDD](GDD_V1_0.md) e [Registro de decisões](REGISTRO_DECISOES.md). Este documento não altera scripts, cenas, assets nem builds.  
**Ponto de partida:** v0.9.3 publicada em GitHub Releases; CI Godot e primeiras duas ondas automatizadas passaram, porém avaliação visual/áudio da versão, teste Windows de 15 ondas, mapa oficial e progressão ainda faltam. Não confundir “documentado” com “desenvolvido”.  
**Norte de referência:** [Pesquisa MW3 Survival de 2011](PESQUISA_MW3_SURVIVAL_2011.md).  
**Condição para v1.0.0:** todos os **G1–G12** do GDD aprovados por evidências, sem bugs P0/P1 e com build Windows testada.

## 1. Três atos de produção — começo, meio e fim

| Ato | Marcos | Estado do produto |
| --- | --- | --- |
| **Ato I — Fundamento jogável (0.9.x)** | M0, M1, M2 | Campo de Testes estável; tiro/arma/aliados aprovados; diretor e IA confiáveis |
| **Ato II — Conteúdo completo (0.9.x até 0.10.x)** | M3, M4, M5 | Economia, suporte, progressão, mapa Industrial e menus/audio completos |
| **Ato III — Produto final (RC → 1.0)** | M6, M7, M8 | Otimização, QA de 15/20 ondas, assinatura de checklist e release v1.0.0 |

Versões intermediárias não precisam de número 0.10; o número deve crescer de maneira coerente com o histórico, sem reciclar releases. Não prometer datas: cada milestone fecha com critérios, não com uma estimativa sem teste.

## 2. Marcos detalhados com ordem de implementação

### M0 — Congelamento do escopo e regressão crítica

**Objetivo:** fechar 10 decisões V1-P01 a V1-P10; preservar sistemas e remover bugs que tornam novos sistemas instáveis.

**Tarefas:**
- Revisar/aceitar escolhas de mapa, cinco armas, classes e exclusões de escopo.
- Manter GitHub README, ROADMAP e testes de versão sincronizados.
- Executar versão atual no Windows real e confirmar armas coloridas/texturizadas, visão ADS, suportes sem cabeça flutuante e recarga adequada.
- Testar compra de uma arma, compra de suporte, morrer, reviver, pausar e completar cinco ondas.
- Se houver P0 de arma, animação, sons, input ou UI, corrigir ANTES de redesenhar o mapa.
- Registrar baseline real de FPS e RAM para 720p low.

**Aceite M0:** checklists preenchidos por teste real, não apenas CI; nenhum P0 no Campo de Testes; 5 ondas com compra e suporte. **Dependência para M1/M2.**

### M1 — Armas, feedback e animação de combate aprovados

**Objetivo:** deixar cinco armas jogáveis com qualidade plausível para lançamento, sem exigir AAA.

**Tarefas:**
- Cada modelo deve ser opaco, colorido, com materiais coerentes, silhueta reconhecível e proporção natural.
- Mãos corretas em gatilho/guarda-mão; não atravessar a arma nas transições e recargas.
- Posição da mira física corresponde ao raycast nas cinco armas. Sem crosshair sobreposta.
- Sons mecânicos próprios por arma para disparo, recarga, empty, impacto, passos.
- Limitar áudio de repetição e volumes; não usar beep agudo a cada acerto.
- Balancear dano, alcance, dispersão, recoil, cadência, munição, tempo de recarga e mobilidade por arma.
- Definir 2 acessórios simples, se aprovados, sem dependência obrigatória para as cinco armas.

**Aceite M1:** 5/5 armas inspecionadas visualmente e testadas em Windows; todos os disparos e recargas funcionam; mira estável, voz e animações sem defeitos P1; relatório de parâmetros por classe. **G4 parcial→completo.**

### M2 — IA e ondas robustas

**Objetivo:** inimigos têm papéis distintos, e nenhuma onda se perde ou trava.

**Tarefas:**
- Separar WaveDirector da cena de mapa de modo incremental, preservando teste de regressão.
- Reconciliar spawn_remaining, alive e inimigos reais vivos; garantir conclusão uma vez.
- Validar spawn de setor, linha de visão, distância/ocupação, prioridade fora do FOV e rotas.
- Criar navegação por mapa e anti-travamento com métricas. Não usar teleporte visto pela câmera.
- Definir soldados básicos, SMG, fuzileiro, corredor e pesado com silhuetas e comportamentos.
- Construir diretor por faixas 1–3, 4–9, 10–14, 15–20, 21+, com ondas-marco e warnings originais.
- Escrever testes: 100+ spawns por posição, 2 ondas completas em CI, 5 e depois 15 ondas reais, múltiplas mortes simultâneas, última unidade presa, aliados matando NPC.
- Limitar 12 inimigos simultâneos inicialmente; só ajustar após benchmark.

**Aceite M2:** ondas 1–15 em Campo de Testes, 100 spawns sem sobreposição, contador consistente, nenhum NPC impede fim de onda, classes distintas. IA sem atravessar colisões. **G3, G5, G6.**

### M3 — Economia, três estações e suporte

**Objetivo:** dinheiro, compras e reforços realmente criam decisões de sobrevivência.

**Tarefas:**
- Separar saldos, inventário, loja e scripts de suporte sem perda de estado entre ondas.
- Configurar tabela de custos e recompensas com limites, reembolsos e avisos.
- Atribuir headshot, clean wave e pequenos bônus com proteção a duplicidade.
- Arsenal: armas, munição e acessórios permitidos; equipamentos: proteção/granada/torreta; suporte: esquadrão/ataque.
- Usar F só em alcance; garantir loja acessível durante preparação e em combate.
- Melhorar inteligência do suporte para não atirar em paredes, não bloquear jogador ou ficar com pose quebrada; suporte comprável depois ativado via 3/4.
- Testar 30 cenários, incluindo item comprado duas vezes, sem dinheiro, troca durante reload, morte ao comprar, modo clássico, último NPC morto por aliado.

**Aceite M3:** cada compra entrega o item correto uma vez; saldo e inventário fiéis; dois aliados, torreta e ataque funcionam. Economia equilibrada em ondas 5/10/15/20, sem riqueza infinita. **G7.**

### M4 — Complexo Industrial completo e jogável

**Objetivo:** 1 mapa definitivo além do Campo de Testes, sem duplicar lógica.

**Tarefas:**
- Definir layout final após blockout. Proposta: cinco setores — pátio, galpão, administração, oficina e perímetro.
- Extrair MapDefinition/MapLoader; Campo de Testes vira cena separada sem regressão.
- Construir rotas, duas vias de acesso a pontos defensivos e navegação IA para térreo e passarela.
- Inserir três estações e 12–18 candidatos de spawn seguros; ajustar por teste e distância.
- Revisar coberturas, ângulos, iluminação, sinalização original, ambientação, texturas e otimização.
- Simular movimentação em preparação de 75s: lojas não podem ficar distantes demais.
- Testar spawn, circulação, ataque de pesado, aliados e torreta em todos os setores.

**Aceite M4:** dois mapas selecionáveis (laboratório e Complexo Industrial), 15 ondas no mapa novo, lojas e suportes integrados, FPS dentro de metas e sem IA presa em setores. **G2 e parte de G6/G11.**

### M5 — Progressão, recordes, interface e áudio integrados

**Objetivo:** o jogo parecer um produto completo, e não uma demo.

**Tarefas:**
- Menu: Jogar, mapa, dificuldade, Configurações, Recordes/Patentes, Créditos, Sair.
- Salvar localmente modo, mapa, onda recorde, XP/patente e preferências; schema versionado e migração de dados antigos.
- Criar até 20 patentes autorais, desbloqueios de opções (não buffs permanentes).
- HUD legível e compacto, sem retícula 2D; mensagens não poluem a câmera.
- Sons ambiente, arma, recarga, onda, ameaça especial, compra e fim de partida; buses separados e limites de volume.
- Fluxo de derrota, recorde e reinício de partida por mapa/modo/dificuldade.
- Tela de ajuda/controles simples acessível no menu; sem tutoriais incessantes na partida.

**Aceite M5:** menus, áudio, controles e gravação corretos após 3 reinícios; dados corrompidos tratados; 10 sessões curtas sem perda de recorde ou mistura treino/clássico. **G8, G9, G10.**

### M6 — Balanceamento e performance no hardware-alvo

**Objetivo:** sobreviver e tomar decisões seja divertido; hardware mínimo é atendido.

**Tarefas:**
- Teste da progressão 1–20; média da duração da onda, moedas ganhas/gastas, munição, uso de suporte.
- Balancear por **uma variável de cada vez**, sem inflar simultaneamente vida, precisão e quantidade.
- Meta 720p baixo: piso medido de **30 FPS em combate típico**; 60 média como desejo, não requisito impositivo.
- Medir FPS médio, 1% low, RAM e CPU com 12 inimigos e suporte ativo, por setor.
- Cache/LOD e redução de luzes, partículas, áudio, materiais e atualização de IA, conforme benchmark.
- Garantir que exportação Windows e máquinas de baixa memória não travem ao abrir/fechar.

**Aceite M6:** relatório reproduzível em notebook e configuração 720p/baixo, sem queda progressiva ou vazamento em 15/20 ondas. **G11.**

### M7 — Release Candidate (RC)

**Objetivo:** congelar features, caçar bugs, homologar todo o percurso.

**Tarefas:**
- Congelar conteúdo; somente correções P0/P1 e polimento com risco baixo.
- Matriz de regressão: iniciar EXE, mapas/modes, 5 armas/ADS/reload, 3 lojas, suportes, inimigos/ondas, save, áudio, pausa, 15 ondas (dois mapas) e 20+ (pelo menos um mapa).
- Remover todo bug P0 e P1; fazer 3 sessões completas sem falha crítica.
- Validar salvamento após fechamento normal e interrupção; sem transação duplicada.
- Conferir licença de todos os assets, origem dos sons/texturas e consistência dos nomes.
- Revisar notas da versão, requisitos mínimos, comandos, changelog, screenshot e checksum.

**Aceite M7:** relatório de RC com evidências G1–G12; sem P0/P1 abertos; não é obrigatório não ter absolutamente nenhum P2 cosmético. **G1–G12.**

### M8 — Lançamento v1.0.0

**Objetivo:** lançar um produto completo, ainda que pequeno em quantidade de conteúdo.

**Tarefas:**
- Tag imutável v1.0.0 com commit da build aprovada.
- Exportar Windows release sem console indevido, com EXE/PCK e ZIP + SHA-256.
- Publicar GitHub Release estável (não marcada como pré-lançamento), notas, limitações e requisitos reais.
- Registrar versão/commit, testes de instalação, captures de menu/mapa e resultados de benchmark.
- Marcar milestones **CONCLUÍDOS (JOGO)** no ROADMAP, cada qual com evidência.
- Abrir backlog v1.1+ só depois do lançamento, sem comprometer v1.0.

**Aceite M8:** download público funciona, EXE roda em Windows limpo e release contém todos os artefatos/referências; jogo pode continuar ondas até o jogador morrer. **G12.**

---

## 3. Quadro de dependências

\`M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8\`.

Pode haver prototipação paralela de arte/sons, mas **não declarar milestone concluído** antes de todas as dependências. A Etapa 6 de QA/performance é transversal e tem gates durante M0–M8.

Evitar investir meses em um novo mapa enquanto as armas ou aliados ainda aparecem deformados: estabilização visual inicial é bloqueante para a percepção de qualidade.

## 4. Matriz de rastreabilidade

| Milestone | Etapa do roadmap | Gate GDD |
| --- | --- | --- |
| M0 | 0 — Estabilização | G1, G3 base |
| M1 | 1 — FPS/armas | G4 |
| M2 | 2 — IA/ondas | G3, G5, G6 |
| M3 | 3 — Economia/suporte | G7 |
| M4 | 4 — Mapas | G2, G6 |
| M5 | 5 — HUD/UX/audio + progressão | G8, G9, G10 |
| M6 | 6 — Performance | G11 |
| M7 | 6 — QA integrado | G1–G12 |
| M8 | 6 — Distribuição | G12 |

**Requisito de status:** marcar cada tarefa com *PENDENTE*, *EM EXECUÇÃO*, *PARCIAL*, *CONCLUÍDO (CI)* ou *CONCLUÍDO (JOGO)*. O último exige aceite real.

## 5. Matriz de testes mínima por camada

| Camada | Ambiente | Gate |
| --- | --- | --- |
| Arquivos | Verificador estático Python/GLB/WAV | Parser/arquivos sem falhas |
| Godot headless | CI Ubuntu | Importação, cena principal, 100 spawns, 2 ondas reais, aliados, cores |
| Windows ZIP | GitHub Releases + Windows real | EXE inicia; pastas/recursos funcionam |
| Jogabilidade curta | Notebook real | 5 ondas, 5 armas, 3 lojas e suportes |
| Jogabilidade longa | Notebook real | 15 ondas cada mapa; 20+ pelo menos um |
| Persistência | Windows real | salvar/reiniciar/corromper arquivo |
| Desempenho | Ryzen 5 7530U e 8 GB | 720p/baixo, ≥30 FPS em combate típico |
| Release final | GitHub | tag, checksum, changelog, requisitos e resultados QA |

## 6. Padrão de relatório de cada entrega

Cada sprint de código deve deixar em GitHub:
1. **Resumo de alterações** com ID de M0–M8, arquivos e riscos.
2. **Execução CI** e, se passou, link para ZIP numerado em Releases.
3. **Casos de teste** executados e os não executados, sem exagerar a evidência.
4. **Estado atualizado** (concluído CI, parcial ou jogo).
5. **Próxima prioridade única**, sem acrescentar features fora de escopo.

Releases são imutáveis; um erro em 0.9.3 leva a 0.9.4 e não substitui artefatos da mesma tag.

## 7. Como lidar com decisões pendentes sem paralisar

O GDD propõe 10 itens V1-P01 a V1-P10, registrados como **a aprovar**. Na ausência de nova decisão, podemos:
- Continuar detalhando e prototipando escolhas de baixo risco.
- Nunca converter uma proposta em “aprovado pelo usuário” silenciosamente.
- Não adicionar recurso caro (co-op, 16 mapas, helicóptero) por achar que MW3 possui.
- Usar protótipos e testes para fundamentar ajustes de mapa, tempo, preços e dificuldades.
- Guardar diferenças entre nossa implementação e os guias de MW3 no documento de pesquisa.

## 8. Critério de concluir o planejamento (antes de dizer “GDD pronto”)

- [x] Pesquisa de referência com fontes e diferenças MW3/Frontline.
- [x] GDD mestre com escopo, sistemas e gates.
- [x] Plano de entrega M0–M8 com dependências e aceite.
- [ ] Aprovação formal de V1-P01 a V1-P10.
- [ ] Tabelas finais de preços, dano, HP e ondas validadas por simulação/playtest.
- [ ] Blockout final aprovado e rotas medidas.
- [ ] Registro de licenças de assets e decisões de UX prontas.
- [ ] Checklist de requisitos completo e rastreado.

**Conclusão correta agora:** *pré-produção estruturada para uma 1.0 com escopo proposto*, não “GDD 100% aprovado” nem “jogo pronto”. A implementação continua separada e deve ser planejada sprint a sprint.


## 9. Replanejamento do Campo de Testes — CT-01 a CT-07 (11/11/2026)

O usuário confirmou em sessão real a progressão até a onda 10 e pediu **perks, Last Stand, desafios por dinheiro, resumo estatístico, attachments em todas as armas, agachamento e deitar**, antes de ampliar mapas, ondas ou veículos. A pesquisa histórica confirmou o intervalo de 30 s do Survival de 2011, diferente dos 75 s presentes no código do Frontline.

**Novo caminho de execução após M0/QA visual do Quaternius:**

| Ordem | Foco | Entrega mínima | Teste de aceite |
| --- | --- | --- | --- |
| **CT-01** | Resumo + intermissão | Estatísticas reais por onda, apresentação curta não bloqueante; padrão 30 s proposto, intervalos maiores configuráveis | 2+ ondas em CI, migração do setting 75, N antecipação, F nas lojas |
| **CT-02** | Metas de dinheiro | Quad Kill, Rampage, Killstreak, headshots, bônus separados por evento | Dedupe de recompensa, headshot e escopeta, 15 ondas simuladas de saldo |
| **CT-03** | Postura | Agachar fisicamente, deitar e rastejar, ADS/colisão corretos | Verificar passagem baixa e teto, câmera/arma, impossibilidade de atravessar parede |
| **CT-04** | Armas customizáveis | Red Dot + Silenciador compráveis juntos nas 5 classes e modelo físico adequado | 5 armas × 2 attachments, comparação tiro/som/ADS, compra/sem saldo |
| **CT-05** | Perks | Um perk por vez, efeitos úteis e visíveis no status; substituição | Compra, troca, duração/limites, sem inflação de dinheiro |
| **CT-06** | Última Chance | Queda com pistola e recuperação, kit consumível separado do perk | Sangramento, chance única, kit, treino, último NPC |
| **CT-07** | Homologação | Balancear tudo no Campo de Testes antes de novas arenas | 15 ondas reais, 5 armas, compras, FPS no notebook-alvo, sem P0/P1 |

**Precedência:** CT-01/02 ampliam M0 e M3; CT-03/04 são obrigatórios para M1; CT-05/06 concluem blocos importantes de M3/M5. M4 (Complexo Industrial) só inicia depois do Campo de Testes ficar consistente, não apenas depois do CI verde.

**Fidelidade sem cópia:** mecânicas comparáveis às do MW3 Survival de 2011, mas modelos, nomes, som, gráficos, economia e referências visuais próprios. Conferir [pesquisa de fontes](PESQUISA_MW3_SURVIVAL_MECANICAS.md) ao detalhar cada sprint. Não confundir perks do multiplayer com Survival.

**Nada foi implementado durante a rodada documental.** Os status acima são **PENDENTES**, não "concluídos".
