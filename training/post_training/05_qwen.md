# Qwen (Alibaba)

**Bu bölümde ne var:** Qwen ekibinin ve Alibaba'nın Kasım 2024 – Kasım 2026 arasında yayımladığı post-training reçeteleri. Post-training, önceden eğitilmiş (pretrained) bir modeli kullanışlı bir asistana ya da agent'a çeviren eğitim aşamalarının toplamıdır. Her girdi arXiv sayfasından, resmi blog'dan ya da resmi model kartından okundu; rakamlar yazarların bildirdiği gibidir ve bulunamayan rakam yazılmadı.

**Kapsam notu:**
- Tongyi Lab'ın (Alibaba'nın bir araştırma birimi) QwenLong çalışmaları dahil; agentic web agent'ları (internette arama yapıp gezinen agent'lar) hariç.
- Qwen2.5-Math ve Qwen2.5-Coder (Eylül 2024) zaman penceresinin dışında kaldığı için alınmadı.
- Qwen3.5 ve Qwen3.6 için ayrı bir technical report bulunamadı.
- Çok uzmanlı ve çok kaynaklı reçeteler ayrı bir başlık olarak değil, ilgili girdilerin içinde anlatılıyor. [RL](00_terimler.md#rl-ve-rlvr), reinforcement learning, modelin kendi denemelerine verilen puanla öğrenmesidir. [Distillation](00_terimler.md#distillation), küçük modelin büyük modelin cevaplarını ya da olasılıklarını taklit ederek öğrenmesidir. Bu reçeteler üç türlü: alan uzmanlarını ayrı RL ile eğitip tek modele distill etmek (Qwen3-Coder-Next, Qwen3.5-Omni), [model merging](00_terimler.md#model-merging) yani birden çok modelin ağırlıklarını birleştirmek (QwenLong-L1.5'te SCE adlı bir merging yöntemi, Qwen3-Embedding'de slerp merging) ve birden çok büyük modelden distillation (Qwen3 ve Qwen3-VL'de strong-to-weak distillation).
- "MOPD: Multi-Teacher On-Policy Distillation" (2606.30406) Qwen3-30B-A3B üzerinde deneniyor, ama MiMo/Xiaomi ekibinin çalışması olduğu için alınmadı ([MOPD](00_terimler.md#multi-teacher-distillation-mopd): birden çok büyük modelden aynı anda on-policy distillation).
- Qwen ekibine ait bir [self-play](00_terimler.md#self-play) çalışması (modelin kendine karşı oynayarak ya da kendine soru üreterek öğrenmesi) bulunamadı.

**Bu bölümün ana dersleri:**
- Qwen3 ve Qwen3-VL'de küçük modeller RL ile değil, büyük modelden distillation ile eğitiliyor (Qwen3.5'in küçük modelleri için bu yazılmamış).
- Qwen3 raporunda 8B modelde [on-policy distillation](00_terimler.md#on-policy-distillation-opd) (küçük model kendi cevabını üretir, büyük model bu cevabı token token puanlar) RL'den hem daha iyi sonuç verdi hem yaklaşık 10 kat daha ucuzdu.
- RL için az ama iyi seçilmiş soru yetiyor; modelin her denemede doğru ya da her denemede yanlış yaptığı sorular atılıyor, çünkü bunlardan öğrenilecek bir şey yok.
- Tek bir "doğru/yanlış" [reward](00_terimler.md#reward)'ı (modelin aldığı puan) model için kolay bir kaçış yolu açabiliyor (Qwen3Guard'da her şeyi reddetmek). Bunu önlemek için ayrı ceza terimleri ekleniyor.
- RL'i kararlı tutmak büyük ekiplerin de ana sorunu. Qwen bunun için GSPO ve SAPO adlı iki algoritma ve bir dizi pratik kural yayımladı.

**Makaleler:**
- Contrastive On-Policy Distillation — küçük modele kısa ve doğru düşünmeyi öğreten distillation.
- Qwen3.5-Omni — metin, görüntü, ses ve video modeli; uzmanları tek modele distill etme.
- Qwen3-Coder-Next — çalıştırılabilir coding ortamlarıyla eğitilen coding agent'ı.
- Qwen3.5 — bizim small model'imizin ailesi; yalnızca blog ve model kartı var.
- Qwen3-Max-Thinking — tool kullanan çok büyük reasoning modeli; yalnızca blog.
- QwenLong-L1.5 — uzun dokümanlarda reasoning için veri sentezi ve dengeli RL.
- Stabilizing RL with LLMs — token düzeyinde RL'in ne zaman doğru çalıştığının teorisi ve pratiği.
- Qwen3-VL — görüntü-metin modeli ailesi; büyükten küçüğe distillation ve iki tür RL.
- SAPO — aşırı değişen token'ları kesmek yerine yumuşakça kısan RL algoritması.
- Qwen3Guard — güvenlik sınıflandırıcısı ve onu reward olarak kullanan güvenlik RL'i.
- Qwen3-Omni — sesi metin ve görüntü kalitesini bozmadan ekleme denemesi.
- GSPO — güncelleme sınırını token token değil, bütün cevap için hesaplayan RL algoritması.
- Qwen3-Coder — kod RL'i ve uzun agent RL'i; yalnızca blog.
- Qwen3-2507 — thinking ve non-thinking modellerini ayrı eğitme kararı.
- Qwen3 Embedding — embedding modelleri; sentetik veri ve model merging'in etkisi.
- Beyond the 80/20 Rule — RL'de asıl işi yapan az sayıdaki "kararsız" token'lar.
- QwenLong-L1 — kısa bağlamda öğrenilen reasoning'i uzun dokümanlara taşıyan aşamalı RL.
- WorldPM — insan tercihi modellemesinin ölçeklenmesi.
- Qwen3 — büyük modeller için dört aşamalı reçete, küçük modeller için distillation.
- QwQ-32B — iki aşamalı RL ile güçlü 32B reasoning modeli; yalnızca blog.
- START — modele örnek göstermeden Python tool'u kullanmayı öğretmek.
- Lessons of Developing PRMs — adım adım puanlayan reward model'lerinin verisi nasıl üretilmeli.
- Qwen2.5 — 0.5B–72B ailesinin post-training reçetesi.
- Marco-o1 — ağaç aramasıyla üretilmiş reasoning verisiyle fine-tuning.

---

## Contrastive On-Policy Distillation (SJTU + Alibaba Group / Qwen ekibi stajı, Temmuz 2026) — [2607.19046](https://arxiv.org/abs/2607.19046)
**Tek cümlede:** Büyük model aynı cevabı "az düşün" ve "çok düşün" talimatlarıyla iki kez puanlar; iki puanın farkı küçük modele hem doğru hem kısa düşünmeyi öğretir. Yöntemin adı COPD (Contrastive On-Policy Distillation).

**Problem:** Uzun düşünen ([long CoT](00_terimler.md#cot-ve-long-cot): cevaptan önce uzun bir adım adım düşünme metni) modeller çoğu zaman gereğinden uzun yazar. Bu, her soruda daha çok token, daha çok süre ve daha çok maliyet demektir. Klasik on-policy distillation (OPD) küçük modele büyük modeli taklit ettirir; büyük model uzun düşünüyorsa küçük model de uzun düşünmeyi öğrenir. Kısalık için ayrıca bir uzunluk cezası koymak ise yeni bir ayar ve denge sorunu getirir.

**Ne yaptılar:**
1. **Veri seçimi.** Görsel reasoning soru seti ViRL-39K'dan yaklaşık 16K örnek aldılar. Yalnızca [pass rate](00_terimler.md#pass-rate-ve-passk)'i (modelin bir soruyu kaç denemede doğru yaptığının oranı) kesin olarak 0 ile 1 arasında kalan sorular tutuldu. Hepsi doğru ya da hepsi yanlış olan sorular atıldı, çünkü bunlarda model için öğrenilecek bir fark yok.
2. **[Rollout](00_terimler.md#rollout).** Eğitilen küçük model her soruya kendi cevabını üretir (rollout: modelin eğitim sırasında ürettiği bir deneme cevabı).
3. **İki talimatla puanlama.** Büyük model, cevabın her token'ına kadar olan kısmını (prefix) iki farklı talimat altında okur: LT ("low thinking", az düşün) ve HT ("high thinking", çok düşün). Her token'ın puanı, büyük modelin bu token'a "az düşün" talimatıyla verdiği log-olasılık eksi "çok düşün" talimatıyla verdiği log-olasılıktır. Örnek: "Cevap 12." gibi doğrudan sonuca giden bir token "az düşün" altında daha olasıdır, puanı pozitif çıkar. "Bir kez daha kontrol edeyim" gibi bir token "çok düşün" altında daha olasıdır, puanı negatif çıkar. Puan −10 ile 10 arasına kırpılır.
4. **Güncelleme.** Bu token puanı [advantage](00_terimler.md#advantage) (bir token'ın ortalamadan ne kadar iyi olduğunu söyleyen sayı) olarak [PPO](00_terimler.md#ppo) tarzı bir clipped objective'de kullanılır (PPO, Proximal Policy Optimization: her adımda modelin fazla değişmesini bir sınırla engelleyen RL yöntemi). Doğruluk için ayrı bir reward ya da uzunluk cezası yoktur; kısalık doğrudan iki talimatın farkından gelir.
5. **Modeller.** Küçük modeller Qwen3-VL-2B-Instruct ve Qwen3.5-2B. Büyük modeller Qwen3-VL-8B/32B ve Qwen3.5-4B/9B/35B-A3B/122B-A10B ("35B-A3B": toplam 35B parametre, her token'da yalnızca 3B'si çalışan bir [MoE](00_terimler.md#moe) modeli; MoE, Mixture of Experts, her token için uzman alt ağlardan birkaçını seçen mimari).
6. **Ayarlar.** Batch 192, PPO mini-batch 48, prompt en fazla 4096 ve cevap en fazla 8192 token, learning rate 1e-6, weight decay 1e-2, 3 epoch.
7. **Self-distillation varyantı (COPSD).** Büyük model yerine eğitilen modelin dondurulmuş bir kopyası da puanlayıcı olabilir. Böylece ayrı bir büyük modele hiç gerek kalmaz.

**Sonuç:** Yazarların raporuna göre doğruluk 9 çok modlu [benchmark](00_terimler.md#benchmarklar)'ın (modelleri karşılaştırmak için kullanılan standart test seti) ortalaması: dördü reasoning (MathVista, MathVerse, WeMath, LogicVista: görsel matematik ve mantık soruları), beşi görüntü anlama (HalluBench, MMMU, MMStar, RWQA, MMGist). Benchmark adları makaleden okundu.
- Qwen3-VL-8B'den 2B'ye (ortalama doğruluk / ortalama cevap uzunluğu): eğitilmemiş base model 52.9 / 2.10K token, klasik OPD 53.6 / 2.24K, ExOPD 55.2 / 2.07K, COPD 57.3 / 0.89K. ExOPD makalede bir karşılaştırma yöntemi: OPD'yi RL gibi ele alıp büyük modeli geçmeye çalışan bir varyant. COPD base'e göre 4.4 puan daha doğru ve cevapları yaklaşık %58 daha kısa. Klasik OPD ise cevabı uzatıyor.
- Qwen3.5-4B'den 2B'ye: COPD 60.1 / 1.92K, ExOPD 57.6 / 3.66K. COPD 2.5 puan önde ve yaklaşık yarı uzunlukta yazıyor.
- Maliyet: COPD eğitimi 60 GPU saati; OPD 132, ExOPD 150. Yani yarıdan daha ucuz.
- Ablation: yalnızca LT puanını kullanmak (iki talimatın farkı yerine) cevabı uzatıyor (53.1 / 2.26K). Kontrast, yani fark, şart.
- Daha büyük model (122B-A10B) yalnızca +0.8 puan getiriyor ama cevap %24.1 uzuyor. Büyük modelin boyu büyüdükçe kazanç azalıyor.
- COPSD (makaleden okundu): Qwen3-VL-2B'de ortalama doğruluk 52.9'dan 56.7'ye çıkıyor, cevap uzunluğu 0.76K token'a iniyor.
- [SFT](00_terimler.md#sft) (doğru cevap örnekleriyle düz eğitim) ya da [GRPO](00_terimler.md#grpo) (her soruya birkaç cevap üretip her cevabı grubun ortalamasıyla karşılaştıran RL yöntemi) ile karşılaştırma raporlanmamış.

**Kaynak notu:** Makale COPSD satırında base uzunluğunu 2.12K veriyor; yukarıdaki tabloda 2.10K. Fark küçük ama iki ölçüm birebir aynı değil.

**Bizim için:** 9B'yi büyük model olarak kullanıp 0.8B'ye OPD yapmak RL'den ucuz bir yol. Pass rate'i 0 ile 1 arasında kalan sorularla sınırlamak ve kısa cevabı ödüllendirmek tool call budget'ımıza uyuyor.

## Qwen3.5-Omni Technical Report (Qwen Team, Nisan 2026) — [2604.15804](https://arxiv.org/abs/2604.15804)
**Tek cümlede:** Qwen3.5 tabanlı metin-görüntü-ses-video modeli; post-training'i "önce ayrı uzmanlar, sonra tek modele distillation" düzeninde.

**Problem:** Omni-modal (her türlü girdiyi alan) bir model, her alanda o alana özel eğitilmiş bir model kadar iyi olmalı. Ayrıca aynı soru sesle sorulduğunda, yazıyla sorulduğu kadar iyi cevaplanmalı. Kullanıcıyla uzun konuşmalarda da dil karışması ya da karakter (persona) kayması gibi sorunlar çıkmamalı. Bu raporun metin tarafı, Qwen3.5 ailesinin genel reçetesini yansıtıyor.

**Ne yaptılar:** Model iki parçadan oluşur: Thinker (girdiyi anlayıp metin cevabı üreten parça) ve Talker (cevabı sese çeviren parça).
1. **Specialist Distillation.** Qwen3.5 base modelinden ayrı ayrı uzman modeller eğitildi: agentic, coding, temel reasoning, görüntü ve ses. Her uzman kendi alanında SFT (supervised fine-tuning) ve RL ile eğitildi. Sonra bu uzmanların çıktıları tek bir modele distill edildi.
2. **On-Policy Distillation.** Aynı sorunun yazılı hâline verilen cevap, sesli hâlinin hedefi oldu. Örnek: model "Fransa'nın başkenti ne?" yazısına "Paris" diyorsa, aynı soruyu sesle duyduğunda da aynı cevabı vermeye zorlanır. Böylece ses girdisi ile metin girdisi arasındaki kalite farkı kapanır.
3. **Interaction-Aligned RL.** Çok turlu konuşmalar ([multi-turn](00_terimler.md#agentic-rl-ve-multi-turn): modelin kullanıcıyla ya da ortamla birden çok tur etkileşimi) üzerinde RL. Reward'lar kullanıcı deneyimine bağlı: dil karışması, persona tutarsızlığı, uzun bağlamda talimat takibi.
4. **Talker.** [DPO](00_terimler.md#dpo-ve-preference-optimization) (iyi ve kötü cevap çiftlerinden doğrudan tercih öğrenen yöntem), kural tabanlı reward ve GSPO (bu dosyada aşağıda ayrı girdisi olan bir RL algoritması).

Thinker için veri boyutu, filtreleme ve RL algoritması raporda verilmemiş.

**Sonuç:** Yazarların raporuna göre Plus varyantı 215 ses ve ses-görüntü alt görevinde SOTA (state of the art: o görevde bilinen en iyi sonuç) bildiriyor. Post-training aşamalarına ait ablation yok; yani hangi aşamanın ne kadar katkı verdiğini bilmiyoruz.

**Bizim için:** "Önce uzmanları ayrı eğit, sonra tek modele distill et" düzeni şunu söylüyor: SQL agent becerisini ayrı bir uzman (9B) üzerinde kurup küçük modele distill etmek, Qwen'in kendi ailesinde kullandığı yol.

## Qwen3-Coder-Next Technical Report (Qwen Team, Şubat 2026) — [2603.00729](https://arxiv.org/abs/2603.00729)
**Tek cümlede:** Çalıştırılabilir coding görevlerini çok büyük ölçekte üretip modeli bu ortamlardan gelen geri bildirimle eğiten bir coding agent reçetesi.

**Problem:** Coding agent'ının (dosya okuyan, komut çalıştıran, kodu düzelten model) başarısı kodun gerçekten çalışıp çalışmadığına bağlı. Bunu öğretmek için çalıştırılabilir, otomatik doğrulanabilen çok sayıda görev gerekir. Model ayrıca farklı araçların (IDE eklentileri, komut satırı araçları) farklı tool biçimlerine uymalı. Yazarlar agentic eğitimi ölçeklemenin model boyundan daha önemli olduğunu savunuyor.

**Ne yaptılar:** Taban model Qwen3-Next: toplam 80B, her token'da 3B aktif parametre; hybrid attention (iki farklı attention türünü karıştıran yapı) ve MoE.
1. **[Mid-training](00_terimler.md#mid-training).** Pretraining ile post-training arasında, belli bir alana odaklı ek eğitim. Trilyonlarca token, 262,144 token bağlam. FIM (fill-in-the-middle: kodun ortasındaki boşluğu öncesine ve sonrasına bakarak doldurma) görevi var. Repo düzeyinde yaklaşık 600B token.
2. **SFT.** İç veri; çalıştırılarak doğrulanmış agentic trajectory'ler (trajectory: agent'ın bir görevdeki bütün tool call'ları ve gözlemleri) ve dokümana dayalı soru-cevap. Boyut verilmemiş. Filtre: SFT cevapları bir agent'la çalıştırılır, çalışmayanlar atılır. Tool-call verisi kural tabanlı biçim kontrolünden geçer; bitiş adımı (finish action) yoksa ya da bir tool call başarısızsa örnek atılır.
3. **Dört uzman.** Aynı SFT checkpoint'inden dört ayrı uzman eğitilir:
   - WebDev uzmanı: Chromium tarayıcıda render edilip VLM (görüntüye bakabilen dil modeli) ve tarayıcı etkileşimiyle doğrulanmış trajectory'lerle.
   - Tool calling uzmanı: birçok scaffold'dan (agent'ı çalıştıran çerçeve) gelen ve biçim kontrolünden geçmiş trajectory'lerle. Bu iki uzman için RL'den söz edilmiyor.
   - Tek turlu doğrulanabilir QA (question answering, soru-cevap) uzmanı: unit test reward'lı RL. Unit test'ler birden çok modelle üretilip çoğunluk oyuyla seçilir.
   - SWE uzmanı (SWE, software engineering: gerçek bir repo'da issue çözme): SWE-Gym, SWE-rebench ve iç ortamlarda çok turlu RL.
4. **Görev havuzu.** GitHub PR'larından (pull request: bir repo'ya önerilen kod değişikliği) 807,693 çalıştırılabilir SWE örneği (52,960 repo) ve yaklaşık 800K sentetik bug görevi. RL prompt'larında pass rate dağılımı tahmin edilir; çok kolaylar ve gürültülü biçimde başarısız olanlar çıkarılır. SFT ve RL prompt'ları tamamen ayrıktır, yani hiçbir soru ikisinde birden yoktur.
5. **Reward.** Ana puan görevin sonundaki başarıdır. Tur sınırını aşan trajectory ceza alır. Her turda geçersiz tool call'ın token'ları ayrıca ceza alır. Görevin repo linkini içeren ya da git/curl/wget kullanan tool call'lar engellenir ve modele açık bir geri bildirim verilir. Amaç [reward hacking](00_terimler.md#reward-hacking)'i (modelin görevi çözmeden puanı almanın kestirme yolunu bulması) önlemek; örneğin çözümü internetten indirmek. RL algoritması ve hiperparametreler verilmemiş. Eğitimde 20 farklı tool template'i (tool call'ların yazım biçimi) kullanılmış.
6. **Distillation.** Dört uzman "SFT modelinin içine" distill edilir. Bunun [off-policy mi on-policy mi](00_terimler.md#on-policy-ve-off-policy) olduğu raporda yok (off-policy: küçük model büyük modelin hazır çıktılarıyla eğitilir; on-policy: küçük model kendi ürettiği cevaplar üzerinde eğitilir). Uzmanların kendisiyle ya da tek bir karışık RL / model merging ile karşılaştırma da yok.

**Sonuç:** Yazarların raporuna göre:
- SWE-Bench Verified (gerçek GitHub issue'larını çözme; insanlarca doğrulanmış alt küme): 70.6–71.3, scaffold'a göre değişiyor.
- SWE-Bench Pro (daha zor ve uzun yazılım görevleri): 42.7.
- Terminal-Bench 2.0 (terminalde komut çalıştırarak görev çözme): 25.8–36.2.
- Beş IDE (kod geliştirme ortamı) ve CLI (komut satırı aracı) scaffold'unda tool template'ine uyma oranı ortalama 92.7.
- Bu dosyada bu rakamlar için başka bir modelle karşılaştırma yok.
- Template çeşitliliği arttıkça SWE-Bench Verified artıyor (yalnızca grafik, rakam yok).
- Reward hacking engeli konduktan sonra RL sırasında ortalama agent tur sayısı 50'den 130'a çıkmış. Yani kestirme yol kapanınca model görevi gerçekten çözmek için daha çok adım atmaya başlamış.

**Bizim için:** Geçersiz tool call token'larına ceza, tur sınırı cezası ve SFT/RL prompt'larının ayrık tutulması doğrudan bizim `execute_sql` / `submit` döngümüze uygulanabilir. Pass rate ile "çok kolay" soruları atmak, RL verisini seçmenin ucuz yolu.

## Qwen3.5: Towards Native Multimodal Agents (Qwen Team, Şubat 2026) — [blog](https://qwen.ai/blog?id=qwen3.5)
**Tek cümlede:** Bizim small model'imizin (Qwen3.5-0.8B) ailesi; RL'i milyonlarca agent ortamına ölçeklediğini söylüyor, ama küçük modellerin nasıl eğitildiğini yazmıyor.

**Problem:** Qwen3.5, baştan çok modlu ve agent işleri için tasarlanmış bir aile. Agent becerisi (tool seçmek, sonucu okuyup karar vermek) çok çeşitli ortamlarda pratik gerektirir. Bizim için asıl soru şu: 0.8B model nasıl eğitildi ve onu nasıl ek eğitmeliyiz?

**Ne yaptılar:**
1. **Mimari.** Gated DeltaNet (uzun bağlamda klasik attention'dan daha ucuz çalışan, doğrusal attention türü bir katman) ile sparse MoE. Early-fusion: görüntü ve metin baştan aynı modelde birlikte işlenir, sonradan eklenmez.
2. **Çıkış tarihleri.** 397B-A17B 16 Şubat 2026'da; 0.8B, 2B, 4B ve 9B küçük modeller 2 Mart 2026'da çıktı.
3. **RL.** [GitHub README](https://github.com/QwenLM/Qwen3.5)'ye göre RL, "giderek karmaşıklaşan görev dağılımlarına sahip milyonlarca agent ortamına" ölçeklenmiş. Bu bir tür [curriculum](00_terimler.md#curriculum) (kolaydan zora sıralanmış eğitim). Rollout üretimi ile eğitimi ayıran asenkron bir RL altyapısı kullanılmış: bir grup makine cevap üretirken diğerleri eğitimi sürdürür.
4. **Küçük modeller.** Nasıl eğitildikleri (distillation mı, RL mi) yazılmamış.
5. **Thinking modu.** 0.8B varsayılan olarak non-thinking çalışır ([thinking mode](00_terimler.md#thinking-mode): modelin cevaptan önce görünür bir düşünme metni yazdığı mod). [Model kartı](https://huggingface.co/Qwen/Qwen3.5-0.8B), 0.8B'nin thinking modunda döngüye girmeye (aynı şeyi tekrar tekrar yazmaya) diğer boylardan daha yatkın olduğunu söylüyor.

**Sonuç:** Yazarların raporuna göre (0.8B model kartı):
- Non-thinking: IFEval (biçim talimatlarına uyma, ör. "200 kelimeden kısa yaz") 52.1; MMLU-Pro (birçok alanda zor çoktan seçmeli bilgi soruları) 29.7.
- Thinking: BFCL-V4 (Berkeley Function Calling Leaderboard: tool/function çağırmanın doğruluğu) 25.3; TAU2-Bench (müşteri hizmeti gibi çok turlu, tool kullanılan görevler) 11.6.
- Bu dosyada bu rakamlar için karşılaştırma yok; ablation da yok. Rakamlar 0.8B'nin agent işlerinde tek başına zayıf olduğunu gösteriyor.

**Kaynak notu:** Resmi bir technical report yok. Bilgiler blog'dan, GitHub README'den ve Qwen3.5-0.8B model kartından.

**Bizim için:** Bizim small model'imizin resmi reçetesi belirsiz. Zorluğu giderek artan ortam dağılımı (curriculum) Qwen'in tercih ettiği yön. 0.8B'yi thinking kapalı eğitmek de kartın uyarısıyla tutarlı.

## Qwen3-Max-Thinking (Alibaba / Qwen, Ocak 2026) — [blog](https://www.alibabacloud.com/blog/602832)
**Tek cümlede:** Search, Memory ve Code Interpreter tool'larını kendisi seçip kullanan, 1 trilyonun üzerinde parametreli bir reasoning modeli.

**Problem:** Çok büyük bir reasoning modelinin, hangi durumda hangi tool'u kullanacağına kendisi karar vermesi isteniyor. Ayrıca zor sorularda tek bir deneme yerine birkaç tur deneyip öncekilerden ders çıkarması amaçlanıyor.

**Ne yaptılar:**
1. **Tool kullanımı için ilk fine-tuning.** Önce model tool kullanmayı örneklerle öğrenir.
2. **RL.** Ardından çeşitli görevlerde kural tabanlı ve model tabanlı geri bildirimle RL. Kural tabanlı: cevap doğru mu diye otomatik kontrol. Model tabanlı: başka bir modelin cevabı puanlaması ([reward model](00_terimler.md#reward-model-grm-ve-prm) ya da [LLM-as-judge](00_terimler.md#llm-as-judge-ve-rubric)).
3. **"Experience-cumulative, multi-round" [test-time scaling](00_terimler.md#test-time-scaling).** Test-time scaling, cevap verirken daha çok hesap harcayarak doğruluğu artırmak demek. Burada model bir soruyu birkaç turda dener. Her turun sonunda çıkarılan sonuçlar sıkıştırılır ve bir sonraki tura taşınır. Örnek: 1. turda "tablo X'te bu sütun yok" öğrenildiyse, 2. tur bunu bilerek başlar.
4. RL algoritması, reward model ve veri boyutu açıklanmamış.

**Sonuç:** Yazarların raporuna göre 19 benchmark'ta Claude Opus 4.5, Gemini 3 Pro ve GPT-5.2-Thinking ile rekabetçi. Blog metninde rakam yok.

**Kaynak notu:** Yalnızca blog. Rakam, algoritma ve veri bilgisi yok.

**Bizim için:** "Önce tool kullanımını SFT ile öğret, sonra kural tabanlı reward'la RL yap" sırası bizim için de varsayılan. Önceki denemelerin özetini bağlama koymak, bizim `compress`'imize benzer bir fikir.

## QwenLong-L1.5: Post-Training Recipe for Long-Context Reasoning and Memory Management (Tongyi Lab, Alibaba, Aralık 2025) — [2512.12967](https://arxiv.org/abs/2512.12967)
**Tek cümlede:** Qwen3-30B-A3B-Thinking-2507'ye çok uzun dokümanlarda reasoning öğreten bir reçete: soru sentezi, görev tiplerini dengeleyen örnekleme ve entropiye göre çalışan bir RL düzeltmesi.

**Problem:** Uzun dokümanlarda (yüz binlerce, hatta milyonlarca token) cevap birçok yerden bilgi toplamayı gerektirir. Bu tür eğitim verisi az. RL de uzun bağlamda kolayca dengesizleşir: bazı görev tipleri baskın çıkar, modelin çeşitliliği bir anda çöker. Bağlama sığmayan dokümanlar için de bir memory-agent yapısı gerekir (model dokümanı parça parça okur ve notlar tutar).

**Ne yaptılar:**
1. **Soru sentezi.** 82,175 dokümandan (yaklaşık 9.2B token) üç yolla soru üretildi: (a) knowledge graph'tan (varlıklar ve ilişkileri) birden çok adım gerektiren sorular; (b) korpus düzeyinde sayısal sorular; bunun için NL2SQL (doğal dilden SQL üreten) bir tablo motoru kullanıldı; (c) self-evolve: soru öneren (proposer), çözen (solver) ve doğrulayan (verifier) agent'ların birlikte çalışması.
2. **Filtre.** 42.7K sentetik örnek; zorluk filtresi, tekilleştirme ve test [decontamination](00_terimler.md#decontamination) (test sorularına benzeyen eğitim örneklerini atma) ile 14.1K'ya iniyor. Doküman olmadan cevaplanabilen sorular atılıyor. İlgisiz doküman eklenince pass@k'sı sıfıra düşen sorular da atılıyor (pass@k: k denemeden en az birinin doğru olma oranı).
3. **Curriculum.** Üç aşama; giriş/çıkış uzunluğu 20K/12K → 60K/20K → 120K/50K token. Her geçişte "difficulty-aware retrospective sampling": önceki aşamanın zor gelen örnekleri bir sonraki aşamanın ayarlarıyla yeniden kullanılır.
4. **Task-balanced sampling.** Offline: sorular base modelin pass@k'sına göre zorluk kovalarına (bin) bölünür ve her kovadan eşit sayıda alınır. Online: her batch'te beş görev tipinden eşit sayıda soru bulunur. Advantage'ın ölçeği (standart sapması) aynı görev tipindeki örneklerden hesaplanır; böylece bir görev tipinin puanları diğerininkini ezmez.
5. **AEPO.** Yazarların önerdiği policy optimization. [Entropi](00_terimler.md#entropy-ve-entropy-collapse) (modelin bir sonraki token'dan ne kadar emin olmadığı) batch'te üst eşiği aşınca negatif advantage'lı örnekler (ortalamadan kötü cevaplar) eğitimden çıkarılır. Entropi alt eşiğin altına düşünce geri gelir. Amaç entropiyi iki eşik arasında tutmak: ne patlasın ne çöksün.
6. **Ayarlar.** Soru başına 8 rollout, batch 128, learning rate 2e-6, temperature 0.7, tamamen on-policy (her güncelleme o anki modelin ürettiği cevaplarla), [KL penalty](00_terimler.md#kl-penalty) yok (KL penalty: modelin başlangıç modelinden fazla uzaklaşmasını engelleyen ceza).
7. **Reward.** Önce kural: doğru cevap çıktıda geçiyor mu. Tutmazsa bir LLM judge karar verir.

**Sonuç:** Yazarların raporuna göre:
- Altı uzun bağlam benchmark'ının ortalaması 61.92'den 71.82'ye çıkıyor (+9.90). MRCR (uzun bir konuşmada birbirine benzeyen birçok istekten doğrusunu bulma) +31.72, CorpusQA (büyük bir doküman yığını üzerinde soru-cevap) +9.69.
- 1M–4M token'lık görevlerde memory-agent baseline'ına göre +9.48.
- Uzun bağlam eğitimi kısa matematiği de bozmuyor, iyileştiriyor: AIME25 (lise matematik olimpiyatı soruları) 82.81'den 86.46'ya.
- Ablation (Qwen3-4B-Thinking): düz GRPO 56.07. Görev dengeli örnekleme ve görev bazlı ölçekleme eklenince 58.62. Üstüne AEPO eklenince 59.36. Yani en büyük katkı dengeli örneklemeden geliyor (+2.55), AEPO bunun üstüne +0.74 ekliyor.

**Bizim için:** Her batch'te SQL görev tiplerini (ör. join, aggregation, filtre ağırlıklı) eşit tutmak ve advantage'ı tip başına ölçeklemek, küçük modelde entropi patlamasını önleyebilir. Pass@k kovalarıyla örneklemek ucuz bir zorluk dengesi.

## Stabilizing Reinforcement Learning with LLMs: Formulation and Practices (Qwen Team, Aralık 2025) — [2512.01374](https://arxiv.org/abs/2512.01374)
**Tek cümlede:** Cevabın tamamına verilen bir reward'ı token token optimize etmenin ne zaman doğru çalıştığını teoriyle gösteren ve bunu koruyan pratikleri deneyle sıralayan bir çalışma.

**Problem:** RL'de reward bütün cevaba verilir (doğru/yanlış), ama eğitim token düzeyinde yapılır. Bu, gerçek amacın yalnızca bir yaklaşığıdır. Yaklaşık bozulursa eğitim çöker: doğruluk birden düşer, entropi sıfıra iner. Büyük ölçekli RL'de bu çöküşler pahalıdır. Hangi tekniğin neden işe yaradığı da çoğu zaman belirsiz kalır.

**Ne yaptılar:**
1. **Teori.** Token düzeyindeki kayıp, gerçek amacın birinci dereceden yaklaşığıdır. Bu yaklaşık iki şart sağlanınca geçerli kalır:
   - **Training-inference farkı küçük olmalı.** Rollout'u üreten inference motoru ile eğitim motoru aynı cevaba biraz farklı olasılıklar verebilir. Nedenleri makaleden: farklı hesaplama kernel'leri, batch'e göre değişen sonuçlar, MoE'de farklı uzman seçimi, farklı sayı hassasiyeti.
   - **Policy staleness küçük olmalı.** Rollout'u üreten model, eğitilen modelin çok eski bir hâli olmamalı.
2. **Bu şartları koruyan üç araç.**
   - [IS correction](00_terimler.md#importance-sampling) (importance sampling düzeltmesi): her token'ın kaybı, eğitim motorunun verdiği olasılığın inference motorunun verdiği olasılığa oranıyla ağırlıklandırılır. Böylece iki motor arasındaki fark düzeltilir.
   - [Clipping](00_terimler.md#clip-ve-clip-higher): bu oran belli bir aralığın dışına çıkınca o token'ın güncellemesi kesilir. Model tek adımda fazla değişmez.
   - Routing Replay (yalnızca MoE için): rollout sırasında seçilen uzmanlar kaydedilir ve eğitimde aynı uzmanlar kullanılır. Makalede iki türü var. R2 eğitim motorunun eski modelde seçtiği uzmanları tekrarlar; staleness'ı azaltır. R3 inference motorunun seçtiği uzmanları tekrarlar; iki motor arasındaki farkı daha doğrudan azaltır.
3. **Deney düzeni.** Qwen3-30B-A3B-Base'ten fine-tune edilmiş bir [cold-start](00_terimler.md#cold-start) model (cold-start: RL'e başlamadan önce kısa bir SFT ile hazırlanmış model). Inference FP8, eğitim BF16 (FP8 ve BF16 sayıları 8 ve 16 bitle tutan biçimler; FP8 daha hızlı ama daha kaba). Bu bilerek seçilmiş zor bir test: iki motor arasındaki fark büyük olsun diye.
4. **Veri.** Doğrulanmış cevabı olan 4,096 matematik problemi. Reward ikili: doğruysa 1, yanlışsa 0.
5. **Batch.** Bir mini-batch 1,024 cevap (64 soru × 16 cevap), cevap en fazla 32,768 token. Off-policy derecesini ayarlamak için global batch 2,048, 4,096 ya da 8,192: bir rollout turundan 2, 4 ya da 8 güncelleme yapılır ve sonraki güncellemeler giderek eskiyen cevaplarla çalışır (off-policy: eğitimin, şu anki modelden farklı bir modelin ürettiği cevaplarla yapılması).
6. **Baseline "MiniRL".** Grup içinde normalize edilmiş advantage (GRPO'daki gibi). Decoupled clipping: oran en fazla %20 aşağı (ε_low 0.2) ve en fazla %27 yukarı (ε_high 0.27) gidebilir. Token düzeyinde IS correction, oran 5'te kırpılır.
7. **Ölçek.** Toplam yüz binlerce GPU saati.

**Sonuç:** Yazarların raporuna göre:
- On-policy eğitimde en kararlı yöntem, IS correction'lı düz policy gradient (MiniRL; policy gradient, iyi cevapların olasılığını artırıp kötülerinkini azaltan en temel RL güncellemesi).
- IS correction kaldırılınca eğitim hızla çöküyor ve entropi düşüyor.
- Length normalization (her cevabın kaybını cevabın uzunluğuna bölmek) kararlı ama sonuç daha kötü.
- Off-policy eğitimde hem clipping hem Routing Replay şart. R2 az off-policy'de (2×) daha iyi; R3 4× ve 8×'te daha iyi.
- Üç farklı cold-start modeli (Qwen3-Max-Thinking-Preview, DeepSeek-R1-0528 ve gpt-oss-120b'den distill edilmiş) kararlı bir RL ile benzer bir son noktaya ulaşıyor. Yani başlangıç noktasından çok RL'in kararlı olması önemli.

**Bizim için:** Dense (MoE olmayan) 0.8B'de MoE'ye özgü Routing Replay gereksiz. Ama MLX'te (Apple Silicon için makine öğrenmesi kütüphanesi) rollout üretip başka bir yerde eğitirsek, iki motor arasındaki fark için IS correction koymak ve olabildiğince on-policy kalmak gerekir. Length normalization'dan kaçınmak da ucuz bir ders.

## Qwen3-VL Technical Report (Qwen Team, Kasım 2025) — [2511.21631](https://arxiv.org/abs/2511.21631)
**Tek cümlede:** 2B'den 235B'ye görüntü-metin modeli ailesi; post-training SFT, büyükten küçüğe distillation ve iki tür RL'den oluşuyor.

**Problem:** Görüntülü bir modelin reasoning yapması isteniyor, ama birçok "görsel" soru aslında görüntüye bakmadan çözülebiliyor. Bu sorular modele görüntüyü kullanmayı öğretmez. Küçük modeller (2B–8B) de büyükler kadar iyi olmalı. Tool kullanan RL'de ise model kolay bir alışkanlığa (tek tool call) saplanabiliyor. Thinking ve non-thinking varyantları ayrı yayımlandı.

**Ne yaptılar:**
1. **SFT.** Yaklaşık 1,200,000 örnek; üçte biri yalnız metin. İki faz: önce 32K, sonra 256K token bağlamla.
2. **Long-CoT cold start.** Base modellerin pass rate'i düşük olan sorular tutulur. Görüntü olmadan çözülebilen sorular atılır. Yanlış, tahmine dayalı ya da kendini tekrarlayan cevaplar atılır.
3. **Küçük modellere distillation (strong-to-weak).** Yalnız metin verisiyle iki adım: önce off-policy (küçük model büyük modelin hazır çıktılarıyla eğitilir), sonra on-policy (küçük model kendi cevabını üretir ve olasılıkları büyük modelinkilere KL ile yaklaştırılır; KL, iki olasılık dağılımı arasındaki farkı ölçen sayı).
4. **RL verisi.** Yaklaşık 30K soru. Her soruya 16 cevap üretilir. Pass rate'i %90'ın üstündeki sorular (çok kolay) atılır. 16 cevabın hepsi yanlışsa (çok zor) da atılır.
5. **Algoritma.** SAPO (bu dosyada hemen aşağıda ayrı girdisi var). Batch'ler görevlere sabit oranla karıştırılır.
6. **Reasoning RL.** Doğrulama kural ya da kod çalıştırıcıyla. Format reward'ı yok. Prompt'un dilinden farklı bir dilde cevap verilirse ceza.
7. **General RL.** Kural tabanlı (format, talimat takibi) ve model tabanlı judge reward'ları.
8. **Tool kullanımlı RL.** Üç reward: cevap doğruluğu, çok turlu reasoning ve tool-calling reward'ı. Tool-calling reward'ı olmadan model tek bir tool call yapıp bırakmaya çöküyor.

**Sonuç:** Yazarların raporuna göre:
- Qwen3-VL-235B-A22B-Thinking: AIME-25 89.7, LiveCodeBench v6 (yayımlandıktan sonra eklenen yarışma kodlama soruları; eğitim verisine sızmamış olsun diye) 70.1. Bu dosyada bu rakamlar için karşılaştırma yok.
- 2B/4B/8B için distillation'ın etkili olduğu söyleniyor, ama rakamla değil.
- Post-training aşamalarının ablation'ı yok.

**Bizim için:** "Hepsi doğru (>%90) ve hepsi yanlış soruları at" filtresi ve tool çağırmayı ayrıca ödüllendirmek (yoksa model tek çağrıya çöküyor) bizim çok adımlı SQL agent'ımız için doğrudan uygulanabilir.

## Soft Adaptive Policy Optimization (Qwen Team, Kasım 2025) — [2511.20347](https://arxiv.org/abs/2511.20347)
**Tek cümlede:** RL'de "sınırı aşan token'ı tamamen kes" kuralı yerine, sınırdan uzaklaştıkça token'ın ağırlığını yumuşakça azaltan bir kapı (SAPO).

**Problem:** RL'de her token için bir importance ratio hesaplanır: eğitilen modelin o token'a verdiği olasılık bölü rollout'u üreten modelin verdiği olasılık. Oran 1'den çok uzaklaşırsa güncelleme tehlikelidir. GRPO bu durumda sert clipping yapar: oran aralığın dışına çıkınca o token'ın gradient'i sıfırlanır. GSPO (aşağıda) oranı bütün cevap için hesaplar; birkaç token aşırı uzaklaşınca bütün cevabı susturur. İki durumda da işe yarar bilgi kaybolur ve eğitim kararsızlaşabilir.

**Ne yaptılar:**
1. **Yumuşak kapı.** Sert sınır yerine, oranın 1'den sapmasını bir sigmoid eğrisinden geçiren bir ağırlık. Oran tam 1 iken ağırlık 1'dir. Oran 1'den uzaklaştıkça ağırlık yavaş yavaş azalır, birden sıfırlanmaz. Kapının dikliği bir sıcaklık (τ) ile ayarlanır. Örnek: oran 1.3 olan bir token GRPO'da tamamen kesilirdi; SAPO'da yalnızca daha az ağırlıkla katkı verir.
2. **Yalnızca kötü token'ları etkilemek.** GSPO'dan farkı: bir cevapta birkaç token aşırı uzaklaşırsa SAPO yalnızca o token'ların ağırlığını düşürür, cevabın geri kalanı öğrenilmeye devam eder.
3. **Pozitif ve negatif için farklı sıcaklık.** Pozitif advantage'lı token'lara (ortalamadan iyi cevaplar) τ_pos = 1.0, negatif advantage'lılara τ_neg = 1.05. Negatif token'ların kapısı biraz daha dik, yani daha hızlı sönümleniyor.
4. **Deney düzeni.** Qwen3-30B-A3B-Base'ten cold-start model, matematik soruları. Her rollout batch'i 4 mini-batch'e bölünür (yani bir rollout'tan 4 güncelleme yapılır). Diğer hiperparametreler GSPO makalesiyle aynı. Qwen3-VL'nin eğitiminde matematik, kod, mantık ve çok modlu görevler sabit oranla karışık.

**Sonuç:** Yazarların raporuna göre:
- AIME25, HMMT25 (Harvard-MIT matematik yarışması soruları) ve BeyondAIME'de (AIME'den zor matematik soruları) SAPO, GSPO'dan ve GRPO-R2'den (GRPO + Routing Replay) daha kararlı ve daha yüksek Pass@1 (ilk denemede doğruluk) veriyor. GSPO ve GRPO-R2 eğitimin erken bir noktasında çöküyor.
- Rakamlar yalnızca grafikte; metinde sayı yok.
- Ablation: τ_neg > τ_pos en kararlı; τ_neg < τ_pos en kararsız. Yani negatif örnekleri biraz daha sert sönümlemek kararlılık getiriyor.
- MoE'de Routing Replay gerektirmiyor.

**Bizim için:** Negatif örnekleri pozitiflerden biraz daha sert sönümlemek küçük modelde de stabilite için ucuz bir ayar. Ama tek GPU'luk, neredeyse on-policy bir koşuda GRPO'nun clipping'i büyük olasılıkla yeterli.

## Qwen3Guard Technical Report (Qwen Team, Ekim 2025) — [2510.14276](https://arxiv.org/abs/2510.14276)
**Tek cümlede:** Güvenlik sınıflandırıcısı (guard) modelleri eğitip birini reward olarak kullanarak Qwen3-4B'ye güvenlik RL'i yaptılar; tek bir ikili reward'ın nasıl hack'lendiğini gösteren temiz bir örnek.

**Problem:** Bir modelin zararlı isteklere uymaması istenir, ama zararsız isteklere de gereksiz yere "hayır" dememesi gerekir. Güvenlik etiketleri de gürültülüdür: bazı örnekler gerçekten tartışmalıdır. Bu çalışma reward model eğitimi, etiket temizleme ve hybrid reward tasarımı için somut bir örnek veriyor.

**Ne yaptılar:**
1. **Generative Qwen3Guard.** Instruct Qwen3 üzerinde düz SFT. 1.19M'den fazla insan etiketli ve sentetik örnek. Üç etiket: safe (güvenli), controversial (tartışmalı), unsafe (güvensiz).
2. **"Controversial" etiketinin üretilmesi.** Veri A ve B diye ikiye bölünür. A üzerinde iki model eğitilir: biri fazladan güvenli örnekle (strict, katı), biri fazladan güvensiz örnekle (loose, gevşek). İki model B'yi etiketler. İkisi çelişirse örnek controversial olur. Sonra A ile B'nin rolleri değişir.
3. **Etiket temizleme.** Ayrık alt kümelerde eğitilen modeller birbirinin etiketlerini düzeltir. Qwen3-32B'den distillation da kullanılır.
4. **Stream Qwen3Guard.** Her token'da risk tahmini yapan, iki çıktı başlığı (head) olan bir varyant. Cevap üretilirken anında uyarı verebilir.
5. **Güvenlik RL'i (Qwen3-4B-SafeRL).** Algoritma GSPO. WildJailbreak'ten (modeli kandırmaya çalışan istekler) prompt'lar; her prompt'a 8 cevap. 8 cevabın hepsinin aynı sonucu verdiği prompt'lar atılır. Thinking için 13.7K, non-thinking için 6.7K örnek kalır.
6. **İki reward denendi.**
   - Guard-only: düşünce ve cevap güvenliyse 1, değilse 0.
   - Hybrid: güvensiz cevap en fazla −10, ret en fazla −5; diğer cevaplar WorldPM-Helpsteer2 adlı reward model'in yardımseverlik skorunu alır (WorldPM bu dosyada aşağıda ayrı bir girdi).

**Sonuç:** Yazarların raporuna göre:
- Guard-only reward yaklaşık 99.7 güvenliğe ulaşıyor, ama ret oranı yaklaşık %96'ya çıkıyor. Bu reward hacking: model her şeyi reddederek tam puan alıyor.
- Hybrid reward, non-thinking: WildGuard (güvenlik değerlendirme seti) güvenliği 64.7'den 98.1'e çıkıyor; ret oranı 12.9'dan 5.3'e düşüyor; ArenaHard-v2 (zor sohbet sorularında genel cevap kalitesi) 9.5'ten 10.7'ye çıkıyor. Yani model hem daha güvenli hem daha az reddediyor, genel kalite de düşmüyor.
- Hybrid reward, thinking: güvenlik 59.0'dan 97.4'e; ret 6.5'ten 6.2'ye.

**Bizim için:** Tek bir ikili reward kolay kaçış yolunu ödüllendirir (bizde: "boş sonuç döndür" ya da hemen `submit`). Asıl reward'ın yanına ayrı bir ceza terimi ve hepsi aynı sonucu veren prompt'ları atan bir filtre koymak gerekir.

## Qwen3-Omni Technical Report (Qwen Team, Eylül 2025) — [2509.17765](https://arxiv.org/abs/2509.17765)
**Tek cümlede:** Tek modelde metin, görüntü, ses ve video; sesi eklerken metin ve görüntü performansını düşürmemeyi hedefleyen bir rapor.

**Problem:** Bir modele yeni bir modalite (ör. ses) eklemek, eski becerilerini bozabilir. Omni bir modelin her alanda tek alana özel modeller kadar iyi olması isteniyor.

**Ne yaptılar:** Thinker'ın (metin cevabını üreten parça) post-training'i üç aşama:
1. **Hafif SFT.** Az veriyle temel davranış.
2. **Strong-to-weak distillation (Qwen3'teki gibi).** Önce off-policy: büyük modellerin hazır çıktılarıyla eğitim. Sonra on-policy: eğitilen model kendi cevabını üretir ve olasılıkları Qwen3-32B ya da Qwen3-235B-A22B'nin olasılıklarına KL ile yaklaştırılır.
3. **GSPO ile RL.** Metin, görüntü, video ve ses üzerinde. Reward: doğrulanabilir görevlerde (matematik, kod, talimat takibi) kural tabanlı. Genel görevlerde referans cevaplı LLM-as-judge (bir modelin, elindeki örnek cevaba bakarak puan vermesi).

Talker'da (cevabı sese çeviren parça) DPO. Veri boyutları verilmemiş.

**Sonuç:** Yazarların raporuna göre:
- Aynı boyda (30B-A3B) üç base model karşılaştırılıyor: yalnız metin, yalnız görüntü ve omni. Sonuçlar karışık: bazı görevlerde omni daha iyi, bazılarında daha kötü.
- Instruct modelde MMLU-Redux (MMLU bilgi sorularının hataları temizlenmiş hâli) 86.6. Yalnız metin kardeşi Qwen3-30B-A3B-Instruct-2507: 89.3. Yani metin bilgisinde 2.7 puan geride.

**Bizim için:** Qwen'in sabit sırası "hafif SFT → off-policy distillation → on-policy distillation → RL". Küçük model için bu sıranın ilk üç adımı RL'den ucuz.

## Group Sequence Policy Optimization (Qwen Team, Temmuz 2025) — [2507.18071](https://arxiv.org/abs/2507.18071)
**Tek cümlede:** Importance ratio'yu ve clipping'i token token değil, bütün cevap üzerinden hesaplayan RL algoritması (GSPO); Qwen3 (2507) modellerinin ve Qwen3-Next'in RL'inde kullanıldı.

**Problem:** GRPO'da reward bütün cevaba verilir, ama importance ratio ve clipping her token için ayrı hesaplanır. Yazarlara göre bu uyumsuzluk token düzeyindeki gradient'leri gürültülü yapar. Gürültü uzun cevaplarda birikir ve eğitimi çökertebilir. MoE modellerinde sorun daha büyüktür, çünkü her güncellemede token'ların gittiği uzmanlar değişebilir.

**Ne yaptılar:**
1. **Cevap düzeyinde oran.** Bir cevabın oranı, cevabın bütün token'larının oranlarının geometrik ortalamasıdır (uzunlukla normalize edilmiş cevap olasılığı oranı). Örnek: 3 token'lık bir cevapta token oranları 1.1, 0.9 ve 1.0 ise cevap oranı bunların geometrik ortalaması, yani 1'e çok yakın bir sayıdır.
2. **Cevap düzeyinde clipping, reward ve optimizasyon.** Clipping kararı bütün cevap için verilir: ya bütün cevap güncellemeye girer ya hiçbiri.
3. **Çok dar clipping aralığı.** Cevap oranı 1'e çok yakın kaldığı için aralık çok dar: 3e-4 aşağı / 4e-4 yukarı. Karşılaştırılan GRPO'da aralık 0.2 / 0.27.
4. **Deney düzeni.** Qwen3-30B-A3B-Base'ten cold-start model. Düzenli güncellenen bir soru seti (boyutu verilmemiş). Her rollout batch'i 4 mini-batch.
5. **GSPO-token varyantı.** Çok turlu RL gibi durumlarda her token'a ayrı advantage vermeye izin veren bir sürüm.

**Sonuç:** Yazarların raporuna göre:
- GSPO, GRPO'ya göre token'ların yaklaşık iki büyüklük mertebesi (yaklaşık 100 kat) daha fazlasını clip ediyor. Buna rağmen aynı compute'ta daha verimli ve daha yüksek doğruluğa ulaşıyor. Yazarlar buradan GRPO'nun token düzeyindeki gradient'lerinin gürültülü olduğu sonucunu çıkarıyor.
- MoE'de GRPO, Routing Replay olmadan yakınsamıyor; GSPO yakınsıyor.
- Cevap olasılığı inference motorunun döndürdüğü olasılıklarla doğrudan hesaplanabildiği için GSPO, eğitim ile inference arasındaki sayı hassasiyeti farkına daha dayanıklı.

**Bizim için:** MLX inference ile başka bir trainer arasında hassasiyet farkı olursa, cevap düzeyinde oran (GSPO) daha güvenli bir varsayılan. Çok turlu tool trajectory'lerinde GSPO-token kullanılabilir.

## Qwen3-Coder: Agentic Coding in the World (Qwen Team, Temmuz 2025) — [blog](https://qwenlm.github.io/blog/qwen3-coder/)
**Tek cümlede:** Qwen3-Coder-480B-A35B'nin post-training'i iki şeyi ölçeklemeye dayanıyor: gerçek coding görevlerinde kod RL'i ve çok turlu, uzun agent RL'i.

**Problem:** Kod RL'i çoğunlukla yarışma problemleriyle yapılır. Ama gerçek coding işi bundan çok daha çeşitlidir. Agent olarak çalışmak da tek bir cevap değil, birçok tur plan, deneme ve düzeltme gerektirir. Bu da çok sayıda paralel ortam ister.

**Ne yaptılar:**
1. **Kod RL'ini genişletmek.** Yalnızca yarışma problemleriyle sınırlı kalmayıp "çözmesi zor, doğrulaması kolay" gerçek coding görevlerine yayıldılar. Örnek: bir fonksiyonu yazmak zordur, ama yazılan fonksiyonun testleri geçip geçmediğini görmek kolaydır.
2. **Test case çoğaltma.** Görevlerin test case'leri otomatik olarak çoğaltıldı. Az testli bir görevde yanlış bir çözüm testleri şans eseri geçebilir; daha çok test bunu zorlaştırır.
3. **Agent RL'i.** Çok turlu tool etkileşimi üzerinde: plan yapmak, ortamdan geri bildirim almak, karar vermek. Bunun için Alibaba Cloud'da paralel 20,000 bağımsız ortam çalıştırıldı.
4. Algoritma ve veri boyutu verilmemiş.

**Sonuç:** Yazarların raporuna göre test-time scaling olmadan (yani cevap başına ek deneme ya da arama yapmadan) açık modeller arasında SWE-Bench Verified'da SOTA. Blog metninde rakam yok. Kod RL'inin kod dışındaki görevleri de iyileştirdiği söyleniyor.

**Kaynak notu:** Yalnızca blog; rakam, algoritma ve veri boyutu yok.

**Bizim için:** SQL de "zor çözülür, kolay doğrulanır" bir görev. Execution-based reward (gold SQL ile cevabın result key'ini karşılaştırmak) bizim için hazır bir verifier.

## Qwen3-2507 güncellemeleri (Qwen Team, Temmuz 2025) — [model kartı](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
**Tek cümlede:** Qwen3'ün tek modelde iki modlu (thinking + non-thinking) yaklaşımından vazgeçilip Instruct ve Thinking modelleri ayrı eğitildi; 4B'de bile büyük kazanç bildiriliyor.

**Problem:** Qwen3'te tek bir model hem düşünerek hem düşünmeden cevap verebiliyordu (hybrid thinking). Ama iki modu aynı ağırlıklarda tutmak, iki modun da en iyi kalitesine ulaşmayı zorlaştırabilir. Ayrılma gerekçesi tam olarak bu: her mod için en iyi kaliteyi ayrı almak.

**Ne yaptılar:**
1. **Modları ayırmak.** Instruct modeli yalnız non-thinking, Thinking modeli yalnız thinking olarak ayrı eğitildi. Model kartı Instruct'ın `<think>` bloğu (düşünme metni) üretmediğini söylüyor.
2. **Eğitim.** Model kartları yalnızca "pre-training & post-training" diyor. RL'de GSPO kullanıldığı GSPO makalesinde belirtiliyor.
3. **Bağlam.** 256K token.

**Sonuç:** Yazarların raporuna göre Qwen3-4B'nin non-thinking modundan Qwen3-4B-Instruct-2507'ye:
- AIME25 (lise matematik olimpiyatı): 19.1 → 47.4, yani yaklaşık 2.5 katı.
- LiveCodeBench v6 (yeni yarışma kodlama soruları): 26.4 → 35.1.
- BFCL-v3 (tool/function çağırma): 57.6 → 61.9.
- IFEval (biçim talimatlarına uyma): 81.2 → 83.4.
- Arena-Hard v2 (zor sohbet sorularında genel kalite): 9.5 → 43.4.
- Kaynak, kazancın ne kadarının modları ayırmaktan, ne kadarının farklı ya da daha fazla eğitimden geldiğini ayırmıyor. Ablation yok.

**Kaynak notu:** Ayrılma gerekçesi Qwen'in kendi metninden değil, Qwen'in duyurusunu aktaran ikincil kaynaklardan ([Nebius](https://docs.studio.nebius.com/cookbook/models/qwen3-235b-a22b-2507)).

**Bizim için:** 4B ölçeğinde bile modu ayırıp tek moda odaklanmak büyük kazanç getirmiş. Biz de small model'i yalnızca non-thinking tool call için eğitmeliyiz.

## Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models (Qwen Team, Haziran 2025) — [2506.05176](https://arxiv.org/abs/2506.05176)
**Tek cümlede:** Qwen3 tabanlı embedding ve reranker modelleri (0.6B–8B); sentetik veri üretimi, benzerlik filtresi ve checkpoint merging'in katkısını ayrı ayrı ölçen temiz bir ablation içeriyor.

**Problem:** Embedding modeli bir metni bir sayı vektörüne çevirir; benzer metinlerin vektörleri birbirine yakın olmalıdır (reranker ise bulunan adayları yeniden sıralar). İyi bir embedding modeli çok sayıda "soru – ilgili doküman" çiftiyle eğitilir, ama bu tür etiketli veri sınırlıdır. Bu bir LLM post-training çalışması değil, ama veri ve merging dersleri bizim için de geçerli. Bizim memory'miz bu ailenin 0.6B modelini kullanıyor.

**Ne yaptılar:**
1. **Zayıf denetimli pretraining.** Qwen3-32B'nin ürettiği yaklaşık 150M sentetik çift. Kayıp InfoNCE tarzı: model doğru çifti, aynı batch'teki yanlış çiftlerden ayırmayı öğrenir.
2. **Sentetik sorgu üretimi.** Sorgular dokümandan üretilir. Qwen3-32B önce bir soru tipi, bir zorluk ve bir persona (Persona Hub'dan; ör. "öğrenci", "avukat") seçer. Sonra bu ayarla o doküman için bir sorgu yazar. Böylece aynı dokümandan çok farklı sorular çıkar.
3. **SFT.** Yaklaşık 7M etiketli açık veri çifti ve yaklaşık 12M kaliteli sentetik çift. Kaliteli sentetik çiftler şöyle seçilir: kosinüs benzerliği (iki vektörün ne kadar aynı yöne baktığı) 0.7'nin üstündeki çiftler tutulur; 150M çift bu filtreyle yaklaşık 12M'e iner.
4. **Model merging.** Birden çok fine-tuning checkpoint'i slerp (spherical linear interpolation: iki ağırlık vektörünü bir küre yüzeyi üzerinde aradan geçerek karıştırma) ile birleştirilir.

**Sonuç:** Yazarların raporuna göre 0.6B modelde MMTEB (çok dilli embedding benchmark'ı; arama, sınıflandırma, kümeleme gibi görevler):
- Tam reçete: 64.33.
- Merging olmadan: 62.56. Yani merging yaklaşık +1.8 puan getiriyor; İngilizce MTEB'de (MTEB-Eng) +2.5.
- Sentetik pretraining olmadan: 61.21. Yani ilk aşama yaklaşık +3.1 puan.
- Yalnız sentetik veriyle: 58.49. Yani etiketli gerçek veri de şart.

**Bizim için:** Aynı koşudan birden çok checkpoint'i (ör. farklı seed ya da farklı SQL alt görevleri) birleştirmek, tek bir eğitim koşusunun maliyetine yakın, ölçülebilir bir kazanç veriyor. Zorluk ve persona çeşitlendirmesiyle sentetik soru üretmek de BIRD train'i genişletmenin bir yolu.

## Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning (Qwen Team + Tsinghua LeapLab, Haziran 2025) — [2506.01939](https://arxiv.org/abs/2506.01939)
**Tek cümlede:** RLVR'da asıl işi, modelin kararsız kaldığı az sayıdaki "çatal" token'lar yapıyor; gradient'i yalnızca en kararsız %20 token'a uygulamak büyük modellerde daha iyi sonuç veriyor.

**Problem:** [RLVR](00_terimler.md#rl-ve-rlvr) (reinforcement learning with verifiable rewards: cevabı otomatik doğrulanabilen görevlerde RL) bütün token'ları aynı ağırlıkla günceller. Ama bir reasoning metnindeki token'ların çoğu neredeyse kesindir (ör. bir kelimenin devamı). Yalnızca birkaç token gerçek bir karar noktasıdır (ör. "o hâlde" mi "ama" mı). RL'in hangi token'larda neyi değiştirdiğini anlamak, daha verimli bir eğitim sağlayabilir.

**Ne yaptılar:**
1. **Entropi analizi.** Her token'ın entropisini (modelin o noktada ne kadar kararsız olduğu) ölçtüler. Token'ların %50.64'ünün entropisi 10⁻²'nin (0.01) altında, yani neredeyse kesin. Az sayıda yüksek entropili token, düşüncenin yön değiştirdiği "çatal" noktalarıdır.
2. **Gözlem.** RLVR asıl olarak bu çatal token'ların entropisini değiştiriyor.
3. **Öneri.** Policy gradient'i yalnızca en yüksek entropili %20 token'a uygulamak. Eşik, token entropisinin 80. yüzdelik dilimi (yaklaşık 0.672): bunun üstündeki token'lar eğitilir, altındakiler eğitime girmez.
4. **Eğitim düzeni.** DAPO (GRPO'nun clip-higher ve [dynamic sampling](00_terimler.md#dynamic-sampling) ekleyen bir varyantı; dynamic sampling, bütün cevapları aynı puanı alan soruları batch'ten çıkarıp yerine yenilerini koymak) ve verl (açık kaynak bir RL eğitim kütüphanesi). Veri DAPO-Math-17K (17K matematik sorusu).
5. **Ayarlar.** Batch 512, mini-batch 32 (bir batch'ten 16 gradient adımı), learning rate 1e-6, warmup yok. Cevap en fazla 20,480 token; son 4,096 token'lık bölgeye giren cevaplara uzunluk cezası (overlong shaping). Clip-higher: oran en fazla %28 yukarı (ε_high 0.28), en fazla %20 aşağı (ε_low 0.2) gidebilir; yukarı sınırın geniş olması, az olası ama iyi token'ların olasılığının daha hızlı artmasına izin verir. KL kaybı ve entropi kaybı yok.

**Sonuç:** Yazarların raporuna göre, tüm token'larla eğitime karşı yalnızca top-%20 token'la eğitim:
- Qwen3-32B: AIME'24 55.83 → 63.54 (+7.71), AIME'25 45.63 → 56.67 (+11.04).
- Qwen3-14B: +5.21 / +4.79.
- Qwen3-8B: neredeyse fark yok (+1.25 / +0.83).
- Kazanç model boyu arttıkça büyüyor. Yazarlar 8B'nin kapasitesinin sınırlı olduğunu düşünüyor.
- Ablation: alt %80 token'la (düşük entropili olanlarla) eğitmek performansı belirgin düşürüyor. %10 ya da %100 kullanmak da %20'den kötü.
- Alan dışı LiveCodeBench'te de (eğitim matematikteydi, test kodda) daha iyi.

**Bizim için:** 8B'de bile kazanç yok denecek kadar az olduğu için 0.8B'de entropi maskeleme büyük olasılıkla değmez. Ama entropiyi izlemek ve clip-higher kullanmak ucuz.

## QwenLong-L1: Towards Long-Context Large Reasoning Models with Reinforcement Learning (Tongyi Lab, Alibaba, Mayıs 2025) — [2505.17667](https://arxiv.org/abs/2505.17667)
**Tek cümlede:** Kısa bağlamda öğrenilmiş reasoning'i uzun dokümanlara taşımak için kısa bir warm-up SFT ve giriş uzunluğu aşama aşama artan bir RL.

**Problem:** Reasoning modelleri genelde kısa sorularla eğitilir. Uzun bir dokümanı okuyup üzerinde düşünmek ise ayrı bir beceri. Uzun girdilerle doğrudan RL yapmak kararsız: KL dalgalanıyor, entropi çöküyor. Uzun bağlamlı RL verisi de az.

**Ne yaptılar:**
1. **Base model.** R1-Distill-Qwen-14B ve 32B (DeepSeek-R1'den distill edilmiş Qwen modelleri).
2. **Warm-up SFT.** DeepSeek-R1'den distill edilmiş 5,305 soru-doküman-cevap üçlüsü. 3 epoch, learning rate 5e-6. Amaç RL'e iyi bir başlangıç noktası vermek.
3. **RL verisi.** DocQA-RL-1.6K: 1,591 örnek (doküman üzerinde soru-cevap).
4. **Curriculum.** Phase I'de giriş en fazla 20K, Phase II'de 60K token. Her faz yalnızca kendi uzunluk aralığındaki örneklerle eğitilir.
5. **Difficulty-aware retrospective sampling.** Bir örneğin zorluğu, base modelin o soruya ürettiği cevapların ortalama reward'ının tersidir (ortalama ne kadar düşükse soru o kadar zor). Phase I'de ortalama doğruluğu 0 olan zor örnekler Phase II'ye de taşınır.
6. **Algoritma.** GRPO (KL'siz) ya da DAPO. Batch 128, mini-batch 32, soru başına 8 rollout, learning rate 2e-6, temperature 0.7, cevap en fazla 10K token.
7. **Reward.** İki kontrol: exact match (cevap referansla birebir aynı mı) ve LLM judge (Qwen2.5-1.5B-Instruct). İkisinden hangisi doğru derse cevap doğru sayılır. Format reward'ı yok.

**Sonuç:** Yazarların raporuna göre 7 DocQA (doküman üzerinde soru-cevap) benchmark'ının ortalaması:
- 32B base 65.6; warm-up SFT 68.7; SFT + DAPO 70.7. Karşılaştırma: o3-mini 70.4, Claude-3.7-Sonnet-Thinking 70.7. Yani 32B model bu iki güçlü kapalı modelin seviyesine geliyor.
- Warm-up SFT her ayarda iyileştiriyor.
- Aşamalı RL tek aşamalı RL'den iyi. Tek aşamada KL dalgalanıyor ve entropi çöküyor.
- Retrospective sampling ek kazanç veriyor.
- SFT'nin dozu: uzun bağlamlı 10K örnekle SFT +2.6 puan veriyor, ama üzerine RL yalnızca +0.3 ekliyor. Kısa bağlamlı SFT + RL ise 68.2'ye ulaşıyor. Yani SFT'yi aşırı yapmak RL'in öğrenebileceği alanı daraltıyor.

**Bizim için:** 1.6K RL örneğiyle anlamlı kazanç alınması bizim bütçemize uygun. SFT'yi kısa tutup RL'e yer bırakmak ve soruları kolaydan zora sıralamak (ör. tek tablo → join → nested) doğrudan uygulanabilir.

## WorldPM: Scaling Human Preference Modeling (Qwen Team, Mayıs 2025) — [2505.10527](https://arxiv.org/abs/2505.10527)
**Tek cümlede:** İnsan tercihlerini tahmin eden modellerin (preference model) de dil modelleri gibi veri ve boyutla düzenli iyileşip iyileşmediğini ölçen bir çalışma.

**Problem:** RLHF'de (reinforcement learning from human feedback: insan tercihine göre puan veren bir modelle yapılan RL) puanı bir preference model verir (iki cevaptan insanın hangisini seçeceğini tahmin eden model). Dil modellerinde "daha çok veri ve daha büyük model = daha iyi" kuralı biliniyor. Preference model için bunun geçerli olup olmadığı bilinmiyordu. Geçerliyse, ucuz ve gürültülü veriyle büyük bir reward model kurulabilir.

**Ne yaptılar:**
1. **Veri.** Forumlardan toplanmış yaklaşık 15M preference örneği (ör. bir soruya verilen cevaplardan hangisinin daha çok beğeni aldığı).
2. **Modeller.** 1.5B'den 72B'ye farklı boyutlarda modeller bu veriyle eğitildi.
3. **Fine-tuning.** WorldPM, önce bu büyük ve gürültülü veriyle eğitilip sonra 7K, 100K ve 800K'lık preference veri setlerinde fine-tune ediliyor.
4. **Kullanım.** Qwen'in iç RLHF pipeline'ında reward model olarak kullanılıyor.

**Sonuç:** Yazarların raporuna göre:
- Adversarial metrikler (kandırmaya yönelik cevapları ayırt etme) veri ve model boyuyla düzenli artıyor.
- Objective metrikler (cevabı belli sorular) yalnızca büyük modellerde ortaya çıkıyor (emergent: küçük boylarda hiç yok, bir boydan sonra beliriyor).
- Subjective metriklerde (kişisel zevke bağlı tercihler) ölçekleme eğilimi yok.
- WorldPM'den başlayıp fine-tune etmek, 7 benchmark'ın 20 alt görevinin çoğunda %5'in üzerinde genelleme kazancı veriyor. Kazancın neye göre ölçüldüğü bu dosyada yazmıyor; büyük olasılıkla WorldPM'siz aynı fine-tuning'e göre.
- İç RLHF'de %4–8 kazanç.

**Bizim için:** Cevabı belli görevlerde (SQL gibi) öğrenilmiş bir reward model yerine kural tabanlı ya da execution reward yeterli. Subjective preference'ı ölçeklemek bizim için gereksiz.

## Qwen3 Technical Report (Qwen Team, Mayıs 2025) — [2505.09388](https://arxiv.org/abs/2505.09388)
**Tek cümlede:** Büyük modeller için dört aşamalı post-training, küçük modeller (0.6B–14B ve 30B-A3B) için büyük modelden distillation; küçük model için on-policy distillation'ın RL'den hem iyi hem ucuz olduğunu gösteren en güçlü kanıt.

**Problem:** Bir model ailesinde her boyu ayrı ayrı RL ile eğitmek çok pahalı. Ayrıca kullanıcı bazen hızlı ve kısa (non-thinking), bazen derin düşünen (thinking) bir cevap ister. Qwen3 iki modu tek modelde birleştirdi (thinking mode fusion; bu yaklaşım 2507 güncellemesinde bırakıldı). Asıl soru: küçük modellere en ucuz yoldan büyük modelin reasoning becerisi nasıl aktarılır?

**Ne yaptılar:** Büyük modeller için dört aşama:
1. **Long-CoT cold start.** Qwen2.5-72B-Instruct, doğrulanması zor soruları ve CoT olmadan (düşünmeden) çözülebilen soruları atar. QwQ-32B her soru için N cevap üretir. Yanlış, tekrarlı, tahmine dayalı, dili karışık ya da validation setiyle çakışan cevaplar atılır. Amaç az örnek ve az adımla modeli hazırlamak, RL'in potansiyelini kısıtlamamak.
2. **Reasoning RL.** Yalnızca 3,995 soru-verifier çifti (verifier: cevabın doğru olup olmadığını otomatik kontrol eden kod). Sorular cold start'ta kullanılmamış, cold-start model için öğrenilebilir, olabildiğince zor ve alt alanları geniş kapsayan sorular. Algoritma GRPO; büyük batch, soru başına çok rollout, off-policy eğitim ve entropi kontrolü.
3. **Thinking mode fusion.** 2. aşamanın modelinden [rejection sampling](00_terimler.md#rejection-sampling) ile (çok cevap üretip yalnızca iyi olanları tutmak) thinking verisi, yanına non-thinking verisi konur ve SFT yapılır. Kullanıcı prompt'a `/think` ya da `/no_think` yazarak modu seçer. Örnek: "/no_think 2+2 kaç?" sorusuna model düşünme metni yazmadan "4" der.
4. **General RL.** 20'den fazla görev. Üç tür reward: kural tabanlı, referans cevaplı model tabanlı ve referanssız (bir preference reward model'in puanı).

Küçük modeller için strong-to-weak distillation:
5. **Off-policy distillation.** Büyük modelin iki moddaki hazır çıktılarıyla eğitim.
6. **On-policy distillation.** Eğitilen model kendi cevabını üretir. Bu cevabın her token'ında olasılıkları Qwen3-32B ya da Qwen3-235B-A22B'nin olasılıklarına KL ile yaklaştırılır.

Ayrıca reasoning için mid-training:
7. **Pretraining aşamaları.** S1: 30T'den fazla genel token. S2 "reasoning" aşaması: yaklaşık 5T daha kaliteli token; STEM (fen, teknoloji, mühendislik, matematik), kod, reasoning ve sentetik veri payı artırılmış, learning rate daha hızlı düşürülmüş. S3: 32K bağlamda yüz milyarlarca token. Toplam 36T. Sentetik veriyi (ders kitabı, soru-cevap, talimat, kod) Qwen2.5, Qwen2.5-Math ve Qwen2.5-Coder üretiyor.

**Sonuç:** Yazarların raporuna göre:
- 235B-A22B'de reasoning RL, AIME'24'ü (lise matematik olimpiyatı) 170 RL adımında 70.1'den 85.1'e çıkarıyor.
- Qwen3-8B'de, off-policy distillation sonrasında AIME'24 55.0. Bu noktadan iki ayrı yol karşılaştırılıyor:
  - RL ile: 67.6, 17,920 GPU saati.
  - On-policy distillation ile: 74.4, 1,800 GPU saati. Yani yaklaşık 1/10 maliyetle 6.8 puan daha iyi.
- Pass@64 (64 denemeden en az birinin doğru olması): RL bunu artırmıyor (90.0 → 90.0), on-policy distillation artırıyor (93.3). Bu, RL'in modelin zaten çözebildiği soruları daha sık doğru yaptırdığını, distillation'ın ise çözülebilen soru kümesini genişlettiğini düşündürüyor.
- 3. ve 4. aşamalar ToolUse skorunu 63.3'ten 85.5'e çıkarıyor, ama AIME'24 ve LiveCodeBench'te 1–2 puanlık düşüş getiriyor. Genel beceri ile en yüksek reasoning arasında küçük bir takas var.

**Bizim için:** Küçük model için en güçlü kanıt bu: aynı compute'ta on-policy distillation RL'den hem ucuz hem iyi. RL için de birkaç bin "öğrenilebilir ama zor" soru yeterli.

## QwQ-32B: Embracing the Power of Reinforcement Learning (Qwen Team, Mart 2025) — [blog](https://qwenlm.github.io/blog/qwq-32b/)
**Tek cümlede:** 32B'lik dense bir modeli, cold-start checkpoint'inden başlayıp RL'i ölçekleyerek DeepSeek-R1 (671B) ile yarışır hâle getirdiler.

**Problem:** Güçlü reasoning için genelde çok büyük modeller gerekir. Soru şu: RL'i ölçeklemek, toplam parametresi yaklaşık 20 kat küçük bir modeli bu seviyeye çıkarabilir mi?

**Ne yaptılar:**
1. **Başlangıç.** Bir cold-start checkpoint'i.
2. **RL aşama 1: yalnızca matematik ve kod.** Öğrenilmiş bir reward model yerine outcome-based reward (yalnızca sonuca bakan puan). Matematikte final cevabı kontrol eden bir accuracy verifier. Kodda, üretilen kodu test case'lerle çalıştıran bir code execution server.
3. **RL aşama 2: kısa bir genel RL.** Genel bir reward model ve kural tabanlı verifier'lar birlikte.
4. Adım sayıları ve veri boyutu verilmemiş.

**Sonuç:** Yazarların raporuna göre RL ilerledikçe matematik ve kodda performans sürekli artıyor. Aşama 2, talimat takibini, insan tercihine uyumu ve agent performansını, matematik ve kodda belirgin bir düşüş olmadan iyileştiriyor. Rakamlar yalnızca grafikte.

**Kaynak notu:** Yalnızca blog; rakamlar metinde değil grafikte, veri boyutu ve adım sayısı yok.

**Bizim için:** Önce doğrulanabilir görevde (SQL doğruluğu) RL, sonra kısa bir "biçim / tool kullanımı" aşaması sırası küçük modele de uyar.

## START: Self-taught Reasoner with Tools (Alibaba Group + USTC, Mart 2025) — [2503.04625](https://arxiv.org/abs/2503.04625)
**Tek cümlede:** Uzun düşünen bir modele hiç örnek göstermeden Python tool'u kullanmayı öğrettiler: düşünmenin ortasına "burada Python kullanmak iyi olabilir" ipucu eklediler ve işe yarayan denemelerle fine-tune ettiler.

**Problem:** Long-CoT modeller hesap hatası yapar ve kendi hesabını kontrol edemez. Python gibi bir tool bunu çözer. Ama modele tool kullanmayı öğretmek için genelde insanların hazırladığı tool'lu örnekler gerekir; bu tür veri az ve pahalı. Model kendi başına tool çağırmayı da akıl etmez.

**Ne yaptılar:**
1. **Hint-infer.** QwQ-32B-Preview düşünürken, düşüncenin ortasına "Wait, maybe using Python here is a good idea." gibi ipuçları eklenir. Model bu ipucunu görünce Python kodu yazar, kod çalıştırılır, sonuç modele geri verilir.
2. **Soru havuzu.** 49,969 soru (yaklaşık 40K matematik, yaklaşık 10K kod); test sorularıyla çakışanlar temizlenmiş (decontamination).
3. **Tohum veri (active learning).** Modelin tool olmadan çözemeyip ipucuyla çözdüğü sorular seçilir: 10K matematik ve 2K kod. Bu, modelin tam da tool sayesinde öğreneceği sorulardır.
4. **Hint-RFT.** RFT (rejection sampling fine-tuning): çok deneme üret, doğru olanları tut, onlarla SFT yap. Tohum veriyle yapılan bu eğitim START-0 modelini verir.
5. **İkinci tur.** START-0 her soru için 16 cevap üretir (temperature 0.6). Soru başına en fazla bir doğru cevap tutulur. Puanlama kural tabanlı, tekrarlı cevaplar atılır. Bu veriyle son model eğitilir. Bu "üret, iyileri seç, onlarla eğit" döngüsü [expert iteration](00_terimler.md#expert-iteration)'a benzer.
6. **Ayarlar.** Learning rate 7e-6, batch 128, 3 epoch, 16,384 token bağlam, cevap başına en fazla 6 tool çağrısı.

**Sonuç:** Yazarların raporuna göre QwQ-32B-Preview'dan START'a:
- AIME24 50.0 → 66.7; AIME25 40.0 → 47.1 (lise matematik olimpiyatı).
- AMC23 (Amerikan lise matematik yarışması) 80.0 → 95.0.
- LiveCodeBench 41.4 → 47.3.
- Ablation: aynı sorularla tool'suz RFT neredeyse kazanç vermiyor (AIME24 53.3, AIME25 33.3; AIME25'te base'in bile altında). Yani kazanç fine-tuning'den değil, tool kullanımından geliyor.

**Bizim için:** "Modelin tek başına çözemediği ama tool'la çözdüğü" soruları seçip soru başına bir doğru trajectory tutmak, experience log'dan SFT verisi seçmek için doğrudan bir kural.

## The Lessons of Developing Process Reward Models in Mathematical Reasoning (Qwen Team, Ocak 2025) — [2501.07301](https://arxiv.org/abs/2501.07301)
**Tek cümlede:** Matematikte her adımı puanlayan reward model'lerinin (PRM) eğitim verisinin nasıl üretilmesi gerektiğini incelediler ve Qwen2.5-Math-PRM modellerini yayımladılar.

**Problem:** PRM (process reward model), yalnızca son cevabı değil, çözümün her adımını puanlar. Böylece doğru cevaba yanlış yoldan ulaşan çözümler yakalanabilir. Ama PRM eğitmek için her adımın doğru mu yanlış mı olduğunu söyleyen etiketler gerekir. İnsanla etiketlemek pahalı; otomatik yöntemlerin ne kadar güvenilir olduğu belirsiz.

**Ne yaptılar:**
1. **Üç etiketleme yöntemini karşılaştırdılar.**
   - Monte Carlo (MC) tahmini: bir adımdan sonra çözüme başka bir modelle birkaç kez devam edilir; kaçının doğru cevaba çıktığına bakılır. Örnek: 3. adımdan 8 kez devam edildi, 6'sı doğru çıktı; o adımın puanı 0.75.
   - LLM-as-judge: güçlü bir model her adımı okuyup doğru mu yanlış mı der.
   - İnsan etiketi.
2. **Consensus filtering.** MC tahmini ile LLM judge'ın aynı fikirde olduğu adımlar tutulur, anlaşmadıkları atılır.
3. **Değerlendirmeyi incelediler.** Best-of-N (N çözüm üret, PRM'in en yüksek puan verdiğini seç) ile yapılan PRM değerlendirmesinin ne kadar güvenilir olduğuna baktılar.

**Sonuç:** Yazarların raporuna göre:
- MC tahmini hem LLM-as-judge'dan hem insan etiketinden daha kötü ve daha az genelleniyor.
- Best-of-N değerlendirmesi yanıltıcı. Yanlış reasoning'le doğru cevaba ulaşan çözümler PRM tarafından kabul edildiği için skorlar şişiyor.
- Birçok PRM en düşük skoru final cevap adımına veriyor. Yani pratikte adımları değil, yalnızca sonucu kontrol eden bir outcome checker gibi davranıyor.
- Consensus filtering veri verimliliğini artırıyor: daha az veriyle daha iyi PRM.
- Bu dosyada rakam verilmemiş.

**Bizim için:** Adım bazlı reward için ayrı bir PRM eğitmek yerine, iki bağımsız sinyalin (execution sonucu ve large model kontrolü) uyuştuğu trajectory'leri tutmak daha güvenilir ve ucuz.

## Qwen2.5 Technical Report (Qwen Team, Aralık 2024) — [2412.15115](https://arxiv.org/abs/2412.15115)
**Tek cümlede:** Qwen2.5 ailesinin (0.5B–72B) raporu; post-training büyük bir SFT, ardından offline (DPO) ve online (GRPO) RL.

**Problem:** Bir model ailesini birçok beceride (uzun metin, matematik, kod, talimat takibi, yapılandırılmış veri, çok dillilik) aynı anda iyi yapmak. Bunun için hem çok çeşitli SFT verisi hem de insan tercihine uyumu artıran bir RL gerekir. Eğitim verisinin test sorularıyla çakışmaması da şart.

**Ne yaptılar:**
1. **SFT.** 1 milyonun üzerinde örnek: uzun üretim, matematik, kod, talimat takibi, yapılandırılmış veri (tablo, JSON), mantık, diller arası transfer ve sistem talimatları. Matematikte reward model ve etiketli cevaplarla rejection sampling. Kodda çok dilli bir sandbox'ta statik kontrol ve unit test. 2 epoch, 32,768 token bağlam, learning rate 7×10⁻⁶'dan 7×10⁻⁷'ye düşürülür.
2. **Offline RL (DPO).** SFT modelinden aynı sorulara yeniden cevap üretilir. Kalite kontrolünü geçen cevap "iyi", geçemeyen "kötü" olarak eşleştirilir. Yaklaşık 150,000 DPO çifti, 1 epoch. "Offline" çünkü cevaplar eğitim başlamadan bir kez üretilir.
3. **Online RL (GRPO).** Reward model'in baktığı ölçütler: doğruluk, yardımseverlik, kısalık, ilgililik, zararsızlık ve önyargısızlık. Soru başına 8 cevap, global batch 2048. Reward skorlarının varyansı yüksek olan sorular önce işlenir; yani 8 cevabın puanlarının birbirinden çok farklı olduğu, modelin kararsız kaldığı sorular.
4. **Decontamination.** Bir test örneğiyle en az 13 token'lık ortak bir alt dizi paylaşan ve bu ortak dizinin uzunluğu kısa olan metnin en az 0.6 katı olan eğitim örnekleri atılır.

**Sonuç:** Yazarların raporuna göre post-training aşamaları için ayrı bir ablation yok. Hangi aşamanın ne kadar katkı verdiği bilinmiyor.

**Bizim için:** "Reward varyansı yüksek soruları önce işle" ilkesi (hepsi doğru ya da hepsi yanlış olmayan sorular), GRPO'da sinyal veren soruları seçmenin en basit hâli. Test sorularıyla n-gram (ardışık token dizisi) çakışmasını temizlemek BIRD dev için de gerekli.

## Marco-o1: Towards Open Reasoning Models for Open-Ended Solutions (MarcoPolo Team, Alibaba International Digital Commerce, Kasım 2024) — [2411.14405](https://arxiv.org/abs/2411.14405)
**Tek cümlede:** Qwen2-7B-Instruct'a CoT fine-tuning, ağaç aramasıyla (MCTS) üretilmiş reasoning verisi ve bir "yeniden düşün" ifadesiyle o1 tarzı reasoning kazandırma denemesi.

**Problem:** OpenAI o1 gibi uzun düşünen modellerin nasıl eğitildiği açık değildi. Açık bir 7B modele benzer bir reasoning kazandırmak istendi. Ayrı bir reward model eğitmeden, modelin kendi token olasılıklarını puan olarak kullanmak denendi.

**Ne yaptılar:**
1. **SFT verisi (toplam 60,266 örnek).** Filtrelenmiş Open-O1 CoT verisi 45,125; MCTS ile üretilmiş sentetik Marco-o1 CoT verisi 10,000; talimat verisi 5,141.
2. **MCTS ile veri üretimi.** MCTS (Monte Carlo Tree Search), olası adımlardan bir ağaç kurup en umut verici dalları daha çok deneyen bir arama yöntemi. Burada her düğüm bir reasoning durumu. Bir hamle (action) ya tam bir adım ya da 64 veya 32 token'lık bir mini-adım.
3. **Reward olarak güven.** Bir dalın puanı, o daldaki token güvenlerinin ortalaması. Bir token'ın güveni, olasılığının o noktadaki en olası 5 alternatife göre softmax ile hesaplanmış payı. Yani model kendi seçtiği token'lardan ne kadar emin olduysa dal o kadar iyi sayılır.
4. **Reflection.** Her düşüncenin sonuna "Wait! Maybe I made some mistakes! I need to rethink from scratch." eklenir; model kendi çözümünü yeniden gözden geçirir.

**Sonuç:** Yazarların raporuna göre MGSM (çok dilli ilkokul matematik problemleri; En İngilizce, Zh Çince) Test@1 (ilk denemede doğruluk):
- Qwen2-7B-Instruct: En 84.00 / Zh 76.80.
- Marco-o1-CoT (yalnız CoT fine-tuning): 85.60 / 71.20. İngilizcede küçük artış, Çincede düşüş.
- MCTS, adım düzeyinde: 90.40 / 80.00.
- MCTS, 32 token'lık mini-adım: 87.60 / 82.40.
- Hamle boyunda açık bir kazanan yok.
- Test@8 ve Test@32'de (8 ya da 32 denemeden en az biri doğru) fark kapanıyor; CoT modeli İngilizcede 97.60 / 99.20'ye çıkıyor. Yani MCTS'nin üstünlüğü yalnızca Test@1'de.
- Reflection'ın zor soruların yaklaşık yarısını düzelttiği söyleniyor, ama tablo yok.

**Bizim için:** Modelin kendi güveniyle arama yapmak bizim için zayıf bir sinyal; SQL'de execution sonucu çok daha sağlam bir reward. Pass@k'da farkın kapanması da kazancın aramadan değil, iyi örnek seçmekten geldiğini düşündürüyor.
