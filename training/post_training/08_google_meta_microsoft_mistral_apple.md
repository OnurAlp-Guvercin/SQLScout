# Google DeepMind, Meta, Microsoft, Mistral, Apple

**Bu bölümde ne var:** Google / Google DeepMind (Google Research ve Google Cloud AI Research dahil), Meta (FAIR, GenAI, Meta Superintelligence Labs), Microsoft (Research, Phi), Mistral AI ve Apple'ın Kasım 2024 – Kasım 2026 arasında yayımladığı post-training reçeteleri. Post-training, ön eğitimi (pretraining) bitmiş bir modelin sonradan eğitilmesidir: [SFT](00_terimler.md#sft) (hazır örneklerden öğrenme), [RL](00_terimler.md#rl-ve-rlvr) (deneyerek ve ödül alarak öğrenme) ve [distillation](00_terimler.md#distillation) (büyük modelin çıktılarından öğrenme) gibi. Bölümde bu laboratuvarların uzman modelleri birleştirme, judge (değerlendirici) model eğitme, preference optimization, self-play ve mid-training çalışmaları da var.

**Kaynaklar ve alınmayanlar:** Her girdi arXiv sayfasından (abs ya da HTML), resmi technical report'tan ya da resmi blog'dan okundu. Yazarların bu laboratuvarlardan olduğu kontrol edildi. Rakamlar yazarların bildirdiği gibidir; bulunamayan rakam yazılmadı. Alınmayanlar: Gemini 3 (yalnızca model kartı var, reçete yok), Gemma 3n (ayrı rapor bulunamadı), SCoRe (Eylül 2024, pencerenin dışında), Branch-Train-MiX (Mart 2024, pencerenin dışında; yerine Meta'nın BTS çalışması alındı), Apple'ın üçüncü nesil Foundation Models'ı (Haziran 2026 blog'u reçete vermiyor, technical report henüz çıkmamış). rStar2-Agent başka bir araştırmacının dosyasında.

**Bu bölümün ana dersleri:**
- Küçük modelde en büyük sıçrama, büyük modelin doğrulanmış çözümleriyle yapılan SFT ya da distillation'dan geliyor (Phi-4-mini-reasoning, Fara-7B, Ministral 3).
- SFT biçimi oturtuyor, RL genelleştiriyor; ikisi birlikte, tek başlarına olduklarından daha iyi (Magistral, SFT Memorizes RL Generalizes).
- RL verisi zorluğa göre süzülmeli: her zaman çözülen ve hiç çözülmeyen sorular öğrenme sinyali vermiyor (ScaleRL, Magistral, Llama 4, SPICE, CWM).
- RL boyunca modelin cevap çeşitliliği (entropy) izlenmeli; çeşitlilik çökerse model yeni şey keşfedemiyor (Apple Entropy-Preserving RL, Magistral).
- "Doğru / yanlış" gibi seyrek bir reward'ı sıklaştırmanın ucuz yolları var: uzman adımlarına benzerlik (SRL, SWE-RL), grup içinde reward model sıralaması (HERO), kararın değiştiği token'da preference çifti (Phi-4).

**Makaleler:**
- Gemma 4 — Google'ın thinking mode'lu açık model ailesi; reçete çok az anlatılmış.
- Entropy-Preserving RL — RL'de cevap çeşitliliğinin çökmesini önleyen iki yöntem (Apple).
- Phi-4-reasoning-vision-15B — yalnızca SFT ile görüntü anlayan reasoning modeli; kazanç veri temizliğinden.
- Self-Improving Pretraining — pretraining'de büyük modeli yeniden yazıcı ve judge olarak kullanan RL.
- Ministral 3 — büyük modeli budayıp distillation ile küçük modeller üretmek, sonra GRPO ve online DPO.
- Fara-7B — büyük modelin çözdüğü web görevleriyle yalnızca SFT yapılmış 7B computer-use agent'ı.
- Supervised Reinforcement Learning (SRL) — uzman çözümünün her adımına benzerliği ödüllendiren RL.
- SPICE — tek modelin belgelerden soru üretip kendisinin çözdüğü self-play.
- ScaleRL — 400 bin GPU saatlik deneylerle RL'nin nasıl ölçekleneceği.
- HERO — ikili doğrulayıcı reward'ını reward model skoruyla birleştirmek.
- CWM — kodun çalışınca ne yaptığını öğrenen 32B kod modeli; çok turlu agentic RL.
- Compute as Teacher (CaT) — referans cevap olmadan, modelin kendi rollout'larından referans kurup RL.
- RA3 — RL'den önce "ne zaman düşünmeli" öğreten bir mid-training yöntemi.
- Language Self-Play (LSP) — veri olmadan, modelin kendine talimat yazıp cevapladığı self-play.
- CoT-Self-Instruct — sentetik soru üretip otomatik filtreleyerek RL ve DPO verisi kurmak.
- Gemini 2.5 — Google'ın raporu; post-training genel hatlarıyla, k-sparse distillation.
- Apple Intelligence Foundation Models 2025 — Apple'ın cihaz üstü ve sunucu modelleri; SFT + RLOO.
- Phi-4-mini-flash-reasoning — yeni mimarili 3.8B model; RL'siz, yalnız SFT + DPO.
- Bridging Offline and Online RL — DPO ve GRPO'yu offline, yarı online ve online karşılaştırma.
- Magistral — Mistral'ın yalnızca RL ile eğittiği reasoning modeli ve SFT + RL'li küçük kardeşi.
- J1 — değerlendirici (judge) modeli karar vermeden önce düşünecek şekilde RL ile eğitmek.
- Phi-4-reasoning — 14B modeli o3-mini cevaplarıyla SFT, sonra kısa bir RL.
- Phi-4-mini-reasoning — 3.8B model için dört aşamalı reçete: distillation, SFT, DPO, RL.
- The Llama 4 herd — Meta'nın blog'u: hafif SFT, online RL, hafif DPO; codistillation.
- Gemma 3 — pretraining ve post-training'de distillation, ardından RL.
- SWE-RL — gerçek GitHub PR'larıyla, patch benzerliği reward'ı kullanan RL.
- NaturalReasoning — pretraining metinlerinden 2.8M reasoning sorusu çıkarmak.
- Distillation Scaling Laws — distillation ne zaman normal eğitimden iyidir, bir yasa.
- BTS — ayrı eğitilmiş uzman modelleri hafif katmanlarla birleştirmek.
- SFT Memorizes, RL Generalizes — SFT ve RL'nin yeni kurallı görevlerde karşılaştırılması.
- rStar-Math — büyük model olmadan, ağaç aramasıyla kendi kendini geliştiren küçük matematik modeli.
- Inference-Aware Fine-Tuning for Best-of-N — modeli "N cevap üret, en iyisini seç" kullanımına göre eğitmek.
- Phi-4 — 14B model; SFT ve iki tur DPO, Pivotal Token Search.

---

## Gemma 4 Technical Report (Google DeepMind, Temmuz 2026) — [2607.02770](https://arxiv.org/abs/2607.02770)
**Tek cümlede:** Google'ın açık Gemma 4 ailesi; Gemma 3'e göre asıl yenilik thinking mode, ama post-training'in nasıl yapıldığı neredeyse hiç anlatılmıyor.

**Problem:** Önceki açık model Gemma 3, zor matematik ve kod sorularında zayıftı. Örneğin Gemma 3 27B, AIME'de (lise matematik olimpiyatı soruları) yalnızca 20.8 alıyordu. Bu tür sorularda model cevaptan önce düşünce adımları yazarsa daha başarılı oluyor. Gemma 4 bunu bir açılıp kapanan mod olarak ekliyor.

