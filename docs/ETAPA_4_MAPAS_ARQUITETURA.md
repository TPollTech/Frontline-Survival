# Frontline Survival — Etapa 4: Mapas e arquitetura multissetorial

**Documento v1.0:** 10/11/2026  
**Estado:** especificação PROPOSTA, ainda não aprovada; nenhuma implementação nesta rodada.  
**Base:** código 0.7, ROADMAP, Etapas 0–3 e plano de mapas existente.  
**Pré-requisitos para implementar:** validar Etapa 0; alinhar IA/spawn (Etapa 2) e lojas/suporte (Etapa 3).  
**Alvo:** Godot 4 Compatibility, Ryzen 5 7530U, Radeon integrada e 8 GB de RAM.

> O mapa deve gerar decisões de combate e compras, não apenas ser grande. Primeiro desenvolver um único mapa definitivo com setores interligados; preservar o Campo de Testes como ambiente permanente de laboratório.

## 1. Regras já estabelecidas

- Survival solo offline, com ondas sucessivas e sem encerramento ao completar uma onda.
- Preparação padrão de **75 segundos**, configurável entre 45 e 120, com N opcional para adiantar.
- Três estações físicas (armas, equipamentos e suporte), acessadas por F no local, sem loja remota no B.
- Campo de Testes atual e textura de asfalto preservados permanentemente.
- Futuros mapas dedicados com vários setores, rotas alternativas e posições táticas.
- Modos de treinamento e clássico, HUD discreto e reforços comprados para uso posterior.
- Identidade original; não copiar mapas, modelos, sons nem marcas protegidos.

As dimensões, número de setores, locais de compra e quantidade de mapas para lançamento ainda são **propostas**.

## 2. Diagnóstico do protótipo 0.7

- A cena principal é um Node3D ligado ao script main.gd.
- Main.gd monta o Campo de Testes com geometria procedural, seus três terminais, os oito pontos de spawn no perímetro, o HUD, as ondas e a economia.
- O chão possui cerca de 52 x 52 unidades e utiliza a textura asphalt.png que deve continuar no laboratório.
- O limite atual é de 12 inimigos ativos; não aumentar sem benchmark.
- Não há, ainda, gerenciador genérico de mapas nem seletor funcional de mapas.

**Risco arquitetural:** criar outro mapa diretamente dentro do main.gd duplicaria código e tornaria manutenção e progressão inconsistentes. A separação deve ser incremental e testada, não uma reescrita sem regressão.

## 3. Mapa 01 — Complexo Industrial (proposta de design)

**Premissa:** instalação industrial de uso militar desativada, com concreto, metal gasto, armazéns, oficinas e área administrativa. Dia ensolarado e visibilidade boa. Realismo estilizado leve em vez de fotorrealismo moderno.

### Escala inicialmente proposta

- Área útil aproximada: **110 x 90 metros**, a alterar após blockout e testes de deslocamento.
- **Cinco setores** conectados sem telas de carregamento.
- Dois níveis verticais no máximo: térreo e uma passarela/andar parcial.
- Evitar corredores extensos vazios: espaço suficiente para combate e rota, mas não exigir corrida longa a cada compra.
- A distância entre terminais deve permitir uso razoável dos **75 segundos** de preparação; tempo real será medido com movimentação do jogador.

### Setores

| ID | Setor | Elementos principais | Benefício tático | Risco |
| --- | --- | --- | --- | --- |
| S1 | Pátio central | Contêineres, barricadas, guindaste estático e cruzamentos | Mobilidade e visão entre setores | Cerco por múltiplos lados |
| S2 | Galpão de cargas | Paletes, prateleiras, duas portas e rotas laterais | Defesa por corredores | Entrada por flanco e bloqueio de saída |
| S3 | Administração | Salas, escada, janelas e passarela parcial | Posição elevada e visão média | Duas rotas para inimigos subirem |
| S4 | Oficina e manutenção | Bancadas, pilares e máquinas decorativas | Cobertura e quebra de linha de tiro | Aproximação curta e cantos cegos |
| S5 | Perímetro e depósitos | Tanques decorativos, muros, portões e passagens de serviço | Rotas de fuga e confronto longo | Visão longa e flanqueamento |

**Regra geral:** nenhuma posição deve ser invulnerável por falha de navegação. Plataformas elevadas e cantos defensivos terão contrajogo e mais de uma via possível de chegada inimiga.

