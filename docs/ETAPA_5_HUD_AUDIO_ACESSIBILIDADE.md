# Frontline Survival — Etapa 5: HUD, menus, áudio e acessibilidade

**Estado:** proposta documental v1.0 — 10/11/2026. **Não aprovada e não implementada por este documento.**
**Referências:** [ROADMAP](../ROADMAP.md), [decisões](REGISTRO_DECISOES.md), [Etapa 1](ETAPA_1_FPS_ARMAS.md), [Etapa 3](ETAPA_3_ECONOMIA_SUPORTE.md), [Etapa 4](ETAPA_4_MAPAS_ARQUITETURA.md).

## 1. Limites já estabelecidos (não são propostas)
- FPS 3D solo offline, identidade original, ondas contínuas; preparação padrão de 75 s.
- Campo de Testes preservado, inclusive asfalto; compras somente nas três estações com **F**; 3/4 acionam suporte previamente comprado; G granada, E corpo a corpo, 1/2 armas.
- HUD discreto, sem painel permanente de atalhos; volume configurável e persistente.
- Hardware de referência: Ryzen 5 7530U, Radeon integrada, 8 GB; Godot 4 Compatibility.
- Morte no treino admite reanimação sem perda do progresso da sessão; morte no clássico encerra partida.
- A existência de HUD e ajustes na versão 0.8 não comprova legibilidade, persistência ou funcionamento em Windows real.

## 2. Hierarquia da informação (PROPOSTA E5-P01)
| Prioridade | Informação | Regra de apresentação |
| --- | --- | --- |
| Crítica | Vida/colete, munição atual/reserva, ameaça direcional | Visível durante combate; alto contraste sem encobrir a mira |
| Alta | Onda, inimigos restantes, créditos, granadas, tokens 3/4 | Compacta, sem tutorial fixo; valores atualizados por eventos |
| Contextual | F para interagir, compra/erro, recarga, reforço indisponível | Mostrar somente quando relevante; desaparecer sem bloquear visão |
| Temporária | Preparação de 75 s, contagem regressiva, bônus, início de onda | Faixa discreta com prioridade sobre avisos não críticos |

**Proposta:** reserva de área central para retícula e alvo; não usar flashes de tela inteira para cada acerto. Texto e cor devem informar o mesmo estado: nunca depender só de vermelho/verde. Indicador direcional da 0.8 requer teste de leitura, não duplicação de sistema.

## 3. Estados de interface e foco (PROPOSTA E5-P02)
Fluxo sugerido: **MENU PRINCIPAL → SELEÇÃO DE MAPA (quando existir) → PARTIDA → PAUSA → PARTIDA**; morte clássica leva a **RESULTADO → MENU/REINICIAR**; treino oferece **REANIMAR**. Onda concluída leva a **PREPARAÇÃO → COMBATE**, não a resultado.

- Pausa congela temporizadores, IA e dano; menu de configurações pode ser acessado da pausa e do menu principal.
- Abrir estação por F depende de proximidade; fechar devolve foco e captura do mouse; abrir loja não pausa a onda automaticamente.
- Durante loja, ações de combate ficam suspensas, mas o mundo continua; fechamento imediato por Esc e, se necessário, quando o jogador sofrer dano (hipótese de UX a validar).
- Prioridade de Esc: fechar modal/loja → voltar da configuração → pausar/retomar. Não fechar duas camadas num único pressionamento.
- Reinício cria sessão limpa e não herda saldo/tokens do jogo anterior; resultados são locais e não exigem conta ou rede.
- Quando houver apenas Campo de Testes, não apresentar seletor de mapas sem destino válido.

## 4. Contrato de feedback (PROPOSTA E5-P03)
- Acerto normal: retícula breve e som curto; headshot: variante âmbar já introduzida na 0.8, sem confirmação de morte se alvo sobreviveu.
- Dano recebido: direção e intensidade legíveis, sem flashes estroboscópicos; alerta de vida crítica com cadência limitada.
- Compra: saldo antes/depois, item e efeito; erro explica motivo e **não debita** (dependência E3-P017).
- Reforço: indicar comprado, pronto, indisponível e em execução; 3/4 não devem sugerir compra remota.
- Onda: início, restante, último inimigo e preparação; aviso sonoro não é fonte única de informação.
- Conflito de mensagens: morte > ameaça imediata > erro de compra > início de onda > dicas; deduplicar avisos repetidos.

