# AU004 — независимый НЕГАТИВНЫЙ аудит TD-DOM-19 fix (ПОСЛЕ-версия)

**Роль:** независимый отрицательный аудитор; не worker, не ревьюер, не принимающий.
**Версия:** code_digest `08aa9a9b978831806bd0ef24fe26f7214ab21b31ca6d2bbe7d27a61bd29bfe6f` (16 файлов; изменены `mockup/admission.py`, `mockup/server.py`; добавлен `mockup/public_dto.py`; baseline `715b1ca8…ba3` 15 файлов — пересчитан мной независимо, MATCH; остальные 13 файлов байт-идентичны baseline).
**product_acceptance:** false · **is_approval:** false · **ВЕРДИКТ:** **REQUEST_CHANGES** (никогда SAFE).
**Собственный прогон:** seed 92041, runtime/AU004/run-au004, реальные MCP stdio subprocess (несколько свежих PID), независимые SQL/file oracle read-backs. Artifacts: artifacts/AUDITOR_AB003_TD19.json, reports/AUDITOR_AB003_TD19.md, runtime/AU004/**.

---

## Секция 0 — «Сомнительное, что я проверил» (обязательна, перед вердиктом)

| Что показалось подозрительным | Как проверил | Что оказалось |
|---|---|---|
| Digest может быть заимствован из receipts worker/reviewer | Пересчитал независимо по методу SEC003 (sorted-json map sha256) | MATCH after `08aa9a9b…` 16 файлов; только admission.py/server.py изменились, public_dto.py добавлен; рассинхрона нет |
| AA-only caller может увидеть foreign ветку через `Claim.dependencies` / `provenance.dependencies` (public DTO `('map','int')` без scope-фильтра) — worker/reviewer никогда не сеяли такой фикстур | union-author создал AA-claim с deps `{AA:1, AB:2}` (AB live rev2); AA-only автор читает query/snapshot/resume/export | **НАХОДКА AU004-F-01:** `dependencies={AA:1, AB:2}` и `provenance.dependencies` утекают AA-only на всех трёх поверхностях + `AB: 2` в байтах YAML export. `read_snapshot` при этом корректно `{AA:2}` — утечка идёт по другому полю |
| `origin_branch=AB` у shared-claim мог быть нелегальной утечкой AA-only | Создал AB-claim, затем AA-applicability (реальное MCP sharing), прочитал AA-only | OK: `origin_branch=AB` появляется ТОЛЬКО у явно applicability-shared claim — это легитимная provenance общего claim, а не скрытое продвижение. X2b не утечка |
| Глобальный gate мог быть отключён ради ACL или «урезан» в публичном Broken | Свежая disposable копия, коррупция среднего AB-события (invalid UTF-8), 7 tools × 2 свежих PID | OK: единый `CHAIN_BROKEN` + `{status,readiness,ready_for_owner_review,blockers,simulated}` без foreign locator; DB не меняется инструментами; oracle отдельно находит seq-уровень AB-разрыва (EVENT_SHAPE_INVALID) |
| Internal delivery proof мог быть урезан ради sanitization | Синхронизация на свежем run; SQL read-back delivery_observations/delivery_acks | OK: полный internal stamp (`chain_head` + AA+AB revisions + `port_reported`) в каждой observation; observation→attempt→ack связаны; 4 obs / 4 ack; дублей записи нет |
| Оба MCP-канала (text/structuredContent) могут расходиться | Сравнил canonical json всех поверхностей | OK: text == structuredContent семантически НА ВСЕХ поверхностях и в gate |
| YAML export мог не быть scoped | Байты экспортированного AA-файла | OK: AA-канарейка есть, AB-канарейки нет, `chain_head`/`events` нет. НО: если deps несут AB (см. AU004-F-01), эта же утечка попадает и в YAML-байты |
| B-side: direct AB-чтение у AA-only | `dom_query(branch=AB)` у author branches=AA | OK: SCOPE_DENIED |

**Пустая секция 0 отсутствует, раскопано.** Никаких пропущенных сомнений без записи.

---

## Находки (fix открывает новый путь; TD19 не дублирую)

### AU004-F-01 — MAJOR — foreign-branch metadata утекает через unscoped dependency/provenance maps

**Инвариант:** public DTO не должен отдавать foreign-branch existence / head revision caller'у, чей launch-grant не включает эту ветку, ни через одно поле/байты.

**Источник:** `mockup/public_dto.py` — `RECORDS['Claim'].dependencies` = `('map','int')` (~стр.84), `Provenance.dependencies` = `('map','int')` (~стр.78). `read_snapshot()` (стр.283–291) скалит ТОЛЬКО `ReadSnapshot.revisions`; claim/provenance dependency-карты НЕ скалятся по launch-grant. `admission.py/check_references` для claim-операций ранне-возвращается (`if p['operation']!='append': return`), поэтому union-автор может легитимно создать AA-claim с реальной AB-веткой в deps.

**Initial conditions:** AA head=rev2, AB head=rev2. Union-автор (branches `AA,AB`) admit'ит AA-claim c `dependencies={'AA':1,'AB':2}`. AA-only caller (author, branches `AA`) читает.

**Repro:** `runtime/AU004/au004_probe.py` (seed 92041).
- `dom_query`/`dom_snapshot`/`dom_resume` → `claims[1].dependencies={AA:1,AB:2}`, `history[1].provenance.dependencies={AA:1,AB:2}` (6 hits в `X1_foreign_deps_leaked`);
- `dom_export` → `AA-2-*.yaml` содержит `AB: 2` (2 hit’а);
- `read_snapshot` остаётся `{AA:2}` (корректно) — свидетельство, что утечка именно по unscoped полю.

**Expected:** AA-only caller не должен видеть AB-name или её revision ни в одном поле/байтах; deps/provenance maps должны скалиться по caller launch-grant так же, как `read_snapshot.revisions`.

**Actual:** `AB:2` видна AA-only на query/snapshot/resume и в YAML-байтах. Text и structuredContent идентичны — маскировки расхождением каналов нет.

**Evidence:** `runtime/AU004/run-au004/results-au004.json` (X1_foreign_deps_leaked, aa_only_surfaces), raw frames `healthy/frames-*.jsonl`, YAML `export-probe/exports/AA-2-*.yaml` стр.35/104 `AB: 2`, stderr-PID logs.

**debt_ref:** НОВЫЙ путь (не дубликат TD19). Рекомендую зарегистрировать новый долг (например `TD-DOM-19-scope-extension` / новый `TD-DOM-NN` «public dependency/provenance map scope filtering»). Пять полей, которые закрывает сам TD19 (chain_head / глобальные revisions / events / head_hash / broken_event_id), закрыты корректно — этот фикс их и закрыл; дефект — СВЕРХ них, в несъfilter-ованных картах зависимостей.

**Почему worker/reviewer не нашли:** их фикстуры всегда использовали пустые/отсутствующие deps и никогда не авторили AA-claim с живой foreign-AB-зависимостью, читаемый AA-only. Vetvis worst-case cross-grant поверхность не была посеяна. Это МОЯ собственная атакующая вариация.

---

## Что подтверждено зелёным (не блокирует TD19-часть)

- Gate: uniform `CHAIN_BROKEN`, без foreign locator, DB не мутируется инструментами, oracle независимо находит разрыв. → global integrity gate сохранён.
- Delivery: полный internal stamp + ack-цепочка + без дублей записи. → internal proof восстановления/доставки сохранён.
- Оба канала — один безопасный объект (text==structured) — держится на всех поверхностях.
- B-side isolation и scope read_snapshot держатся.
- Пять канонических полей TD19 (chain_head/global revisions/events/head_hash/broken_event_id) больше не утекают.

---

## NOT_CHECKED / ограничения

- **Timing: NOT_CHECKED** — не измерялось (замеров времени нет).
- CP-PL-10 busy/read-only (WAL) подкейсы: NOT_TESTED (наследие прошлых срезов, не перепрогонялось).
- Реальная production auth/identity — вне модели (launch-гранты — trusted-launcher фикстура, не auth).
- B/C/D, UD-01…06, refinement/search/Git/auth/OS/checkpoint — вне scope данного TD19-среза.
- Это delta-аудит TD19-fix, не полная системная приёмка безопасности.

---

## Эскап-хэтч (находки)

| Уровень | Что нашёл | Что сделал | Где зафиксировано |
|---|---|---|---|
| 2 | AU004-F-01 (major, confidentiality) НОВЫЙ путь: unscoped Claim/Provenance dependencies карты утекают foreign branch revision AA-only | Зафиксировал в артефакте/отчёте; tech_debt не правил (read-only); рекомендация новый долг | artifacts/AUDITOR_AB003_TD19.json, reports/AUDITOR_AB003_TD19.md |
| — | Проверенных нарушений вне AU004-F-01 нет | зелёные части задокументированы | секция выше |

---

## Вердикт

**REQUEST_CHANGES.** Пять канонических полей TD19 закрыты и глобальный gate+delivery сохранены (это зелёная часть засчитана). Но найден новый, ранее не посеянный путь утечки hidden-branch metadata через unscoped `Claim.dependencies`/`Provenance.dependencies` (и через YAML export), что нарушает ту же цель конфиденциальности TD19 другим полем. Рекомендую НЕ закрывать TD19 полностью, пока не будет добавлена scope-фильтрация dependency/provenance maps (или явное решение/скоп-заметка), и зарегистрировать новый долг. Решение о закрытии TD19 — за OMH/заказчиком, не за аудитором.