### Conexões — grafo conceitual

    S2 GALPÃO -------- S3 ADMINISTRAÇÃO
       |   \           /    |
       |    \         /     |
       |       S1 PÁTIO     |
       |    /         \     |
       |   /           \    |
    S4 OFICINA ------- S5 PERÍMETRO

Este diagrama é de **conectividade**, não planta em escala. Exige dois caminhos viáveis entre posições de interesse, circuitos para recuo e rotas para a IA sem becos que prendam o último inimigo.

**Decisão ainda aberta:** manter todos os setores acessíveis desde o início (recomendação) ou criar bloqueios. Portas desbloqueáveis não são necessárias ao jogo base e ficam como expansão opcional.

## 4. Estações de compra: localização proposta

| Estação | Setor candidato | Razão |
| --- | --- | --- |
| Armas | S2 Galpão — entrada de serviço | Mudança de armamento exige sair da zona defensiva |
| Equipamentos | S4 Oficina — corredor externo | Recuperação distribuída pelo mapa |
| Suporte | S3 Administração — térreo | Compra de reforços exige exposição e movimento |

**Regras:** F somente perto do terminal; não suspender automaticamente a onda ao comprar; não criar áreas imunes em torno do terminal; o fechamento da loja deve devolver a câmera e os controles. Distâncias devem permitir ao menos uma visita significativa entre ondas sem depender da tecla N.

## 5. Spawn justo e progressão espacial

### Pontos propostos

- Inicialmente **12 a 18 pontos candidatos** espalhados pelos cinco setores, com setor/ID, posição, direção de entrada, espaço de colisão e conectividade navegável.
- Rejeitar spawn dentro de paredes, player, NPC, torre ou loja.
- Preferir surgimento fora da câmera/linha de visão quando existir alternativa.
- Distância mínima inicial de **10 m do jogador**, hipótese da Etapa 2 a validar no tamanho real do mapa.
- Não criar inimigos durante preparação e não permitir spawns sem rota até o combate.
- Se nenhum ponto for válido, aguardar e registrar a tentativa, sem gerar instância inválida ou ciclo infinito.

### Uso de setores pelas ondas (proposta)

| Etapa de ondas | Pressão espacial |
| --- | --- |
| 1–3 | Chegada em 1–2 setores, permitindo aprender rotas |
| 4–9 | Chegada em 2–3 setores, alternando aproximação e flancos |
| 10–15 | Maior alternância e pesados anunciados, respeitando 12 ativos |
| 16+ | Misturas variáveis por vários setores, sem aparições instantâneas injustas |

Não modificar a curva de quantidade e armamento da Etapa 2 sem aprovação. A distribuição espacial é outro parâmetro a testar, não dificuldade extra imposta automaticamente.

### Navegação e antitravamento

- Construir uma malha de navegação ou regiões conectadas para corredores, rampas e escadas; validar cápsulas dos NPCs.
- Detectar agentes sem progresso de percurso, recalcular trajetos e usar saídas alternativas.
- Escalonar recálculos de caminhos para evitar picos de CPU quando muitos inimigos surgem.
- Não teletransportar inimigos visivelmente para forçar dificuldade.
- Evitar que aliados, inimigos ou torretas bloqueiem permanentemente acessos essenciais.
- O último inimigo deve sempre poder reencontrar o combate ou permitir diagnóstico de um travamento, sem acabar a onda artificialmente.

## 6. Arquitetura de mapas — proposta técnica futura

### Responsabilidades separadas

| Sistema | Responsabilidade | Independência |
| --- | --- | --- |
| GameSession | Estado da partida, modo, vida/morte, reinício | Não deve depender de coordenadas de um mapa |
| WaveDirector | Ondas, timers, composição, fila e contagem | Recebe pontos de spawn do mapa |
| MapLoader | Seleção, carregamento/descarregamento e verificação | Não modifica o saldo nem a onda |
| MapDefinition | ID, nome, limites, pontos, setores, navegação, estações | Dados de cada mapa |
| Economy/Inventory | Crédito, armas possuídas, consumíveis, suporte | Regras iguais para todos os mapas |
| HUD/Menu | Mostra sessão e seleção de mapa | Não depende da geometria |
| Player/Enemy/Ally | Combate e movimentação | Não deve conter IDs específicos de cenário |

### Estrutura conceitual de cena

    MapRoot
      Geometry
      Collisions
      Navigation
      SpawnPoints
      Stations
        Weapons
        Gear
        Support
      PlayerStarts
      Sectors
      Bounds
      Lighting
      AudioZones

