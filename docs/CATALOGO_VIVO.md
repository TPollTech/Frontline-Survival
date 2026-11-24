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
