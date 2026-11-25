# Catálogo vivo de assets

Gerar no checkout: `python tools/asset_pipeline/live_catalog.py --output /tmp/live_catalog.json`. Para anexar captura real, adicionar `--runtime qa-inventory/runtime_inventory.json` da mesma revisão. O workflow Asset inventory runtime evidence produz o JSON com as evidências e confere reprodução byte a byte. Não escrever sobre assets/catalog/manifest.json.

Descoberta: arquivos Git rastreados e não ignorados em assets/ e scenes/, shaders em scripts/, referências literais res:// em cenas/scripts/recursos, dependências externas relativas do glTF. Arquivos desconhecidos são registrados sem inventar categoria; sidecars import são recursos, não modelos. IDs antigos preservados; arquivos novos recebem file:<path>; scripts geradores heurísticos sem família conhecida recebem candidate:<path>, não são prova de uso. Registra SHA-256 e Git blob SHA-1 atuais, origem histórica apenas quando hash coincide, referências literais, lacunas dinâmicas, ausência e divergência. GLB/glTF usa caminho original, cena/runtime requer captura real, sem malha substituta. Campos não medidos permanecem nulos; approved sempre false.

Captura opcional: exige commit correspondente, sem falhas, e confere hashes dos recursos/fontes históricos contra a revisão. Relaciona famílias, amostras, recursos de mesh/audio e texturas efetivas; consultas preservadas. Runtime é finito e não garante todas as combinações. A evidência não contém buffers de geometria, portanto composição procedural ainda não é renderizável no Studio. A detecção literal não resolve UID, concatenação arbitrária, todos os formatos binários ou dependências de terceiros; candidatos e lacunas são explicitados. A revisão de runtime é validada para baseline; mudanças em novas fontes ainda exigem captura no mesmo checkout limpo. Não homologar por mera descoberta. O catálogo não substitui o contrato histórico nem a inspeção visual.

O JSON é artefato de build, consumível pelo futuro Studio; nenhum arquivo de gameplay ou asset de produção foi modificado. Oito testes unitários e workflow real de captura/descoberta aguardam execução.

CI 45467773407: 8/8 unitários e captura Godot passaram; reconciliação falhou porque Godot regenerou assets/audio/weapons/lmg.wav.import. A correção diferencia metadados importados e registra hashes anterior/atual, sem aceitar drift dos arquivos de geometria, texturas ou scripts. Revalidação pendente.

CI 45469213836: catálogo reconciliado e reprodução idêntica confirmados; 52 registros, 100 recursos após importação Godot (incluindo sidecars gerados), 48 registros observados por amostra/consulta, 0 referências literais ausentes, 4 dinâmicas. Artefato 14955479321. Checkout limpo para Studio: 62 recursos. A captura procedural ainda não contém buffers de malhas.


## Revisão 00-12 — 24/11/2026

O catálogo agora examina buffers e imagens externos em glTF JSON e no chunk JSON de GLB 2.0, normaliza caminhos relativos locais e registra o vínculo URI/caminho/hash para o Studio. Recusa URIs externas, caminhos que escapam do checkout, symlinks e separadores codificados; entradas ausentes ficam explícitas. A captura runtime descobre caminhos de recursos reais antes de gerar os registros, normaliza subrecursos Godot, registra lacunas de caminhos e rejeita divergência de hashes ou recursos observados não rastreados na revisão. Não altera a baseline imutável.

