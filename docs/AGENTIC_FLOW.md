# Predict – Gate – Settle (PGS)

**Forecast ile denetlenen agent loop, candidate selection ve handoff ile agentic Text-to-SQL.**

Küçük bir policy agent soruyu tool'larla çözer; soru belirsizse kullanıcıya sorar. Her SQL'i çalıştırmadan önce sonucunu tahmin eder (agent forecast) ve gerçek çalıştırma bu tahmini denetler (predict). Cevap, ayrı ayrı yazılmış SQL'lerin aynı sonucu verip vermediğine bakan bir gate'ten geçer (gate) ve dönen her cevap gerçekten çalıştırılmıştır (settle). Agent takılırsa iş büyük bir teacher LLM'e devredilir (handoff). Tasarımın dayandığı literatür [ARASTIRMA.md](ARASTIRMA.md), kodun yapısı [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

## Akış

**Kısaca:** soru → başlangıç bağlamı (1) → agent döngüsü: ara ya da sor (3), SQL dene (4–6) → `submit` → candidate'ler (7) → confidence gate (8) → final check (9) → cevap. Agent takılırsa teacher devralır (10).

![PGS akışı](PGS_akis_TR.png)

| Renk | Bileşen |
|---|---|
| 🟦 Mavi | Policy agent |
| 🟩 Yeşil | Harness (LLM yok) |
| 🟥 Kırmızı | Gerçek veritabanı |
| 🩵 Turkuaz | Teacher LLM |
| 🟪 Mor | Harness kararı (confidence gate, final check) |
| ⬜ Kesikli | Soru bittikten sonra: database memory, experience log, agent eğitimi (ileride) |
| ⚪ Beyaz, yuvarlak | Sistemin dışı: kullanıcının sorusu, `ask_user`'ı cevaplayan kullanıcı ve dönen cevap |

Ok renkleri: **siyah** tool call, **mavi** agent'a dönen observation, **mor** karar sonucu, **turkuaz** handoff, **kesikli** soru bittikten sonra.

## Terimler

