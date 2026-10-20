# Predict – Gate – Settle (PGS)

**Forecast ile denetlenen agent loop, candidate selection ve handoff ile agentic Text-to-SQL.**

Küçük bir policy agent soruyu tool'larla çözer; soru belirsizse kullanıcıya sorar. Her SQL'i çalıştırmadan önce sonucunu tahmin eder (agent forecast) ve gerçek çalıştırma bu tahmini denetler. World model yalnızca çalıştırma pahalıyken devreye girer. Agent takılırsa iş büyük bir teacher LLM'e devredilir (handoff). Tasarımın dayandığı literatür [ARASTIRMA.md](ARASTIRMA.md), kodun yapısı ve yazım sırası [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

## Akış

**Kısaca:** soru → başlangıç bağlamı (1) → agent döngüsü: ara ya da sor (3), SQL dene (4–7) → `submit` → candidate'ler (8) → confidence gate (9) → final check (10) → cevap. Agent takılırsa teacher devralır (11).

![PGS akışı](PGS_akis_TR.png)

| Renk | Bileşen |
|---|---|
| 🟦 Mavi | Policy agent |
| 🟧 Turuncu | World model |
| 🟩 Yeşil | Harness (LLM yok) |
| 🟥 Kırmızı | Gerçek veritabanı |
| 🩵 Turkuaz | Teacher LLM |
| 🟪 Mor | Harness kararı (gate'ler, final check) |
| ⬜ Kesikli | Offline learning |
| ⚪ Beyaz, yuvarlak | Sistemin dışı: kullanıcının sorusu, `ask_user`'ı cevaplayan kullanıcı ve dönen cevap |

Ok renkleri: **siyah** tool call, **mavi** agent'a dönen observation, **mor** karar sonucu, **turkuaz** handoff, **kesikli** offline learning.

## Terimler

| Terim | Anlamı |
|---|---|
| Policy agent | Soruyu adım adım çözen küçük model |
| Tool call | Agent'ın bir turda yaptığı tek istek (ör. `execute_sql`) |
| Observation | Bir tool call'dan sonra agent'a dönen sonuç |
| Tool-call budget | Bir soruda yapılabilecek en fazla tool call sayısı (10) |
| Trial loop | Agent'ın ara, sor, dene, sonuca bak, düzelt diye döndüğü döngü (adım 2–7) |
| Column profile | Bir sütunun özeti: tipi, NULL oranı, en sık değerleri (az değerli sütunlarda hepsi), sayısalsa min ve max |
| Harness | Agent'ın etrafındaki normal kod: tool'ları çalıştırır, kontrolleri ve gate'leri yönetir. İçinde LLM yok |
| World model | SQL'in sonucunu çalıştırmadan tahmin eden küçük model |
| Placeholder world model | World model eğitilene kadar onun yerine kullanılan, eğitilmemiş bir LLM. Prompt'la world model gibi davranır: aynı biçimde prediction ve confidence verir, sistemin geri kalanı farkı görmez |
| Agent forecast | Agent'ın bir SQL'i çalıştırmadan önce yazdığı sonuç tahmini |
| Prediction | World model'in bir SQL'in sonucu için yaptığı tahmin. Agent forecast'ten ayrıdır: onu agent yazar |
| Pre-check | SQL çalıştırılmadan önce harness'ın yaptığı ucuz kontroller: salt okuma mı, `EXPLAIN` hata veriyor mu, cache'te var mı, world model'e gidilsin mi (adım 5) |
| Cache | Aynı soru içinde daha önce çalışmış SQL'lerin saklanan sonuçları; aynı SQL yeniden çalıştırılmaz |
| Gate | Harness'ın "devam mı, dur mu, başka yola mı?" diye verdiği karar noktası. Prediction gate world model'in tahminine güvenilip güvenilmeyeceğine (adım 6), confidence gate candidate'lerin yeterince uzlaşıp uzlaşmadığına (adım 9) karar verir |
| Final check | Cevap dönmeden önceki son kontrol: gerçekten çalıştı mı, hata yok mu, boşsa bu bekleniyor muydu (adım 10) |
| Candidate | Aynı soruya yazılmış alternatif SQL |
| Consensus | Farklı candidate'lerin aynı sonucu vermesi |
| Adaptive rule | Candidate sayısını duruma göre seçen kural: önce 2 ek candidate, uzlaşma yoksa toplam 8 (adım 8) |
| Handoff | İşin büyük teacher modele bırakılması |
| Evidence | BIRD'ün her soruyla birlikte verdiği kısa ipucu metni (ör. "iade edilen = `status = 'returned'`"). BIRD'de standart değerlendirme bununla yapılır |
| `ask_user` | Agent'ın belirsiz bir soruda kullanıcıya kısa bir netleştirme sorusu sorduğu tool (ör. "adet mi, tutar mı?") |
| Clarification | Kullanıcının `ask_user` sorusuna verdiği cevap. Sorunun bir parçası sayılır |
| User simulator | Değerlendirmede gerçek kullanıcının yerine `ask_user` sorularını cevaplayan model. Doğru SQL'i görür ama SQL'i ya da cevabı söylemez, yalnızca soruyu netleştirir |
| Search notes | Search sonuçlarının, candidate prompt'u için ayrıca saklanan kopyası |
| Surprise note | Forecast tutmayınca gerçek sonuçla birlikte agent'a dönen kısa not (ör. "dolu bekliyordun, boş geldi") |
| Medium note | Confidence gate medium çıkınca agent'a dönen not: en kalabalık iki candidate grubunun özeti |
| Database memory | Bir veritabanında daha önce yapılmış ve doğrulanmış düzeltmelerin kaydı. Adım 1'de bağlama eklenir; örnek adım 1'de |
| Result key | Bir sorgu sonucunu karşılaştırmak için kullanılan anahtar. Sonucun bütün satırları küme olarak alınır: satır sırası ve tekrar eden satırlar önemsiz, sütun sırası önemli (BIRD'ün resmi kuralı). Anahtarı aynı olan iki sonuç "aynı sonuç" sayılır |
| Fallback answer | Hiçbir cevap kontrollerden geçmediğinde dönen en iyi cevap; `low_confidence` etiketi taşır |
| Label | Dönen cevabın etiketi: `ok` (kontrollerden geçti), `low_confidence` (geçmedi ama bir cevap var), `no_answer` (çalışan hiçbir SQL yok) |
| Experience log | Her çalıştırmanın, tahminin ve sonucun yazıldığı kayıt; eğitim verisi buradan çıkar |
| Guardrail | Harness'ın agent'ı koruyan kuralları: aynı çağrının tekrarı yok, uzun sonuç kırpılır, bağlam dolarsa sıkıştırılır |
| Split | Verinin bölümü: train (eğitim) ya da dev/test (değerlendirme). Eğitime yalnızca train girer |
| LoRA | Büyük bir modelin tamamını değil, küçük bir ek katmanını eğitme yöntemi |
| SFT | Modeli doğru örnekleri taklit ettirerek eğitmek |
| On-policy distillation | Öğrenci modelin kendi denemelerini teacher'ın düzeltmesiyle eğitmek |
| RL | Modeli denemelerinin sonucuna göre reward ve ceza vererek eğitmek |
| EXPLAIN | Veritabanının sorguyu çalıştırmadan "bunu nasıl çalıştırırım, ne kadar tarama yaparım" planını göstermesi. SQLite'ta sözdizimi ve eksik tablo/sütun hatalarını da çalıştırmadan yakalar |
| Calibration | Bir confidence score'un gerçekle uyumlu olması: "%90 eminim" dendiğinde %90 doğru çıkması |
| Audit | Güvenilen prediction'ların küçük bir kısmını yine de çalıştırıp kontrol etmek |
| Cost simulation | SQLite'ta sorgular ucuz olduğu için bazı sorguları pahalıymış gibi saymak; pahalı sorgu yolunu (adım 6) SQLite'ta denemeyi sağlar |
| Bird-coin | Mini-Interact'in maliyet birimi: her çalıştırma, soru ve cevap gönderme bird-coin harcar ve her görevin bir bird-coin budget'ı vardır |
| Baseline | Karşılaştırma için ölçülen en basit sistem (ör. aşama 5'teki tool'suz tek SQL) |
| Ablation | Sistemden tek bir parçayı kapatıp (flag ile) sonucu tam sistemle karşılaştırmak; o parçanın katkısını gösterir |
| Promotion gate | Yeniden eğitilen policy'nin, eskisinden kötü olmadığı test edilmeden kullanıma alınmaması |
| Phase / aşama | Phase: üç büyük dönemden biri (veritabanı ortamına göre). Aşama: tek bir parça ekleyen, numaralı küçük iş (KOD_YAPISI.md "Yazım sırası"). Eğitim ayrı ve isteğe bağlı bir bölümdür, phase'lerden sonra gelir |
| Imagination loop (Dyna) | Modelin bazı adımları gerçek veritabanı yerine world model'in tahminiyle denemesi |
| Seed | Rastgeleliği sabitleyen sayı; farklı seed'lerle tekrar denemek, sonucun şans olmadığını gösterir |
| Live fork | Handoff'u değerlendirirken eski kaydı tekrar oynatmak (replay) yerine sistemi o noktadan gerçekten yeniden çalıştırmak |

## Bileşenler

- **Policy agent (Qwen3.5-4B):** Her adımda hangi tool'u çağıracağına karar verir. SQL çalıştırmadan önce sonucu tahmin eder. Eğitilmemiş hâliyle kullanılır. Eğitimi (harness içinde SFT → on-policy distillation → RL) isteğe bağlıdır ve sistem uçtan uca çalıştıktan sonra yapılır.
- **World model (ilk sürümde placeholder LLM; eğitim yapılırsa Qwen3.5-0.8B + LoRA):** SQL'in sonucunu çalıştırmadan üç düzeyde tahmin eder ve her biri için bir confidence score verir:
  - **Result type:** sorgu hata mı verecek, boş mu dönecek, yoksa satır mı döndürecek?
  - **Result shape:** hangi sütunlar gelecek, yaklaşık kaç satır gelecek?
  - **Values:** dönecek gerçek değerler (yalnızca küçük sonuçlarda).

  İlk sürümde placeholder'dır: eğitilmemiş bir LLM, prompt'la world model gibi davranır. Eğitim yapılırsa yerini gerçek çalıştırma kayıtlarıyla eğitilen küçük model alır; sistemin geri kalanı değişmez.
- **Harness (düz Python, LLM yok):** Tool'ları çalıştırır, kontrolleri yapar, gate'leri yönetir, experience log'u tutar. Guardrail'leri de o uygular.
- **Veritabanı (SQLite, salt okunur):** `execute_sql`.
- **Kullanıcı:** `ask_user` sorularını cevaplar. `run.py`'de terminaldeki kişidir. Değerlendirmede user simulator'dür: teacher modeli, doğru SQL'i görerek kullanıcı gibi cevap verir (BIRD-Interact'teki gibi). Doğru SQL'i yalnızca simulator görür; agent'ın bağlamına hiç girmez. Mini-Interact'te benchmark'ın kendi simülatörü kullanılır; onun LLM'i de yerelde teacher modelidir.
- **Teacher LLM (Qwen3.6-27B, 4-bit):** Yalnızca handoff'tan sonra devreye girer. Agent'ın kaldığı yerden devam eder. 4-bit hâliyle ~16–17 GB yer kaplar; policy ve world model ile birlikte 48 GB'a sığması beklenir (aşama 35'te ölçülür).

