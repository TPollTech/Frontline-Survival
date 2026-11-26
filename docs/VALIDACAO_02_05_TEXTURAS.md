# 02-05 — Texturas e normal maps: candidatos autorais

26/11/2026. Escopo exclusivo 02-05. Base 823c26df6311e18f497ab4786ce7fb51b0714ed6; 02-04 concluído por execução anterior na main, 02-03 permanece parcial. Consultados AGENTS.md, checklist, critérios, especificação, padrão artístico, biblioteca PBR e serviço de materiais. Não promover outros IDs.

## Implementação e procedência

- `tools/asset_pipeline/parametric/production_texture_maps.py`, blob 1ed9f217c82902dc759450e80df18c734b132c76: seis famílias procedurais originais com ruído periódico interpolado, microestrias direcionais, granulação e veios ondulados. Função de pixels sem dependência externa; adaptador candidato para TextureData, PBRMaterial e MaterialLibrary já existentes. Não duplica a serialização PNG da biblioteca.
- `tests/test_production_texture_maps.py`, blob 7cf019dac877330e5e5df614371044c1e9813e11: nove testes focados.
- Base color RGB8 neutro, sRGB, destinado a multiplicar a cor autoral de vértice, sem luz direta pintada. Normal tangent-space +Y com componente Z positiva e derivadas centrais periódicas; ORM linear: R=255 (sem AO autoral), G=rugosidade absoluta com microvariação, B=metalicidade absoluta. Evitar multiplicar novamente os fatores absolutos. Procedência autoral, nenhuma textura externa, adaptador declara CC0-1.0.
- Frequências, contraste e intensidade são escolhas artísticas iniciais, não medições de materiais físicos. A madeira ainda apresenta repetição regular visível; requer refinamento e teste no modelo.

## Execução real

Python em diretório temporário, dois arquivos idênticos aos blobs publicados, importação por namespaces sem o pacote completo. `python -m unittest discover -s tests -v` — 9/9 OK (0,346 s): cobertura/dimensões, determinismo, distinção dos seis normais, neutralidade do albedo, comprimento dos normais e Z positivo, canais ORM, periodicidade do campo e amostras adjacentes, variação por seed, rejeição de entradas inválidas.

Adicionalmente: 18 mapas RGB8 256×256 gerados com os fatores da tabela atual de perfis PBR e seeds 205+i (ordem alfabética), salvos temporariamente com Pillow 12.3.0 e abertos em folha de inspeção. Repetição dos seis conjuntos produziu buffers idênticos 6/6. NumPy 2.3.5 verificou os 393.216 texels de normal (seis mapas): todos Z positivos, erro máximo de norma ao quadrado 0,008766, menor que 0,025. ORM de todos os conjuntos: R=255, B=0 ou 255 conforme perfil. Hashes SHA-256 dos buffers RGB8 (não dos PNGs):

| Perfil | Base color | Normal | ORM |
|---|---|---|---|
| brass | ac70a0f73fef50781f3fb7cfb1c29a731767357fa12efc8457d16b71789e055c | 7cde1ef6cbc8c4e1a85ba3b3b23b9c8af8772b9908bdf08af2b9c0a582b017f5 | 2396bc8ae3fe9d34b296b59c9df81042643b47270f495b3d7a686d56dcd007c7 |
| exposed_metal | 2a998aaa3e043a50c8fe85c3c5797179cb16fa9c692e86a17a1ea8d2ea74d41e | b7f1688f5aa7b8e2c619c027402b27d7f84181647a14abee88fcb2a0277e1b17 | f6f77caea44fce92e2e25f2252b8a4611ea7e24af59ebb2c8dc285606fa5257b |
| painted_metal | c32e1e47c0ad85895f15a10a1de8d10569d453b0e5d1c1b15a8f35acdfea2bf2 | 47434e46a7b0db9ebf4b0ced6c737a780b691765d7fb7366e380fe8403924017 | 81fef36ccd565e775023a1bf4a137646f021e1338bf39b5f56f6f14633536f09 |
| polymer | 6a5d0230578712e9bfc947101fa73d1e767d032c6a45122c57ac91d00f7eb0a0 | 43ba0fc3f5e13f5c831457d516cae07abf9d12d0fbb67e0bb09b40425c55d1a3 | 76935791749ef3c542683d0a1920cf6de057fc7afdc3f5a706bc02854c376e85 |
| rubber | f8805c67ebe2297b4ac0b38fcbbbc93f972bab6af76fe9c14d62bdbab17725f2 | 147f4dd2e6abf263a38fba66fbc8be819aaeb78c9b22360a91d512958ef8ce57 | a4d35b14cd57ee88336061a0e6f2e911a0fad4fb692a29e3243b4fbd5375cb1c |
| wood | 08b5bb69a0024115387b85d68ae55f44b2d6e8108eb81ed49abdf558f8b04383 | db1ccbffce196cd61152e1650d89f2a4fc9b2dc5413acc7b422614c79e7b526e | df6ca5a2f795d2ba99e9973acfd755e124a96bd5bf36f20094c4c7806fbeed65 |

