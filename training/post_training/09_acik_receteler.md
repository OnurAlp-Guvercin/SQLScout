# Açık reçeteler (AI2, Stanford, Berkeley, Hugging Face, Thinking Machines ve diğerleri)

**Bu bölümde ne var:** Bu bölümde, eğitim ayrıntılarını, verisini ya da ağırlıklarını açıkça paylaşan grupların post-training reçeteleri var. Post-training, önceden eğitilmiş bir modeli belli bir işte daha iyi hale getirmek için yapılan sonraki eğitimdir. Bütün rakamlar yazarların kendi bildirdiğidir; bulunamayan rakam yazılmadı. Sıra: en yeni önce.

Bu dosyada sık geçen terimler (ayrıntısı sözlükte):
- [SFT](00_terimler.md#sft) (supervised fine-tuning): modele doğru örnek cevapları gösterip onları taklit ettirerek eğitmek.
- [RL ve RLVR](00_terimler.md#rl-ve-rlvr) (reinforcement learning; RL with verifiable rewards): model kendi cevaplarını üretir, iyi cevaplar puan alır, model puan alan davranışa doğru güncellenir. RLVR'da puan otomatik ve kesin bir kontrolden gelir (ör. "son cevap doğru mu", "testler geçiyor mu").
- [Rollout](00_terimler.md#rollout): modelin eğitim sırasında bir soru için ürettiği tek bir deneme (cevap ya da bütün bir agent konuşması).
- [Reward](00_terimler.md#reward): bir rollout'a verilen puan. "İkili reward": doğruysa 1, yanlışsa 0.
- [Distillation](00_terimler.md#distillation): büyük bir modelin bildiğini küçük bir modele aktarmak; çoğu zaman büyük modelin cevaplarıyla küçük modele SFT yapmak.
- [Benchmark](00_terimler.md#benchmarklar): modelleri karşılaştırmak için kullanılan sabit soru seti.

**Bu bölümün ana dersleri:**
- Veri seçimi çoğu zaman algoritmadan daha önemlidir: az ama doğru zorlukta ve temiz örnek, çok sayıda rastgele örnekten iyi sonuç verir (LIMO, s1, OpenThoughts).
- RL genelde modelin zaten arada bir çözebildiği soruları güvenilir hale getirir; modelin hiç çözemediği sorular için büyük modelden SFT ya da distillation gerekir.
- Küçük modelde sade bir GRPO (ikili reward, sabit ayarlar) iyi bir ilk denemedir; ek cezalar ve "akıllı" reward'lar sık sık zarar verir (JustRL, SimpleRL-Zoo).
- RL'e verilecek sorular modelin seviyesine göre süzülmelidir: her seferinde çözülen ve hiç çözülemeyen sorular öğrenme sinyali vermez (POLARIS, Skywork OR1, Light-R1).
- Qwen modellerinde RL kazancı yanıltıcı olabilir: rastgele reward bile puan artırabiliyor, bu yüzden kontrol koşusu gerekir (Spurious Rewards).

**Makaleler:**
- OpenThoughts-Agent — agent'lar için SFT verisinin her aşamasını ölçen ablation çalışması.
- Polaris V2 — ayrı bir model eğitmeden ara adımlara puan veren RL reçetesi (4B math).
- rLLM-FinQA — finansal tablo sorgulayan 4B agent'ın RL ile eğitimi.
- JustRL — 1.5B modelde tek aşamalı, sade GRPO'nun yeterli olduğu.
- Olmo 3 / Olmo 3.1 — her aşaması açık 7B ve 32B model ailesi (SFT → DPO → RLVR).
- On-Policy Distillation — küçük modelin kendi cevaplarını büyük modelin token puanlarıyla düzeltmek.
- LoRA Without Regret — LoRA'nın ne zaman full fine-tuning kadar iyi olduğu.
- SmolLM3 post-training — 3B, düşünme modu açılıp kapanan modelin açık reçetesi.
- The Delta Learning Hypothesis — iki zayıf cevabın farkından öğrenmek.
- FlexOlmo — ayrı eğitilmiş alan uzmanlarını tek modelde birleştirmek.
- Skywork-Reward-V2 — insan ve LLM'in birlikte etiketlediği büyük preference verisiyle reward model.
- DeepSWE — SFT'siz, yalnızca RL ile yazılım agent'ı.
- SPIRAL — kendi kopyasına karşı oyun oynayarak RL (self-play).
- OctoThinker — RL'den önceki ara eğitimin (mid-training) RL'e etkisi.
- Spurious Rewards — Qwen'de rastgele reward'ın bile kazanç vermesi.
- POLARIS — güçlü küçük modelleri RL ile ileri taşımak: veri zorluğu ve temperature.
- OpenThoughts — akıl yürütme SFT verisinin her adımını ölçen 1.000+ deney.
- Skywork Open Reasoner 1 — uzun düşünme için açık RL reçetesi ve entropy çöküşü.
- The Entropy Mechanism of RL — RL'de entropy'nin neden çöktüğü ve nasıl önleneceği.
- Entropy Minimization — etiketsiz, yalnızca modelin kendinden emin olmasıyla eğitim.
- Mixture-of-Thoughts ve OpenR1-Distill-7B — DeepSeek-R1 distillation'ını açık veriyle yeniden üretmek.
- Absolute Zero — dış veri olmadan, modelin kendi görevlerini üretip çözdüğü RL.
- One Training Example — tek bir örnekle RLVR.
- Does RL Really Incentivize... — RL'in yeni yetenek mi kazandırdığı, var olanı mı öne çıkardığı.
- DeepCoder — 14B modeli kod üzerinde RL ile eğitmek.
- Open-Reasoner-Zero — taban model üzerinde doğrudan, sade PPO.
- Understanding R1-Zero-Like Training — GRPO'daki iki yanlılık ve Dr. GRPO.
- SimpleRL-Zoo — SFT'siz RL'i 10 farklı taban modelde denemek.
- Light-R1 — iki aşamalı SFT, DPO, merge ve GRPO ile math modeli.
- LIMO — 800 iyi seçilmiş örnekle SFT.
- DeepScaleR — 1.5B modeli RL ile AIME'de güçlendirmek.
- s1 — 1.000 örnekle SFT ve düşünme süresini kontrol etmek (budget forcing).
- Sky-T1-32B-Preview — 450 dolardan az maliyetle akıl yürütme modeli.
- OLMo 2 Instruct — Tülu 3 reçetesinin açık OLMo 2'ye uygulanması.
- Tülu 3 — açık SFT → DPO → RLVR reçetesi; RLVR teriminin kaynağı.

---

## OpenThoughts-Agent: Data Recipes for Agentic Models (OpenThoughts projesi, openthoughts.ai; 50 yazar, ilk yazar Negin Raoof; Haziran 2026) — [2606.24855](https://arxiv.org/abs/2606.24855)
**Tek cümlede:** Tool kullanan agent'lar için SFT verisini hazırlamanın altı aşamasını tek tek ölçüp en iyi açık agent verisini kurdular, sonra üstüne RL eklediler.

**Problem:** OpenThoughts projesi daha önce akıl yürütme (math, kod) için iyi bir SFT verisi reçetesi çıkarmıştı. Ama terminalde komut çalıştıran ya da yazılım hatası düzelten, çok turlu tool kullanan agent'lar için ([agentic RL ve multi-turn](00_terimler.md#agentic-rl-ve-multi-turn): model birçok tur boyunca tool çağırır ve her turda tool'un cevabını görür) böyle bir reçete yoktu. Agent verisinde birçok karar var: görevler nereden alınacak, hangi büyük model trajectory üretecek, hangi trajectory'ler atılacak. Hangisinin gerçekten önemli olduğu bilinmiyordu. Trajectory, agent'ın bir görevi çözerken yaptığı bütün adımların kaydıdır: düşünce, tool call, tool'un cevabı, tekrar tool call...

**Ne yaptılar:**
1. **Sabit bir deney düzeni kurdular.** Her denemede 10.000 trajectory ile Qwen3-8B'ye full-parameter SFT yaptılar (bütün ağırlıklar güncellenir). Ayarlar hep aynıydı: LR (learning rate, öğrenme hızı) 4e-5, cosine takvim (öğrenme hızı eğitim boyunca yavaşça azalır), batch 96, 7 epoch (veri 7 kez gezilir), 32.768 token context. Trajectory'leri GLM-4.7-AWQ üretti (AWQ: ağırlıkları sıkıştırılmış, daha az bellek isteyen sürüm). Böylece her deneyde yalnızca veri değişti.
2. **Altı aşamayı 100'den fazla ablation ile ölçtüler.** Ablation, bir parçayı değiştirip ya da kaldırıp sonucun nasıl değiştiğine bakmaktır. Aşamalar: task sourcing (görevlerin kaynağı), mixing (kaynakları karıştırma), augmentation (görev metnini yeniden yazma), task filtering (görev eleme), veri üreten büyük modelin seçimi, trace filtering (trajectory eleme).
3. **Görev kaynağını seçtiler.** 95 kaynak denendi. 4 kaynağı karıştırmak, 1 ya da 16 kaynaktan iyi çıktı.
4. **Görevleri süzdüler.** İki filtre en çok işe yaradı. Birincisi, bir LLM'e görevin iyi olup olmadığını sordurmak. İkincisi bir zorluk filtresi: GPT-5'in çözmek için daha çok token harcadığı görevler "zor" sayılıp tutuldu.
5. **Trajectory'leri süzdüler.** En iyi kural basitti: 5 turdan kısa trajectory'ler atıldı. Yani tek adımda biten, agent'lık öğretmeyen kayıtlar çıkarıldı.
6. **Son veriyi kurdular.** 100K satır.
7. **Üstüne RL denediler.** Algoritma async RLOO. RLOO (leave-one-out): bir cevabın ne kadar iyi olduğu, aynı sorudaki diğer cevapların ortalamasıyla karşılaştırılarak hesaplanır. Async: rollout üretimi ile eğitim aynı anda, birbirini beklemeden yürür. Reward ikiliydi: görev başarıldıysa 1, yoksa 0. Başlangıç noktası, önce hafif bir SFT'den ([cold start](00_terimler.md#cold-start): RL'den önce modele biçimi öğreten kısa SFT) geçmiş 8B checkpoint'iydi. 24 A100 GPU'da ~46 saat, batch 64.

**Sonuç:** Yazarların raporuna göre:
- Görev kaynağı çok büyük fark yarattı. Terminal-Bench 2.0'da (terminalde gerçek görev çözme benchmark'ı) en iyi kaynak %10.9, en kötüsü %0.4 verdi. Yani yanlış kaynak, eğitimi neredeyse boşa çıkarıyor.
- Görev metnini yeniden yazmak ya da zorlaştırmak işe yaramadı.
- LLM tabanlı görev filtresi +3 puan, zorluk filtresi ~+3 puan getirdi; bunlar en büyük kazançlardı.
- 5 turdan kısa trajectory'leri atmak, aynı token miktarında rastgele seçime göre +3.5 puan getirdi.
- Qwen3-32B bu 100K veriyle SFT'lenince yedi agentic benchmark ortalamasında %44.8 aldı. Önceki en iyi açık veri modeli Nemotron-Terminal-32B %40.9 alıyordu; fark ~4 puan. SWE-Bench Verified'da (gerçek GitHub projelerinde hata düzeltme) %54.0.
- Benchmark'ta en güçlü model en iyi veri üreticisi değil: GPT-5.3-Codex, GLM-4.7-AWQ'dan ~%5 daha kötü veri üretti.
- Aynı göreve daha çok rollout eklemek 31.6K'dan 100K'ya kadar plato yaptı (kazanç durdu). Yeni görev eklemek daha değerliydi.
- RL, SFT checkpoint'ine ~+5 puan ekledi (SWE-Bench Verified'da +5.4). RL görevlerinin kaynağı 7.6 puanlık fark yarattı; aynı ayarla tekrar koşular arasındaki rastgele fark ise ~2 puandı. Yani kaynak seçimi gerçek bir etki.
- Çıplak Qwen3-8B, agentic RL'den tek başına fayda görmedi; önce hafif SFT gerekti.

**Bizim için:** Bizim experience log'umuza doğrudan uyar: önce az sayıda iyi kaynaktan, çok turlu (tek adımlık olmayan) başarılı trajectory'lerle SFT, sonra aynı tool'larla (`search_values`, `execute_sql`, `submit`) ikili reward'lı RL. 0.8B'yi doğrudan RL'e sokmak yerine hafif bir SFT cold start şart görünüyor.

---

## Polaris V2 (HKU NLP, ByteDance Seed, Fudan, Mart 2026) — [blog](https://hkunlp.github.io/blog/2026/Polaris2)
**Tek cümlede:** Ayrı bir puanlayıcı model eğitmeden, doğru çözümlerin ortak ara sonuçlarından adım düzeyinde reward üreterek 4B math modelini güçlendirdiler.

**Problem:** İkili reward yalnızca son cevaba bakar. Son cevabı yanlış ama yolun çoğunu doğru yürümüş bir çözüm de 0 alır; bu, sinyali seyrek yapar. Ara adımları puanlamak için genelde ayrı bir [PRM](00_terimler.md#reward-model-grm-ve-prm) (process reward model: çözümün her adımını puanlayan ayrı model) eğitilir. Bu pahalıdır ve PRM'in kendisi hata yapabilir. Bu, POLARIS'in (aşağıda) ikinci sürümüdür.

**Ne yaptılar:**
1. **Biçim SFT'si.** Qwen3-4B-2507, 20K soruluk bir SFT'den geçti. Cevapları GPT-OSS-20B üretti. Model, ara sonuçlarını `\underline{}` içine yazmayı öğrendi (ör. "toplam \underline{36}"). Böylece ara sonuçlar otomatik okunabilir hale geldi. Cevap uzunluğu en fazla 16K token.
2. **RL verisini süzdüler.** AReaL-boba-106K setinden başladılar. Her soru için 8 trajectory üretip kolay ve uygunsuz soruları attılar; 14K soru kaldı.
3. **CORE ile adım düzeyinde reward.** CORE (Consensus Offline Reward Estimation): doğru trajectory'lerin ara sonuçları bir "consensus" (ortak görüş) kümesine eklenir. Yanlış bir trajectory, bu kümeyle ne kadar örtüşüyorsa o kadar kısmi reward alır; en fazla 0.5. Örnek: doğru çözümler hep 12 ve 36 ara sonuçlarından geçiyor. Yanlış bir çözüm 12 ve 36'yı bulmuş ama son adımda hata yapmışsa 0 yerine kısmi puan alır.
4. **Gürültülü örnekleri attılar.** Trajectory'ler arasında farkın yüksek olduğu örnekler RL setinden çıkarıldı. Önce bir [curriculum](00_terimler.md#curriculum) (kolaydan zora sıralı eğitim) planlanmıştı; bu filtreleme daha iyi çalıştı.
5. **Ayarlar.** RL algoritması [GRPO](00_terimler.md#grpo) (aynı soruya üretilen cevapları birbirleriyle karşılaştırıp ortalamanın üstündekileri güçlendiren RL yöntemi). Temperature (örneklemenin rastgeleliği; yüksek değer daha çeşitli cevap) Stage 1'de 1.2, Stage 2'de 1.3. Sayılar BF16 yerine FP16 biçiminde tutuldu; ikisi de 16 bitlik biçimler, amaç eğitim ile cevap üretimi arasındaki küçük sayısal farkları azaltmaktı. Batch 64, soru başına 8 rollout; 32 H800 GPU'da 10 gün.
6. **235B modele aktarma.** 4B'nin cevaplarıyla 235B'lik bir modele SFT yapıldı (distillation; burada yön küçükten büyüğe). Sonra bu model ile tabanı [model merging](00_terimler.md#model-merging) ile birleştirildi: iki modelin ağırlıkları yarı yarıya ortalandı (α=0.5).

**Sonuç:** Yazarların raporuna göre, 4B model sırasıyla AIME25 / AIME26 / HMMT25'te (AIME: ABD lise matematik olimpiyatı soruları; HMMT: Harvard-MIT matematik turnuvası soruları):
- Taban: 80.9 / 78.9 / 55.6
- + biçim SFT'si: 82.4 / 79.8 / 68.2 (HMMT'de +12.6; yalnızca biçim öğretmek bile büyük fark yarattı)
- + GRPO: 86.5 / 84.3 / 72.4
- + process reward (CORE): 88.0 / 85.6 / 76.1 (+1.5 / +1.3 / +3.7)
- + veri filtreleme: 91.8 / 89.5 / 80.0
Toplamda tabana göre AIME25'te +10.9, HMMT25'te +24.4 puan. 235B tarafında, 4B'den yalnızca SFT ile distillation karışık sonuç verdi (AIME25 düştü). Distill edilen model ile tabanın merge'ü 94.2 / 93.2 / 90.5'e çıktı. ~300 RL adımından sonra plato oldu; daha yüksek temperature, entropy loss ve kolay örnek filtreleme bunu aşamadı.

**Kaynak notu:** Kaynak bir blog yazısı; hakemli bir makale değil. 235B tabanının kendi rakamları bu dosyada yok.

**Bizim için:** SQL'de "ara sonuç" doğal olarak var: bulunan değerler, ara sorguların sonuçları. Doğru trajectory'lerle örtüşen yanlış trajectory'lere kısmi reward vermek, ikili reward'ın seyrek kaldığı küçük modelde ucuz bir process reward olabilir.

---

## rLLM-FinQA: tool disiplini ile 4B model (UC Berkeley Agentica / Sky Computing Lab + Snorkel AI, Şubat 2026) — [blog](https://snorkel.ai/blog/how-tool-discipline-let-a-4b-model-outsmart-a-235b-giant-on-financial-tasks/)
**Tek cümlede:** Finansal tabloları sorgulayan 4B bir agent'ı RL ile "önce bak, doğrula, hata olursa yeniden dene" alışkanlığına eğittiler.

**Problem:** Küçük modeller tablo sorularında tool'u yanlış kullanır: tabloyu tanımadan sorgu yazar, sonucu kontrol etmez, hatada vazgeçer. Yazarlar buna "tool disiplini" eksikliği diyor. Amaç, 4B bir modelin doğru tool alışkanlıklarıyla çok daha büyük modelleri geçip geçemeyeceğini görmekti.

**Ne yaptılar:**
1. **Ortam.** Finansal tablolar üzerinde sorgu çalıştıran bir agentic ortam kurdular. Model tabloları keşfeder, sorgu çalıştırır, sonucu görür.
2. **Model ve framework.** Qwen3-4B-Instruct-2507'yi rLLM framework'üyle (agent'ları RL ile eğitmek için açık bir kütüphane) RL ile eğittiler.
3. **Reward.** Cevabı bir yargıç model puanladı ([LLM-as-judge](00_terimler.md#llm-as-judge-ve-rubric): cevabı bir LLM'e kontrol ettirmek). Basit doğrulamalar için küçük bir yargıç (GPT-5-nano), karmaşık çok tablolu sorgular için daha büyük modeller.
4. **Veri.** Eğitimde yalnızca tek tablolu, basit sorgular kullanıldı.
5. **Donanım.** 8 H100 GPU; koşu başına 500 dolardan az.

**Sonuç:** Yazarların raporuna göre, iç pass@1 ablation'ı ([pass@1](00_terimler.md#pass-rate-ve-passk): modelin ilk denemede doğru cevap verme oranı):
- Yalnızca tek tablolu görevler: %66.3
- Tek ve çok tablolu görevler karışık: %61.6
- Önce tek, sonra çok tablo (curriculum): %64.8
Yani kolay, tek tablolu görevlerle eğitmek, zor örnek eklemekten (4.7 puan daha iyi) ve curriculum'dan (1.5 puan daha iyi) daha iyi genelledi. Model, Snorkel'in finans benchmark'larında Qwen3-235B-A22B'yi (235B toplam, 22B aktif parametreli bir [MoE](00_terimler.md#moe) modeli; MoE: her token için parametrelerin yalnızca bir kısmını çalıştıran "uzmanlar karışımı" mimarisi) geçti.

**Kaynak notu:** Kaynak bir blog yazısı. RL algoritması blogda yazmıyor; ikincil kaynaklar GRPO diyor. Veri boyutu ve hiperparametreler verilmiyor. Blogdaki rakamlar farklı değerlendirmelerden geliyor; iç pass@1 rakamları kamuya açık benchmark rakamlarıyla karşılaştırılmamalı.

**Bizim için:** Bizim işimize en yakın örnek: 4B model, tablo sorgulayan tool'larla, az bütçeyle RL. Tool'u doğru sırayla kullanmayı öğreten kolay görevlerle başlamak, zor çok tablolu BIRD sorularını karıştırmaktan daha iyi olabilir.

---

## JustRL: Scaling a 1.5B LLM with a Simple RL Recipe (Tsinghua THUNLP, Aralık 2025) — [2512.16649](https://arxiv.org/abs/2512.16649)
**Tek cümlede:** 1.5B modellerde, tek aşamalı ve hiç değişmeyen ayarlarla düz bir GRPO'nun karmaşık reçeteler kadar iyi olduğunu gösterdiler.

**Problem:** Küçük modelleri RL ile eğiten reçeteler giderek karmaşıklaştı: çok aşamalı eğitim, eğitim sırasında değişen ayarlar, curriculum, uzunluk cezaları. Bu parçaların gerçekten gerekli olup olmadığı belli değildi. Her ek parça hem compute hem ayar yükü getirir.

**Ne yaptılar:**
1. **İki taban model seçtiler.** DeepSeek-R1-Distill-Qwen-1.5B ve OpenMath-Nemotron-1.5B. İkisinde de aynı ayarları kullandılar.
2. **Veriyi süzmediler.** DAPO-Math-17k setini olduğu gibi kullandılar. Ne önceden zorluk filtresi ne de eğitim sırasında [dynamic sampling](00_terimler.md#dynamic-sampling) (bütün cevapları aynı puanı alan soruları batch'ten atma) var.
3. **Basit reward.** DAPO'nun kural tabanlı, ikili cevap kontrolcüsü: son cevap doğruysa 1, değilse 0.
4. **Düz GRPO, sabit ayarlar.** veRL kütüphanesiyle GRPO. [KL penalty](00_terimler.md#kl-penalty) (modeli başlangıç haline yakın tutan ceza) kapalı. Entropy bonusu kapalı. Batch 256, soru başına 8 rollout, LR 1e-6 sabit, temperature 1.0, 16K context.
5. **Clip higher.** Clip, bir güncellemede bir token'ın olasılığının ne kadar değişebileceğinin sınırıdır. Burada oran 0.8 ile 1.28 arasında tutuldu. Üst sınırın daha geniş olması ([clip higher](00_terimler.md#clip-ve-clip-higher)) düşük olasılıklı token'ların daha hızlı büyüyebilmesini sağlar; bu, modelin yeni yollar denemesini (exploration) korur.
6. **Uzun koşu.** 32 A800 GPU'da model başına ~15 gün; 4.380 ve 3.440 adım.

**Sonuç:** Yazarların raporuna göre, 9 math benchmark ortalaması:
- JustRL-DeepSeek %54.87. Taban %37.65'ti; fark +17.2 puan. Başka bir RL reçetesi olan ProRL-V2 %53.08, DeepScaleR %44.88 alıyor. Yani sade reçete onları geçti.
- JustRL-Nemotron %64.32; karşılaştırılan QuestA %63.81.
- Harcanan token bütçesi ProRL-V2'nin yaklaşık yarısı.
Ablation: DAPO tarzı overlong penalty (cevap belli uzunluğu aşınca reward'dan düşülen ceza) eklemek AIME24'ü ~%55'ten ~%50'ye düşürdü ve [entropy](00_terimler.md#entropy-ve-entropy-collapse)'yi çökertti (model hep aynı kalıpta cevap vermeye başladı). Üstüne DeepScaleR'ın daha ayrıntılı ("robust") cevap kontrolcüsü eklenince ~%45'e indi. Uzunluk cezası olmadan da cevaplar kendiliğinden ~7-8K'dan 4-5K token'a kısaldı.

**Bizim için:** Küçük modelde ilk RL denemesi düz GRPO + ikili reward + sabit ayarlarla başlamalı. Uzunluk cezası ya da "akıllı" reward eklemeleri exploration'ı öldürebilir.

---

## Olmo 3 / Olmo 3.1 (AI2, Kasım 2025; rapor Aralık 2025) — [2512.13961](https://arxiv.org/abs/2512.13961)
**Tek cümlede:** Verisi, kodu ve her checkpoint'i açık 7B ve 32B model ailesi; post-training SFT → DPO → RLVR sırasıyla yapılıyor.

**Problem:** Güçlü açık modellerin çoğunda yalnızca son ağırlıklar açıktır; hangi veriyle, hangi sırayla eğitildikleri bilinmez. Bu yüzden araştırmacılar bir aşamanın etkisini tekrar üretemez. AI2, her aşamanın verisini ayrı ayrı açarak bunu çözmeye çalıştı. Post-training verisinin adı Dolci; her aşama için ayrı bir karışım var.

**Ne yaptılar:** Üç yol var: Think (uzun düşünerek cevap), Instruct (kısa cevap, tool kullanımı) ve RL-Zero (taban model üzerinde doğrudan RL). Think yolu:
1. **SFT.** Dolci-Think-SFT (7B) ~2.27M örnek. İçerik: OpenThoughts3 941K, Dolci Think Python 467K, Persona IF 223K, Precise IF 136K (IF: instruction following, talimata uyma), Nemotron kod 114K, SYNTHETIC-2 105K ve DeepSeek R1 ile yeniden üretilmiş sohbet, güvenlik ve çok dilli prompt'lar. Amaç, modele uzun düşünme biçimini ve geniş bir yetenek yelpazesini öğretmek.
2. **DPO.** [DPO](00_terimler.md#dpo-ve-preference-optimization) (direct preference optimization): modele aynı soruya bir "iyi" (chosen) ve bir "kötü" (rejected) cevap gösterilir; model iyiyi daha olası, kötüyü daha az olası yapmayı öğrenir. Dolci-Think-DPO 150K çift. Çiftler "delta learning" ile kuruldu (aşağıda ayrı bölüm): chosen Qwen3-32B'nin cevabı, rejected Qwen3-0.6B'nin cevabı (ikisi de reasoning modunda).
3. **RLVR.** Dolci-Think-RL (7B) 102K prompt: math 30.2K, instruction following 29.8K, kod 21.4K (test'leri çalıştırılarak süzülmüş), genel 20.6K. Her satırda bir pass rate alanı var (modelin o soruyu ne sıklıkla çözdüğü), böylece sorular zorluğa göre seçilebiliyor.
4. **Algoritma ve hız.** OlmoRL (GRPO ve DAPO tabanlı). İki sistem iyileştirmesiyle ~4 kat hız: continuous batching (biten rollout'un yerine hemen yenisi başlatılır, en yavaş cevap beklenmez) ve inflight weight update (yeni ağırlıklar, rollout üretimi durdurulmadan yüklenir).
5. **RL-Zero yolu.** Olmo 3 Base üzerinde math, kod, IF ve genel sohbet için ayrı ayrı RL.
6. **Olmo 3.1.** En iyi RL koşusu 224 GPU'da 21 gün daha sürdürüldü.

**Sonuç:** Yazarların raporuna göre, Olmo 3.1 Think 32B: AIME24 80.6, AIME25 78.1 (lise matematik olimpiyatı), MATH 96.2 (yarışma matematiği), IFEval 93.8 (kontrol edilebilir talimatlara uyma, ör. "3 paragraf yaz"), LiveCodeBench v3 83.3 (yarışma kodlama soruları). Bu sonuçlar, Qwen3 32B'nin eğitimindekinin yaklaşık altıda biri kadar token'la alındı. RL'i 21 gün daha sürdürmek Olmo 3'e göre AIME'de 5+, IFBench'te (yeni talimat uyma kısıtları) 20+ puan ekledi. Raporun bölüm başlıklarına göre üç bulgu: DPO, aynı veriyle SFT'nin veremediği kazancı veriyor; RL için DPO'dan başlamak SFT'den başlamaktan iyi; RL verisini farklı alanlardan karıştırmak over-optimization'ı (modelin tek bir hedefe aşırı uyup başka yeteneklerini kaybetmesi) önlüyor.

**Bizim için:** SFT → DPO → RL sırası ve "büyük modelin cevabı chosen, küçük modelin cevabı rejected" DPO çiftleri bizde ucuzca kurulabilir: 9B'nin doğru trajectory'si chosen, 0.8B'nin yanlış trajectory'si rejected.

---

## On-Policy Distillation (Thinking Machines Lab, Ekim 2025) — [blog](https://thinkingmachines.ai/blog/on-policy-distillation/)
**Tek cümlede:** Küçük model kendi cevabını üretir, büyük model bu cevabın her token'ını puanlar; böylece RL'in "kendi verisiyle öğrenme" avantajı ile SFT'nin "her token'da sinyal" avantajı birleşir.

**Problem:** SFT'de model büyük modelin cevaplarını taklit eder. Sinyal yoğundur (her token'da), ama veri modelin kendi üretimi değildir; model kendi yaptığı hatalardan nasıl çıkacağını görmez. RL'de model kendi cevabını üretir ([on-policy](00_terimler.md#on-policy-ve-off-policy)), ama sinyal seyrektir: uzun bir cevabın sonunda tek bir puan. [On-policy distillation](00_terimler.md#on-policy-distillation-opd) ikisinin iyi yanını birleştirmeyi hedefler.

**Ne yaptılar:**
1. **Rollout eğitilen modelden.** Cevabı eğitilen (küçük) model üretir.
2. **Büyük model her token'ı puanlar.** Büyük model, cevaptaki her token için log-prob hesaplar: "ben bu noktada bu token'ı ne kadar olası bulurdum". Ayrı bir reward model gerekmez.
3. **Token başına [advantage](00_terimler.md#advantage).** Advantage, bir token'ın beklenenden ne kadar iyi olduğunu söyleyen sayıdır. Burada advantage, iki modelin token olasılıkları arasındaki farktır (reverse KL'in negatifi). Küçük model, büyük modelin düşük olasılık verdiği bir token seçtiyse o token eksi sinyal alır. Örnek: küçük model "SELECT *" yazdı, büyük model o noktada "SELECT name" bekliyordu; "*" token'ı cezalanır.
4. **Discount 0.** Her token yalnızca kendi puanıyla değerlendirilir; sonraki token'ların puanı geriye taşınmaz.
5. **Loss.** RL'in [importance-sampling](00_terimler.md#importance-sampling) loss'u kullanılır (veriyi üreten model ile güncellenen model arasındaki küçük farkı düzelten ağırlıklandırma).
6. **Varsayılan ayarlar.** Batch başına 64 prompt, prompt başına 4 örnek.
7. **Akıl yürütme deneyi.** Qwen3-8B-Base, OpenThoughts-3'ten 400K prompt'la SFT'lenmiş bir checkpoint'ten başladı (AIME'24'te %60). Büyük model olarak Qwen3-32B düşünülmüştü; Qwen3-8B biraz daha iyi çıktığı için o kullanıldı.
8. **Kişiselleştirme deneyi.** Model, şirket içi dokümanlarla [mid-training](00_terimler.md#mid-training)'den (yeni bilgi öğretmek için ara eğitim) geçince talimata uyma yeteneği kayboldu. Bunu Tulu3 prompt'larıyla on-policy distillation geri getirdi.

**Sonuç:** Yazarların raporuna göre:
- ~150 adımda (~77K prompt) AIME'24 %60'tan %70'e çıktı. SFT'nin bu seviyeye ~2M prompt'ta ulaşacağı tahmin ediliyor. Qwen3 raporundaki RL ise %67.6'da kalmış ve 17.920 GPU saati harcamış.
- FLOP (toplam hesaplama miktarı) olarak, 2M prompt'luk SFT'ye göre 9-30 kat daha ucuz.
- Kişiselleştirme: yalnızca dokümanla mid-training IF-eval'i %85'ten %45'e düşürdü. %70 doküman / %30 sohbet karışımı %79'da kaldı. Üstüne distillation ile %83'e döndü; iç bilgi skoru %41'de kaldı (taban %18). Yani yeni bilgi korunurken kaybolan yetenek büyük ölçüde geri geldi.
- [LoRA](00_terimler.md#lora) rank 32 ile: SFT sonrası full fine-tuning'den %13 geride, on-policy distillation sonrası yalnızca %6 geride.

**Kaynak notu:** Kaynak bir blog yazısı. "SFT ~2M prompt'ta ulaşır" rakamı ölçüm değil, tahmin.

**Bizim için:** Büyük model (9B) API'de token log-prob'u verebiliyorsa, 0.8B'nin kendi tool-call trajectory'lerini 9B'nin log-prob'larıyla düzeltmek, az veriyle SFT'den çok daha verimli olabilir. Yerel 4B ile yerel 0.8B arasında bunu MLX'te de yapmak mümkün.

---

## LoRA Without Regret (Thinking Machines Lab, Eylül 2025) — [blog](https://thinkingmachines.ai/blog/lora/)
**Tek cümlede:** LoRA'nın hangi koşullarda full fine-tuning kadar iyi olduğunu SFT ve RL için sistematik olarak ölçtüler (John Schulman ve ekip).

**Problem:** [LoRA](00_terimler.md#lora), modelin ağırlıklarını doğrudan değiştirmek yerine her katmana küçük ek matrisler ekler ve yalnızca onları eğitir. Rank, bu ek matrislerin genişliğidir; rank küçükse eğitilen parametre azdır. LoRA çok daha az bellek ister, ama full fine-tuning'den (bütün ağırlıkları eğitmek) kötü olup olmadığı ve hangi ayarlarla kullanılacağı net değildi.

**Ne yaptılar:**
1. **SFT deneyleri.** Tulu3 ve OpenThoughts3 verileriyle SFT.
2. **RL deneyleri.** MATH gibi setlerde policy-gradient RL (cevabın puanına göre modeli güncelleyen temel RL yöntemi).
3. **Ayar taraması.** Farklı rank'lar, LoRA'nın hangi katmanlara konduğu, LR ve batch boyutu tarandı.

**Sonuç:** Yazarların raporuna göre:
- Küçük-orta boy SFT veri setlerinde LoRA, full fine-tuning'e eşit. Veri LoRA'nın kapasitesini aşınca geride kalıyor.
- RL'de rank 1 bile full fine-tuning'e eşit. Nedeni: policy gradient her episode'da (bir rollout'un sonunda) yaklaşık sabit, birkaç bitlik bilgi öğreniyor ("iyi mi kötü mü"). MATH örneği: 10.000 problem × 32 örnek ≈ 320.000 bit bilgi. Llama-3.1-8B'de rank-1 LoRA bile ≈ 3M parametre; yani kapasite fazlasıyla yetiyor.
- LoRA bütün katmanlara, özellikle MLP'ye (her katmanda attention'dan sonra gelen ve parametrelerin çoğunu tutan kısım) uygulanmalı. Yalnızca attention'a uygulanan LoRA kötü sonuç veriyor.
- En iyi LoRA LR'ı, full fine-tuning'in ~10 katı (ölçülen çarpan 9.8).
- LoRA büyük batch'e daha az dayanıklı.

**Kaynak notu:** Kaynak bir blog yazısı; hakemli bir makale değil.

**Bizim için:** Mac'te (MLX) RL için düşük rank'lı LoRA yeterli: MLP dahil bütün katmanlar, LR ~10 kat, küçük batch. SFT'de veri çok büyürse LoRA'nın kapasite sınırına dikkat etmek gerekir.

---

## SmolLM3 post-training (Hugging Face, Temmuz 2025) — [blog](https://huggingface.co/blog/smollm3)
**Tek cümlede:** Düşünme modu açılıp kapanabilen 3B bir model için tamamen açık bir post-training reçetesi: mid-training → SFT → APO → model merging.

**Problem:** Küçük bir modelin hem uzun düşünerek hem de kısa cevap verebilmesi istendi ([thinking mode](00_terimler.md#thinking-mode): modelin cevaptan önce uzun bir düşünme metni yazıp yazmaması). Kullanıcı bunu `/think` ve `/no_think` ile seçiyor. İki modu tek modelde tutmak zordur: bir moda yapılan eğitim diğerini bozabilir. Ayrıca preference eğitimi uzun context yeteneğini düşürebiliyor. Hugging Face bu reçeteyi sonradan post-training'i de anlatan uzun bir rehbere ([Smol Training Playbook](https://huggingfacetb-smol-training-playbook.hf.space/)) dönüştürdü.

**Ne yaptılar:**
1. **Akıl yürütme mid-training'i.** OpenThoughts3-1.2M ve Llama-Nemotron post-training verisinin bir kısmından 35B token, 4 epoch (toplam ~140B token). Amaç, modele SFT'den önce uzun düşünme metinlerini ([long CoT](00_terimler.md#cot-ve-long-cot): cevaptan önce adım adım, uzun düşünme zinciri) bolca göstermek.
2. **SFT.** 1.8B token: 1B düşünmesiz, 0.8B düşünmeli; sırasıyla 12 ve 10 veri seti. Eksik alanlar için Qwen3-32B'nin reasoning modunda ürettiği sentetik veri eklendi. 4 epoch. BFD packing (Best-Fit Decreasing) kullanıldı: kısa örnekler, dolgu token'ı boşa harcanmadan aynı diziye yerleştirildi.
3. **APO.** APO (Anchored Preference Optimization), DPO ailesinden bir preference yöntemi. Düşünmesiz çiftler Tulu3 preference verisinden geldi. Düşünmeli çiftlerde chosen Qwen3-32B'nin, rejected Qwen3-0.6B'nin cevabı (bu, aşağıdaki delta learning fikri).
4. **Model merging.** MergeKit aracıyla APO checkpoint'lerinden bir "model soup" yapıldı (aynı başlangıçtan gelen birkaç checkpoint'in ağırlıklarının ortalaması). Sonra bu soup, mid-training checkpoint'iyle 0.9 / 0.1 oranında lineer merge edildi (ağırlıkların %90'ı soup'tan, %10'u eski checkpoint'ten). Amaç, 128K token'a kadar uzun context başarısını geri getirmekti.

**Sonuç:** Yazarların raporuna göre, merge, APO sırasında düşen RULER (uzun context'te bilgi bulma ve kullanma benchmark'ı) skorunu geri kazandırdı.

**Kaynak notu:** Kaynak bir blog yazısı. Blog ayrıntılı benchmark tablosunu model sayfasına bırakıyor; bu dosyada rakam yok.

**Bizim için:** Küçük modelde SFT'den sonra uzmanlaşan checkpoint'i eski genel checkpoint'le lineer merge etmek, Text-to-SQL'e özelleşirken kaybedilen genel yeteneği (ör. talimata uyma) ucuzca geri getirebilir.

---

## The Delta Learning Hypothesis (UW, AI2, Temmuz 2025) — [2507.06187](https://arxiv.org/abs/2507.06187)
**Tek cümlede:** Preference eğitiminde chosen ve rejected cevapların ikisi de zayıf olsa bile, aradaki kalite farkı ("delta") modeli iyileştirmeye yetiyor.

**Problem:** DPO için genelde güçlü bir etiketleyici (ör. GPT-4o) ya da çok güçlü bir modelin cevapları gerekir. Bu pahalıdır. Öte yandan eğitilen modelden daha zayıf modellerin cevaplarıyla SFT yapmak modele zarar verir: model kötü cevapları taklit eder. Soru şuydu: zayıf cevaplar, SFT'de değil de çift olarak kullanılırsa işe yarar mı?

**Ne yaptılar:**
1. **Zayıf çiftler kurdular.** Her soru için 3B bir modelin cevabı chosen, daha küçük 1.5B bir modelin cevabı rejected oldu. İkisi de eğitilen 8B modelden zayıf. Güçlü bir etiketleyici kullanılmadı. Örnek: 3B'nin biraz eksik cevabı ile 1.5B'nin daha da eksik cevabı; model "3B'nin yönüne doğru" gitmeyi öğrenir.
2. **8B modeli DPO ile eğittiler.** Bu çiftlerle DPO.
3. **Karşılaştırma için SFT.** Aynı zayıf verilerle tek başına SFT'nin modele zarar verdiğini gösterdiler.
4. **Teorik açıklama.** Basit bir lojistik regresyon modelinde, iki zayıf modelin farkının daha güçlü bir eğitilen modele faydalı yön verdiğini gösterdiler: fark, "hangi yön daha iyi" bilgisini taşır.

**Sonuç:** Yazarların raporuna göre, 11 benchmark'lık setin ortalamasında model, aynı tabandan ama çok daha güçlü etiketleyicilerle eğitilmiş Tülu 3'e eşit çıktı. Yani pahalı etiketleme olmadan aynı kazanç alındı. Bu fikir Olmo 3'ün Think DPO verisinin ve SmolLM3'ün APO çiftlerinin temeli oldu (ikisinde de chosen büyük model, rejected 0.6B).

**Bizim için:** DPO çifti için mükemmel cevap gerekmiyor: aynı soruda 4B'nin daha iyi trajectory'si ile 0.8B'nin daha kötü trajectory'si bile çift kurmaya yetebilir.

---

## FlexOlmo (AI2, UW, Temmuz 2025) — [2507.07024](https://arxiv.org/abs/2507.07024)
**Tek cümlede:** Her biri kendi kapalı verisinde ayrı eğitilen alan uzmanlarını, ortak eğitim yapmadan tek bir MoE modelinde birleştirdiler.

**Problem:** Birçok kurumun verisi paylaşılamaz (ör. sağlık, hukuk). Bu verilerle ortak bir model eğitmek için veriyi tek yere toplamak gerekir; bu çoğu zaman mümkün değil. Ayrıca bir veri sahibi sonradan verisini modelden çekmek isteyebilir. Amaç, her veri sahibinin kendi uzmanını ayrı eğitip sonradan birleştirebilmesiydi.

**Ne yaptılar:**
1. **Ortak başlangıç.** Kamuya açık veriyle eğitilmiş genel bir uzman var. Bütün alan uzmanları buradan başlar.
2. **Bağımsız uzmanlar.** Her alan uzmanı kendi verisinde, diğerlerinden habersiz eğitilir.
3. **Birleştirme.** Uzmanlar tek bir MoE modelinde (her token'ı bazı uzmanlara yönlendiren mimari) toplanır. Hangi uzmana gidileceğine "domain-informed routing" karar verir: yönlendirme, her uzmanın veri alanı bilgisine dayanır. Birleştirmeden sonra ortak eğitim yok.
4. **Esneklik.** Bir uzman ve verisi, çıkarım sırasında modele eklenip çıkarılabiliyor.
5. **Veri ve ölçek.** FlexMix: kamuya açık veri ve kapalı veriyi taklit eden yedi alan seti. Model 37B toplam (20B aktif) parametreye kadar.

**Sonuç:** Yazarların raporuna göre, 31 görevde genel uzmanı bağımsız uzmanlarla birleştirmek ortalama %41 göreli iyileşme getirdi. Yöntem, önceki model merging yöntemlerini ortalama %10.1 geçiyor. Aynı FLOP'la (aynı hesaplama miktarıyla), veri kısıtı olmadan eğitilmiş standart bir MoE'yi de geçiyor.

**Kaynak notu:** Özette %41'lik iyileşmenin hangi modele göre ölçüldüğü açıkça yazmıyor; bunun için makalenin tamamına bakmak gerekir.

**Bizim için:** Ölçeği bize uymaz ama fikir uyar: farklı veritabanı türleri için ayrı LoRA uzmanları eğitip birleştirmek mümkün. Yine de tek bir küçük modelde merge ya da routing maliyeti önce ölçülmeli.

---

## Skywork-Reward-V2 (Skywork AI, Temmuz 2025) — [2507.01352](https://arxiv.org/abs/2507.01352)
**Tek cümlede:** İnsan ve LLM'in birlikte etiketlediği 40M çiftlik bir preference verisiyle 0.6B–8B arası güçlü reward model'ler eğittiler.

**Problem:** Reward model, bir cevabın ne kadar iyi olduğunu puanlayan ayrı bir modeldir ([reward model](00_terimler.md#reward-model-grm-ve-prm)); doğrulanamayan işlerde (sohbet, yazı) RL'in puanını verir. Açık reward model'ler benchmark'larda zayıf kalıyordu. Yazarlar ana nedenin veri olduğunu savundu: dar, sentetik etiketli ve kalite kontrolü yapılmamış preference verisi.

**Ne yaptılar:**
1. **Büyük veri seti.** SynPref-40M: 40 milyon preference çifti (aynı soruya iki cevap ve hangisinin daha iyi olduğu).
2. **İki aşamalı küratörlük.** Birinci aşamada insanlar doğrulanmış etiketler verdi. İkinci aşamada LLM'ler bu insan etiketlerini örnek alarak geri kalan veriyi otomatik süzdü. Böylece insan kalitesi büyük ölçeğe taşındı.
3. **Model eğitimi.** Reward model'ler bunun 26M çiftlik süzülmüş alt kümesiyle eğitildi; 0.6B'den 8B'ye sekiz model.

**Sonuç:** Yazarların raporuna göre, yedi reward model benchmark'ında en iyi sonucu aldılar ve generative reward model'leri (puanı metin üreterek, ör. önce gerekçe yazarak veren LLM yargıçlar) geçtiler. Ablation'lar kazancın hem veri ölçeğinden hem küratörlük kalitesinden geldiğini gösteriyor.

**Kaynak notu:** Özette sayı verilmiyor; bu yüzden burada rakam yok.

**Bizim için:** Bizim reward'ımız zaten çalıştırılabilir (sonuç doğru mu), bu yüzden ayrı bir reward model şu an gereksiz. Ama 0.6B gibi küçük bir reward model'in iyi veriyle güçlü olabilmesi, ileride trajectory kalitesini puanlamak için bir seçenek.

---

## DeepSWE (UC Berkeley Agentica, Together AI, Temmuz 2025) — [model kartı](https://huggingface.co/agentica-org/DeepSWE-Preview)
**Tek cümlede:** Qwen3-32B'yi SFT olmadan, yalnızca RL ile çok turlu bir yazılım mühendisliği agent'ı olarak eğittiler.

**Problem:** Yazılım agent'ları genelde önce büyük modellerin trajectory'leriyle SFT'den geçer. Bu veriyi üretmek pahalıdır. Yazarlar, güçlü bir taban modelin (Qwen3-32B, thinking açık) doğrudan RL ile agent olmayı öğrenip öğrenemeyeceğini denedi. Uzun, çok adımlı görevlerde RL'in ayrıca bir sorunu var: birçok trajectory süre ya da context sınırına takılıp yarım kalır.

**Ne yaptılar:**
1. **Görevler.** R2E-Gym'in (gerçek yazılım projelerinden kurulmuş, çalıştırılabilir hata düzeltme ortamları) bir alt kümesinden 4.5K problem.
2. **Tool'lar.** Dört tool: bash, arama, dosya editörü, finish/submit.
3. **Reward.** İkili: model'in yaptığı değişiklik (patch) örneklenen test'leri süre sınırı içinde geçerse 1, yoksa 0. Testler iki türdü: Pass2Pass (önceden geçen testler hâlâ geçiyor mu) ve Fail2Pass (hatayı gösteren testler artık geçiyor mu).
4. **GRPO üzerine değişiklikler.** Clip high ve KL yok (DAPO'dan). Reward'ları std'ye bölmeme ve loss'u cevap uzunluğu yerine max context'e bölme (Dr. GRPO'dan; aşağıda ayrı bölüm). Leave-one-out advantage (RLOO: bir cevap, aynı sorudaki diğer cevapların ortalamasıyla karşılaştırılır). Entropy loss yok.
5. **Compact filtering.** Max context'e, max adım sayısına ya da süre sınırına takılan trajectory'lerin loss'u maskelendi ([loss masking](00_terimler.md#loss-masking): bu örnekler güncellemeye katılmaz). Yani yarım kalan deneme "yanlış" diye cezalanmadı, yok sayıldı.

**Sonuç:** Yazarların raporuna göre, SWE-Bench Verified'da (gerçek GitHub hatalarını düzeltme) Pass@1 %42.2 (16 koşunun ortalaması). Hibrit best@16 ile %59: 16 aday çözüm üretilip içlerinden biri seçiliyor ([test-time scaling](00_terimler.md#test-time-scaling): cevap anında daha çok compute harcayarak başarıyı artırmak). 200 RL adımında skor ~%20 arttı.

**Kaynak notu:** Kaynak bir model kartı; ayrı bir makale yok. "~%20 artış"ın göreli mi mutlak mı olduğu burada belirtilmiyor.

**Bizim için:** Bizim `submit`'li döngümüze çok benzer: max adıma ya da context'e takılan trajectory'leri cezalandırmak yerine loss'tan maskelemek, küçük modelin yarım kalan denemelerinden yanlış sinyal öğrenmesini önler.

---

## SPIRAL: Self-Play on Zero-Sum Games (NUS, Sea AI Lab, UW ve diğerleri, Haziran 2025) — [2506.24119](https://arxiv.org/abs/2506.24119)
**Tek cümlede:** Modeli, kendi sürekli gelişen kopyasına karşı basit oyunlarda RL ile eğittiler ve bu oyunların genel akıl yürütmeyi iyileştirdiğini gösterdiler.

**Problem:** RL için doğrulanabilir sorular ve cevaplar gerekir; bunları toplamak emek ister. Ayrıca soruların zorluğu sabittir: model gelişince sorular kolay kalır. [Self-play](00_terimler.md#self-play)'de (modelin kendi kopyasına karşı oynaması) rakip de modelle birlikte güçlenir. Böylece zorluk kendiliğinden artar ve kendiliğinden bir curriculum oluşur.

**Ne yaptılar:**
1. **Oyunlar.** Çok turlu, sıfır toplamlı (bir tarafın kazancı diğerinin kaybı) üç oyun: TicTacToe (XOX), Kuhn Poker (az kartlı basit bir poker) ve Simple Negotiation (basit pazarlık).
2. **Sistem.** Tamamen online, çok turlu, çok agent'lı bir RL sistemi. Model iki tarafı da oynar.
3. **RAE.** Role-conditioned advantage estimation: her rol (ör. ilk oynayan ve ikinci oynayan) için ayrı bir baseline (beklenen ortalama puan). Örnek: ilk oynayan oyunu daha sık kazanıyorsa, onun kazanması "olağan" sayılır ve fazla ödüllendirilmez. Bu, eğitimi kararlı tuttu.
4. **Modeller.** Qwen ve Llama ailesinden dört taban model (DeepSeek-R1-Distill-Qwen-7B dahil).
5. Makale ICLR 2026'da yayımlandı.

**Sonuç:** Yazarların raporuna göre, 8 akıl yürütme benchmark'ında %10'a kadar iyileşme oldu. Bu, 25.000 uzman oyun trajectory'siyle yapılan SFT'yi geçiyor; yani hazır uzman verisi olmadan daha iyi sonuç alındı. Birden çok oyunla eğitmek tek oyundan iyi çıktı.

**Bizim için:** Self-play bize doğrudan uymaz. Ama "her rol için ayrı baseline" fikri, küçük model ile büyük modelin aynı log'da farklı rollerde olduğu durumda advantage hesabında işe yarar.

---

## OctoThinker: Mid-training Incentivizes RL Scaling (SJTU GAIR, Haziran 2025) — [2506.20512](https://arxiv.org/abs/2506.20512)
**Tek cümlede:** Llama'nın RL'den Qwen kadar fayda görmemesinin nedenini mid-training verisinde buldular ve RL'e uygun bir mid-training reçetesi önerdiler.

**Problem:** Aynı RL reçetesi Qwen modellerinde büyük kazanç verirken Llama modellerinde çok az kazanç veriyor. Bu, RL'in başarısının algoritmadan çok taban modelin daha önce ne gördüğüne bağlı olduğunu düşündürüyor. Yazarlar, pretraining ile RL arasına konan mid-training'in (belli bir yetenek için yapılan ara eğitim) bu farkı kapatıp kapatamayacağını araştırdı.

**Ne yaptılar:**
1. **"Stable-then-Decay" takvimi.** Önce sabit LR ile 200B token. Sonra LR düşürülerek 20B token; bu ikinci aşama üç ayrı dala bölündü, her dal farklı bir CoT (chain-of-thought, adım adım düşünme) verisine odaklandı.
2. **Corpus karşılaştırması.** Yüksek kaliteli math corpus'u MegaMath-Web-Pro faydalı çıktı; FineMath-4plus çıkmadı.
3. **Veri biçimi karşılaştırması.** Soru–cevap (QA) biçimli veri, özellikle uzun CoT'li olanı, sonraki RL'i iyileştirdi. Instruction verisi eklemek bu etkiyi artırdı. Ama uzun CoT cevapları uzatıp RL'i kararsızlaştırabiliyor.

**Sonuç:** Yazarların raporuna göre, mid-training'i büyütmek sonraki RL başarısını tutarlı biçimde artırıyor. OctoThinker ailesi (Llama tabanlı) Qwen ile arayı kapatıyor. 70B token'ı aşan MegaMath-Web-Pro-Max corpus'u açıldı.

**Kaynak notu:** Özette benchmark sayısı yok; bu yüzden burada rakam yok.

**Bizim için:** RL'den önce modelin tool-call biçimini ve SQL'i "görmüş" olması gerekiyor. Bu bizde mid-training değil, kısa bir SFT aşamasıyla sağlanabilir.

---

## Spurious Rewards: Rethinking Training Signals in RLVR (UW, AI2, Haziran 2025) — [2506.10947](https://arxiv.org/abs/2506.10947)
**Tek cümlede:** Qwen2.5-Math modellerinde rastgele, yanlış ya da yalnızca biçime bakan reward'larla bile RLVR büyük kazanç veriyor; Llama ve OLMo'da vermiyor.

**Problem:** RLVR'ın modele doğru cevabı öğrettiği varsayılır. Ama birçok makale aynı model ailesini (Qwen) kullanıyordu. Yazarlar, kazancın gerçekten reward'daki bilgiden mi geldiğini, yoksa modelin zaten bildiği bir davranışın ortaya çıkmasından mı geldiğini test etti. Spurious reward, gerçek doğrulukla ilgisi olmayan reward'dır.

**Ne yaptılar:**
1. **Reward türleri.** Doğru reward (cevap doğruysa 1), yanlış etiket reward'ı (yanlış cevaba ödül), rastgele reward (yazı-tura gibi; cevaba bakmadan) ve format reward (yalnızca biçim, ör. cevap belirli bir kutunun içinde mi).
2. **Ortak reçete.** DeepScaleR verisi, GRPO. KL kapalı, LR 5e-7 sabit, mini-batch 128, rollout batch 64, prompt başına 16 rollout, temperature 1.
3. **Model aileleri.** Qwen2.5-Math, Llama3 ve OLMo2 üzerinde aynı deneyler.
4. **Mekanizma analizi.** Qwen-Math'in "kodla akıl yürütme" davranışını izlediler: model Python kodu yazıyor ama çalıştırmadan, kodu düşünme aracı olarak kullanıyor.

**Sonuç:** Yazarların raporuna göre, Qwen2.5-Math-7B'nin MATH-500'deki (MATH'ten seçilmiş 500 yarışma sorusu) mutlak kazancı:
- Doğru reward: +29.1
- Yanlış etiket: +24.1
- Rastgele reward: +21.4
Yani rastgele reward, gerçek reward'ın kazancının yaklaşık dörtte üçünü veriyor. Format reward AMC'de (ABD lise matematik yarışması) +13.8 getirdi. Llama3 ve OLMo2'de spurious reward'lar az kazanç ya da kayıp getirdi. Yazarların açıklaması: GRPO'nun clip terimindeki bir yanlılık, modelin zaten sık yaptığı davranışı güçlendiriyor. Qwen-Math'te bu davranış kodla akıl yürütme; oranı %65'ten %90'ın üstüne çıktı. Ders: puandaki artış her zaman reward'ın öğrettiği şeyden gelmeyebilir ([reward hacking](00_terimler.md#reward-hacking) ile akraba bir uyarı: model, reward'ın asıl amacını değil başka bir şeyi öğrenebilir).

**Bizim için:** Bizim modelimiz de Qwen. Bir RL kazancını gerçek sayabilmek için rastgele reward'lı bir kontrol koşusu, mümkünse de ikinci bir model ailesiyle tekrar gerekir.

---

## POLARIS (HKU NLP, ByteDance Seed, Fudan, Haziran 2025) — [blog](https://hkunlp.github.io/blog/2025/Polaris)
**Tek cümlede:** Zaten güçlü olan küçük akıl yürütme modellerini RL ile daha da ileri taşıyan bir reçete; ağırlık noktası veri zorluğu ve temperature.

**Problem:** Qwen3-4B gibi modeller zaten güçlü. Böyle bir modelde RL'in çoğu soru kolay gelir: model 8 denemenin 8'ini de çözer. Bu sorularda bütün cevaplar aynı puanı alır, advantage sıfırdır ve model hiçbir şey öğrenmez. Ayrıca güçlü modellerde çeşitlilik düşüktür; aynı soruya hep benzer cevaplar verirler.

**Ne yaptılar:**
1. **Veri.** DeepScaleR-40K ve AReaL-106K'dan Polaris-Dataset-53K kuruldu.
2. **Zorluk filtresi.** Model 8 denemenin 8'ini çözüyorsa soru atıldı. DeepScaleR-40K 26K'ya, Qwen3-4B için 53K 30K'ya indi. Hedef, zor sorulara biraz ağırlık veren bir zorluk dağılımı (yazarlar şeklinden dolayı buna "ters J" diyor).
3. **Aşama aşama süzme.** Her aşamanın sonunda doğruluğu 0.9'u geçen örnekler atıldı; model geliştikçe veri yeniden zorlaştırıldı.
4. **Temperature ayarı.** Temperature, cevapların çeşitliliğine bakılarak seçildi ve aşama aşama artırıldı. 4B: 1.4 → 1.45 → 1.5. 7B: 0.7 → 1.0 → 1.1.
5. **Rollout rescue.** 8 denemenin hiçbiri doğru değilse (0/8), o soru için daha önce bulunmuş bir doğru cevap bir buffer'dan (önceki doğru cevapların saklandığı yer) gruba eklendi. Böylece grupta en az bir doğru cevap olur ve sinyal oluşur.
6. **Sıfır advantage'lı örnekleri değiştirme.** Bütün cevapları aynı puanı alan örneklerin yerine, karışık sonuçlu (bazı cevapları doğru, bazıları yanlış) örneklerin kopyaları konuldu.
7. **Diğer ayarlar.** Entropy loss ve KL yok, clip high. Uzunluk: eğitimde 52K token'a kadar. Çıkarımda YaRN (factor 1.5): modelin eğitildiğinden daha uzun metni okuyabilmesi için konum kodlamasını esneten yöntem.
8. **Donanım.** 4B: 32 H800 GPU'da 10 gün, batch 128, soru başına 8 rollout.

**Sonuç:** Yazarların raporuna göre:
- POLARIS-4B-Preview: AIME24 81.2 / AIME25 79.4. Taban Qwen3-4B: 73.8 / 65.6. Yani +7.4 ve +13.8 puan.
- POLARIS-7B-Preview: 72.6 / 52.6 (tabanının rakamı bu dosyada yok).
- YaRN ile 32K token'ı aşan cevaplarda doğruluk %26'dan %50'nin üstüne çıktı.

**Kaynak notu:** Kaynak bir blog yazısı; hakemli bir makale değil.

**Bizim için:** RL verisini küçük modelin kendi başarı oranına göre süzmek (hep çözdüğü soruyu atmak) ve hiç çözemediği soruda büyük modelin doğru trajectory'sini gruba eklemek ("rollout rescue") bizim handoff log'larımızla doğal olarak yapılabilir.

---

## OpenThoughts: Data Recipes for Reasoning Models (OpenThoughts projesi; yazarlar arasında Ludwig Schmidt ve Alexandros G. Dimakis; Haziran 2025) — [2506.04178](https://arxiv.org/abs/2506.04178)
**Tek cümlede:** Akıl yürütme için SFT verisi üretmenin her adımını 1.000'den fazla kontrollü deneyle ölçtüler; sonuçta OpenThoughts3-1.2M verisini ve OpenThinker3-7B modelini yayımladılar.

**Problem:** Güçlü akıl yürütme modellerinin SFT verisi genelde gizlidir. Açık veri setleri ise "şunu yaptık" der ama neden o seçimi yaptığını ölçmez. Soruları nereden almalı, kaç cevap üretmeli, hangi soruları ve cevapları atmalı? Bu kararların her birinin etkisi bilinmiyordu. Makale ICLR 2026'da yayımlandı.

**Ne yaptılar:**
1. **Küçük ölçekli deney düzeni.** Ablation'lar ~31.6K örnekle, Qwen2.5-7B-Instruct üzerinde yapıldı. Her deneyde tek bir karar değiştirildi.
2. **Soru kaynağı.** En iyi bir-iki kaynak, 8-16 kaynağı karıştırmaktan iyi çıktı.
3. **Soru filtresi.** Soruları seçmek için LLM tabanlı filtreler, fastText (hızlı, kelime tabanlı bir metin sınıflandırıcı) ve embedding tabanlı filtrelerden iyi çıktı. Kodda en iyi filtre, LLM'in soruya verdiği zorluk etiketiydi. Math ve bilimde en iyi filtre, LLM'in cevabının uzunluğuydu: uzun cevap = zor soru.
4. **Soru başına çok cevap.** Her soru için ~16 cevap örneklemek veriyi büyütmenin etkili yolu oldu. Aynı sorulara daha çok cevap eklemek, daha çok farklı soru eklemek kadar ya da ondan iyi çıktı.
5. **Cevap filtresi.** Cevapları süzmek (doğrulama, çoğunluk oyu, uzunluk) denendi. Doğrulama, yanlış cevapları atmaktır ([rejection sampling](00_terimler.md#rejection-sampling): çok cevap üretip yalnızca kontrolden geçenleri tutmak). Bu filtreler, bütün cevaplarla eğitmeyi güvenilir biçimde geçemedi.
6. **Veriyi üreten model.** Farklı büyük modellerin cevapları karşılaştırıldı; sonunda QwQ-32B seçildi.
7. **Son veri.** 1.2M örnek: 850K math, 250K kod, 100K bilim; cevapları QwQ-32B üretti.

**Sonuç:** Yazarların raporuna göre:
- Kodda en iyi 2 kaynak, 16 kaynağı karıştırmayı ~%5 geçti.
- LLM tabanlı soru filtreleri rastgele seçime göre math'te ~%4, kodda ~%6 kazanç getirdi.
- OpenThinker3-7B: AIME25 %53.3 (lise matematik olimpiyatı), LiveCodeBench %51.7 (yarışma kodlama soruları), GPQA Diamond %53.7 (uzman düzeyi fen soruları). DeepSeek-R1-Distill-Qwen-7B'ye göre sırasıyla +15.3, +17.2 ve +20.5 puan.
- Benchmark'ta daha zayıf olan QwQ-32B, DeepSeek-R1'den daha iyi veri üretti (kod +1.9, math +2.6). Yani "en güçlü model en iyi veriyi üretir" varsayımı doğru değil.

**Bizim için:** Büyük modelin bir soruda birden çok trajectory'sini SFT verisine almak, yeni soru bulmaktan ucuz bir büyütme yolu. "Zor soru" için uzun trajectory iyi bir vekil.

---

## Skywork Open Reasoner 1 (Skywork AI, Mayıs 2025) — [2505.22312](https://arxiv.org/abs/2505.22312)
**Tek cümlede:** DeepSeek-R1-Distill modelleri (7B, 32B) üzerinde uzun düşünme için açık bir RL reçetesi; entropy çöküşünü ayrıntılı incelediler ve ağırlıkları, kodu ve veriyi açtılar.

**Problem:** Uzun düşünen modellerle RL yaparken sık görülen bir sorun var: [entropy collapse](00_terimler.md#entropy-ve-entropy-collapse). Entropy, modelin bir sonraki token'dan ne kadar emin olmadığını ölçer. Entropy çökünce model hep aynı cevap kalıbını üretir, yeni yol denemez ve öğrenme durur. Ayrıca RL compute'unun çoğu, modelin hep çözdüğü ya da hiç çözemediği sorulara gidip boşa harcanır.

**Ne yaptılar:**
1. **Veri toplama ve temizlik.** Ön işleme ve tekilleştirmeden sonra ~105K math ve 13.7K kod (2.7K LeetCode + 11K TACO) sorusu. İspat soruları (cevabı otomatik kontrol edilemez) ve test'i olmayan kod soruları atıldı.
2. **[Decontamination](00_terimler.md#decontamination).** Test sorularının eğitim verisine sızmasını temizleme; AIME24 ve AIME25'e karşı yapıldı.
3. **Modele göre zorluk filtresi.** Her soru math'te 16, kodda 8 kez çözdürüldü (temperature 1.0, 32K context). Hiç çözülemeyen (0/N) ve hep çözülen (N/N) sorular atıldı.
4. **Kalite filtresi.** Math'te iki LLM'in toplam 32 oyuyla bozuk ya da belirsiz sorular elendi.
5. **Aşamalar arası süzme.** Her aşamanın başında, önceki aşamada hep çözülen sorular atıldı. Advantage'ı sıfır olan gruplar (bütün cevapları aynı puanı alan) batch'ten çıkarıldı.
6. **MAGIC algoritması.** Loss token düzeyinde hesaplanır ve cevap uzunluğuna bölünmez. Adaptif entropy kontrolü: entropy'yi 0.2 hedefi civarında tutmaya çalışan otomatik bir ayar. KL yok, rollout temperature 1.0, on-policy güncelleme (her rollout batch'iyle yalnızca bir güncelleme; eski veriyle tekrar tekrar eğitilmez).
7. **Kademeli context.** Context aşama aşama büyütüldü: 8K → 16K → 32K.

**Sonuç:** Yazarların raporuna göre:
- Skywork-OR1-32B: AIME24 82.2, AIME25 73.3, LiveCodeBench 63.0. Üç benchmark ortalaması %57.8'den %72.8'e çıktı (+15 puan).
- 7B: 70.2 / 54.6 / 47.6.
- Entropy hızlı çökerse test başarısı düşüyor.
- Batch başına daha çok SGD adımı (aynı rollout'larla birden çok güncelleme, yani [off-policy](00_terimler.md#on-policy-ve-off-policy) veriyle eğitim) çöküşü hızlandırıyor.
- Düşük temperature erken çöküşe yol açıyor.

**Bizim için:** Küçük modelde RL'e başlamadan önce her soruyu küçük modelle birkaç kez koşup hep çözülen ve hiç çözülemeyen soruları atmak, compute'u boşa harcamamanın en ucuz yolu.

---

## The Entropy Mechanism of RL for Reasoning LMs (Shanghai AI Lab, Tsinghua ve diğerleri, Mayıs 2025) — [2505.22617](https://arxiv.org/abs/2505.22617)
**Tek cümlede:** RL'in başında entropy'nin neden hızla çöktüğünü açıkladılar, entropy ile başarı arasında basit bir formül buldular ve çöküşü önleyen iki yöntem önerdiler.

**Problem:** Entropy'ye müdahale edilmezse RL'in başında policy entropy'si (modelin token seçimindeki belirsizlik) hızla düşüyor. Başarı da tam bu sırada doyuyor: model yeni yollar denemeyi bırakıyor. Bunun nedeni ve nasıl önleneceği net değildi.

**Ne yaptılar:**
1. **Formül.** Entropy ile başarı arasında şu ilişkiyi buldular: R = −a·e^H + b (R başarı, H entropy, a ve b koşuya göre değişen sabitler). Sözle: entropy düştükçe başarı artıyor, ama bu artışın bir tavanı var. Entropy sıfıra indiğinde e^0 = 1 olur ve başarı b − a'da durur. Yani entropy bittiğinde başarı tahmin edilebilir bir sınıra takılır.
2. **Teorik açıklama.** Entropy'nin nasıl değişeceğini, bir token'ın olasılığı ile o token'ın güncellemede ne kadar değiştiği arasındaki kovaryans (birlikte değişme) belirliyor. Policy gradient'te bu kovaryans advantage ile orantılı ve eğitimde çoğunlukla pozitif. Sözle: model zaten yüksek olasılık verdiği token'lar iyi sonuç verdiğinde onları daha da olası yapıyor. Örnek: model "SELECT"ten sonra hep "*" yazıyor ve bu çoğu zaman işe yarıyorsa, "*" giderek tek seçenek haline gelir. Bu yüzden entropy düşüyor.
3. **Çözüm.** Yüksek kovaryanslı token'ları (çöküşü en çok iten token'ları) hedefleyen iki yöntem. Clip-Cov: bu token'ların güncellemesini kırpar. KL-Cov: bu token'lara KL cezası uygular (değişimlerini frenler).

**Sonuç:** Yazarların raporuna göre, iki yöntem de entropy çöküşünden kaçınıp daha iyi sonuç veriyor.

**Kaynak notu:** Özette sayı yok; bu yüzden burada rakam yok.

**Bizim için:** RL koşusunda entropy'yi izlemek gerekir. Küçük modelin tool-call'ları hızla tek bir kalıba oturursa (ör. hep aynı `search_values` → `submit` sırası) daha fazla eğitim kazanç getirmez.

---

## The Unreasonable Effectiveness of Entropy Minimization in LLM Reasoning (UIUC, Mayıs 2025) — [2505.15134](https://arxiv.org/abs/2505.15134)
**Tek cümlede:** Hiç etiket kullanmadan, yalnızca modelin kendi cevaplarındaki entropy'yi düşürmenin (modeli kendinden daha emin yapmanın) akıl yürütmeyi iyileştirdiğini gösterdiler (Jiawei Han, Hao Peng grubu).

**Problem:** RLVR için doğru cevabı bilinen sorular gerekir. Doğru cevabı bilinmeyen (etiketsiz) veri ise çok daha boldur. Yazarlar, etiketsiz veride modelin kendi güvenini sinyal olarak kullanmanın işe yarayıp yaramadığını sordu. Fikir: model doğru cevaplara genelde daha emin verir; emin olmayı ödüllendirmek doğru cevapları güçlendirebilir. Aynı dönemde Berkeley'den Intuitor ([2505.19590](https://arxiv.org/abs/2505.19590), Sergey Levine, Dawn Song), modelin kendi "self-certainty"sini (kendinden eminlik ölçüsü) tek reward olarak kullanıp GRPO ile benzer sonuç bildirdi.

**Ne yaptılar:** Üç yol denediler.
1. **EM-FT.** Model etiketsiz sorulara kendi cevaplarını üretir. Bu cevaplarda token entropy'sini düşüren bir fine-tuning yapılır.
2. **EM-RL.** RL yapılır, ama reward olarak yalnızca negatif entropy kullanılır: model ne kadar emin cevap verirse o kadar yüksek reward.
3. **EM-INF.** Eğitim yok. Cevap üretilirken logit'ler (token olasılıklarının ham değerleri) entropy düşecek şekilde ayarlanır.

**Sonuç:** Yazarların raporuna göre:
- EM-RL, Qwen-7B'de 60K etiketli örnekle eğitilen GRPO ve RLOO'ya eşit ya da daha iyi. Yani etiket olmadan, etiketli RL kadar kazanç.
- EM-INF, Qwen-32B'yi SciCode'da (bilimsel hesaplama kodu yazma) GPT-4o, Claude 3 Opus ve Gemini 1.5 Pro seviyesine getiriyor. Self-consistency'den (aynı soruya çok cevap üretip çoğunluğu seçme) 3 kat verimli.
- Intuitor math'te GRPO'ya eşit, koda daha iyi genelliyor.

**Bizim için:** Etiketsiz kullanım verisinde (`split = use`) ek sinyal olabilir. Ama Spurious Rewards bulgusu yüzünden Qwen'de bu tür kazançlar dikkatle kontrol edilmeli; bizde zaten gerçek bir reward (execution sonucu) var.

---

## Mixture-of-Thoughts ve OpenR1-Distill-7B (Hugging Face Open-R1, Mayıs 2025) — [GitHub](https://github.com/huggingface/open-r1)
**Tek cümlede:** DeepSeek-R1'in distill edilmiş 7B modelini tamamen açık veri ve kodla yeniden ürettiler; Open-R1 projesinin ilk adımı.

**Problem:** DeepSeek, R1'den distill ettiği küçük modelleri yayımladı ama distillation verisini yayımlamadı. Bu yüzden kimse aynı sonucu tekrar üretemiyor ya da veriyi değiştirip etkisini ölçemiyordu. Open-R1 bu veriyi açık olarak yeniden kurmayı hedefledi.

**Ne yaptılar:**
1. **Veri: Mixture-of-Thoughts.** DeepSeek-R1'den distill edilmiş, doğrulanmış 350K düşünme metni (trace). Math 93.7K (OpenR1-Math-220k), kod 83.1K (codeforces-cots), bilim 173K (Llama-Nemotron).
2. **Alan alan optimizasyon.** Her alanın verisi önce ayrı ayrı denenip en iyi hale getirildi, sonra birleştirildi (Phi-4-reasoning'in yöntemi).
3. **Alan kararları.** Kodda C++ ve Python trace'lerinin karışımı seçildi. Math'te 131K kolay soruluk ek bir "extended" alt küme eklenmedi: küçük bir kayıp karşılığında veri boyutu düşük tutuldu. Bilimde, prompt'u Qwen modelleriyle ön işlenmiş trace'ler atıldı (483K → 173K).
4. **Model ve SFT.** Qwen2.5-Math-7B'nin RoPE tabanı 300K'ya çıkarıldı. RoPE, token konumlarını kodlama yöntemidir; tabanı büyütmek modelin daha uzun context'i işlemesine yardım eder. 32K context, LR 4e-5, 5 epoch SFT.

**Sonuç:** Yazarların raporuna göre, OpenR1-Distill-7B: AIME24 52.7, GPQA Diamond 52.8 (uzman düzeyi fen soruları), LiveCodeBench v5 39.4. DeepSeek-R1-Distill-Qwen-7B: 51.3 / 52.4 / 37.4. Yani açık veriyle orijinal yakalandı ve biraz geçildi. MATH-500'de ise geride: 89.0'a karşı 93.5. Alanları birlikte eğitmek en iyi sonucu verdi.

**Kaynak notu:** Kaynak bir GitHub sayfası; ayrı bir makale yok.

**Bizim için:** SFT verisi alan alan (ör. veritabanı başına) ayrı ölçülüp sonra birleştirilebilir. Bizim ölçeğimizde LR ve epoch sayısı ilk taranacak iki ayar.

---

## Absolute Zero: Reinforced Self-play Reasoning with Zero Data (Tsinghua LeapLab ve diğerleri, Mayıs 2025) — [2505.03335](https://arxiv.org/abs/2505.03335)
**Tek cümlede:** Hiç dış veri kullanmadan, aynı modelin hem görev önerdiği hem çözdüğü ve doğrulamanın bir kod çalıştırıcıyla yapıldığı bir self-play RL (Absolute Zero Reasoner, AZR).

**Problem:** RLVR bile insanların hazırladığı soru–cevap çiftlerine muhtaç. Model insanlardan daha yetenekli hale gelirse, ona uygun zorlukta soru hazırlamak giderek zorlaşır. Yazarlar, modelin kendi eğitim görevlerini üretebilmesini istedi. Doğrulama için insan yerine kod çalıştırıcı kullanıldı: bir programın çıktısı çalıştırılarak kesin bilinir.

**Ne yaptılar:**
1. **Üç görev tipi.** Hepsi üç parça üzerine kurulu: program p, girdi i, çıktı o. Örnek: p = `def f(x): return x * 2`, i = 3, o = 6.
   - Deduction: p ve i verilir, o tahmin edilir ("f(3) kaç?").
   - Abduction: p ve o verilir, i bulunur ("f(?) = 6 olan girdi ne?").
   - Induction: girdi–çıktı örnekleri verilir, p yazılır ("3→6, 5→10 veren programı yaz").
2. **İki rol.** Model önce görev önerir (proposer), sonra çözer (solver). Kod çalıştırıcı görevin geçerli olup olmadığını ve cevabın doğru olup olmadığını kontrol eder.
3. **Önerenin reward'ı: öğrenilebilirlik.** Çözücünün o görevdeki ortalama başarısı 0 ise reward 0. Değilse reward 1 − başarı. Örnek: çözücü 4 denemenin 1'inde çözdüyse öneren 0.75 alır; 4'ünde de çözdüyse 0 alır. Yani hep çözülen ya da hiç çözülemeyen görev ödül almaz; en çok ödülü "zor ama çözülebilir" görev alır.
4. **Algoritma.** Task-Relative REINFORCE++: altı görev-rol birleşiminin (3 görev tipi × 2 rol) her biri için ayrı bir baseline.
5. **Modeller.** Qwen2.5-7B ve Qwen2.5-7B-Coder; ayrıca 3B, 14B ve Llama-3.1-8B.

**Sonuç:** Yazarların raporuna göre, AZR-Coder-7B:
- Kod ortalaması 56.6 → 61.6 (+5.0)
- Math ortalaması 23.9 → 39.1 (+15.2)
- Genel ortalama 40.2 → 50.4 (+10.2)
Hiç küratörlü veri görmeden, binlerce küratörlü örnekle eğitilmiş zero-RL modellerini genelde geçiyor (ör. ORZ 48.6). Kazanç model büyüdükçe artıyor: 3B +5.7, 7B +10.2, 14B +13.2.

**Bizim için:** Küçük modelde kazanç düşük. Ama "doğrulanabilir görev üretme" fikri bize uyar: veritabanından otomatik soru–SQL üretip execution ile doğrulamak eğitim verisini çoğaltabilir.

---

## Reinforcement Learning for Reasoning in LLMs with One Training Example (UW, Microsoft ve diğerleri, Nisan 2025) — [2504.20571](https://arxiv.org/abs/2504.20571)
**Tek cümlede:** Tek bir eğitim örneğiyle yapılan RLVR'ın (1-shot RLVR), binlerce örnekle yapılan RLVR'a yakın kazanç verdiğini gösterdiler.

**Problem:** RLVR için genelde binlerce doğrulanmış soru kullanılır. Ama bu soruların ne kadarının gerçekten gerekli olduğu bilinmiyordu. Eğer çok az örnek yetiyorsa, RL'in modele yeni bilgi mi öğrettiği yoksa var olan bir yeteneği mi açtığı sorusu da önem kazanır.

**Ne yaptılar:**
1. **Taban model.** Qwen2.5-Math-1.5B.
2. **Tek örnek seçimi.** Önce normal bir eğitim yapılıp her örneğin eğitim boyunca doğruluğu kaydedildi. Doğruluğu en çok dalgalanan (geçmiş varyansı en yüksek) örnek seçildi. Fikir: model bu soruyu bazen çözüp bazen çözemiyor, yani öğrenme sinyali en çok burada.
3. **Algoritma.** GRPO; [PPO](00_terimler.md#ppo) (proximal policy optimization: ayrı bir value model ile advantage hesaplayan klasik RL yöntemi) da denendi.
4. **Entropy loss.** Uygun bir katsayıyla entropy loss eklendi (modeli çeşitli cevaplar üretmeye teşvik eden terim).
5. **Uzun eğitim.** Aynı tek örnek üzerinde binlerce adım eğitim yapıldı.

**Sonuç:** Yazarların raporuna göre:
- MATH500 %36.0'dan %73.6'ya çıktı; altı math benchmark ortalaması %17.6'dan %35.7'ye.
- Karşılaştırma: 1.2K örneklik DeepScaleR alt kümesiyle eğitim %73.6 / %35.9. Yani tek örnek, 1.200 örnekle neredeyse aynı.
- 2 örnekle %74.8 / %36.6.
- "Post-saturation generalization": modelin o tek örnekteki eğitim doğruluğu hızla %100'e yaklaşıp doysa da test doğruluğu artmaya devam ediyor. Tek örneğe aşırı uyum ancak ~1.4K adımdan sonra başlıyor.
- Kazancın çoğu policy gradient loss'tan geliyor; entropy loss MATH500'e ~4 puan ekliyor.
- Llama-3.2-3B-Instruct'ta ve DeepSeek-R1-Distill-1.5B'de kazanç çok daha küçük.

**Bizim için:** RL'in az veriyle de çalışabildiğini gösterir, ama kazancın çoğu Qwen-Math'e özgü olabilir. Bizde az sayıda iyi seçilmiş (küçük modelin bazen çözdüğü) soruyla başlamak makul.

---

## Does Reinforcement Learning Really Incentivize Reasoning Capacity Beyond the Base Model? (Tsinghua LeapLab, Gao Huang grubu, Nisan 2025) — [2504.13837](https://arxiv.org/abs/2504.13837)
**Tek cümlede:** RLVR'ın modele yeni akıl yürütme yeteneği mi kazandırdığını, yoksa tabanın zaten bildiğini mi öne çıkardığını büyük k'lı pass@k ile ölçtüler (NeurIPS 2025 oral).

**Problem:** RLVR'dan sonra pass@1 artınca, modelin "yeni bir şey öğrendiği" varsayılır. Ama bu artış başka bir şeyden de gelebilir: taban model doğru cevabı zaten 100 denemenin birinde buluyordur, RL yalnızca o doğru yolu daha sık seçtiriyordur. İkisini ayırt etmek, RL'den ne beklenebileceğini belirler.

**Ne yaptılar:**
1. **Büyük k'lı [pass@k](00_terimler.md#pass-rate-ve-passk).** Pass@k: modele k deneme hakkı verilir; en az biri doğruysa soru çözülmüş sayılır. Küçük k (ör. 1) "ilk denemede ne kadar iyi" sorusunu, büyük k (ör. 256) "denemeye devam ederse ulaşabileceği sınır ne" sorusunu ölçer. Örnek: taban model bir soruyu 256 denemenin 3'ünde çözüyorsa pass@1'i düşük ama pass@256'sı 1'dir.
2. **Geniş kapsam.** Birçok model ailesi; math, kod ve görsel akıl yürütme; altı popüler RLVR algoritması.
3. **Ek analizler.** Coverage (modelin en az bir kez çözebildiği soruların oranı) ve perplexity (RL modelinin cevaplarının taban model için ne kadar "beklenmedik" olduğu) analizi.
4. **Distillation ile karşılaştırma.** Aynı tabandan büyük modelden distillation ile eğitilen modellerle karşılaştırma.

**Sonuç:** Yazarların raporuna göre:
- RLVR'lı modeller küçük k'da (pass@1) tabanı geçiyor. Ama büyük k'da taban model daha yüksek pass@k'ya ulaşıyor. Yani RLVR'ın çözdüğü sorular, tabanın zaten çözebildiği sorular; RL kapsamı genişletmiyor, hatta biraz daraltıyor.
- Altı algoritma birbirine yakın sonuç veriyor ve hepsi tabanın potansiyelini kullanmaktan uzak.
- Distillation ise yeni akıl yürütme kalıpları getirip yeteneği gerçekten genişletebiliyor.

**Bizim için:** 0.8B'nin hiç çözemediği soruları RL tek başına açamaz; bunlar için büyük modelin trajectory'leriyle SFT ya da distillation gerekir. RL ise küçük modelin bazen çözdüğü soruları güvenilir hale getirir.

---

## DeepCoder (UC Berkeley Agentica, Together AI, Nisan 2025) — [model kartı](https://huggingface.co/agentica-org/DeepCoder-14B-Preview)
**Tek cümlede:** DeepSeek-R1-Distill-Qwen-14B'yi kod üzerinde RL ile eğitip o3-mini seviyesine yaklaştırdılar; veri, kod ve log'lar açık.

**Problem:** Kod için RL'de her soruda, cevabı otomatik kontrol edecek güvenilir test'ler gerekir. Ayrıca uzun düşünen modellerde cevaplar context sınırını aşıp yarıda kesilir. Yazarlar orta boy bir modelle güçlü bir açık kod modeli kurmayı hedefledi.

**Ne yaptılar:**
1. **Veri.** ~24K problem–test çifti: TACO-Verified, PrimeIntellect SYNTHETIC-1 ve LiveCodeBench v5'in Mayıs 2023–Temmuz 2024 arası soruları. Kodlama problemlerinin bir kısmında önceden (offline) zorluk filtresi uygulandı.
2. **Reward.** Kod, problemin test'lerini geçerse ödül alır (test geçme; ikili).
3. **GRPO+.** GRPO'ya yapılan değişiklikler: entropy loss yok, KL loss yok, clip high. Overlong filtering: context sınırında kesilen (truncated) cevapların loss'u maskelendi; uzun ama belki doğru giden bir cevap "yanlış" diye cezalanmadı.
4. **Kademeli context.** Context 16K'dan 32K'ya büyütüldü.

**Sonuç:** Yazarların raporuna göre, LiveCodeBench v5'in (yarışma kodlama soruları) Ağustos 2024–Şubat 2025 arası sorularında Pass@1 %60.6. Context'i 16K'dan 32K'ya çıkarmak skoru %54'ten %58'e taşıdı (+4 puan). Test soruları, eğitimde kullanılan LiveCodeBench sorularından daha yeni bir döneme ait.

**Kaynak notu:** Kaynak bir model kartı; ayrı bir makale yok. "o3-mini seviyesine yakın" yazarların ifadesi; o3-mini'nin rakamı bu dosyada yok.

**Bizim için:** Test geçme gibi ikili ve kesin bir reward (bizde: sonuç gold ile aynı mı) ile, uzunluğa takılan rollout'u cezalandırmak yerine maskelemek iyi bir varsayılan.

---

## Open-Reasoner-Zero (StepFun, Tsinghua, Mart 2025) — [2503.24290](https://arxiv.org/abs/2503.24290)
**Tek cümlede:** Taban model üzerinde doğrudan, büyük ölçekli ve sade bir RL reçetesi (R1-Zero tarzı); DeepSeek-R1-Zero-Qwen-32B'yi ~1/10 adımla yakaladıklarını bildirdiler.

**Problem:** DeepSeek-R1-Zero, SFT olmadan doğrudan taban model üzerinde RL ile akıl yürütme öğretilebileceğini gösterdi. Ama reçetenin ayrıntıları ve hangi parçaların gerekli olduğu açık değildi. Yazarlar, en sade haliyle hangi parçaların yettiğini görmek istedi.

**Ne yaptılar:**
1. **Taban modeller.** Qwen2.5 taban modelleri, 0.5B'den 32B'ye.
2. **Vanilla PPO.** Ek değişiklik yapılmamış PPO. Advantage GAE ile hesaplandı (generalized advantage estimation: bir value model'in tahminini kullanarak her token'ın advantage'ını hesaplama yöntemi). λ=1 ve γ=1 seçildi: her token'ın advantage'ı, sondaki reward'ın indirimsiz haliyle value model'in tahmini arasındaki farktır. Clip 0.2.
3. **Hiçbir düzenleme yok.** KL loss, KL cezası ve entropy bonusu yok.
4. **Sade reward.** İkili: cevap etiketinin içindeki cevap referansla tam eşleşirse 1. Format reward yok.
5. **Veri.** AIME (2023'e kadar), MATH, NuminaMath, Tulu3 MATH, OpenR1-Math-220k, AoPS ve sentetik genel akıl yürütme soruları. İspat soruları çıkarıldı. Pass rate'i aşırı uçta olan (hep ya da hiç çözülen) örnekler LLM ile süzüldü.
6. **Annealing aşaması (32B).** İlk 1.100 adımda 64 denemenin 4'ünden azını çözdüğü 13K zor soruyla 100 adım daha eğitildi.

**Sonuç:** Yazarların raporuna göre, ORZ-32B: AIME24 48.1, MATH500 92.2, GPQA Diamond 55.5. Ablation'lar:
- λ=1, λ=0.95'ten daha kararlı.
- KL'siz eğitim en iyisi.
- 57K'lık veriyle skor büyümeye devam ederken 7.5K'lık MATH erken plato yapıyor; yani veri çeşitliliği ve miktarı önemli.
- Yalnızca İngilizce veri daha kararlı.
- GRPO 7B'de ~240 adımda kararsızlaştı; PPO kararlı kaldı.

**Bizim için:** Format reward'a gerek yok. Ama bizim tool-call biçimimiz taban modelde hazır olmadığı için, R1-Zero tarzı doğrudan RL 0.8B'de pratik değil.

---

## Understanding R1-Zero-Like Training: A Critical Perspective (Sea AI Lab, NUS, SMU, Mart 2025) — [2503.20783](https://arxiv.org/abs/2503.20783)
**Tek cümlede:** R1-Zero tarzı eğitimin iki parçasını (taban model ve GRPO) eleştirel incelediler; GRPO'daki iki yanlılığı bulup düzelten Dr. GRPO'yu önerdiler.

**Problem:** R1-Zero tarzı eğitimde iki gözlem öne çıkıyordu: cevaplar eğitim boyunca uzuyor ve bir noktada model kendi hatasını fark ediyor ("aha moment"). Bunlar RL'in akıl yürütmeyi geliştirdiğinin kanıtı sayılıyordu. Yazarlar iki şeyi sordu: bu davranışlar taban modelde zaten var mı, ve cevapların uzaması gerçekten daha iyi düşünmeden mi geliyor, yoksa algoritmanın bir yan etkisi mi?

**Ne yaptılar:**
1. **Taban modelleri incelediler.** Qwen2.5 taban modellerini şablonsuz ve şablonlu (prompt biçimi) denediler; "aha moment"in taban modellerde olup olmadığına baktılar.
2. **GRPO'daki iki yanlılığı buldular.**
   - **Uzunluk yanlılığı.** GRPO her cevabın loss'unu o cevabın uzunluğuna böler. Yanlış bir cevapta (eksi advantage) bu, uzun cevabın token başına daha az ceza alması demek. Örnek: 100 token'lık yanlış cevapta her token cezanın 1/100'ünü, 1.000 token'lık yanlış cevapta 1/1.000'ini alır. Model "yanlışsam uzun yazayım" eğilimi kazanır; yanlış cevaplar uzar.
   - **Std yanlılığı.** GRPO advantage'ı, gruptaki reward'ların standart sapmasına (std) böler. Çok kolay ya da çok zor sorularda (ör. 8 cevabın 7'si doğru) std küçüktür, bölünce advantage büyür. Bu sorular, orta zorluktaki sorulardan (ör. 4/8 doğru) daha ağır basar. Yani sorular zorluklarına göre eşitsiz ağırlık alır.
3. **Dr. GRPO.** İki bölmeyi de kaldırdılar: loss cevap uzunluğuna, advantage std'ye bölünmez.
4. **Minimal reçete.** Qwen2.5-Math-7B, MATH'in 3-5. seviye (zor) soruları, Qwen-Math şablonu, Dr. GRPO; 8 A100 GPU'da ~27 saat.

**Sonuç:** Yazarların raporuna göre:
- Oat-Zero-7B, AIME 2024'te %43.3.
- Qwen2.5 taban modelleri şablonsuz da soruları cevaplıyor: şablonsuz ortalama 38.2, 4-shot (prompt'a 4 örnek eklenmiş) 23.8. Yani bu modeller soru-cevap biçimini zaten biliyor.
- "Aha moment" neredeyse bütün taban modellerde, RL'den önce de var.
- Dr. GRPO token verimliliğini artırıyor ve yanlış cevapların uzunluğunu düşürüyor. Yani yanlış cevapların uzamasının bir kısmı algoritmanın yan etkisi.
- Llama-3.2-3B'de math pretraining RL'in tavanını yükseltiyor.

**Bizim için:** GRPO uygularken uzunluk ve std normalizasyonunu kaldırmak (Dr. GRPO), küçük modelin boşuna uzun ve çok adımlı trajectory'lere kaymasını önleyebilir.

---

## SimpleRL-Zoo (HKUST ve diğerleri, Mart 2025) — [2503.18892](https://arxiv.org/abs/2503.18892)
**Tek cümlede:** Zero RL'i (SFT'siz, doğrudan taban model üzerinde RL) aynı basit reçeteyle 10 farklı taban modelde denediler.

**Problem:** Zero RL çalışmalarının çoğu Qwen2.5 üzerinde yapılmıştı. Bu yüzden bulguların genel mi yoksa Qwen'e özgü mü olduğu bilinmiyordu. Yazarlar Llama, Mistral, DeepSeek-Math ve 0.5B'den 32B'ye Qwen2.5 modellerini aynı reçeteyle eğitip karşılaştırdı.

**Ne yaptılar:**
1. **Basit veri.** Yalnızca GSM8K (ilkokul düzeyi sözel matematik problemleri) ve MATH (yarışma matematiği; 1-5 arası zorluk seviyeli).
2. **Zorluğa göre üç set, her biri 8K soru.** Kolay (GSM8K + MATH seviye 1), orta (MATH 1-4), zor (MATH 3-5).
3. **Modele uygun set.** Her model kendi yeteneğine uygun sette eğitildi: Qwen2.5-0.5B orta, büyük Qwen'ler zor, Llama ve Mistral kolay sette.
4. **Reward.** Kural tabanlı: doğruysa +1, değilse 0. Format reward yok.
5. **Algoritma.** Uzunluk normalizasyonu olmayan GRPO (verl kütüphanesiyle). Prompt batch 1.024, prompt başına 8 rollout, en fazla 8.192 token, temperature 1.0. KL katsayısı 1e-4 (14B'ye kadar olan modellerde).

**Sonuç:** Yazarların raporuna göre:
- Katı bir format reward (cevabı belirli bir biçimde yazmayı zorlamak) exploration'ı engelliyor ve zayıf modellerde çöküşe yol açıyor.
- Veri zorluğu modele uymalı: Mistral-7B zor veride bozuluyor; Qwen2.5-7B ise kolay veride daha kötü sonuç veriyor.
- Cevap uzunluğunun artması her zaman daha iyi akıl yürütme demek değil.
- Zero RL pass@k'yı ~10-30 puan artırıyor.
- SFT ile cold start, keşfi kısıtlayıp RL'in tavanını düşürebiliyor.

**Bizim için:** RL verisinin zorluğunu küçük modelin seviyesine göre seçmek şart: 0.8B için büyük modelin bile zor çözdüğü sorular değil, küçük modelin arada bir çözebildiği sorular.

---

## Light-R1 (Qiyuan Tech / Qihoo 360, Mart 2025) — [2503.10460](https://arxiv.org/abs/2503.10460)
**Tek cümlede:** Uzun düşünen bir math modeli için açık bir reçete: iki aşamalı curriculum SFT, DPO, model merge, sonra GRPO.

**Problem:** DeepSeek-R1 gibi uzun düşünen modelleri sıfırdan, düşünmeyen bir modelden (Qwen2.5-32B-Instruct) eğitmek pahalı ve ayrıntıları açık değildi. Yazarlar, az sayıda ama doğru seçilmiş soruyla ve aşamalarla bunun ucuzca yapılabileceğini göstermek istedi.

**Ne yaptılar:**
1. **Soru havuzu.** ~1M math sorusundan başladılar.
2. **Stage 1 verisi.** DeepScaleR-1.5B-Preview'ın pass rate'ine göre süzülmüş ~76K soru.
3. **Stage 2 verisi.** DeepSeek-R1'in düşük ve karışık başarı gösterdiği ~3K daha zor soru.
4. **Cevaplar.** DeepSeek-R1 üretti; yalnızca doğru cevaplar tutuldu.
5. **Decontamination.** Rakamları yok sayan tam eşleşme (yalnızca sayıları değiştirilmiş kopyaları da yakalamak için) ve 32-gram (32 kelimelik ortak parça) eşleşmesi. MATH-500'de onlarca kirli soru bulundu.
6. **Light-R1-32B eğitimi.** Taban Qwen2.5-32B-Instruct. SFT-1 (LR 5e-5), sonra SFT-2 (LR 1e-5). Sonra DPO; loss olarak NCA (DPO ailesinden bir preference loss'u) kullanıldı. Rejected: Stage-2 modelinin kendi cevabı; chosen: DeepSeek-R1'in cevabı. Sonra TIES-merging: birden çok modelin ağırlık değişikliklerini birleştiren, çakışan küçük değişiklikleri ayıklayan bir merge yöntemi.
7. **RL.** Ayrı olarak DeepSeek-R1-Distill-Qwen-14B üzerinde GRPO. Yalnızca pass rate'i 0.25 ile 0.625 arasındaki prompt'lar kullanıldı (ör. 8 denemede 2 ile 5 arası doğru; orta zorluk). ~220 adım.

**Sonuç:** Yazarların raporuna göre:
- Light-R1-32B: AIME24 / AIME25 = 76.6 / 64.6. Taban Qwen2.5-32B-Instruct 16.6 / 13.6'ydı; yani düşünmeyen bir modelden uzun düşünen bir modele geçişle ~50-60 puanlık artış.
- Light-R1-14B-DS: SFT sonrası 72.3 / 58.9, GRPO sonrası 74.0 / 60.2 (+1.7 / +1.3). Zaten güçlü bir modelde RL küçük ama net kazanç getirdi.
- Light-R1-7B-DS: 59.1 / 44.3.

**Bizim için:** Önce geniş ve kolay, sonra küçük ve zor bir SFT aşaması; RL'de "orta zorluk" (pass rate 0.25-0.625) bandı küçük bütçeli bir pipeline için somut eşikler veriyor.

---

## LIMO: Less is More for Reasoning (SJTU GAIR, Şubat 2025) — [2502.03387](https://arxiv.org/abs/2502.03387)
**Tek cümlede:** Çok az ama çok iyi seçilmiş örnekle (800) SFT'nin, 100 kat büyük veri setlerinden daha iyi akıl yürütme verdiğini gösterdiler.

**Problem:** Akıl yürütme öğretmek için yüz binlerce örnek gerektiği düşünülüyordu. Yazarların hipotezi: güçlü bir taban model math bilgisini pretraining'de zaten öğrenmiştir; SFT'nin yalnızca bu bilgiyi nasıl kullanacağını göstermesi gerekir. Bunun için az ama çok kaliteli örnek yeterli olabilir.

**Ne yaptılar:**
1. **Aday havuzu.** On milyonlarca adaydan 2.125 soruluk bir havuz kuruldu.
2. **Kolay soruları atma.** Qwen2.5-Math-7B-Instruct'ın 4 denemede çözdüğü sorular atıldı.
3. **Çok zor soruları seçme.** DeepSeek-R1-Distill-Qwen-32B'nin 32 denemede yalnızca 1-3 kez çözdüğü sorular tutuldu. Yani güçlü bir modelin bile zor çözdüğü sorular.
4. **Decontamination.** n-gram (ardışık kelime dizisi) eşleşmesiyle test sorularına benzeyenler çıkarıldı.
5. **Çözüm zinciri seçimi.** Çözümler DeepSeek R1, R1-Distill-32B ve QwQ-32B'den geldi. Her çözüm kural tabanlı puanlandı: uzunluk %30, doğrulama kelimeleri ("kontrol edelim" gibi) %20, deneme kelimeleri ("belki", "deneyelim" gibi) %25, bağlaçlar %25. En iyi 800 soru–çözüm seçildi.
6. **SFT.** Qwen2.5-32B-Instruct, full SFT, LR 5e-6, 15 epoch, batch 64.

**Sonuç:** Yazarların raporuna göre:
- AIME24 %63.3, MATH500 %95.6; ortalama %78.1.
- Karşılaştırma: aynı tabanı 100K örneklik NuminaMath ile eğitmek %32.3, 114K örneklik OpenThoughts ile %58.3 veriyor. Yani 800 örnek, 100 kat fazla veriyi 20 puan geçiyor.
- Ablation: zor sorular ve kaliteli zincirler daha iyi. 400 örnek bile AIME24'te %57.5 veriyor. 800'den sonra getiri azalıyor.
- Taban model çok önemli: aynı veriyle Qwen1.5-32B yalnızca %9.2. 3B modelde AIME24 yalnızca %2.5.

**Bizim için:** Az ama iyi seçilmiş SFT'nin işe yaraması tabanın bilgisine bağlı ve küçük modelde (3B) zayıf. 0.8B için "az örnek" yeterli olmayabilir, ama zor ve temiz trajectory seçme kriterleri aynen kullanılabilir.

---

## DeepScaleR (UC Berkeley Agentica / Sky Lab, Şubat 2025) — [model kartı](https://huggingface.co/agentica-org/DeepScaleR-1.5B-Preview)
**Tek cümlede:** 1.5B'lik bir distill modelini RL ile, AIME'de o1-preview'ı geçecek seviyeye taşıdılar.

**Problem:** RL'in büyük modellerde işe yaradığı biliniyordu, ama çok küçük modellerde (1.5B) ne kadar kazanç getirebileceği belli değildi. Uzun düşünen modellerde RL çok pahalıdır, çünkü her rollout binlerce token sürer. Yazarlar, compute'u context uzunluğunu aşama aşama artırarak düşürmeyi denedi.

**Ne yaptılar:**
1. **Taban.** DeepSeek-R1-Distill-Qwen-1.5B (DeepSeek-R1'in cevaplarıyla SFT'lenmiş küçük model).
2. **Veri.** ~40K tekil problem–cevap çifti: AIME 1984-2023, 2023 öncesi AMC, Omni-MATH (olimpiyat düzeyi sorular) ve Still.
3. **Reward.** Cevap LaTeX/Sympy kontrolünden (matematiksel ifadeleri karşılaştıran araçlar) geçip doğruysa 1; yanlışsa ya da biçim bozuksa 0. PRM ya da ara adım sinyali yok.
4. **Algoritma.** GRPO, KL regularization ile (modeli başlangıca yakın tutan ceza açık).
5. **Kademeli context.** 8K (0-1.040. adımlar, 8 A100) → 16K (1.040-1.520, 32 A100) → 24K (1.520. adımdan sonra, 32 A100). Kısa context'te başlamak, ilk adımları ucuz yapar.

**Sonuç:** Yazarların raporuna göre, AIME 2024'te Pass@1 %43.1. Karşılaştırma için: aşağıdaki Sky-T1 bölümündeki rakama göre o1-preview AIME 2024'te 40.0 alıyor. JustRL'in karşılaştırmasında DeepScaleR'ın toplam token bütçesi ~2.2×10^8 (1.750 adım, batch 128, soru başına 8 rollout).

**Kaynak notu:** Kaynak bir model kartı; ayrı bir makale yok. Taban modelin AIME rakamı bu dosyada yok.

**Bizim için:** Küçük model RL'inde önce kısa trajectory/context bütçesiyle başlayıp sonra büyütmek Mac'te belleği ve süreyi düşürür. Bizim tool-call budget'ımız için de aynı kademeli artış denenebilir.

---

## s1: Simple test-time scaling (Stanford, UW, AI2 ve diğerleri, Ocak 2025) — [2501.19393](https://arxiv.org/abs/2501.19393)
**Tek cümlede:** 1.000 iyi seçilmiş örnekle SFT ve "budget forcing" (düşünme süresini zorla kısaltmak ya da uzatmak) ile güçlü bir akıl yürütme modeli kurdular.

**Problem:** o1 gibi modeller cevap anında daha uzun düşünerek daha iyi sonuç veriyordu (test-time scaling). Bunun en basit nasıl tekrar üretilebileceği bilinmiyordu. Yazarlar iki soruyu sordu: en az kaç örnekle bir model uzun düşünmeyi öğrenir, ve düşünme süresi basit bir yöntemle kontrol edilebilir mi?

**Ne yaptılar:**
1. **Başlangıç havuzu.** 16 kaynaktan 59.029 soru. Düşünme metinleri (trace) Gemini Flash Thinking'den alındı.
2. **Kalite filtresi.** API hatası olan ve biçimi bozuk sorular atıldı; 51.581 kaldı.
3. **Zorluk filtresi.** Qwen2.5-7B-Instruct ya da 32B-Instruct'ın çözebildiği sorular atıldı; 24.496 kaldı. Uzun trace de zorluk işareti sayıldı.
4. **Çeşitlilik.** Sorular AMS konu sınıflarına (Amerikan Matematik Derneği'nin konu sınıflandırması) ayrıldı. Önce rastgele bir alan seçildi, sonra o alandan uzun trace'li bir soru. Böylece ~50 alana yayılmış 1.000 örnek (s1K) çıktı.
5. **Decontamination.** 8-gram eşleşmesi.
6. **SFT.** Qwen2.5-32B-Instruct, 5 epoch, batch 16, LR 1e-5; 16 H100 GPU'da ~26 dakika.
7. **Budget forcing.** Cevap anında düşünme süresini kontrol etme. Kısaltmak için: model belli bir token sayısına ulaşınca düşünme zorla bitirilir ve cevap istenir. Uzatmak için: model düşünmeyi bitirmek istediğinde bitiş işareti silinir ve metne "Wait" eklenir; model düşünmeye devam eder ve bazen kendi hatasını düzeltir.

**Sonuç:** Yazarların raporuna göre:
- Budget forcing ile AIME24 %50'den %57'ye çıktı; yalnızca cevap anında daha uzun düşündürerek +7 puan.
- Ablation (AIME24): s1K 50.0. Rastgele seçilmiş 1K örnek 36.7. Yalnızca çeşitliliğe göre seçilmiş 1K 26.7. Yalnızca en uzun trace'li 1K 33.3. 59K'nın tamamı 53.3.
- Yani 59 kat fazla veri yalnızca 3.3 puan fazla getirdi, ama 394 GPU saatine karşı 7 GPU saati harcandı. Kalite, zorluk ve çeşitliliği birlikte kullanmak en verimlisi; tek başına hiçbiri yetmiyor.

**Bizim için:** SFT verisini seçerken üç kriter birlikte kullanılmalı: küçük modelin çözemediği (zorluk), farklı veritabanlarına yayılmış (çeşitlilik) ve hatasız çalışan (kalite) trajectory'ler.

---

## Sky-T1-32B-Preview (UC Berkeley NovaSky / Sky Computing Lab, Ocak 2025) — [blog](https://novasky-ai.github.io/posts/sky-t1/)
**Tek cümlede:** 450 dolardan az maliyetle o1-preview seviyesine yakın bir akıl yürütme modeli eğittiler; veri ve kod açık.

**Problem:** o1-preview gibi akıl yürütme modelleri kapalıydı ve eğitimlerinin çok pahalı olduğu düşünülüyordu. Yazarlar, açık bir modelin ve az bir bütçenin yetip yetmeyeceğini göstermek istedi.

**Ne yaptılar:**
1. **Veri.** 17K örnek: 5K kod (APPs, TACO), 10K math (NuminaMATH'in AIME, MATH ve Olympiads alt kümeleri), 1K bilim ve bulmaca (STILL-2).
2. **Cevap üretimi.** Cevapları QwQ-32B-Preview üretti.
3. **Rejection sampling.** Veri setindeki çözüme göre yanlış olan cevaplar atıldı; yalnızca doğrular kaldı.
4. **Biçim temizliği.** Trace'ler GPT-4o-mini ile düzgün ve tek tip bir biçime yeniden yazıldı.
5. **SFT.** Qwen2.5-32B-Instruct, 8 H100 GPU'da 19 saat.

**Sonuç:** Yazarların raporuna göre:
- AIME2024: 43.3. Taban 16.7, o1-preview 40.0. Yani taban 26.6 puan geçildi ve o1-preview'ın biraz üstüne çıkıldı.
- MATH500: 82.4. Taban 76.2 (+6.2).

**Kaynak notu:** Kaynak bir blog yazısı; hakemli bir makale değil.

**Bizim için:** Büyük modelin trajectory'lerini yalnızca doğru olanlarla tutmak (rejection sampling) ve tool-call biçimini tek tipe sokmak, SFT verisinin ilk ve en ucuz temizliği.

---

## OLMo 2 Instruct (AI2, Aralık 2024) — [2501.00656](https://arxiv.org/abs/2501.00656)
**Tek cümlede:** Tülu 3 reçetesini (SFT → DPO → RLVR) tamamen açık OLMo 2 modellerine uyguladılar ve RLVR aşamasını genişlettiler.

**Problem:** Tülu 3 reçetesi Llama 3.1 üzerinde geliştirilmişti; Llama'nın pretraining verisi açık değil. AI2, aynı reçeteyi pretraining'i de tamamen açık olan kendi modellerine uygulayarak bütün zinciri açık hale getirmek istedi. Ayrıca reçetenin farklı boyutlarda (1B'den 32B'ye) nasıl davrandığı görülmek istendi.

**Ne yaptılar:**
1. **SFT.** 939K prompt'luk Tülu 3 karışımı (7B ve 13B için; 1B ve 32B için 866K).
2. **DPO.** Cevaplar iki kaynaktan geldi: geliştirme sırasındaki SFT checkpoint'lerinden on-policy (modelin kendi) cevaplar ve 20 modelden oluşan bir havuz. Cevaplar GPT-4o ile puanlanıp chosen ve rejected olarak ikiye ayrıldı. 7B için 366.7K, 13B için 377.7K prompt.
3. **RLVR.** 7B ve 13B'de PPO; value model (bir noktadan sonra beklenen reward'ı tahmin eden yardımcı model) bir reward model'den başlatıldı. 1B ve 32B'de GRPO (32B: LR 5e-7, KL katsayısı 0.1, prompt başına 16 örnek).
4. **13B'de art arda üç RLVR.** Önce GSM8K + MATH + kısıtlı talimat prompt'ları, sonra yalnızca GSM8K, sonra yalnızca MATH. Her aşama zayıf kalan bir alanı hedefledi.

**Sonuç:** Yazarların raporuna göre, GSM8K (ilkokul düzeyi sözel matematik) / MATH (yarışma matematiği), SFT → DPO → RLVR sırasıyla:
- 7B: 74.6 / 25.3 → 82.6 / 30.3 → 85.1 / 32.5
- 13B: 76.3 / 29.5 → 82.3 / 35.2 → 87.4 / 39.2
- 32B: 78.4 / 35.9 → 85.7 / 46.8 → 87.6 / 49.7
Kazancın büyük kısmı DPO'dan geliyor (ör. 7B'de GSM8K +8.0). RLVR hedef benchmark'lara üstüne ekliyor (7B'de GSM8K +2.5). Üç aşamalı RLVR'ın uygulandığı 13B'de RLVR kazancı daha büyük (GSM8K +5.1, MATH +4.0).

**Bizim için:** Zayıf kalan bir alana (ör. bir veritabanı) yönelik ayrı, kısa bir RLVR aşaması eklemek o alanı düzeltebilir.

---

## Tülu 3 (AI2, Kasım 2024) — [2411.15124](https://arxiv.org/abs/2411.15124)
**Tek cümlede:** Açık bir post-training reçetesi: SFT → DPO → RLVR; "RLVR" (Reinforcement Learning with Verifiable Rewards) terimi ve yöntemi bu çalışmayla ortaya çıktı.

**Problem:** Kapalı modellerin post-training reçeteleri gizliydi; açık reçeteler ise onların çok gerisindeydi. Ayrıca RL genelde öğrenilmiş bir reward model ile yapılıyordu; böyle bir modelin puanı gürültülü olabilir. Tülu 3, cevabı otomatik ve kesin kontrol edilebilen işlerde (math, talimat kısıtları) doğrudan bu kontrolü reward olarak kullanmayı önerdi.

**Ne yaptılar:**
1. **SFT.** ~23.3M küratörlü prompt'tan seçilmiş 939.344 prompt.
2. **DPO.** SFT modelinin ve başka modellerin cevaplarıyla on-policy üretilmiş 354.192 preference örneği.
3. **Decontamination.** 8-gram eşleşmesine bakıldı. Bir eval setinin %2'sinden fazlasıyla çakışan eğitim seti ya tamamen atıldı ya da yalnızca çakışan örnekler çıkarıldı.
4. **RLVR.** Algoritma PPO. Reward: cevap doğrulanabilir biçimde doğruysa 10, yanlışsa 0; EOS (cevabın bittiğini gösteren özel token) ile bitmeyen cevaba −10. Veri 29.946 prompt: GSM8K 7.473, MATH 7.500, IFEval kısıtları 14.973 (ör. "cevabı tamamen küçük harfle yaz" gibi kontrol edilebilir kurallar). LR 3e-7, KL β 0.05 (8B için; β, modeli başlangıca yakın tutan cezanın gücü), temperature 1.0.

**Sonuç:** Yazarların raporuna göre, 8B'de DPO'dan RLVR'a geçiş:
- GSM8K 84.3 → 87.6 (+3.3)
- MATH 42.0 → 43.7 (+1.7)
- IFEval 81.1 → 82.4 (+1.3)
Kazançlar küçük ama yalnızca hedeflenen, doğrulanabilir becerilerde. Diğer bulgular:
- Value model'i genel bir reward model'den başlatmak en iyisi.
- Yalnızca doğrulanabilir reward kullanmak, üstüne reward model puanı eklemekten iyi; ek puan gürültü getiriyor.
- RL'e DPO'dan başlamak SFT'den başlamaktan iyi.
- KL çok düşükse (β küçük) over-optimization oluyor ve skor düşüyor.

**Bizim için:** Execution sonucunun doğruluğu bizim için kesin bir verifiable reward. Tülu 3'ün dersi: bunun yanına öğrenilmiş bir reward eklemek gürültü getirir, ve RL'den önce bir preference (DPO) aşaması faydalıdır.