## Akış adım adım

Görseldeki numaralar bu adımlardır. İş bölümü basit:
- **Agent** ne yapılacağına karar verir: hangi tool, hangi SQL, forecast, kullanıcıya ne sorulacağı, ne zaman `submit` ya da `handoff`.
- **Harness** geri kalan her şeye karar verir: kontroller, world model'e gidilip gidilmeyeceği, candidate'ler, gate'ler, final check.

Tool argümanları ve sayısal sınırlar [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

### 1. Başlangıç bağlamı

**Neden:** Her search bir tool call harcar. Bilgi baştan verilirse budget denemeye kalır.

Harness agent'a şunları verir:
- Soru ve varsa evidence.
- Şema: tablolar, sütunlar, BIRD'ün sütun açıklamaları, foreign key'ler.
- Column profile'ları. En fazla 30 farklı değeri olan sütunlarda (ör. `status`) bütün değerler.
- Sorudaki kelimelerin değer eşleşmeleri: harness `search_values`'ı kendisi çalıştırır. Örnek: "Los Angles" → `city = 'Los Angeles'`.
- Database memory: bu veritabanında daha önce yapılmış hatalar ve düzeltmeleri (en fazla 3 kayıt).

Bağlam en fazla 16K token olur (bağlamın yarısı); taşarsa soruyla eşleşmeyen tabloların ayrıntıları kısaltılır.

Database memory örneği: önceki bir soruda agent `status = 'iade'` yazdı, sonuç boş geldi, sonra `'returned'` ile düzeltti. Bu hata ve düzeltmesi kaydedilir; yeni bir iade sorusunda agent bunu baştan görür. Kayıt yalnızca cevap kontrollerden geçtiyse yazılır; gold SQL kullanılmaz.
→ 2

### 2. Agent ne yapacağına karar verir

Agent her turda tek bir tool call yapar:
- Bilgi eksikse → `search_schema` / `search_values` → 3
- Soru belirsizse ve şema, değerler ya da evidence bunu çözmüyorsa → `ask_user` → 3
- Bir SQL'i denemek istiyorsa → `execute_sql` → 4
- Cevaptan eminse → `submit` → 8
- Takıldıysa → `handoff` → 11

Her observation'dan sonra agent buraya döner. Her tool call budget'tan bir düşer (en fazla 10). Reddedilen istekler ve tool call olarak okunamayan çıktılar da sayılır; hata agent'a döner. Budget biterse harness handoff'u zorlar → 11.

**Guardrail'ler.** Küçük modeller bazı tipik hataları sık yapar; bunlar sistemi bozmasın diye harness her adımda üç basit kural uygular. Bunlar olmadan agent'ın eğitimi bile çöküyor (DualSQL).
1. **Tekrar yok:** Model bazen aynı SQL'i tekrar tekrar gönderip döngüye girer. Aynı çağrı (aynı tool, aynı argümanlar) ikinci kez gelirse çalıştırılmaz; "bunu zaten denedin" notu ve önceki sonuç döner, budget yine düşer. `execute_sql`'de yalnızca SQL'e bakılır, forecast farklı olsa da tekrar sayılır. `submit` hariç: medium note'tan sonra aynı SQL'i yeniden göndermek geçerli bir seçimdir.
2. **Uzun sonuç kırpılır:** 50.000 satırın hepsi verilse bağlam dolar. Agent en fazla 20 satır görür, yanında "toplam 50.000 satır" yazar.
3. **Bağlam sıkıştırılır:** Konuşma 32K token'ı aşarsa en eski sonuçlar tek satırlık özete iner (ör. "3 sütun, 120 satır").

### 3. Bilgi toplama: search ve `ask_user`

Agent bunları istediği an kullanır. Adım 1 zengin olduğu için çoğu soruda az gerekir.
- **`search_schema`:** Soruyla ilgili tablo ve sütunları bulur; adlarda ve sütun açıklamalarında arar. Örnek: "kategori" → `categories` tablosu.
- **`search_values`:** Bir kelimenin veritabanında hangi sütunda, hangi değer olarak geçtiğini bulur; benzer yazılanlar dahil. Örnek: "Los Angles" → `city = 'Los Angeles'`.
- **`ask_user`:** Soruyu yalnızca kullanıcı netleştirebiliyorsa kısa bir soru sorulur. Örnek: "adet mi, tutar mı?" → "adet". Şema, değerler ya da evidence cevabı veriyorsa sorulmaz. Soru başına en fazla 5 kez (agent ve teacher toplam).

Arama her şeyi bulamaz: soruda "iade", veritabanında `'returned'` yazıyorsa eşleşmez. Bu durumda evidence çoğu zaman eşleşmeyi verir; vermezse agent kullanıcıya sorar ya da yanlış değerle boş sonuç alır ve surprise note onu başka bir değer denemeye yönlendirir.

Sonuç observation olarak agent'a döner. Harness ayrıca bir kopyasını saklar: search sonuçlarını **search notes**, kullanıcının cevaplarını **clarification** olarak. İkisi de adım 8'de candidate'lere, adım 11'de teacher'a verilir. Neden kopya? Candidate'ler agent'ın geçmişini görmez; görse agent'ın SQL'ini kopyalar. Kopya sayesinde bulunan bilgiyi (ör. `'returned'`) alırlar, SQL'i almazlar.
→ 2

### 4. `execute_sql` isteği ve forecast

Agent SQL'le birlikte sonucun ne olacağını da tahmin eder (forecast):
- Result type: `error` (hata), `empty` (boş) ya da `rows` (dolu).
- Result shape (yalnızca `rows` ise): sütunlar ve satır aralığı (`0`, `1`, `2-10`, `11-100`, `100+`).
- `trust` ya da `unsure`.

Örnek: `{"type": "rows", "columns": ["category", "n"], "rows": "1", "trust": true}`

Forecast yoksa istek reddedilir (→ 2). `USE_AGENT_FORECAST` kapalıysa forecast istenmez. Bundan sonra sorgunun nereye gideceğine harness karar verir.
→ 5

### 5. Pre-check

**Neden:** Bozuk ya da pahalı bir sorguyu çalıştırmadan, ucuz yoldan yakalamak.

Agent'ın SQL'leri de candidate'ler de buradan geçer. Harness sırayla dört soru sorar:
1. **Yazma mı yapıyor?** `SELECT` ya da `WITH` ile başlamıyorsa reddedilir. Örnek: `DELETE FROM orders`.
2. **Bozuk mu?** `EXPLAIN` sorguyu çalıştırmadan yazım hatasını, olmayan tabloyu ve sütunu yakalar. Örnek: `customers` tablosunda olmayan bir `price` sütunu.
3. **Daha önce çalıştı mı (cache)?** Çalıştıysa yeniden çalıştırılmaz; saklanan sonuç adım 7'deki gibi forecast'le karşılaştırılıp döner. Agent'ın kendi tekrarını zaten guardrail yakalar; cache, aynı SQL'in başka bir yoldan gelmesi içindir. Örnek: bir candidate agent'ın SQL'ini birebir yeniden yazar.
4. **Pahalı mı, ya da budget az mı?** Tahmini taranacak satır 1 milyonu aşıyorsa ya da kalan budget başlangıcın %25'inin altındaysa → 6 (world model). Değilse → 7 (gerçek çalıştırma). SQLite'ta pahalı sorgu az olduğu için çoğu sorgu doğrudan 7'ye gider. `USE_WORLD_MODEL` kapalıysa bu soru sorulmaz.

1–3'te takılan sorgunun notu agent'a döner (→ 2). Sorgu bir candidate ise not agent'a değil adım 8'e döner.

### 6. World model ve prediction gate

**Neden:** Pahalı bir sorgunun sonucunu çalıştırmadan tahmin etmek.

World model'i harness çağırır, agent değil. World model result type, result shape ve values için bir prediction ve her biri için bir confidence score verir. Prediction gate yalnızca type ve shape'in confidence'ına bakar; values yalnızca bilgi olarak agent'a gösterilir.
- İkisi de ≥ 0.9 → trusted: prediction "prediction" etiketiyle agent'a döner → 2. Agent bunu sonraki SQL'i yazarken kullanabilir, cevap olarak kullanamaz.
- Değilse → untrusted → 7.
- **Audit:** Trusted prediction'ların rastgele %5'i yine de 7'de çalıştırılır. Böylece gate'in calibration'ı gerçek sonuçlarla denetlenmeye devam eder.

### 7. Gerçek çalıştırma, compare & log

Sorgu veritabanında salt okunur çalıştırılır (en fazla 30 saniye). Gerçek sonuç agent'ın forecast'iyle (varsa world model'in prediction'ıyla da) karşılaştırılır ve experience log'a yazılır.
- Forecast'in "tuttu" sayılması için result type aynı olmalı; `rows` ise sütun sayısı ve satır aralığı da. Sütun adlarına bakılmaz, çünkü aynı sütun farklı takma adla gelebilir.
- Agent'a gerçek sonuç (kırpılmış hâli) döner. Forecast tutmadıysa yanında bir surprise note gelir. Örnek: "dolu bekliyordun, boş geldi".
→ 2

> Adım 2 → 7 arası agent'ın **trial loop**'udur: ara, sor, dene, sonuca bak, düzelt.

### 8. `submit` → candidate'ler

**Neden:** Bir SQL'in hatasız çalışması doğru olduğunu göstermez. En sağlam sinyal, ayrı ayrı yazılmış SQL'lerin aynı sonucu vermesidir (consensus).

- **Kim yazar:** Agent'ın SQL'i de bir candidate'tir. Diğerlerini aynı policy modeli tool'suz, tek seferde yazar. Prompt'ta soru, evidence, clarification'lar, adım 1 bağlamı ve search notes var. Agent'ın SQL'i prompt'a konmaz; konursa model onu kopyalar. Search ya da trial loop yoktur.
- **Kaç tane (adaptive rule):** Önce 2 ek candidate. Hepsi agent'ın SQL'iyle aynı sonucu verirse durulur. Ayrışırlarsa 5 tane daha üretilir, toplam 8 olur.
- **Nasıl çalışır:** Her candidate agent'ın SQL'leriyle aynı yoldan geçer: 5 → (6) → 7. Daha önce çalışmış SQL cache'ten gelir; agent'ın SQL'i hiç çalışmadıysa şimdi çalıştırılır. World model açıksa ve candidate pahalıysa, "hata verir" ya da "boş döner" diye güvenle tahmin edilen candidate çalıştırılmadan düşer. Candidate'ler budget'tan düşmez, sonuçları agent'a dönmez (tek istisna adım 9'daki medium note).
- **Gruplama:** Result key'i aynı olanlar, yani gerçek sonucu aynı olanlar, bir gruptur. Result key agent'a gösterilen 20 satırdan değil, bütün satırlardan hesaplanır. Hata veren ya da elenen candidate hiçbir gruba girmez.
- **Seçim:** En kalabalık grup seçilir. Başa baş ise agent'ın SQL'inin bulunduğu grup; agent'ın grubu berabere kalanlar arasında değilse en önce üretilmiş candidate'i içeren grup. Grubun cevabı tek bir SQL'dir: içinde agent'ın SQL'i varsa o, yoksa grubun en önce üretilmiş candidate'i.
- **İkinci `submit`:** Agent medium note ya da final check notundan sonra yeniden `submit` ederse candidate'ler baştan üretilir, çünkü search notes ve clarification'lar değişmiş olabilir. Aynı SQL'ler cache'ten gelir.

Ek çalıştırmalar bilinçli bir takastır: birkaç çalıştırma, yanlış cevap göndermekten ya da teacher'a handoff yapmaktan ucuzdur. Takas ölçülür: `USE_CANDIDATES` kapalıysa 8 ve 9 atlanır, agent'ın SQL'i doğrudan 10'a gider.
→ 9

### 9. Confidence gate

Karar yalnızca consensus'a bakar: en kalabalık grupta kaç candidate var? Hata veren ya da elenen candidate sayılmaz.
- **High:** 3/3 ya da 8'in en az 6'sı → 10.
- **Medium:** 8'in 4–5'i → agent'a medium note döner → 2. Not en kalabalık iki grubu gösterir: temsilci SQL, kaç candidate'te olduğu, sütunlar, satır sayısı, ilk 3 satır. Agent birini seçip yeniden `submit` edebilir, yeni bir deneme yapabilir ya da fark sorunun belirsizliğinden geliyorsa `ask_user` ile sorabilir. Bu en fazla bir kez olur; ikinci medium → 11.
- **Low:** 8'in en fazla 3'ü → 11.

### 10. Final check

Cevap dönmeden önceki son kontrol:
- **Gerçekten çalıştırıldı mı?** Çalıştırılmadıysa (ör. teacher'ın cevabı) harness şimdi çalıştırır; böylece dönen her cevap gerçekten çalıştırılmış olur. Hata veren cevap geçmez.
- **Salt okuma mı, tablolar ve sütunlar var mı?**
- **Sonuç boşsa, bu bekleniyor muydu?** Bu SQL için yazılan son forecast "boş" değilse ya da forecast yoksa geçmez. Örneğin seçilen SQL bir candidate ise ya da `USE_AGENT_FORECAST` kapalıysa forecast yoktur.

Geçti → **cevap döner ✔** (label `ok`). Geçmedi → nedeni agent'a not olarak döner → 2. İkinci kez geçmezse → 11.

### 11. Handoff

Handoff'u agent kendisi isteyebilir (adım 2) ya da harness zorlar: budget bitti, confidence low, ikinci kez medium, final check 2 kez geçmedi.
- Teacher sıfırdan başlamaz, agent'ın kaldığı yerden devam eder: soru, evidence, clarification'lar, bütün observation'lar, varsa medium note ve handoff'un nedeni.
- Yeni bir budget'la (10 tool call) ve aynı tool'larla çalışır (adım 2–7). `handoff` tool'u teacher'a sunulmaz; `ask_user` için yalnızca sorunun kalan hakkını kullanır.
- Teacher'ın `submit`'i candidate'lere gitmez, doğrudan final check'e gider. Geçerse `ok`; geçmezse tekrar denenmez, SQL `low_confidence` ile döner. Teacher budget'ı içinde `submit` etmezse fallback answer döner.

**Fallback answer** sırası: en son seçilen cevap (adım 8'in seçtiği SQL; adım 8 kapalıysa agent'ın `submit` ettiği SQL; teacher'ın `submit` ettiği SQL) → yoksa en son hatasız çalışan SQL (agent'ın ya da teacher'ın) → yoksa cevap yok. İlk ikisi `low_confidence`, sonuncusu `no_answer` etiketiyle döner. `USE_HANDOFF` kapalıysa teacher yerine hep fallback answer döner ve agent'a `handoff` tool'u sunulmaz.
→ Cevap ✔

**Dönen cevap:** SQL, sonucu, label (`ok`, `low_confidence`, `no_answer`) ve cevabı kimin bulduğu (agent ya da teacher).

### İki örnek

**Örnek 1 ("2025'te en çok iade edilen kategori hangisi?", SQLite):**
1 (evidence: iade = `status = 'returned'`; şemada `categories` tablosu var, adım 3'e gerek kalmaz) → 2 → 4 (SQL + forecast: "dolu, 1 satır") → 5 (ucuz) → 7 (gerçek sonuç, forecast tuttu) → 2 → 8 → 9 (high: 3/3) → 10 → ✔

**Örnek 2 (aynı soru, candidate'ler ayrışırsa):**
1 → 2 → 4 → 5 → 7 → 2 → 8 → 9 (medium: 8 candidate'in 5'i adet sayıyor, 3'ü tutarı topluyor; medium note iki grubu gösterir) → 2 → 3 (`ask_user`: "adet mi, tutar mı?" → "adet") → 2 → 8 (clarification artık prompt'ta) → 9 (high: 7/8) → 10 → ✔

### Soru bittikten sonra (offline learning)

Experience log üç yere akar:
- **Database memory:** Soru `ok` ile bittiyse ve yolda bir hata ya da surprise note olduysa hemen bir kayıt yazılır: soru, ilk hatalı SQL, aldığı not, cevap SQL'i. Gold kullanmadığı için değerlendirme sırasında da yazılır. Tekrar üretilebilir olması için her çalıştırmada boş başlar ve sorular veri setindeki sırayla çalıştırılır. `USE_DB_MEMORY` kapalıysa memory ne okunur ne yazılır.
- **World model:** Gerçek çalıştırmalarla yeniden eğitilir ve gate'ler yeniden kalibre edilir.
- **Policy:** Handoff vakalarıyla yeniden distile edilir (re-distillation). Yeni policy, eskisinden kötü olmadığı test edilmeden kullanıma alınmaz (promotion gate).

Son ikisi eğitimdir: isteğe bağlıdır ve sistem uçtan uca çalıştıktan sonra yapılır; o zamana kadar experience log yalnızca birikir. Eğitime ve calibration'a yalnızca train split'inden gelen kayıtlar girer; dev ve test çalıştırmaları log'a yazılır ama eğitimde kullanılmaz.

## Tasarım kararları

| Karar | Neden | Dayanak |
|---|---|---|
| Forecast'i agent yapar, gerçek çalıştırma denetler | Her adım için ayrı bir eğitim sinyali verir | ANTE, ECHO |
| World model'e gitme kararını harness verir | Agent'lar world model tool'unu ya hiç kullanmıyor ya da yanlış kullanıyor | World-model-as-tool (ACL'26) |
| World model'e yalnızca pahalı sorguda gidilir | SQLite'ta çalıştırma ucuz ve kesin; küçük modellerin confidence'ı yeni şemalarda kalibre kalmıyor | DSWorld, BAP-SQL |
| Son cevap her zaman gerçekten çalıştırılır | Prediction cevap ya da reward olursa policy onu istismar eder | Imperfect WMs are Exploitable |
| Candidate generation & selection | Liderlik tablosunun zirvesindeki sistemlerin ortak yöntemi | Agentar-Scale-SQL, SIRIUS-SQL |
| Sonuçlar BIRD'ün resmi kuralıyla karşılaştırılır (result key) | Candidate gruplama ile puanlama aynı ölçüyü kullanır; "aynı sonuç" tek bir yerde tanımlıdır | BIRD |
| `ask_user` tool'u hep açık | Belirsiz soruda tahmin etmek yerine sormak; agent'lar netleştirme sorusunu çok erken bırakıyor. User simulator doğru SQL'i gördüğü için literatürle karşılaştırmada `ask_user` kapalı sonuç da raporlanır | BIRD-Interact, PlanPool |
| Adım 1 olabildiğince çok bilgi verir (değer eşleşmeleri, sütun açıklamaları) | Her search bir tool call harcar. Bilgi baştan gelirse budget denemeye kalır, candidate'ler de aynı bilgiyi alır | DualSQL, HarnessSQL |
| Belirsizlik sinyali candidate ayrışmasıdır (medium note) | Harness'ta LLM yok, belirsizliği kendisi anlayamaz. Ayrışan candidate grupları ölçülebilir bir işarettir; karar agent'ındır | SIRIUS-SQL, PlanPool |
| Agent harness içinde eğitilir | Harness dışında eğitilen model, harness'ta kullanıldığında 30.4'ten 9.6'ya düşüyor | HarnessSQL |
| Teacher agent'ın kaldığı yerden devam eder | Handoff kayıtları doğrudan eğitim verisi olur | OLIVE, OVCSD |
| Database memory gold kullanmaz; eğitim yalnızca train verisiyle yapılır | Değerlendirme cevapları sisteme sızmaz | — |
| İlk sürümde sabit eşikler ve yalnızca consensus kuralı kullanılır | Basit ve açıklanabilir. Öğrenilmiş birleştirici, sertifikalı eşik ve ayrı verifier modeli gerekmez; ileride eklenebilir | What Predicts Correctness, SIRIUS-SQL |
| Policy, Phase 1'de world model'in hayalinde eğitilmez (imagination loop yok) | SQLite'ta gerçek çalıştırma ucuz ve kesin. Hayali rollout'larda hata birikir ve policy world model'i istismar eder. Dyna tarzı sınırlı bir imagination loop, eğitim yapılırsa eklenir: tek adımlı hayal, reward her zaman gerçek çalıştırmadan | Qwen-AgentWorld, Imperfect WMs are Exploitable |
| World model ilk sürümde placeholder'dır (prompt'lanan eğitilmemiş LLM); eğitim isteğe bağlı ve en sondadır | Akışın bütün adımları eğitim beklemeden uçtan uca kurulup ölçülür. World model'in arayüzü (prediction + confidence) baştan sabittir; eğitilmiş model gelirse yalnızca bu bileşen değişir | — |
| Sistem küçük aşamalarla kurulur | Her aşama tek bir parça ekler ve ölçülür; bir parçanın katkısı ayrıca görünür ve hata nerede çıktıysa orada yakalanır | — |

## Uygulama sırası

Üç phase var, ardından yerel modellere geçiş ve isteğe bağlı eğitim gelir. Her biri küçük, numaralı aşamalara bölünür (toplam 43). Her aşama tek bir parça ekler, çalışan bir sistem bırakır ve küçük bir testle denenir. Aşamaların tam listesi, dosyaları ve deneme yolları [KOD_YAPISI.md](KOD_YAPISI.md) "Yazım sırası" bölümünde.

Geliştirme boyunca modeller bir API'den gelir: policy, teacher ve user simulator gerçek LLM'lerdir; world model ise placeholder'dır (prompt'la world model gibi davranan eğitilmemiş bir LLM). Sistem uçtan uca çalışınca yerel modellere geçilir ve makale rakamları onlarla alınır. Eğitim en sona kalır ve isteğe bağlıdır; yapılmazsa world model placeholder olarak kalır ve makalede böyle anlatılır.

1. **Phase 1, SQLite + BIRD:** Agent, harness, gate'ler ve placeholder world model kurulur. Cost simulation kapalıdır; adım 6 yalnızca gerçekten pahalı sorgularda ya da budget azken çalışır.
   - **A. Temel, model yok (aşama 1–3):** veritabanı katmanı, BIRD verisi ve puanlama, başlangıç bağlamı.
   - **B. Agent parça parça.** Her tool ve her guardrail ayrı bir aşamada eklenir; her parça bir öncekinin üzerine gelir ve tek başına ölçülür:
     - B1, ilk çalışan agent (4–8): model, tool'suz tek SQL, yalnızca `submit` ile loop iskeleti, `execute_sql`, pre-check.
     - B2, trial loop'u güçlendirme (9–16): üç guardrail ayrı ayrı (tekrar ve cache, kırpma, sıkıştırma), `search_values`, `search_schema`, adım 1'de değer eşleşmesi, forecast, experience log.
     - B3, cevabı doğrulama (17–21): final check, candidate'ler, adaptive rule, confidence gate, medium note.
     - B4, yardım ve hafıza (22–25): handoff, `ask_user` (terminal), user simulator, database memory.
     - B5, world model (26–28): placeholder world model ve ölçümü, prediction gate ve audit, world model ile candidate eleme.
     - B6, Phase 1 sonuçları (29): tam BIRD dev ve ablation'lar (API modelleriyle; ilerlemeyi ve ablation'ların yönünü gösterir).
2. **Phase 2, aynı ortamda cost simulation (aşama 30–33):** Sırayla Mini-Interact ve user simulator'ü, cost simulation ve eşiklerin ölçülerek ayarlanması.
3. **Phase 3, gerçekten yavaş veritabanı (aşama 34):** Önce DuckDB adapter'ı (TPC-DS) ya da büyütülmüş BIRD veritabanları, sonra gerçek gecikme ölçümü.
4. **Yerel modellere geçiş (aşama 35):** Policy, teacher ve world model yerelde çalışır; modellerin birlikte belleğe sığdığı ölçülür. Makale rakamları burada alınır.
5. **Eğitim, isteğe bağlı (aşama 36–43):** World model eğitimi (veri toplama, eğitim ve calibration; placeholder'ın yerini alır), policy eğitimi (teacher izleri → SFT → on-policy distillation → RL), Dyna tarzı imagination loop ve promotion gate. Zaman kalırsa yapılır; yapılırsa rakamlar yeniden alınır.

Her phase'de tek bir veritabanı vardır. "Ucuz / pahalı" iki ayrı veritabanı değil, harness'ın her sorgu için verdiği karardır (adım 5).

Geçişleri ucuz tutmak için baştan uyulacak kurallar:
- Veritabanı işleri tek bir adapter arayüzünün arkasında durur: `execute`, `explain`, `estimate_cost`, `schema`, `profile`. Yeni motora geçişte yalnızca yeni bir adapter yazılır.
- Cost model takılabilir olur: simüle edilmiş ya da gerçek.
- Experience log'a motor ve dialect bilgisi de yazılır.
- Yeni dialect'e geçerken eğitim verisi SQLGlot ile çevrilir.

Uygulama ayrıntıları (hiperparametreler, reward'lar, veri setleri) [ARASTIRMA.md](ARASTIRMA.md)'nin 8. ve 9. bölümlerinde.

## Değerlendirme

- **BIRD dev (ana sonuç):** Orijinal 1.534 soru, evidence ile, tam sistem (`ask_user` açık, user simulator cevaplar). Diğer sistemler soru sormadığı için `ask_user` kapalı sonuç da raporlanır. Doğruluk ile çalıştırma sayısının Pareto eğrisi. Doğruluk, BIRD'ün resmi kuralıyla ölçülür: cevabın result key'i gold SQL'inkiyle aynıysa doğru. Daha temiz dev bölümü (`bird_sql_dev_20251106`) ek sonuç olarak raporlanır.
- **Aşama kontrolleri:** Her bölümün (B1–B5) son aşamasından sonra BIRD dev'den sabit 50 soruluk bir alt kümede hızlı ölçüm yapılır. Bu rakamlar yalnızca ilerlemeyi görmek içindir; makaleye girmez.
- **Mini-Interact:** World model'in ve `ask_user`'ın asıl testi, çünkü burada her çalıştırmanın ve her sorunun bir maliyeti var. `ask_user`'ı benchmark'ın kendi user simulator'ü cevaplar; onun LLM'i yerelde teacher modelidir. Bu yüzden rakamlar resmi tabloyla birebir karşılaştırılamaz; makalede bu belirtilir.
- **BIRD-Critic-SQLite ve Spider 2.0-Lite (SQLite):** onarım becerisi ve genelleme.
- **Ablation'lar:** Her flag tek tek kapatılarak tam sistemle karşılaştırılır (flag'ler KOD_YAPISI.md'de).
- Her karşılaştırma en az 3 seed ile yapılır (0, 1, 2). Handoff, replay ile değil live fork ile değerlendirilir.
- **Hedef:** BIRD dev 66–71 (benzer sistemlerden çıkarım, ölçüm değil).

Bütün eşikler başlangıç değeridir; Phase 2'de ölçülerek ayarlanır.

## Kaynakça

Yalnızca bu tasarımı doğrudan şekillendiren çalışmalar. Tam tarama [ARASTIRMA.md](ARASTIRMA.md) dosyasında.

**Agent forecast ve world model'in rolü**
- ANTE: Anticipate, Then Execute ([2610.15368](https://arxiv.org/abs/2610.15368)): agent'ın çalıştırmadan önce forecast yazması ve forecast reward (adım 4).
- ECHO: Terminal Agents Learn World Models for Free ([2605.24517](https://arxiv.org/abs/2605.24517)): gerçek çalıştırmanın forecast'i denetleyip eğitim sinyali üretmesi (adım 7).
- DSWorld ([2607.15901](https://arxiv.org/abs/2607.15901)): simülatöre yalnızca pahalı adımlarda gidilmesi (adım 5–6).
- BAP-SQL ([2608.02876](https://arxiv.org/abs/2608.02876)): çalıştırma öncesi maliyet tahmini ve budget (adım 5).
- Current Agents Fail to Leverage World Model as Tool for Foresight ([ACL 2026](https://aclanthology.org/2026.acl-long.623/)): world model'e gitme kararının agent'a bırakılmaması (adım 5).
- Imperfect World Models are Exploitable ([2605.15960](https://arxiv.org/abs/2605.15960)): prediction'ın son cevap ya da reward olmaması (adım 6, 10).

**Pre-check ve gate'ler**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): önce ucuz yapısal kontroller, sonra öğrenilmiş tahmin (adım 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): gerçek çalıştırma cache'i (adım 5).
- What Predicts Correctness in Text-to-SQL? ([2607.06799](https://arxiv.org/abs/2607.06799)): confidence sinyalleri; eşiklerin görülmemiş veritabanlarında seçilmesi (adım 6, 9).

**Candidate selection**
- Agentar-Scale-SQL ([2509.24403](https://arxiv.org/abs/2509.24403)): candidate generation & selection (adım 8).
- SIRIUS-SQL ([2606.01246](https://arxiv.org/abs/2606.01246)): candidate'leri sonuca göre gruplama; consensus'un tek başına güçlü bir sinyal olması (adım 8, 9).
- Knowing When to Stop ([2607.03991](https://arxiv.org/abs/2607.03991)): candidate'ler uzlaşınca örneklemeyi erken durdurmak (adım 8).

**Kullanıcıya sorma**
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): `ask` eyleminin maliyeti ve user simulator (adım 3).
- PlanPool ([2610.02739](https://arxiv.org/abs/2610.02739)): agent'ların netleştirme sorusunu çok erken bırakması (adım 3, 9).

**Harness ve eğitim**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): agent'ın kullanılacağı harness'ın içinde eğitilmesi; tool seti; teacher seçimi (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): rollout guardrail'leri (aynı çağrının tekrarı, format hatası).

**Handoff ve offline learning**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) ve OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): teacher'ın agent'ın kaldığı yerden devam etmesi (adım 11).
- Measuring Crystallization in Text-to-SQL ([2608.07213](https://arxiv.org/abs/2608.07213)): doğrulanmış düzeltmelerin database memory'ye yazılması (adım 1).
- BCIT ([2608.26730](https://arxiv.org/abs/2608.26730)): yeniden eğitilen policy için promotion gate.
- Qwen-AgentWorld ([2606.24597](https://arxiv.org/abs/2606.24597)): simülasyonla RL'in ancak gerçek çapayla işe yaraması (imagination loop kararı).

**Değerlendirme**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): ana benchmark, evidence ve resmi sonuç karşılaştırma kuralı.
- BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)): çalıştırma maliyetli benchmark (Mini-Interact).
- OmniSQL / SynSQL-2.5M ([2503.02240](https://arxiv.org/abs/2503.02240)): world model eğitimi için sentetik SQL verisi.
