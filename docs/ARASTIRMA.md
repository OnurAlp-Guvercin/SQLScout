# Literatür Taraması: Agentic Text-to-SQL ve World Model'ler

**Kapsam:** 17 Nisan – 17 Ekim 2026. Bu aralıkta konferansta yayımlanan daha eski arXiv makaleleri ayrıca işaretlendi.
**Tarama tarihi:** 17 Ekim 2026.

## Yöntem ve doğrulama

- Beş alt konu paralel tarandı:
  1. Agentic Text-to-SQL ve RL
  2. Agent'lar için world model'ler
  3. Doğrulama, seçim ve güven
  4. Distillation, handoff ve kendini geliştiren agent'lar
  5. Benchmark'lar ve en iyi sistemler
- Makalelerin çoğu arXiv özet sayfasından doğrulandı. Tarifin ayrıntıları gereken yerlerde HTML tam metin de okundu. Liderlik tabloları 17 Ekim 2026'da doğrudan sayfalarından çekildi.
- Rakamların hepsi yazarların kendi raporladığı değerler. Hiçbiri yeniden üretilmedi.
- Makaleler arasında BIRD rakamları doğrudan karşılaştırılamaz: bazıları açgözlü (greedy) çözümleme, bazıları N candidate arasından seçim ya da oylama raporluyor.
- BIRD Mini-Dev'in %52.8'inde, Spider2-Snow'un %62.8'inde etiket hatası raporlanmış ([2601.08778](https://arxiv.org/abs/2601.08778)). 1–2 puanlık farklar bu gürültünün içinde kalabilir.

## 1. Özet: alan nereye yakınsadı?

1. **Önce teacher izleriyle SFT, sonra RL.** Bunu ablation'la test eden her çalışmada iki aşama birlikte, tek başına her birinden iyi çıkıyor. SFT olmadan yapılan RL reward istismarına kayıyor (TRUST-SQL).
2. **Model, kullanılacağı harness'ın aynısında eğitilmeli.** HarnessSQL'de harness dışında eğitilen model 9.6, harness içinde eğitilen 30.4 alıyor. SFT yolun tamamı üzerinde yapılıyor, observation token'ları kayıptan maskeleniyor.
3. **RL algoritması GRPO ailesinden, DAPO hileleriyle.** Asimetrik clip, sıfır varyanslı grupları filtrelemek, KL'i kaldırmak ya da azaltmak. Reward'un ağırlığı çalıştırma doğruluğunda; yardımcı terimler küçük tutuluyor ve doğrulukla koşullanıyor.
4. **4B ölçeği yeterli.** DualSQL-4B ve FineStep-4B BIRD dev'de yaklaşık 68 alıyor. Kapalı 4B sistemler BIRD test'te 76+ alıyor (Native mini 76.86, JoyDataAgent-SQL 76.19).
5. **Genel sıralamanın zirvesinde candidate generation & selection mimarisi var.** Candidate'ler sonuçlarına göre kümeleniyor, ardından ikili seçici ya da turnuva uygulanıyor. Tek başına reward model, kümeler arası consensus'tan zayıf kalıyor; ikisi birleştirildiğinde daha iyi.
6. **Küçük verifier'lar yeni şemalarda çöküyor.** Bilinen şemalarda AUROC 0.77–0.80, görülmemiş şemalarda 0.58–0.67. Şemalar arasında genelleyen tek sinyal büyük, dondurulmuş bir judge model.
7. **SQL sonucunu tahmin eden öğrenilmiş bir world model literatürde yok, yani `predict_sql` özgün.** Komşu alanlardan gelen kanıt, world model'in en büyük getirisinin çalıştırmanın yerine geçmekte değil, policy'yi eğitmekte olduğunu gösteriyor. Agent çalıştırmadan önce sonucu tahmin ediyor (agent forecast), gerçek çalıştırma bu forecast'ı kontrol ediyor ve bu kontrol her adım için ayrı bir eğitim sinyali veriyor (ANTE, ECHO).
8. **Çalıştırma tasarrufunun resmi olarak ölçülebildiği tek benchmark BIRD-Interact / Mini-Interact.** Her eylemin bir bird-coin maliyeti var ve `execute` 1 coin. Gereksiz deneme çalıştırmaları başarıyla negatif ilişkili (r ≈ −0.52).

## 2. Benchmark'lar ve liderlik tabloları (17 Ekim 2026)

### BIRD (test EX)

| Sıra | Sistem | Skor | Not |
|---|---|---|---|
| 1 | GrainSQL (Purdue) | 82.95 | Rapor yok |
| 2 | DataGallery-Text2SQL (Huawei) | 82.39 | Semantik katman + veri agent'ı |
| 3 | SiriusAI-SQL (Tencent) | 82.28 | |
| 5 | Agentar-Scale-SQL (Ant) | 81.67 | 17 candidate + RL ile eğitilmiş 32B seçici ile turnuva ([2509.24403](https://arxiv.org/abs/2509.24403)) |
| Tek model 1 | Gemini-SQL2 | 80.04 | Kapalı |
| Tek model 2 | ReToolSQL (Gemma-4 31B) | 78.14 | SFT → çok turlu RL |
| Tek model | SiriusAI-SQL-9B | 77.08 | |
| Tek model | Native mini (4B) | 76.86 | Tek 4B model, RL ile eğitilmiş veri agent'ı; ağırlıklar kapalı |
| Genel | JoyDataAgent-SQL (4B) | 76.19 | Rapor yok |
| Tek model | Qwen3.5-2B + StructCoT | 68.47 | Qwen 27B teacher'dan distillation, RL yok |
| Tek model | xorazm-text2sql (0.8B) | 59.59 | Qwen3.5-0.8B + GRPO |

- İnsan performansı 92.96.
- `bird_sql_dev_20251106` adlı daha temiz bir dev bölümü yayımlandı.

### Diğer benchmark'lar

| Benchmark | Neyi ölçer | En iyi | Bizim için |
|---|---|---|---|
| **BIRD-Interact / Mini-Interact** (SQLite, 300 görev) | Belirsizlik, kullanıcı simülatörü, bird-coin budget'ı. Maliyetler: `execute`=1, `ask`=2, `submit`=3; budget B = 6 + 2·m_amb + 2·λ | Tam set, a-Interact: ~30.9 (Reward*) | Gereksiz çalıştırmanın ve soru sormanın maliyetinin ölçülebildiği yer |
| BIRD-CRITIC-SQLite (500) | SQL hata ayıklama | 63.4; açık 7B modeller ~44 | Onarım ve handoff döngüsü |
| LiveSQLBench Base-Lite-SQLite | Kirlenmemiş, bilgi gerektiren sorular | 72.2 | SELECT alt kümesi |
| Spider 2.0-Lite (SQLite dilimi, 135) | Büyük şemalar, dağılım dışı | 76.2 (tümü) | Genelleme testi |
| Effi-SQL (yeni) | SQL verimliliği | | Çalıştırma sayısını değil sorgu hızını ölçer |

## 3. Agentic Text-to-SQL ve RL

| Çalışma | Tarih | Model | Tarif | Sonuç | Bizim için ders |
|---|---|---|---|---|---|
| [HarnessSQL 2610.12274](https://arxiv.org/abs/2610.12274) | Eki | Qwen3 8B/14B | Harness içinde toplanan, doğrulanmış teacher izleriyle SFT → DAPO; ikili reward | Spider2-SQLite 15.5→45.2 (8B) | Harness içinde eğit. Başarısız tool call'ları eğitim verisinden silme. Bağlam 8K→32K: 27→45. Large model seçimi kritik |
| [DualSQL 2609.18135](https://arxiv.org/abs/2609.18135) | Eyl | Qwen3 4B/8B | Yalnızca RL, iki rol tek ağırlıkta; tool'lar: FTS5 değer arama, profilleyici, execute; REX reward'u | BIRD dev **68.0 (4B)** / 71.1 | Rollout guardrail'leri: format hatasında kes, aynı çağrının tekrarını yasakla. Guardrail olmadan eğitim çöküyor |
| [ReToolSQL 2608.27796](https://arxiv.org/abs/2608.27796) | Ağu | Gemma-4 31B / E4B | Ayrıcalıklı teacher izleriyle SFT → GRPO + DAPO; KL azaltılarak | 74.32 dev; E4B 68.45 | Tool seti bizimkine çok benziyor. Tool'lar ile RL birbirinin etkisini artırıyor. Küçük modelde KL'i azaltarak gitmek +2 |
| [FineStep 2605.04719](https://arxiv.org/abs/2605.04719) | May | Qwen3 4B–30B | Ek model gerektirmeyen adım düzeyi process reward (hücre geri çağırma oranı) | **68.51 (4B, oylama)** | Ucuz adım düzeyi kredi. Tekrarlanan sorguyu cezalandır |
| [SERL-SQL 2608.00485](https://arxiv.org/abs/2608.00485) | Ağu | Qwen2.5-Coder 7–32B | Teacher, student'ın eylemlerini yeniden puanlıyor; GRPO avantajları yalnızca SQL/tool token'larında yeniden ağırlıklanıyor | 76.56 (16 candidate arasından seçim) | Large model sinyalini RL'in içine gömmenin bir yolu |
| [TRUST-SQL 2603.16448](https://arxiv.org/abs/2603.16448) | EMNLP'26 | Qwen3 4B/8B | Keşfet → Öner → Üret → Onayla; şema reward'u yalnızca cevap doğruysa veriliyor | 64.9 / 67.2 (4B) | Keşif tool'larının (ör. `search_values`) reward'u doğrulukla koşullanmalı. SFT olmadan model reward'u istismar ediyor |
| [SQL-Trail](https://aclanthology.org/2026.acl-long.1677/) | ACL'26 | Qwen2.5-Coder 3–14B | 1k Claude izi ile SFT → GRPO; reward 5×doğruluk + 2×tur | 64.2 (7B, oylama) | Tur reward'u gereksiz uzunluğu kesiyor |
| [BAP-SQL 2608.02876](https://arxiv.org/abs/2608.02876) | Ağu | **Qwen3.5-4B** | Analitik bir maliyet tahmincisi (EXPLAIN + istatistikler) + budget reward'u + çalışma zamanı kalkanı | Dar budget'ta +3.4; BIRD EX değişmiyor | `predict_sql`'e en yakın örnek. Yalnız dar budget'ta işe yarıyor, veritabanı yükünü azaltmıyor |
| [SQLConductor 2606.23537](https://arxiv.org/abs/2606.23537) | Haz | 4B/8B LoRA orkestratör | MCTS ile toplanan izlerle SFT → müfredatlı GRPO; büyük modelleri yönetiyor | 73.2 | Small model + büyük modeller kurgusu. SFT verisini en kısa çözüme göre değil, kararlılığa göre seç |
| [Progress-SQL 2606.06825](https://arxiv.org/abs/2606.06825) | Haz | 7B/14B | İlerleme reward'u + erken düzeltme bonusu | 67.5 (14B) | Hatadan toparlanmayı ödüllendirme şekli |
| [MERIT 2606.00547](https://arxiv.org/abs/2606.00547) | May | Bellek seçici 4B | RL ile öğrenilen bellek getirme + 7B process reward model | BIRD-Interact 23.3→33.0 | Experience log'dan bellek getirme. Yalnızca başarılı yolları sakla |
| [MARS-SQL 2511.01008](https://arxiv.org/abs/2511.01008) | ICML'26 | 3×7B | Öğrenilmiş verifier | 77.84 (verifier +8.5) | Final check aşamasının değeri büyük |
| [SQL-Zero 2609.04697](https://arxiv.org/abs/2609.04697) | Eyl | 3B/7B | Etiketsiz öz-oyun (self-play) | +6.6 / +7.3 | Yalnızca ilk iterasyon dağılım dışına transfer oluyor |
| [ReViSQL 2603.20004](https://arxiv.org/abs/2603.20004) | Ağu | | Doğrulanmış veriyle RLVR; SQL denkliği reward'u | | Sonuç eşleşmesi reward'unda yanlış pozitifler var |
| [Sentinel 2610.04156](https://arxiv.org/abs/2610.04156) | Eki | | Yol özelliklerinden reddet / durdur / cevabı tut kararı veren sınıflandırıcı | | Agent'ın takıldığını fark edip hand off etmesi için şablon |
| [Small LM DB agent 2609.21341](https://arxiv.org/abs/2609.21341) | Eyl | 39 yerel model | Hata analizi | Kayıpların %36'sı tool argümanı hatası | Tool şemasını doğrula, argümanları kaydet |

## 4. World model'ler

| Çalışma | Tarih | Ne tahmin ediyor | Nasıl kullanılıyor | Sonuç | Bizim için ders |
|---|---|---|---|---|---|
| [ANTE 2610.15368](https://arxiv.org/abs/2610.15368) | Eki | Her tool call'dan önce policy bir agent forecast (test sonucu, çıkış kodu) ve "trust / abstain" kararı yazıyor | Trust reward'u γ = αq*/(1−q*): "trust" demek ancak doğruluk q* hedefini aşınca kazandırıyor | SWE-bench V 25.0→57.2 (inanç olmadan aynı RL'e göre +6.2) | Agent'ın kendi sonucunu tahmin edip güvenip güvenmeyeceğine karar vermesi için en yakın şablon |
| [ECHO 2605.24517](https://arxiv.org/abs/2605.24517) | May | Ortam token'ları | GRPO'ya ek kayıp: ortam token'ları üzerinde çapraz entropi | Terminal-Bench'te GRPO'nun yaklaşık 2 katı | Ek rollout gerektirmeyen yoğun sinyal |
| [DSWorld 2607.15901](https://arxiv.org/abs/2607.15901) | Tem | Veri bilimi durum geçişleri (8B) | MLP yönlendirici: ucuz adımlar gerçek çalıştırmaya, pahalılar simülatöre | Aramada 3–6 kat hız; calibration raporlanmamış | Kurallarla durum inşası. Maliyet bilincine dayalı yönlendirme |
| [EnvSimBench 2605.07247](https://arxiv.org/abs/2605.07247) | May | Tool geri bildirimi + durum değişiklikleri | 4B simülatör | Durum değişikliği sayısı arttıkça doğruluk uçuruma düşüyor (5+ değişiklikte ≤%4) | Eğitim verisini sonuç sınıfına göre dengele. Akıl yürütme izleri burada zarar veriyor |
| [Qwen-AgentWorld 2606.24597](https://arxiv.org/abs/2606.24597) | Haz | 7 alanda dil tabanlı world model (35B/397B) | Simülatörde RL | Kontrolsüz simülasyon fayda sağlamıyor; kontrol edilebilir simülasyon + kural çapası +3.7 / +12.3 | Simülasyonla RL'de mutlaka gerçek çapa olmalı |
| [WMRL 2608.12564](https://arxiv.org/abs/2608.12564) | Ağu | Deney sonucu | RL'de reward kaynağı | Eğitim 3–4 kat hızlı | Online yanlılık giderme + ters varyansla ağırlıklandırma |
| [CoMAP 2606.02372](https://arxiv.org/abs/2606.02372) | Haz | Eylem geri bildirimi | Agent'ın değişen davranışına uyum için policy'nin kendi yolları üzerinde self-distillation'la güncelleniyor | Qwen3-4B'de +16.75% (göreli) | World model'i small model'in güncel verisiyle sürekli yeniden eğit |
| [Dual-Frontier 2609.26293](https://arxiv.org/abs/2609.26293) | Eyl | | Prediction'a yalnızca, beklenen kazanç world model hatası için sertifikalı sınırı aşıyorsa güven | Kanıtlı garanti | "Önce doğrula, sonra güven" ilkesi |
| [Role-Stratified CRC 2607.24343](https://arxiv.org/abs/2607.24343) | Tem | | Her rol için ayrı conformal risk budget'ı | | Result type, result shape, values ve sorgu tipleri için ayrı eşikler |
| [CYGNET 2606.04645](https://arxiv.org/abs/2606.04645) | Haz | Cypher sorguları için çalıştırma öncesi gate | Katmanlı kontrol: ayrıştırma → şema → ayna veritabanında çalıştırma | Yapısal hataların %100'ünü yakalıyor; semantik hataların %0'ını | Önce ucuz yapısal kontroller, sonra öğrenilmiş prediction |
| [CacheRL 2606.14179](https://arxiv.org/abs/2606.14179) | Haz | | Gerçek çalıştırma sonuçlarının bulanık cache'i | | Cache, ilk ve en ucuz world model katmanı |
| [AOSpec 2608.00881](https://arxiv.org/abs/2608.00881) | Ağu | Observation spekülasyonu | Spekülasyon her zaman doğrulanarak kullanılıyor | Gecikme %12–33 azalıyor | Prediction, doğrulanırsa gecikmeyi kayıpsız gizler |
| [WorldEvolver 2606.30639](https://arxiv.org/abs/2606.30639) | Haz | | Seçici öngörü | Güçlü modellerde kazanç gürültü düzeyinde | Ham token olasılığı aşırı özgüvenli |
| [World-model-as-tool](https://aclanthology.org/2026.acl-long.623/) | ACL'26 | | World model agent'a tool olarak veriliyor | Agent'lar adımların %1'inden azında çağırıyor; zorlanınca %5'e varan kayıp | Simülatörü kullanma kararı yalnızca small model'e bırakılmamalı |
| [Imperfect WMs are Exploitable 2605.15960](https://arxiv.org/abs/2605.15960) | May | | Teori | | Small model, world model'in hatalarını istismar eder |
| [False Prophets 2607.23147](https://arxiv.org/abs/2607.23147) | Tem | | Saldırı | Yanlış prediction'ı tetikleme başarısı %95 | Prediction güvenlik korumalarını asla devre dışı bırakmamalı |

## 5. Doğrulama, seçim, güven ve calibration

| Çalışma | Tarih | Bulgu | Bizim için ders |
|---|---|---|---|
| [Selective prediction 2607.06799](https://arxiv.org/abs/2607.06799) | Tem | Kara kutu sinyaller 0.61–0.68 AUROC. İnce ayarlı verifier bilinen şemada 0.77–0.80, yeni şemada 0.66. İki büyük judge'ın lojistik regresyonla birleşimi 0.82 AUROC, ECE 0.03 | Gate'i, eğitimde görülmemiş veritabanlarında kalibre et |
| [TraceSQL 2608.17795](https://arxiv.org/abs/2608.17795) | Ağu | Görülmemiş veritabanlarında GradeSQL-7B 0.58 AUROC; yapısal özellikler yardımcı | Küçük reward model'e yeni şemada güvenme |
| [Certified Against Which Oracle? 2609.25938](https://arxiv.org/abs/2609.25938) | Eyl | Tek veritabanında çalıştırma eşleşmesi riski 3–10 puan düşük gösteriyor; nominal 0.10 garanti, uzman etiketlerine göre 17–20 puan risk taşıyor | Calibration'ı daha sıkı etiketlerle yap (çoklu veritabanı örneği ile test paketi) |
| [GradeSQL 2606.30851](https://arxiv.org/abs/2606.30851) | Haz | Sonuç reward model'i, 32 candidate arasında 68.90 (çoğunluk oylaması 66.95). 32B reward model daha kötü | 1.5–7B reward model yeterli, ama yalnızca bilinen şemalarda |
| [SIRIUS-SQL 2606.01246](https://arxiv.org/abs/2606.01246) | May | Reward model tek başına 74.32 < çoğunluk oylaması 75.03 < consensus + reward model 75.88 | Reward model'i consensus'un yerine değil, yanına ekle |
| [R³-SQL 2604.25325](https://arxiv.org/abs/2604.25325) | Nis | Candidate'ler sonuca göre gruplanıyor; doğru candidate havuzda yok görünüyorsa yeniden örnekleniyor | Gate ile yeniden örnekleme birlikte kullanılabilir |
| [Knowing When to Stop 2607.03991](https://arxiv.org/abs/2607.03991) | Tem | Öğrenilmiş durma kuralı %35 daha az çağrı yapıyor | Örneklemeyi ne zaman durduracağına uyarlanabilir karar ver |
| [LLM-as-Judge audit 2609.30290](https://arxiv.org/abs/2609.30290) | Eyl | Qwen3.6-27B judge ≈ Opus düzeyinde (κ 0.72). Zayıf ve güçlü judge'ın ortalaması daha kötü sonuç veriyor | Judge'ları ortalama ile değil, birleştirici model (stacking) ya da oybirliği ile birleştir |
| [Small LMs know? 2609.20824](https://arxiv.org/abs/2609.20824) | | Küçük modelde token entropisi durumların %91'inde bilgi taşımıyor | Örneklemeye ya da çalıştırmaya dayalı belirsizlik kullan |
| [Predict own failure 2610.18614](https://arxiv.org/abs/2610.18614) | Eki | GRPO içinde sonuca göre ödüllendirilen sözel güven: AUROC 0.68–0.85, ECE <0.12 | RL'e calibration reward ekle |
| [PlanPool 2610.02739](https://arxiv.org/abs/2610.02739) | Eki | Agent'lar netleştirme sorusunu çok erken bırakıyor | Belirsiz soruda tahmin etmek yerine sormak gerekir |
| [Crystallization 2608.07213](https://arxiv.org/abs/2608.07213) / [MIRA 2608.06950](https://arxiv.org/abs/2608.06950) | Ağu | Doğrulanmış onarımları saklamak +4.34 (MIRA: +16.5) | Veritabanına özgü repair memory |

## 6. Distillation, handoff ve kendini geliştiren agent'lar

### Distillation

| Çalışma | Tarih | Bulgu | Bizim için ders |
|---|---|---|---|
| [Guided-OPD 2606.15912](https://arxiv.org/abs/2606.15912) | Haz | Teacher müdahalesi kosinüsle sıfıra iniyor; student turlarında ters KL, teacher turlarında ileri KL | Eğitimin 2. adımı (on-policy distillation) için en yakın şablon (aynı tokenizer gerekiyor) |
| [TCOD 2604.24005](https://arxiv.org/abs/2604.24005) | Nis | Yol derinliği üzerinde müfredat; OPD'ye göre +18 | Çok turlu OPD'yi kararlı hale getiriyor |
| [SOD 2605.07725](https://arxiv.org/abs/2605.07725) | May | İlk yanlış tool call'dan sonrasını maskelemek 42.98'den 31.85'e düşürüyor | Hatadan sonrasını kesme, ağırlığını düşür |
| [STRIDE 2609.14636](https://arxiv.org/abs/2609.14636) | Eyl | Teacher'ın log-olasılığı düştüğünde rollout'u durdurup oradan yeniden başlatıyor; 3.7 kat hız | Aynı sinyal handoff tetikleyicisi olarak da kullanılabilir |
| [Top-K tool drift 2607.07050](https://arxiv.org/abs/2607.07050) | Tem | Qwen3.5'te top-K logit'ler tool call'u başlatan token'ı kaçırıyor | **Qwen3.5'e özgü:** top-K OPD'de tool başlangıç token'larını geri ekle |
| [Sequential Beats Joint 2609.04108](https://arxiv.org/abs/2609.04108) | Eyl | Önce OPD, sonra RL; OPD, RL için SFT'den daha iyi bir başlangıç | 3 aşamalı tasarımımızı doğruluyor |
| [RL Starts before RL 2609.28145](https://arxiv.org/abs/2609.28145) | Eyl | RL'den önce ters KL, sonra ileri KL | KL yönü seçimi |
| [GATS 2609.37898](https://arxiv.org/abs/2609.37898) / [RSTG 2608.00782](https://arxiv.org/abs/2608.00782) | Eyl / Ağu | Teacher yalnızca tüm denemeleri başarısız olan gruplarda devreye giriyor ve zamanla geri çekiliyor | RL adımında large model'in rolü |
| [SGCD 2606.12634](https://arxiv.org/abs/2606.12634) | Haz | Doğrudan self-distillation tool kullanımını bozabiliyor | Kontrol policy gradient'te kalmalı |
| [Solving w/o Stopping 2609.37326](https://arxiv.org/abs/2609.37326) | Eyl | OPD küçük modele çözmeyi öğretiyor, durmayı öğretmiyor | Düşünme kapalı ya da kısa düşünme modu kullan |
| [Below the Noise Floor 2608.27729](https://arxiv.org/abs/2608.27729) | Ağu | Seed'ler arası standart sapma 2.8–48.7 puan | En az 3 seed'le değerlendir |
| [OLIVE 2609.36246](https://arxiv.org/abs/2609.36246) | Eyl | Teacher, student'ın bıraktığı durumdan devam ediyor; log-olasılık gerekmiyor | **API ile kullanılan large model için OPD alternatifi; handoff kayıtlarımız zaten bu yapıda** |
| [BPM 2607.22334](https://arxiv.org/abs/2607.22334) | Tem | Farklı tokenizer'lar arasında OPD | Large model farklı aileden olursa |
| [AMD 2608.07169](https://arxiv.org/abs/2608.07169) | Ağu | Eğitimsiz, hiyerarşik teacher belleği; en çok 4B student'lar kazanıyor | Ağırlıklara dokunmadan bilgi aktarımı |

### Handoff ve yönlendirme

| Çalışma | Tarih | Bulgu | Bizim için ders |
|---|---|---|---|
| [TSDS 2607.26865](https://arxiv.org/abs/2607.26865) | Tem | Learn-Then-Test ile kalibre edilen handoff eşiği; maliyet garantisi | Eşik calibration'ı için ilkeli bir yöntem |
| [Replay Gap 2608.08239](https://arxiv.org/abs/2608.08239) | Ağu | Model değişince sonraki eylemlerin %61–94'ü değişiyor | Handoff'u replay ile değil, live fork'larla değerlendir. Large model'e yeni bir budget ver |
| [KL-PBD 2610.15128](https://arxiv.org/abs/2610.15128) | Eki | Uzman etiketi yalnızca hand off edilen vakalarda var, bu bir seçim yanlılığı yaratıyor | Handoff verisindeki yanlılığı düzelt |
| [Agentic Routing Flywheel 2607.11399](https://arxiv.org/abs/2607.11399) | Tem | Her karar (sorgu, durum, seçim, iz, sonuç, maliyet) kaydı olarak tutuluyor | Experience log şeması |

### Kendini geliştirme ve çökme riski

| Çalışma | Tarih | Bulgu | Bizim için ders |
|---|---|---|---|
| [Continual Experience 2606.04703](https://arxiv.org/abs/2606.04703) | Haz | Tekrarlı turlarda mevcut yöntemler giderek çöküyor | Tekrarlı yeniden eğitim turlarında en büyük risk |
| [ReSAIL 2609.39306](https://arxiv.org/abs/2609.39306) | Eyl | Bilgilendirici adımları seçmek + dondurulmuş teacher'a doğru düzenlileştirme | Çökmeye karşı tarif |
| [Denser ≠ Better 2607.01763](https://arxiv.org/abs/2607.01763) | Tem | Yoğun self-distillation daha çok unutturuyor; GRPO koruyor | Her turda RL bileşeni kalmalı |
| [BCIT 2608.26730](https://arxiv.org/abs/2608.26730) | Ağu | Geçmiş güncelleme kanıtlarının yeniden kullanımını gate'lemek | Yeniden eğitilen small model için promotion gate |
| [UpgradeBench 2608.20918](https://arxiv.org/abs/2608.20918) | Ağu | Bir Text-to-SQL uzmanı modelin ömrü, temel modelin bir sürüm aralığından kısa | Ham girdileri sakla; large model yeniden etiketleyebilsin |
| [OVCSD 2607.27937](https://arxiv.org/abs/2607.27937) / [HINT-SD 2605.17873](https://arxiv.org/abs/2605.17873) | Tem / May | Teacher, student'ın durumundan devam ediyor; kayıp yalnızca hatanın olduğu yerlere uygulanıyor | Handoff vakasını eğitim verisine çevirme şablonu |
| [MFC 2609.13997](https://arxiv.org/abs/2609.13997) | Eyl | 128 çözülemeyen problem ≈ 2.000 problemle GRPO | Zor vakalar için müfredat |

## 7. 4B agent için gerçekçi beklenti

Bu tablo karşılaştırılabilir sistemlerden yapılmış bir çıkarımdır, ölçüm değildir.

| Kurulum | Beklenen BIRD EX |
|---|---|
| Qwen3.5-4B sıfır atış / düz SFT | ~46 / 54–56 (dev) |
| SFT + tool'lu RL, tek geçiş | 62–68 (dev) |
| + en fazla 8 candidate, sonuç kümelemesi | 66–71 (dev); test ~70–74 |
| Kapalı 4B sistemlerin tavanı | 76+ (test) |
| Large model'e handoff | +2–5, ancak bu durumda sistem genel sıralamaya girer, tek model sıralamasına değil |
| Mini-Interact Reward* | ~10–20 (en iyi modeller ~30) |

## 8. Veri setleri

| Veri seti | Motor | Boyut | Kullanım |
|---|---|---|---|
| BIRD train / dev | SQLite | ~9.4k / 1.534 soru, 95 veritabanı, toplam 33.4 GB | Small model'in eğitimi ve ana değerlendirme. Daha temiz dev bölümü: `bird_sql_dev_20251106` |
| SynSQL-2.5M (OmniSQL, [2503.02240](https://arxiv.org/abs/2503.02240)) | SQLite | 2.544.390 örnek, 16.583 veritabanı, Apache 2.0 | World model'in eğitimi: SQL'ler çalıştırılıp etiket üretilir. Small model için ek SFT verisi |
| Mini-Interact / BIRD-Interact ([2510.05318](https://arxiv.org/abs/2510.05318)) | SQLite / Postgres | 300 görev (Mini) | Budget'lı değerlendirme. Bir kısmı CRUD görevi; salt okunur kurulumda SELECT alt kümesi kullanılır |
| BIRD-Critic-SQLite | SQLite | 500 görev | Onarım ve handoff |
| LiveSQLBench Base-Lite-SQLite | SQLite | | Kirlenmemiş değerlendirme (SELECT alt kümesi) |
| Spider 2.0-Lite (SQLite dilimi) / Spider 2.0-DBT | SQLite / DuckDB | 135 / 68 görev | Dağılım dışı genelleme. HarnessSQL, DBT veritabanlarını SQLite'a taşıdı |
| TPC-H / TPC-DS | DuckDB / Postgres | İstenen ölçekte üretilir | Gerçekten yavaş veritabanı (Phase 3). Doğal dilde soru seti yok |

Etiket kalitesi uyarısı: ReViSQL, BIRD train örneklerinin %61'inin düzeltme gerektirdiğini raporluyor. Eğitimden önce veri temizliği yapılmalı (DualSQL bariz ve çözülemez örnekleri çıkardı, bazılarını yeniden etiketledi).

## 9. Uygulama için tarif özeti

Aşağıdaki değerler ilgili makalelerden alındı. Başlangıç noktasıdır, ablation'la ayarlanmalıdır.

**Harness ve tool'lar**
- Tool'lar ReToolSQL ve DualSQL ile uyumlu:
  - Salt okunur sorgu: yalnızca SELECT/WITH, en fazla ~100 satır döner.
  - Column profiler.
  - BM25 / FTS5 ile değer arama.
- Tur sınırı 5–10. SERL-SQL'de 10 tur 5 turdan biraz kötü; TRUST-SQL'de 12 tur kararsız.
- Bağlam 32K. HarnessSQL'de 8K'dan 32K'ya çıkmak doğruluğu 27.4'ten 45.2'ye taşıyor.
- Guardrail'ler (DualSQL):
  - Format hatasında rollout kesilir.
  - Aynı çağrının aynı argümanlarla tekrarı yasaklanır.
  - Observation token'ları kayıptan maskelenir.
- Tool argümanları doğrulanır ve kaydedilir. Küçük modellerde kayıpların %36'sı tool argümanı hatası (2609.21341).
- Düşünme modu kapalı ya da kısa olmalı (Solving w/o Stopping).

**Small model eğitimi**
1. **SFT** (HarnessSQL):
   - Veri: harness içinde toplanmış, doğrulanmış large model izleri. Başarılı izlerin içindeki başarısız tool call'lar silinmez.
   - Kayıp yolun tamamı üzerinde hesaplanır, observation'lar maskelenir.
   - 3 epoch, lr 1e-5 (cosine), etkin batch 16.
   - **Seçilen large model: Qwen3.6-27B, 4-bit** (~16–17 GB; 48 GB'a small model ile birlikte sığar). Gerekçe: HarnessSQL'de bu large model'le 23.0, Qwen3.5-9B ile 7.4; DeepEye-SQL bununla BIRD test 78.42; judge olarak Opus düzeyinde (κ 0.72). Kullanmadan önce bizim harness'ımızdaki başarısı ölçülür.
2. **On-policy distillation** (Guided-OPD, TCOD):
   - Large model müdahalesi kosinüsle sıfıra iner.
   - Small model turlarında ters KL, large model turlarında ileri KL.
   - İlk yanlış tool call'dan sonrası kesilmez, ağırlığı düşürülür (SOD).
   - Top-K logit kullanılıyorsa tool call'u başlatan token'lar geri eklenir (Qwen3.5'e özgü sorun).
   - Qwen3.6 ile Qwen3.5'in tokenizer'ı aynı mı, önce doğrulanır. Değilse OLIVE kullanılır: large model, small model'in kaldığı yerden devam eder, log-olasılık gerekmez.
   - Doğrulama skoru durağanlaşınca RL'e geçilir (Sequential Beats Joint).
3. **RL** (HarnessSQL, ReToolSQL):
   - DAPO, asimetrik clip [0.20, 0.28], lr 1e-6.
   - Grup başına 8–16 rollout, sıfır varyanslı gruplar filtrelenir.
   - KL kapalı ya da azalarak sıfıra iner (ReToolSQL: 0.005 → 0.001 → 0).
   - **Ana reward:** REX (sağlam sonuç eşleşmesi) ile ikili çalıştırma doğruluğu, artı küçük bir format terimi. Yardımcı terimler (şema, tur) yalnızca cevap doğruysa verilir (TRUST-SQL).
   - **İsteğe bağlı calibration reward:** sözel güven, sonuca göre ödüllendirilir (2610.18614).
   - Large model yalnızca tüm denemeleri başarısız olan gruplarda devreye girer ve zamanla geri çekilir (GATS, RSTG).

**Handoff ve offline döngü**
- Large model, small model'in kaldığı yerden yeni bir budget'la devam eder (OLIVE). Yalnızca çalıştırmayla doğrulanan devamlar eğitime girer, kayıp hatanın olduğu adımlara uygulanır (OVCSD, HINT-SD).
- Her turda önceki verilerle karıştırılır. Dondurulmuş önceki small model'e doğru düzenlileştirilir (ReSAIL). RL bileşeni korunur (Denser ≠ Better).
- Yeni small model, en az 3 seed'le ve tutma testleriyle promotion gate'ten geçer (BCIT, Below the Noise Floor).
- Ham girdiler saklanır. Temel model yükseltildiğinde large model yeniden etiketleyebilir (UpgradeBench).
- Experience log şeması (Agentic Routing Flywheel'den): soru, split, konuşmanın tamamı (her tool call ve observation), cevap, label, doğru mu, handoff nedeni, model adları. Eğitime yalnızca train split'i girer.