## 5. Áudio e mixagem (PROPOSTA E5-P04)
**Buses sugeridos:** Master, Armas/Combate, Ambiente, Interface, Música; opção de desligar música sem silenciar alertas. Persistir valores após reinício; limitar polifonia de disparos/impactos e impedir clipping com múltiplos inimigos e torretas. Atenuação espacial de armas/inimigos deve permitir reconhecer distância/direção; UI e avisos de acessibilidade permanecem compreensíveis com áudio desligado. Não reutilizar gravações ou trilhas protegidas de outras franquias.

## 6. Acessibilidade e vídeo (PROPOSTA E5-P05)
- Escala de HUD e texto (ex.: 100/125/150%, valores sujeitos a teste); área segura para 1280×720, 1600×900 e 1920×1080.
- Sensibilidade do mouse, inversão vertical opcional, FOV com limites confortáveis; reduzir balanço da câmera e efeitos de tremor.
- Contraste e símbolos para distinguir inimigo, aliado e objetivos; avisos visuais equivalentes a sinais sonoros.
- Presets gráficos **realmente conectados** às opções: baixo/médio e sombras/partículas quando suportados; não exibir controles sem efeito.
- Persistência local de opções sem exigir internet. Mudanças de resolução devem oferecer reversão se a imagem ficar inutilizável.

## 7. Menus, resultado e recordes (PROPOSTA E5-P06)
Menu principal mínimo: Jogar, Configurações, Sair; escolha de modo/mapa só quando disponível. Resultado clássico: onda alcançada, eliminações confirmadas, tempo e créditos ganhos; distinguir impactos de abates. **Proposta da Etapa 4:** recordes locais por mapa e modo, ainda não aprovada. O treino pode mostrar estatísticas, mas não deve ser confundido com ranking competitivo clássico. Sem conquistas online, conta, loja real ou narrativa/campanha no jogo base.

## 8. Dependências e implementação futura (NÃO executar nesta rodada)
| Ordem | Pacote | Depende de | Entrega verificável |
| --- | --- | --- | --- |
| 5A | Inventário de telas/estados e eventos HUD | Etapa 0 estabilizada | Matriz de eventos sem estados contraditórios |
| 5B | HUD escalável e mensagens | 5A, Etapas 1–3 | Informação legível em 720p e sob combate |
| 5C | Fluxos de pausa, loja e resultado | 5A, Etapa 3 | Esc/foco corretos, sem compra duplicada |
| 5D | Buses, mixagem e preferências | 5A, Etapa 1 | Sem clipping perceptível, valores persistidos |
| 5E | Acessibilidade e vídeo | 5B–5D | Ajustes efetivos, reversíveis e salvos |
| 5F | Recordes por mapa | Etapa 4 e 5C | Sem misturar modos/mapas nem perder dados existentes |
| 5G | Verificação integrada | 5A–5F, Etapa 6 | QA documentado no hardware-alvo |

## 9. Critérios de aceite e matriz de QA (situação auditada em 12/11/2026)
| ID | Cenário | Resultado esperado | Situação atual |
| --- | --- | --- | --- |
| U5-01 | HUD 720p/900p/1080p | Sem corte, sobreposição ou obstrução da retícula | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-02 | Vida baixa e dano de múltiplas direções | Prioridade e direção identificáveis | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-03 | Headshot sem morte | Feedback de acerto sem abate falso | **CONCLUÍDO (CI)** — teste integrado confirmado |
| U5-04 | Finalizar onda e esperar 30 s (padrão atual) | Contagem, compra e reinício de combate corretos | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-05 | Antecipar com N | Sem duplicar avisos/ondas | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-06 | F longe e perto de cada estação | Só abre terminal alcançável | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-07 | Esc com loja/configurações/pausa | Fecha camada correta e restaura mouse | **CONCLUÍDO (CI)** — teste integrado confirmado |
| U5-08 | Comprar sem créditos | Erro legível, sem débito | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-09 | 3/4 sem token | Não ativa nem anuncia compra | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-10 | Morrer em treino/clássico | Revive/resultado conforme modo | **CONCLUÍDO (CI)** — teste integrado confirmado |
| U5-11 | Reiniciar sessão | Sem estado de compra ou suporte herdado | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-12 | Ajustar volumes e reiniciar | Valores persistidos; sem clipping sob carga | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-13 | Som desligado | Avisos críticos permanecem visuais | **PARCIAL** — código/CI parcial; falta aceite completo |
| U5-14 | Escala de HUD e FOV extremos permitidos | Layout e mira continuam utilizáveis | **PENDENTE** — falta ajuste específico de escala do HUD |
| U5-15 | Alterar resolução inválida | Retorno seguro à configuração anterior | **PENDENTE** — não existe fallback testado de resolução inválida |
| U5-16 | 12 inimigos, torretas e aliados | UI/áudio não causam queda de desempenho sem registro | **PENDENTE** — sem benchmark com 12 NPCs e suporte |
| U5-17 | Resultado e recordes por mapa/modo | Contagens consistentes e armazenamento local | **PENDENTE** — recordes por mapa dependem de Etapa 4 |
| U5-18 | Executável Windows sem editor | Menus, fonte e preferências funcionam | **PARCIAL** — código/CI parcial; falta aceite completo |