**Ne yaptılar:**
1. **Model ailesi:** 2.3B'den 31B'ye beş model: E2B, E4B, 12B, 26B-A4B ve 31B. Bir kısmı dense (her token'da bütün parametreler çalışır), bir kısmı [MoE](00_terimler.md#moe) (her token'da yalnızca birkaç "uzman" alt ağ çalışır; böylece model büyük ama her adım ucuz olur).
2. **Thinking mode:** Model cevaptan önce bir reasoning trace (düşünce metni) üretebiliyor. Sistem mesajına `<|think|>` konunca bu mod açılıyor. Ayrıntısı için: [thinking mode](00_terimler.md#thinking-mode).
3. **Post-training:** Rapor bunu tek paragrafta anlatıyor: "Gemma 3'tekine benzer bir post-training yaklaşımı", artı thinking mode.
4. **Veri filtreleme (Gemma 3 ile aynı):** Kişisel bilgi, güvensiz ya da toksik çıktılar, modelin kendini yanlış tanıttığı örnekler ve tekrarlar atılıyor. Halüsinasyonu (uydurma bilgiyi) azaltmak için kaynak gösteren, temkinli cevap veren (hedging) ve gerektiğinde reddeden örnekler ekleniyor.

**Sonuç:** Yazarların raporuna göre, thinking mode açıkken (sırasıyla 31B / 26B-A4B / 12B / E4B / E2B):
- Benchmark'ların kısa tanımları için bkz. [benchmarklar](00_terimler.md#benchmarklar).
- AIME 2026: 89.2 / 88.3 / 77.5 / 42.5 / 37.5. Gemma 3 27B 20.8 alıyordu; yani 31B dört kattan fazla iyi. Ama en küçük iki model büyüklerin yarısının altında kalıyor.
- LiveCodeBench v6 (yeni yarışma programlama soruları; ezber riski düşük): 80.0 / 77.1 / 72.0 / 52.0 / 44.0. Gemma 3 27B: 29.1.
- GPQA Diamond (uzman düzeyinde fizik, kimya, biyoloji çoktan seçmeli soruları): 84.3 / 82.3 / 78.8 / 58.6 / 43.4. Bu notta Gemma 3 karşılaştırması yok.
- Arena'da (insanların iki modelin cevabını karşılaştırıp oy verdiği sıralama) 31B 1451 Elo.
- Ablation (bir parçayı çıkarıp etkisini ölçen deney) yok.

**Kaynak notu:** Raporda distillation, SFT veri boyutu, RL algoritması, reward'lar ve thinking trace'lerinin nasıl eğitildiği yok. Rakamlar yalnızca son modellere ait; hangi adımın ne kadar kazandırdığı bilinmiyor.

**Bizim için:** Küçük boyda thinking ile büyük boy arasındaki fark çok büyük (AIME'de 37.5'e karşı 89.2). 0.8B'de uzun reasoning'e değil, kısa ve tool'a dayanan adımlara yatırım yapmak daha mantıklı.

## Entropy-Preserving Reinforcement Learning (Apple, Mart 2026) — [2603.11682](https://arxiv.org/abs/2603.11682)
**Tek cümlede:** RL eğitimi modelin cevap çeşitliliğini (entropy) hızla öldürüyor; yazarlar bunu ölçüp entropy'yi sabit tutan iki yöntem öneriyor. ICLR 2026.

**Problem:** [Entropy](00_terimler.md#entropy-ve-entropy-collapse), modelin bir sonraki token'da ne kadar kararsız olduğunun ölçüsüdür. Entropy yüksekse model farklı yollar dener; düşükse hep aynı cevabı verir. RL ancak model farklı yollar denerse yeni bir şey keşfedebilir (exploration). Yazarlar policy gradient yöntemlerinin (modeli reward'a göre güncelleyen RL yöntemleri) eğitim boyunca entropy'yi düşürdüğünü ve bunun keşfi bitirdiğini gösteriyor.

**Ne yaptılar:**
1. **Deney düzeni:** Modeller Qwen-3-8B ve Qwen-3-32B. İki ortam var. Birincisi AppWorld: model tool kullanarak uygulamalarda görev yapan bir agent'tır. Eğitimde yalnızca 90 train problemi var; test 168 Normal ve 417 Challenge (daha zor) görevden oluşuyor. İkincisi yarışma matematiği: NuminaMath-1.5'ten 563 AMC/AIME problemi, cevap başına 4096 token budget.
2. **Algoritmaları karşılaştırdılar:** [GRPO](00_terimler.md#grpo) (aynı soruya birkaç cevap üretip her cevabı grubun ortalamasıyla kıyaslayan RL), LOOP (GRPO'nun standart sapmaya bölmeyen bir türevi), RLOO (her cevabın kıyas noktası aynı gruptaki diğer cevapların ortalaması), DAPO ve GSPO. DAPO asimetrik clipping kullanıyor (ε_low 0.2, ε_high 0.28). [Clipping](00_terimler.md#clip-ve-clip-higher), bir güncellemede token olasılığının ne kadar değişebileceğine sınır koymaktır; üst sınırı (ε_high) daha geniş tutmak, nadir token'ların olasılığının artmasına izin verir. GSPO ise sınırı token yerine bütün cevap düzeyinde koyuyor.
3. **Bulgular:**
   - GRPO eğitim boyunca entropy'sinin yaklaşık %90'ını kaybediyor.
   - [PPO](00_terimler.md#ppo) tarzı, aynı veriyle birkaç kez yapılan [off-policy](00_terimler.md#on-policy-ve-off-policy) güncellemeler (veriyi üreten model ile güncellenen modelin artık aynı olmaması) çöküşü büyütüyor.
   - Tam on-policy RLOO entropy'yi daha yavaş kaybediyor.
   - DAPO ve GSPO entropy'yi daha iyi koruyor, ama DAPO bazı koşularda entropy'yi kontrolsüz artırıyor.
   - Sayısal hassasiyet önemli: BF16'da (16 bitlik, düşük hassasiyetli sayı biçimi) log-probability yuvarlaması [importance ratio](00_terimler.md#importance-sampling)'yu (yeni ve eski modelin olasılık oranı) kaydırıp entropy düşüşünü kolaylaştırıyor. FP16 ve yuvarlama düzeltmesiyle bu davranış tersine dönüyor.
4. **REPO:** Her token'ın [advantage](00_terimler.md#advantage)'ından (o token'ın ortalamadan ne kadar iyi olduğu) o token'ın log-olasılığıyla orantılı bir pay çıkarıyor. Etkisi: nadir ama doğru çözümler biraz daha çok ödüllenir, nadir yanlış çözümler biraz daha az cezalanır. İki varyantı var: REPO-D ve REPO-R (daha ucuz yaklaşım). Payın ağırlığını bir kontrolcü ayarlıyor: entropy başlangıç değerinin altına düşerse ağırlık iki katına çıkıyor, üstüne çıkarsa yarıya iniyor.
5. **ADAPO:** ε_low 0.2'de sabit. ε_high 0.2 ile 0.32 arasında ayarlanıyor: entropy başlangıç değerinin altındaysa ε_high büyüyor (entropy artabilsin diye), üstündeyse küçülüyor.

**Sonuç:** Yazarların raporuna göre:
- REPO-R ve ADAPO, baseline'larından (GRPO, DAPO) daha yüksek skor alıyor ve entropy'yi sabit tutuyor.
- Sıralı eğitimde (önce bir ortam, sonra ikincisi) entropy'si çökmüş GRPO modeli ikinci ortamı öğrenemiyor; DAPO ve REPO öğrenebiliyor. Yani çöken çeşitlilik sonraki eğitimi de bozuyor.
- FP16 ile on-policy RLOO, Qwen-3-32B'de AppWorld'de Test Normal %79 ve Test Challenge %71 alıyor. Yazarlara göre bu o tarihteki en yüksek skor; önceki en iyi skor bu notta yok.

**Bizim için:** Tool-call agent'ında az problemle (90 görev) RL çalışabiliyor. MLX'te RL yaparsak entropy'yi her adımda izlemek, asimetrik clipping kullanmak ve sayısal hassasiyete (BF16 log-prob) dikkat etmek gerekiyor.

## Phi-4-reasoning-vision-15B Technical Report (Microsoft Research, Mart 2026) — [2603.03975](https://arxiv.org/abs/2603.03975)
**Tek cümlede:** Görüntü de anlayan 15B açık reasoning modeli; RL kullanılmadan, yalnızca SFT ile eğitildi ve yazarlara göre kazancın çoğu veri temizliğinden geliyor.

**Problem:** Multimodal (görüntü + metin) veri setleri çok hatalı: yanlış cevaplar, kötü sorular, bozuk biçim. Ayrıca her soruda uzun düşünmek gereksiz ve yavaş; bazı sorular (ör. bir grafikten değer okumak) doğrudan cevap ister. Yazarlar tek modelin hem düşünen hem doğrudan cevap veren olmasını ve verinin temizlenmesini hedefliyor.

**Ne yaptılar:**
1. **Mimari:** Mid-fusion. Önce hazır bir görüntü kodlayıcısı görüntüyü "görsel token"lara çeviriyor; sonra bu token'lar dil modelinin girdisine bağlanıyor.
2. **İki mod:** Mod token'larıyla (`<think>` / `<nothink>`) model basit soruda doğrudan cevap veriyor, zor soruda reasoning yapıyor.
3. **Yalnızca SFT, üç aşama:**
   - MLP pretraining: görüntü kodlayıcısını dil modeline bağlayan küçük katman (MLP) eğitiliyor; 2.0M örnek, 1.4B token.
   - Instruction tuning: 62.8M örnek, 188.5B token.
   - Uzun bağlam + çoklu görüntü + RAI (Responsible AI: güvenlik ve sorumlu kullanım verisi): 3.2M örnek, 12B token.
4. **Veri temizliği elle başlıyor:** Her veri setine 5–10 dakika bakılıp "mükemmel", "iyi soru ama yanlış cevap", "düşük kaliteli soru" gibi sınıflara ayrılıyor. Yanlış cevaplar GPT-4o ve o4-mini ile yeniden üretiliyor; bazen doğrulama ya da çoğunluk oyu ile. Çok hatalı setler tamamen atılıyor. Biçim hataları programla düzeltiliyor.
5. **Karışım:** Verinin yaklaşık %20'si reasoning, %80'i `<nothink>` verisi. Yazarlar bu oranın en iyi olmayabileceğini ve başka oran denemediklerini yazıyor.
6. **Maliyet:** 240 B200 GPU'da yaklaşık 4 gün.

**Sonuç:** Yazarların raporuna göre:
- 5B'lik küçük bir deneme modelinde matematik verisini 150K'dan 450K'ya çıkarmak (computer-use verisi sabitken) hem matematiği hem computer-use'u artırıyor. ScreenSpot-V2'de (ekran görüntüsünde istenen arayüz öğesini bulma) 60.0 → 63.1; MathVista'da (görsel matematik soruları) 37.3 → 38.9. Yani bir alanın verisi başka bir alana da yardım ediyor.
- Karışık mod (model modu kendisi seçiyor), zorla tek moda göre ortalamada daha iyi. ChartQA'da (grafik okuma soruları) karışık mod 83.3, zorla no-think 76.5. Ama MathVerse'te (görsel matematik) zorla think 53.1, karışık mod 44.9; yani matematikte her zaman düşünmek daha iyi.
- Veri temizliğinin etkisini ayrı ölçen sayısal bir ablation yok; yani raporun ana iddiası sayıyla desteklenmiyor.

**Bizim için:** SFT verisinde her kaydın doğruluğunu bir kez elle ve büyük modelle kontrol etmek, veri miktarını artırmaktan daha değerli. Düşünmeyi her soruda değil yalnızca gereken yerde açmak 0.8B için de uygun.

## Self-Improving Pretraining: using post-trained models to pretrain better models (Meta FAIR, Ocak 2026) — [2601.21343](https://arxiv.org/abs/2601.21343)
**Tek cümlede:** Pretraining'de "sıradaki token'ı tahmin et" yerine, güçlü bir büyük modelin yeniden yazıcı ve judge olduğu online bir RL döngüsü kuruluyor.

**Problem:** Normal pretraining'de model internetteki metni olduğu gibi taklit eder; metin kötü, güvensiz ya da yanlışsa onu da öğrenir. Kalite, güvenlik ve doğruluk genelde sonradan post-training ile düzeltilir. Yazarlar bu sinyali pretraining'in içine taşımak istiyor.

**Ne yaptılar:**
1. **Suffix döngüsü:** Belge akışında her adımda sonraki 128 token "suffix" (devam metni) olarak ayrılıyor. Eğitilen model bu devamı kendisi üretmeye çalışıyor.
2. **Büyük modelin iki rolü:** Daha önce post-train edilmiş güçlü bir model hem rewriter (suffix'i daha kaliteli ya da güvenli yeniden yazar) hem judge (orijinal suffix'i, yeniden yazılmışı ve eğitilen modelin [rollout](00_terimler.md#rollout)'larını, yani kendi ürettiği devamları puanlar) oluyor.
3. **Modeller:** Eğitilen model Llama 2 1.4B; hem continued pretraining (var olan modelin pretraining'ine devam) hem sıfırdan eğitim, 21k adım. Judge'lar: GRPO ile ince ayarlanmış Llama 3.1 8B Instruct ve prompt'lanmış GPT-OSS-120B. Güvenlik için ayrı bir rewriter var (ince ayarlı Llama 3.1 8B). Veri SlimPajama ve RedPajama.
4. **Güncelleme:** İki seçenek. Online DPO: en iyi ve en kötü aday arasında [DPO](00_terimler.md#dpo-ve-preference-optimization) (iyi cevabı kötü cevaptan daha olası yapan tercih kaybı). Ya da reward-filtered NLL: en yüksek reward'lı aday seçilip normal "bu metni tahmin et" kaybıyla öğreniliyor. Prompt başına 16 rollout, 2,000 adım, 64 GPU.
5. **[Reward](00_terimler.md#reward)'lar:** Kalite (adaylar ikişer ikişer karşılaştırılıyor), güvenlik (her aday için tek tek "güvenli mi" kararı), factuality (halüsinasyon yok / olası / kesin → 1 / 0.5 / 0; kalite skoruyla birlikte kullanılıyor).
6. **Kendiliğinden [curriculum](00_terimler.md#curriculum):** Eğitimin başında orijinal ve yeniden yazılmış suffix'ler kazanıyor; eğitilen model iyileştikçe kendi rollout'ları giderek kazanan oluyor. Yani hedef, modelin seviyesine göre kendiliğinden zorlaşıyor.

**Sonuç:** Yazarların raporuna göre:
- Continued pretraining'de kalite kazanma oranı Llama Base'e karşı %86.3; yani judge çoğu karşılaştırmada yeni modelin metnini seçiyor.
- Factuality ortalaması 42.3 → 57.6 (%36.2 göreli artış). Güvenlik 76.9 → 91.1.
- Sıfırdan eğitimde kalite kazanma oranı 32.4, normal next-token baseline'ında 1.3. Güvenlik 85.2 → 97.5.

**Bizim için:** Büyük modeli (9B) hem düzeltici hem judge olarak kullanıp küçük modelin kendi çıktıları arasından en iyisini seçtirmek, gold SQL'e ek olarak kullanılabilecek ucuz bir sinyal. Ama Mac'te pretraining ölçeğinde değil, yalnızca agent trajectory'leri üzerinde uygulanabilir.

## Ministral 3 (Mistral AI, Ocak 2026) — [2601.08584](https://arxiv.org/abs/2601.08584)
**Tek cümlede:** Mistral, 24B'lik bir modeli adım adım budayıp distillation ile 14B, 8B ve 3B modeller üretiyor; sonra distillation, GRPO ve online DPO ile post-training yapıyor.

**Problem:** Küçük modelleri sıfırdan eğitmek pahalı ve büyük modelin bilgisini kullanmıyor. Ayrıca küçük modeller düz SFT ile çok uzun ve dağınık cevaplar üretmeye eğilimli. Yazarlar büyük bir modelden küçük modellere bilgi aktarmanın ucuz bir yolunu arıyor.

**Ne yaptılar:**
1. **Cascade distillation (pretraining):** Mistral Small 3.1 (24B) başlangıç. Model budanıyor (prune): katmanlar, gizli boyut ve FFN (her katmandaki ileri beslemeli alt ağ) küçültülüyor. Sonra büyük modelden logit distillation yapılıyor: küçük model, büyük modelin her token için verdiği olasılık dağılımını taklit ediyor (forward-KL kaybıyla). Bu iş tekrarlanarak 24B → 14B → 8B → 3B'ye iniliyor. Yazarlar distillation kaybını tek başına kullanmanın, next-token kaybıyla karıştırmaktan iyi olduğunu buldu. Bağlam önce 16K, sonra 262K token. Toplam 1–3T token.
2. **Instruct modeli:**
   - Mistral Medium 3'ten logit distillation kaybıyla SFT (fp8, yani 8 bitlik sayılarla).
   - Sonra ODPO (online DPO): her prompt için temperature 0.7'de iki cevap üretiliyor. Pairwise reward model (iki cevaptan hangisinin iyi olduğunu söyleyen model) kazanma olasılığı veriyor; DPO bu olasılıkla yumuşatılıyor. Sonsuz döngüye giren cevap kaybeden sayılıyor. Üretim sırasında tool çalıştırma açık.
3. **Reasoning modeli:**
   - Kısa [CoT](00_terimler.md#cot-ve-long-cot) (chain-of-thought, adım adım düşünce) ve uzun CoT verisiyle SFT. Biçim hatası, tekrar ve dil karışması olan örnekler filtreleniyor.
   - 3B'de düz SFT çok uzun cevap ürettiği için Magistral Small 1.2'den logit distillation kullanılıyor.
   - GRPO 1. aşama STEM: doğrulanmış matematik, kod ve görsel reasoning.
   - GRPO 2. aşama genel: bir LLM judge cevabı atomik rubric maddeleriyle puanlıyor; reward, cevabın sağladığı madde oranı. Örneğin 5 maddeden 4'ü sağlanırsa reward 0.8. Ayrıntı: [LLM-as-judge ve rubric](00_terimler.md#llm-as-judge-ve-rubric).
   - En uzun üretim 32K'dan 80K'ya çıkarıldı.
   - Son olarak thinking kısmı atılarak ODPO.

**Sonuç:** Yazarların raporuna göre:
- Reasoning modelleri (14B / 8B / 3B): AIME 2025 85.0 / 78.7 / 72.1; LiveCodeBench v6 64.6 / 61.6 / 54.8; GPQA Diamond 71.2 / 66.8 / 53.4. Bu notta başka modellerle karşılaştırma yok; 3B'nin AIME'de 14B'ye yakın kalması dikkat çekici.
- Pretraining'de daha güçlü büyük model her zaman daha iyi değil: Mistral Small 3.1, Mistral Medium 3'ten daha iyi bir kaynak.
- Post-train edilmiş büyük model, base büyük modelden daha iyi kaynak.
- SFT'de preference-tuned büyük model, yalnızca SFT'li büyük modelden daha iyi kaynak.
- Instruct SFT'ye uzun CoT eklemek STEM'i artırıyor ama aşırı geri dönüş ve tekrar tekrar düşünme davranışı getiriyor.
- 3B'de ODPO public benchmark'larda kazanç vermedi; iç insan değerlendirmesine göre seçildi.

**Kaynak notu:** SFT veri boyutları ve GRPO hiperparametreleri raporda yok.

**Bizim için:** 3B'de bile düz SFT yerine büyük modelin logit'lerine distillation uzun ve dağınık cevabı önlüyor. "En büyük model en iyi kaynak değildir" bulgusu, 9B'yi 0.8B için makul bir kaynak yapıyor.

## Fara-7B: An Efficient Agentic Model for Computer Use (Microsoft Research, Kasım 2025) — [2511.19663](https://arxiv.org/abs/2511.19663)
**Tek cümlede:** Ekran görüntüsünden çalışan 7B bir web agent'ı; büyük modellerin çözüp doğrulayıcılardan geçirdiği görevlerle yalnızca SFT yapılmış.

**Problem:** Computer-use agent'ları (tarayıcıda tıklayan, yazan modeller) için eğitim verisi az ve pahalı. İnsanların görev çözdüğü kayıtları toplamak zor. Yazarlar bu veriyi otomatik üreten bir sistem kuruyor ve küçük bir modelin bununla ne kadar ileri gidebileceğine bakıyor.

**Ne yaptılar:**
1. **FaraGen ile görev önermek:** Görevler üç yoldan geliyor: hedefli URL bölümleri (~%28), rastgele sitelerde agent keşfi (~%67), örnek görevlerin genişletilmesi. Başlangıç URL'leri çoğunlukla ClueWeb22 (büyük bir web sayfası koleksiyonu).
2. **Görevleri çözdürmek:** Çözücü, Magentic-One tabanlı çok agent'lı bir sistem: bir Orchestrator (plan yapan) ve bir WebSurfer (tarayıcıyı kullanan). Modeller GPT-4o ve o4-mini; ablation'da o3 ve GPT-5.
3. **Çözümleri doğrulamak:** Üç LLM doğrulayıcı var: Alignment (görev istenen şeyi yaptı mı), Rubric (maddelere göre puan; eşik 0.8) ve Multimodal (ekran görüntülerine bakarak). İnsan kararıyla uyumları %83.3; yanlış pozitif oranı %16.7 (yani kabul edilen her 6 çözümden biri aslında hatalı).
4. **Veri:** 145,603 trajectory, ~1.01M adım (trajectory başına ortalama 6.9 adım), ~70K alan adı. Trajectory başına maliyet ~$0.59–1.08.
5. **Karışım:** Trajectory'ler grounding (ekranda bir öğeyi bulma), reddetme ve arayüz soru-cevap verileriyle toplam 1.8M örneğe karıştırılıyor; trajectory verisi upsample ediliyor (birden çok kez kullanılıyor).
6. **Güvenlik:** Satın alma, giriş yapma, e-posta gönderme gibi kritik noktalarda durup kullanıcıya sormak öğretiliyor.
7. **Eğitim:** Base Qwen2.5-VL-7B, yalnızca SFT; RL yok.

**Sonuç:** Yazarların raporuna göre:
- WebVoyager (gerçek sitelerde web görevleri) 73.5, Online-Mind2Web (canlı sitelerde görevler) 34.1, DeepShop (çok adımlı alışveriş görevleri) 26.2, WebTailBench (web görevleri benchmark'ı) 38.4. Bu notta baseline rakamları yok.
- Veri ölçeği ablation'ı: 18K → 180K → 1.8M adımda skor sürekli artıyor; yani veri henüz doymamış.
- Çözücü sistemi iyileştirmek, WebVoyager'da çözücünün başarısını %33'ten %60'a çıkarıyor; daha iyi çözücü, daha çok kullanılabilir veri demek.

**Kaynak notu:** Doğrulayıcı filtrelemesinin eğitime etkisi ablation'la ölçülmemiş.

**Bizim için:** Agentic küçük model için en ucuz yol, büyük modelin çözdüğü ve doğrulayıcıdan geçen trajectory'lerle SFT. Bizde final check ve BIRD'ün gold sonucu doğrulayıcı rolünü bedavaya görüyor.

## Supervised Reinforcement Learning: From Expert Trajectories to Step-wise Reasoning (Google Cloud AI Research + UCLA, Ekim 2025) — [2510.25992](https://arxiv.org/abs/2510.25992)
**Tek cümlede:** SFT ile RLVR arasında bir yöntem (SRL): model uzman çözümünün her adımını kendisi üretmeye çalışıyor ve reward, ürettiği adımın uzmanın adımına ne kadar benzediği. ICLR 2026.

**Problem:** RLVR (RL with verifiable rewards: reward'ı otomatik doğrulanan sonuçtan gelen RL) zor sorularda tıkanıyor: modelin bütün rollout'ları yanlışsa reward hep 0 olur, model hiçbir şey öğrenmez. SFT ise uzman çözümünü token token ezberletir; az sayıda zor örnekte modeli bozabilir. SRL, hiç doğru cevap bulunamayan sorularda da sinyal vermek istiyor.

**Ne yaptılar:**
1. **Uzman çözümünü adımlara bölmek:** Matematikte veri s1K-1.1 (1,000 zor soru; 60'ı doğrulama için). DeepSeek R1'in çözümleri Gemini-2.5-flash ile numaralı adımlara çevriliyor.
2. **Her adımdan bir prompt:** N adımlı bir çözüm N−1 kısmi prompt veriyor. Her prompt, sorunun ve ilk birkaç uzman adımının ardından "sıradaki adımı yaz" diyor.
3. **Modelin cevabı:** Model önce kendi iç düşüncesini yazıyor, sonra bir "action" (o adımın kendisi) üretiyor.
4. **Reward:** Yalnızca action'a bakılıyor, iç düşünceye değil. Benzerlik Python'un `difflib.SequenceMatcher` oranı: eşleşen karakter sayısının iki katı, iki metnin toplam uzunluğuna bölünüyor (0 ile 1 arası). Örneğin uzmanın adımı "x = 5" ve modelinki "x = 6" ise oran yüksek ama 1 değil. Biçim bozuksa reward −1.
5. **[Dynamic sampling](00_terimler.md#dynamic-sampling):** Bir örneğin rollout reward'larının standart sapması eşiğin altındaysa (bütün cevaplar aşağı yukarı aynı puanı almışsa) örnek atılıyor; çünkü öyle bir örnek öğrenme sinyali vermez.
6. **Modeller:** Matematikte Qwen2.5-7B-Instruct ve Qwen2.5-3B-Instruct. Yazılım mühendisliğinde (SWE) Qwen2.5-Coder-7B-Instruct; claude-3-7-sonnet'in 5,000 trajectory'si 134k adım örneğine bölünmüş.
7. **Birleştirme:** SRL'den sonra normal RLVR de deneniyor (SRL→RLVR).

**Sonuç:** Yazarların raporuna göre:
- Matematik ortalaması (AMC23 ve AIME24/25: lise yarışma matematiği; Minerva: üniversite düzeyi bilim ve matematik problemleri; greedy, yani her token'da en olası seçim): base 24.6, SFT 16.3, RLVR 24.5, SRL 27.6, SRL→RLVR 28.3. Yani 1K zor soruda düz SFT modeli 8 puan bozuyor, RLVR yerinde sayıyor, SRL 3 puan artırıyor; ardından RLVR eklemek biraz daha artırıyor.
- SWE-Bench Verified (gerçek GitHub hatalarını düzeltme; testlerle doğrulanıyor): oracle dosya düzenlemede (doğru dosya verilmişken) base 5.8, SWE-Gym-7B 8.4, SRL 14.8. Uçtan uca (dosyayı da kendisi bulunca) 3.2 / 4.2 / 8.6. SRL iki durumda da en iyi baseline'ın yaklaşık iki katı.

**Bizim için:** Bizim projeye en yakın reçetelerden biri. Büyük modelin (9B) tool call adımlarını hedef alıp küçük modelin her `search_values` / `execute_sql` çağrısını difflib benzerliğiyle ödüllendirmek, 0.8B'nin hiç doğru cevap bulamadığı sorularda bile sinyal verir; sonra RLVR (sonuç doğru mu) eklenir.

## SPICE: Self-Play In Corpus Environments Improves Reasoning (Meta FAIR, Ekim 2025) — [2510.24684](https://arxiv.org/abs/2510.24684)
**Tek cümlede:** Tek model iki rol oynuyor: belgelerden soru üreten Challenger ve o soruları belgeyi görmeden çözen Reasoner; belgeye bağlı olmak self-play'i sağlam tutuyor.

**Problem:** [Self-play](00_terimler.md#self-play)'de model kendine soru üretip kendisi çözer, böylece insan verisine gerek kalmaz. Ama soru bir belgeye dayanmıyorsa (ungrounded) model halüsinasyon üretebilir ve cevabın doğru olup olmadığı bilinemez; sinyal zamanla kaybolur. SPICE soruları gerçek belgelere bağlayarak bunu çözmeye çalışıyor.

**Ne yaptılar:**
1. **Corpus:** 20,000 belge; yarısı Nemotron-CC-Math (matematik içerikli web metinleri), yarısı NaturalReasoning (DCLM alt kümesi; bkz. bu dosyadaki NaturalReasoning girdisi).
2. **Challenger:** Bir belgeden reasoning görevi üretiyor; cevap belgeden çıkarılıyor. Reward'ı, Reasoner'ın doğru/yanlış sonuçlarının varyansına uygulanan bir Gauss fonksiyonu. Varyans, Reasoner yarı yarıya çözdüğünde en büyüktür (0.25). Yani Challenger en çok, Reasoner'ın %50 [pass rate](00_terimler.md#pass-rate-ve-passk) ile çözdüğü soruyu ürettiğinde ödül alıyor. Örnek: Reasoner 8 denemeden 4'ünü bilirse ödül en yüksek; 8'ini de bilirse ya da hiçbirini bilemezse düşük. Geçersiz soruya −0.1.
3. **Reasoner:** Belgeyi görmeden çözüyor. Reward, belgeden çıkarılan gold cevaba göre doğru (1) ya da yanlış (0).
4. **Algoritma:** DrGRPO (GRPO'nun standart sapmaya bölmeyen ve uzunluk yanlılığını kaldıran türevi). İki rol için ayrı, yalnızca ortalaması çıkarılmış advantage kullanılıyor.
5. **Modeller:** Qwen3-4B-Base, Qwen3-8B-Base, OctoThinker-3B/8B-Hybrid-Base.
6. **Kendiliğinden curriculum:** İki rol yarıştığı için sorular, Reasoner'ın sınırında kalacak şekilde zorlaşıyor.

**Sonuç:** Yazarların raporuna göre:
- Benchmark ortalaması (base → SPICE): Qwen3-4B 35.8 → 44.9; Qwen3-8B 43.0 → 48.7; OctoThinker-3B 14.7 → 25.2; OctoThinker-8B 20.5 → 32.4. Kazanç zayıf modellerde daha büyük (OctoThinker'da ~10 puan).
- Corpus'suz self-play Qwen3-4B'de 40.7'de kalıyor; belgeye bağlı sürüm aynı grafikte 43.9. Yani belge kullanmak yaklaşık 3 puan kazandırıyor.

**Kaynak notu:** Corpus'suz karşılaştırma eğitim grafiğinden okunuyor; grafikteki grounded değer (43.9), tablodaki SPICE sonucundan (44.9) farklı.

**Bizim için:** "%50 pass rate'te en çok ödül" kuralı, kendi kendine soru üretmeden de RL verisini seçmek için kullanılabilir: küçük modelin BIRD train'de yarı yarıya çözdüğü sorular en değerli RL verisi.

## The Art of Scaling Reinforcement Learning Compute for LLMs — ScaleRL (Meta + UT Austin + UCL + Berkeley/Harvard, Ekim 2025) — [2510.13786](https://arxiv.org/abs/2510.13786)
**Tek cümlede:** 400,000 GPU saatinden fazla deneyle RL'nin compute arttıkça nasıl iyileştiğini bir eğriyle ölçüp, en iyi ölçeklenen seçimleri ScaleRL reçetesinde topladılar.

**Problem:** RL'ye ayrılan compute hızla büyüyor, ama hangi reçetenin büyük ölçekte iyi gideceğini önceden bilmenin yolu yoktu. Küçük bir deneyde iyi görünen bir seçim, büyük ölçekte tavana erken takılabilir. Yazarlar küçük koşulardan büyük koşunun sonucunu tahmin etmek istiyor.

**Ne yaptılar:**
1. **Sigmoid eğri:** Performansı compute'a karşı çizip S biçimli bir eğri uydurdular. Eğrinin iki sayısı var: A, asimptot (sonsuz compute'ta ulaşılacak tavan skor); B, verim (tavana ne kadar hızlı yaklaşıldığı). Bir seçim tavanı mı yükseltiyor yoksa yalnızca hızı mı değiştiriyor, bu iki sayıyla ayrılıyor.
2. **Tahmin testi:** Tek bir koşuyu 100,000 GPU saatine çıkardılar ve sonucunun erken noktalardan uydurulan eğriyle tahmin edilebildiğini gösterdiler.
3. **ScaleRL reçetesinin seçimleri:**
   - PipelineRL: üretim ve eğitim aynı anda sürüyor; model güncellenirken eski ağırlıklarla üretim devam ediyor. Bir cevap en fazla 8 adım eski bir modelden gelebiliyor (off-policy).
   - Zorla kesme: çok uzun üretimlerin sonuna "düşünmeyi bitir" ifadesi eklenip model cevaba geçmeye zorlanıyor.
   - CISPO kaybı: kırpılmış importance sampling ile REINFORCE (en temel policy gradient). Importance ağırlığı kırpılıyor ama token güncellemeden tamamen çıkarılmıyor. DAPO ve GSPO'ya tercih edildi.
   - LM head'de FP32: modelin son katmanı (her token'ın olasılığını hesaplayan katman) 32 bitlik tam hassasiyetle çalışıyor.
   - Prompt düzeyinde loss ortalaması: önce her prompt'un kaybı ortalanıyor, sonra prompt'lar; böylece her prompt kayba eşit ağırlıkla giriyor.
   - Batch düzeyinde advantage normalizasyonu: advantage'lar grup yerine bütün batch'in standart sapmasına bölünüyor.
   - Zero-variance filtering: bütün cevapları aynı reward'ı alan prompt kayba girmiyor (hepsi doğru ya da hepsi yanlışsa öğrenecek bir fark yok).
   - No-Positive-Resampling: geçmiş pass rate'i 0.9 ya da üstü olan prompt, sonraki epoch'lardan kalıcı olarak çıkarılıyor.
   - [KL penalty](00_terimler.md#kl-penalty) yok (modeli başlangıç modeline yakın tutan ceza kullanılmıyor).
4. **Modeller ve veri:** Çoğu ablation 8B dense modelde; büyük koşu Llama-4 Scout (17B×16 MoE). Veri Polaris-53K (matematik); ortak koşularda Deepcoder (kod) eklenmiş. Batch 48 prompt × 16 cevap. Uzunluk: 12,288 düşünme + 2,048 çözüm + 2,048 prompt token'ı.

**Sonuç:** Yazarların raporuna göre:
- ScaleRL'in tavanı A ≈ 0.61 (hata payı ±0.02); karşılaştırılan diğer reçetelerden yüksek.
- FP32 LM head tek başına A'yı 0.52'den 0.61'e çıkarıyor; küçük bir sayısal değişiklik tavanı 9 puan yükseltiyor.
- CISPO ve GSPO, DAPO'dan daha yüksek tavana ulaşıyor.
- Loss ortalaması, normalizasyon, curriculum ve length penalty (uzun cevaba ceza) çoğunlukla yalnızca verimi (B) değiştiriyor, tavanı değil.
- Büyük batch başta yavaş ama sonunda daha yüksek. Üretim budget'ını 14k'dan 32k'ya çıkarmak başı yavaşlatıp tavanı yükseltiyor.
- Scout, 8B'nin ~1/6 RL compute'uyla daha yüksek tavana ulaşıyor; büyük model RL'yi daha verimli kullanıyor.

**Bizim için:** Küçük bütçede en önemli iki kural: bütün rollout'ları aynı reward'ı alan soruları atmak ve neredeyse her zaman çözülen soruları (pass rate ≥ 0.9) havuzdan kalıcı olarak çıkarmak. Küçük bir koşunun eğrisi, büyük koşunun sonucunu tahmin etmeye yetiyor.

## Hybrid Reinforcement: When Reward Is Sparse, It's Better to Be Dense — HERO (Meta FAIR + UW–Madison, Ekim 2025) — [2510.07242](https://arxiv.org/abs/2510.07242)
**Tek cümlede:** İkili "doğru / yanlış" doğrulayıcı reward'ını bir reward model'in sürekli skoruyla birleştiriyorlar; doğrulayıcı grubu belirliyor, reward model yalnızca grup içinde sıralıyor.

**Problem:** Doğrulayıcı (verifier) reward'ı güvenilir ama seyrek: bir cevap ya 1 ya 0 alır, "neredeyse doğru" ile "tamamen saçma" aynı puanı alır. [Reward model](00_terimler.md#reward-model-grm-ve-prm) (RM: cevaba puan veren eğitilmiş model) ise sürekli ve ayrıntılı bir skor verir, ama yanılabilir ve yanlış bir cevaba yüksek puan verebilir. HERO ikisinin iyi yanını birleştirmek istiyor.

**Ne yaptılar:**
1. **Stratified normalization:** Cevaplar önce doğrulayıcıya göre iki gruba ayrılıyor: doğrular ve yanlışlar. RM skorları her grubun kendi içinde min-max normalize ediliyor (en düşük 0'a, en yüksek 1'e çekiliyor) ve gruplar ayrı aralıklarda tutuluyor. Böylece RM, doğru bir cevabı yanlış bir cevabın altına düşüremiyor; yalnızca iki doğru cevaptan hangisinin daha iyi olduğunu söylüyor. Örnek: 8 cevaptan 3'ü doğru; bu üçü RM'ye göre kendi aralarında sıralanıyor, ama üçü de 5 yanlışın üstünde kalıyor.
2. **Variance-aware weighting:** Cevapları arasında RM skoru daha çok değişen prompt'lar daha yüksek ağırlık alıyor; cevapların hep aynı puanı aldığı önemsiz prompt'ların ağırlığı düşüyor.
3. **Modeller:** Qwen3-4B-Base ve OctoThinker-8B-Hybrid-Base; RL'den önce [cold start](00_terimler.md#cold-start) olarak kısa bir SFT.
4. **Veri:** OpenMathReasoning'den üç rejim: kolay doğrulanan (cevabı tek bir sayı gibi), zor doğrulanan (cevabı serbest biçimli) ve karışık.
5. **Baseline'lar:** Yalnız RM (AceMath-RM-7B) ve yalnız doğrulayıcı (math_verify kütüphanesi).

**Sonuç:** Yazarların raporuna göre, Qwen3-4B-Base ile (HERO / yalnız RM / yalnız doğrulayıcı):
- Kolay doğrulanan veriyle eğitince, doğrulanabilir görevlerde 62.0 / 56.4 / 58.3; zor doğrulanan görevlerde 66.3 / 54.6 / 57.1. HERO en iyi baseline'dan yaklaşık 4–9 puan önde.
- Karışık veriyle eğitince, zor doğrulanan görevlerde 64.1 / 54.0 / 58.9.
- 72B RM, 7B RM'ye göre belirgin kazanç vermiyor; yani kazanç daha büyük RM'den değil, birleştirme tasarımından geliyor.

**Bizim için:** SQL'de sonuç eşleşmesi ikili ve seyrek. Aynı "doğru" ya da "yanlış" grubun içinde daha az çağrıyla ya da daha temiz SQL'le bitirilen trajectory'yi biraz daha ödüllendirmek, doğruluğu bozmadan sinyali sıklaştırabilir.

## CWM: An Open-Weights LLM for Research on Code Generation with World Models (Meta FAIR, Eylül 2025) — [2510.02387](https://arxiv.org/abs/2510.02387)
**Tek cümlede:** 32B dense kod modeli; mid-training'de kodun çalışınca ne yaptığını öğreniyor ("world model"), sonra SFT ve çok görevli, çok turlu RL ile eğitiliyor. Mid-training, SFT ve RL checkpoint'leri açık.

**Problem:** Kod modelleri çoğunlukla kodun metnini görerek eğitilir, kod çalışınca ne olduğunu görmez. Yazarlar, programın çalışma izlerini ve bir ortamla etkileşimi gören bir modelin kodu daha iyi anlayacağını düşünüyor. Ayrıca agentic yazılım görevlerinde (SWE) uzun, çok turlu RL'nin nasıl kurulacağını göstermek istiyorlar.

**Ne yaptılar:**
1. **[Mid-training](00_terimler.md#mid-training) (pretraining ile post-training arasındaki ara eğitim):** Python yürütme trace'leri (kod satır satır çalışırken değişkenlerin aldığı değerler) ve agentic Docker ortamı etkileşimleri. Model böylece "bu kod çalışınca ne olur" sorusunu öğreniyor.
2. **SFT:** 100B token, 50k adım, 2M token batch, 32k bağlam, sabit lr (öğrenme hızı) 1e-5. Verinin ~%30'u mid-training verisinin tekrarı. Geri kalanı: agentic SWE trajectory'leri (bir kısmı önceki CWM sürümlerinden [rejection sampling](00_terimler.md#rejection-sampling) ile, yani çok cevap üretip yalnızca doğruları tutarak), OpenMathReasoning ve OpenCodeReasoning. Reasoning özel token'larla açılıyor; bu token'ların kaybı [maskeleniyor](00_terimler.md#loss-masking) (model bu token'lar için cezalandırılmıyor).
3. **RL algoritması (değiştirilmiş GRPO):** Çok turlu maskeleme (ortamın çıktıları öğrenilmiyor), asenkron üretim, advantage = return − ortalama (standart sapmaya bölme ve uzunluk normalizasyonu yok), clip-higher (ε_high 0.25 / ε_low 0.2), KL yok. Sıfır advantage'lı ve 100 adımdan eski trajectory'ler atlanıyor. Anlamsız metin üreten cevaplar tespit ediliyor.
4. **RL ortamları:**
   - Agentic SWE: 128 tura kadar; tool'lar bash, edit, create ve submit. Bütün gizli testler geçerse reward 1; geçmezse patch benzerliğine göre 0 ya da −1.
   - Competitive programming: 81k prompt, [dekontamine](00_terimler.md#decontamination) (test sorularına benzeyen örnekler atılmış); +1/−1.
   - Agentic coding ve matematik.
5. **Zorluk filtresi ve ipucu:** SWE örnekleri SFT modelinin pass@1'ine (tek denemede çözme oranı) göre süzülüyor. %95 üstü kolay diye atılıyor. %0 olan örneklere gizli testler ipucu olarak ekleniyor; böylece pass@1 ~%30'a çıkıyor. İpucu sonra kaldırılıyor. Son SWE seti 12.6k örnek (6.9k birincil, 5.7k ikincil).
6. **Self-bootstrapping:** Üç tur: RL → RL modelinden rejection sampling → bu doğru trajectory'lerle yeniden SFT.

**Sonuç:** Yazarların raporuna göre:
- SWE-bench Verified (gerçek GitHub hatalarını düzeltme) pass@1: [test-time scaling](00_terimler.md#test-time-scaling) ile (inference'ta birden çok deneme üretip birini seçmek) %65.8, onsuz %53.9.
- LiveCodeBench-v5 68.6; Math-500 (MATH veri setinden 500 soru) 96.6; AIME 2024 76.0. Bu notta baseline rakamları yok.
- Self-bootstrapping turlarında SFT checkpoint'inin SWE-bench Verified skoru 30 → 37 → 43. Yani her tur, RL'nin bulduğu doğru çözümleri SFT'ye geri besleyerek 6–7 puan ekliyor.

**Bizim için:** Küçük modelin hiç çözemediği sorulara ipucu (ör. gold SQL'in tabloları) ekleyip RL'ye sokmak, sonra ipucunu kaldırmak; ve RL'den çıkan doğru trajectory'leri tekrar SFT'ye beslemek, experience log'u büyütmenin doğrudan bir yolu.

## Compute as Teacher: Turning Inference Compute Into Reference-Free Supervision (Meta Superintelligence Labs + Oxford, Eylül 2025) — [2509.14234](https://arxiv.org/abs/2509.14234)
**Tek cümlede:** Referans cevap olmadan RL: model birkaç cevap üretiyor, dondurulmuş bir model bunları birleştirip bir "pseudo-reference" (sözde referans) yazıyor, reward bu referanstan türetiliyor. ICML 2026.

**Problem:** RL için genelde her sorunun doğru cevabı ya da bir doğrulayıcı gerekir. Birçok alanda (sağlık danışmanlığı gibi) böyle bir referans yok, ya da etiketsiz sorular var. Yazarlar modelin inference'ta harcadığı compute'u (çok sayıda cevap üretmeyi) bir eğitim sinyaline çevirmek istiyor.

**Ne yaptılar:**
1. **Rollout'lar:** Eğitilen model bir prompt için paralel olarak 8 cevap üretiyor.
2. **Synthesis:** Dondurulmuş bir anchor model (eğitim boyunca güncellenmeyen bir model) bu 8 cevabı okuyup tek bir pseudo-reference yazıyor.
3. **Doğrulanabilir alanda reward (matematik):** Rollout'un cevabı referansla eşleşiyor mu; eşleşirse 1.
4. **Doğrulanamayan alanda reward:** Model referanstan evet/hayır biçiminde "self-proposed rubric" maddeleri çıkarıyor (açıklama için uydurulmuş bir örnek: "cevap doktora başvurmayı öneriyor mu?"). Bir LLM judge her rollout'u sağladığı madde oranıyla puanlıyor.
5. **Algoritma ve veri:** GRPO, prompt başına 8 rollout. HealthBench (sağlık sohbetleri; cevaplar uzmanların yazdığı rubric'lerle puanlanıyor): 5,000 konuşma, 500 test. MATH-500: etiketsiz test-time RL (test sorularıyla, cevapları bilinmeden eğitim). Modeller Gemma 3 4B, Qwen 3 4B, Llama 3.1 8B.

**Sonuç:** Yazarların raporuna göre (başlangıç → CaT):
- HealthBench: Gemma 3 4B 0.35 → 0.43; Qwen 3 4B 0.39 → 0.43; Llama 3.1 8B 0.29 → 0.38. Göreli artış en fazla ~%30.
- MATH-500: Gemma 3 4B 0.70 → 0.78; Qwen 3 4B 0.78 → 0.83; Llama 3.1 8B 0.42 → 0.56.
- Eğitilmiş modelin tek cevabı, eğitimsiz modelde inference'ta synthesis yapmaya (8 cevap üretip birleştirmeye) eşit ya da daha iyi; üstelik ~9 kat daha az test-time compute ile.
- Rollout'lar birbirine benzediğinde kazanç duruyor: cevaplar aynıysa birleştirmek yeni bilgi vermiyor.

**Bizim için:** Gold SQL'i olmayan sorularda (kullanım verisi) küçük modelin birden çok SQL'inin sonuçlarını büyük modele birleştirtip pseudo-reference yapmak, `split = use` kayıtlarını da eğitime sokmanın bir yolu olabilir. Ama bizde train'in gold'u olduğu için önce gold'lu RL denenmeli.

## Learning to Reason as Action Abstractions with Scalable Mid-Training RL — RA3 (Apple + Northwestern + UIUC, Eylül 2025) — [2509.25810](https://arxiv.org/abs/2509.25810)
**Tek cümlede:** RL'den önce yapılan bir mid-training yöntemi; model her kod satırından önce "düşünmeli miyim yoksa doğrudan mı yazmalıyım" kararını öğreniyor. ICLR 2026.

**Problem:** RL'nin ne kadar iyi gideceği, RL'ye başlayan modelin ne kadar iyi hazırlandığına bağlı. Yazarlara göre mid-training en iyi, modelin seçeceği seçenek sayısı küçük ve kararın etkisini gördüğü mesafe kısa olduğunda çalışır. Token düzeyinde seçenek çok fazla (bütün vocabulary). Bu yüzden token'lar yerine "action abstraction"lar üzerinde çalışıyorlar: satır başına yalnızca iki seçenek, "düşün" ya da "doğrudan yaz".

**Ne yaptılar:**
1. **EM tarzı döngü:** EM (expectation-maximization), iki adımı sırayla tekrarlayan bir yöntemdir: önce gizli bilgiyi tahmin et, sonra modeli bu tahminle eğit.
2. **E-adımı (RL ile gizli kararı bulmak):** Uzmanın yazdığı her kod satırı için gizli bir karar (latent) aranıyor: satırdan önce `<act>` (doğrudan yaz) ya da `<think>` ile başlayan bir yorum satırı (kısa düşünce). Reward, bu karardan sonra uzmanın gerçek kod satırının ne kadar olası olduğu (log-likelihood). Yani bir düşünce, gerçek kodu daha tahmin edilebilir yapıyorsa ödül alıyor. Gereksiz düşünmeye ceza var (c = 0.05). Sonuçta satırların %40'ından azında düşünme çıkıyor.
3. **M-adımı:** Bu kararlarla zenginleştirilmiş veride normal next-token fine-tuning.
4. **Veri ve modeller:** OpenCoder'ın Python continued-pretraining alt kümesi. Modeller Qwen-2.5-1.5B, Llama-3.2-1B, Llama-3.1-8B.
5. **Ardından RLVR:** GRPO ile AReaL-boba-2-RL-Code (~7.7K kod problemi).

**Sonuç:** Yazarların raporuna göre:
- HumanEval / MBPP (kısa Python fonksiyonu yazma görevleri; testlerle puanlanıyor) ve daha çok testli sürümleri HumanEval+ / MBPP+'ın pass@1 ortalaması (base / NTP / RA3). NTP, aynı veriyle normal next-token eğitimi demek.
  - Llama-3.2-1B: 23.3 / 25.3 / 29.8
  - Qwen-2.5-1.5B: 37.9 / 41.7 / 46.6
  - Llama-3.1-8B: 41.0 / 47.7 / 48.9
- Yani RA3, aynı veriyle normal eğitime göre küçük modellerde 4–5 puan, 8B'de ~1 puan daha iyi. Kazanç küçük modellerde daha büyük.
- RLVR'de RA3 ile başlayan model daha hızlı yakınsıyor ve daha yüksek bir tavana çıkıyor.

**Kaynak notu:** RLVR kazancı yalnızca grafikte veriliyor; sayı yok.

**Bizim için:** RL'den önce, düşünmenin yalnızca gereken adımlarda olduğu kısa bir ara eğitim küçük modelde (1–1.5B) RL'yi hızlandırıyor. Bizde bu, trajectory'lerdeki gereksiz düşünce metnini atıp kısa adımlarla SFT yapmak anlamına gelebilir.

## Language Self-Play For Data-Free Training (Meta Superintelligence Labs + UC Berkeley, Eylül 2025) — [2509.07414](https://arxiv.org/abs/2509.07414)
**Tek cümlede:** Veri olmadan RL: aynı model Challenger olarak talimat yazıyor, Solver olarak cevaplıyor; iki rol birbirine karşı oynayarak gelişiyor.

**Problem:** RL için çok sayıda prompt gerekir ve bunları toplamak pahalıdır; eldeki veri bitince eğitim de durur. Yazarlar modelin kendi eğitim verisini üretip eğitimi süresiz sürdürebileceği bir düzen arıyor.

**Ne yaptılar:**
1. **İki rol, tek model:** Model özel bir prompt'la Challenger olarak talimat üretiyor, normal hâliyle Solver olarak cevaplıyor. Solver iyi cevap verdiği için, Challenger Solver'ı zorladığı için ödül alıyor.
2. **Algoritma:** İki rol de GRPO tarzı, grup göreli advantage kullanıyor. Challenger'ın anlamsız metne kaymasını, reference model'e (başlangıç modeline) KL cezası önlüyor.
3. **İki sürüm:** LSP-Zero saf sıfır toplamlı bir oyun (birinin kazancı diğerinin kaybı). LSP buna bir kalite self-reward'ı ekliyor: reference model cevabı 7 puanlık bir rubric'le puanlıyor. Yazarlara göre bu ek, eğitimi süresiz sürdürülebilir yapıyor.
4. **Model ve RM:** Llama-3.2-3B-Instruct. RM: Skywork-Reward-V2-Llama-3.2-3B. OpenAssistant RM ile AlpacaEval iyileşmemiş.

**Sonuç:** Yazarların raporuna göre, AlpacaEval'de (talimat takibi; bir LLM judge'ın, cevabı güçlü bir referans modelin cevabına tercih etme oranı) kazanma oranı:
- Base %26.5.
- Alpaca verisiyle GRPO (gerçek veriyle normal RL) %38.8.
- LSP-Zero %32.0; LSP %36.4; LSP'den sonra RL %39.5.
- Yani hiç veri kullanmayan LSP, gerçek veriyle yapılan GRPO'nun kazancının çoğunu (12.3 puanın ~10 puanını) geri getiriyor. Bazı görevlerde LSP'nin kazancı sınırlı.

**Bizim için:** BIRD train zaten yeterli soru veriyor. Self-play bizim için ancak train soruları tükendiğinde, yeni sorular üretmek için ikinci planda düşünülmeli.

## CoT-Self-Instruct: Building high-quality synthetic prompts for reasoning and non-reasoning tasks (Meta FAIR, Temmuz 2025) — [2507.23751](https://arxiv.org/abs/2507.23751)
**Tek cümlede:** Birkaç seed sorudan, LLM'e önce adım adım plan yaptırıp benzer zorlukta yeni sentetik sorular ürettiler, sonra otomatik filtrelerle süzüp RLVR ve DPO'da kullandılar.

**Problem:** RL ve DPO için iyi soru bulmak zor; insan yazımı sorular az ve pahalı. Basit sentetik soru üretimi (Self-Instruct) ise kolay, tekrarlı ya da cevabı yanlış sorular üretir. Yazarlar daha kaliteli sentetik soru üretmek ve kötülerini otomatik ayıklamak istiyor.

**Ne yaptılar:**
1. **CoT ile üretim:** LLM'e seed sorular gösteriliyor. Model önce onların ne istediğini ve ne kadar zor olduğunu adım adım düşünüyor, sonra benzer zorlukta yeni bir soru (ve doğrulanabilir görevlerde hedef cevabı) yazıyor.
2. **Doğrulanabilir görevlerde filtre, Answer-Consistency:** Soru için K çözüm üretiliyor. Çözümlerin çoğunluk cevabı, üreticinin yazdığı hedef cevapla eşleşmezse soru atılıyor (ya soru belirsiz ya hedef cevap yanlış).
3. **Doğrulanamayan görevlerde filtre, RIP:** Talimat için K cevap üretilip RM ile puanlanıyor. Talimatın puanı, bu cevapların en düşük RM skoru. En yüksek puanlı talimatlar tutuluyor (en kötü cevabı bile iyi olan talimat, açık ve iyi yazılmış demektir).
4. **Seed:** s1k'dan 893 doğrulanabilir soru; ~4k WildChat (gerçek kullanıcı sohbetleri) talimatı.
5. **Reasoning eğitimi:** Qwen3-4B-Base üzerinde GRPO (lr 1e-6, 40 epoch, batch 128, prompt başına 16 rollout).
6. **Talimat takibi:** Llama 3.1-8B-Instruct üzerinde DPO (lr 1e-6, β 0.1, talimat başına 64 cevap, 5,000 çift).

**Sonuç:** Yazarların raporuna göre:
- MATH500 / AMC23 / AIME24 / GPQA-D ortalaması:
  - base 36.1
  - s1k + R1 cevapları (893 insan sorusu): 44.6
  - OpenMathReasoning (10,000 soru): 47.5
  - Self-Instruct (5,000 sentetik): 42.7
  - CoT-Self-Instruct (5,000 sentetik): 53.0
  - CoT-Self-Instruct + Answer-Consistency filtresi (2,926 soru kaldı): 57.2
  - 10,000 filtrelenmiş soruya çıkınca: 58.7
- Yani filtrelenmiş 2,926 sentetik soru, 10,000 insan/gold sorudan (47.5) yaklaşık 10 puan iyi. Filtre tek başına, soru sayısı azalmasına rağmen 4 puan ekliyor.
- Talimat takibinde (AlpacaEval 2 ve Arena-Hard: zor kullanıcı sorularında judge'ın tercih oranı) CoT-Self-Instruct + RIP 54.7, WildChat insan verisi + RIP 50.7.

**Bizim için:** RL verisinde birkaç bin iyi filtrelenmiş soru, on binlerce filtresiz sorudan iyi. BIRD train sorularını da "büyük modelin çoğunluk cevabı gold'la eşleşiyor mu" diye süzmek, etiketi hatalı soruları atar.

## Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities (Google DeepMind, Temmuz 2025) — [2507.06261](https://arxiv.org/abs/2507.06261)
**Tek cümlede:** Gemini 2.5 Pro, Flash ve Flash-Lite raporu; post-training yalnızca genel hatlarıyla anlatılıyor, küçük modellerin distillation ile üretildiği yazıyor.

**Problem:** Google, en güçlü modelinin yanında daha ucuz ve hızlı modeller de sunmak istiyor. Bu küçük modelleri büyük modelin bilgisini aktararak üretmek, sıfırdan eğitmekten verimli. Ayrıca thinking modellerinin inference'ta daha çok compute kullanarak daha iyi cevap vermesi isteniyor.

**Ne yaptılar:**
1. **SFT:** "Dikkatle toplanıp denetlenmiş" instruction tuning verisi. SFT, reward modeling ve RL boyunca veri kalitesine odaklanılıyor. Süreçlere modelin kendisi de yardım ediyor (model-assisted).
2. **RL:** RL'ye ayrılan training compute artırılmış. Reward'larda doğrulanabilir reward'lar ve model tabanlı generative reward'lar (cevabı metinle değerlendiren modeller) birlikte kullanılıyor.
3. **Thinking:** Thinking modelleri, inference'ta ek compute kullanmak için RL ile eğitiliyor.
4. **k-sparse distillation:** Flash ve daha küçük modeller distillation ile eğitiliyor. Büyük modelin sonraki token dağılımı, vocabulary'nin tamamı yerine en olası k token'la yaklaşıklanıyor. Örneğin çok büyük bir vocabulary'de yalnızca en olası birkaç token'ın olasılığı saklanıyor, gerisi sıfır sayılıyor. Rapora göre veri akışı ve depolama yükü k kat artsa da (yalnızca doğru token yerine k token saklandığı için) kaliteye değiyor.

**Sonuç:** Yazarların raporuna göre post-training aşamalarına ait ablation ya da sayısal ayrıştırma yok.

**Kaynak notu:** Veri boyutları, algoritma ve hiperparametreler raporda yok; reçete yalnızca genel hatlarıyla anlatılıyor.

**Bizim için:** Büyük modelin tam dağılımı yerine en olası k token'ını saklamak, 9B'den 0.8B'ye logit distillation'ı Mac'in diskine sığdırmanın standart yolu.

## Apple Intelligence Foundation Language Models Tech Report 2025 (Apple, Temmuz 2025) — [2507.13575](https://arxiv.org/abs/2507.13575)
**Tek cümlede:** Apple'ın cihaz üstünde çalışan (~3B) ve sunucuda çalışan modellerinin raporu; post-training SFT + RLHF, cihaz modeli ise bir MoE'den distillation ile eğitiliyor.

**Problem:** Telefonda çalışacak bir model küçük olmak zorunda, ama kalitesi yüksek olmalı. Büyük bir modeli eğitip ondan distillation yapmak pahalı. Apple hem küçük modeli ucuza güçlendirmek hem de RL altyapısını verimli kurmak istiyor.

**Ne yaptılar:**
1. **SFT:** İnsan yazımı örnekler ve sentetik veri: genel bilgi, CoT'li reasoning, OCR (görüntüdeki yazıyı okuma), grounding (görüntüde bir nesneyi bulma), çoklu görüntü. Veri boyutu verilmemiş.
2. **RLHF (insan geri bildirimiyle RL):** Algoritma RLOO (REINFORCE Leave-One-Out): her cevabın kıyas noktası, aynı soruya verilen diğer cevapların ortalaması; ayrı bir value network (değer tahmin eden ikinci model) gerekmiyor. İki modelde de bütün parametreler güncelleniyor.
3. **Reward:** Metin ve görüntü-metin tercih verisiyle eğitilmiş bir RM; matematik ve STEM için kural tabanlı cevap doğrulama.
4. **Prompt seçimi:** "Cohesion" başlıklı ayrı bir RM ve komşuluk araması (benzer prompt'ları bulma) ile tutarlı prompt'lar seçiliyor. Bağlam olarak: insan değerlendiriciler tercih verisinin %20–30'unda anlaşamıyor; yani tercih etiketleri gürültülü.
5. **Asenkron RL altyapısı:** Trajectory üreticiler ve bir replay buffer (üretilen trajectory'lerin beklediği havuz). Senkron sisteme göre %37.5 daha az cihaz ve %75 daha az süre.
6. **Cihaz modeli için distillation:** ~14T token'la eğitilmiş dense model, 1T token'la 64 uzmanlı bir MoE'ye sparse-upcycle ediliyor (dense modelin katmanları kopyalanıp uzmanlara dönüştürülüyor). Sonra dense model son ~1.4T token'da bu MoE'den distillation kaybıyla yeniden eğitiliyor. Böylece büyük model ayrıca sıfırdan eğitilmiyor; büyük model eğitim maliyeti %90 azalıyor.

**Sonuç:** Yazarların raporuna göre, metin prompt setiyle RLHF, RLHF öncesine göre:
- Arena Hard'da (zor kullanıcı sorularında judge'ın tercih oranı) ~%4 artış.
- AlpacaEval'de GPT-4 Turbo'ya karşı kazanma oranında %7 artış.
- GPQA'da %7, Math500'de %5 artış.
- İnsan değerlendirmesinde RLHF'li model SFT'li modeli 16:9 kazanma/kaybetme oranıyla geçiyor; yani kazanılan her 16 karşılaştırmaya karşılık 9 kaybediliyor.

**Bizim için:** RLOO, value network'süz ve on-policy olduğu için Mac'te en basit RL seçeneklerinden biri. Reward'ı karışık olan prompt'ları RL'den önce elemek bütçeyi korur.

## Decoder-Hybrid-Decoder Architecture for Efficient Reasoning with Long Generation — Phi-4-mini-flash-reasoning (Microsoft, Temmuz 2025) — [2507.06607](https://arxiv.org/abs/2507.06607)
**Tek cümlede:** Asıl katkı uzun üretimde hızlı çalışan yeni bir mimari (SambaY); bu mimariyle eğitilen 3.8B Phi4-mini-Flash-Reasoning, RL kullanmadan yalnızca SFT ve DPO ile eğitildi. NeurIPS 2025.

**Problem:** Reasoning modelleri çok uzun cevap üretir (on binlerce token). Normal transformer'da her yeni token önceki bütün token'lara baktığı için uzun üretim yavaşlar ve bellek tüketir. Yazarlar uzun üretimi hızlandıran bir mimari arıyor ve bunun reasoning kalitesini koruyup korumadığına bakıyor.

**Ne yaptılar:**
1. **Mimari:** SambaY, decoder-hybrid-decoder yapısında. Gated Memory Unit (GMU) adlı bir birim, katmanlar arasında bellek paylaşımı sağlıyor: üst katmanlar, alt katmanların hesapladığı bir temsili yeniden hesaplamadan kullanıyor. Sonuç, uzun üretimde daha az hesap.
2. **Pretraining:** 5T token (Phi4-mini verisi), 1K A100 GPU'da 14 gün. Eğitim ıraksadığı (kayıp kontrolsüz büyüdüğü) için iki düzenleme eklenmiş: label smoothing 0.1 (doğru token'a %100 yerine biraz daha az olasılık hedeflemek) ve attention dropout 0.05 (attention ağırlıklarının bir kısmını eğitimde rastgele sıfırlamak).
3. **Post-training:** Phi4-mini-Reasoning ile "aynı çok aşamalı distillation verisi" (bkz. bu dosyadaki Phi-4-Mini-Reasoning girdisi). Yalnızca SFT ve DPO; RL aşaması yok. Hiperparametreler ekte.

**Sonuç:** Yazarların raporuna göre, Phi4-mini-Reasoning'e karşı (pass@1, 32K token üretim):
- AIME24 48.13 → 52.29; AIME25 31.77 → 33.59.
- Math500 91.20 → 92.45; GPQA-D 44.51 → 45.08.
- Yani RL'li öncülünü bütün benchmark'larda geçiyor; fark AIME24'te ~4 puan, diğerlerinde 1–2 puan.
- 2K prompt + 32K üretimde, vLLM'de (yaygın bir inference motoru) 10 kata kadar daha hızlı decoding.

**Bizim için:** İyi bir distillation verisi + SFT + DPO, RL olmadan da 3.8B'de RL'li sürümün seviyesine çıkabiliyor (mimari de değiştiği için kazancın hepsi eğitimden gelmiyor olabilir). RL'yi ancak bu basit hat doyduktan sonra eklemek yeterli.

## Bridging Offline and Online Reinforcement Learning for LLMs (Meta FAIR + NYU, Haziran 2025) — [2506.21495](https://arxiv.org/abs/2506.21495)
**Tek cümlede:** DPO ve GRPO'yu, cevapları ne sıklıkla yeniden ürettiklerine göre offline, semi-online ve online rejimlerde karşılaştırdılar; hem doğrulanabilir hem doğrulanamayan görevlerde.

**Problem:** Offline eğitim (cevapları bir kez üretip sonra hep onlarla eğitmek) ucuz ama model değiştikçe veri eskir. Online eğitim (her adımda güncel modelle yeni cevap üretmek) daha iyi ama pahalı. Aradaki seçeneklerin ne kadar iyi olduğu bilinmiyordu.

**Ne yaptılar:**
1. **Model:** Llama-3.1-8B-Instruct.
2. **Doğrulanabilir görev:** NuminaMath'ten 261,440 matematik problemi; Math-Verify ile ikili reward (doğru 1, yanlış 0).
3. **Doğrulanamayan görev:** WildChat-1M (gerçek kullanıcı sohbetleri) prompt'ları; reward Athene-RM-8B adlı bir reward model'den.
4. **Senkron aralığı s:** Cevapları üreten model her s adımda bir, eğitilen modelin güncel hâliyle değiştiriliyor.
   - s = ∞: offline DPO (cevaplar baştan bir kez üretilir).
   - s = 1: online DPO ve GRPO (her adımda güncel model üretir).
   - s = 5 / 10 / 100: semi-online DPO.
5. **Birlikte eğitim:** İki görev ayrı ayrı ve birlikte eğitildi.

**Sonuç:** Yazarların raporuna göre:
- Math500: seed (başlangıç) 47.4, offline DPO 53.7, semi-online DPO (s=10) 57.2, online DPO 58.7, GRPO 58.1.
- AlpacaEval LC (uzunluk kontrollü AlpacaEval: uzun cevap yazarak kazanmayı engelleyen sürüm): 21.3 / 38.3 / 59.4 / 60.1 / 55.0.
- Yani semi-online ve online birbirine çok yakın; ikisi de offline'dan çok iyi (talimat takibinde ~21 puan).
- İki görevi birlikte eğitmek (online DPO): Math500 57.3, AlpacaEval LC 65.6; talimat takibi tek başına eğitimden daha iyi.
- Doğrulanabilir görevde online rejimlerde entropy belirgin düşüyor.
- DPO'nun kıyas aldığı reference model eğitim boyunca güncellenmezse, online DPO'da cevap uzunluğu çöküyor.

**Bizim için:** Cevapları her adımda değil her 5–10 adımda yeniden üretmek (semi-online DPO) neredeyse tam online kadar iyi. Mac'te rollout üretimi pahalı olduğu için bu bizim için en uygun orta yol.

## Magistral (Mistral AI, Haziran 2025) — [2506.10910](https://arxiv.org/abs/2506.10910)
**Tek cümlede:** Mistral'in ilk reasoning modelleri: Magistral Medium başka reasoning modellerinden distillation olmadan yalnızca RL ile, Magistral Small (24B) ise Medium'un trace'leriyle SFT + RL ile eğitildi.

**Problem:** Reasoning modellerinin çoğu, başka bir reasoning modelinin (ör. DeepSeek-R1) çıktılarıyla distillation yapılarak üretiliyor. Mistral, yalnızca kendi RL hattıyla bir reasoning modeli kurmak ve RL'nin tek başına ne kadar ileri gittiğini görmek istiyor. Küçük model için de SFT ile RL'nin nasıl birleşmesi gerektiğini ölçüyorlar.

**Ne yaptılar:**
1. **GRPO değişiklikleri:**
   - KL cezası yok.
   - Loss, batch'teki toplam üretim uzunluğuyla (token sayısıyla) normalize ediliyor.
   - Advantage minibatch içinde normalize ediliyor.
   - Clip-higher: ε_high Medium'da entropy'yi sabit tutmak için 0.26–0.28 arasında, Small'da 0.3.
   - Bütün cevapları aynı anda doğru ya da aynı anda yanlış olan gruplar atılıyor (öğrenme sinyali yok).
2. **Reward:** Biçim 0.1 + doğruluk 0.9. Üretim uzunluk sınırına yaklaşınca yumuşak bir length penalty. Kullanıcının dilinde düşünmeye dil tutarlılığı bonusu (dil fastText ile, yani bir dil tanıma aracıyla tespit ediliyor).
3. **Matematik verisi:** ~699k soru → biçim filtresiyle 501k → zorluk filtresiyle 38k. Zorluk filtresi iki aşamalı:
   - Mistral Large 2 her soruya 16 çözüm üretiyor; hiç çözülmeyen ve çok kolay sorular atılıyor.
   - Bu setle RL'lenen 24B model tüm havuzu yeniden 16 örnekle puanlıyor; en kolaylar ve hâlâ çözülmeyenler atılıyor.
   - Örneklerin çoğunun referans cevapla çeliştiği sorular etiket hatası sayılıp atılıyor (model hep aynı farklı cevabı veriyorsa, referans büyük olasılıkla yanlıştır).
4. **Kod verisi:** ~35k problem. Testi yetersiz problemler atılmış; testler, çözümlerin çoğunluğunun ürettiği çıktıya göre düzeltilmiş.
5. **Curriculum:** Cezasız uzunluk 16k → 24k → 32k token'a çıkarken batch 8k → 4k → 2k'ya iniyor.
6. **Magistral Small:** OpenThoughts ve OpenR1 code prompt'larına Medium'un trace'leri, Medium'un RL'inden çıkan doğru trace'ler ve %10 genel instruction verisi. 4 epoch SFT, sonra RL (batch 2048).

**Sonuç:** Yazarların raporuna göre:
- Magistral Medium, AIME'24 pass@1'de 26.8'den (başlangıç modeli) 73.6'ya çıkıyor; yalnızca RL ile ~47 puan.
- Small ablation'ı (yalnız SFT / yalnız RL / SFT+RL):
  - AIME'24: 65.4 / 65.8 / 70.7
  - AIME'25: 55.6 / 51.9 / 62.8
  - LiveCodeBench v5: 52.2 / 46.4 / 55.8
  - Yani ikisini birleştirmek, her birinden 3–7 puan daha iyi.
- Yalnızca metin üzerinde RL, multimodal reasoning'i koruyor ya da artırıyor: MMMU'da (üniversite düzeyi görsel sorular) ~%5 artışla ~%70. IFEval (biçim kurallı talimatlara uyma) ve function calling yerinde ya da biraz daha iyi.
- İşe yaramayanlar: kod testlerinde kısmi reward (testlerin bir kısmı geçince kısmi puan) ve entropy bonusu.

**Bizim için:** Küçük modelde SFT + RL, yalnız RL'den açıkça iyi. RL verisini önce büyük modelle, sonra RL'lenmiş modelle iki kez zorluk filtresinden geçirmek ve tutarlı biçimde yanlış görünen soruları etiket hatası saymak doğrudan uygulanabilir.

## J1: Incentivizing Thinking in LLM-as-a-Judge via Reinforcement Learning (Meta FAIR, Mayıs 2025) — [2505.10320](https://arxiv.org/abs/2505.10320)
**Tek cümlede:** Cevapları değerlendiren bir LLM'i (generative judge), karar vermeden önce düşünecek şekilde online RL ile eğittiler.

**Problem:** LLM-as-judge (bir LLM'in cevapları puanlaması) RL'de reward için ve değerlendirmede çok kullanılıyor. Ama judge'lar yanılıyor ve cevapların gösterilme sırasından etkileniyor (position bias: ilk gösterilen cevabı daha çok seçmek gibi). Değerlendirme görevlerinin çoğunda doğru karar otomatik bilinmediği için judge'ı RL ile eğitmek de zor.

**Ne yaptılar:**
1. **Doğrulanabilir hâle çevirmek:** Hangi cevabın daha iyi olduğu bilinen sentetik tercih çiftleri kuruldu: ~22K çift (17K WildChat, 5K MATH). Böylece judge'ın kararının doğru olup olmadığı bilinir ve reward "karar doğru mu" (1 ya da 0) olur.
2. **Algoritma:** GRPO.
3. **Position bias'a karşı tutarlılık reward'ı:** Aynı çift iki sırayla da gösteriliyor; reward için iki sırada da doğru karar gerekiyor.
4. **Varyantlar:** Pairwise (iki cevabı karşılaştırıp birini seçer), pointwise (her cevaba ayrı puan verir; yalnızca pairwise etiketlerden eğitiliyor) ve multitask (ikisi birlikte).
5. **Modeller:** Base modeller Llama-3.1 ve Qwen3; 8B, 32B ve 70B.

**Sonuç:** Yazarların raporuna göre:
- PPE Correctness'ta (judge'ın doğrulanabilir sorularda doğru cevabı seçme oranı) J1-Qwen-32B-MultiTask 76.8. Karşılaştırma: EvalPlanner-Llama-70B 70.2, eğitimsiz Qwen3-32B 66.5. Yani 32B model, 70B'lik önceki judge'ı 6.6 puan geçiyor.
- RewardBench (reward model'lerin insan tercihini doğru tahmin etme oranı) 93.6.
- Beş benchmark'ın üçünde o3 ve R1'i geçiyor.
- Ablation: yalnızca "karar doğru mu" reward'ı en iyisi; negatif ya da biçim reward'ı eklemek biraz zarar veriyor.
- Pointwise judge sıraya daha tutarlı ama daha çok beraberlik veriyor.
- Test anında birden çok örnek ortalamak tutarlılığı artırıyor.

**Bizim için:** Final check'teki büyük model kontrolü, cevap sırası değiştirilerek ve yalnızca "karar doğru mu" reward'ıyla küçük bir judge olarak eğitilebilir. Ama bizde puanlamayı zaten BIRD'ün result key'i yaptığı için bu ikinci öncelik.

## Phi-4-reasoning Technical Report (Microsoft, Nisan 2025) — [2504.21318](https://arxiv.org/abs/2504.21318)
**Tek cümlede:** 14B Phi-4'ü o3-mini'nin reasoning cevaplarıyla SFT edip Phi-4-reasoning'i, buna kısa bir RL ekleyip Phi-4-reasoning-plus'ı elde ettiler; ana fikir "teachable" (öğretilebilir) prompt seçimi.

**Problem:** SFT verisinin büyük kısmı ya model için çok kolay (hiçbir şey öğretmez) ya da çok zor (model öğrenemez). Yazarlar, modelin tam yeteneğinin sınırındaki soruları seçerek SFT'yi daha verimli yapmak istiyor.

**Ne yaptılar:**
1. **SFT verisi:** 1.4M'den fazla prompt-cevap çifti, ~8.3B tekil token; matematik, kod ve güvenlik. Prompt'lar web'den, mevcut veri setlerinden, lisanslı koleksiyonlardan ve sentetik üretimden.
2. **Cevaplar:** Yüksek reasoning effort'ta (uzun düşünme ayarında) o3-mini'den.
3. **Zorluk tahmini:** Bir soru için zayıf modellerin cevabının bir proxy ground truth'la (gerçek cevap yerine kullanılan güçlü bir tahminle) ne sıklıkla anlaştığına bakılıyor. Modelin sınırında olan seed sorular tutuluyor.
4. **Dekontaminasyon:** Birçok benchmark'ın sorularına benzeyen örnekler atılıyor.
5. **Eğitim:** lr 1e-5, 450 adım warmup (lr'nin yavaş yavaş artırıldığı başlangıç), ~16K adım, batch 32, 32K bağlam, toplam ~16B token. Veri karışımının ağırlıkları her alan için ayrı ayarlanıyor, sonra bu ağırlıklar toplanarak birleştiriliyor.
6. **RL (plus sürümü):** Yalnızca ~6K matematik problemiyle GRPO. Reward = uzunluğa duyarlı doğruluk (ağırlık 8/13) + tekrar cezası (ağırlık 1/13). 90. adımdaki checkpoint seçilmiş; sonrası kazanç vermemiş.

**Sonuç:** Yazarların raporuna göre (reasoning / plus):
- AIME 2025: 63.1 / 78.0; DeepSeek-R1 70.4. Yani yalnızca ~90 RL adımı 15 puan ekliyor ve 14B model, çok daha büyük R1'i geçiyor.
- HMMT (Harvard-MIT matematik turnuvası soruları): 43.8 / 53.6.
- GPQA-D: 67.1 / 69.3.
- Plus ~1.5 kat daha uzun cevap üretiyor.
- Yazarlar AIME skorlarının koşudan koşuya çok değiştiğini ve tek koşuluk karşılaştırmaların güvenilmez olduğunu vurguluyor.

**Bizim için:** SFT için modelin yarı yarıya çözdüğü soruları seçmek ve SFT'den sonra yalnızca birkaç bin soruyla, kısa (onlarca adım) bir RL eklemek. SFT verisi RL verisinden iki büyüklük mertebesi fazla (1.4M'ye karşı ~6K soru).

## Phi-4-Mini-Reasoning: Exploring the Limits of Small Reasoning Language Models in Math (Microsoft, Nisan 2025) — [2504.21233](https://arxiv.org/abs/2504.21233)
**Tek cümlede:** 3.8B Phi-4-Mini için dört aşamalı bir reçete (distillation mid-training → SFT → rollout DPO → RLVR); küçük modelde küçük distillation setlerinin yetmediğini, büyük ölçekli distillation'ın şart olduğunu gösteriyor.

**Problem:** Büyük modellerde birkaç yüz ya da bin örneklik küçük, seçkin distillation setleri (LIMO, S1K) reasoning'i açmaya yetiyor. Yazarlar bunun 3.8B gibi küçük bir modelde işe yaramadığını gördü. Küçük model için hangi aşamaların, hangi sırayla gerektiğini arıyorlar.

**Ne yaptılar:**
1. **Distillation mid-training:** DeepSeek-R1'in ürettiği ~10M rollout (1.6M soru, soru başına ~8). Rejection sampling ile yalnızca doğru cevaplar tutuluyor. Packing ile (birden çok kısa örneği tek uzun diziye art arda koyarak) eğitiliyor, doğrulama skoru doyana kadar.
2. **SFT:** Daha küçük, kaliteli, üniversite üstü zorlukta bir alt küme; packing'siz, 20K uzunluk. Aşama 1–2'de batch 128, lr 1e-5, 5 epoch.
3. **Rollout DPO:** Modelin kendi doğru rollout'u tercih edilen, yanlış rollout'u reddedilen cevap oluyor. Sorular GPT-4o-mini ile lise ve üstü zorluğa süzülmüş. lr 5e-7, 1 epoch.
4. **RL:** Final cevaba göre +1/−1 reward, GRPO tarzı, 25K uzunluk, lr 5e-7.
5. **RL kararlılık önlemleri:**
   - Cevap uzunlukları birbirine yakın prompt'ları tutmak.
   - Fazla örnek üretip (oversample) bütün doğru cevapları tutmak ve onları yanlışlarla eşlemek; grup doğruluğu %50'nin üstündeki prompt'ları atmak.
   - Temperature'ı eğitimin ilk yarısında 1.0'dan 0.6'ya indirmek (önce çok keşif, sonra daha kararlı cevaplar).

**Sonuç:** Yazarların raporuna göre:
- MATH-500 94.6 (DeepSeek-R1-Distill-Qwen-7B 91.4); AIME 2024 57.5 (53.3); GPQA-D 52.0 (49.5). Yani 3.8B model, kendisinden neredeyse iki kat büyük bir distill modeli üç benchmark'ta da geçiyor.
- Aşama ablation'ı (AIME / MATH-500):
  - base: 10.0 / 71.8
  - mid-training: 30.0 / 82.9
  - SFT: 43.3 / 89.3
  - rollout DPO: 50.0 / 93.6
  - RL: 57.5 / 94.6
  - En büyük sıçrama distillation mid-training'den (AIME'de +20); her sonraki aşama 7–13 puan daha ekliyor.
- DAPO ile eğitimde consensus@16 (16 cevabın çoğunluk oyunun doğruluğu) AIME'de eğitim boyunca düşerken, yazarların yöntemi kararlı kalıyor.

**Bizim için:** 0.8B–4B'de en büyük sıçrama büyük ölçekli distillation'dan geliyor (AIME 10 → 30 → 43). Küçük modelin kendi doğru ve yanlış rollout'larıyla DPO, RL'den önce ucuz ve etkili bir ara adım; experience log'daki başarılı ve başarısız trajectory'ler tam bu çiftleri veriyor.

## The Llama 4 herd (Meta, Nisan 2025) — [blog](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)
**Tek cümlede:** Meta'nın Llama 4 ailesi; post-training sırası "hafif SFT → online RL → hafif DPO" olarak değiştirildi ve Maverick, dev Behemoth modelinden codistillation ile eğitildi.

**Problem:** Meta'ya göre ağır SFT ve DPO modeli fazla kısıtlıyor; model belirli bir cevap biçimine kilitlenince online RL'de yeni yollar keşfedemiyor. Ayrıca kolay örnekler SFT verisinin çoğunu kaplıyor ve bir şey öğretmiyor. Yazarlar SFT'yi küçültüp RL'ye daha çok alan bırakmak istiyor.

**Ne yaptılar:**
1. **Modeller:** Llama 4 Scout, Maverick (17B aktif, 400B toplam parametre) ve önizlemesi yapılan Behemoth (288B aktif, ~2T toplam).
2. **Maverick, hafif SFT:** Llama modelleri judge olarak "kolay" veriyi işaretledi; bunun %50'den fazlası atıldı. SFT kalan zor sette yapıldı.
3. **Maverick, online RL:** Dikkatle seçilmiş zor prompt'larla multimodal online RL. Sürekli online RL'de eğitim ile veri havuzunu yeniden filtreleme dönüşümlü yapılıyor; yalnızca orta-zor prompt'lar tutuluyor.
4. **Maverick, hafif DPO:** En sonda, yanıt kalitesindeki uç durumlar için.
5. **Behemoth:** SFT verisinin %95'i budandı. Prompt zorluğu pass@k analiziyle (k denemeden en az birinin doğru olma oranı) belirlendi ve zorluğu artan bir curriculum uygulandı. Sıfır advantage'lı prompt'lar dinamik olarak atıldı. Batch'lerde farklı yeteneklerden prompt'lar karıştırıldı. Talimat takibini korumak için çeşitli sistem talimatları örneklendi. Asenkron online RL çerçevesi önceki nesle göre ~10 kat verimli.
6. **Codistillation:** Maverick, Behemoth'un çıktılarından öğreniyor. Yeni bir distillation kaybı, soft hedefleri (büyük modelin olasılık dağılımı) ve hard hedefleri (gerçek token) eğitim boyunca dinamik olarak ağırlıklandırıyor. Behemoth'un kendi eğitimi sırasında hesaplanan çıktılar yeniden kullanılıyor; Behemoth ek forward pass'i yalnızca küçük modelin eğitimine eklenen yeni veri için yapıyor.

**Sonuç:** Blog post-training veri boyutu ya da RL adım sayısı vermiyor; ablation sayısı da yok.

**Kaynak notu:** Kaynak yalnızca resmi blog; technical report yok ve hiçbir aşamanın katkısı sayıyla verilmemiş.

**Bizim için:** SFT verisini küçük tutup kolay örnekleri atmak ve RL'ye geniş bir keşif alanı bırakmak; RL sırasında havuzu periyodik olarak yeniden süzüp yalnızca orta-zor soruları tutmak.

## Gemma 3 Technical Report (Google DeepMind, Mart 2025) — [2503.19786](https://arxiv.org/abs/2503.19786)
**Tek cümlede:** 1B–27B açık modeller; pretraining'de ve post-training'de büyük bir modelden distillation, post-training'de distillation'ın ardından RL fine-tuning.

**Problem:** Küçük açık modellerin kalitesi büyük modellerin çok gerisinde. Büyük bir modelin bilgisini hem pretraining'de hem post-training'de küçük modele aktarmak, aynı compute ile daha iyi model verir. Ama büyük modelin bütün vocabulary üzerindeki dağılımını her token için saklamak çok pahalı.

**Ne yaptılar:**
1. **Pretraining distillation:** Her token için büyük modelin olasılıklarına göre 256 token (logit) örnekleniyor. Örneklenmeyen token'ların olasılığı sıfırlanıp kalanlar yeniden normalize ediliyor (toplamları 1 yapılıyor). Küçük model bu kırpılmış dağılımı cross-entropy ile öğreniyor.
2. **Post-training distillation:** Büyük bir instruction-tuned modelden geliştirilmiş knowledge distillation. Yöntem Hinton'un ve Anil'in çalışmalarına ve GKD'ye dayanıyor. GKD, [on-policy distillation](00_terimler.md#on-policy-distillation-opd)'dır: küçük model kendi ürettiği metin üzerinde büyük modelin dağılımını öğrenir.
3. **RL:** BOND, WARM ve WARP'ın geliştirilmiş sürümlerine dayanıyor. BOND, "N cevap üret, en iyisini seç" davranışını tek cevaba damıtır. WARM, birden çok reward model'in ağırlıklarını ortalar. WARP, RL ile eğitilmiş policy'lerin ağırlıklarını ortalar. Ağırlık ortalaması için bkz. [model merging](00_terimler.md#model-merging).
4. **Reward'lar:** İnsan geri bildirimiyle eğitilmiş, ağırlıkları ortalanmış reward model'ler; kod için çalıştırma geri bildirimi; matematikte ground-truth (doğru cevap) reward'ı.
5. **Veri filtreleme:** Kişisel bilgi, güvensiz/toksik çıktı, yanlış kimlik ve tekrarlar atılıyor. Kaynak gösteren, temkinli (hedging) ve reddeden örnekler ekleniyor.

**Sonuç:** Yazarların raporuna göre:
- Gemma 3 27B IT: Chatbot Arena'da (insan oylarıyla model sıralaması) 1338 Elo; Mart 2025'te ilk 10'da.
- MATH (lise yarışma matematiği) 89.0.
- Bu notta önceki Gemma sürümüyle karşılaştırma rakamı yok; post-training aşamalarına ait ablation da yok.

**Bizim için:** Logit distillation'da yalnızca 256 örneklenmiş logit'i saklamak, 9B → 0.8B distillation'ı yerelde uygulanabilir kılar. Birden çok RL koşusunun ağırlıklarını ortalamak (WARP tarzı) ucuz bir kararlılık hilesi.

## SWE-RL: Advancing LLM Reasoning via Reinforcement Learning on Open Software Evolution (Meta + UIUC + CMU, Şubat 2025) — [2502.18449](https://arxiv.org/abs/2502.18449)
**Tek cümlede:** Gerçek GitHub PR'larından (pull request: bir koda önerilen değişiklik), kodu çalıştıracak bir ortam kurmadan, kural tabanlı bir benzerlik reward'ıyla yazılım görevlerinde RL. NeurIPS 2025.

**Problem:** Yazılım hatası düzeltme görevlerinde RL için genelde her proje için çalışan bir ortam (bağımlılıklar, testler) gerekir. Bunu binlerce proje için kurmak çok pahalı. Yazarlar, ortam kurmadan yalnızca gerçek düzeltmeye benzerlikle ödül vermenin yetip yetmediğini test ediyor.

**Ne yaptılar:**
1. **Veri:** Ham GitHub PR verisinden 273k PR seed'i seçildi. Koşullar: en az bir bağlı issue (hata kaydı) olması, issue'nun bir hata düzeltme isteği olması ve değişikliklerin kod dosyalarına dokunması.
2. **Görev:** Model issue'yu ve ilgili kodu görüp bir patch (kod değişikliği) üretiyor.
3. **Reward:** Biçim yanlışsa −1. Değilse, modelin patch'i ile PR'daki gerçek patch arasındaki `difflib.SequenceMatcher` benzerliği (0 ile 1 arası; iki metin ne kadar ortak parça paylaşıyorsa o kadar yüksek).
4. **Model ve algoritma:** Base Llama-3.3-70B-Instruct, GRPO.

**Sonuç:** Yazarların raporuna göre:
- Llama3-SWE-RL-70B, Agentless Mini ile (agent döngüsü olmadan, hatayı bulup düzelten basit bir hat) SWE-bench Verified'da %41.0 alıyor. Bu notta base model rakamı yok.
- Beş alan dışı görevde (function coding, kütüphane kullanımı, code reasoning, matematik, genel dil anlama) iyileşme var. Aynı veriyle yapılan SFT baseline'ı ise bu görevlerde ortalamada geriliyor. Yani RL yalnızca eğitildiği işi değil, genel reasoning'i de iyileştiriyor; SFT ise bozuyor.

**Kaynak notu:** Grup boyu, adım sayısı ve lr, makalenin okunan abs/HTML kısmında yok.

**Bizim için:** Çalıştırılabilir reward yokken bile gold'a metin benzerliği işe yarıyor. Bizde gerçek çalıştırma ve result key olduğu için asıl reward sonuç eşleşmesi olmalı; SQL metin benzerliği yalnızca yardımcı (yoğunlaştırıcı) reward olabilir.

## NaturalReasoning: Reasoning in the Wild with 2.8M Challenging Questions (Meta FAIR + NYU, Şubat 2025) — [2502.13124](https://arxiv.org/abs/2502.13124)
**Tek cümlede:** Pretraining metinlerinden (DCLM-baseline, FineMath) insan etiketi olmadan 2.8M çok alanlı reasoning sorusu çıkarıp distillation ve self-training'de kullandılar.

**Problem:** Reasoning verisinin çoğu matematik ve kodda; başka alanlarda (fizik, ekonomi, hukuk...) zor ve çeşitli soru az. İnsanlara soru yazdırmak pahalı. Yazarlar, internetteki metinlerde zaten bulunan bilgiden otomatik olarak çok alanlı zor sorular üretmek istiyor.

**Ne yaptılar:**
1. **Belge seçimi ve soru yazımı:** Bir LLM belgeleri reasoning içeriğine göre puanlıyor. Yüksek puanlı belgelerden, belgeye bakmadan da anlaşılan (kendi kendine yeten) sorular yazıyor.
2. **Referans cevap:** İkinci bir LLM, referans cevabın belgeden çıkarılabilir olup olmadığını kontrol ediyor. Soruların ~%81.7'sinde referans var.
3. **Temizlik:** Min-hash ile tekrar silme (birbirine çok benzeyen soruları bulup atma). 13-gram dekontaminasyon: test setleriyle 13 kelimelik ortak parça paylaşan sorular atılıyor (~%0.026).
4. **Zorluk vekili:** Llama-3.3-70B-Instruct'ın cevabının uzunluğu (medyan 434 kelime). Uzun cevap gerektiren soru zor sayılıyor.
5. **Distillation:** Llama3.1-8B-Base, 1.5M örnekle.
6. **Uzun CoT:** Llama-3.3-70B-Instruct, 100K soru ve DeepSeek-R1'in cevaplarıyla.
7. **Self-training:** Llama3.1-8B-Instruct üzerinde DPO. Çiftler modelin kendi verdiği puanla (self-score) filtreleniyor.

**Sonuç:** Yazarların raporuna göre:
- 1.5M örnekle eğitilen Llama3.1-8B-Base, MATH / GPQA / MMLU-Pro (çok alanlı zor bilgi ve reasoning soruları) ortalamasında Meta'nın kendi Llama3.1-8B-Instruct'ını geçiyor.
- Karşılaştırılan OpenMathInstruct-2 MATH'te iyi ama GPQA ve MMLU-Pro'da geride; yani yalnız matematik verisi başka alanlara taşınmıyor. Bazı veri setleri veri büyüdükçe doyuyor ya da geriliyor.
- 100K NaturalReasoning sorusu + R1 cevapları ile ortalama 78.9. DeepSeek-R1-Distill-Llama-70B 800K örnekle 79.4 alıyor. Yani 8 kat az veriyle neredeyse aynı skor.
- Referans cevaba göre filtrelemek sonucu iyileştiriyor.
- Self-training DPO: base 40.81 → self-score ile 43.67; dış bir RM (INF-ORM) ile 43.12. Modelin kendi puanı, dış RM kadar iyi çalışıyor.

**Bizim için:** Referans cevabıyla filtrelenmiş az sayıda zor soru, çok sayıda dar sorudan daha verimli. Kendi kendine puanlamayla DPO, dış RM'ye yakın sonuç veriyor.

## Distillation Scaling Laws (Apple + Oxford, Şubat 2025) — [2502.08606](https://arxiv.org/abs/2502.08606)
**Tek cümlede:** Distillation için bir scaling law (ölçekleme yasası): küçük modelin ne kadar iyi olacağı, kendi boyu, distillation token sayısı ve büyük modelin kalitesiyle tahmin edilebiliyor. ICML 2025.

**Problem:** Küçük bir model gerekiyorsa iki yol var: onu doğrudan veriyle eğitmek (supervised learning) ya da büyük bir modelden distillation yapmak. Hangisinin daha verimli olduğu, hangi büyüklükte büyük modelin seçileceği ve ne kadar veri gerektiği belirsizdi. Yazarlar bunu deneylerle bir formüle bağlıyor.

**Ne yaptılar:**
1. **Modeller:** Küçük modeller 143M–12.6B parametre; büyük modeller 198M–7.75B.
2. **Veri:** Birkaç milyar ile 512B token arası; yalnızca İngilizce C4 (temizlenmiş web metni), 4096 uzunluk.
3. **Saf distillation:** λ = 1, yani küçük model yalnızca büyük modelin dağılımından öğreniyor; normal next-token kaybı karıştırılmıyor. Temperature 1.
4. **Sabit compute bütçeleri:** Küçük model için IsoFLOP budget'ları (aynı toplam hesaplama miktarı) 3×10¹⁹ – 10²¹ FLOP.
5. **Yasa:** Küçük modelin cross-entropy'si (kaybı; düşük olan iyi) kendi boyuna, distillation token sayısına ve büyük modelin cross-entropy'sine bağlı. Büyük modelin boyu ve kaç token'la eğitildiği, yalnızca onun cross-entropy'si üzerinden etki ediyor.

**Sonuç:** Yazarların raporuna göre:
- Capacity gap: büyük model güçlendikçe küçük modelin kaybı önce düşüyor, sonra yükseliyor. Yani çok güçlü bir büyük model, daha kötü bir küçük model verebilir; arada çok fark varsa küçük model taklit edemiyor.
- Distillation, supervised learning'i yalnızca küçük modelin compute ya da token bütçesi sınırlıyken geçiyor. Yeterli veri ya da compute varsa supervised learning kazanıyor.
- Büyük model zaten varsa ya da başka işlere de yarayacaksa distillation daha verimli. Büyük modeli yalnızca tek bir küçük model için eğitmek gerekiyorsa, supervised learning genelde daha iyi.
- Yasa deneylere ~%1 göreli hatayla uyuyor.

**Bizim için:** 9B zaten hazır ve compute'umuz kısıtlı; bu iki koşul tam olarak distillation'ın supervised learning'den iyi olduğu bölge. Ama capacity gap yüzünden 9B'den daha büyük bir kaynak her zaman daha iyi olmayabilir.

## BTS: Harmonizing Specialized Experts into a Generalist LLM (Meta + Oxford, Ocak 2025) — [2502.00075](https://arxiv.org/abs/2502.00075)
**Tek cümlede:** Bir seed modelden alan uzmanları ayrı ayrı eğitiliyor, sonra uzmanlar dondurulup aralarına yalnızca küçük "stitch" (dikiş) katmanları eklenip eğitiliyor. EMNLP 2025.

**Problem:** Kod, matematik ve çok dilli görevlerde ayrı ayrı uzmanlaşmış modeller var; hepsini tek bir genel modelde toplamak istiyoruz. Bütün uzmanları birlikte yeniden eğitmek pahalı. Düz ağırlık ortalaması ucuz ama uzmanlıkları bozuyor. BTS, Branch-Train-MiX çizgisinin devamı olarak, uzmanlara dokunmadan onları birleştirmenin bir yolunu arıyor; uzmanlar yeniden eğitim olmadan eklenip çıkarılabiliyor.

**Ne yaptılar:**
1. **Branch (dallandır):** Seed model 2.7B (Llama 3 tarifiyle, 15T token).
2. **Train (eğit):** Üç uzman: code, math, multilingual. Her biri seed'den başlayarak 200B token daha eğitilmiş (96k adım, lr 5e-6).
3. **Stitch (dik):** Uzmanlar ve seed model donduruluyor. Seed model "hub" (merkez) oluyor. Her beş katmandan sonra dört stitch katmanı ekleniyor. Bunlar dönüşümlü iki tür: Experts-into-Hub (uzmanların temsillerini hub'a taşır) ve Hub-into-Experts (hub'ın temsilini uzmanlara taşır).
4. **Stitch eğitimi:** Yalnızca stitch katmanları eğitiliyor; 15B token, 7,000 adım. Veri %15'er code / math / multilingual ve %55 seed'in pretraining verisi.
5. **Karşılaştırma:**
   - BTX: uzmanları bir MoE'ye upcycle edip bütün parametreleri günceller.
   - BAM: uzmanları MoE'de birleştiren başka bir yöntem.
   - Model Soup: uzmanların ağırlıklarının düz ortalaması (model merging).
   - BTM: uzmanların çıktılarını (logit'lerini) inference'ta birleştiren ensemble.

**Sonuç:** Yazarların raporuna göre:
- Ortalama skor: BTS 28.1, BAM 27.8, BTX Soft 27.4, BTM 26.9, Model Soup 25.7, seed 24.0. En basit yol (ağırlık ortalaması) en zayıf, seed'e ancak 1.7 puan ekliyor.
- BTS, code uzmanını MBPP'de (32.2'ye karşı 32.0), math uzmanını MATH'te (10.6'ya karşı 10.1) az farkla geçiyor; yani birleşik model uzmanlığı kaybetmiyor.
- ~11B toplam parametrenin yalnızca 264M'i eğitiliyor.

**Bizim için:** Ayrı uzmanları birleştirmenin en basit yolu (ağırlık ortalaması) en zayıf sonuç veriyor. Tek bir SQL agent'ı için uzman birleştirmeye gerek yok; ama ileride ayrı uzmanlar olursa doğrudan ortalama yerine distillation ya da hafif birleştirici katman tercih edilmeli.

## SFT Memorizes, RL Generalizes: A Comparative Study of Foundation Model Post-training (HKU + UC Berkeley + Google DeepMind + NYU + U. Alberta, Ocak 2025) — [2501.17161](https://arxiv.org/abs/2501.17161)
**Tek cümlede:** Aynı veride SFT ile RL'yi, kuralları ya da görselleri değiştirilmiş görevlerde karşılaştırdılar: SFT ezberliyor ve yeni kurala uyamıyor, RL genelleşiyor.

**Problem:** Post-training'den sonra modelin gerçekten bir beceri mi öğrendiği yoksa eğitim örneklerini mi ezberlediği belirsiz. Bunu anlamanın yolu, modeli eğitim dağılımının dışında (OOD: out-of-distribution, yani eğitimde görmediği türde girdilerde) test etmek. Yazarlar SFT ve RL'yi bu açıdan yan yana koyuyor.

**Ne yaptılar:**
1. **Görevler:** GeneralPoints (kartlarla aritmetik: verilen kart değerlerinden bir hedef sayıya ulaşmak) ve V-IRL (gerçek dünya sokaklarında talimatla yol bulma).
2. **OOD testi:** Eğitimden sonra görevin kuralları ya da görselleri değiştiriliyor. Model bu yeni kurala uyabiliyor mu diye bakılıyor. "-L" ile biten sürümler (GP-L, V-IRL-L) görevin yalnızca metinle verilen hâli.
3. **Model:** Backbone Llama-3.2-Vision-11B.
4. **Eğitim:** Önce SFT, sonra sonuç tabanlı reward'la çok adımlı RL. RL'de model, bir doğrulayıcıdan gelen geri bildirimle kendi cevabını düzeltebiliyor (bkz. [agentic RL ve multi-turn](00_terimler.md#agentic-rl-ve-multi-turn)).
5. **SFT'siz deneme:** Base Llama 3.2 ile uçtan uca RL.

**Sonuç:** Yazarların raporuna göre, OOD kural değişiminde (başlangıç → eğitim sonrası):
- RL: GP-L 11.5 → 15.0 (+3.5), V-IRL-L 80.8 → 91.8 (+11.0).
- SFT: GP-L 11.5 → 3.4 (−8.1), V-IRL-L 80.8 → 1.3 (−79.5). Yani SFT, yeni kurallı görevde modeli neredeyse tamamen bozuyor; eski kuralı ezberliyor.
- SFT'siz RL bütün koşularda başarısız: base model biçimsiz, uzun cevaplar ürettiği için reward çıkarılamıyor. SFT, RL'nin başlayabilmesi için gerekli.
- Aynı compute'ta doğrulama adımı sayısını 1'den 10'a çıkarmak, OOD kazancını +0.48'den +5.99'a çıkarıyor. Daha çok "dene, geri bildirim al, düzelt" turu daha iyi genelleme veriyor.

**Kaynak notu:** Makale birçok kurumdan; bu bölüme Google DeepMind'dan yazarları (Dale Schuurmans ve Quoc V. Le) olduğu için alındı.

**Bizim için:** SFT önce biçimi (Qwen tool-call biçimi) oturtmak için şart, ama genelleme RL'den geliyor. Bizim döngüdeki gibi çok turlu doğrulama ve düzeltme, RL'nin kazancını büyütüyor.

## rStar-Math: Small LLMs Can Master Math Reasoning with Self-Evolved Deep Thinking (Microsoft Research Asia, Ocak 2025) — [2501.04519](https://arxiv.org/abs/2501.04519)
**Tek cümlede:** Daha büyük bir modelden distillation olmadan, küçük bir policy modeli (çözüm üreten model) ve bir process preference model (PPM: adımları puanlayan model) ağaç aramasıyla kendi kendini geliştiriyor.

**Problem:** Küçük modelleri reasoning'de güçlendirmenin en yaygın yolu büyük bir modelin çözümlerini taklit ettirmek. Ama bu, büyük modelin seviyesiyle sınırlı ve büyük modele bağımlı. Ayrıca bir çözümün hangi adımının iyi olduğunu etiketlemek zor. rStar-Math, küçük modelin kendi ürettiği ve doğruladığı veriyle gelişmesini istiyor.

**Ne yaptılar:**
1. **Code-augmented CoT:** Her reasoning adımı kısa bir doğal dil düşüncesi + Python kodu. Kodu çalışmayan adım atılıyor; yalnızca kodu hatasız çalışan adımlar tutuluyor.
2. **MCTS ile adım puanı:** MCTS (Monte Carlo Tree Search), çözümü adım adım bir ağaç gibi dallandırıp her daldan çok sayıda deneme yapan bir arama yöntemi. Çok sayıda rollout, her adıma bir Q-değeri veriyor: o adımdan geçen denemeler ne sıklıkla doğru cevaba ulaşıyor. Örneğin bir adımdan geçen 10 denemenin 8'i doğruysa o adımın Q-değeri yüksek.
3. **PPM:** Bir process reward model (PRM: çözümün her adımını puanlayan model) türü. Gürültülü Q-skorlarını doğrudan hedef almak yerine, iyi ve kötü adım çiftlerinden tercih kaybıyla eğitiliyor ("bu adım şundan iyi").
4. **Self-evolution, dört tur:** Policy ve PPM, her turda kendi ürettikleri ve doğrulanmış veriyle yeniden eğitiliyor; her tur daha iyi veri üretiyor (bkz. [expert iteration](00_terimler.md#expert-iteration)). 747k matematik problemi.
5. **Modeller:** Policy'ler Qwen2.5-Math-7B, 1.5B ve Phi3-mini-3.8B; PPM 7B.

**Sonuç:** Yazarların raporuna göre:
- MATH: Qwen2.5-Math-7B 58.8 → 90.0; Phi3-mini-3.8B 41.4 → 86.4. İki modelde de ~30–45 puanlık artış.
- AIME 2024'te 7B ile 15 sorudan 8'i (%53.3).
- Ablation: doğrulanmış kendi trajectory'leri, GPT'den distill edilmiş veriyi ve rejection sampling'i geçiyor. PPM, outcome RM'den (yalnızca son cevabı puanlayan model) ve Q-değeri tabanlı PRM'den daha iyi.

**Bizim için:** "Yalnızca çalışan adımı tut" kuralı bizde `execute_sql`'in hatasız çalışmasına karşılık geliyor. Trajectory'leri adım adım çalıştırılabilirliğe göre süzmek, büyük model olmadan da küçük modelin kendi verisini temizler.

## Inference-Aware Fine-Tuning for Best-of-N Sampling in Large Language Models (Google DeepMind + Google Research, Aralık 2024) — [2412.15287](https://arxiv.org/abs/2412.15287)
**Tek cümlede:** Model, inference'ta Best-of-N ile kullanılacağını (N cevap üretip doğrulayıcıyla en iyisini seçmek) hesaba katarak fine-tune ediliyor.

**Problem:** Normal eğitim, modelin tek bir cevabını en iyi yapmaya çalışır. Ama pratikte çoğu zaman N cevap üretilip en iyisi seçilir. Bu durumda iyi olan, N cevabın birbirinden farklı olması ve en az birinin çok iyi olmasıdır. Seçim adımı "en büyük skorlu cevabı al" (argmax) işlemidir ve türevlenemez; gradient bu adımdan geçmez. Yazarlar bu engeli aşan imitation ve RL yöntemleri öneriyor.

**Ne yaptılar:**
1. **BoN-SFT:** Uzman verisiyle imitation; kayıp, BoN seçimini hesaba katacak biçimde yazılmış.
2. **BoN-RL-V:** RL; seçim sinyali doğrulayıcıdan geliyor.
3. **BoN-RL-S:** RL; reward ortamdan geliyor (ör. cevap doğru mu).
4. **BoN-RLB ve BoN-RLB(P):** İkili reward için kapalı formda (formülle doğrudan hesaplanan) policy gradient'ler. BoN-RLB(P) yalnızca pozitif (doğru) örneklerden öğreniyor.
5. **Modeller ve veri:** Gemma 2 2B ve 9B. Hendrycks MATH (eğitim/test); Functional MATH (MATH sorularının sayıları değiştirilmiş sürümleri) ve MathOdyssey (farklı zorlukta matematik soruları) dış test. Kodda MBPP eğitim, HumanEval test.

**Sonuç:** Yazarların raporuna göre, Gemma 2B ile:
- MATH Bo32 (32 cevaptan doğrulayıcının seçtiğinin doğruluğu): 26.8 → 30.8 (BoN-RL-V).
- MATH pass@32 (32 cevaptan en az birinin doğru olma oranı): 60.0 → 67.0 (BoN-RL-S).
- HumanEval pass@16: 61.6 → 67.1 (BoN-RLB(P)).
- Tek cevap (N' = 1) için optimize eden standart RL pass@N'i biraz düşürüyor; yani çeşitliliği azaltıyor. BoN'a göre eğitilen model ise en iyi cevapları daha çeşitli cevaplarla karıştırmayı öğreniyor.
- Zor problemler daha yüksek temperature ve daha çok örnek istiyor; en iyi temperature N ile birlikte artıyor.

**Bizim için:** Bizim döngüde reddedilen çağrıdan sonra 0.7 temperature'la yeniden örnekleme var. RL'yi yalnızca ilk denemenin doğruluğu için optimize etmek bu yeniden denemelerin çeşitliliğini öldürebilir; bu yüzden reward bütün trajectory'nin sonucuna verilmeli.

## Phi-4 Technical Report (Microsoft Research, Aralık 2024) — [2412.08905](https://arxiv.org/abs/2412.08905)
**Tek cümlede:** 14B Phi-4; pretraining'de yoğun sentetik veri, post-training'de SFT ve iki tur DPO; ilk DPO turunda "Pivotal Token Search" (PTS) ile preference çiftleri kararın değiştiği tek token'lar üzerinden kuruluyor.

**Problem:** Normal DPO'da bütün bir iyi cevap ile bütün bir kötü cevap karşılaştırılır. Ama iki cevap çoğu yerde aynıdır; asıl fark birkaç kritik token'dadır. Bütün cevap üzerinden öğrenmek bu sinyali gürültüye boğar. PTS, preference'ı tam o kritik noktaya yerleştirmek istiyor.

**Ne yaptılar:**
1. **SFT:** lr 1e-6, ~8B token: matematik, kod, reasoning, sohbet, kimlik, güvenlik ve 40 dil. Her prompt için birden çok cevap üretilip LLM değerlendirmesiyle en iyisi seçiliyor.
2. **DPO 1 (PTS):** ~250K çift: 132,859 çoktan seçmeli soru-cevap, 76,552 matematik, 21,806 C++/Go/Java/JS/Rust, 16,080 Python, 3,000 güvenlik.
   - PTS cevabı özyinelemeli olarak ikiye bölüyor ve doğru cevaba ulaşma olasılığını bir eşikten fazla değiştiren token'ları buluyor.
   - O token'a kadarki metin prompt oluyor; olasılığı artıran token tercih edilen, düşüren token reddedilen cevap oluyor.
   - Açıklama için uydurulmuş bir örnek: bir matematik çözümünde "…buradan x'i bulmak için iki tarafı **topla**" yerine "**çarp**" demek başarı olasılığını %70'ten %20'ye düşürüyorsa, çift bu tek kelime üzerinden kuruluyor.
   - Yalnızca başarı olasılığı 0.2 ile 0.8 arasında olan sorular kullanılıyor.
3. **DPO 2 (judge-guided):** GPT-4o, GPT-4t ve Phi-4'ün cevaplarından ~850K çift. GPT-4o cevapları doğruluk, üslup ve ayrıntıya göre yargılıyor.
4. **Reddetme verisi:** Modelin bilmediği trivia sorularını reddetmesi için örnekler.
5. **Pretraining:** 50 türde ~400B sentetik token (karışımın ~%40'ı), toplam ~10T token. Bağlamı 4K'dan 16K'ya çıkarmak için ~250B token'lık bir mid-training.

**Sonuç:** Yazarların raporuna göre, aşama ablation'ı (yalnız SFT / SFT + DPO-PTS / SFT + yalnız DPO-2 / ikisi):
- GPQA: 47.3 / 53.6 / 52.4 / 56.1
- MATH: 77.1 / 80.5 / 77.6 / 80.4
- ArenaHard (zor kullanıcı sorularında judge'ın tercih oranı): 56.7 / 66.5 / 69.8 / 75.4
- PTS en çok reasoning'e (GPQA +6.3, MATH +3.4), judge-guided DPO en çok ArenaHard'a (+13.1) yardım ediyor. İkisi birbirini tamamlıyor: birlikte GPQA'da +8.8, ArenaHard'da +18.7.

**Bizim için:** Preference çiftlerini bütün cevap yerine kararın değiştiği noktada kurmak (bizde: trajectory'nin yanlış tabloya ya da yanlış değere saptığı tool call) DPO'yu çok daha verimli yapar. Burada da yalnızca başarı olasılığı 0.2–0.8 arası sorular seçiliyor.
