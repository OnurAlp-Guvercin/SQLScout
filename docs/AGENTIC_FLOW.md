# Predict – Gate – Settle (PGS)

**Agent loop, final check ve handoff ile agentic Text-to-SQL.**

Küçük bir policy agent soruyu tool'larla çözer: değer arar, SQL dener, sonuca bakar, düzeltir. Agent cevap olarak seçtiği SQL'i `submit` eder; cevap bir final check'ten geçer ve dönen her cevap gerçekten çalıştırılmıştır. Agent ilerleyemez ya da takılırsa iş büyük bir teacher LLM'e devredilir (handoff). Tasarımın dayandığı literatür [ARASTIRMA.md](ARASTIRMA.md), kodun yapısı [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

## Akış

**Kısaca:** soru → başlangıç bağlamı (1) → agent döngüsü: değer ara (3), SQL dene (4–6) → `submit` → final check (7) → cevap. Agent takılırsa teacher devralır (8).

![PGS akışı](PGS_akis_TR.png)

| Renk | Bileşen |
|---|---|
| 🟦 Mavi | Policy agent |
| 🟩 Yeşil | Harness (LLM yok) |
| 🟥 Kırmızı | Gerçek veritabanı |
| 🩵 Turkuaz | Teacher LLM |
| 🟪 Mor | Harness kararı (final check) |
| ⬜ Kesikli | Soru bittikten sonra: experience log, agent eğitimi (ileride) |
| ⚪ Beyaz, yuvarlak | Sistemin dışı: kullanıcının sorusu ve dönen cevap |

Ok renkleri: **siyah** tool call, **mavi** agent'a dönen observation, **mor** karar sonucu, **turkuaz** handoff, **kesikli** soru bittikten sonra.

## Terimler

| Terim | Anlamı |
|---|---|
| Policy agent | Soruyu adım adım çözen küçük model |
| Tool call | Agent'ın bir turda yaptığı tek istek (ör. `execute_sql`) |
| Observation | Bir tool call'dan sonra agent'a dönen sonuç |
| Tool-call budget | Bir soruda yapılabilecek en fazla tool call sayısı (10) |
| Trial loop | Agent'ın ara, dene, sonuca bak, düzelt diye döndüğü döngü (adım 2–6) |
| Column profile | Bir sütunun özeti: tipi, NULL oranı, en sık değerleri (az değerli sütunlarda hepsi), sayısalsa min ve max |
| Harness | Agent'ın etrafındaki normal kod: tool'ları çalıştırır, kontrolleri ve handoff'u yönetir. İçinde LLM yok |
| Pre-check | SQL çalıştırılmadan önce harness'ın yaptığı ucuz kontroller: salt okuma mı, `EXPLAIN` hata veriyor mu, cache'te var mı (adım 5) |
| Cache | Aynı soru içinde daha önce çalışmış SQL'lerin saklanan sonuçları; aynı SQL yeniden çalıştırılmaz |
| Final check | Cevap dönmeden önceki son kontrol: submit edilen SQL hatasız çalışıyor mu, agent sonucunu görmüş mü (adım 7) |
| Handoff | İşin büyük teacher modele bırakılması |
| Evidence | BIRD'ün her soruyla birlikte verdiği kısa ipucu metni (ör. "iade edilen = `status = 'returned'`") |
| Result key | Bir sorgu sonucunu karşılaştırmak için kullanılan anahtar. Sonucun bütün satırları küme olarak alınır: satır sırası ve tekrar eden satırlar önemsiz, sütun sırası önemli (BIRD'ün resmi kuralı). Cevap, result key'i doğru SQL'inkiyle aynıysa doğrudur |
| Fallback answer | Hiçbir cevap final check'ten geçmediğinde dönen cevap: en son hatasız ve dolu çalışan SQL; `fallback` etiketi taşır |
| Label | Dönen cevabın etiketi: `ok` (final check'ten geçti), `fallback` (geçmedi ama çalışan bir SQL var), `no_answer` (dolu sonuç veren hiçbir SQL yok) |
| Base | Karşılaştırma için tool'suz tek SQL: model adım 1'in bağlamını görür ve tek seferde bir SQL yazar (`baseline.py`) |
| Experience log | Her sorunun bütün konuşmasının (agent'ın ve teacher'ın her adımı), cevabın ve cevap doğru mu bilgisinin kaydı; agent'ın eğitim verisi buradan çıkar |
| Split | Verinin bölümü: train (eğitim) ya da dev (değerlendirme). Eğitime yalnızca train girer |
| SFT | Modeli doğru örnekleri taklit ettirerek eğitmek |
| On-policy distillation | Öğrenci modelin kendi denemelerini teacher'ın düzeltmesiyle eğitmek |
| RL | Modeli denemelerinin sonucuna göre reward ve ceza vererek eğitmek |
| Guardrail | Harness'ın agent'ı koruyan kuralları: aynı çağrının tekrarı yok, uzun sonuç kırpılır, bağlam dolarsa sıkıştırılır |
| Temperature | Modelin cevabındaki rastgelelik: 0'da hep en olası cevap, büyüdükçe daha çeşitli |
| EXPLAIN | Veritabanının sorguyu çalıştırmadan planını göstermesi. SQLite'ta sözdizimi ve eksik tablo/sütun hatalarını da çalıştırmadan yakalar |
| Seed | Rastgeleliği sabitleyen sayı; farklı seed'lerle tekrar denemek, sonucun şans olmadığını gösterir |
| Aşama | Tek bir parça ekleyen, numaralı küçük iş (KOD_YAPISI.md "Yazım sırası") |

## Bileşenler

- **Policy agent:** Her adımda hangi tool'u çağıracağına karar verir. Şu an yerel `Qwen3.5-0.8B`; hedef `Qwen3.5-4B`. Şimdilik eğitilmemiş hâliyle kullanılır; ileride experience log'la harness'ın içinde eğitilir.
- **Harness (düz Python, LLM yok):** Tool'ları çalıştırır, kontrolleri ve final check'i yapar, handoff'a karar verir. Guardrail'leri de o uygular.
- **Veritabanı (SQLite, salt okunur):** `execute_sql`. Doğru SQL agent'ın bağlamına hiç girmez, yalnızca puanlamada kullanılır.
- **Teacher LLM:** Yalnızca handoff'tan sonra devreye girer, agent'ın kaldığı yerden devam eder. Şu an OpenRouter API'sindeki `Qwen3.5-9B`; hedef yerel `Qwen3.6-27B` (4-bit).

## Akış adım adım

Görseldeki numaralar bu adımlardır. İş bölümü basit:
- **Agent** ne yapılacağına karar verir: hangi tool, hangi SQL, ne zaman `submit`.
- **Harness** geri kalan her şeye karar verir: kontroller, final check, handoff.

Tool argümanları ve sayısal sınırlar [KOD_YAPISI.md](KOD_YAPISI.md) dosyasında.

### 1. Başlangıç bağlamı

**Neden:** Her search bir tool call harcar. Bilgi baştan verilirse budget denemeye kalır.

Harness agent'a şunları verir:
- Soru ve varsa evidence.
- Şema: tablolar, sütunlar, BIRD'ün sütun açıklamaları, foreign key'ler.
- Column profile'ları. Metin sütunlarında en sık 10 değer (en fazla 10 farklı değeri olan sütunlarda, ör. `status`, bütün değerler); geri kalan değerleri agent gerekirse `search_values` ile bulur. Sayısal sütunlarda yalnızca en küçük ve en büyük değer.

BIRD dev'de bu bağlam en fazla ~12K token; modelin bağlam sınırının çok altında.

→ 2

### 2. Agent ne yapacağına karar verir

Agent her turda tek bir tool call yapar. Prompt ona bir çalışma sırası verir: önce soruyu cevaplayan SQL'i yaz ve çalıştır (keşif sorgusuyla başlama), sonuca bak, gerekirse düzelt, sonuç soruyu cevaplıyorsa `submit` et.
- Soruyu cevaplayan SQL'i denemek istiyorsa → `execute_sql` → 4
- Bir değerin veritabanında nasıl yazıldığını bilmiyorsa → `search_values` → 3
- Çalıştırdığı bir SQL soruyu cevaplıyorsa → o SQL'le `submit` → 7. Arada attığı sorgular (kontrol, düzeltme) cevabı etkilemez

Her observation'dan sonra agent buraya döner. Agent her adımda en olası cevabı seçer (temperature 0). Son çağrısı reddedildiyse ya da bir tekrarsa, aynı girdiye yine aynı cevabı vereceği için sıradaki adım örneklenir (temperature 0.7). Her tool call budget'tan bir düşer (en fazla 10). Reddedilen istekler ve tool call olarak okunamayan çıktılar da sayılır; hata agent'a döner. Her sonucun altında kalan tool call sayısı yazar; son 2 hakta "çalıştırdığın bir sorgu soruyu cevaplıyorsa onu şimdi submit et" hatırlatması da eklenir. Agent ilk 4 tool call'ında dolu sonuç veren hiçbir SQL çalıştıramadıysa ilerlemiyor sayılır ve harness işi hemen teacher'a verir → 8; teacher kısa bir geçmişle başlar, boşa adım ve maliyet harcanmaz. Budget biterse de harness handoff'u zorlar → 8.

**Guardrail'ler.** Küçük modeller bazı tipik hataları sık yapar; bunlar sistemi bozmasın diye harness her adımda üç basit kural uygular (DualSQL).
1. **Tekrar yok:** Aynı çağrı (aynı tool, aynı argümanlar) ikinci kez gelirse çalıştırılmaz; "bunu zaten denedin" notu ve önceki sonuç döner, budget yine düşer. Aynı çağrı 3. kez tekrarlanırsa agent takılmış sayılır ve harness handoff yapar → 8. Yalnızca kendi tekrarları sayılır: teacher'ın agent'ın denediği bir çağrıyı yinelemesi onu takılmış saymaz. `submit` tekrar sayılmaz; onu final check sınırlar (adım 7).
2. **Uzun sonuç kırpılır:** Agent en fazla 20 satır görür, yanında toplam satır sayısı yazar.
3. **Bağlam sıkıştırılır:** Konuşma 32K token'ı aşarsa en eski sonuçlar tek satırlık özete iner (ör. "Columns: name | 358 rows").

### 3. Değer arama: `search_values`

Adım 1 zengin olduğu için çoğu soruda az gerekir. `search_values` bir kelimenin veritabanında hangi sütunda, hangi değer olarak geçtiğini bulur; benzer yazılanlar dahil. Örnek: "Los Angles" → `city = 'Los Angeles'`. Hiçbir değer bulamazsa ve aranan kelime bir sütun adına benziyorsa o sütunları söyler; küçük modeller sütun adlarını da bu tool'la arıyor. Örnek: "Consumption" → `yearmonth.Consumption` sütunu.

Arama her şeyi bulamaz: soruda "iade", veritabanında `'returned'` yazıyorsa eşleşmez. Bu durumda evidence çoğu zaman eşleşmeyi verir; vermezse agent yanlış değerle boş sonuç alır; boş sonucun altındaki not onu değerin yazılışını `search_values` ile kontrol etmeye yönlendirir.
→ 2

### 4. `execute_sql` isteği

Agent denemek istediği SQL'i `execute_sql(sql="SELECT ...")` ile gönderir. SQL'i tool call yerine mesajında bir ` ```sql ` bloğu olarak yazarsa o da aynı şekilde çalıştırılır.
→ 5

### 5. Pre-check

**Neden:** Bozuk bir sorguyu çalıştırmadan, ucuz yoldan yakalamak.

Agent'ın SQL'leri ve final check buradan geçer. Harness sırayla üç soru sorar:
1. **Yazma mı yapıyor?** `SELECT` ya da `WITH` ile başlamıyorsa reddedilir. Örnek: `DELETE FROM orders`.
2. **Bozuk mu?** `EXPLAIN` sorguyu çalıştırmadan yazım hatasını, olmayan tabloyu ve sütunu yakalar. Not, hatayı düzeltmek için gerekeni de söyler: olmayan sütun hangi tablolarda var, alias verilmiş bir tablo kendi adıyla yazıldıysa alias'ı ve sorgudaki tabloların gerçek sütunları; olmayan bir tablo yazıldıysa veritabanındaki tablolar. Örnek: `no such column: cc.client_id` → "client_id şu tablolarda var: client, disp. Sorgudaki tablolar ve sütunları: card (cc): card_id, disp_id, type, issued; ...".
3. **Daha önce çalıştı mı (cache)?** Çalıştıysa yeniden çalıştırılmaz, saklanan sonuç kullanılır. Örnek: agent'ın çalıştırdığı SQL'i final check yeniden çalıştırır.

1–2'de takılan sorgunun notu agent'a döner (→ 2).
→ 6

### 6. Gerçek çalıştırma

Sorgu veritabanında salt okunur çalıştırılır (en fazla 30 saniye). Agent'a gerçek sonuç döner: sütunlar, satır sayısı, en fazla 20 satır ya da hata mesajı. Sonuç boşsa altına "sorgu bir metin değerine göre filtreliyorsa yazılışını `search_values` ile kontrol et" notu eklenir; değerin yanlış yazılması boş sonucun en sık sebebi.
→ 2

> Adım 2 → 6 arası agent'ın **trial loop**'udur: ara, dene, sonuca bak, düzelt.

### 7. `submit` → final check

Agent cevap olarak seçtiği SQL'i `submit(sql="SELECT ...")` ile gönderir; arada attığı sorgular cevabı etkilemez. Cevap dönmeden önce son kontrol:
- **Salt okuma mı, tablolar ve sütunlar var mı, hatasız çalışıyor mu?** (adım 5–6; agent bu SQL'i daha önce çalıştırdıysa sonuç cache'ten gelir). Hata veren cevap geçmez. Boş sonuç geçer.
- **Agent bu SQL'in sonucunu görmüş müydü?** Agent sonucuna bakmadığı bir cevabı gönderemez. Görmediyse harness sorguyu çalıştırır, sonucunu agent'a gösterir ve "soruyu cevaplıyorsa yeniden submit et" der → 2. Bu bir hata sayılmaz. Örnek: agent hiç denemeden `WHERE County = 'Alemeda'` yazdıysa boş sonucu burada görür ve değeri düzeltir. Agent'a en fazla 20 satır gösterildiği için büyük sonuçlar sorun olmaz.

Geçti → **cevap döner ✔** (label `ok`). Final check'ten geçmedi → nedeni agent'a not olarak döner → 2. İkinci kez geçmezse → 8.

### 8. Handoff

Handoff'u harness yapar: ilk 4 adımda ilerleme yok, aynı çağrı 3 kez tekrarlandı, final check 2 kez geçmedi ya da budget bitti.
- Teacher sıfırdan başlamaz, agent'ın kaldığı yerden devam eder: bütün konuşmayı ve handoff'un nedenini görür.
- Agent'ınkinin yarısı kadar yeni bir budget'la (5 tool call) ve aynı tool'larla çalışır (adım 2–7).
- Teacher'ın `submit`'i de agent'ınki gibi final check'ten geçer (adım 7). Final check yine 2 kez geçmezse ya da teacher budget'ı içinde `submit` etmezse fallback answer döner.

**Fallback answer:** agent'ın ya da teacher'ın en son hatasız ve dolu sonuç veren SQL'i (`fallback`); yoksa cevap yok (`no_answer`). Çalışmayan bir SQL hiçbir zaman cevap olmaz.
→ Cevap ✔

**Dönen cevap:** SQL, label (`ok`, `fallback`, `no_answer`) ve cevabı kimin bulduğu (agent ya da teacher).

### İki örnek

**Örnek 1 ("2025'te en çok iade edilen kategori hangisi?"):**
1 (evidence: iade = `status = 'returned'`) → 2 → 4 (SQL) → 5 → 6 (gerçek sonuç: 1 satır) → 2 → 7 (final check geçti) → ✔

**Örnek 2 (aynı soru, agent yanlış sütun ve değer yazar):**
1 → 2 → 4 → 5 (`no such column: o.state`; not, sorgudaki tabloların gerçek sütunlarını gösterir) → 2 → 4 (düzeltilmiş SQL) → 5 → 6 (boş sonuç) → 2 → 3 (`search_values`: "returnd" → `status = 'returned'`) → 2 → 4 → 5 → 6 (1 satır) → 2 → 7 → ✔

### Soru bittikten sonra

**Experience log:** Her soru bitince, nereden çalıştırılırsa çalıştırılsın (`run.py`, `evaluate.py` ya da kullanımdaki bir uygulama), bir satır yazılır: agent'ın (handoff olduysa teacher'ın da) gördüğü konuşmanın tamamı, cevap ve label. Değerlendirmede cevabın doğru olup olmadığı da yazılır (`split = dev`); kullanımda doğru SQL olmadığı için bu alan boş kalır (`split = use`), orada eğitim sinyali teacher'ın çözümleri ve label'dır. Kayıtlar birikir, hiç silinmez.

**Agent eğitimi (ileride):** Agent, kullanılacağı harness'ın içinde, experience log'daki kayıtlarla eğitilir: önce teacher'ın doğru çıkan çözümleriyle SFT, sonra on-policy distillation (agent'ın kendi denemeleri, teacher'ın düzeltmesiyle), sonra RL (reward: cevabın doğruluğu). Eğitime yalnızca train split'inin kayıtları girer.

## Tasarım kararları

| Karar | Neden | Dayanak |
|---|---|---|
| Son cevap her zaman gerçekten çalıştırılır | Çalıştırılmamış bir SQL'in doğru olduğu bilinemez | — |
| Agent önce cevabı yazar, keşif sorgusuyla başlamaz | Keşif sorgularıyla başlayan küçük model çoğu zaman keşifte kalıyor ve cevabı hiç yazmıyor | — |
| Hata notu düzeltmek için gerekeni söyler | Küçük modeller hatayı ancak neyin yanlış olduğu açıkça yazılırsa düzeltebilir (ör. sorgudaki tabloların gerçek sütunları) | DualSQL |
| Temperature 0; takılınca örnekleme | En olası cevap tek SQL'de daha doğru; ama aynı girdiye hep aynı cevap verildiği için reddedilen ya da tekrarlanan çağrıdan sonra örneklenir | — |
| Sonuçlar BIRD'ün resmi kuralıyla karşılaştırılır (result key) | "Aynı sonuç" tek bir yerde tanımlıdır | BIRD |
| Adım 1 olabildiğince çok bilgi verir (sütun açıklamaları, column profile'ları) | Her search bir tool call harcar. Bilgi baştan gelirse budget denemeye kalır | DualSQL, HarnessSQL |
| İlerlemeyen agent erken handoff yapar | İlk adımlarında dolu sonuç alamayan agent genelde soruyu çözemiyor; teacher kısa bir geçmişle başlar, maliyet düşer | — |
| Teacher agent'ın kaldığı yerden devam eder | Agent'ın bulduğu bilgi boşa gitmez; handoff kayıtları doğrudan eğitim verisi olur | OLIVE, OVCSD |
| Agent harness içinde eğitilir | Harness dışında eğitilen model, harness'ta kullanıldığında 30.4'ten 9.6'ya düşüyor | HarnessSQL |

## Uygulama sırası

Sistem küçük, numaralı aşamalarla kuruldu; her aşama tek bir parça ekledi ve testle denendi. Liste [KOD_YAPISI.md](KOD_YAPISI.md) "Yazım sırası" bölümünde.

1. **SQLite + BIRD:** temel (veritabanı, puanlama, başlangıç bağlamı), ilk çalışan agent, trial loop (guardrail'ler, `search_values`), cevabı doğrulama (final check), handoff.
2. **Yerel modeller:** Policy ve teacher yerelde çalışır.
3. **Agent eğitimi (ileride):** experience log'la SFT → on-policy distillation → RL.

## Değerlendirme

- **BIRD dev:** 1.534 soru, evidence ile. Doğruluk BIRD'ün resmi kuralıyla ölçülür: cevabın result key'i gold SQL'inkiyle aynıysa doğru.
- **Base:** aynı sorularda tool'suz tek SQL (`baseline.py`); agentic sistem bununla karşılaştırılır.
- **Bir test için** 10 soru yeter (`--limit 10`). Kıyaslamalar en az 3 seed ile yapılır (0, 1, 2).
- **Ablation'lar:** Bir parçanın katkısı ölçülmek istendiğinde o parçayı kapatan bir flag eklenir; şu an her parça hep açıktır.

Bütün eşikler başlangıç değeridir; ölçülerek ayarlanır.

## Kaynakça

Yalnızca bu tasarımı doğrudan şekillendiren çalışmalar. Tam tarama [ARASTIRMA.md](ARASTIRMA.md) dosyasında.

**Pre-check**
- CYGNET ([2606.04645](https://arxiv.org/abs/2606.04645)): önce ucuz yapısal kontroller (adım 5).
- CacheRL ([2606.14179](https://arxiv.org/abs/2606.14179)): gerçek çalıştırma cache'i (adım 5).

**Harness**
- HarnessSQL ([2610.12274](https://arxiv.org/abs/2610.12274)): agent'ın kullanılacağı harness'ın içinde eğitilmesi; tool seti; teacher seçimi (Qwen3.6-27B).
- DualSQL ([2609.18135](https://arxiv.org/abs/2609.18135)): guardrail'ler (aynı çağrının tekrarı, format hatası).

**Handoff**
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) ve OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): teacher'ın agent'ın kaldığı yerden devam etmesi (adım 8); on-policy distillation.

**Değerlendirme**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): ana benchmark, evidence ve resmi sonuç karşılaştırma kuralı.