**Evidência obrigatória:** commit/build, resolução, FPS, captura de tela, resultado observado, falha e reteste. Nenhum cenário acima foi executado nesta etapa documental.

## 10. Decisões pendentes
| ID | Questão | Proposta, NÃO aprovada |
| --- | --- | --- |
| E5-P01 | Hierarquia/posição e escala do HUD | Quatro prioridades e escala 100–150% |
| E5-P02 | Loja fecha ao receber dano? | Testar fechamento preventivo sem bloquear compras |
| E5-P03 | Feedback de dano/acerto | Evitar tela inteira e avisos duplicados |
| E5-P04 | Buses de áudio | Master, Combate, Ambiente, UI, Música |
| E5-P05 | FOV, tremor e presets | Ajustes acessíveis e efetivos |
| E5-P06 | Resultado e recordes | Dados locais; por mapa/modo sujeito à Etapa 4 |

## 11. Coerência, encerramento de escopo e próxima lacuna
- Não substituir o HUD 0.8 sem validar seu comportamento; a documentação é requisito futuro, não prova de implementação.
- A UI de compras respeita o contrato da Etapa 3 e o posicionamento da Etapa 4; áudio de armas segue Etapa 1; alertas de ondas seguem Etapa 2.
- Jogo base tem **início** (menu, mapa/modo, sessão), **meio** (ondas infinitas com compras e preparação) e **fim da partida** (morte clássica, resultado, recorde); não exige fim narrativo ou última onda.
- Expansões fora do escopo: coop, campanha, mapas adicionais, cosméticos online, árvore extensa de perks e interface de inventário complexa.
- **Próxima lacuna:** Etapa 6 — plano de desempenho, testes, empacotamento e critérios de entrega; depois consolidar GDD e checklist de consistência.

**Resultado:** especificação documental apenas. Nenhum código, cena, asset, configuração executável ou teste de gameplay foi alterado/executado.


---

## Auditoria de execução — 12/11/2026 (base v0.9.17)

**Quadro atualizado após o documento histórico.** Critérios: **3 concluídos em CI; 11 parciais; 4 pendentes**. **A Etapa 5 ainda NÃO está completamente concluída.**

### Entregas já implementadas

- [x] Menus inicial, pausa e configurações por categoria integrados — **CONCLUÍDO (CÓDIGO/CI)**
- [x] Feedback de hit/headshot e estados de morte/última chance testados no CI — **CONCLUÍDO (CÓDIGO/CI)**
- [x] Volumes separados e preferências armazenadas em GameSettings — **CONCLUÍDO (CÓDIGO/CI)**

### Itens parciais

- [ ] HUD reduzido na v0.9.17, ainda sem aprovação visual em três resoluções — **PARCIAL**
- [ ] Opções de FOV, sensibilidade, dano e escala 3D; acessibilidade ainda incompleta — **PARCIAL**

### Pendências de execução ou validação

- [ ] Implementar controle de escala do HUD e fallback de resolução — **PENDENTE**
- [ ] Testar mixagem e clipping no Windows e resoluções 720/900/1080 — **PENDENTE**
- [ ] Separar recordes por mapa/modo quando houver outros mapas — **PENDENTE**

**Evidências:** [Godot CI da v0.9.17](https://github.com/TPollTech/Frontline-Survival/actions/runs/43171938905) · [Release Windows v0.9.17](https://github.com/TPollTech/Frontline-Survival/releases/tag/v0.9.17) · [Auditoria central](AUDITORIA_CHECKLISTS_2026_11_12.md). Teste CI não substitui validação real no notebook.
