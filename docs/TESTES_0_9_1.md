# Frontline Survival v0.9.1 — Matriz de testes

**Origem:** captura de usuário na 0.9.0 (preparação onda 03, 16 abates, 108 FPS instantâneos). Nesta versão, eram visíveis armas inteiramente brancas, aliados deformados e mira desalinhada, além do relato de sons agudos. A captura **não** confirma FPS médio.

## Critérios de entrega

| ID | Cenário | Comportamento esperado | Situação |
| --- | --- | --- | --- |
| 091-A1 | Trocar as cinco armas | Cores escuras/cinza/tan, sem arma branca; faces completas | **PARCIAL** — material implementado, teste visual pendente |
| 091-A2 | Inspecionar arma em ADS | Visor 3D fica no centro real da câmera | **PARCIAL** — coordenadas calculadas, teste de campo pendente |
| 091-A3 | Atirar em alvo parado com ADS | Primeiro disparo segue a direção visada, depois ocorre recuo | **PARCIAL** — ordem do raycast corrigida, teste pendente |
| 091-A4 | Jogar sem HUD de mira | Nenhuma crosshair 2D, inclusive fora do ADS | **PARCIAL** — removida do código, teste pendente |
| 091-A5 | Disparar e recarregar | Mãos, carregador, ação e flash permanecem coerentes | **PARCIAL** |
| 091-S1 | Chamar 2 aliados | Modelos de armas coloridos, mãos sobre a arma | **PARCIAL** — solução IK nova, teste visual pendente |
| 091-S2 | Aliados andando e atirando | Cotovelos não dobram ao contrário/atravessam torso sistematicamente | **PARCIAL** |
| 091-S3 | Inimigos atacando | Empunhadura em duas mãos sem inversão grave | **PARCIAL** |
| 091-AU1 | Consecutivos acertos na cabeça/corpo | Sem apitos de hitmarker repetidos | **PARCIAL** — som removido do código |
| 091-AU2 | Finalizar onda 1 e 2 | Cue grave e baixo, sem apito agudo irritante | **PARCIAL** — áudio original sintetizado no jogo |
| 091-AU3 | Comprar e ajustar som | Som de compra atenuado; volume UI controla alertas | **PARCIAL** |
| 091-R1 | Onda 1 → 2 → 3 | Preparação de 75s e estado/contagem íntegros | **PENDENTE de regressão real 0.9.1** |
| 091-R2 | Usar F, comprar, recarregar, usar 3/4 | Nenhum novo bloqueio ou falha nos controles | **PENDENTE** |
| 091-R3 | 15 ondas com suporte | Sem travas e com FPS/RAM medidos no notebook | **PENDENTE** |

## Evidências técnicas necessárias

- Build: Godot 4.4.1 headless --import, smoke test, `verify_project.py` e exportação Windows passando sem erros.
- GitHub Release: tag v0.9.1, ZIP contendo EXE/PCK, link e SHA256.
- Jogabilidade: captura de armas/aliados e relato de áudio. Se persistirem erros, registrar por arma e situação.
- Não marcar Etapas 1, 2 ou 5 inteiramente concluídas somente por compilar. Marcar **CONCLUÍDO (CI)** para exportação e **PARCIAL** para acabamento até teste real.