**Contrato do mapa:** map_id estável, nome público, tipo (treino/definitivo), ponto de início, limites, três terminais acessíveis, pontos de spawn com identificadores únicos, rotas navegáveis e setores nomeados.

**Validação antes da partida:** IDs duplicados, referência ausente, início sem piso, estação fora de acesso, spawn dentro da parede ou sem rota são defeitos detectados com mensagem clara. Não carregar parcialmente uma sessão quebrada.

### Caminhos sugeridos, NÃO criados nesta rodada

- scenes/maps/campo_de_testes.tscn
- scenes/maps/complexo_industrial.tscn
- scripts/map/map_loader.gd
- scripts/map/map_definition.gd
- scripts/session/game_session.gd
- scripts/session/wave_director.gd
- scripts/ui/hud.gd

**Migração segura:** somente após Etapa 0 testada; primeiro migrar o Campo de Testes para cena separada e reproduzir seu comportamento. Só depois introduzir o mapa definitivo. Não substituir tudo em um commit.

### Progresso e escolha de mapa

- Iniciar mapa diferente = começar **nova partida**, nunca trocar de mapa no meio de uma onda.
- Compras e suportes pertencem à sessão, não à cena do mapa.
- **Proposta:** recordes separados por mapa e por modo (treino/clássico), preservando histórico antigo do Campo de Testes.
- Mostrar seletor de mapas apenas quando houver dois mapas jogáveis, não um botão sem função.
- **Proposta de escopo da primeira versão completa:** Campo de Testes + um mapa definitivo; mapas urbanos, porto e montanha entram no backlog futuro, sem data prometida.

## 7. Visual e produção de assets

Kit modular recomendado para produção depois do blockout: painéis de galpão, vigas, portas, escadas, corrimãos, contêineres, paletes, caixas, barris, pilares, máquinas, veículos estáticos e placas originais de identificação.

Ordem visual futura: blockout navegável -> rotas e IA -> estações e spawn -> iluminação base -> materiais/texturas -> props e ambientação -> otimização. A geometria em blocos é aceitável **somente como etapa de blockout**, não como arte final.

## 8. Limites de hardware e medição

- Godot Compatibility, Ryzen 5 7530U e 8 GB continuam a referência.
- **Meta, não benchmark:** piso desejado de 30 FPS a 720p baixo e tentativa de 60 FPS em cenas comuns.
- Manter até 12 inimigos ativos até prova em contrário; não aumentar conjuntamente NPCs, luzes e partículas.
- Luz direcional principal, sombras configuráveis, sem dezenas de sombras dinâmicas em interiores.
- Geometria e colisões simplificadas; reduzir materiais únicos e objetos isolados sem ganho visual.
- Usar repetição/atlas de texturas quando adequado; avaliar visibilidade e LOD sem supor que funcionem igualmente em todo renderizador.
- Limitar fontes de áudio e efeitos simultâneos; animação distante mais barata quando possível.
- Registrar FPS, RAM e pior queda perceptível em S1–S5, ondas 5/10/15 e reforços ativos; comparar com o Campo de Testes na mesma configuração.

Caso o mapa novo não alcance o piso de desempenho, reduzir efeitos, detalhes, sombras e distâncias de visão antes de comprometer rotas, regras de ondas ou estações.

## 9. Implementação futura em etapas independentes (NÃO executar agora)

| Código | Entrega | Dependência | Aceite |
| --- | --- | --- | --- |
| 4A | Isolar Campo de Testes como cena | Etapa 0 validada | Mesmo cenário, textura, compras e ondas sem regressão |
| 4B | MapLoader, contrato e validação | 4A | Dados consistentes independentemente do nome do mapa |
| 4C | Blockout dos cinco setores | 4B | Rotas alternativas e níveis acessíveis |
| 4D | Spawn e navegação | 4C + Etapa 2 | Agentes alcançam player e não travam o fim da onda |
| 4E | Três terminais e suporte | 4D + Etapa 3 | Compras e ações funcionam por F, 3 e 4 |
| 4F | Arte final leve e otimização | 4E | Qualidade legível e FPS/RAM medidos |
| 4G | Seletor e recordes por mapa | 4F | Novas sessões sem estado herdado indevidamente |

## 10. Testes de aceitação — situação auditada em 12/11/2026

