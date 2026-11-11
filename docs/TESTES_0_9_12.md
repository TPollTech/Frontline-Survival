# QA de combate — Frontline Survival v0.9.12

**Prioridade:** M0 + M1 (Campo de Testes). **Novas ondas, mapas e desembarques por veículos congelados** até estabilidade e boa jogabilidade.

| Código | Teste | Estado |
| --- | --- | --- |
| T12-01 | Shift + W abaixa/inclina a arma e separa a mão de apoio; transição suave | **PARCIAL** — implementação; teste visual pendente |
| T12-02 | Correr bloqueia disparo/consumo de munição | **CI** — teste na cena Godot |
| T12-03 | Hitmarker somente ao acertar; headshot em âmbar; sem crosshair | **CI** + inspeção visual pendente |
| T12-04 | Indicador de dano em arco no lado do impacto | **PARCIAL** — teste visual pendente |
| T12-05 | Efeitos curtos de sangue limitados | **CI** + visual pendente |
| T12-06 | Cadáver permanece por ~17 segundos sem colisão | **PARCIAL** — teste de duração/visual pendente |
| T12-07 | Armas no chão coletáveis por F; chance de caixa de munição | **CI** + gameplay pendente |
| T12-08 | Munição corresponde à arma caída; não se converte para arma equipada | **CI** — teste adicional de calibres |
| T12-09 | No máximo 12 corpos, 18 itens de loot simultâneos | **PARCIAL** — teste de estresse pendente |
| T12-10 | Cabeça, mãos, colete e arma visualmente alinhados nos NPCs | **PARCIAL** — teste visual pendente |
| T12-11 | 10 WAVs gravados em PCM preservados, sem apitos | **CI** |
| T12-12 | Jogar 15 ondas com FPS/CPU/RAM e observar loot | **PENDENTE** |
| T12-13 | ZIP Windows v0.9.12 com EXE/PCK e SHA-256 em Releases | **PENDENTE DO CI/RELEASE** |

**Feedback registrado:** usuário já alcançou a onda 10 e considera o sistema de ondas progressivo, mas deseja sprint tático, hitmarker, sangue, corpos, loot e modelos mais humanos. Novas ondas e mapas devem esperar.

**Aceite:** CI passa para scripts, importação, áudio e lógica integrada. A avaliação visual e a sessão longa no Windows são indispensáveis para marcar **CONCLUÍDO (JOGO)**.
