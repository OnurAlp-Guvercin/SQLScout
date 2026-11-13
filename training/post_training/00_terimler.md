# Terimler sözlüğü

Bölümlerde sık geçen teknikler burada bir kez, basitçe anlatılıyor. Her terimde önce ne olduğu, sonra küçük bir örnek, sonra neden önemli olduğu var. Bölümler bu başlıklara link verir.

Örneklerde hep aynı senaryo kullanılıyor: model bir matematik sorusu ya da bizim projedeki gibi bir Text-to-SQL sorusu çözüyor.

## Temel kavramlar

### SFT
**Supervised fine-tuning.** Modele hazır "soru → doğru cevap" örnekleri verilir; model cevabı token token tahmin etmeyi öğrenir. Kayıp (loss) yalnızca cevap kısmında hesaplanır; soru kısmı kayba girmez.
- **Örnek:** "2+2 kaç?" sorusu ve "4" cevabı. Model "4"ü üretme olasılığını artırır.
- **Neden önemli:** Modele yeni bir biçim ya da davranış öğretmenin en ucuz yolu. Ama model yalnızca gördüğünü taklit eder; kendi hatasından öğrenmez.

### RL ve RLVR
**Reinforcement learning (RL):** Model kendi cevaplarını üretir, her cevaba bir puan ([reward](#reward)) verilir, model yüksek puan alan cevapları daha olası hale getirir. SFT'den farkı: hazır doğru cevap gerekmez, modelin kendi denemeleri kullanılır.
**RLVR (RL with verifiable rewards):** Puanın otomatik ve kesin bir kontrolle verildiği RL. Matematikte cevap doğru mu, kodda testler geçiyor mu, SQL'de sonuç doğru SQL'inkiyle aynı mı. Terim Tülu 3 (AI2) ile yaygınlaştı.
- **Fark:** RLHF'de puanı insan tercihlerinden öğrenilmiş bir [reward model](#reward-model-grm-ve-prm) verir. RLVR'da puan kuraldan gelir; bu yüzden kandırılması daha zordur.
- **Bizim projede:** "Cevabın sonucu gold SQL'in sonucuyla aynı mı" kontrolü hazır bir RLVR reward'ıdır.

### Rollout
RL sırasında modelin bir soruya ürettiği tam bir cevap. Agent'ta ise baştan sona bir trajectory: bütün tool call'lar ve observation'lar.
- **Örnek:** Aynı soruya 8 rollout = model soruyu 8 kez, örnekleyerek (temperature > 0) çözer.
- **Neden önemli:** RL'in en pahalı kısmı rollout üretmektir. Eğitim süresinin çoğu buraya gider.

### Reward
Bir rollout'a verilen puan.
- **Örnek:** Doğru cevap 1, yanlış 0. Bazen biçim hatasına −1 ya da çalışan ama yanlış SQL'e 0.1 gibi ara puanlar eklenir.
- **Neden önemli:** Model reward'ı en yükseğe çıkarmayı öğrenir, istediğimiz şeyi değil. Reward yanlış tasarlanırsa model açığı bulur ([reward hacking](#reward-hacking)).

### Pass rate ve pass@k
**Pass rate:** Bir soruya N rollout atıldığında doğru çıkanların oranı. 8 rollout'un 2'si doğruysa pass rate 0.25.
**pass@k:** k denemeden en az biri doğru mu? pass@1 tek denemedeki başarı; pass@8, 8 denemeden en az birinin doğru olma olasılığı.
- **Neden önemli:** Pass rate bir sorunun model için ne kadar zor olduğunu ölçer. RL verisi seçilirken en çok kullanılan ölçü budur: 0 (hiç çözemiyor) ve 1 (hep çözüyor) olan sorulardan model bir şey öğrenmez ([dynamic sampling](#dynamic-sampling)).

### Rejection sampling
Büyük ya da eğitilen modelden bir soruya birçok cevap üretilir; yalnızca doğrulanan (doğru çıkan) cevaplar tutulur, gerisi atılır. Tutulanlar SFT verisi olur.
- **Örnek:** 9B model bir BIRD sorusuna 4 kez çözüm üretir; sonucu gold'la aynı olan 1 tanesi SFT verisine girer.
- **Neden önemli:** Neredeyse bütün büyük laboratuvarlar SFT verisini böyle seçiyor. Bizim experience log'umuzdan SFT verisi çıkarmak da tam olarak budur.

### Cold start
RL'den önce yapılan kısa, küçük bir SFT. Amaç modele biçimi öğretmek: uzun düşünme, tool çağırma biçimi, cevabı nereye yazacağı.
- **Örnek:** DeepSeek-R1, RL'den önce birkaç bin örnekle cold start yaptı.
- **Neden önemli:** Biçimi bilmeyen bir model RL'de hiç doğru cevap üretemez, reward hep 0 olur, öğrenme başlamaz. Küçük modellerde bu daha da belirgin.

### CoT ve long CoT
**Chain of thought (CoT):** Modelin cevaptan önce adım adım düşünmesi.
**Long CoT:** Binlerce token'lık, kendini kontrol eden, geri dönen uzun düşünme (o1/R1 tarzı).
- **Neden önemli:** Reasoning modellerinin gücü buradan gelir. Ama uzun CoT küçük modellere aktarılırken zorlanıyor; bazı çalışmalar 3B ve altında kısa CoT'un daha iyi olduğunu gösteriyor. Bizim projede thinking kapalı.

### Thinking mode
Modelin cevaptan önce `<think> ... </think>` bloğunda düşünmesi. "Hybrid" modeller (ör. Qwen3) aynı ağırlıkla hem düşünerek hem düşünmeden cevap verebilir; bir talimatla seçilir.
- **Bizim projede:** Qwen3.5'te thinking kapalı, çünkü açıkken doğruluk düştü.

## RL algoritmaları

### PPO
**Proximal Policy Optimization.** Klasik RL algoritması. İki fikir var:
1. **Avantaj:** Her cevabın beklenenden ne kadar iyi olduğunu ayrı bir "value model" (critic) tahmin eder.
2. **Clip:** Model bir adımda çok fazla değişmesin diye, yeni ve eski model olasılıklarının oranı belli bir aralıkta (ör. 0.8–1.2) kırpılır.
- **Neden önemli:** Sağlam ama pahalı; value model ikinci bir büyük model demek. GRPO bu maliyeti kaldırmak için çıktı.

### GRPO
**Group Relative Policy Optimization** (DeepSeekMath, 2024). Bugün reasoning RL'inin standardı.
1. Her soru için bir grup rollout üretilir (ör. 8).
2. Her rollout'un reward'ı grubun ortalamasıyla karşılaştırılır: ortalamadan iyi olanın [avantajı](#advantage) pozitif, kötü olanınki negatif.
3. Model, avantajı pozitif cevapları daha olası, negatifleri daha az olası yapar (PPO'daki gibi clip ile).
- **Örnek:** 8 rollout'tan 2'si doğru (reward 1), 6'sı yanlış (0). Doğru olanlar güçlenir, yanlışlar zayıflar.
- **Neden önemli:** Value model gerekmez, bu yüzden çok daha ucuz. Dezavantajı: grubun hepsi aynı reward'ı alırsa (hepsi doğru ya da hepsi yanlış) avantaj sıfır olur ve o sorudan hiçbir şey öğrenilmez.
- **Türevleri:** DAPO, Dr. GRPO, GSPO, CISPO gibi pek çok değişiklik bölümlerde kendi yerlerinde anlatılıyor.

### Advantage
Bir cevabın "beklenenden ne kadar iyi" olduğu. GRPO'da: cevabın reward'ı eksi grubun ortalama reward'ı (çoğu zaman standart sapmaya bölünür).
- **Neden önemli:** Model reward'ı değil avantajı kullanır. Bu yüzden herkesin aynı puanı aldığı grupta sinyal yoktur.

### Clip ve clip-higher
**Clip:** Bir eğitim adımında bir token'ın olasılığı en fazla belli bir oranda değişebilir (ör. ±%20). Eğitimin aniden bozulmasını önler.
**Clip-higher** (DAPO): Üst sınır alt sınırdan geniş tutulur (ör. −%20, +%28). Böylece düşük olasılıklı ama iyi token'lar daha hızlı büyüyebilir.
- **Neden önemli:** Simetrik clip'te model zamanla hep aynı cevabı vermeye kayar ([entropy collapse](#entropy-ve-entropy-collapse)). Clip-higher keşfi canlı tutar.

### KL penalty
Eğitilen modelin başlangıç modelinden (reference model) çok uzaklaşmasına verilen ceza.
- **Neden önemli:** Klasik RLHF'de modeli dengede tutar. Reasoning RL'inde çoğu ekip KL'i kapatıyor ya da çok küçük tutuyor, çünkü modelin uzun düşünmeyi öğrenmesi için başlangıçtan uzaklaşması gerekiyor. NVIDIA ProRL ise uzun eğitimde KL'i kullanıp reference model'i ara ara güncelliyor.

### Dynamic sampling
Bütün rollout'ları aynı reward'ı alan soruları (pass rate 0 ya da 1) batch'ten atmak ve batch'i yeni sorularla doldurmak (DAPO).
- **Örnek:** 8 rollout'un 8'i de doğru: soru zaten öğrenilmiş, atılır. 8'in 0'ı doğru: model henüz bu soruya hazır değil, atılır.
- **Neden önemli:** Bu sorular GRPO'da sıfır gradient verir, yani boşuna hesaplanır. DAPO'da tek başına +8 puan getirdi. Neredeyse her reçetede var.

### Entropy ve entropy collapse
**Entropy:** Modelin bir sonraki token konusunda ne kadar "kararsız" olduğu. Yüksek entropy = çeşitli cevaplar.
**Entropy collapse:** RL sırasında modelin hep aynı cevabı vermeye başlaması. Bütün rollout'lar aynı olunca yeni bir şey denenmez ve öğrenme durur.
- **Neden önemli:** Uzun RL'in en sık bozulma nedeni. Clip-higher, entropy bonusu ya da yalnızca yüksek entropy'li token'ları güncellemek gibi çözümler var.

### Importance sampling
Veriyi üreten modelle eğitilen model tam olarak aynı değilse, her token'ın katkısı iki modelin olasılık oranıyla düzeltilir.
- **Ne zaman gerekir:** Rollout'lar bir önceki model sürümüyle üretildiyse, ya da inference motoru (ör. vLLM, bizde `mlx_lm.server`) eğitim kodundan biraz farklı olasılık hesaplıyorsa.
- **Neden önemli:** Bu fark büyürse RL bozulur. IcePop (Ant), GSPO (Qwen) gibi yöntemler bu sorunla uğraşıyor. Bizim kurulumda da geçerli: rollout'ları `mlx_lm.server` üretip eğitimi MLX kodu yaparsa iki taraf aynı olasılığı vermeyebilir.

### On-policy ve off-policy
**On-policy:** Eğitim verisi, eğitilen modelin kendi o anki cevaplarıdır (RL rollout'ları).
**Off-policy:** Veri başka bir modelden ya da modelin eski bir sürümünden gelir (ör. büyük modelin cevaplarıyla SFT).
- **Neden önemli:** On-policy veri, modelin gerçekten yaptığı hataları içerir; model kendi hatasından öğrenir. Off-policy veri ucuzdur ama model hiç düşmediği durumları öğrenir, kendi düştüğü durumları değil.

## Distillation ve tercih öğrenme

### Distillation
Büyük modelin bilgisini küçük modele aktarmak.
- **En basit hali (off-policy):** Büyük model cevaplar üretir, küçük model bunlarla SFT yapılır. DeepSeek-R1'in küçük modelleri (Distill-Qwen) böyle eğitildi.
- **Logit distillation:** Küçük model yalnızca büyük modelin seçtiği token'ı değil, bütün token'lara verdiği olasılıkları taklit eder. Daha çok bilgi taşır ama iki modelin tokenizer'ı aynı olmalı.
- **Neden önemli:** Küçük modeller için literatürdeki en güçlü yol. DeepSeek-R1'de 32B modelde distillation 72.6, doğrudan RL 47.0 aldı.

### On-policy distillation (OPD)
Küçük model kendi cevabını üretir; büyük model bu cevabın her token'ını puanlar ("ben bu token'ı ne kadar olası bulurdum?"). Küçük model, büyük modelin olası bulmadığı token'lardan uzaklaşır.
- **Örnek:** Küçük model SQL'de yanlış bir sütun adı yazar. Büyük model o token'a düşük olasılık verir. Küçük model tam o noktada düzeltilir.
- **Neden önemli:** RL gibi kendi hatasından öğrenir, ama reward tek bir sayı değil her token için bir sinyaldir. Bu yüzden çok daha verimli: Qwen3'te RL'in ~1/10 maliyetiyle RL'i geçti.
- **Gereken:** Büyük modelin token olasılıklarına erişim (genelde aynı tokenizer). API üzerinden çalışan büyük modelde bu her zaman mümkün olmayabilir.

### Multi-teacher distillation (MOPD)
Birden çok büyük modelden aynı anda distillation. 2026'daki yaygın hali: her alan için ayrı bir uzman model (matematik, kod, agent...) RL ile eğitilir; sonra tek bir model, her soruda o alanın uzmanından on-policy distillation ile öğrenir (Xiaomi MiMo, DeepSeek-V4, Kimi K3, NVIDIA).
- **Neden önemli:** Tek seferde bütün alanlarda RL yapmak alanları birbirine karıştırabiliyor; uzmanları ayrı eğitip birleştirmek bunu önlüyor. Ama karşılaştırmalı çalışmalar farkın küçük olduğunu söylüyor (en fazla ~1.4 puan). Tek görevli bir agent için gerekli değil.

### DPO ve preference optimization
**Preference optimization:** Modele "bu cevap şundan iyi" çiftleriyle öğretmek.
**DPO (Direct Preference Optimization):** Her çiftte iyi cevabın (chosen) olasılığı kötü cevaba (rejected) göre artırılır. Reward model ya da rollout gerekmez; SFT kadar ucuzdur.
- **Örnek:** Aynı BIRD sorusuna doğru SQL (chosen) ve yanlış SQL (rejected).
- **Neden önemli:** RL'den ucuz bir ara adım. Bizim experience log'umuz bu çiftleri zaten içeriyor.

### Reward model, GRM ve PRM
**Reward model (RM):** Bir cevaba puan veren, eğitilmiş ayrı bir model. Doğrulanamayan görevlerde (sohbet, yazı) kullanılır.
**GRM (generative reward model):** Puanı vermeden önce gerekçe yazan reward model (DeepSeek-GRM). Bizim large model kontrolümüz de böyle çalışıyor: önce gerekçe, sonra karar.
**PRM (process reward model):** Yalnızca son cevaba değil her adıma puan veren reward model. Karşıtı ORM (outcome reward model, yalnızca sonuca bakar).
- **Neden önemli:** Doğrulanabilir görevlerde (bizim SQL'imiz gibi) kural tabanlı reward çoğu zaman yeterli ve daha güvenilir; RM'ler kandırılabilir.

### LLM-as-judge ve rubric
Bir LLM'in başka bir modelin cevabını değerlendirmesi. **Rubric:** değerlendirmenin maddelere bölünmüş kriterleri (ör. "doğru tabloyu kullandı mı", "fazladan sütun var mı").
- **Neden önemli:** Doğrulanamayan görevlerde reward kaynağı. Kimi K2/K3 her sentetik görev için ayrı rubric yazdırıyor.

## Veri ve eğitim düzeni

### Curriculum
Eğitim verisini zorluk sırasıyla vermek.
- **Sabit curriculum:** Önce kolay, sonra zor (önceden belirlenmiş sıra).
- **Uyarlanır (adaptive) curriculum:** Modelin o anki başarısına göre zorluk seçilir; ör. pass rate'i ~0.5 olan sorular öne alınır.
- **Neden önemli:** Literatüre göre sabit sıra pek işe yaramıyor, uyarlanır curriculum yarıyor. Bağlam uzunluğunu ya da tur sayısını kademeli artırmak da bir curriculum türü.

### Model merging
Birkaç modelin ağırlıklarını birleştirmek (ör. ortalamasını almak), hiç eğitim yapmadan.
- **Örnek:** Aynı eğitimin son 3 checkpoint'inin ortalaması; ya da biri matematikte biri kodda iyi iki modelin birleşimi. "Slerp", "TIES" gibi yöntemler birleştirmenin farklı yollarıdır.
- **Neden önemli:** Çok ucuz, küçük ama ölçülebilir kazanç verebiliyor (Qwen3 Embedding 0.6B'de ~+2). Agent görevlerinde kötü sonuç da verebiliyor.

### Mid-training
Pretraining ile post-training arasında, hedefli veriyle (reasoning, uzun bağlam, agent trajectory'leri) yapılan ek eğitim.
- **Neden önemli:** Bazı raporlar (NVIDIA, Kimi) modelin RL'den ne kadar kazanacağının büyük ölçüde bu aşamada belirlendiğini söylüyor. Bizim ölçeğimizde yapılması gerçekçi değil; ama hangi base modelin seçileceğini etkiler.

### Self-play
Modelin kendi eğitim görevlerini üretmesi ya da kendisiyle oynaması.
- **Örnek:** Model bir soru yazar, sonra kendisi çözer; ya da bir rol saldırır, diğeri savunur.
- **Neden önemli:** Etiketli veri olmadan eğitim sinyali üretir. Absolute Zero, SPICE gibi çalışmalar bunu deniyor.

### Expert iteration
Döngü: model cevap üretir → doğrular tutulur → model bunlarla eğitilir → yeni modelle tekrar.
- **Neden önemli:** Rejection sampling'in tekrar tekrar uygulanması. RL'in basit, kararlı bir alternatifi (ör. DeepSeek-Prover-V2, GLM-4.5).

### LoRA
**Low-Rank Adaptation.** Modelin bütün ağırlıklarını değil, her katmana eklenen küçük "adaptör" matrislerini eğitmek.
- **Neden önemli:** Bellek ve hesap maliyeti çok düşer; bizim Mac'te eğitim için en gerçekçi yol (`mlx_lm.lora`). Thinking Machines'in "LoRA Without Regret" çalışmasına göre RL için çok küçük LoRA (rank 1) bile yetiyor, çünkü RL episode başına az bilgi öğretiyor.

### Loss masking
Bazı token'ları kayıptan çıkarmak: model onları görür ama üretmeyi öğrenmez.
- **Örnek:** Agent konuşmasında tool'un döndürdüğü sonuçlar (observation'lar) modelin yazdığı şey değildir; maskelenir. Model yalnızca kendi tool call'larını öğrenir.
- **Neden önemli:** Maskelenmezse model veritabanı sonuçlarını "uydurmayı" öğrenir. Search-R1'de maske kalkınca ~9 puan düştü. `mlx_lm.lora --mask-prompt` her örnekte yalnızca son cevabı kayba sokar.

### Reward hacking
Modelin reward'ı, görevi gerçekten çözmeden yükseltmenin yolunu bulması.
- **Örnek:** Güvenlik reward'ıyla eğitilen model her soruyu reddetmeyi öğrenir (Qwen3Guard). Ya da SQL'de reward "çalışıyor mu"ya verilirse model hep `SELECT 1` yazar.
- **Neden önemli:** Reward ne kadar basit ve kesinse o kadar az kandırılır. Ara reward'lar yalnızca cevap doğruysa verilmeli.

### Decontamination
Eğitim verisinden değerlendirme (benchmark) sorularını ve onlara çok benzeyenleri temizlemek; genelde n-gram çakışmasıyla.
- **Neden önemli:** Temizlenmezse ölçülen başarı ezberden gelir. Bizim projede eğitime yalnızca BIRD train girer, değerlendirme dev'de yapılır.

### MoE
**Mixture of Experts.** Modelin her token için parametrelerinin yalnızca bir kısmını (birkaç "uzman" alt ağ) kullanması. "235B toplam, 22B aktif" demek: model 235B parametreli ama her token'da 22B'si çalışıyor.
- **Neden önemli:** Büyük laboratuvar raporlarının çoğu MoE modeller. RL'de ek kararsızlık yaratıyor (her rollout'ta farklı uzmanlar seçilebiliyor). Bizim 0.8B modelimiz dense.

## Agent'a özgü

### Agentic RL ve multi-turn
Modelin tek cevap yerine birçok tur boyunca tool çağırdığı RL. Bir rollout = bütün konuşma: tool call → observation → tool call → ... → son cevap.
- **Zorluklar:**
  1. **Credit assignment:** Reward genelde yalnızca sonda gelir; 10 adımdan hangisinin iyi, hangisinin kötü olduğu bilinmez.
  2. **Observation masking:** Tool sonuçları kayba girmemeli ([loss masking](#loss-masking)).
  3. **Bozuk trajectory'ler:** Kesilen, tool hatasıyla biten ya da boş turlu rollout'lar genelde cezalandırılmak yerine güncellemeden çıkarılır.
  4. **Maliyet:** Her rollout gerçek tool çalıştırır (bizde SQL), bu yüzden yavaştır.
- **Bizim projede:** Small model'in döngüsü tam olarak bu yapıda; experience log'daki her satır bir multi-turn trajectory.

### Test-time scaling
Eğitimden sonra, cevap verirken daha çok hesap harcayarak başarıyı artırmak.
- **Örnek:** Daha uzun düşünmek, 8 cevap üretip çoğunluk oyu almak, en iyisini bir verifier'la seçmek.
- **Neden önemli:** Bazı reçeteler eğitimi buna göre yapıyor (ör. s1 "budget forcing"). Bizim final check'imiz de bir test-time kontrolü.

## Ölçüm

### Benchmarklar
Bölümlerde sık geçen değerlendirme setleri:

| Ad | Ne ölçer |
|---|---|
| AIME (2024, 2025) | Amerikan lise matematik olimpiyatı elemesi; yılda ~30 soru, cevap bir tam sayı. Reasoning'in en çok raporlanan ölçüsü |
| MATH-500 | 500 lise/üniversite matematik problemi |
| GPQA-Diamond | Doktora düzeyi fen soruları (çoktan seçmeli) |
| LiveCodeBench | Yakın tarihli yarışma programlama soruları; eğitim verisine sızmamış olsun diye sürekli yenilenir |
| Codeforces | Programlama yarışması sitesi; modelin "rating"i insanlarla karşılaştırılır |
| SWE-bench Verified | Gerçek GitHub issue'larını kod yazarak düzeltmek; testler geçerse başarılı |
| BFCL, τ-bench (tau-bench) | Tool calling: doğru fonksiyonu doğru argümanlarla çağırma, çok turlu görevler |
| MMLU, MMLU-Pro | Genel bilgi (çoktan seçmeli, birçok alan) |
| IFEval, Arena-Hard | Talimat takibi ve sohbet kalitesi |
| BIRD | Gerçek veritabanlarında Text-to-SQL; **EX (execution accuracy):** üretilen SQL'in sonucu doğru SQL'inkiyle aynıysa doğru. Bizim ana benchmark'ımız |
| Spider, Spider 2.0 | Text-to-SQL; Spider 2.0 büyük, kurumsal şemalarla |

- **pass@1 / avg@k:** Çoğu rapor tek denemedeki başarıyı (pass@1) k denemenin ortalaması olarak verir (ör. avg@16). Farklı makalelerin rakamları farklı ayarlarla ölçüldüğü için doğrudan karşılaştırılamaz.