CI [45500967316](https://github.com/TPollTech/Frontline-Survival/actions/runs/45500967316), commit 76a1e981, aprovou 13/13 testes (incluindo GLB externo, URIs locais e inseguras, descoberta runtime e drift em um Git real), 86 amostras Godot, 52 registros, 100 recursos, 48 registros observados, zero referências literais ausentes e quatro dinâmicas. Repetição byte a byte do catálogo aprovada. A cobertura dinâmica é finita e composições procedurais ainda não têm buffers de geometria exportados; 00-12 permanece parcial, sem aprovação visual.


## Integração de amostras ao Studio — revisão 00-12

O catálogo vivo agrega runtime_samples, indexado pelos IDs originais das amostras e ligado a cada família/recurso já reconciliado. Registra contagens de nós, malhas, superfícies, vértices, triângulos conhecidos, superfícies sem topologia medida, colisores habilitados/desabilitados, classes e LOD bias; scope=whole_sample_subtree e approved=false. Não tratar a subárvore como asset individual nem o bias como índice de LOD. O CI do Studio e Pages agora captura e valida o inventário Godot na mesma revisão, prepara novamente o pacote a partir do catálogo reconciliado e preserva as cinco capturas. A publicação anterior não trazia amostras reconciliadas. Teste de agregação cobre topologia desconhecida e colisores desativados. O primeiro CI 45504658915 falhou antes dos testes pela referência absoluta do auxiliar LOD; corrigida em 446f31eb. Revalidação pendente. Quatro referências dinâmicas e buffers de geometria procedural continuam lacunas; não há alegação de cobertura total.

Revalidação 446f31eb: [CI 45504785941](https://github.com/TPollTech/Frontline-Survival/actions/runs/45504785941) aprovado, 14/14 testes, 52 registros, 100 recursos, 48 registros observados, 86 amostras de Godot, zero referências literais ausentes, quatro dinâmicas, catálogo reproduzido byte a byte. Não implica cobertura integral de composições.


## Fechamento da descoberta e catálogo da versão atual — 00-12

Preservados 45d495b8 e efb50743 (sincronização posterior de screenshots). CIs anteriores 45534922543, 45534922509, 45534922526, 45534922557 e 45534922505 aprovados; Pages confirmou HTTP pós-deploy de 8e5a757a (14 pilotos QA). Nenhuma mudança de gameplay, modelos de produção, baseline histórica ou estados de outras tarefas.

45334ed6 introduziu extração das superfícies procedurais reais no Godot (var_to_bytes sem objetos, base64, SHA-256 por buffer), reconciliação de quatro padrões dinâmicos por ResourceLoader.exists, registro das amostras observadas e recursos de cenas/material/shader/shape/skin, verificação de drift das fontes descobertas. f9fb9b1f acrescentou metadados de carregamento dos recursos físicos, vínculos de texturas à biblioteca sem confundir uso nas malhas, todos os níveis efetivos dos quatro assemblies de barricadas e payloads separados para composição completa e geometria. Os dados de composição são os nós originais da amostra, transforms, materiais, hierarquias, shapes, câmeras e outros campos já medidos no inventário, sem modelo substituto.

| Medida | Resultado |
|---|---:|
| Registros do catálogo | 52 |
| Recursos físicos, incluindo sidecars gerados | 100 |
| Recursos históricos conciliados | 60/60 |
| GLBs observados | 32/32 |
| Famílias amostradas/consultas executadas | 24/24 |
| Amostras/composições | 86 |
| Registros de malha nas amostras | 2996 |
| Buffers procedurais únicos na revisão final | 167 |
| Bytes binários dos buffers únicos | 4204400 |
| Referências a buffers em superfícies das amostras | 2804 |
| Buffers sem vínculo a amostra ou LOD | 0 |
| Referências literais ausentes / lacunas runtime | 0 / 0 |
| Registros observados em amostras/consultas | 50/52 |

Dois registros restantes são texturas de polímero: carregadas pelo Godot e usadas na construção da biblioteca de materiais, sem atribuição efetiva às malhas amostradas. Mantêm status não observado em cena e evidência separada de carregamento. Não promover aprovação.

Quatro padrões dinâmicos: enemy.gd modelos 8/8 existentes, 4 observados; enemy.gd reload 5/8 existentes, 4 observados; loot_pickup.gd modelos 8/8 existentes e observados; player.gd partes 23/24 existentes e observadas. Total 48 candidatos, 44 existentes, 39 observados. Quatro ausências protegidas: shotgun_mag.glb e reloads bolt_sniper/sentinela/sniper.wav. O domínio é finito, conservador e não prova reachability arbitrária. Padrões desconhecidos futuros permanecem unresolved. As quatro referências continuam listadas como expressões dinâmicas, agora com dynamic_resolution e evidências; não confundir número de expressões com falhas. 

CIs [45535740278](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535740278) (165 buffers/86 composições) e [45535950057](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535950057) (167/86) aprovados, 16 testes do catálogo, inventário Godot, reprodução byte a byte e gate de cobertura. Artefatos [14987051971](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535740278/artifacts/14987051971) e [14986892329](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535950057/artifacts/14986892329) baixados, todos os buffers da revisão final conferidos localmente pelo SHA-256. Quatro capturas da primeira revisão abertas e inspecionadas: mapa/menu, ADS, inimigo legado e humanoide experimental ainda em T-pose; sem homologação de qualidade. Os 12 níveis registrados das quatro barricadas reutilizam três buffers únicos (432/108/48 triângulos por saco); preservam os caminhos das partes e dos bloqueadores físicos. Não são 12 malhas únicas.

CI [45535740281](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535740281) aprovou Studio, 32 GLBs, 86 amostras, cinco vistas e ZIP offline. A revisão final f9fb9b1f tem gate de HTTP/hash dos dois payloads no browser em [45535950024](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535950024), ainda em execução ao registrar; Pages [45535950018](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535950018) e Windows [45535950052](https://github.com/TPollTech/Frontline-Survival/actions/runs/45535950052) também em validação. Não afirmar deploy dessa revisão. 

**Critério 00-12:** descoberta e catalogação do conteúdo atual identificado, incluindo famílias procedurais e os quatro domínios dinâmicos conhecidos, concluídas com evidência de engine. Não equivale a captura de todas as combinações futuras ou reconstrução/renderização web integral. Buffers são Godot Variant v4, não glTF diretamente consumível; LOD nativo implícito, blend shapes, shaders completos, UIDs/arbitrariedade dinâmica futura e estados não amostrados têm limitações. Migração de composições/mapas e integração visual seguem 00-13/17/31/32/34; não promover estados dessas tarefas. 
