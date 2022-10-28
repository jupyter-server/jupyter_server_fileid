# Changelog

<!-- <START NEW CHANGELOG ENTRY> -->

## 0.6.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.5.0...328d893ff2323f20925e036e57eb62f302fa94e2))

### Enhancements made

- set default file ID manager to arbitrary [#37](https://github.com/jupyter-server/jupyter_server_fileid/pull/37) ([@dlqqq](https://github.com/dlqqq))
- remove unused REST API [#36](https://github.com/jupyter-server/jupyter_server_fileid/pull/36) ([@dlqqq](https://github.com/dlqqq))
- allow for recursive moves, copies, deletes in ArbitraryFileIdManager [#35](https://github.com/jupyter-server/jupyter_server_fileid/pull/35) ([@dlqqq](https://github.com/dlqqq))
- prefix root dir to records in ArbitraryFileIdManager [#34](https://github.com/jupyter-server/jupyter_server_fileid/pull/34) ([@dlqqq](https://github.com/dlqqq))
- use UUIDs for default file ID manager implementations [#30](https://github.com/jupyter-server/jupyter_server_fileid/pull/30) ([@dlqqq](https://github.com/dlqqq))
- implement optimistic get_path() in LocalFileIdManager [#38](https://github.com/jupyter-server/jupyter_server_fileid/pull/38) ([@dlqqq](https://github.com/dlqqq))
- Fix abstract base class definition [#33](https://github.com/jupyter-server/jupyter_server_fileid/pull/33) ([@kevin-bates](https://github.com/kevin-bates))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-25&to=2022-10-28&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Acodecov-commenter+updated%3A2022-10-25..2022-10-28&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-25..2022-10-28&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Akevin-bates+updated%3A2022-10-25..2022-10-28&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Awelcome+updated%3A2022-10-25..2022-10-28&type=Issues)

<!-- <END NEW CHANGELOG ENTRY> -->

## 0.5.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.4.2...d968097b42f7b4d21fd851bd69c23a34098e675a))

### Enhancements made

- implement autosync_interval trait [#25](https://github.com/jupyter-server/jupyter_server_fileid/pull/25) ([@dlqqq](https://github.com/dlqqq))

- Allow arbitrary contents managers [#24](https://github.com/jupyter-server/jupyter_server_fileid/pull/24) ([@davidbrochart](https://github.com/davidbrochart))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-21&to=2022-10-25&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Acodecov-commenter+updated%3A2022-10-21..2022-10-25&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adavidbrochart+updated%3A2022-10-21..2022-10-25&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-21..2022-10-25&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Akevin-bates+updated%3A2022-10-21..2022-10-25&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Apre-commit-ci+updated%3A2022-10-21..2022-10-25&type=Issues)

## 0.4.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.4.1...15a183a28eb63741659971585acff9a23be05c18))

### Bugs fixed

- pass self.config to file ID manager class [#23](https://github.com/jupyter-server/jupyter_server_fileid/pull/23) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-20&to=2022-10-21&type=c))

[@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-20..2022-10-21&type=Issues)

## 0.4.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.4.0...99bd17b2502e67fbe2b4952675762027a9d438c2))

### Enhancements made

- log root_dir and db_path before connection [#22](https://github.com/jupyter-server/jupyter_server_fileid/pull/22) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-20&to=2022-10-20&type=c))

[@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-20..2022-10-20&type=Issues)

## 0.4.0

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.3.2...a4a6683f4f3e134f2a06788ca6347d57aa07c1cd))

### Enhancements made

- update get_path() to return a path relative to root_dir [#21](https://github.com/jupyter-server/jupyter_server_fileid/pull/21) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-19&to=2022-10-20&type=c))

[@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-19..2022-10-20&type=Issues)

## 0.3.2

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.3.1...16535e222d705401142ad98b1d869fb30754d47e))

### Merged PRs

- add boolean sync argument to get_path() [#20](https://github.com/jupyter-server/jupyter_server_fileid/pull/20) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-18&to=2022-10-19&type=c))

[@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-18..2022-10-19&type=Issues)

## 0.3.1

([Full Changelog](https://github.com/jupyter-server/jupyter_server_fileid/compare/v0.3.0...b17224adff24fd729683c9d8ebe46c6dad3c6752))

### Merged PRs

- Listen to ContentsManager save events [#18](https://github.com/jupyter-server/jupyter_server_fileid/pull/18) ([@dlqqq](https://github.com/dlqqq))
- fix get_path() runtime errors [#16](https://github.com/jupyter-server/jupyter_server_fileid/pull/16) ([@dlqqq](https://github.com/dlqqq))
- Add GET/PUT file ID/path handlers [#12](https://github.com/jupyter-server/jupyter_server_fileid/pull/12) ([@davidbrochart](https://github.com/davidbrochart))
- Cleanup [#11](https://github.com/jupyter-server/jupyter_server_fileid/pull/11) ([@davidbrochart](https://github.com/davidbrochart))
- Use hatch for version [#10](https://github.com/jupyter-server/jupyter_server_fileid/pull/10) ([@davidbrochart](https://github.com/davidbrochart))
- add basic cli and drop command [#9](https://github.com/jupyter-server/jupyter_server_fileid/pull/9) ([@dlqqq](https://github.com/dlqqq))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyter-server/jupyter_server_fileid/graphs/contributors?from=2022-10-10&to=2022-10-18&type=c))

[@codecov-commenter](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Acodecov-commenter+updated%3A2022-10-10..2022-10-18&type=Issues) | [@davidbrochart](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adavidbrochart+updated%3A2022-10-10..2022-10-18&type=Issues) | [@dlqqq](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Adlqqq+updated%3A2022-10-10..2022-10-18&type=Issues) | [@ellisonbg](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Aellisonbg+updated%3A2022-10-10..2022-10-18&type=Issues) | [@kevin-bates](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Akevin-bates+updated%3A2022-10-10..2022-10-18&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Apre-commit-ci+updated%3A2022-10-10..2022-10-18&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyter-server%2Fjupyter_server_fileid+involves%3Awelcome+updated%3A2022-10-10..2022-10-18&type=Issues)
