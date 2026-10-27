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
| Final check | Cevap dönmeden önceki son kontrol: submit edilen SQL hatasız çalışıyor mu, agent sonucunu görmüş mü, teacher onaylıyor mu (adım 7) |
| Handoff | İşin büyük teacher modele bırakılması |
| Evidence | BIRD'ün her soruyla birlikte verdiği kısa ipucu metni (ör. "iade edilen = `status = 'returned'`") |
| Result key | Bir sorgu sonucunu karşılaştırmak için kullanılan anahtar. Sonucun bütün satırları küme olarak alınır: satır sırası ve tekrar eden satırlar önemsiz, sütun sırası önemli (BIRD'ün resmi kuralı). Cevap, result key'i doğru SQL'inkiyle aynıysa doğrudur |
| Fallback answer | Hiçbir cevap kabul edilmediğinde dönen cevap: agent'ın ya da teacher'ın submit ettiği ve hatasız çalışan son SQL; `fallback` etiketi taşır, güveni düşüktür |
| Label | Dönen cevabın etiketi: `ok` (kabul edildi), `fallback` (kabul edilmedi ama submit edilmiş ve hatasız çalışan bir SQL var; düşük güven), `no_answer` (böyle bir SQL yok; SQL yerine hata mesajı döner) |
| Base | Karşılaştırma için tool'suz tek SQL: model adım 1'in bağlamını görür ve tek seferde bir SQL yazar (`baseline.py`) |
| Experience log | Her sorunun bütün konuşmalarının (agent'ın ve handoff olduysa teacher'ın her adımı), cevabın ve cevap doğru mu bilgisinin kaydı; agent'ın eğitim verisi buradan çıkar |
| Split | Verinin bölümü: train (eğitim) ya da dev (değerlendirme). Eğitime yalnızca train girer |
| SFT | Modeli doğru örnekleri taklit ettirerek eğitmek |
| On-policy distillation | Öğrenci modelin kendi denemelerini teacher'ın düzeltmesiyle eğitmek |
| RL | Modeli denemelerinin sonucuna göre reward ve ceza vererek eğitmek |
| Guardrail | Harness'ın agent'ı koruyan kuralları: aynı çağrının tekrarı yok, uzun sonuç kırpılır, bağlam dolarsa sıkıştırılır |
| Temperature | Modelin cevabındaki rastgelelik: 0'da hep en olası cevap, büyüdükçe daha çeşitli |
| EXPLAIN | Veritabanının sorguyu çalıştırmadan planını göstermesi. SQLite'ta sözdizimi ve eksik tablo/sütun hatalarını da çalıştırmadan yakalar |
| Aşama | Tek bir parça ekleyen, numaralı küçük iş (KOD_YAPISI.md "Yazım sırası") |

## Bileşenler

- **Policy agent:** Her adımda hangi tool'u çağıracağına karar verir. Şu an yerel `Qwen3.5-0.8B`; hedef `Qwen3.5-4B`. Şimdilik eğitilmemiş hâliyle kullanılır; ileride experience log'la harness'ın içinde eğitilir.
- **Harness (düz Python, LLM yok):** Tool'ları çalıştırır, kontrolleri ve final check'i yapar, handoff'a karar verir. Guardrail'leri de o uygular.
- **Veritabanı (SQLite, salt okunur):** `execute_sql`. Doğru SQL agent'ın bağlamına hiç girmez, yalnızca puanlamada kullanılır.
- **Teacher LLM:** Agent'ın cevabını kontrol eder (adım 7); handoff'tan sonra soruyu sıfırdan, kendi agent döngüsüyle çözer (adım 8). Şu an OpenRouter API'sindeki `Qwen3.5-9B`; hedef yerel `Qwen3.6-27B` (4-bit).

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
- Column profile'ları. Metin sütunlarında en sık 10 değer (en fazla 10 farklı değeri olan sütunlarda, ör. `status`, bütün değerler); geri kalan değerleri agent gerekirse `search_values` ile bulur. Neredeyse her satırı farklı olan metin sütunlarında (ör. isimler, kodlar) yalnızca 3 örnek: on isim yazılışı öğretmez, yalnızca bağlamı uzatır. Sayısal sütunlarda yalnızca en küçük ve en büyük değer. Boşluklu, özel karakterli ya da SQL kelimesi olan adlar (ör. `` `order` `` tablosu) backtick içinde gösterilir; agent onları öyle yazar.

BIRD dev'de bu bağlam en fazla ~12K token; modelin bağlam sınırının çok altında.

→ 2

### 2. Agent ne yapacağına karar verir

Agent her turda tek bir tool call yapar. Ne yapacağına ve hangi sırayla yapacağına kendisi karar verir; prompt yalnızca tool'ları ve ne işe yaradıklarını anlatır. Agent örnek bir sorguyla başlayabilir, önce veriyi keşfedebilir (ör. bir sütunda hangi değerler var, iki tablo nasıl bağlanıyor) ya da önce bir değeri arayabilir.
- Bir sorgu denemek ya da veriyi keşfetmek istiyorsa → `execute_sql` → 4
- Bir değerin veritabanında nasıl yazıldığını bilmiyorsa → `search_values` → 3
- Çalıştırdığı bir SQL soruyu cevaplıyorsa → o SQL'le `submit` → 7. Arada attığı sorgular (kontrol, düzeltme) cevabı etkilemez

Her observation'dan sonra agent buraya döner. Agent her adımda en olası cevabı seçer (temperature 0). Son çağrısı reddedildiyse ya da bir tekrarsa, aynı girdiye yine aynı cevabı vereceği için sıradaki adım örneklenir (temperature 0.7). Her tool call budget'tan bir düşer (en fazla 10). Reddedilen istekler ve tool call olarak okunamayan çıktılar da sayılır; hata agent'a döner. SQL argument'ının etrafındaki ```sql işaretleri ve baştaki `--` yorum satırları atılır; küçük modeller bunları sık ekler. Her sonucun altında kalan tool call sayısı yazar; son 2 hakta "çalıştırdığın bir sorgu soruyu cevaplıyorsa onu şimdi submit et" hatırlatması da eklenir. Agent ilk 4 tool call'ında dolu sonuç veren hiçbir SQL çalıştıramadıysa ya da bunlardan 2'si boşa gittiyse (okunamadı, tekrarlandı ya da pre-check'te reddedildi) ilerlemiyor sayılır ve harness işi hemen teacher'a verir → 8; boşa adım ve maliyet harcanmaz. Budget biterse de harness handoff'u zorlar → 8.

**Guardrail'ler.** Küçük modeller bazı tipik hataları sık yapar; bunlar sistemi bozmasın diye harness her adımda üç basit kural uygular (DualSQL).
1. **Tekrar yok:** Aynı çağrı (aynı tool, aynı argümanlar; SQL'de boşluklar ve sondaki `;` önemsenmez) ikinci kez gelirse çalıştırılmaz; "bunu zaten denedin" notu ve önceki sonuç döner, budget yine düşer. Aynı çağrı 3. kez tekrarlanırsa agent takılmış sayılır ve harness handoff yapar → 8. Yalnızca kendi çağrıları sayılır: teacher agent'ın konuşmasını görmediği için agent'ın denediği bir çağrı teacher'a tekrar sayılmaz, çalıştırılır. `submit` tekrar sayılmaz; onu final check sınırlar (adım 7).
2. **Uzun sonuç kırpılır:** Agent en fazla 20 satır görür, yanında toplam satır sayısı yazar.
3. **Bağlam sıkıştırılır:** Konuşma 32K token'ı aşarsa en eski sonuçlar tek satırlık özete iner (ör. "Columns: name | 358 rows").

### 3. Değer arama: `search_values`

Adım 1 zengin olduğu için çoğu soruda az gerekir. `search_values` bir kelimenin veritabanında hangi sütunda, hangi değer olarak geçtiğini bulur; benzer yazılanlar dahil. Örnek: "Los Angles" → `city = 'Los Angeles'`. 3 harften kısa kelimeler (ör. "UK") büyük/küçük harf farkı gözetmeden tam eşleşmeyle aranır. Birden çok kelimeli bir metin bulunamazsa kelimeler tek tek aranır: "Lewis Hamilton"da ad ve soyad ayrı sütunlardadır. Aynı benzerlikte harfleri birebir tutan değer önce gösterilir ('hamilton' değil 'Hamilton'). Hiçbir değer bulamazsa ve aranan kelime bir sütun adına benziyorsa o sütunları söyler; küçük modeller sütun adlarını da bu tool'la arıyor. Örnek: "Consumption" → `yearmonth.Consumption` sütunu.

Arama her şeyi bulamaz: soruda "iade", veritabanında `'returned'` yazıyorsa eşleşmez. Bu durumda evidence çoğu zaman eşleşmeyi verir; vermezse agent yanlış değerle boş sonuç alır; boş sonucun altındaki not onu değerin yazılışını `search_values` ile kontrol etmeye yönlendirir.
→ 2

### 4. `execute_sql` isteği

Agent denemek istediği SQL'i `execute_sql(sql="SELECT ...")` ile gönderir.
→ 5

### 5. Pre-check

**Neden:** Bozuk bir sorguyu çalıştırmadan, ucuz yoldan yakalamak.

Agent'ın SQL'leri ve final check buradan geçer. Harness sırayla üç soru sorar:
1. **Yazma mı yapıyor?** `SELECT` ya da `WITH` ile başlamıyorsa reddedilir. Örnek: `DELETE FROM orders`.
2. **Bozuk mu?** `EXPLAIN` sorguyu çalıştırmadan yazım hatasını, olmayan tabloyu ve sütunu yakalar. SQLite normalde bulamadığı "çift tırnaklı" bir adı metin sayar (`"Free Meal Count" > 10` hatasız ama yanlış çalışır); pre-check'te bu kapalıdır, SQLite "tek tırnak mı olmalıydı?" diye sorar. Not, hatayı düzeltmek için gerekeni de söyler: olmayan sütun hangi tablolarda var (o adda sütun yoksa adı benzeyen sütunlar, ör. `Free Meal Count` → `` `Free Meal Count (K-12)` ``), alias verilmiş bir tablo kendi adıyla yazıldıysa alias'ı ve sorgudaki tabloların gerçek sütunları; olmayan bir tablo yazıldıysa veritabanındaki tablolar. Örnek: `no such column: cc.client_id` → "client_id şu tablolarda var: client, disp. Sorgudaki tablolar ve sütunları: card (cc): card_id, disp_id, type, issued; ...".
3. **Daha önce çalıştı mı (cache)?** Çalıştıysa yeniden çalıştırılmaz, saklanan sonuç kullanılır. Örnek: agent'ın çalıştırdığı SQL'i final check yeniden çalıştırır.

1–2'de takılan sorgunun notu agent'a döner (→ 2).
→ 6

### 6. Gerçek çalıştırma

Sorgu veritabanında salt okunur çalıştırılır: keşif ve deneme sorguları en fazla 50 saniye, cevap olarak submit edilen ana sorgu en fazla 200 saniye. Keşifte zaman aşımına uğrayan sorgu için agent'a, soruyu cevaplıyorsa submit edebileceği söylenir; submit edilince uzun sınırla yeniden çalışır. 1 milyondan çok satır dönen sorgu (ör. JOIN koşulu unutulmuş) "JOIN koşulu ya da filtre ekle" hatasıyla durdurulur; BIRD dev'in en büyük doğru sonucu ~278 bin satır. Agent'a gerçek sonuç döner: sütunlar, satır sayısı, en fazla 20 satır ya da hata mesajı. Sonuç boşsa ya da tek satırı yalnızca 0 veya NULL ise (ör. yanlış yazılmış bir değerle `COUNT(*)` = 0) altına "sorgu bir metin değerine göre filtreliyorsa yazılışını `search_values` ile kontrol et" notu eklenir; değerin yanlış yazılması bunun en sık sebebi. Böyle bir sonuç ilerleme sınırı (adım 2) için dolu sayılmaz.
→ 2

> Adım 2 → 6 arası agent'ın **trial loop**'udur: ara, dene, sonuca bak, düzelt.

### 7. `submit` → final check

Agent cevap olarak seçtiği SQL'i `submit(sql="SELECT ...")` ile gönderir; arada attığı sorgular cevabı etkilemez. Cevap dönmeden önce son kontrol:
- **Salt okuma mı, tablolar ve sütunlar var mı, hatasız çalışıyor mu?** (adım 5–6; agent bu SQL'i daha önce çalıştırdıysa sonuç cache'ten gelir). Hata veren cevap geçmez. Boş sonuç geçer.
- **Agent bu SQL'in sonucunu görmüş müydü?** Agent sonucuna bakmadığı bir cevabı gönderemez. Görmediyse harness sorguyu çalıştırır, sonucunu agent'a gösterir ve "soruyu cevaplıyorsa yeniden submit et" der → 2. Bu bir hata sayılmaz. Örnek: agent hiç denemeden `WHERE County = 'Alemeda'` yazdıysa boş sonucu burada görür ve değeri düzeltir. Agent'a en fazla 20 satır gösterildiği için büyük sonuçlar sorun olmaz.
- **Teacher cevabı onaylıyor mu?** Çalışan bir SQL yanlış da olabilir. Agent'ın cevabını teacher kontrol eder: adım 1'in bağlamını, SQL'i ve sonucunu (agent'a yönelik `search_values` notu olmadan) görüp "bu soruyu doğru cevaplıyor mu? evet/hayır" sorusuna tek kelimeyle cevap verir. "Hayır" derse iş teacher'a geçer → 8. Handoff'tan sonra teacher'ın kendi `submit`'i de aynı kontrolden geçer; "hayır" çıkarsa iş kimseye geçmez: teacher'a "cevap yanlış bulundu, soruya ve evidence'a göre düzelt" notu döner ve bu final check hakkından düşer. Teacher'ın API'sine birkaç denemeye rağmen ulaşılamazsa agent'ın cevabı kaybolmasın diye kabul edilir; kontrolün yapılamadığı sonuç kaydına yazılır (`teacher_error`).

Geçti → **cevap döner ✔** (label `ok`). Final check'ten geçmedi → nedeni agent'a not olarak döner → 2. İkinci kez geçmezse → 8.

### 8. Handoff

Handoff'u harness yapar: ilk 4 adımda ilerleme yok ya da 2 çağrı boşa gitti, aynı çağrı 3 kez tekrarlandı, final check 2 kez geçmedi, teacher agent'ın cevabını onaylamadı ya da budget bitti.
- Teacher soruyu sıfırdan çözer: agent'ın konuşmasını görmez, yalnızca sistem prompt'u ve adım 1'in bağlamıyla başlar. Küçük modelin tekrarları ve yanlış denemeleri teacher'ı da yanlış yola sokar. Agent'ın konuşması experience log için saklanır.
- **İlk deneme:** Teacher önce base gibi tool'suz tek bir SQL yazar (temperature 0); harness onu `execute_sql` olarak çalıştırır ve sonucunu teacher'ın konuşmasına ilk adım olarak ekler (bir tool call sayılır). Teacher bu cevaptan başlar: doğruysa hemen submit eder, hata, boş sonuç ya da ret görürse döngüde düzeltir. Böylece döngü, teacher'ın tek seferde bildiği soruyu kaybettirmez; yalnızca üstüne ekler.
- Agent'ınkiyle aynı budget'la (10 tool call) ve aynı tool'larla, aynı agent döngüsünü çalıştırır (adım 2–7). İlk adımını temperature 0 ile atar. Final check'te kendi 2 hakkı vardır; submit edeceği SQL'in sonucunu kendisi görmüş olmalıdır.
- Teacher'ın `submit`'i de agent'ınki gibi final check'ten geçer (adım 7). Final check yine 2 kez geçmezse, teacher budget'ı içinde `submit` etmezse ya da teacher'ın API'sine ulaşılamazsa (`teacher_error`) fallback answer döner.

**Fallback answer:** agent'ın ya da teacher'ın submit ettiği ve hatasız çalışan son SQL (`fallback`, düşük güven). Örnek: teacher agent'ın cevabına "hayır" dedi ama kendisi de çözemedi; agent'ın reddedilen SQL'i döner. Kimse böyle bir SQL submit etmediyse cevap yok (`no_answer`): SQL yerine nedenini söyleyen bir hata mesajı döner. Keşif sorguları ve çalışmayan SQL'ler hiçbir zaman cevap olmaz.
→ Cevap ✔

**Dönen cevap:** SQL (cevap yoksa hata mesajı), label (`ok`, `fallback`, `no_answer`) ve cevabı kimin bulduğu (agent ya da teacher).

### İki örnek

**Örnek 1 ("2025'te en çok iade edilen kategori hangisi?"):**
1 (evidence: iade = `status = 'returned'`) → 2 → 4 (SQL) → 5 → 6 (gerçek sonuç: 1 satır) → 2 → 7 (final check geçti) → ✔

**Örnek 2 (aynı soru, agent yanlış sütun ve değer yazar):**
1 → 2 → 4 → 5 (`no such column: o.state`; not, sorgudaki tabloların gerçek sütunlarını gösterir) → 2 → 4 (düzeltilmiş SQL) → 5 → 6 (boş sonuç) → 2 → 3 (`search_values`: "returnd" → `status = 'returned'`) → 2 → 4 → 5 → 6 (1 satır) → 2 → 7 → ✔

### Soru bittikten sonra

**Experience log:** Her soru bitince, nereden çalıştırılırsa çalıştırılsın (`run.py`, `evaluate.py` ya da kullanımdaki bir uygulama), bir satır yazılır: agent'ın gördüğü konuşmanın tamamı, handoff olduysa teacher'ınki de (ayrı), cevap ve label. Değerlendirmede cevabın doğru olup olmadığı da yazılır (`split = dev`); kullanımda doğru SQL olmadığı için bu alan boş kalır (`split = use`), orada eğitim sinyali teacher'ın çözümleri ve label'dır. Kayıtlar birikir, hiç silinmez.

**Agent eğitimi (ileride):** Agent, kullanılacağı harness'ın içinde, experience log'daki kayıtlarla eğitilir: önce teacher'ın doğru çıkan çözümleriyle SFT, sonra on-policy distillation (agent'ın kendi denemeleri, teacher'ın düzeltmesiyle), sonra RL (reward: cevabın doğruluğu). Eğitime yalnızca train split'inin kayıtları girer.

## Tasarım kararları

| Karar | Neden | Dayanak |
|---|---|---|
| Son cevap her zaman gerçekten çalıştırılır | Çalıştırılmamış bir SQL'in doğru olduğu bilinemez | — |
| Hata notu düzeltmek için gerekeni söyler | Küçük modeller hatayı ancak neyin yanlış olduğu açıkça yazılırsa düzeltebilir (ör. sorgudaki tabloların gerçek sütunları) | DualSQL |
| Temperature 0; takılınca örnekleme | En olası cevap tek SQL'de daha doğru; ama aynı girdiye hep aynı cevap verildiği için reddedilen ya da tekrarlanan çağrıdan sonra örneklenir | — |
| Sonuçlar BIRD'ün resmi kuralıyla karşılaştırılır (result key) | "Aynı sonuç" tek bir yerde tanımlıdır | BIRD |
| Adım 1 olabildiğince çok bilgi verir (sütun açıklamaları, column profile'ları) | Her search bir tool call harcar. Bilgi baştan gelirse budget denemeye kalır | DualSQL, HarnessSQL |
| Agent'ın cevabını teacher onaylar | Çalışan bir SQL yanlış da olabilir; küçük model kendi yanlışını fark etmez. Teacher'ın tek kelimelik kontrolü, doğru cevapları ucuza kabul eder, yanlışları teacher'a gönderir | — |
| Fallback yalnızca submit edilmiş bir SQL'dir | Agent veriyi keşfedebildiği için en son çalışan sorgu bir keşif sorgusu olabilir; submit edilen SQL ise birinin "cevabım bu" dediği sorgudur. Kabul edilmediği için `fallback` etiketiyle düşük güvenli döner | — |
| İlerlemeyen agent erken handoff yapar | İlk adımlarında dolu sonuç alamayan ya da çağrıları boşa giden agent genelde soruyu çözemiyor; erken handoff aynı doğrulukla daha az tool call harcar | — |
| Teacher önce tek SQL yazar, cevabı da kontrol edilir | Döngüdeki teacher keşif yaptıkça soruyu yeniden yorumlayıp tek seferde bildiği soruları kaybediyordu; tek SQL'le başlamak bunu önler. Kontrolün reddi teacher'ın kaçırdığı hatayı (ör. eksik `HAVING`) döngüde düzeltmesini sağlar | — |
| Teacher sıfırdan, tam budget'la başlar | Agent'ın konuşmasını devralan teacher, küçük modelin tekrarlarını ve yanlış yollarını sürdürüyordu; temiz bağlamla kendi döngüsünü çalıştırınca daha çok soruyu çözüyor | — |
| Agent harness içinde eğitilir | Harness dışında eğitilen model, harness'ta kullanıldığında 30.4'ten 9.6'ya düşüyor | HarnessSQL |

## Uygulama sırası

Sistem küçük, numaralı aşamalarla kuruldu; her aşama tek bir parça ekledi ve testle denendi. Liste [KOD_YAPISI.md](KOD_YAPISI.md) "Yazım sırası" bölümünde.

1. **SQLite + BIRD:** temel (veritabanı, puanlama, başlangıç bağlamı), ilk çalışan agent, trial loop (guardrail'ler, `search_values`), cevabı doğrulama (final check), handoff.
2. **Yerel modeller:** Policy ve teacher yerelde çalışır.
3. **Agent eğitimi (ileride):** experience log'la SFT → on-policy distillation → RL.

## Değerlendirme

- **BIRD dev:** 1.534 soru, evidence ile. Doğruluk BIRD'ün resmi kuralıyla ölçülür: cevabın result key'i gold SQL'inkiyle aynıysa doğru.
- **Base:** aynı sorularda tool'suz tek SQL (`baseline.py`); agentic sistem bununla karşılaştırılır.
- **Teacher'ın kontrolü de ölçülür:** onayladığı ya da reddettiği SQL de puanlanır; özet, kaç onayın doğru, kaç reddin aslında doğru cevaba olduğunu yazar.
- **Bir test için** 10 soru yeter (`--limit 10`). Kıyaslamalar en az 3 tekrar koşuyla yapılır (her koşu ayrı bir `--name`). Gold SQL soru başına bir kez, ana sorgu süre sınırıyla (200 saniye) çalıştırılır.
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
- OLIVE ([2609.36246](https://arxiv.org/abs/2609.36246)) ve OVCSD ([2607.27937](https://arxiv.org/abs/2607.27937)): on-policy distillation (agent eğitimi, ileride).

**Değerlendirme**
- BIRD ([2305.03111](https://arxiv.org/abs/2305.03111)): ana benchmark, evidence ve resmi sonuç karşılaştırma kuralı.