| ID | Caso | Resultado esperado | Situação atual |
| --- | --- | --- | --- |
| M4-01 | Campo de Testes após migração | Asfalto, lojas, ondas e FPS preservados | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-02 | Iniciar Complexo Industrial | Aparecer em piso livre sem colisão | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-03 | Caminhar por S1–S5 | Setores conectados e rotas coerentes | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-04 | Acessar passarela | Jogador e inimigos conseguem subir | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-05 | Circular entre três estações | Viável durante os 75 s, medido em jogo | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-06 | Interagir via F fora de alcance | Loja não abre remotamente | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-07 | 100 entradas inimigas | Sem spawn dentro de objetos/jogador | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-08 | Onda 10 com pesado | Rota válida, aviso e contrajogo | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-09 | Último inimigo preso | Recuperação ou diagnóstico; não travar indefinidamente | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-10 | 15 ondas completas | Sem game over indevido ou perda de contagem | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-11 | Reanimação treino | Mantém créditos, armas e onda | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-12 | Morte clássico | Encerra partida corretamente | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-13 | Pausa e configurações | Temporizadores congelados e áudio persistente | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-14 | Torreta, esquadrão e ataque | Sem bloquear rotas ou quebrar sessão | **PARCIAL** — código/CI parcial; falta aceite completo |
| M4-15 | FPS/RAM por setor | Medições reais e comparação com baseline | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-16 | Troca de mapa pelo menu | Nova sessão limpa | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-17 | Recordes por mapa/modo | Sem contaminar treino/clássico ou perder legado | **PENDENTE** — não implementado ou sem teste válido para este cenário |
| M4-18 | Carregar mapa inválido | Falha controlada com diagnóstico | **PENDENTE** — não implementado ou sem teste válido para este cenário |

Nenhum caso foi executado neste ciclo de documentação.

## 11. Decisões pendentes

| ID | Questão | Proposta inicial |
| --- | --- | --- |
| M4-P01 | Dimensão útil | 110 x 90 m, revisar após blockout |
| M4-P02 | Número de setores | Cinco |
| M4-P03 | Verticalidade | Térreo + passarela/andar parcial |
| M4-P04 | Posição das estações | Armas S2, equipamentos S4, suporte S3 |
| M4-P05 | Setores bloqueados | Todos livres desde a primeira onda |
| M4-P06 | Quantidade de spawn candidatos | 12–18, condicionados à navegação |
| M4-P07 | Mapas da primeira versão completa | Campo de Testes + Complexo Industrial |
| M4-P08 | Recordes | Separados por mapa e modo |
| M4-P09 | Navegação | Regiões/NavigationAgent3D ou solução leve após teste |

## 12. Limites de escopo

**Não incluir nesta etapa:** mundo aberto, coop, campanha, helicópteros pilotáveis, destruição física de todo o cenário, portas compráveis sem aprovação, mapa urbano completo ou seleção de mapas ainda inexistentes.

**Próxima lacuna documental recomendada:** Etapa 5 — HUD, menus, áudio, estatísticas, acessibilidade e identidade visual; depois Etapa 6 e consolidação do GDD mestre. O jogo segue em planejamento; nenhuma implementação nova foi feita agora.


---

## Auditoria de execução — 12/11/2026 (base v0.9.17)

**Quadro atualizado após o documento histórico.** Critérios: **0 concluídos em CI; 8 parciais; 10 pendentes**. **A Etapa 4 ainda NÃO está completamente concluída.**

### Entregas já implementadas

- [x] Layout conceitual dos cinco setores, rotas e estações documentado — **CONCLUÍDO (CÓDIGO/CI)**
- [x] Campo de Testes preservado e jogável nas builds de teste — **CONCLUÍDO (CÓDIGO/CI)**

### Itens parciais

- [ ] Sondas de spawn e navegação validadas somente no Campo de Testes — **PARCIAL**

### Pendências de execução ou validação

- [ ] Produzir blockout e navegação do Complexo Industrial S1–S5 — **PENDENTE**
- [ ] Criar seletor e recordes por mapa — **PENDENTE**
- [ ] Validar 15 ondas e FPS/RAM no mapa definitivo — **PENDENTE**

**Evidências:** [Godot CI da v0.9.17](https://github.com/TPollTech/Frontline-Survival/actions/runs/43171938905) · [Release Windows v0.9.17](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.17) · [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md). Teste CI não substitui validação real no notebook.
