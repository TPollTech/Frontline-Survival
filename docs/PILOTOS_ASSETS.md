# Pilotos de assets — revisão 00-24, 00-25, 00-27

24/11/2026. Preservados os recursos e código do gameplay existentes. Revisão anterior d4e9a126 com [Windows 45511716282](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716282) e [Studio 45511716406](https://github.com/TPollTech/Frontline-Survival/actions/runs/45511716406) aprovada. A main também continha a3ac48ad (sincronização de capturas), preservada.

## Piloto canônico 1 — objeto industrial

Balizador de proteção de área industrial, conceito genérico autoral, sem alegação de réplica, marca ou referência fotográfica analisada. Fonte editável: tools/asset_pipeline/parametric/pilot_object.py. Base 0,22 × 0,045 × 0,22 m, altura total 0,835 m; corpo torneado com perfil não trivial e faixa elevada. Três malhas, biblioteca PBR existente (texturas base color, ORM e normal), normais, UV e tangentes autorais. Pivô da raiz no chão; base com offset local de 0,0225 m; orientação canônica Y-up, direção da raiz -Z (referência de transform, não prova de orientação de uma forma rotacionalmente simétrica). Três LODs com 48/24/12 segmentos e distâncias propostas 0/15/35 m, orçamento provisório da categoria object. Colisor de caixa de 0,22 × 0,835 × 0,22 m separado do visual, centro 0,4175 m.

```sh
python -m tools.asset_pipeline.parametric.pilot_object /tmp/frontline-pilot REVISION
```

Gera GLB/glTF de cada LOD, report com SHA-256 e contrato, executa Audit estrito sobre cada exportação, verifica orçamento de triângulos por nível e slots por instância. CI gera duas cópias e compara diretórios byte a byte. Stage separado injeta exatamente os GLBs no Studio de QA, sem publicar no Pages de produção. O script Godot carrega os mesmos GLBs no mapa real em sessão isolada, mede atributos, contagem, dimensões e identidade do colisor e captura a câmera do jogador. Chromium confere o mesmo SHA-256, contagens, dimensões, normais e UVs e salva três capturas. Não substitui nenhuma geometria de produção. Troca de LOD durante a captura é controlada pelo teste, não ligada a distância no gameplay.

## Matriz de cobertura

pilot_coverage.py gera evidência a partir do catálogo vivo reconciliado: categorias existentes, IDs, arquivos GLB/glTF, amostras reais e um candidato por categoria. Inclui também categorias previstas nos BUDGETS sem asset existente. As amostras e os candidatos legados não equivalem a pilotos de fonte canônica nem aprovação visual. Categorias não geométricas (áudio, textura, material, shader, câmera, física) exigem verificações próprias; não inventar uma malha substituta para representá-las. Somente object possui o novo piloto canônico nesta rodada.

## Evidências e limites

[CI 45514843046](https://github.com/TPollTech/Frontline-Survival/actions/runs/45514843046): geração e reprodução estrita das seis exportações aprovadas; etapas Godot/Studio ainda em execução ao registrar. O primeiro workflow 45514798558 não iniciou por uso do contexto runner.temp no env do job; corrigido no commit beb9316a com GITHUB_ENV. Capturas automatizadas não equivalem a inspeção visual efetiva. Não houve integração permanente do piloto, homologação de aparência, benchmark no hardware-alvo ou cobertura de pilotos de todas as categorias. 00-24, 00-25 e 00-27 permanecem parciais. 


## Expansão de pilotos — revisão 00-27

O CI anterior [45514843046](https://github.com/TPollTech/Frontline-Survival/actions/runs/45514843046) terminou verde: balizador 876/444/228 triângulos, seis exports determinísticos, três GLBs importados/renderizados no Godot, três no Studio com hashes/dimensões/contagens coincidentes, colisor separado invariável; matriz de 20 categorias. Continua sem homologação visual manual ou integração permanente.

Fonte autoral dos novos conceitos: `tools/asset_pipeline/parametric/pilot_suite.py`. Preservados os assets atuais, o commit 3b920fe0 e a sincronização posterior c7e59e96. São pilotos técnicos preliminares, não réplicas de produtos comerciais ou modelos aprovados para gameplay. Sem pesquisa fotográfica ou revisão visual efetiva nesta rodada. Arma fictícia visual e carcaça de acessório são sólidos gráficos sem mecanismos funcionais.

| ID | Categoria | Conceito |
|---|---|---|
| qa:training_prop | weapon | Silhueta fictícia de treinamento |
| qa:optic_shell | accessory | Carcaça óptica opaca sem função |
| qa:glove | first_person | Luva com cinco dedos em nós independentes |
| qa:mannequin | character | Manequim vestido com membros separados |
| qa:shelter | structure | Abrigo industrial aberto |
| qa:supply_station | object | Terminal de suprimentos sem lógica de compra |
| qa:planter | environment | Floreira com volumes orgânicos |
| qa:terrain_tile | terrain | Módulo de terreno elevado |
| qa:yard_composition | map | Composição de pátio; não mapa completo nem export do cenário original |

A receita define envelopes físicos por componente e pivô local inferior, perfis chanfrados por extrusão, lofts elípticos de cinco seções com resolução decrescente, PBR base/ORM/normal, UVs, normais e tangentes. Cada piloto exporta três LODs GLB e glTF. Contrato de dimensão calculado a partir dos envelopes autorais, independentemente da malha exportada; direção -Z é uma referência de transformação, não homologação semântica. A luva e o manequim são estudos estáticos de partes articuláveis, não rig anatômico/IK. Não há proxy de colisão criado para as nove novas peças, troca por distância no jogo ou navegação; esses campos são explicitamente desconhecidos/não integrados. Orçamentos são por instância QA e provisórios, não medição de desempenho.

```sh
python -m tools.asset_pipeline.parametric.pilot_suite /tmp/frontline-suite REVISION
```

O workflow `asset-pilot-suite.yml` gera e compara duas cópias byte a byte, exige os contratos e budgets de todos os 54 exports, abre a cena real do Godot em sessão QA com a câmera nativa, posiciona cada GLB para enquadramento isolado e verifica SHA-256, triângulos, dimensões, atributos e clipping. Stage QA injeta os GLBs idênticos, sem publicar no Studio de produção. Playwright compara hashes, contagens e dimensões nos mesmos 27 GLBs, salva capturas por nível. A imagem gerada é evidência técnica, não revisão visual manual.

[CI 45516214029](https://github.com/TPollTech/Frontline-Survival/actions/runs/45516214029): geração estrita e comparação byte a byte concluídas com sucesso; renderização Godot/Studio em andamento no momento do registro. Não contar renders antes de verificar logs. Cobertura canônica total ainda não alcançada (veículo, efeito, colisão, geometria de biblioteca e categorias não geométricas, entre outras). Não substituir produção sem cumprir AGENTS.md. Sem benchmark em hardware-alvo e sem nova release homologada.