| Terim | Anlamı |
|---|---|
| Policy agent | Soruyu adım adım çözen küçük model |
| Tool call | Agent'ın bir turda yaptığı tek istek (ör. `execute_sql`) |
| Observation | Bir tool call'dan sonra agent'a dönen sonuç |
| Tool-call budget | Bir soruda yapılabilecek en fazla tool call sayısı (10) |
| Trial loop | Agent'ın ara, sor, dene, sonuca bak, düzelt diye döndüğü döngü (adım 2–6) |
| Column profile | Bir sütunun özeti: tipi, NULL oranı, en sık değerleri (az değerli sütunlarda hepsi), sayısalsa min ve max |
| Harness | Agent'ın etrafındaki normal kod: tool'ları çalıştırır, kontrolleri ve gate'i yönetir. İçinde LLM yok |
| Agent forecast | Agent'ın bir SQL'i çalıştırmadan önce yazdığı sonuç tahmini |
| Pre-check | SQL çalıştırılmadan önce harness'ın yaptığı ucuz kontroller: salt okuma mı, `EXPLAIN` hata veriyor mu, cache'te var mı (adım 5) |
| Cache | Aynı soru içinde daha önce çalışmış SQL'lerin saklanan sonuçları; aynı SQL yeniden çalıştırılmaz |
| Confidence gate | Candidate'lerin yeterince uzlaşıp uzlaşmadığına bakan karar noktası (adım 8) |
| Final check | Cevap dönmeden önceki son kontrol: gerçekten çalıştı mı, hata yok mu, boşsa bu bekleniyor muydu (adım 9) |
| Candidate | Aynı soruya yazılmış alternatif SQL |
| Consensus | Farklı candidate'lerin aynı sonucu vermesi |
| Adaptive rule | Candidate sayısını duruma göre seçen kural: önce 2 ek candidate, uzlaşma yoksa toplam 8 (adım 7) |
| Handoff | İşin büyük teacher modele bırakılması |
| Evidence | BIRD'ün her soruyla birlikte verdiği kısa ipucu metni (ör. "iade edilen = `status = 'returned'`") |
| `ask_user` | Agent'ın belirsiz bir soruda kullanıcıya kısa bir netleştirme sorusu sorduğu tool (ör. "adet mi, tutar mı?") |
| Clarification | Kullanıcının `ask_user` sorusuna verdiği cevap. Sorunun bir parçası sayılır |
| Search notes | Search sonuçlarının, candidate prompt'u için ayrıca saklanan kopyası |
| Surprise note | Forecast tutmayınca gerçek sonuçla birlikte agent'a dönen kısa not (ör. "dolu bekliyordun, boş geldi") |
| Medium note | Confidence gate medium çıkınca agent'a dönen not: en kalabalık iki candidate grubunun özeti |
| Database memory | Bir veritabanında daha önce yapılmış ve düzeltilmiş hataların kaydı. Adım 1'de bağlama eklenir |
| Result key | Bir sorgu sonucunu karşılaştırmak için kullanılan anahtar. Sonucun bütün satırları küme olarak alınır: satır sırası ve tekrar eden satırlar önemsiz, sütun sırası önemli (BIRD'ün resmi kuralı). Anahtarı aynı olan iki sonuç "aynı sonuç" sayılır |
| Fallback answer | Hiçbir cevap kontrollerden geçmediğinde dönen en iyi cevap; `low_confidence` etiketi taşır |
| Label | Dönen cevabın etiketi: `ok` (kontrollerden geçti), `low_confidence` (geçmedi ama bir cevap var), `no_answer` (çalışan hiçbir SQL yok) |
| Experience log | Her sorunun bütün konuşmasının (agent'ın ve teacher'ın her adımı), cevabın ve cevap doğru mu bilgisinin kaydı; agent'ın eğitim verisi buradan çıkar |
| Split | Verinin bölümü: train (eğitim) ya da dev (değerlendirme). Eğitime yalnızca train girer |
| SFT | Modeli doğru örnekleri taklit ettirerek eğitmek |
| On-policy distillation | Öğrenci modelin kendi denemelerini teacher'ın düzeltmesiyle eğitmek |
| RL | Modeli denemelerinin sonucuna göre reward ve ceza vererek eğitmek |
| Guardrail | Harness'ın agent'ı koruyan kuralları: aynı çağrının tekrarı yok, uzun sonuç kırpılır, bağlam dolarsa sıkıştırılır |
| EXPLAIN | Veritabanının sorguyu çalıştırmadan planını göstermesi. SQLite'ta sözdizimi ve eksik tablo/sütun hatalarını da çalıştırmadan yakalar |
| Seed | Rastgeleliği sabitleyen sayı; farklı seed'lerle tekrar denemek, sonucun şans olmadığını gösterir |
| Phase / aşama | Phase: büyük dönem (Phase 1 BIRD, Phase 2 Mini-Interact). Aşama: tek bir parça ekleyen, numaralı küçük iş (KOD_YAPISI.md "Yazım sırası") |

## Bileşenler

- **Policy agent (Qwen3.5-4B):** Her adımda hangi tool'u çağıracağına karar verir. SQL çalıştırmadan önce sonucu tahmin eder. Şimdilik eğitilmemiş hâliyle kullanılır; ileride experience log'la harness'ın içinde eğitilir.
- **Harness (düz Python, LLM yok):** Tool'ları çalıştırır, kontrolleri yapar, confidence gate'i ve final check'i yönetir. Guardrail'leri de o uygular.
- **Veritabanı (SQLite, salt okunur):** `execute_sql`.
- **Kullanıcı:** `ask_user` sorularını cevaplar. Soru hep terminale gelir, `run.py`'de de `evaluate.py`'de de. Deneyi yürüten kişi, sorunun ne demek istediğini bilen bir kullanıcı gibi tek cümleyle cevaplar; SQL'i ya da sonucu söylemez. Doğru SQL agent'ın bağlamına hiç girmez, yalnızca puanlamada kullanılır.
- **Teacher LLM (Qwen3.6-27B, 4-bit):** Yalnızca handoff'tan sonra devreye girer. Agent'ın kaldığı yerden devam eder.

## Akış adım adım

Görseldeki numaralar bu adımlardır. İş bölümü basit:
- **Agent** ne yapılacağına karar verir: hangi tool, hangi SQL, forecast, kullanıcıya ne sorulacağı, ne zaman `submit`.
- **Harness** geri kalan her şeye karar verir: kontroller, candidate'ler, confidence gate, final check, handoff.

Tool argümanları ve sayısal sınırlar [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

### 1. Başlangıç bağlamı

**Neden:** Her search bir tool call harcar. Bilgi baştan verilirse budget denemeye kalır.

Harness agent'a şunları verir:
- Soru ve varsa evidence.
- Şema: tablolar, sütunlar, BIRD'ün sütun açıklamaları, foreign key'ler.
- Column profile'ları. Metin sütunlarında en sık 10 değer (en fazla 10 farklı değeri olan sütunlarda, ör. `status`, bütün değerler); geri kalan değerleri agent gerekirse `search_values` ile bulur. Sayısal sütunlarda yalnızca en küçük ve en büyük değer.
- Database memory: bu veritabanında daha önce yapılmış hatalar ve düzeltmeleri (soruya en çok benzeyen 3 kayıt).

Bağlam en fazla 16K token olur. Taşarsa soruya gereken tabloları bir LLM seçer (schema linking): şema sığacak parçalara bölünür, model her parçadan gereken tabloların adlarını yazar, seçimler birleştirilir. Seçilmeyen tablolar tek satıra iner (yalnızca sütun adları ve tipleri). Model şemayı yeniden yazmaz, yalnızca tablo seçer; böylece olmayan bir sütun uyduramaz. BIRD dev ve Mini-Interact'te bağlam bu sınırı hiç aşmıyor (en büyüğü ~14K).

Database memory örneği: önceki bir soruda agent `status = 'iade'` yazdı, sonuç boş geldi, sonra `'returned'` ile düzeltti. Bu hata ve düzeltmesi kaydedilir; yeni bir iade sorusunda agent bunu baştan görür.
→ 2

### 2. Agent ne yapacağına karar verir

Agent her turda tek bir tool call yapar:
- Bir değerin veritabanında nasıl yazıldığını bilmiyorsa → `search_values` → 3
- Soru belirsizse ve şema, değerler ya da evidence bunu çözmüyorsa → `ask_user` → 3
- Bir SQL'i denemek istiyorsa → `execute_sql` → 4
- Cevaptan eminse → `submit` → 7

Her observation'dan sonra agent buraya döner. Her tool call budget'tan bir düşer (en fazla 10). Reddedilen istekler ve tool call olarak okunamayan çıktılar da sayılır; hata agent'a döner. Son 2 tool call kalınca sonucun altına "çalıştırdığın bir sorgu soruyu cevaplıyorsa şimdi submit et" hatırlatması eklenir. Budget biterse harness handoff'u zorlar → 10.

**Guardrail'ler.** Küçük modeller bazı tipik hataları sık yapar; bunlar sistemi bozmasın diye harness her adımda üç basit kural uygular (DualSQL).
1. **Tekrar yok:** Aynı çağrı (aynı tool, aynı argümanlar) ikinci kez gelirse çalıştırılmaz; "bunu zaten denedin" notu ve önceki sonuç döner, budget yine düşer. `execute_sql`'de yalnızca SQL'e bakılır. `submit` hariç: medium note'tan sonra aynı SQL'i yeniden göndermek geçerli bir seçimdir.
2. **Uzun sonuç kırpılır:** Agent en fazla 20 satır görür, yanında toplam satır sayısı yazar.
3. **Bağlam sıkıştırılır:** Konuşma 32K token'ı aşarsa en eski sonuçlar tek satırlık özete iner (ör. "Columns: name | 358 rows").

### 3. Bilgi toplama: `search_values` ve `ask_user`

Agent bunları istediği an kullanır. Adım 1 zengin olduğu için çoğu soruda az gerekir.
- **`search_values`:** Bir kelimenin veritabanında hangi sütunda, hangi değer olarak geçtiğini bulur; benzer yazılanlar dahil. Örnek: "Los Angles" → `city = 'Los Angeles'`.
- **`ask_user`:** Soruyu yalnızca kullanıcı netleştirebiliyorsa kısa bir soru sorulur. Örnek: "adet mi, tutar mı?" → "adet". Soru başına en fazla 5 kez (agent ve teacher toplam).

Arama her şeyi bulamaz: soruda "iade", veritabanında `'returned'` yazıyorsa eşleşmez. Bu durumda evidence çoğu zaman eşleşmeyi verir; vermezse agent kullanıcıya sorar ya da yanlış değerle boş sonuç alır ve surprise note onu başka bir değer denemeye yönlendirir.

Sonuç observation olarak agent'a döner. Harness ayrıca bir kopyasını saklar: search sonuçlarını **search notes**, kullanıcının cevaplarını **clarification** olarak. İkisi de adım 7'de candidate'lere verilir. Neden kopya? Candidate'ler agent'ın geçmişini görmez; görse agent'ın SQL'ini kopyalar. Kopya sayesinde bulunan bilgiyi (ör. `'returned'`) alırlar, SQL'i almazlar.
→ 2

### 4. `execute_sql` isteği ve forecast

Agent SQL'le birlikte sonucun ne olacağını da tahmin eder (forecast). Bunlar `execute_sql`'in argümanlarıdır:
- `type` (zorunlu): `error` (hata), `empty` (boş) ya da `rows` (dolu).
- `columns` ve `rows` (`rows` ise, yazabiliyorsa): beklenen sütunlar ve satır aralığı (`0`, `1`, `2-10`, `11-100`, `100+`).
- `trust` (isteğe bağlı): emin mi, değil mi.

Örnek: `execute_sql(sql="SELECT ...", type="rows", columns=["category", "n"], rows="1", trust=true)`

`type` yoksa ya da bir alanın biçimi bozuksa istek reddedilir (→ 2). Küçük biçim hataları düzeltilir (ör. `"true"` → `true`, `358` → `"100+"`); alanlar iç içe bir `forecast` nesnesinde gelse de kabul edilir.
→ 5

### 5. Pre-check

**Neden:** Bozuk bir sorguyu çalıştırmadan, ucuz yoldan yakalamak.

Agent'ın SQL'leri, candidate'ler ve final check buradan geçer. Harness sırayla üç soru sorar:
1. **Yazma mı yapıyor?** `SELECT` ya da `WITH` ile başlamıyorsa reddedilir. Örnek: `DELETE FROM orders`.
2. **Bozuk mu?** `EXPLAIN` sorguyu çalıştırmadan yazım hatasını, olmayan tabloyu ve sütunu yakalar. Olmayan bir sütun başka bir tabloda varsa not bunu da söyler.
3. **Daha önce çalıştı mı (cache)?** Çalıştıysa yeniden çalıştırılmaz, saklanan sonuç kullanılır. Örnek: bir candidate agent'ın SQL'ini birebir yeniden yazar.

1–2'de takılan sorgunun notu agent'a döner (→ 2).
→ 6

### 6. Gerçek çalıştırma ve karşılaştırma

Sorgu veritabanında salt okunur çalıştırılır (en fazla 30 saniye) ve gerçek sonuç agent'ın forecast'iyle karşılaştırılır.
- Forecast'in "tuttu" sayılması için result type aynı olmalı; `rows` ise, yazıldıysa sütun sayısı ve satır aralığı da. Sütun adlarına bakılmaz, çünkü aynı sütun farklı takma adla gelebilir.
- Agent'a gerçek sonuç (kırpılmış hâli) döner. Forecast tutmadıysa yanında bir surprise note gelir. Örnek: "1 sütun ve 100+ satır bekliyordun, sonuç boş".
→ 2

> Adım 2 → 6 arası agent'ın **trial loop**'udur: ara, sor, dene, sonuca bak, düzelt.

### 7. `submit` → candidate'ler

**Neden:** Bir SQL'in hatasız çalışması doğru olduğunu göstermez. En sağlam sinyal, ayrı ayrı yazılmış SQL'lerin aynı sonucu vermesidir (consensus).

- **Önce:** Submit edilen SQL çalışmıyorsa (pre-check'ten geçmiyor ya da hata veriyorsa) candidate üretilmez; hata agent'a döner (→ 2).
- **Kim yazar:** Agent'ın SQL'i de bir candidate'tir. Diğerlerini aynı policy modeli tool'suz, tek seferde yazar. Prompt'ta adım 1 bağlamı, search notes ve clarification'lar var. Agent'ın SQL'i prompt'a konmaz; konursa model onu kopyalar.
- **Kaç tane (adaptive rule):** Önce 2 ek candidate. Hepsi agent'ın SQL'iyle aynı sonucu verirse durulur. Ayrışırlarsa toplam 8'e tamamlanır.
- **Nasıl çalışır:** Her candidate adım 5–6'dan geçer (forecast'siz). Daha önce çalışmış SQL cache'ten gelir. Candidate'ler budget'tan düşmez, sonuçları agent'a dönmez (tek istisna adım 8'deki medium note).
- **Gruplama:** Result key'i aynı olanlar, yani gerçek sonucu aynı olanlar, bir gruptur. Hata veren candidate hiçbir gruba girmez.
- **Seçim:** En kalabalık grup seçilir. Başa baş ise en önce üretilmiş candidate'i içeren grup; agent'ın SQL'i ilk olduğu için onun grubu. Grubun cevabı grubun ilk SQL'idir.
- **İkinci `submit`:** Agent medium note ya da final check notundan sonra yeniden `submit` ederse candidate'ler baştan üretilir, çünkü search notes ve clarification'lar değişmiş olabilir.
→ 8

### 8. Confidence gate

Karar yalnızca consensus'a bakar: en kalabalık grupta kaç candidate var?
- **High:** 3/3 ya da 8'in en az 6'sı → 9.
- **Medium:** 8'in 4–5'i → agent'a medium note döner → 2. Not en kalabalık iki grubu gösterir: temsilci SQL, kaç candidate'te olduğu, sütunlar, satır sayısı, ilk 3 satır. Agent birini seçip yeniden `submit` edebilir, yeni bir deneme yapabilir ya da `ask_user` ile sorabilir. Bu en fazla bir kez olur; ikinci medium → 10.
- **Low:** 8'in en fazla 3'ü → 10.

### 9. Final check

Cevap dönmeden önceki son kontrol:
- **Salt okuma mı, tablolar ve sütunlar var mı?** (adım 5)
- **Gerçekten çalışıyor mu?** Çalıştırılmadıysa (ör. teacher'ın cevabı) harness şimdi çalıştırır; böylece dönen her cevap gerçekten çalıştırılmış olur. Hata veren cevap geçmez.
- **Sonuç boşsa, bu bekleniyor muydu?** Bu SQL için yazılan son forecast "boş" değilse ya da forecast yoksa geçmez.

Geçti → **cevap döner ✔** (label `ok`). Geçmedi → nedeni agent'a not olarak döner → 2. İkinci kez geçmezse → 10.

### 10. Handoff

Handoff'u harness yapar: budget bitti, confidence low, ikinci kez medium, final check 2 kez geçmedi.
- Teacher sıfırdan başlamaz, agent'ın kaldığı yerden devam eder: bütün konuşmayı ve handoff'un nedenini görür.
- Agent'ınkinin yarısı kadar yeni bir budget'la (5 tool call) ve aynı tool'larla çalışır (adım 2–6). `ask_user` için yalnızca sorunun kalan hakkını kullanır.
- Teacher'ın `submit`'i candidate'lere gitmez, doğrudan final check'e gider. Geçerse `ok`. Geçmezse tekrar denenmez: SQL çalışıyorsa (ör. beklenmeyen boş sonuç) `low_confidence` ile döner, hiç çalışmıyorsa fallback answer döner. Teacher budget'ı içinde `submit` etmezse de fallback answer döner.

**Fallback answer** sırası: adım 7'nin en son seçtiği SQL → yoksa candidate'lerin consensus'u (model 8 tool'suz SQL yazar, en kalabalık grubun SQL'i) → yoksa en son hatasız çalışan SQL → yoksa cevap yok. İlk üçü `low_confidence`, sonuncusu `no_answer` etiketiyle döner. Çalışmayan bir SQL hiçbir zaman cevap olmaz.
→ Cevap ✔

**Dönen cevap:** SQL, label (`ok`, `low_confidence`, `no_answer`) ve cevabı kimin bulduğu (agent ya da teacher).

### İki örnek

**Örnek 1 ("2025'te en çok iade edilen kategori hangisi?"):**
1 (evidence: iade = `status = 'returned'`) → 2 → 4 (SQL + forecast: "dolu, 1 satır") → 5 → 6 (gerçek sonuç, forecast tuttu) → 2 → 7 → 8 (high: 3/3) → 9 → ✔

**Örnek 2 (aynı soru, candidate'ler ayrışırsa):**
1 → 2 → 4 → 5 → 6 → 2 → 7 → 8 (medium: 8 candidate'in 5'i adet sayıyor, 3'ü tutarı topluyor; medium note iki grubu gösterir) → 2 → 3 (`ask_user`: "adet mi, tutar mı?" → "adet") → 2 → 7 (clarification artık prompt'ta) → 8 (high: 7/8) → 9 → ✔

### Soru bittikten sonra

**Database memory:** Cevap döndükten sonra, sorunun kendi konuşmasından yazılır. Soru `ok` ile bittiyse, yolda bir hata ya da surprise note olduysa ve cevap SQL'i o hatalı SQL'den farklıysa bir kayıt yazılır: soru, ilk hatalı SQL, aldığı not, cevap SQL'i. SQL değişmediyse hata sorguda değil forecast'teydi; kayıt bir şey öğretmez. Gold kullanılmaz. `evaluate.py` her deneyi boş bir memory ile başlatır.

**Experience log:** Her soru bitince, nereden çalıştırılırsa çalıştırılsın (`run.py`, `evaluate.py` ya da kullanımdaki bir uygulama), bir satır yazılır: agent'ın (handoff olduysa teacher'ın da) gördüğü konuşmanın tamamı, cevap ve label. Değerlendirmede cevabın doğru olup olmadığı da yazılır (`split = dev`); kullanımda doğru SQL olmadığı için bu alan boş kalır (`split = use`), orada eğitim sinyali teacher'ın çözümleri, label ve kullanıcının cevaplarıdır. Kayıtlar birikir, hiç silinmez.

**Agent eğitimi (ileride):** Agent, kullanılacağı harness'ın içinde, experience log'daki kayıtlarla eğitilir: önce teacher'ın doğru çıkan çözümleriyle SFT, sonra on-policy distillation (agent'ın kendi denemeleri, teacher'ın düzeltmesiyle), sonra RL (reward: cevabın doğruluğu, yanında forecast'in tutması). Eğitime yalnızca train split'inin kayıtları girer.

## Tasarım kararları

| Karar | Neden | Dayanak |
|---|---|---|
| Forecast'i agent yapar, gerçek çalıştırma denetler | Agent hatasını sonuca bakmadan önce verdiği tahminle karşılaştırarak görür | ANTE, ECHO |
| Son cevap her zaman gerçekten çalıştırılır | Çalıştırılmamış bir SQL'in doğru olduğu bilinemez | — |
| Candidate generation & selection | Liderlik tablosunun zirvesindeki sistemlerin ortak yöntemi | Agentar-Scale-SQL, SIRIUS-SQL |
| Sonuçlar BIRD'ün resmi kuralıyla karşılaştırılır (result key) | Candidate gruplama ile puanlama aynı ölçüyü kullanır; "aynı sonuç" tek bir yerde tanımlıdır | BIRD |
| `ask_user` tool'u hep açık | Belirsiz soruda tahmin etmek yerine sormak; agent'lar netleştirme sorusunu çok erken bırakıyor | BIRD-Interact, PlanPool |
| Bağlam sınırı aşılırsa tabloları LLM seçer (schema linking), şemayı özetlemez | Model tablo adı seçtiği için olmayan bir sütun uyduramaz | MAC-SQL (Selector) |
| Adım 1 olabildiğince çok bilgi verir (sütun açıklamaları, column profile'ları) | Her search bir tool call harcar. Bilgi baştan gelirse budget denemeye kalır, candidate'ler de aynı bilgiyi alır | DualSQL, HarnessSQL |
| Belirsizlik sinyali candidate ayrışmasıdır (medium note) | Harness'ta LLM yok, belirsizliği kendisi anlayamaz. Ayrışan candidate grupları ölçülebilir bir işarettir; karar agent'ındır | SIRIUS-SQL, PlanPool |
| Teacher agent'ın kaldığı yerden devam eder | Agent'ın bulduğu bilgi boşa gitmez; handoff kayıtları doğrudan eğitim verisi olur | OLIVE, OVCSD |
| Agent harness içinde eğitilir | Harness dışında eğitilen model, harness'ta kullanıldığında 30.4'ten 9.6'ya düşüyor | HarnessSQL |
| Database memory gold kullanmaz | Değerlendirme cevapları sisteme sızmaz | — |
| Sabit eşikler ve yalnızca consensus kuralı | Basit ve açıklanabilir; ayrı bir verifier modeli gerekmez | What Predicts Correctness, SIRIUS-SQL |

## Uygulama sırası

Sistem küçük, numaralı aşamalarla kuruldu; her aşama tek bir parça ekledi ve testle denendi. Liste [KOD_YAPISI.md](KOD_YAPISI.md) "Yazım sırası" bölümünde.

1. **Phase 1, SQLite + BIRD:** temel (veritabanı, puanlama, başlangıç bağlamı), ilk çalışan agent, trial loop (guardrail'ler, `search_values`, forecast), cevabı doğrulama (final check, candidate'ler, confidence gate, medium note), yardım ve hafıza (handoff, `ask_user`, database memory).
2. **Phase 2, Mini-Interact:** bilerek belirsiz bırakılmış sorularda `ask_user`.
3. **Yerel modeller:** Policy ve teacher yerelde çalışır.
4. **Agent eğitimi (ileride):** experience log'la SFT → on-policy distillation → RL.

## Değerlendirme

- **BIRD dev:** 1.534 soru, evidence ile. Doğruluk BIRD'ün resmi kuralıyla ölçülür: cevabın result key'i gold SQL'inkiyle aynıysa doğru.
- **Mini-Interact:** 300 belirsiz soru; `ask_user`'ın asıl testi. Doğru SQL'leri e-postayla istenir; gelene kadar sorular çalışır ama puanlanmaz.
- **Bir test için** 5–10 soru yeter (`--limit 10`). Kıyaslamalar en az 3 seed ile yapılır (0, 1, 2).
- **Ablation'lar:** Bir parçanın katkısı ölçülmek istendiğinde o parçayı kapatan bir flag eklenir; şu an her parça hep açıktır.

Bütün eşikler başlangıç değeridir; ölçülerek ayarlanır.

## Kaynakça

Yalnızca bu tasarımı doğrudan şekillendiren çalışmalar. Tam tarama [ARASTIRMA.md](ARASTIRMA.md) dosyasında.

**Agent forecast**
- ANTE: Anticipate, Then Execute ([2610.15368](https://arxiv.org/abs/2610.15368)): agent'ın çalıştırmadan önce forecast yazması (adım 4).
- ECHO: Terminal Agents Learn World Models for Free ([2605.24517](https://arxiv.org/abs/2605.24517)): gerçek çalıştırmanın forecast'i denetlemesi (adım 6).

**Pre-check ve gate**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): önce ucuz yapısal kontroller (adım 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): gerçek çalıştırma cache'i (adım 5).
- What Predicts Correctness in Text-to-SQL? ([2607.06799](https://arxiv.org/abs/2607.06799)): confidence sinyalleri (adım 8).

**Candidate selection**
- Agentar-Scale-SQL ([2509.24403](https://arxiv.org/abs/2509.24403)): candidate generation & selection (adım 7).
- SIRIUS-SQL ([2606.01246](https://arxiv.org/abs/2606.01246)): candidate'leri sonuca göre gruplama; consensus'un tek başına güçlü bir sinyal olması (adım 7, 8).
- Knowing When to Stop ([2607.03991](https://arxiv.org/abs/2607.03991)): candidate'ler uzlaşınca örneklemeyi erken durdurmak (adım 7).

**Kullanıcıya sorma**
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): `ask` eyleminin maliyeti ve belirsiz sorular (adım 3).
- PlanPool ([2610.02739](https://arxiv.org/abs/2610.02739)): agent'ların netleştirme sorusunu çok erken bırakması (adım 3, 8).

**Harness**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): agent'ın kullanılacağı harness'ın içinde eğitilmesi; tool seti; teacher seçimi (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): guardrail'ler (aynı çağrının tekrarı, format hatası).
- MAC-SQL ([2312.11242](https://arxiv.org/abs/2312.11242)): şema uzunsa soruya gereken tabloları bir LLM'in seçmesi (adım 1).

**Handoff ve memory**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) ve OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): teacher'ın agent'ın kaldığı yerden devam etmesi (adım 10); on-policy distillation.
- Measuring Crystallization in Text-to-SQL ([2608.07213](https://arxiv.org/abs/2608.07213)): düzeltmelerin database memory'ye yazılması (adım 1).

**Değerlendirme**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): ana benchmark, evidence ve resmi sonuç karşılaştırma kuralı.
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): Mini-Interact.