Inspeção dos mapas isolados: estrias de metal e latão distinguíveis, granulações diferentes para polímero/pintura/borracha, madeira com veios marcados mas repetitivos. Não se trata de renderização PBR em malha, inspeção de UVs ou teste de emendas na engine.

## Bloqueios e próximo passo

Ambiente desta execução: /mnt/data sem checkout, Chromium disponível, Godot/Blender ausentes do PATH, clonagem Git falhou por DNS. Não executado o adaptador build_library com o pacote completo; nenhum PNG candidato publicado como asset de produção. Integrar o adaptador com a biblioteca real e validar serialização; aplicar mapas por superfície explícita, revisar UVs e tangentes consistentes com o modo de projeção, conciliar canais ORM com os fatores efetivos do Godot e Studio, preservar o acabamento de 02-04. Verificar artefatos e repetição sob iluminação normal na distância de uso. Não alterar fontes geométricas ou silhuetas sem justificativa. Sem CI, ZIP, mudança de shader, GLB ou gameplay. Estado parcial.

## Segunda execução — integração isolada com a biblioteca canônica

Base ec99f6fa3de9ada5c02b5bb5374c00038f6e45f5. Recuperados os quatro arquivos de fonte e conferidos os blobs Git locais antes da edição: model.py 06713595b8709a822f1f103177b57f7d047662a2; pbr.py 187633e377b25ae451becf8a22c9a50a89ddf715; production_texture_maps.py 1ed9f217c82902dc759450e80df18c734b132c76; production_surface_profiles.json 29350aa5cf025a2ca53a2331c9d67962b0486074. Executados em diretório temporário, importação por namespaces, sem checkout completo do jogo. A biblioteca PBR e os perfis permanecem inalterados.

Corrigido no candidato o mascaramento de seeds inválidas pelo adaptador e a aceitação de resoluções não inteiras; a validação antecede a geração, sem mudar o algoritmo para entradas válidas. Novo blob dbe9f730f828ecb75ceb54de6441f395795035e3. Teste focado `tests/test_production_texture_library.py` (blob 0877604447753bc6ee8a6b4a0f6588ffa7f854ed), executado com Python 3.13.5: `python -m unittest discover -s tests -p test_production_texture_library.py -v` — 6/6 OK, 5,256 s. Verificados vínculos dos seis materiais aos 18 mapas, procedência e espaços de cor no manifesto, serialização/decodificação real de 18 PNGs (CRC, dimensões, filtro, igualdade dos bytes RGB e SHA-256), determinismo mesmo com ordem de perfis invertida, rejeição de arquivo truncado/ausente e sobrescrita do diretório, rejeição de configurações inválidas.

A biblioteca gerada em 256×256, seed 205, possui manifesto canônico SHA-256 `53439e35e3c9a360c86216377a1315aeb9537099cb657abf6866c3c77718badc`. Conferidos os 18 SHA-256 de pixels com a tabela anterior: coincidem. Não reclassificar esse resultado como teste de importação Godot; o espaço de cor é metadado do manifesto, não garantia da configuração do importador. Os PNGs foram gerados temporariamente, não publicados como texturas de produção. O gerador de mapas não foi alterado artisticamente, a repetição da madeira permanece aberta.

Ambiente nesta execução: Godot/Blender/Firefox ausentes do PATH, Chromium presente, Git sem resolução DNS para github.com, sem checkout completo. O serviço de materiais do jogo continua com os dois conjuntos antigos. Faltam vinculação das texturas por superfície no runtime/Studio, validação do modo de projeção, UVs/tangentes reais e inspeção à distância de uso; não alterar 02-03 ou 02-04. Nenhum GLB, shader, textura de produção, gameplay, Action ou instalador modificado. Estado parcial.
