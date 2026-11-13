# Veri seçimi, zorluk, curriculum ve SFT↔RL etkileşimi (kesişen çalışmalar)

**Bu bölümde ne var:** Bu dosya tek bir laboratuvarın değil, beş ortak soruya cevap arayan çalışmaların dosyası. Sorular şunlar: [SFT](00_terimler.md#sft) verisi nasıl seçilir (SFT: modele doğru örnekleri gösterip taklit ettirmek), SFT ile [RL](00_terimler.md#rl-ve-rlvr) nasıl birleşir (RL: model kendisi dener, iyi denemeleri ödüllendirilir), RL verisinin zorluğu ve [curriculum](00_terimler.md#curriculum)'u nasıl ayarlanır (curriculum: soruların hangi sırayla ve hangi zorlukta verileceği), [distillation](00_terimler.md#distillation)'ın ayrıntıları neler (distillation: büyük bir modelin bilgisini küçük modele aktarmak) ve birden çok büyük modelden ya da domain expert'ten (alan uzmanı modelden) nasıl öğrenilir. Girdiler önce soruya göre (1→5), her sorunun içinde yeniden eskiye sıralı. Rakamlar yazarların bildirdiği değerlerdir; her girdi arXiv sayfasından doğrulandı.

**Bu bölümün ana dersleri:**
- **Soru 1 (SFT verisi):** Küçük model için büyük modelin en parlak cevabı değil, küçük modele tanıdık gelen, doğrulanmış ve kısa cevaplar seçilmeli; az veriyi çok kez tekrar etmek çok veriyi bir kez görmekten iyi olabilir.
- **Soru 2 (SFT ile RL):** Modelin hiç çözemediği sorular SFT'ye (doğru çözüm gösterilerek), ara sıra çözdüğü sorular RL'e gitmeli; uzun ve ağır bir SFT sonraki RL'i bozabilir, RL eski yetenekleri SFT'den daha az unutturur.
- **Soru 3 (RL verisinin zorluğu):** RL'de en çok öğreten sorular modelin denemelerinin yaklaşık yarısında çözdükleri; hep çözülen ya da hiç çözülemeyen soruları atlamak eğitimi yaklaşık iki kat hızlandırıyor.
- **Soru 4 (distillation):** Büyük modelin gücünden çok, eğitilen modelle düşünme biçiminin uyumu önemli; önce kısa bir SFT, sonra on-policy distillation (eğitilen modelin kendi cevapları üzerinde, her token'da büyük modelin olasılıklarına yaklaşması) iyi bir sıra.
- **Soru 5 (birden çok kaynak):** Domain expert'leri tek modelde toplamanın yolları (merge: ağırlıkları birleştirmek; karışık RL: bütün alanların verisiyle tek RL; MOPD: birden çok expert'ten on-policy distillation) ortalamada birbirine çok yakın; tek görevli bir agent için tek bir RL koşusu yeterli, farklı kaynakların verisini düz karıştırmak ise zararlı olabilir.

**Makaleler:**

*Soru 1: SFT verisi nasıl seçilir*
- Capacity-Dependent Effects of Data Selection for Reasoning — hangi cevabın seçileceği modelin boyutuna bağlı.
- Rethinking Generalization in Reasoning SFT — SFT de genelleyebilir; süre, veri kalitesi ve taban model belirliyor.
- Student-in-the-Loop Chain-of-Thought Distillation — eğitilen model, büyük modelin cevabını yazılırken yönlendiriyor.
- Data Repetition Beats Data Scaling in Long-CoT SFT — az veriyi çok epoch'la eğitmek daha iyi.
- NaturalThoughts — hangi düşünce izlerinin distillation'a gireceği: zorluk, çeşitlilik, kısa/uzun karışımı.
- AceReason-Nemotron 1.1 — (başka dosyada) SFT ve RL'in birlikte etkisi.
- Climbing the Ladder of Reasoning — SFT hangi zorluktaki soruyu ne kadar veriyle çözüyor.
- Small Models Struggle to Learn from Strong Reasoners — küçük modeller çok güçlü modelin uzun izlerinden öğrenemiyor.

*Soru 2: SFT ile RL nasıl birleşir*
- DeReason — kolay sorular SFT'ye, zor sorular RL'e.
- On the Interplay of Pre-Training, Mid-Training, and RL — RL verisi modelin biraz üstünde olmalı.
- Supervised Reinforcement Learning — (başka dosyada) uzman trajectory'lerinden adım adım RL.
- Towards a Unified View of LLM Post-Training (HPT) — soru başına SFT ya da RL seçen kural.
- RL's Razor — RL neden daha az unutturuyor.
- On the Generalization of SFT (DFT) — SFT kaybında tek satırlık bir düzeltme.
- SRFT — SFT ve RL'i tek aşamada, entropy'ye göre ağırlıklandırarak birleştirmek.
- Learning What RL Can't (ReLIFT) — RL sırasında çözülemeyen sorulara ara ara SFT.
- Learning to Reason under Off-Policy Guidance (LUFFY) — RL grubuna güçlü bir modelin doğru cevabını eklemek.
- SFT or RL? (görsel-dil modelleri) — ağır SFT sonraki RL'i bozabiliyor.
- SFT Memorizes, RL Generalizes — (başka dosyada) SFT ezber, RL genelleme.

*Soru 3: RL verisinin zorluğu ve curriculum*
- Small Generalizable Prompt Predictive Models (GPS) — rollout atmadan soru zorluğunu tahmin etmek.
- The Art of Scaling RL Compute — (başka dosyada) öğrenme sinyali vermeyen soruları atmak.
- Demystifying RL in Agentic Reasoning — tool kullanan agent'larda veri ve RL tercihleri.
- Prompt Curriculum Learning (PCL) — yarı yarıya çözülen soruları seçmek.
- Reasoning with Exploration: An Entropy Perspective — keşfi korumak için advantage'a entropy terimi.
- Act Only When It Pays (GRESO) — işe yaramayacak rollout'ları baştan atlamak.
- The Surprising Effectiveness of Negative Reinforcement — yanlış cevapları cezalandırmanın gücü.
- Self-Evolving Curriculum (SEC) — curriculum'u bir bandit'e öğretmek.
- Adaptive Curriculum Learning (AdaRFT) — ortalama ödülü 0.5'te tutan zorluk ayarı.
- LIMR: Less is More for RL Scaling — RL verisinin %16'sıyla aynı sonuç.

*Soru 4: Distillation ayrıntıları*
- SOD: Step-wise On-policy Distillation — (başka dosyada) küçük agent'larda on-policy distillation.
- Rethinking On-Policy Distillation — OPD ne zaman işler, hangi büyük model seçilmeli.
- Self-Distilled Reasoner (OPSD) — ayrı bir büyük model olmadan on-policy distillation.
- Distillation Scaling Laws — (başka dosyada) distillation'da ölçekleme.

*Soru 5: Birden çok büyük modelden ya da domain expert'ten öğrenme*
- Who Teaches Which Token? (VG-OPD) — hangi expert'in hangi token'ı öğreteceğine bir verifier karar veriyor.
- Consolidating RLVR Capabilities Across Domains — merge, karışık RL ve MOPD aynı koşullarda.
- MOPD: Multi-Teacher On-Policy Distillation — domain expert'leri OPD ile tek modelde toplamak.
- To Mix or To Merge — karışık RL ile ayrı RL + merge karşılaştırması.
- Local Naturalness for Selecting Teacher Data — birden çok büyük modelin cevapları arasından seçim.
- Merge-of-Thought Distillation — her büyük model için ayrı SFT, sonra ağırlıkları ortalamak.
- Agentic-R1 — tool kullanan ve kullanmayan iki büyük modelden tek modele.

---

## Soru 1: SFT verisi nasıl seçilir?
Elimizde büyük modelin yazdığı çok sayıda çözüm var; hangilerini küçük modele göstermeliyiz? Bu grup; zorluk, çeşitlilik, veri miktarı, tekrar sayısı ve çözümün uzunluğu açısından bu soruya bakıyor.

### Capacity-Dependent Effects of Data Selection for Reasoning (Virginia Tech, Ağustos 2026) — [2608.13721](https://arxiv.org/abs/2608.13721)
**Soru:** 1 (zorluk: veriyi eğitilen modelin kapasitesine göre seçmek).

**Tek cümlede:** Küçük modele, büyük modelin cevapları arasından ona tanıdık gelen cevabı vermek, yabancı gelen cevabı vermekten daha iyi; bu yalnız 8B'de ve uzun eğitimde tersine dönüyor.

**Problem:** Büyük model aynı soruya birkaç farklı doğru cevap yazabilir. SFT'ye hangisinin gireceği önemli. Bir görüşe göre modele en çok yeni şey öğreten "uzak" cevap seçilmeli. Öbür görüşe göre modelin kolayca öğrenebileceği "tanıdık" cevap seçilmeli. Yazarlar doğru seçimin eğitilen modelin boyutuna bağlı olup olmadığını sordu.

**Ne yaptılar:**
1. Sorular MATH12K'dan alındı (yarışma matematiği soruları). Cevapları iki büyük model yazdı: Qwen2.5-72B ve gemma-3-27b-it.
2. Her cevabın "zorluğu", eğitilen modelin o cevaba verdiği log-likelihood ile ölçüldü. Log-likelihood, modelin bu metni kendisinin üretme olasılığının logaritmasıdır. Yüksekse cevap modele tanıdıktır ("bunu ben de yazabilirdim"). Düşükse cevap modele uzaktır.
3. Her soru için eğitilen modele göre en yüksek ya da en düşük likelihood'lu cevap seçildi. Böylece iki veri seti çıktı: "tanıdık" set ve "uzak" set.
4. Bu setlerle 1.5B ile 8B arası modeller eğitildi (Qwen2.5-1.5B, Qwen2.5-3B-Instruct, Qwen3-4B, Qwen3-8B...). Her model 1 ve 5 epoch eğitildi. Epoch, verinin tamamının üzerinden bir kez geçmek demek.

**Sonuç:** Yazarların raporuna göre ortaya "Fast-Fit / Slow-Gain" (hızlı uyum / yavaş kazanç) deseni çıkıyor. Tanıdık veri hızlı öğreniliyor. Uzak veri ancak büyük modelde ve uzun eğitimde karşılığını veriyor.
- 1.5B'de tanıdık veri hep kazanıyor. 5 epoch sonra MATH'te (lise ve üniversite düzeyi yarışma matematiği) 57.6'ya karşı 44.4; 13 puandan fazla fark. AMC'de (ABD lise matematik yarışması) 35.0'a karşı 22.5.
- 1.5B, 3B ve 4B'de 5 epoch sonra da tanıdık veri önde.
- Yalnız 8B'de, uzun eğitimde uzak veri 10 [benchmark](00_terimler.md#benchmarklar)'ın 9'unda öne geçiyor (benchmark: modelleri karşılaştırmak için kullanılan standart test seti).
- Küçük modeller uzak cevapları öğrenemeyince yüzeysel ya da kendini tekrar eden davranışa kayıyor.

**Bizim için:** 0.8B–4B için SFT'ye, large model'in trajectory'leri arasından small model'in zaten "anlayabildiği" (yüksek likelihood'lu) başarılı olanlar seçilmeli; uzak ve parlak çözümler değil.

### Rethinking Generalization in Reasoning SFT: A Conditional Analysis on Optimization, Data, and Model Capability (Shanghai AI Lab, SJTU, USTC; Nisan 2026, COLM 2026) — [2604.06628](https://arxiv.org/abs/2604.06628)
**Soru:** 1 ve 2 (doğrulanmış iz; "SFT ezberler" iddiası).

**Tek cümlede:** Uzun düşünce metinleriyle yapılan SFT de başka alanlara genelleyebilir; ama bu, eğitimin süresine, verinin kalitesine ve taban modelin gücüne bağlı.

**Problem:** Yaygın bir görüş var: "SFT ezberler, RL genelleştirir." Yani SFT ile eğitilen model yalnız gördüğü türden sorularda iyileşir. Yazarlar bunun uzun [CoT](00_terimler.md#cot-ve-long-cot) SFT'si için de geçerli olup olmadığını sordu. CoT (chain-of-thought), modelin cevaptan önce yazdığı adım adım düşünce metnidir; uzun CoT bunun binlerce token'lık hâlidir. Görüş yanlışsa, SFT'yi erken bırakan ekipler yanlış karar veriyor demektir.

**Ne yaptılar:**
1. Taban modeller: Qwen3-14B/8B-Base, InternLM2.5-20B ve daha küçükler (Qwen3-4B, 1.7B). "Base" model, yalnız pre-training görmüş, talimat eğitimi almamış modeldir.
2. Düşünce izlerini (çözüm metinlerini) Qwen3-32B üretti; DeepSeek-R1 ve QwQ-32B de kullanıldı.
3. Veri olarak 20K soruluk Math-CoT gibi setler alındı. Modeller 8 epoch eğitildi; dayanıklılığı sınamak için yapılan stres testinde 16 epoch.
4. Üç etken ayrı ayrı değiştirildi: eğitimin süresi, verinin kalitesi (doğrulanmış uzun iz ya da düşük kaliteli çözüm) ve taban modelin gücü.

**Sonuç:** Yazarların raporuna göre:
- Alan dışı başarı (eğitilmediği görevlerdeki başarı) önce düşüyor, uzun eğitimde geri geliyor. Buna "dip-and-recovery" (dibe vurup toparlanma) diyorlar. Bu yüzden erken bir checkpoint'e (eğitimin ara kaydına) bakıp karar vermek yanıltıyor.
- Doğrulanmış uzun CoT ile Qwen3-14B, LCB v2'de (LiveCodeBench: yeni çıkmış programlama yarışması soruları) taban modelin 37.5'inden 55.1'e çıkıyor. GPQA-D'de (GPQA-Diamond: lisansüstü düzeyde, aramayla bulunması zor fen soruları) 44.1'den 63.3'e. Yani matematik verisiyle kod ve fende yaklaşık 18–19 puan kazanılıyor.
- Düşük kaliteli NuminaMath çözümleri ise alan dışında geniş bir düşüş getiriyor.
- 1.7B neredeyse hiç kazanmıyor; yalnız uzun cevabın biçimini kopyalıyor.
- Uzun CoT SFT'si güvenliği (ör. zararlı istekleri reddetme davranışını) belirgin biçimde bozuyor.

**Bizim için:** Küçük modelde uzun düşünce izini taklit ettirmek yerine kısa, doğrulanmış (final check'ten geçmiş) trajectory'lerle ve yeterince epoch'la SFT yapılmalı; sonuç erken checkpoint'lerle değerlendirilmemeli.

### Student-in-the-Loop Chain-of-Thought Distillation via Generation-Time Selection (Tsinghua, Nisan 2026) — [2604.02819](https://arxiv.org/abs/2604.02819)
**Soru:** 1 (öğrenilebilirlik açığı; hangi izin seçileceği).

**Tek cümlede:** Büyük model cevabını yazarken her yol ayrımında eğitilen modele "hangisi sana tanıdık?" diye sorunca, çıkan SFT verisi küçük model için çok daha öğretici oluyor.

**Problem:** Standart distillation'da büyük model cevabı baştan sona yazar. Sonra bir süzgeç uygulanır; çoğunlukla [rejection sampling](00_terimler.md#rejection-sampling) (birkaç cevap üretip yalnız doğru olanları tutmak). Ama doğru bir cevap bile küçük modele çok yabancı olabilir; küçük model onu öğrenemez. Buna "öğrenilebilirlik açığı" deniyor. Üretim bittikten sonra süzmek, baştan yabancı bir yola sapmış izleri kurtaramaz.

**Ne yaptılar:** Yönteme Gen-SSD diyorlar.
1. Büyük model (QwQ-32B; ablation'da R1-Distill 7B/14B/32B) cevabı parça parça yazıyor. Her parçada birkaç farklı devam örnekliyor. (Ablation: bir parçayı değiştirip ya da çıkarıp etkisini ölçen deney.)
2. Eğitilen model (Qwen2.5-Math-1.5B) bu adaylardan perplexity'si en düşük olanı seçiyor. Perplexity, modelin bir metne ne kadar "şaşırdığını" ölçer; düşükse metin ona tanıdıktır.
3. Büyük model yalnız seçilen daldan devam ediyor. Parça başına aday sayısı 16 → 8 → 4.
4. Sonunda doğru cevaba varan ve toplam perplexity'si en düşük tek iz tutuluyor; SFT bu izlerle yapılıyor.

Basit bir benzetme: büyük model bir problemde üç farklı ilk adım önerir. İkisi ileri bir yöntem, biri küçük modelin bildiği basit bir yol. Küçük model basit olanı seçer ve çözüm o yoldan sürer.

**Sonuç:** Yazarların raporuna göre beş matematik benchmark'ının ortalamasında Gen-SSD 34.94 alıyor. Rejection sampling ile standart distillation 29.01'de kalıyor; fark +5.9 puan. Üretim bittikten sonra eğitilen modele göre süzen MoRSD 33.07 alıyor. Yani seçimi üretim sırasında yapmak, sonradan süzmekten de yaklaşık 1.9 puan daha iyi.

**Bizim için:** Large model'in handoff trajectory'lerinden SFT verisi seçerken, small model'in perplexity'si düşük ve doğru biten trajectory'ler öne alınmalı; bu ucuz bir "öğrenilebilirlik" süzgecidir.

### Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning (UTN, NVIDIA, Mistral AI; Şubat 2026) — [2602.11149](https://arxiv.org/abs/2602.11149)
**Soru:** 1 (veri miktarı ve tekrar; epoch sayısı).

**Tek cümlede:** Aynı eğitim bütçesiyle, az sayıda örneği çok kez tekrar etmek, çok sayıda örneği bir kez görmekten belirgin biçimde daha iyi.

**Problem:** SFT verisi üretmek pahalı; her örneği büyük model yazmalı ve doğrulanmalı. Sabit bir hesaplama bütçesi varsa iki seçenek var: az veriyi çok epoch'la eğitmek ya da çok veriyi tek geçişle eğitmek. Yaygın sezgi "çok veri daha iyidir" der. Yazarlar bunu uzun CoT SFT'sinde ölçtü.

**Ne yaptılar:**
1. Base modeller: Olmo3-7B, Qwen3-8B, Qwen3-4B.
2. Veri: Dolci adlı uzun CoT setinden 200 ile 51.2K örnek arası iç içe alt kümeler (küçük küme büyüğün içinde).
3. Toplam güncelleme sayısı hep 51.200'de sabit tutuldu. Küçük veri daha çok epoch'la (1 ile 256 arası) bu sayıya ulaştı. Örneğin 3.2K örnek × 16 epoch = 51.2K güncelleme.
4. Eğitim boyunca token accuracy de izlendi: modelin eğitim verisindeki bir sonraki token'ı doğru tahmin etme oranı.

**Sonuç:** Yazarların raporuna göre:
- Olmo3-7B'de 3.2K örnek × 16 epoch: AIME'24 42.3, AIME'25 39.2, GPQA 34.0. (AIME: ABD lise matematik olimpiyatı eleme soruları; GPQA: lisansüstü düzey fen soruları.)
- Aynı bütçeyle 51.2K örnek × 1 epoch: 17.7, 22.3 ve 11.5. Yani 16 kat az veriyle iki katından fazla puan.
- Kazanç 32–64 epoch civarında doyuyor. Qwen3-4B daha erken, yaklaşık 8 epoch'ta doyuyor.
- Eğitim token accuracy'si %100'e yaklaşınca kazanç bitiyor. Yazarlar bunu durma ölçütü olarak öneriyor; validation loss'un (ayrı tutulan verideki kaybın) yanılttığını söylüyorlar.
- Zayıf bir kaynaktan (0.6B model) üretilen veride ise örnek sayısı arttıkça sonuç kötüleşiyor.

**Bizim için:** Az sayıda doğru trajectory'yi çok epoch'la eğitmek, Mac'te pahalı veri üretmekten daha verimli olabilir; durma için token accuracy izlenmeli.

### NaturalThoughts: Selecting and Distilling Reasoning Traces for General Reasoning Tasks (Meta FAIR, Temmuz 2025) — [2507.01921](https://arxiv.org/abs/2507.01921)
**Soru:** 1 (rastgele ölçek, zorluk, çeşitlilik, kısa ve uzun CoT karışımı).

**Tek cümlede:** DeepSeek-R1'in düşünce izlerinden hangilerinin distillation'a girmesi gerektiğini sistematik olarak karşılaştırdılar; rastgele ve bol veri güçlü, ama zor sorular ve zorluğa göre kısa/uzun karışımı daha verimli.

**Problem:** Büyük modelin ürettiği izler çok sayıda ve her biri pahalı. Hepsini kullanmak yerine iyi bir alt küme seçilebilir mi? Seçilecekse ölçüt ne olmalı: uzunluk mu, zorluk mu, konu çeşitliliği mi? Ayrıca her soruya uzun düşünce gerekmeyebilir.

**Ne yaptılar:**
1. Sorular NaturalReasoning setinden (genel akıl yürütme soruları), izler DeepSeek-R1'den alındı.
2. Eğitilen modeller: Llama-3.1-8B, Qwen-2.5-7B, Llama-3.3-70B. Veri boyutu 1K ile 500K örnek arasında değiştirildi.
3. Seçim ölçütleri karşılaştırıldı: izin uzunluğu; modellerin anlaşmazlığı (birkaç model farklı cevap veriyorsa soru zor sayılır); konu çeşitliliği ve akıl yürütme stratejisi çeşitliliği.
4. Ayrıca tam iz (System-2: yavaş, adım adım düşünme) ile yalnız cevap (System-1: doğrudan cevap) karışımı denendi.

**Sonuç:** Yazarların raporuna göre:
- Rastgele örneklerle veriyi büyütmek güçlü bir base. GPQA-D 1K örnekte 37.1, 500K örnekte 48.3; doyum görülmüyor.
- 10K örnekte en iyi seçim "modeller anlaşmıyor" (yani zor) sorular: 39.7. Aynı boyutta rastgele seçim 37.6.
- Konu bazlı çeşitlilik rastgeleden kötü (32.7). Akıl yürütme stratejisi çeşitliliği ise iyi.
- Zorluğa göre karışım (izlerin yalnız %36'sı uzun) hem daha kısa hem daha doğru cevaplar veriyor: 38.9. Bu karışımın hangi ayarla karşılaştırıldığı notta belirtilmemiş.

**Bizim için:** Kolay sorularda kısa (doğrudan submit eden) trajectory, zor sorularda uzun keşifli trajectory kullanan bir karışım, small model'in hem doğruluğunu hem tool call sayısını iyileştirebilir.

*AceReason-Nemotron 1.1: Advancing Math and Code Reasoning through SFT and RL Synergy — Soru 1 ve 2 (soru sayısı ve soru başına cevap sayısı; SFT'nin gücünün sonraki RL'e etkisi). Bir model raporu, ama çekirdeği kontrollü bir SFT/RL çalışması. Ayrıntısı "NVIDIA (Nemotron)" bölümünde ([07_nvidia.md](07_nvidia.md)).*

### Climbing the Ladder of Reasoning: What LLMs Can—and Still Can't—Solve after SFT? (UC Berkeley, AI2; Nisan 2025) — [2504.11741](https://arxiv.org/abs/2504.11741)
**Soru:** 1 (veri boyutu ve küratörlük).

**Tek cümlede:** SFT orta zorluktaki soruları az veriyle hızla çözüyor, zor sorularda bir tavana çarpıyor, en zor soruları ise hiç çözemiyor.

**Problem:** Birçok çalışma "1K iyi seçilmiş örnek yeter" diyor (ör. s1, LIMO). Ama hangi zorlukta yeter? Ortalama bir puan, kolay soruda kazanılanı ve zor soruda kaybedileni gizler. Yazarlar SFT'nin etkisini zorluk katmanlarına ayırarak ölçtü.

**Ne yaptılar:**
1. AIME24 sorularını (2024 ABD lise matematik olimpiyatı eleme soruları) dört zorluk katmanına ayırdılar: kolay, orta, zor, en zor.
2. Qwen2.5-32B-Instruct'a 100 ile 20K arası R1 tarzı uzun düşünce iziyle SFT yaptılar.
3. Sonuçları, küçük ve özenle seçilmiş verilerle eğitilmiş s1.1, LIMO, OpenThinker gibi modellerle karşılaştırdılar.

**Sonuç:** Yazarların raporuna göre:
- Orta katman 500–1K izle hızla çözülüyor: 500 izle %82.5, 1K izle %93.4.
- Zor katman logaritmik büyüyor. Yani veri 10 katına çıktıkça kazanç hep aynı küçük miktarda artıyor. 10K izle %52.1; tavan yaklaşık %65.
- En zor katmanda bütün SFT modelleri %0.
- Küçük, özenle seçilmiş set ile rastgele set arasındaki fark küçük. Veri boyutunu artırmak, seçimi iyileştirmekten daha etkili.

**Bizim için:** Kolay ve orta BIRD sorularında az SFT verisi yeter; zor sorulardaki tavanı SFT verisini büyütmek değil, RL ya da handoff çözer.

### Small Models Struggle to Learn from Strong Reasoners (University of Washington, CMU; Şubat 2025) — [2502.12143](https://arxiv.org/abs/2502.12143)
**Soru:** 1 ve 4 (öğrenilebilirlik açığı, uzun ve kısa CoT, büyük model boyutu).

**Tek cümlede:** 3B ve altı modeller en güçlü modelin uzun düşünce izlerinden iyi öğrenemiyor; kısa izler ya da az oranda uzun iz karıştırmak daha iyi.

**Problem:** Sezgi şöyle der: en güçlü modelin en ayrıntılı çözümü en iyi öğretmendir. Yazarlar bunun küçük modeller için geçerli olmadığını gösterdi. Bu duruma "Small Model Learnability Gap" (küçük model öğrenilebilirlik açığı) adını verdiler. Çözüm olarak Mix Distillation'ı önerdiler.

**Ne yaptılar:**
1. Eğitilen modeller: Qwen2.5 0.5B–32B ve Llama 1B–70B. Veri: 7.5K MATH sorusu.
2. İki ekseni ayrı ayrı denediler: uzun CoT ile kısa CoT; büyük kaynak modelin izi ile küçük kaynak modelin izi.
3. Mix Distillation: iki türü karıştırmak. Örneğin "Mix-Long" verisinin 0.2'si (α = 0.2) uzun iz, kalanı kısa iz. "Mix-Large" verisinin 0.2'si büyük modelin izi, kalanı küçük modelin izi.

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-1.5B'de kısa CoT, uzundan 7.1 puan iyi. 32B'de ise uzun CoT 13.7 puan iyi. Yani doğru seçim modelin boyutuna göre tersine dönüyor.
- 0.5B'de büyük kaynağın izi, küçük kaynağınkinden 3.5 puan kötü. 32B'de 6.5 puan iyi. Bu fark izlerin uzunluğundan kaynaklanmıyor.
- Qwen2.5-3B'de Mix-Long 45.9 alıyor; yalnız uzun iz 40.3, yalnız kısa iz 43.4. Mix-Large 45.8. Yani az oranda karıştırmak iki saf seçeneği de geçiyor.

**Bizim için:** 0.8B için en güçlü modelin uzun izleri değil, ağırlıkla kısa ya da orta boy bir modelin (ör. 9B large model) trajectory'leri kullanılmalı; uzun izler küçük bir oranda karıştırılabilir.

## Soru 2: SFT ile RL nasıl birleşir?
SFT modele doğru çözümü gösterir; RL ise modelin kendi denemelerini ödüllendirir. Bu grup, ikisinin hangi sırayla, hangi veriyle ve hangi oranda birleştirileceğine ve birinin ötekini nasıl etkilediğine bakıyor.

### DeReason: A Difficulty-Aware Curriculum Improves Decoupled SFT-then-RL Training for General Reasoning (University of Zurich, HKUST; Mart 2026) — [2603.11193](https://arxiv.org/abs/2603.11193)
**Soru:** 2 ve 3 (veriyi SFT ile RL arasında bölmek).

**Tek cümlede:** Aynı soru havuzunu zorluğa göre bölüp kolay ve bilgi ağırlıklı soruları SFT'ye, akıl yürütme isteyen zor soruları RL'e vermek, iki aşamayı rastgele bölünmüş veriyle yapmaktan daha iyi.

**Problem:** "Önce SFT, sonra RL" yaygın bir reçete. Ama genelde iki aşamaya aynı türden veri verilir ya da veri rastgele bölünür. Oysa SFT bilgi aktarmakta, RL ise zor akıl yürütmeyi geliştirmekte daha iyi olabilir. Yazarlar veriyi bu farka göre bölmenin işe yarayıp yaramadığını sordu.

**Ne yaptılar:**
1. Taban model Qwen3-4B-Base.
2. Veri: WebInstruct-Verified (web'den toplanmış, cevabı doğrulanabilen genel alan soruları) ve WebScale-RL.
3. Qwen3-4B-Instruct her soruyu 1 ile 5 arasında puanladı: soru ne kadar akıl yürütme istiyor? 4–5 alan sorular RL'e, kalanlar SFT'ye gitti.
4. SFT cevapları Qwen3-4B-Instruct-2507'den alındı.
5. RL [GRPO](00_terimler.md#grpo) ile, VeRL kütüphanesinde yapıldı. GRPO, aynı soruya bir grup cevap üretip her cevabı grubun ortalamasına göre ödüllendiren bir RL yöntemidir.

**Sonuç:** Yazarların raporuna göre WebInstruct-Verified ortalamasında:
- Yalnız SFT 41.8, yalnız RL 37.6.
- Rastgele bölünmüş veriyle SFT→RL 42.9.
- Zorluğa göre bölen DeReason 43.8; yani rastgele bölmeden 0.9, yalnız SFT'den 2 puan iyi.
- Base modelden doğrudan RL hem az örnekle verimsiz hem SFT'nin gerisinde. Veri büyüdükçe SFT, RL'i geçiyor.
- Kazanç en çok zor benchmark'larda görülüyor.

**Bizim için:** BIRD train'de small model'in kolay çözdüğü sorular SFT'ye, ara sıra çözdüğü zor sorular RL'e ayrılmalı; aynı soruları iki aşamada tekrar kullanmak yerine.

### On the Interplay of Pre-Training, Mid-Training, and RL on Reasoning Language Models (CMU, Aralık 2025, ICML 2026) — [2512.07783](https://arxiv.org/abs/2512.07783)
**Soru:** 2 ve 3 (RL verisi "yeterlilik sınırında" olmalı).

**Tek cümlede:** RL ancak modelin biraz üstündeki görevlerde ve modelin daha önce az da olsa gördüğü konularda yeni yetenek kazandırıyor; modelin zaten yapabildiği görevlerde yalnız tutarlılığı artırıyor.

**Problem:** Büyük modellerde pre-training, [mid-training](00_terimler.md#mid-training) ve RL'in katkısını birbirinden ayırmak zor. Pre-training verisi bilinmiyor; her şey birbirine karışıyor. Mid-training, pre-training ile post-training arasında, belirli bir alana yönelik ek eğitimdir. Yazarlar her aşamanın verisini tamamen kendileri kontrol edebilecekleri küçük bir düzen kurdu.

**Ne yaptılar:**
1. 100M parametreli küçük modeller kullandılar.
2. Görevler sentetik ve adım adım doğrulanabilir; her adımın doğru olup olmadığı kesin biliniyor.
3. Her aşamada verinin içeriği ve zorluğu ayarlandı. RL verisinin zorluğu, bir bağlamın (ör. bir problem türünün) pre-training'de görülme oranı ve process reward oranı değiştirildi.
4. Process reward, her ara adım için verilen ödüldür; outcome reward ise yalnız son cevaba bakar. (Ayrıntı: [reward model, GRM ve PRM](00_terimler.md#reward-model-grm-ve-prm).)
5. Başarı [pass@k](00_terimler.md#pass-rate-ve-passk) ile ölçüldü. pass@k: modele k deneme hakkı verildiğinde en az birinin doğru olma olasılığı. pass@1 "ilk denemede doğru", pass@128 "128 denemeden en az biri doğru" demek.

**Sonuç:** Yazarların raporuna göre:
- Modelin zaten yaptığı türden (dağılım içi) görevlerde RL yalnız pass@1'i artırıyor, pass@128'i artırmıyor. Yani yeni bir şey öğretmiyor, bildiğini daha tutarlı yaptırıyor.
- Modelin biraz üstündeki görevlerde RL pass@128'i yaklaşık %42'ye kadar artırıyor; burada gerçekten yeni çözümler buluyor.
- Yeni bir bağlamı pre-training'de %0–0.1 oranında görmüş model RL'den aktarım almıyor. %1 görmüş model alıyor: pass@128'de %60'a kadar artış.
- Mid-training + RL, yalnız RL'den en zor görevlerde %10.8 daha iyi.
- Ödül karışımında 0.2 outcome + 0.8 process reward en iyisi.

**Bizim için:** RL'e small model'in pass@1'de kaçırıp pass@k'da çözdüğü BIRD soruları verilmeli; hiç çözemediği sorular önce SFT ile (ya da handoff verisiyle) tanıtılmalı.

*Supervised Reinforcement Learning: From Expert Trajectories to Step-wise Reasoning — Soru 2 (SFT ile RL'i birleştirmek, agent görevleri). Ayrıntısı "Google DeepMind, Meta, Microsoft, Mistral, Apple" bölümünde ([08_google_meta_microsoft_mistral_apple.md](08_google_meta_microsoft_mistral_apple.md)).*

### Towards a Unified View of Large Language Model Post-Training (Tsinghua, Shanghai AI Lab; Eylül 2025) — [2509.04419](https://arxiv.org/abs/2509.04419)
**Soru:** 2 (SFT ile RL'i tek amaçta birleştirmek).

**Tek cümlede:** SFT ve RL aynı formülün iki özel hâli; bu yüzden her soru için "model bunu çözebiliyor mu?" diye bakıp SFT ile RL arasında geçiş yapan basit bir kural (HPT) ikisini de geçiyor.

**Problem:** SFT ve RL genelde iki ayrı aşama olarak, sabit bir sırayla uygulanır. Ama bir soru için doğru tercih modelin o soruyu çözüp çözemediğine bağlı. Model bir soruyu hiç çözemiyorsa RL'in ödüllendirecek bir denemesi yoktur. Çözebiliyorsa, başkasının çözümünü taklit ettirmek gereksizdir.

**Ne yaptılar:**
1. Önce teorik bir sonuç gösterdiler: SFT ve RL, aynı policy gradient tahmincisinin özel durumları. Policy gradient, modelin ağırlıklarını iyi sonuçlu çıktıların olasılığını artıracak yönde güncelleyen formüldür. SFT, bu formülün "çıktı hazır bir gösterim, ödülü hep 1" hâline benziyor.
2. Buna dayanarak Hybrid Post-Training'i (HPT) önerdiler. Her soruda model n tane [rollout](00_terimler.md#rollout) üretiyor (rollout: modelin bir soruya baştan sona ürettiği bir deneme).
3. Doğru rollout oranı P bir eşiğin (γ) üstündeyse o soru için saf RL yapılıyor. Değilse hazır gösterim (doğru çözüm) üzerinde saf SFT yapılıyor.
4. Qwen için γ = 0: yalnız hiç çözülemeyen sorular SFT'ye gidiyor. Llama için γ = 2/8: 8 denemenin en fazla 2'si doğruysa SFT.
5. Modeller: Qwen2.5-Math-7B, Qwen2.5-Math-1.5B, Llama-3.1-8B.

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-Math-7B, AIME24'te: HPT 33.0; LUFFY 26.1, SFT→GRPO 25.7, SRFT 18.4 (LUFFY ve SRFT aşağıda anlatılıyor). Yani en yakın rakipten yaklaşık 7 puan iyi.
- Qwen2.5-Math-1.5B ortalamasında: HPT 41.9; SFT 36.9, LUFFY 34.7, GRPO 34.0. Yani 5 puan ve üstü fark.
- Daha büyük γ (daha çok soruyu SFT'ye göndermek) yardımcı olmuyor: 1.5B'de 39.0 ve 38.7, yani γ = 0'ın altında.

**Bizim için:** Agent loop'unda small model'in hiç çözemediği sorularda large model'in trajectory'siyle SFT, çözebildiklerinde RL yapmak doğrudan uygulanabilir bir kural.

### RL's Razor: Why Online Reinforcement Learning Forgets Less (MIT, Eylül 2025) — [2509.04259](https://arxiv.org/abs/2509.04259)
**Soru:** 2 (SFT'nin unutturması, RL'in korunumu).

**Tek cümlede:** Yeni görevde aynı başarıya ulaşınca RL eski yetenekleri SFT'den çok daha iyi koruyor; ne kadar unutulacağı, modelin başlangıç hâlinden ne kadar uzaklaştığıyla öngörülebiliyor.

**Problem:** Bir modeli yeni bir göreve eğitince eski görevlerde gerileyebilir; buna "unutma" denir. SFT ile RL bu açıdan farklı mı? Farklıysa neden? Bunu bilmek, hangi yöntemin genel yeteneği bozmadan ince ayar yapacağını söyler.

**Ne yaptılar:**
1. Qwen2.5-3B-Instruct'ı üç yeni göreve eğittiler: matematik, bilim soru-cevap ve tool use (ToolAlpaca: araç çağırma görevleri).
2. Aynı deneyi robotik görevlerde ve oyuncak bir MLP'de (küçük, basit bir sinir ağı) de yaptılar.
3. SFT ve RL'i, yeni görevde aynı başarıya ulaştıkları noktada karşılaştırdılar.
4. Unutmayı, yeni görevde eğitilmiş model ile base model arasındaki ileri KL uzaklığıyla ilişkilendirdiler. KL (Kullback–Leibler) uzaklığı, iki modelin çıktı olasılıklarının ne kadar farklı olduğunu ölçer ([KL penalty](00_terimler.md#kl-penalty)).

**Sonuç:** Yazarların raporuna göre:
- Unutma ile ileri KL arasındaki ilişki güçlü: oyuncak deneyde R² = 0.96, LLM'lerde 0.71. R², bir değişkenin ötekini ne kadar açıkladığını gösterir; 1 tam açıklama demek.
- Eğitimden sonra modelin iç temsillerinin base modele benzerliği RL'de 0.94, SFT'de 0.56. Yani RL modelin içini çok daha az değiştiriyor.
- RL'in ürettiği veriyle yapılan SFT, RL'in doğruluk–unutma dengesini yakalıyor. Yani fark algoritmadan değil, verinin modelin kendi çıktısı olmasından geliyor. Buna [on-policy](00_terimler.md#on-policy-ve-off-policy) veri denir: eğitilen modelin kendi ürettiği veri. Başka bir modelin ürettiği veri ise off-policy'dir.

**Bizim için:** SFT verisi small model'in kendi (on-policy) başarılı trajectory'lerinden geldikçe genel yetenek daha az bozulur; large model'in uzak trajectory'leri en çok unutturandır.

### On the Generalization of SFT: A Reinforcement Learning Perspective with Reward Rectification (Southeast University ve diğerleri, UC Merced; Ağustos 2025, ICLR 2026) — [2508.05629](https://arxiv.org/abs/2508.05629)
**Soru:** 2 (SFT'nin genellemesi).

**Tek cümlede:** SFT kaybı, modelin zor bulduğu token'lara aşırı ağırlık veriyor; her token'ın kaybını kendi olasılığıyla çarpan tek satırlık bir düzeltme (DFT) genellemeyi belirgin biçimde artırıyor.

**Problem:** SFT çoğu zaman RL'den kötü genelliyor. Yazarlar nedeni SFT'nin matematiğinde aradı. SFT'nin kaybı her token için −log p'dir (p: modelin doğru token'a verdiği olasılık). Bunun gradyanı 1/p ile büyür. Yani modelin "hiç beklemediği" token'lar çok sert itilir. RL diliyle, SFT örtük bir [reward](00_terimler.md#reward) içerir ve bu reward olasılığı düşük token'lara aşırı ağırlık verir. (Reward: modelin bir çıktısına verilen ödül puanı.)

**Ne yaptılar:**
1. Dynamic Fine-Tuning'i (DFT) önerdiler. Her token'ın kaybı, o token'ın olasılığıyla çarpılıyor. Bu olasılığın gradyanı durduruluyor; yani yalnız bir ağırlık olarak kullanılıyor, kendisi eğitilmiyor.
2. Örnek: normal SFT'de olasılığı 0.01 olan bir token, olasılığı 0.5 olan bir token'a göre yaklaşık 50 kat sert itilir. DFT'de bu fark ortadan kalkar; iki token benzer ağırlık alır.
3. Değişiklik kodda tek satır.
4. Modeller: Qwen2.5-Math-1.5B/7B, Llama-3.2-3B, Llama-3.1-8B. Görevler: matematik, kod ve çok modlu (görsel + metin) görevler.

**Sonuç:** Yazarların raporuna göre beş matematik benchmark'ının ortalamasında:
- Qwen2.5-Math-1.5B: base 15.92, SFT 18.01, DFT 31.58. SFT 2 puan eklerken DFT yaklaşık 15.7 puan ekliyor.
- Qwen2.5-Math-7B: base 21.25, SFT 23.62, DFT 37.15.
- Sınır: bilgi gerektiren bir görevde (Natural Questions: Google aramalarından gelen bilgi soruları) SFT 36.62 alırken DFT 30.14'e düşüyor. Yani modelin bilmediği yeni bilgiyi öğretmekte DFT zayıf.

**Bizim için:** Trajectory SFT'sinde DFT'yi denemek ucuz (MLX'te tek satır), ama şemaya özgü yeni bilgi (sütun adları, değerler) öğretiliyorsa standart SFT kaybı korunmalı.

### SRFT: A Single-Stage Method with Supervised and Reinforcement Fine-Tuning for Reasoning (Institute of Automation CAS, Meituan, SJTU; Haziran 2025) — [2506.19767](https://arxiv.org/abs/2506.19767)
**Soru:** 2 (SFT ve RL'i tek aşamada birleştirmek).

**Tek cümlede:** SFT ve RL kayıplarını aynı anda, modelin o anki belirsizliğine (entropy) göre ağırlıklandırarak uygulamak, iki aşamalı eğitimden ve SFT'siz RL'den daha iyi sonuç veriyor.

**Problem:** SFT modelin çıktı dağılımını geniş çapta değiştirir; RL ise seçici, küçük değişiklikler yapar. İkisini sırayla uygulamak, SFT'nin RL'e zarar verdiği ya da RL'in SFT'nin kazancını sildiği durumlara yol açabilir. Yazarlar ikisini tek aşamada dengelemenin yolunu aradı.

**Ne yaptılar:**
1. Model Qwen2.5-Math-7B.
2. Her adımda iki tür veri birlikte kullanılıyor: hazır gösterimler (doğru çözümler) ve modelin kendi rollout'ları.
3. Gösterimlere SFT kaybı, rollout'lara RL kaybı uygulanıyor.
4. Ağırlıklar [entropy](00_terimler.md#entropy-ve-entropy-collapse)'ye göre ayarlanıyor. Entropy, modelin bir sonraki token'dan ne kadar emin olmadığını ölçer; yüksekse model kararsızdır.
5. SFT ağırlığı 0.5·exp(−H): entropy (H) yükseldikçe SFT'nin etkisi azalıyor. Olumlu RL örneklerinin ağırlığı 0.1·exp(H): entropy yükseldikçe artıyor. Kısacası model kararsızken SFT onu daha az zorluyor.

**Sonuç:** Yazarların raporuna göre:
- Beş matematik benchmark'ında ortalama %59.1.
- Zero-RL yöntemlerinden (SFT'siz, doğrudan base modelden RL) %9.0 iyi.
- Üç alan dışı benchmark'ta %10.9 iyi.
- Ablation: SFT ağırlığını kaldırmak 4.0 puan, RL ağırlığını kaldırmak 2.9 puan kaybettiriyor.

**Bizim için:** İki aşamalı eğitimi kurmak zorsa, tek aşamada entropy ile ağırlıklandırılmış bir SFT+RL kaybı bir seçenek; HPT ile karşılaştırılırsa basit olanı tercih edilmeli.

### Learning What Reinforcement Learning Can't: Interleaved Online Fine-Tuning for Hardest Questions (Peking University, Haziran 2025, ICLR 2026) — [2506.07527](https://arxiv.org/abs/2506.07527)
**Soru:** 2 (iç içe SFT/RL; SFT verisinin oranı).

**Tek cümlede:** RL sırasında modelin hiç çözemediği soruları bir kenara toplayıp ara ara bunların doğru çözümleriyle kısa bir SFT adımı atmak (ReLIFT), gösterim verisinin yalnız %13'üyle hem saf RL'i hem saf SFT'yi geçiyor.

**Problem:** Yazarlar RL'in ağırlıkla modelin zaten yapabildiği soruları iyileştirdiğini gördü. Model bir soruda hiç doğru cevap üretemiyorsa RL'in ödüllendirecek bir şeyi yoktur. SFT ise modelin dışında kalan sorularda ilerleme sağlıyor. İkisini doğru anda birleştirmek gerekiyor.

**Ne yaptılar:** Yönteme ReLIFT diyorlar.
1. Normal RL eğitimi sürüyor.
2. Hiçbir rollout'u doğru olmayan sorular bir buffer'a (bekleme kutusuna) toplanıyor.
3. Buffer, batch boyutu kadar (64 soru) dolunca bu soruların doğrulanmış çözümleriyle bir SFT adımı atılıyor. Sonra RL devam ediyor.
4. Çözümler DeepSeek-R1'den; yalnız cevabı doğru olanlar.
5. Modeller: Qwen2.5-Math-7B (ayrıca 1.5B, Qwen2.5-7B, Llama-3.1-8B).
6. Başarısız denemeler: her RL adımından sonra SFT yapmak (ReLIFT-all) eğitimi çökertti. Sabit olarak her 8 adımda bir SFT yapmak da daha kötü sonuç verdi.

**Sonuç:** Yazarların raporuna göre ortalama doğrulukta:
- ReLIFT 52.6.
- Saf RL 46.9, saf SFT 49.0, SFT→RL 50.8, LUFFY 50.9. Yani en yakın rakipten yaklaşık 1.7 puan, saf RL'den 5.7 puan iyi.
- Gösterim verisinin yalnız %13'ünü kullanıyor.
- Cevap uzunluğu RL'den uzun, SFT'den kısa.

**Bizim için:** Experience log'da small model'in tüm denemelerde kaçırdığı sorular için large model'in doğru trajectory'leri ara ara SFT'ye verilip geri kalan eğitim RL ile yürütülebilir.

### Learning to Reason under Off-Policy Guidance (Shanghai AI Lab, Westlake, Nanjing Univ., CUHK; Nisan 2025) — [2504.14945](https://arxiv.org/abs/2504.14945)
**Soru:** 2 (LUFFY: off-policy rehberlikle RL).

**Tek cümlede:** GRPO'da modelin kendi denemelerinin yanına güçlü bir modelin doğru çözümünü eklemek (LUFFY), modelin hiç çözemediği sorularda da RL'in öğrenmesini sağlıyor.

**Problem:** On-policy RL yalnız modelin kendi ürettiği cevaplardan öğrenir. Model bir sorunun hiçbir denemesinde doğruya ulaşamıyorsa öğrenme sinyali yoktur. Zayıf modeller bu yüzden yalnız kolay sorularda ilerler. Off-policy veri, yani başka bir modelin çözümü, bu açığı kapatabilir. Ama düz taklit yüzeysel kalır ve modelin keşfini öldürebilir.

**Ne yaptılar:**
1. [RLVR](00_terimler.md#rl-ve-rlvr) çerçevesinde çalıştılar (RLVR: ödülün otomatik bir doğrulayıcıdan geldiği RL; ör. cevap doğru mu).
2. Mixed-Policy GRPO: GRPO grubundaki on-policy rollout'ların yanına daha güçlü bir modelin doğrulanmış izleri ekleniyor.
3. İzler DeepSeek-R1'den. OpenR1-Math'ten süzülmüş yaklaşık 45K soru; 8.192 token'dan uzun ve doğrulanmayan izler atıldı.
4. Policy shaping: düzenlenmiş [importance sampling](00_terimler.md#importance-sampling). Importance sampling, başka bir modelden gelen veriyi kendi modelin açısından yeniden ağırlıklandırma yöntemidir. Burada f(x) = x/(x+0.1) dönüşümü kullanılıyor (x: token'ın olasılığı). Bu dönüşüm düşük olasılıklı off-policy token'ları büyütüyor. Örneğin x = 0.01 ise f ≈ 0.09 (yaklaşık 9 kat büyüyor); x = 0.9 ise f = 0.9 (değişmiyor). Böylece model, kendisine yabancı ama önemli adımları göz ardı etmiyor.
5. Modeller: Qwen2.5-Math-7B, 1.5B, Qwen2.5-Instruct-7B, Llama-3.1-8B.

**Sonuç:** Yazarların raporuna göre:
- Dağılım içi (matematik) ortalama 50.1; on-policy RL 45.5.
- Önceki RLVR yöntemlerinden dağılım içinde +6.4, alan dışında +6.2.
- SFT→RL'den dağılım içinde +1.9, alan dışında +16.1; üstelik GPU saatinin yaklaşık %59'uyla.
- Llama-3.1-8B'de on-policy RL yalnız en kolay sorularda öğrenirken LUFFY her zorlukta ilerliyor.
- Policy shaping olmadan entropy hızla çöküyor ([entropy collapse](00_terimler.md#entropy-ve-entropy-collapse): model hep aynı cevabı vermeye başlar ve keşif biter).

**Bizim için:** Small model'in GRPO grubuna large model'in doğru bir trajectory'sini eklemek, 0.8B'nin hiç ödül alamadığı sorularda RL'i çalıştırmanın yolu; ama yeni bir loss terimi eklediği için HPT'den karmaşık.

### SFT or RL? An Early Investigation into Training R1-Like Reasoning Large Vision-Language Models (UC Santa Cruz, Amazon Research, UT Dallas, Penn State; Nisan 2025) — [2504.11468](https://arxiv.org/abs/2504.11468)
**Soru:** 2 (SFT sonraki RL'i nasıl etkiler).

**Tek cümlede:** Görsel-dil modellerinde, uzun ve tereddütlü uzman izlerini taklit ettiren bir SFT, sonraki RL'i iyileştirmek yerine belirgin biçimde kötüleştiriyor.

**Problem:** "Önce SFT ile düşünme biçimini öğret, sonra RL ile geliştir" reçetesi metin modellerinde yaygın. Yazarlar bunun görsel-dil modellerinde (resim ve metni birlikte anlayan modellerde) de işe yarayıp yaramadığını sordu. Özellikle "bekle, bir daha bakayım" gibi tereddütlü ifadeler içeren uzun izleri SFT ile öğretmenin RL'e etkisine baktılar.

**Ne yaptılar:**
1. VLAA-Thinking adlı bir veri seti kurdular: SFT için bir bölüm ve RL için ayrı, zor bir bölüm.
2. Modeller: Qwen2-VL-7B ve Qwen2.5-VL-3B.
3. RL GRPO ile; ödül, algı (resimde doğru şeyi görmek) ve biliş (doğru akıl yürütmek) ödüllerinin karışımı.
4. SFT+GRPO ile yalnız GRPO karşılaştırıldı. SFT verisinin boyutu (5K, 10K) ve "aha" ifadelerini öğretmenin etkisi ayrıca ölçüldü.

**Sonuç:** Yazarların raporuna göre:
- 7B'de (Instruct model) SFT+GRPO ortalaması 19.8, yalnız GRPO 32.5. Yani SFT eklemek sonucu %39 düşürüyor.
- 3B'de 5K SFT örneği bile GRPO'yu ortalama %13.5 düşürüyor. SFT verisini 10K'ya çıkarmak yalnız %0.8 ekliyor.
- "Aha" ifadelerini SFT ile öğretmek modeli base'in altına indiriyor (−%10.5). GRPO bu ifadeleri kendisi buluyor.

**Bizim için:** Small model zaten tool call biçimini biliyorsa, uzun büyük model trajectory'leriyle ağır bir SFT RL'den önce zarar verebilir; SFT yalnız biçimi ve temel davranışı oturtacak kadar kısa tutulmalı.

*SFT Memorizes, RL Generalizes: A Comparative Study of Foundation Model Post-training — Soru 2 (SFT ezber, RL genelleme; SFT'nin RL'den önceki rolü). Ayrıntısı "Google DeepMind, Meta, Microsoft, Mistral, Apple" bölümünde ([08_google_meta_microsoft_mistral_apple.md](08_google_meta_microsoft_mistral_apple.md)).*

## Soru 3: RL verisinin zorluğu ve curriculum
RL'de model her soruya birkaç cevap üretir ve bu pahalıdır. Bu grup, hangi zorluktaki soruların en çok öğrettiğine, işe yaramayacak soruların nasıl önceden atlanacağına ve soruların hangi sırayla verileceğine bakıyor.

### Small Generalizable Prompt Predictive Models Can Steer Efficient RL Post-Training of Large Reasoning Models (Tsinghua, Tencent; Şubat 2026, ICML 2026) — [2602.01970](https://arxiv.org/abs/2602.01970)
**Soru:** 3 (prompt seçimi; rollout'suz zorluk tahmini).

**Tek cümlede:** Her sorunun zorluğunu rollout atmadan tahmin eden küçük bir model (GPS), RL'e orta zorlukta ve çeşitli sorular seçerek eğitimi daha az adımda ve çok daha az rollout'la bitiriyor.

**Problem:** RL'de en çok öğreten sorular orta zorluktakiler. Ama bir sorunun zorluğunu bilmenin olağan yolu, ona birkaç rollout atıp kaçının doğru olduğuna bakmak. Bu da tam kaçınmak istediğimiz maliyet. [Dynamic Sampling](00_terimler.md#dynamic-sampling) gibi yöntemler (hep doğru ya da hep yanlış sonuç veren soruları rollout'tan sonra atmak) sonucu iyileştiriyor ama rollout'u yine harcıyor.

**Ne yaptılar:** Yönteme GPS (Generalizable Predictive Prompt Selection) diyorlar.
1. Küçük, hafif bir generative model, prompt'un zorluğunu tahmin ediyor. Makalenin özetine göre bu tahmin bir Bayesçi çıkarım: model, eldeki kanıtla zorluk hakkındaki inancını güncelliyor.
2. Bu küçük model, RL eğitiminin ortak geçmişinden öğreniyor: hangi sorular daha önce hangi sonucu verdi.
3. Batch seçimi iki ilkeyi birleştiriyor: orta zorluktaki sorulara öncelik vermek ve geçmişe dayalı çeşitlilik (hep aynı tür soruları seçmemek).
4. Deneyler: R1-Distill-1.5B/7B (DeepScaleR verisi, yaklaşık 40K matematik sorusu) ve Qwen3-4B/8B-Base (Countdown: verilen sayılarla dört işlem yapıp hedef sayıya ulaşma oyunu). RL GRPO ile (verl kütüphanesi).
5. Karşılaştırma: uniform (rastgele) seçim, MoPPS, PCL, GRESO ve Dynamic Sampling. (PCL ve GRESO aşağıda anlatılıyor.)

**Sonuç:** Yazarların raporuna göre:
- Uniform seçime göre 1.4–2.0 kat daha az adımda aynı noktaya ulaşıyor. Ortalama doğruluk matematikte +1.6–1.9, mantık görevlerinde +4.1–5.7 puan.
- Dynamic Sampling'e göre %69'a kadar daha az rollout ve %28–47 daha kısa eğitim süresi; doğruluk benzer.
- Test zamanında (eğitimden sonra, model kullanılırken) %36.4'e kadar daha az çıkarım (model çağrısı) gerekiyor; bu, [test-time scaling](00_terimler.md#test-time-scaling) bütçesini zor sorulara ayırmaya yarıyor.

**Bizim için:** Rollout'un pahalı olduğu Mac'te, soruların geçmiş pass rate'lerinden zorluk tahmini yapıp rollout'u yalnız orta zorluktaki sorulara harcamak en büyük tasarruf.

*The Art of Scaling Reinforcement Learning Compute for LLMs — Soru 3 (zero-variance süzgeci, kolay prompt'ların atılması). Ayrıntısı "Google DeepMind, Meta, Microsoft, Mistral, Apple" bölümünde ([08_google_meta_microsoft_mistral_apple.md](08_google_meta_microsoft_mistral_apple.md)).*

### Demystifying Reinforcement Learning in Agentic Reasoning (Princeton, NUS, UIUC; Ekim 2025) — [2510.11701](https://arxiv.org/abs/2510.11701)
**Soru:** 1 ve 3, tool kullanan agent'lar için (gerçek ve sentetik trajectory, çeşitlilik, modele göre veri).

**Tek cümlede:** Tool kullanan agent'larda SFT için gerçek uçtan uca trajectory'ler, RL için modelin pass rate'ine göre süzülmüş çeşitli veri ve birkaç basit RL ayarı, 4B'lik bir modeli 32B'lik rakibin üstüne çıkarıyor.

**Problem:** [Agentic RL](00_terimler.md#agentic-rl-ve-multi-turn), modelin birden çok turda tool çağırıp sonuca bakarak ilerlediği görevlerde RL demek. Burada veri nasıl hazırlanmalı, hangi RL ayarları önemli, model ne sıklıkla tool çağırmalı? Bu sorulara dağınık cevaplar var. Yazarlar bunları kod yorumlayıcı (Python çalıştıran tool) kullanan agent'larda sistematik olarak inceledi.

**Ne yaptılar:**
1. Modeller: Qwen3-4B-Instruct-2507 ve Qwen2.5-7B-Instruct.
2. Önce SFT, ardından GRPO'nun çeşitli biçimleri.
3. SFT verisi için iki seçenek karşılaştırıldı: gerçek uçtan uca tool trajectory'leri (agent gerçekten tool çağırmış, gerçek sonuç almış) ve parçaları sonradan birleştirilmiş sentetik trajectory'ler.
4. Modele göre RL verisi: her soruya 8 rollout atılıyor. %0 ya da %100 çözülen sorular atılıyor (öğretecek bir şeyleri yok). Kalanlar kolay, orta, zor diye bölünüyor.
5. RL ayarları: token düzeyinde loss (kayıp her cevap yerine her token üzerinden ortalanıyor), [clip-higher](00_terimler.md#clip-ve-clip-higher) (olasılığı düşük token'ların daha çok yükselebilmesine izin veren gevşek üst sınır) ve overlong shaping (çok uzun cevaplara kademeli ceza).

**Sonuç:** Yazarların raporuna göre:
- Gerçek trajectory'lerle SFT, sentetik olanlardan çok daha iyi. Qwen3-4B'nin AIME25 average@32'si (32 denemenin ortalama doğruluğu) %3.65'ten %29.79'a çıkıyor.
- Çeşitli RL verisi AIME25'te %50'yi 150 adımda geçiyor; DAPO-Math verisiyle bu 220 adım sürüyor. Çeşitli veri entropy'yi de yüksek tutuyor, yani model keşfetmeyi sürdürüyor.
- Token düzeyinde loss + clip-higher + overlong shaping, GRPO'nun en iyi sonucuna compute'un yaklaşık %25'iyle ulaşıyor.
- Az ama düşünülmüş tool call (çağrıların %70'ten fazlası başarılı), sık ve kısa tool call'dan iyi.
- Sonuç modeli 4B; AIME25'te 70.0 alıyor. 32B'lik ReTool 54.3.

**Bizim için:** SFT için experience log'daki gerçek (uçtan uca, çalışmış) agent trajectory'leri kullanılmalı, elle birleştirilmiş sahte konuşmalar değil; RL havuzu small model'in pass rate'ine göre süzülmeli.

### Prompt Curriculum Learning for Efficient LLM Post-Training (Meta, Cornell; Ekim 2025) — [2510.01135](https://arxiv.org/abs/2510.01135)
**Soru:** 3 (prompt zorluğu, batch boyutu, prompt başına üretim sayısı).

**Tek cümlede:** RL'de en çok öğreten sorular modelin yaklaşık yarısını çözdükleri; PCL bu soruları, modelle birlikte eğitilen bir value model sayesinde rollout atmadan bulup eğitimi 12–17 kat hızlandırıyor.

**Problem:** RL'de iki sorunun cevabı belirsiz: hangi zorlukta sorular seçilmeli ve bir batch nasıl kurulmalı (kaç soru, her soruya kaç cevap)? Ayrıca iyi soruları seçmek için genelde önce rollout atmak gerekiyor, bu da pahalı.

**Ne yaptılar:**
1. Önce batch boyutunun ve prompt zorluğunun etkisini ayrı ayrı ölçtüler.
2. Sonra PCL'i önerdiler. Policy (eğitilen model) ile birlikte bir value model eğitiliyor. Value model, bir prompt'un o anki pass rate'ini tahmin ediyor. Bu tahminle orta zorluktaki prompt'lar rollout atmadan seçiliyor.
3. Modeller: Qwen3-1.7B/4B/8B-Base ve Llama3.2-3B-it. Veri: MATH ve DeepScaleR. 4.096 token bağlam; senkron on-policy eğitim.

**Sonuç:** Yazarların raporuna göre:
- Yaklaşık %50 pass rate'li prompt'lar, en yüksek etkili oranı (öğrenme sinyali veren cevap oranını) ve en büyük gradyan normunu (en güçlü güncellemeyi) veriyor.
- Bu zorlukta prompt başına 16 üretim, başka zorluklardaki 128 üretimi geçiyor.
- %50 prompt'larda 32'den fazla üretim kötüleşiyor; çünkü batch'e daha az farklı prompt sığıyor ve çeşitlilik düşüyor.
- Toplam yaklaşık 8K cevaplık batch (ör. 512 prompt × 16 cevap) en hızlı yakınsıyor.
- PCL, rollout tabanlı süzgeçten MATH'te 12.1, DeepScaleR'da 16.9 kat hızlı. Qwen3-4B'de eğitim 14.0 saat sürüyor; Dynamic Sampling (DS) 37.1, GRPO 29.2 saat.

**Bizim için:** RL'de soru başına az rollout (ör. 8–16) ve pass rate'i yaklaşık 0.5 olan sorular seçilmeli; rollout sayısını artırmak yerine soru sayısını artırmak daha verimli.

### Reasoning with Exploration: An Entropy Perspective (Microsoft Research Asia, Renmin University; Haziran 2025, AAAI 2026) — [2506.14758](https://arxiv.org/abs/2506.14758)
**Soru:** 3 (keşif ve entropy; zor sorularda pass@k).

**Tek cümlede:** Modelin kararsız olduğu (yüksek entropy'li) token'lar keşif anlarına denk geliyor; advantage'a entropy'ye dayalı küçük bir terim eklemek, özellikle pass@k'yı belirgin biçimde artırıyor.

**Problem:** RL ilerledikçe model emin olduğu tek bir çözüm yoluna kilitlenir. pass@1 artar ama farklı çözüm denemesi azalır; zor sorularda pass@k düşer. Keşfi korumak gerekiyor ama eğitimi bozmadan.

**Ne yaptılar:**
1. Önce yüksek entropy'li token'ların neye karşılık geldiğine baktılar. Bunlar keşif davranışlarıyla örtüşüyor: bağlayıcı token'lar (ör. "ama", "öyleyse"), kendini doğrulama ve nadir davranışlar.
2. [Advantage](00_terimler.md#advantage)'a küçük bir ek terim koydular. Advantage, bir cevabın ortalamadan ne kadar iyi olduğunu söyleyen sayıdır; RL güncellemesinin yönünü ve gücünü belirler.
3. Ek terim: entropy × α. Ama bu terim advantage'ın mutlak değerinin yarısını (κ = 2) geçemiyor. α, GRPO'da 0.4, [PPO](00_terimler.md#ppo)'da 0.1 (PPO: ayrı bir value model kullanan klasik RL yöntemi).
4. Entropy'nin gradyanı durduruluyor; yani entropy advantage'ı büyüten bir sayı olarak giriyor, kendisi üzerinden ayrıca gradyan akmıyor. Sınır sayesinde terim negatif bir advantage'ı pozitife çeviremiyor; kötü cevap kötü kalıyor.
5. Modeller: Qwen2.5-Base-7B ve Qwen2.5-Math-7B.

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-Base, GRPO: AIME24 Pass@256 46.7'den 56.7'ye (+10 puan). MATH500 (500 soruluk MATH alt kümesi) Pass@1 55.3'ten 58.5'e.
- PPO ile: AIME25 Pass@256 43.3'ten 56.7'ye.
- Bir yerde gerileme var: Qwen2.5-Math'te AIME24 Pass@256 83.3'ten 80.0'a düşüyor.

**Bizim için:** Small model RL'de tek bir SQL kalıbına kilitlenirse bu tek satırlık advantage terimi keşfi korumanın ucuz yolu; ama önce sıcaklık/entropy izlenmeli.

### Act Only When It Pays: Efficient Reinforcement Learning for LLM Reasoning via Selective Rollouts (CMU, LLNL, UIUC, Meta; Haziran 2025) — [2506.02177](https://arxiv.org/abs/2506.02177)
**Soru:** 3 (online süzgeç; zero-variance prompt'ları rollout'tan önce atlamak).

**Tek cümlede:** Bir epoch'ta öğrenme sinyali vermeyen sorular sonraki epoch'larda da büyük ölçüde öyle kalıyor; GRESO bunları rollout atmadan olasılıkla atlayıp eğitimi 2 kata kadar hızlandırıyor.

**Problem:** GRPO'da bir sorunun bütün rollout'ları aynı ödülü alırsa (hepsi doğru ya da hepsi yanlış) advantage sıfır olur. Bu sorular hiçbir şey öğretmez; bunlara "zero-variance" (ödülleri arasında hiç fark olmayan) prompt denir. Dynamic Sampling bunları rollout'tan sonra atar, ama rollout zaten harcanmıştır.

**Ne yaptılar:** Yönteme GRESO diyorlar.
1. Önce bir gözlem yaptılar: bir epoch'ta zero-variance olan prompt, sonraki epoch'larda da büyük olasılıkla zero-variance kalıyor.
2. Her prompt'un art arda kaç kez zero-variance olduğu tutuluyor. Bu sayı arttıkça prompt'un atlanma olasılığı artıyor.
3. Atlanan prompt'lar ara ara yeniden deneniyor; model değiştikçe bir soru yeniden öğretici olabilir.
4. Batch'teki zero-variance oranı yaklaşık %25'te tutuluyor.
5. Modeller: Qwen2.5-Math-1.5B, R1-Distill-Qwen-1.5B, Qwen2.5-Math-7B.

Örnek: bir soru üç epoch boyunca 8 denemenin 8'inde de doğru çözüldüyse, dördüncü epoch'ta büyük olasılıkla atlanıyor; arada bir yine deneniyor.

**Sonuç:** Yazarların raporuna göre:
- Rollout süresinde 2.4 kata, toplam eğitimde 2.0 kata kadar hızlanma; doğruluk kaybı yok.
- Qwen2.5-Math-7B'de rollout sayısı 13.1M'den 6.3M'ye iniyor, yani yarıdan fazla azalıyor. Ortalama doğruluk %57.5; Dynamic Sampling %57.8. Fark 0.3 puan.

**Bizim için:** Experience log zaten soru başına geçmiş sonuçları tutuyor; art arda hep çözülen ya da hiç çözülemeyen soruları RL'de seyrek örneklemek Mac'teki rollout süresini yarıya indirebilir.

### The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning (Princeton, University of Virginia; Haziran 2025, NeurIPS 2025) — [2506.01347](https://arxiv.org/abs/2506.01347)
**Soru:** 3 (öğrenme sinyali nereden gelir: doğru ve yanlış örnekler).

**Tek cümlede:** RLVR'da yalnız yanlış cevapları cezalandırmak bile modeli her k değerinde base'in üstüne çıkarıyor; doğru cevapları ödüllendirmek ise pass@1'i artırırken çeşitliliği öldürüyor.

**Problem:** RLVR iki şey yapar: doğru cevapların olasılığını artırır, yanlışların olasılığını azaltır. Bu iki parçanın her birinin ne katkı verdiği bilinmiyordu. Yazarlar ikisini ayırıp tek tek ölçtü.

**Ne yaptılar:**
1. Sinyali ikiye ayırdılar. PSR (Positive Sample Reinforcement): yalnız doğru cevabı güçlendirmek. NSR (Negative Sample Reinforcement): yalnız yanlış cevabı cezalandırmak.
2. Her birini ayrı ayrı eğitip pass@k'yı k = 256'ya kadar ölçtüler.
3. Sonra Weighted-REINFORCE'u önerdiler. REINFORCE, en basit policy gradient yöntemidir. Burada olumlu terim λ = 0.1 ile küçültülüyor; yani doğru cevaplar yanlış cevaplara göre on kat daha az ağırlık alıyor.
4. Modeller: Qwen2.5-Math-7B, Qwen3-4B (non-thinking; [thinking mode](00_terimler.md#thinking-mode) kapalı, yani model cevaptan önce uzun düşünce yazmıyor), Llama-3.1-8B-Instruct.

**Sonuç:** Yazarların raporuna göre:
- Yalnız NSR, bütün pass@k aralığında base'i geçiyor. Yalnız PSR pass@1'i artırıyor ama yüksek k'da çeşitliliği öldürüyor.
- Qwen2.5-Math-7B, AIME25: Weighted-REINFORCE pass@1'de 10.6 (PPO 8.5, GRPO 10.3). pass@256'da 56.7 (PPO 43.3, GRPO 50.0). Yani pass@1'de eşit ya da biraz iyi, pass@256'da 6.7–13.4 puan iyi.
- MATH ve AMC23'te PPO/GRPO ile eşit ya da üstün.

**Bizim için:** Final check'te reddedilen SQL'ler de değerli bir RL sinyali; olumlu örneklerin ağırlığını düşürmek, small model'in çeşitli SQL denemelerini (dolayısıyla pass@k'yı) korur.

### Self-Evolving Curriculum for LLM Reasoning (Mila, ServiceNow AI Research; Mayıs 2025) — [2505.14970](https://arxiv.org/abs/2505.14970)
**Soru:** 3 (öğrenilen curriculum).

**Tek cümlede:** Hangi soru türünün ne zaman verileceğini elle sabitlemek yerine, eğitim sırasında "şu an en çok hangi türden öğreniyorum?" diye bakan bir bandit'e seçtirmek (SEC), sabit kolaydan zora sıralamadan ve çoğu zaman rastgeleden iyi.

**Problem:** Klasik curriculum soruları kolaydan zora sıralar. Ama hangi sıranın en iyi olduğu modele ve göreve göre değişir; model ilerledikçe de değişir. Sıra sabit olunca model artık öğrenmediği kolay sorularda vakit kaybedebilir.

**Ne yaptılar:** Yönteme SEC diyorlar.
1. Sorular kategorilere ayrıldı: zorluk seviyesi ya da problem türü.
2. Kategori seçimi bir non-stationary multi-armed bandit olarak kuruldu. Multi-armed bandit, birkaç kol arasından en çok kazandıranı denerek bulmaya çalışan bir seçim problemidir (kumar makinesi kollarını düşünün). Non-stationary, kolların değerinin zamanla değiştiği anlamına gelir.
3. Her kategorinin "ödülü", o kategorideki soruların ortalama mutlak advantage'ı. Bu, modelin o kategoriden şu an ne kadar öğrendiğinin yaklaşık bir ölçüsü.
4. Kategorilerin değeri TD(0) ile güncelleniyor: her adımda eski değer, son gözlenen ödüle doğru biraz kaydırılıyor.
5. Modeller: Qwen2.5-3B ve 7B (Countdown için Llama-3.2-1B). Görevler: planlama (Countdown; Zebra: mantık bulmacaları), tümevarım (ARC-1D: tek boyutlu desen tamamlama bulmacaları) ve matematik.
6. Karşılaştırma: rastgele seçim ve sabit kolaydan zora sıralı curriculum.

**Sonuç:** Yazarların raporuna göre (değerler 0–1 arası doğruluk):
- Qwen2.5-3B, alan dışı testlerde: Countdown 0.542 (rastgele 0.479, sabit sıralı 0.321). Zebra 0.345 (rastgele 0.285). AIME24 0.100 (rastgele 0.075).
- 7B'de kazanç karışık: Countdown ve ARC'de rastgeleden biraz düşük; AIME24'te 0.175'e karşı 0.138 ile önde.
- Sabit kolaydan zora sıralama rastgeleden kötü.

**Bizim için:** BIRD'de veritabanı ya da zorluk kategorisi başına ortalama |advantage|'ı izleyip örneklemeyi ona göre kaydırmak basit bir bandit ile yapılabilir; sabit kolaydan zora sıralama önerilmez.

### Efficient Reinforcement Finetuning via Adaptive Curriculum Learning (USC, University of Maryland; Nisan 2025) — [2504.05520](https://arxiv.org/abs/2504.05520)
**Soru:** 3 (uyarlanır zorluk curriculum'u).

**Tek cümlede:** AdaRFT, modelin ortalama ödülünü 0.5 civarında tutacak şekilde soru zorluğunu her adımda ayarlayan tek formüllük bir curriculum; eğitimi 2 kata kadar kısaltıyor.

**Problem:** Veri seti çoğu zaman dengesizdir: ya çok kolay ya çok zor sorular ağır basar. Kolay sorular modele bir şey öğretmez; çok zorlar hiç ödül vermez. Modelin seviyesi de eğitim boyunca değişir. Soru zorluğunu modelin o anki seviyesine göre otomatik ayarlamak gerekiyor.

**Ne yaptılar:** Yönteme AdaRFT diyorlar.
1. Her sorunun zorluğu önceden (offline) hesaplandı: Qwen2.5-Math-7B'ye her soru için 128 rollout attırıldı; başarısızlık oranı zorluk sayıldı.
2. Bir hedef zorluk T tutuluyor. Her adımda zorluğu T'ye en yakın sorularla eğitiliyor.
3. T, son batch'in ortalama ödülüne göre güncelleniyor. Hedef ödül β = 0.5. Ortalama ödül 0.5'in üstündeyse (model kolay buluyor) T artırılıyor, altındaysa azaltılıyor. Artışın büyüklüğü tanh ile yumuşatılıyor (çok büyük sıçrama olmuyor) ve T izin verilen aralığın içinde kırpılıyor.
4. Örnek: son batch'te model soruların %80'ini çözdüyse, sonraki batch daha zor sorulardan seçilir. %20'sini çözdüyse daha kolaylardan.
5. RL PPO ile. Modeller: Qwen2.5-Math-1.5B ve Qwen2.5-7B. Veri: DeepScaleR'dan 10K'lık üç set: uniform (dengeli), kolaya kaymış, zora kaymış.

**Sonuç:** Yazarların raporuna göre:
- Eğitim süresinde 2 kata kadar azalma.
- 1.5B ortalaması: zora kaymış veride 37.41'den 40.48'e, uniform veride 37.20'den 41.11'e (yaklaşık 3–4 puan kazanç).
- Kazanç en çok dengesiz veride ve küçük modelde. Model güçlüyse ya da veri dengeliyse kazanç azalıyor.

**Bizim için:** Elimizdeki BIRD train dengesiz olduğu için, small model'in ortalama ödülünü yaklaşık 0.5'te tutan bu tek formüllük curriculum 0.8B için ucuz ve etkili bir başlangıç.

### LIMR: Less is More for RL Scaling (SJTU GAIR, Şubat 2025) — [2502.11886](https://arxiv.org/abs/2502.11886)
**Soru:** 3 (küçük RL verisi; öğrenme etkisi ölçümü).

**Tek cümlede:** RL verisini, her sorunun ödül eğrisinin modelin genel öğrenme eğrisine ne kadar benzediğine göre seçmek, verinin yalnız %16'sıyla tam veriye eşit ya da daha iyi sonuç veriyor.

**Problem:** RL verisini büyütmek hep daha iyi mi? Çok soru, çok rollout ve çok compute demek. Bazı soruların öğretici, bazılarının gürültü olduğu düşünülebilir. Öğretici olanları ayırmanın bir yolu gerekiyor.

**Ne yaptılar:**
1. Learning Impact Measurement (LIM) adını verdikleri bir ölçüt tanımladılar. Önce bütün veriyle RL yapılıyor; her sorunun epoch'lar boyunca aldığı ödül kaydediliyor.
2. Her sorunun ödül eğrisi, modelin ortalama öğrenme eğrisiyle karşılaştırılıyor. Eğrisi ortalamaya benzeyen soru, modelin genel öğrenmesiyle birlikte ilerleyen, yani öğretici bir soru sayılıyor.
3. Örnek: bir sorunun ödülü eğitim boyunca 0'dan 1'e, modelin genel başarısıyla aynı hızda çıkıyorsa skoru yüksek. Baştan hep 1 olan ya da hep 0 kalan sorunun skoru düşük.
4. LIM skoru 0.6'nın üstündeki sorular tutuluyor: 8.523 sorudan 1.389'u.
5. Qwen2.5-Math-7B base modelinden PPO ile (OpenRLHF kütüphanesi), prompt başına 8 rollout.

**Sonuç:** Yazarların raporuna göre (tam veri / rastgele 1.389 soru / LIMR):
- AIME24: 32.5 / 25.8 / 32.5.
- MATH500: 76.6 / 66.0 / 78.0.
- AMC23: 61.9 / 56.3 / 63.8.
- Yani aynı boyutta rastgele seçim 5–12 puan geride kalıyor. LIMR verinin yaklaşık %16'sıyla tam veriye eşit ya da üstün.
- 7B'de LIMO ve s1 tarzı az veriyle SFT'den de iyi.

**Bizim için:** Kısa bir ön RL koşusunun ödül eğrilerinden "öğrenen" soruları seçip asıl RL'i yalnız onlarla yapmak, sınırlı compute'ta BIRD train'in tamamını kullanmaktan verimli olabilir.

## Soru 4: Distillation ayrıntıları
Distillation'da büyük modelin bilgisi küçük modele aktarılır. Bu grup, özellikle on-policy distillation'ın ne zaman işlediğine ve hangi büyük modelin seçilmesi gerektiğine bakıyor.

*SOD: Step-wise On-policy Distillation for Small Language Model Agents — Soru 4 (tool kullanan küçük agent'larda on-policy distillation). Ayrıntısı "Agentic, tool-use ve Text-to-SQL post-training" bölümünde ([11_agentic_text_to_sql.md](11_agentic_text_to_sql.md)).*

### Rethinking On-Policy Distillation of Large Language Models: Phenomenology, Mechanism, and Recipe (Tsinghua, ShanghaiTech, UIUC, RUC; Nisan 2026) — [2604.13016](https://arxiv.org/abs/2604.13016)
**Soru:** 4 (on-policy distillation ne zaman işler; hangi büyük model seçilmeli).

**Tek cümlede:** On-policy distillation'da büyük modelin puanından çok, eğitilen modelle düşünme biçiminin ne kadar örtüştüğü önemli; daha güçlü bir büyük model her zaman daha iyi öğretmen değil.

**Problem:** [On-policy distillation](00_terimler.md#on-policy-distillation-opd) (OPD) şöyle işler: eğitilen model kendi cevabını üretir; büyük model bu cevabın her token'ı için "ben burada hangi olasılıkları verirdim" der; eğitilen model büyük modelin olasılıklarına yaklaşacak şekilde güncellenir. OPD bazen çok iyi, bazen hiç işlemiyor. Hangi koşullarda başarılı olduğu belli değildi.

**Ne yaptılar:**
1. Kontrollü deneyler kurdular. Birinci düzen: eğitilen model Qwen3-1.7B-Base, büyük modeller farklı yollarla eğitilmiş Qwen3-4B'ler.
2. İkinci düzen: eğitilen model R1-Distill-1.5B; büyük modeller JustRL-1.5B ve R1-Distill-7B.
3. Veri DAPO-Math-17K (17K matematik sorusu). Değerlendirme AIME24/25 ve AMC23.
4. Başarının mekanizmasını anlamak için, iki modelin her konumda en olası gördüğü token'ların ne kadar örtüştüğünü izlediler.
5. Ayrıca şunları değiştirdiler: OPD'den önce bir SFT olup olmaması, cevap uzunluğu ve kayıbın biçimi (yalnız örneklenen token, en olası k token ya da yalnız en olası tek token).

**Sonuç:** Yazarların raporuna göre:
- Düşünme kalıbı uyumu, büyük modelin puanından önemli. Aynı doğrulukta iki Qwen3-4B'den GRPO ile eğitilmiş olanı eğitilen modelle daha çok örtüşüyor ve daha iyi aktarıyor.
- Daha güçlü 7B büyük model, 1.5B'yi daha iyi yapmıyor.
- Başarılı OPD'de en olası token örtüşmesi yaklaşık %72'den %91'in üstüne çıkıyor. Öğrenme sinyali neredeyse tamamen zaten örtüşen token'lardan geliyor.
- OPD'den önce büyük modelin rollout'larıyla SFT yapmak ([cold start](00_terimler.md#cold-start); burada off-policy veriyle başlangıç eğitimi) daha iyi sonuç veriyor.
- 3K–7K token'lık cevaplar en iyisi. 10K–15K'da eğitim geç bir aşamada çöküyor.
- Yalnız örneklenen token'la OPD, neredeyse top-k kadar iyi. Yalnız en olası token'a (top-1) bakmak kötü.

**Bizim için:** Large model olarak small model ile aynı aileden ve aynı konuşma biçimini kullanan (Qwen3.5) bir model seçmek doğru; önce kısa bir SFT, sonra OPD sırası izlenmeli.

### Self-Distilled Reasoner: On-Policy Self-Distillation for Large Language Models (UCLA, Meta Superintelligence Labs, HKU; Ocak 2026, ICML 2026) — [2601.18734](https://arxiv.org/abs/2601.18734)
**Soru:** 4 (ayrı bir büyük model olmadan on-policy distillation).

**Tek cümlede:** Aynı modelin referans çözümü gören hâlini rehber, yalnız soruyu gören hâlini eğitilen model yapan on-policy self-distillation (OPSD), GRPO'ya yakın sonuç veriyor ve çok daha az token harcıyor; ama küçük modelde zayıf.

**Problem:** OPD için ayrı ve güçlü bir büyük model gerekir; onu çalıştırmak pahalıdır. Yazarlar şunu sordu: model, doğru çözümü bağlamında gördüğünde kendi kendine rehber olabilir mi? Olabilirse ayrı bir büyük modele gerek kalmaz.

**Ne yaptılar:** Yönteme OPSD diyorlar.
1. Aynı model iki bağlamda kullanılıyor. Rehber hâli soruyla birlikte referans çözümü de görüyor. Eğitilen hâli yalnız soruyu görüyor.
2. Eğitilen hâl kendi rollout'unu üretiyor. Her token'da iki hâlin olasılıkları arasındaki JSD küçültülüyor. JSD (Jensen–Shannon divergence), iki olasılık dağılımının ne kadar farklı olduğunu ölçen simetrik bir uzaklıktır.
3. Modeller: Qwen3 1.7B/4B/8B. Veri: OpenThoughts matematik alt kümesinden en fazla 30K soru.
4. Soru başına tek rollout, 1.024 token sınırı. Eğitim [LoRA](00_terimler.md#lora) ile (LoRA: modelin tamamı yerine küçük ek matrisleri eğiten ucuz ince ayar yöntemi).
5. Karşılaştırma: aynı veride SFT ve GRPO (soru başına 8 rollout, 16K token).

**Sonuç:** Yazarların raporuna göre dört benchmark ortalaması (base / SFT / GRPO / OPSD):
- 8B: 50.0 / 50.0 / 51.3 / 52.2.
- 4B: 48.3 / 49.6 / 49.6 / 50.4.
- 1.7B: 28.8 / 28.0 / 30.5 / 30.0.
- 4B'de GRPO'dan 8–12 kat daha az token'la eğitiliyor.
- Yazarlar kazancın küçük olduğunu (base'e göre yaklaşık 1–2 puan) ve 1.7B'de GRPO'nun gerisinde kaldığını belirtiyor. Modelin referans çözümü anlayacak kapasitesi olması gerekiyor.

**Bizim için:** Gold SQL'i gören small model'i rehber yapmak ucuz bir seçenek gibi görünse de 0.8B kapasitede işe yaraması beklenmez; 4B'ye geçince denenebilir.

*Distillation Scaling Laws — Soru 4 (distillation'da ölçekleme; büyük modelin boyutu). Ayrıntısı "Google DeepMind, Meta, Microsoft, Mistral, Apple" bölümünde ([08_google_meta_microsoft_mistral_apple.md](08_google_meta_microsoft_mistral_apple.md)).*

## Soru 5: Birden çok büyük modelden ya da domain expert'ten öğrenme
Bazen tek bir büyük model yerine birkaç kaynak vardır: farklı büyük modeller ya da her biri bir alanda RL ile eğitilmiş domain expert'ler. Bu grup, bunları tek modelde toplamanın yollarını (birden çok kaynaktan distillation, multi-teacher on-policy distillation, model merging) ve bunların tek bir karışık RL ile karşılaştırmasını inceliyor.

### Who Teaches Which Token? Verifier-Gated Multi-Expert On-Policy Distillation for Scientific Reasoning (Fudan, HKUST; Eylül 2026) — [2609.15404](https://arxiv.org/abs/2609.15404)
**Soru:** 5 (multi-teacher on-policy distillation; token düzeyinde expert seçimi).

**Tek cümlede:** Birden çok expert'ten on-policy distillation yaparken her token'a eşit ağırlık vermek israf; bir verifier'ın hangi expert'in hangi token'ı gerçekten düzeltebileceğine karar verdiği VG-OPD, hem GRPO'yu hem düz distillation'ı geçiyor.

**Problem:** [Multi-teacher OPD](00_terimler.md#multi-teacher-distillation-mopd) (MOPD), birkaç domain expert'in bilgisini on-policy distillation ile tek modele aktarır. Olağan yöntem her prompt'u tek bir expert'e yönlendirir ve cevabın bütün token'larına eşit ağırlık verir. Yazarlar yararlı sinyalin seyrek olduğunu gösterdi: token'ların çoğunda expert yeni bir şey söylemiyor. Bütün token'lara eşit ağırlık vermek gürültü ekliyor.

**Ne yaptılar:** Yönteme VG-OPD (verifier-gated, yani verifier kapılı OPD) diyorlar.
1. Ortak bir taban üzerinde, her biri bir bilim alanında RL ile eğitilmiş dört LoRA expert hazırlandı (rank 64; LoRA'nın boyutu).
2. Eğitilen modeller: Qwen3-4B ve 8B (non-thinking).
3. Bir verifier, her token için hangi expert'in o token'ı "öğretebileceğine" karar veriyor. İki şeye bakıyor: expert'in cevap ölçütünde sağladığı karşı-olgusal kazanç (expert'in önerisi izlenseydi cevap ne kadar iyileşirdi) ve expert ile eğitilen modelin o token'da ne kadar anlaşmadığı.
4. Yalnız kapıdan geçen token'larda expert ile eğitilen model arasındaki KL uzaklığı hesaplanıyor. Bu kapılı KL, GRPO'ya token düzeyinde ek bir advantage olarak giriyor.
5. Değerlendirme: yedi bilimsel akıl yürütme benchmark'ı.

**Sonuç:** Yazarların raporuna göre:
- 4B'de GPQA-Diamond 46.3 (GRPO 43.9, MOPD 43.8). ChemBench (kimya bilgi ve akıl yürütme testi) 66.4 (GRPO 61.2, MOPD 63.1).
- İki model boyutunda da yedi benchmark'ın beşinde birinci.
- Ablation: GRPO'nun içine kapısız, yoğun (her token'da) distillation eklemek sonucu yalnız RL'in altına düşürüyor. GRPO+MOPD 50.1, GRPO+OPSD 51.6, yalnız RL 53.0, VG-OPD 55.0.
- Distillation sinyalini rastgele token'lara koymak en zararlı değişiklik (−6.3 puan).

**Bizim için:** Large model'in logit rehberliği her token'a değil, yalnız small model'in yanlış yaptığı ve large model'in düzeltebildiği kısımlara (ör. hatalı `execute_sql` argument'ı) verilmeli; ayrım gözetmeyen distillation RL'i bozabilir.

### Consolidating RLVR Capabilities Across Domains: A Deep Dive into Fusion Paradigms (Tencent, Fudan; Ağustos 2026) — [2608.27409](https://arxiv.org/abs/2608.27409)
**Soru:** 5 (merge, karışık multi-domain RL ve MOPD'nin aynı expert'ler ve veriyle karşılaştırılması).

**Tek cümlede:** Domain expert'leri tek modelde toplamanın üç yolu (merge, karışık RL, MOPD) ortalamada en fazla 1.4 puan farklı; aralarındaki asıl fark maliyette.

**Problem:** Her alan için ayrı RLVR ile eğitilmiş expert'ler varsa, bunları tek bir modelde toplamak gerekir. Üç yaygın yol var ama bunlar hiç aynı koşullarda karşılaştırılmamıştı. Hangisinin ne zaman seçileceği belirsizdi.

**Ne yaptılar:**
1. Modeller: Qwen3-4B-Instruct-2507 ve Qwen3-8B. Domain'ler: matematik, bilim, kod, instruction following (talimatlara uyma) ve agent.
2. Her domain için ayrı RLVR ile bir expert eğitildi.
3. Üç birleştirme yolu karşılaştırıldı:
   - **Merge:** expert'lerin ağırlıklarını birleştirmek ([model merging](00_terimler.md#model-merging)). Task Arithmetic kullanıldı: her expert'in base'den farkı (task vector) alınıp λ = 0.6 ile ölçeklenerek base'e ekleniyor. TIES (çakışan değişiklikleri ayıklayan bir merge yöntemi) 8B'de daha kötü: 49'a karşı 53.7.
   - **Mix RL:** bütün domain'lerin verisiyle tek bir RL.
   - **MOPD:** expert'leri multi-teacher on-policy distillation ile eğitilen modele aktarmak.

**Sonuç:** Yazarların raporuna göre:
- Ortalamalar en fazla 1.4 puan farklı. 4B'de: domain RL (her alan kendi expert'i) 63.88, Merge 63.7, Mix RL 62.26, MOPD 63.31. Tek bir benchmark'ta ise fark 8.6 puana çıkıyor.
- Maliyet (domain RL = 1.00 kabul edilerek): Mix RL 0.58–0.67 kat, Merge yaklaşık 0 (expert'ler zaten varsa), MOPD toplamda 1.14–1.19 kat.
- Üçü de pass@1'i artırıyor; ama pass@32'de AIME'de base'den ayırt edilemiyor. Yani modelin çözebildiği soru kümesini genişletmiyor, yalnız ilk denemede bulma olasılığını artırıyor.
- Öneri: expert'ler zaten varsa Merge; yoksa domain oranları ayarlanmış Mix RL; domain kazancını korumak öncelikliyse MOPD.

**Bizim için:** Tek görevli (Text-to-SQL) bir agent için ayrı expert'ler eğitmek gereksiz; tek bir RL koşusu hem en ucuz hem yeterli. Merge yalnız ayrı denemeler (ör. iki farklı veriyle eğitilmiş LoRA'lar) elde varsa bedava bir seçenek.

### MOPD: Multi-Teacher On-Policy Distillation for Capability Integration in LLM Post-Training (Xiaomi, Peking University; Haziran 2026) — [2606.30406](https://arxiv.org/abs/2606.30406)
**Soru:** 5 (domain expert'leri on-policy distillation ile tek modele toplamak).

**Tek cümlede:** Önce her domain için paralel olarak ayrı bir RL expert'i eğitip sonra hepsini on-policy distillation ile tek modele aktarmak (MOPD), expert ile başlangıç modeli arasındaki farkın %91–95'ini kapatıyor ve diğer birleştirme yollarını geçiyor.

**Problem:** Tek bir RL ile bütün domain'leri birlikte eğitmek, domain'ler arasında çekişme yaratabilir. Ayrı expert'leri merge etmek ise ağırlıklar uyuşmadığında kayıp verir. Yazarlar expert'lerin bilgisini, eğitilen modelin kendi cevapları üzerinden aktarmanın daha iyi olup olmadığını sordu.

**Ne yaptılar:**
1. Taban: Qwen3-30B-A3B-Base üzerine genel bir SFT. Bu bir [MoE](00_terimler.md#moe) modeli (mixture of experts: 30B parametre var, ama her token'da yalnız yaklaşık 3B'si çalışıyor).
2. Aynı SFT checkpoint'inden her domain için ayrı bir RL expert eğitildi (paralel). Domain'ler: matematik, instruction following, yazılım mühendisliği.
3. Eğitilen model kendi rollout'larını üretiyor. Her rollout, domain'ine göre ilgili expert'e yönlendiriliyor.
4. Expert, token düzeyinde reverse KL ile distill ediliyor. Pratikte: expert'in log-olasılığı ile eğitilen modelin log-olasılığı arasındaki fark, o token'ın advantage'ı oluyor; ±5 ile kırpılıyor. Örneğin expert bir token'ı eğitilen modelden çok daha olası buluyorsa o token güçlendiriliyor.
5. Ayrıca top-k (k = 64) biçimi denendi: yalnız seçilen token yerine en olası 64 token'ın dağılımı eşleştiriliyor.
6. Yöntem MiMo-V2-Flash'in post-training'inde kullanılmış.

**Sonuç:** Yazarların raporuna göre normalize skor şöyle tanımlanıyor: 0 = başlangıçtaki SFT modeli, 1 = o domain'in expert'i.
- MOPD 0.937.
- Mix-RL 0.882, Param-Merge (Task Arithmetic) 0.857, Off-Policy Finetune (expert çıktılarıyla SFT) 0.824, Cascade RL (domain'leri sırayla RL) 0.775, basit ağırlık ortalaması 0.328.
- Her domain'de expert ile aradaki farkın %91–95'i kapanıyor.

**Bizim için:** Bizde tek domain olduğu için doğrudan gerekmez; ama "önce ayrı RL, sonra OPD" sırası, ileride farklı SQL lehçeleri ya da veritabanı türleri için ayrı LoRA expert'leri birleştirmenin en güçlü yolu.

### To Mix or To Merge: Toward Multi-Domain Reinforcement Learning for Large Language Models (Peking University, Samsung Research; Şubat 2026, COLM 2026) — [2602.12566](https://arxiv.org/abs/2602.12566)
**Soru:** 5 (karışık multi-domain RL ile domain başına RL + merge).

**Tek cümlede:** Bütün domain'leri tek bir karışık RL ile eğitmek, ayrı ayrı RL yapıp birleştirmekle aynı sonucu daha ucuza veriyor; ama agent becerisi diğer domain'lerden aktarılmıyor.

**Problem:** Birden çok domain için iki yol var: hepsini tek RL'de karıştırmak ya da her birini ayrı RL ile eğitip sonra merge etmek. Karıştırınca domain'ler birbirini bozar mı? Ayrı eğitince maliyet ne kadar artar? Ayrıca bir domain'deki RL diğerine yardım eder mi?

**Ne yaptılar:**
1. Model: Qwen3-4B-Base; yaklaşık 14M örnekle SFT, ardından GRPO.
2. Domain'ler: matematik, kod, bilim, instruction following ve agent.
3. Karşılaştırılanlar: tek karışık RLVR; ayrı RLVR'ların farklı merge yöntemleriyle birleştirilmesi (ortalama, task arithmetic, TIES, SCE; DARE'li ve DARE'siz); MT-OPD (multi-teacher on-policy distillation). DARE, birleştirmeden önce her expert'in değişikliklerinin bir kısmını rastgele atıp kalanı büyüten bir yöntem.
4. Ayrıca her domain'in ağırlıkta hangi parametreleri değiştirdiğine (ağırlık değişim maskelerine) ve bunların ne kadar örtüştüğüne baktılar.
5. Değerlendirme: dokuz benchmark (AIME, LiveCodeBench, GPQA-Diamond, IFEval: talimatlara uyma testi, BFCL v3: function/tool çağırma testi...).

**Sonuç:** Yazarların raporuna göre:
- Maliyet: karışık RL 10.051 GPU saati, ayrı beş RL toplam 15.779 GPU saati. Yani karışık RL ayrı eğitimin %63.7'si kadar tutuyor.
- Performans yakın (dokuz benchmark ortalaması): karışık RL yaklaşık 61.2, en iyi merge (TIES) 61.0, MT-OPD 60.5.
- Domain'ler arası girişim az. Akıl yürütme domain'leri birbirini güçlendiriyor. Agent kazancı diğer domain'lerden gelmiyor ama zarar da görmüyor.
- Domain'lerin ağırlık değişim maskeleri büyük ölçüde örtüşüyor: Jaccard yaklaşık 0.45–0.48, rastgele maskelerde 0.18. Jaccard, iki kümenin ortak elemanlarının toplam elemanlara oranıdır.
- Uzun multi-task RL üretimi iyileştiriyor ama kendini doğrulama yeteneğini bozuyor.

**Bizim için:** Tool call davranışı (agent) diğer akıl yürütme verisinden aktarılmıyor; small model'in agent becerisi kendi trajectory'leriyle eğitilmeli, genel matematik/kod RL'i bunun yerini tutmaz.

### Distilling Reasoning into Student LLMs: Local Naturalness for Selecting Teacher Data (Virginia Tech, Ekim 2025) — [2510.03988](https://arxiv.org/abs/2510.03988)
**Soru:** 5 ve 1 (birden çok büyük modelin cevapları arasından seçim).

**Tek cümlede:** Birden çok büyük modelin cevapları karışınca, cevabı eğitilen modelin bütün metne verdiği ortalama olasılıkla seçmek bozuluyor; her cümleyi yalnız önceki birkaç cümleye göre puanlayan "local naturalness" daha güvenilir.

**Problem:** Elimizde birden çok büyük modelin cevapları varsa, eğitilen modele en "doğal" geleni seçmek mantıklı görünür. Olağan ölçüt, eğitilen modelin bütün cevaba verdiği ortalama log-olasılıktır ("global" skor). Yazarlar bu ölçütün kaynaklar karışınca yanıldığını gösterdi. Uzun izlerde, bir cümlenin olasılığı çok önceki bir sapmadan etkileniyor ve skor bozuluyor.

**Ne yaptılar:**
1. "Local naturalness" önerdiler: cevap cümle cümle puanlanıyor. Her cümlenin log-olasılığı yalnız önceki k = 4 cümleye koşullu hesaplanıyor. Böylece uzun bir izin başındaki tuhaflık sonraki bütün cümleleri cezalandırmıyor.
2. Veri: MATH (8.890 soru; Qwen2.5-72B ve Gemma3-27B cevapları) ve LIMO (817 soru; Qwen3-32B, DeepSeek-R1, QwQ-32B izleri).
3. Eğitilen modeller: Qwen2.5-7B/32B-Instruct, Qwen2.5-Math-7B, Llama-3.1-8B.
4. Karşılaştırma: local skorla seçim, global skorla seçim, en iyi tek kaynağın bütün verisi ve rastgele seçim.

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-32B'de karışık havuzdan local skorla seçim 0.726. Global skorla 0.632, en iyi tek kaynağın tüm verisi 0.719, rastgele 0.651. Yani global skor rastgeleden bile kötü; local skor en iyi tek kaynağı da biraz geçiyor.
- Qwen2.5-7B'de local 0.440, global 0.412.
- Local skor, büyük modelleri sonradan elde edilen başarıyla aynı sırada diziyor; bunun için yaklaşık 200 prompt yetiyor.
- Global skorda en "tanıdık" görünen Qwen3-32B, eğitimde en kötü sonucu veriyor.

**Bizim için:** Large model'in ve başka kaynakların (ör. farklı sıcaklıkla üretilmiş) trajectory'leri karışınca, small model'e göre adım (tool call) düzeyinde olasılıkla seçmek, tüm trajectory'nin ortalama olasılığıyla seçmekten güvenilir.

### Merge-of-Thought Distillation (Zhejiang University, Ant Group; Eylül 2025) — [2509.08814](https://arxiv.org/abs/2509.08814)
**Soru:** 5 (birden çok büyük modelden distillation; ağırlık birleştirme).

**Tek cümlede:** Her büyük modelin izleriyle ayrı bir SFT dalı eğitip dalların ağırlıklarını ortalamak (MoT), bütün kaynakların verisini tek sette birleştirmekten ve en iyi tek kaynaktan daha iyi.

**Problem:** Birden çok büyük model varsa, doğal yol hepsinin çözümlerini tek bir SFT setinde toplamaktır. Ama farklı modellerin çözüm stilleri çelişebilir; eğitilen model hangisini izleyeceğini şaşırır. Yazarlar stilleri veri düzeyinde değil, ağırlık düzeyinde birleştirmeyi denedi.

**Ne yaptılar:** Yönteme MoT diyorlar.
1. Kaynak büyük modeller: Qwen3-32B, QwQ, DeepSeek-R1, Qwen3-235B. Her soru için 16 cevaptan bir doğru cevap seçildi.
2. Veri yalnız 200 matematik sorusu: BOBA-200 ve S1K-200 (iki ayrı 200 soruluk set).
3. Eğitilen modeller: Qwen3-8B/14B/30B-A3B.
4. Her turda, her kaynağın izleriyle ayrı bir SFT dalı eğitiliyor (kaynak başına 50 adım). Sonra dalların ağırlıkları ortalanıyor. Ortalama, bir sonraki turun başlangıcı oluyor. Beş tur.
5. Karşılaştırma: tek kaynakla SFT ve bütün kaynakların verisinin birleşimiyle SFT.

**Sonuç:** Yazarların raporuna göre Qwen3-14B'nin AIME24/25 ortalaması (BOBA-200 / S1K-200):
- Base: 74.59.
- En iyi tek kaynak: 76.98 / 76.57.
- Bütün kaynakların birleşik verisi: 75.94 / 76.26. Yani verileri düz birleştirmek en iyi tek kaynaktan bile kötü.
- MoT: 78.13 / 78.65; en iyi tek kaynaktan yaklaşık 1.2–2.1 puan iyi.
- Qwen3-8B'de 71.46'dan yaklaşık 74.5'e.

**Bizim için:** Farklı kaynakların (large model, farklı prompt'lar) trajectory'lerini tek SFT setinde düz karıştırmak çelişkili stiller yüzünden zararlı olabilir; ya tek tutarlı kaynak seçilmeli ya da ayrı LoRA'lar eğitilip birleştirilmeli.

### Agentic-R1: Distilled Dual-Strategy Reasoning (CMU, Temmuz 2025) — [2507.05707](https://arxiv.org/abs/2507.05707)
**Soru:** 5 (farklı stratejideki iki büyük modelden, tool kullanan ve kullanmayan, tek modele distillation).

**Tek cümlede:** Kod çalıştıran bir agent ile salt metinle düşünen bir modelin çözümlerini birleştirip tek bir modele hangi soruda hangi stratejiyi seçeceğini öğretmek (DualDistill), ardından self-distillation ile modeli daha da iyileştirmek.

**Problem:** Bazı sorular kodla hesaplamayla kolay çözülür (ör. büyük sayılarla sayma). Bazıları ise salt metinle akıl yürütmeyle. Bir tool agent'ı ve bir metin modeli ayrı ayrı güçlü; ama her biri bazı sorularda zayıf. Tek bir model ikisini de öğrenip soruya göre seçebilir mi?

**Ne yaptılar:** Yönteme DualDistill diyorlar.
1. İki büyük kaynak: kod çalıştıran bir agent (OpenHands, Claude-3.5-Sonnet üzerinde) ve salt metinle akıl yürüten DeepSeek-R1.
2. Eğitilen model DeepSeek-R1-Distill-7B.
3. Her soruya iki çözüm alınıyor. İkincisi doğruysa, birincisinin üstüne bir geçiş cümlesiyle ekleniyor (ör. "bu yol işe yaramadı, kodla deneyeyim"). İkisi de yanlışsa soru atılıyor.
4. Yaklaşık 2.678 örnek, 4 epoch SFT.
5. Self-distillation: eğitilen model her soruya 16 çözüm örnekliyor. Doğru çözümler bir doğrulama adımıyla, yanlış çözümler bir düzeltmeyle eşleniyor; bunlarla yeniden eğitiliyor.

**Sonuç:** Yazarların raporuna göre DeepMath-L'de ortalama 63.1, self-distillation ile 67.4. Combinatorics300'de 49.4, self-distillation ile 52.0.
- DeepMath-L: DeepMath'in cevabı çok büyük (mutlak değeri 10^5'ten büyük) 87 sorusu; yazarlar bunlarda kodla hesaplamanın işe yarayacağını varsaydı.
- Combinatorics300: çeşitli matematik setlerinden toplanmış, cevabı 10^4'ten büyük 300 kombinatorik sorusu; sayma ve örnekleme gerektirdiği için tool kullanımına uygun.
- Makalenin Tablo 1'ine göre Combinatorics300'de taban model DeepSeek-R1-Distill-7B 44.5 alıyor; yani DualDistill yaklaşık 5, self-distillation yaklaşık 7.5 puan ekliyor.

**Kaynak notu:** Makalenin Tablo 1'i (bir özetleme aracıyla) okunduğunda DeepMath-L sütununda 56.3 (taban model), 59.3 (Agentic-R1-7B) ve 65.3 (self-distillation sonrası) değerleri görünüyor. Yukarıdaki 63.1 ve 67.4'ün bu sütuna mı yoksa birden çok benchmark'ın ortalama sütununa mı ait olduğu bu okumayla kesinleşmedi; rakam kullanılmadan önce tablo doğrudan kontrol edilmeli.

**Bizim için:** "Önce kendi denemesi, yanlışsa large model'in düzeltmesi" biçiminde birleştirilmiş trajectory'ler, small model'e handoff yerine kendi hatasından dönmeyi öğretmenin bir yolu.
