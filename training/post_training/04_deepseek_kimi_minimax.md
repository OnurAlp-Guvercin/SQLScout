# DeepSeek, Moonshot (Kimi), MiniMax

**Bu bölümde ne var:** Üç Çin laboratuvarının (DeepSeek, Moonshot AI ve MiniMax) Aralık 2024 ile Temmuz 2026 arasındaki post-training raporları. Post-training, ön-eğitimi bitmiş bir modeli [SFT](00_terimler.md#sft) (hazır örnek cevaplarla eğitme) ve [RL](00_terimler.md#rl-ve-rlvr) (modelin kendi denemelerini puanlayarak eğitme) ile kullanışlı hâle getirme aşamasıdır. Makaleler yeniden eskiye sıralı; her biri ne yaptığını, neden yaptığını ve sonuçlarını anlatır.

**Bu bölümün ana dersleri:**
- Küçük bir model için en ucuz ve en etkili adım, güçlü bir modelin doğru çözümleriyle SFT'dir ([distillation](00_terimler.md#distillation)); RL bundan sonra ek kazanç için gelir (DeepSeek-R1, Prover-V2).
- RL için soru seçimi en ucuz kazançtır: model bir soruyu ya hep çözüyorsa ya da hiç çözemiyorsa o soru RL'de bir şey öğretmez, bu yüzden atılır (M1, V3.2, Kimi-Dev, k1.5).
- Büyük laboratuvarlar önce her alan için ayrı uzman modeller eğitiyor, sonra bunları tek modele birleştiriyor (K3, V4, V3.2).
- Agent RL'inde reward üç parçalı olmaya başladı: görev doğru mu, biçim hatası var mı, kaç adımda ya da ne kadar sürede bitti (M2, Forge, Kimi-Researcher).
- Üretim ([rollout](00_terimler.md#rollout): modelin bir denemesi) ile eğitim aynı olasılıkları görmezse RL kararsızlaşır; birçok rapor bu farkı kapatmak için ayrı önlem alıyor (M1, V3.2, K2 Thinking).

**Makaleler:**
- Kimi K3 — dokuz uzman modelin tek modele birleştirildiği 2.8T'lik model.
- The MiniMax-M2 Series — agent odaklı post-training hattı ve CISPO ile RL.
- DeepSeek-V4 — karma RL yerine tamamen on-policy distillation.
- Forge / MiniMax-M2.5 — ölçekli agent RL'i için eğitim altyapısı (yalnızca blog).
- Kimi K2.5 — görsel agent modeli, kısa düşünmeyi öğreten Toggle ve paralel alt agent'lar.
- DeepSeek-V3.2 — büyük RL bütçesi ve sentetik agent görevleri.
- DeepSeekMath-V2 — kendi ispatını denetleyebilen matematik modeli.
- Kimi K2 Thinking — yüzlerce tool call'u art arda yürüten thinking agent (yalnızca blog).
- Kimi-Dev — sabit iş akışlı eğitimin SWE agent'ları için ön beceri olması.
- DeepSeek-R1 (Nature) — R1'in hakemli sürümü ve ilk kez açıklanan hiperparametreler.
- Kimi K2 — sentetik tool verisi ve doğrulanabilir + doğrulanamaz reward'lı RL.
- Kimi-Researcher — uçtan uca RL ile eğitilmiş deep research agent'ı (yalnızca blog).
- MiniMax-M1 — CISPO algoritmasının ilk tanıtıldığı reasoning modeli.
- DeepSeek-Prover-V2 — Lean 4'te formel ispat; büyük modelden küçüğe aktarım.
- Inference-Time Scaling for Generalist Reward Modeling — kendi ilkelerini yazan reward model.
- DeepSeek-R1 — SFT'siz RL ile ortaya çıkan akıl yürütme ve küçük modellere distillation.
- Kimi k1.5 — value function'sız RL ve uzun düşünmeyi kısaltma yöntemleri.
- DeepSeek-V3 — R1'den distillation'lı SFT ve GRPO ile RL.

---

## Kimi K3: Open Frontier Intelligence (Moonshot AI, Temmuz 2026) — [tech report (GitHub)](https://github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf)
**Tek cümlede:** Her alan ve her "düşünme miktarı" için ayrı bir uzman model RL ile eğitilir, sonra dokuz uzman tek bir modelde birleştirilir.

**Problem:** Tek bir modeli aynı anda kodlamada, araştırmada ve yazımda iyi yapmak zordur; bir alana yapılan RL başka bir alanı bozabilir. Ayrıca kullanıcı bazen hızlı ve kısa bir cevap, bazen uzun ve derin bir düşünme ister. Model ne kadar düşüneceğini bu isteğe göre ayarlayabilmelidir.

**Ne yaptılar:**
1. **Model.** 2.8T parametreli bir [MoE](00_terimler.md#moe) (Mixture of Experts: her token için parametrelerin yalnızca bir kısmı çalışır; burada 104B'si). Bağlam 1M token. Native multimodal, yani görsel ve metni baştan birlikte işler.
2. **SFT ile [cold start](00_terimler.md#cold-start).** Cold start, RL'den önce modele temel davranışı öğreten kısa bir SFT'dir. Veri, önceki Kimi serisinin alan uzmanı modellerinin ürettiği trajectory'lerden sentezlenir (trajectory: bir görevi çözerken yazılan düşünce, tool call ve sonuçların tamamı). Veri çok aşamalı doğrulamadan ve insanların da etiketlediği (human-in-the-loop) bir süzgeçten geçer.
3. **Quantization-aware training (QAT).** Model, eğitim sırasında da düşük hassasiyetli sayılarla çalışıyormuş gibi eğitilir; böylece sonradan sıkıştırılınca bozulmaz. Ağırlıklar MXFP4 (4 bitlik sayı biçimi), aktivasyonlar MXFP8 (8 bit). Bu SFT'den itibaren uygulanır.
4. **Dokuz uzman model.** RL üç geniş alanda yapılır: genel görevler; genel agent'lar (uzun ufuklu asistan, deep research, yazım); coding agent'lar (SWE yani yazılım mühendisliği görevleri, kernel yazımı, web geliştirme). Her alan üç effort seviyesiyle (low, high, max) çaprazlanır: 3 × 3 = 9 uzman.
5. **RL algoritması (K2.5'ten).** Her prompt için K rollout örneklenir. Partial rollout kullanılır: rollout'ların belli bir oranı (λ) bitince üretim durur, bitmeyenler sonraki iterasyonda kaldığı yerden sürer. Böylece en yavaş birkaç rollout herkesi bekletmez. Bu yarım kalan rollout'lar modelin biraz eski bir hâlinden geldiği için "bayat"tır; etkisini azaltmak için token başına bir düzenlileştirme (regularization) eklenir.
6. **Effort seviyesini öğreten RL.** Her probleme bir token budget'ı verilir. Budget, cold-start modelinin o problemde ne kadar uzun yazdığından tahmin edilir. Bu budget'ın τ katını aşan trajectory'nin [reward](00_terimler.md#reward)'ı −1 olur. Örnek olarak: cold-start modeli bir soruda 2.000 token yazıyorsa ve τ = 2 ise, 4.000 token'ı geçen her cevap −1 alır. Önce büyük τ ile max uzmanı eğitilir, sonra τ küçültülerek high ve low uzmanları. Bu aşamalı bir [curriculum](00_terimler.md#curriculum)'dur (kolay koşuldan zor koşula doğru sıralı eğitim).
7. **Doğrulanamayan görevlerde reward.** Doğru cevabı otomatik kontrol edilemeyen görevlerde (ör. yazım) Agentic Generative Reward Model kullanılır ([GRM](00_terimler.md#reward-model-grm-ve-prm): puanı gerekçesiyle metin olarak yazan reward model). Adaylar turnuva gibi ikişer ikişer karşılaştırılır. Judge önce bir [rubric](00_terimler.md#llm-as-judge-ve-rubric) (puanlama ölçütleri listesi) yazar, sonra adayları puanlar. Uzunluk sınırını aşan aday karşılaştırmayı otomatik kaybeder. Bu, "daha uzun yazan kazanır" türünden bir [reward hacking](00_terimler.md#reward-hacking)'i (modelin reward'ı görevi yapmadan şişirmesi) engeller.
8. **Uzmanları birleştirme: [MOPD](00_terimler.md#multi-teacher-distillation-mopd).** MOPD (Multi-Teacher On-Policy Distillation), birden çok uzmanın bilgisini tek modele aktarır. Eğitilen model kendi cevabını üretir. Her token'ın reward'ı şudur: o token'a uzmanın verdiği olasılık, eğitilen modelin verdiğinden ne kadar büyükse o kadar pozitif, küçükse o kadar negatif (log-olasılık oranı). Bu sayı sabit bir reward olarak alınır (stop-gradient) ve [−Rmax, Rmax] aralığına kırpılır, yani aşırı uçlar sınırlanır. Uzmanın en olası k token'ını da hedef olarak vermek (daha ince top-k distillation) belirgin fayda göstermemiş.
9. **RL görevlerinin üretimi.** Üç kaynak var. Birincisi knowledge-graph rehberli sentez: agent'lar web'de hiyerarşik bir kavram grafiği genişletir; buradan anahtar kelime örneklenip kaynak bulunur ve görev yazılır. İkincisi "white-box" ortamlar: Kimi Code, Claude Code, Codex gibi farklı harness'ları taklit eder, böylece model tek bir tool biçimine alışmaz. Üçüncüsü Autonomous Execution Tasks: sonucu bağımsız bir verifier'ın kontrol ettiği görevler.

**Sonuç:** Yazarların raporuna göre RL'e harcanan hesaplama (FLOPs) arttıkça modelin tool call adım sayısı ile bilgi, akıl yürütme, görsel, agent ve kodlama skorları birlikte artar (Figure 8). Max effort'ta skorlar şöyle: Terminal-Bench 2.1 88.3 (terminalde gerçek görevleri bitirme), BrowseComp 91.2 (web'de zor bulunan bilgiyi bulma), DeepSWE 67.5 ve SWE-Marathon 42.0 (kodlama agent görevleri), GPQA Diamond 93.5 (aramayla bulunamayan doktora düzeyi fen soruları). Bu dosyada bu rakamlar için önceki bir modelin skoru yok; yazarlar modelin en güçlü kapalı modellerin (Claude Fable 5, GPT-5.6 Sol) gerisinde kaldığını kendileri belirtir. Benchmark'ların ortak listesi için bkz. [benchmarklar](00_terimler.md#benchmarklar).

**Bizim için:** Budget'ı her soru için cold-start modelinin cevap uzunluğundan türetip aşanı −1 ile cezalandırmak, 10 tool call'luk budget'lı SQL agent'ımıza doğrudan taşınabilir. Tek bir harness'a overfit etmemek için prompt ve tool biçimini çeşitlendirmek de aynı şekilde uygulanabilir.

## The MiniMax-M2 Series: Mini Activations Unleashing Max Real-World Intelligence (MiniMax, Mayıs 2026) — [2605.26494](https://arxiv.org/abs/2605.26494)
**Tek cümlede:** Az aktif parametreli M2 ailesinin agent odaklı post-training hattı: doğrulanabilir agent verisi, Forge adlı RL sistemi ve CISPO algoritması.

**Problem:** Gerçek dünyadaki agent görevleri (kod düzeltme, terminal, web araması) uzun ve çok adımlıdır. Böyle görevlerde hem doğru trajectory verisi bulmak hem de RL'i kararlı yürütmek zordur. MiniMax bunu az aktif parametreyle, yani ucuz çalışan bir modelle yapmak istiyor.

**Ne yaptılar:**
1. **Model ailesi.** Toplam 229.9B, aktif 9.8B parametre. Sürümler M2 → M2.5 → M2.7. M2.7'de model kendi eğitim koşularını ve scaffold'unu (etrafındaki agent kodunu) düzenleyen erken bir "self-evolution" yapar.
2. **SFT, interleaved thinking ile.** Düşünce, eylem (tool call) ve gözlem (tool sonucu) tek bir trajectory'de iç içe yazılır. Veri, alana özgü reward sinyallerine karşı büyük ölçekli [rejection sampling](00_terimler.md#rejection-sampling) ile kurulur: çok aday üretilir, yalnızca iyi puan alanlar tutulur. Sonra çok aşamalı temizlikten geçer. Alanlar: chat, reasoning, code ve cowork; tek turlu ve çok turlu agent verisi.
3. **RL algoritması: CISPO.** Önce [importance sampling](00_terimler.md#importance-sampling) gerekiyor: veri modelin biraz eski hâliyle üretildiği için, her token'ın katkısı "yeni modelin olasılığı / eski modelin olasılığı" oranıyla (importance ratio) düzeltilir. [PPO](00_terimler.md#ppo) tarzı [clip](00_terimler.md#clip-ve-clip-higher) bu oran belli bir aralığın dışına çıkınca o token'ın gradient'ini tamamen sıfırlar. CISPO token'ı atmaz; yalnızca oranın kendisini yukarıdan (1 + ε_high'ta) kırpar ve bu ağırlığı sabit sayar (stop-gradient). Örnek: nadir bir "Bekle, tekrar bakayım" token'ının oranı 1.5'e çıktıysa PPO onu öğrenmeden çıkarır; CISPO onu tutar, ağırlığını üst sınıra indirir. [Advantage](00_terimler.md#advantage) (bir eylemin ortalamadan ne kadar iyi olduğu) şöyle hesaplanır: o adımdan sonra gelen reward'ların toplamı (reward-to-go) eksi trajectory düzeyinde bir baseline. Bağlam 192K token'a kadar.
4. **Karışık alanlı RL ve curriculum.** Her aşamada reasoning, coding, agent ve genel veri birlikte örneklenir. Erken aşamalar reasoning ve genel veriye, sonrakiler agent ve kodlamaya ağırlık verir. Bağlam her alan için aşamalarla uzatılır. Zorluk geniş bir karışımdan zor görevlere kayar.
5. **Reward üç parça.** Process reward: dil karışması ve tool call biçim hatası cezası, ağırlıklı olarak. Hız reward'ı: görevin bir baseline'a göre ne kadar sürede bittiği; bu paralel tool kullanımını teşvik eder. Performans reward'ı: görev başarısı. SWE görevlerinde başarı testlerle ölçülür: F2P (fail-to-pass, önceden kırık olup düzelmesi gereken testler) ve P2P (pass-to-pass, önceden geçen ve geçmeye devam etmesi gereken testler). Uygulama geliştirmede (AppDev) rubric'le çalışan bir agent doğrulayıcı (Agent-as-a-Verifier) kullanılır.
6. **Terminal-Gym ile zorluk ayarı.** Görevin zorluğu, bir referans çözücünün o görevdeki geçmiş [pass rate](00_terimler.md#pass-rate-ve-passk)'iyle (denemelerin yüzde kaçının başarılı olduğu) ölçülür. İlk denemede (sıfır-atış) pass rate'i düşük olan zor varyantlar tutulur.

**Sonuç:** Yazarların raporuna göre M2.5'ten M2.7'ye skorlar artar: SWE-bench Pro 55.4 → 56.2 (gerçek GitHub hatalarını düzeltme, zor sürüm), Terminal-Bench 2.0 51.7 → 57.0, BrowseComp 76.3 → 77.8, Toolathlon 38.3 → 46.3 (çok tool'lu uzun görevler; en büyük artış, yaklaşık 8 puan), AIME 2026 87.2 → 94.2 (lise matematik olimpiyatı soruları). İki ablation var. Birincisi, önceki turların düşüncesini bağlamdan atmak performansı düşürür; en çok deep search ve SWE'de. İkincisi, SFT'de full attention, hibrit SWA'ya (sliding window attention: her token yalnızca yakınındaki token'lara bakar) göre SWE-bench Verified'da 54.7'ye 50.2 verir, yani tam dikkat 4.5 puan daha iyi. M2.7'nin 100 turluk otonom kendini geliştirme döngüsü iç değerlendirmede %30 kazanç bildirir.

**Bizim için:** Önceki tool call'ların düşüncesini konuşmada tutmak ve reward'a biçim hatası cezası eklemek ucuz ve yararlı. "Referans çözücünün pass rate'iyle zorluk ayarı", BIRD train sorularını small model'in pass rate'ine göre seçmenin aynısı.

## DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence (DeepSeek-AI, Nisan 2026) — [2606.19348](https://arxiv.org/abs/2606.19348)
**Tek cümlede:** Önce her alan için ayrı uzmanlar SFT ve RL ile eğitilir, sonra hepsi tek modele [on-policy distillation](00_terimler.md#on-policy-distillation-opd) ile aktarılır; V3.2'deki karma RL aşaması tamamen kalkar.

**Problem:** V3.2'de bütün alanlar tek bir karma RL aşamasında birlikte eğitiliyordu. Farklı alanların reward'ları birbirini etkiler ve bu aşama pahalıdır. V4, uzmanların bilgisini tek modele RL yerine daha doğrudan bir yolla aktarmayı dener.

**Ne yaptılar:**
1. **Modeller.** V4-Pro: 1.6T parametre, 49B aktif. V4-Flash: 284B, 13B aktif. Bağlam 1M token.
2. **Aşama 1, uzman eğitimi.** Her alan uzmanı (matematik, kodlama, agent, instruction following) kendi alanının yüksek kaliteli verisiyle SFT görür. Ardından [GRPO](00_terimler.md#grpo) ile RL yapılır. GRPO, aynı soruya birkaç cevap üretip her cevabı grubun ortalamasıyla karşılaştıran bir RL algoritmasıdır; ayrı bir value modeli gerekmez. Hiperparametreler yalnızca "önceki çalışmalarla uyumlu" diye anılır, değer verilmez.
3. **Üç reasoning modu.** Non-think, Think High ve Think Max ayrı RL ayarlarından çıkar. Farkları length penalty (uzun cevaba ceza) ve bağlam penceresidir. [Thinking mode](00_terimler.md#thinking-mode) ile ilgili genel açıklama sözlükte.
4. **Reward.** Doğrulanabilir görevlerde kural tabanlı verifier ya da testler kullanılır. Doğrulaması zor görevlerde tek sayı veren bir reward model yerine rubric'li bir GRM kullanılır. GRM'in kendisi de RL ile eğitilir: eğitilen model (actor) aynı zamanda GRM işini de görür. Bunun için az sayıda insan etiketi yeter.
5. **Aşama 2, OPD.** Ondan fazla uzman tek modele aktarılır. Trajectory'leri eğitilen modelin kendisi üretir (on-policy). Kayıp şudur: eğitilen modelin dağılımı her uzmanın dağılımından ne kadar farklı (reverse [KL](00_terimler.md#kl-penalty)); bu farklar her uzmanın ağırlığıyla çarpılıp toplanır ve küçültülür. Reverse KL, farkı eğitilen modelin kendi ürettiği metin üzerinde ölçer. Fark yalnızca seçilen token'ın olasılığından tahmin edilince sonuç çok oynak (yüksek varyanslı) çıktığı için, her pozisyonda bütün sözlüğün (vocabulary) olasılıkları karşılaştırılır (tam vocabulary logit distillation).
6. **Agent RL ortamı: DSec sandbox.** Gerçek araçlarla çalışır: function call, container, microVM ve tam sanal makine; yüz binlerce örnek aynı anda koşar. Tool çağrısı varken düşünce turlar arasında korunur.

**Sonuç:** Yazarların raporuna göre V4-Pro Max'in skorları: SWE Verified 80.6 (gerçek GitHub hatalarını düzeltme), Terminal Bench 2.0 67.9, Codeforces 3206 (yarışma programlama puanı), HLE 37.7 (Humanity's Last Exam: uzmanların yazdığı çok zor sorular), LiveCodeBench 93.5 (yeni çıkmış yarışma programlama soruları). Düşünme miktarı arttıkça (Non-think → High → Max) bütün zor görevlerde skor artar; ör. Pro'da HLE 7.7 → 34.5 → 37.7. Yani düşünmeyi açmak HLE'de skoru dört katından fazla artırır, Max ise High'a az ekler. 30 görevlik iç kodlama değerlendirmesinde V4 %67 alır; Sonnet 4.5 %47, Opus 4.5 %70. OPD için ablation raporlanmamış, yani OPD'nin karma RL'den ne kadar iyi olduğu ölçülmemiş.

**Bizim için:** "Önce ayrı uzmanlar, sonra on-policy distillation" yaklaşımı, small model'i large model'in (9B) logit'lerine karşı kendi rollout'ları üzerinde eğitmeye karşılık gelir. Tam vocabulary distillation iki modelin aynı tokenizer'ı kullanmasını gerektirir; Qwen3.5 0.8B ve 9B için bu sağlanıyor.

## Forge: Scalable Agent RL Framework and Algorithm / MiniMax-M2.5 (MiniMax, Şubat 2026) — [blog](https://www.minimax.io/blog/forge-scalable-agent-rl-en-1779896141)
**Tek cümlede:** MiniMax'in M2.5'i eğittiği RL sistemi Forge; amaç, herhangi bir agent scaffold'uyla büyük ölçekte RL yapabilmek.

**Problem:** Gerçek agent'lar çok farklı scaffold'larla (modelin etrafındaki agent kodu) ve binlerce farklı tool biçimiyle çalışır. RL sistemi bunların her birine uyum sağlamalı. Ayrıca agent görevlerinin süresi çok değişkendir: kolay görev birkaç saniyede, zor görev saatler içinde biter. Sistem yalnızca önce bitenlerle eğitirse model kolay görevlere kayar. [M2.5 duyurusuna](https://www.minimax.io/blog/minimax-m25) göre M2, M2.1 ve M2.5 yaklaşık üç buçuk ayda çıktı ve ana itici güç RL ölçeklemesiydi.

**Ne yaptılar:**
1. **Mimari üç katman.** Agent tarafı: white-box (içi görülen) ve black-box (yalnızca girdisi ve çıktısı görülen) scaffold'lar; bu taraf yalnızca trajectory üretir. Ara katman: bir gateway ve bir data pool. Altta rollout ve train motorları.
2. **Algoritma: uzun ufuklu agent'lara uyarlanmış CISPO** (ayrıntısı MiniMax-M2 ve M1 girişlerinde). Importance ratio 0 ile 1 + ε_high arasına kırpılır. Her token'ın advantage'ı, o token'dan sonra gelen hız ve performans reward'larının toplamı eksi bir baseline'dır. Yani bir adım, ondan sonra olanların puanını alır.
3. **Tek koşuda karışık eğitim.** Reasoning, genel soru-cevap ve agent görevleri ardışık aşamalar yerine aynı koşuda birlikte eğitilir.
4. **Reward üç parça.** Process reward: dil karışması ve tool çağırma hatası cezası. Süre reward'ı: görevi tamamlama süresi; paralel tool kullanımını teşvik eder. Reward-to-go normalizasyonu: uzun görevlerde reward seyrek gelir (yalnızca sonda), bu da gradient'i çok oynak yapar; normalizasyon bu oynaklığı (varyansı) azaltır. Blog normalizasyonun tam formülünü vermiyor.
5. **Ölçek.** 100.000'den fazla gerçek scaffold ve ortam, binlerce tool çağırma biçimi, günde milyonlar mertebesinde örnek, 200K token'a kadar bağlam.
6. **Windowed FIFO scheduling.** Üretilen N trajectory bir kuyruğa dizilir. Eğitim yalnızca kuyruğun başındaki W tanesinin (ör. W = 0.3N) içinden, bitmiş olanları alabilir. Pencerenin dışında bitmiş bir trajectory olsa bile beklemek zorundadır. Pencere ancak kuyruğun başındaki trajectory alınınca bir adım ilerler. Böylece yavaş ve uzun görevler beklenir, eğitim verisi kolay ve hızlı biten örneklere kaymaz.
7. **Prefix tree ile birleştirme.** Agent trajectory'lerinin başı (sistem prompt'u, görev, ilk adımlar) çoğu zaman aynıdır. Bu ortak başlangıçlı trajectory'ler tek bir ağaçta birleştirilir; ortak kısım bir kez hesaplanır. İleri geçişten sonra ağaç yeniden açılır ve kayıp normal şekilde hesaplanır.

**Sonuç:** Yazarların raporuna göre prefix tree birleştirmesi, kaybı matematiksel olarak hiç değiştirmeden eğitimi 40 kat hızlandırır. Blog sayısal bir benchmark vermez. M2.5 duyurusu, M2.5'in SWE-Bench Verified'ı (gerçek GitHub hatalarını düzeltme) M2.1'den %37 daha hızlı bitirdiğini bildirir; bu doğruluk değil, süre karşılaştırmasıdır.

**Kaynak notu:** Bu yalnızca bir blog yazısıdır; hakemli bir makale değildir ve sayısal benchmark sonucu içermez.

**Bizim için:** Asenkron rollout'ta erken biten (genelde kolay) soruların eğitimi domine etmesi gerçek bir tuzak. Aynı soruya ait rollout'ları birlikte beklemek ve prompt'un ortak önekini (şema bağlamı) bir kez hesaplamak MLX'te de büyük tasarruf demek.

## Kimi K2.5: Visual Agentic Intelligence (Moonshot AI, Şubat 2026) — [2602.02276](https://arxiv.org/abs/2602.02276)
**Tek cümlede:** K2'nin üstüne kurulmuş native multimodal bir agent modeli; kısa düşünmeyi öğreten Toggle ve paralel alt agent'ları yöneten Agent Swarm ile.

**Problem:** Modele görsel yetenek eklenirken metin yeteneği korunmalıdır. Uzun düşünen modeller de gereksiz yere çok token harcar. Ayrıca geniş arama görevlerinde tek bir agent'ın adımları sırayla atması yavaştır.

**Ne yaptılar:**
1. **Model.** K2 üzerine yaklaşık 15T karışık görsel-metin token'ıyla eğitim.
2. **SFT.** K2 hattını izler. Aday cevaplar K2, K2 Thinking ve şirket içi uzman modellerden gelir; insan etiketleme, prompt mühendisliği ve çok aşamalı doğrulamadan geçer.
3. **"Zero-vision SFT".** SFT'de yalnızca metin verisi kullanılır. Görsel işlemler (kırpma, büyütme gibi) IPython ile kod yazılarak yapılır. İnsanların tasarladığı görsel trajectory'leri eklemek genellemeyi bozmuş.
4. **RL alanları yeteneğe göre.** Alanlar modaliteye (görsel, metin) göre değil, yeteneğe göre ayrılır: bilgi, akıl yürütme, kod, agent. Sonucu doğru çıkan görsel RL trajectory'leri rejection-sampling fine-tuning'e (doğru çıkanlarla yeniden SFT) geri beslenir.
5. **RL algoritması.** Baseline, aynı soruya üretilen K cevabın ortalama reward'ıdır. Her token için yeni ve eski modelin olasılık oranının logaritması hesaplanır. Bu değer [α, β] aralığının dışındaysa o token'ın gradient'i sıfırlanır. Ayrıca bu log-oranın karesi τ katsayısıyla cezalandırılır; bu, modelin bir adımda çok değişmesini engeller. Optimizer MuonClip (Moonshot'un K2'de kullandığı optimizer).
6. **Toggle: kısa düşünmeyi öğretme.** Eğitim iki faz arasında gidip gelir. Birinci fazda her problemin bir token budget'ı zorunludur; budget, o problemin doğru cevaplarının uzunluk dağılımının ρ-inci yüzdeliğidir. Örnek: ρ = 50 ise budget, doğru cevapların ortanca uzunluğudur. İkinci fazda tam uzunluğa izin verilir. Her m iterasyonda bir kontrol yapılır ve ortalama doğruluk λ eşiğini geçmişse faz değişir.
7. **GRM'ler.** K2'nin self-critique rubric'leri (modelin kendi cevaplarını ölçütlerle karşılaştırması) chat, kodlama, arama ve dosya ya da belge gibi çıktılar üreten agent'lara genişletilir. Reward hacking'e karşı birden çok rubric kullanılır.
8. **Agent Swarm ve PARL.** Bir orkestratör model işi alt agent'lara paralel dağıtır; PARL bu orkestratörü RL ile eğitir. Reward üç parçanın toplamıdır: paralellik ödülü (λ1 ağırlıklı), işi bitirme ödülü (λ2 ağırlıklı) ve görev performansı. λ1 ve λ2 eğitim boyunca sıfıra indirilir; yani paralellik ve bitirme başta yol gösterir, sonunda yalnızca performans kalır. Alt agent'lar donuktur, yalnızca orkestratör eğitilir.

**Sonuç:** Yazarların raporuna göre görsel RL metin benchmark'larını da artırır: MMLU-Pro 84.7 → 86.4 (geniş konulu bilgi soruları), GPQA-Diamond 84.3 → 86.4, LongBench v2 56.7 → 58.9 (uzun metin anlama). Yani görsel eğitim metin yeteneğini bozmamış, 1.5–2 puan artırmış. Toggle, K2 Thinking'de çıktı token'ını ortalama %25–30 azaltır; doğruluk kaybı ihmal edilebilir düzeydedir. Toggle yalnızca matematik ve kodla eğitildiğinde bile GPQA ve MMLU-Pro'da token kullanımı azalır, yani kısalık başka alanlara da geçer. Agent Swarm, tek agent'a göre BrowseComp'u 60.6 → 78.4, WideSearch item-F1'i (çok sayıda öğe toplamayı gerektiren geniş arama; bulunan öğelerin isabeti) 72.7 → 79.0 yapar ve gecikmeyi 3–4.5 kat azaltır.

**Bizim için:** Yardımcı (shaping) reward'ları başta verip sonra sıfıra indirmek (λ annealing) ve doğruluk eşiği aşılınca budget'ı sıkılaştırmak uygun bir sıralama. Small model'e önce "tool'u doğru çağır", sonra "az çağrıyla doğru SQL bul" öğretilebilir.

## DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models (DeepSeek-AI, Aralık 2025) — [2512.02556](https://arxiv.org/abs/2512.02556)
**Tek cümlede:** Ön-eğitim maliyetinin %10'undan fazlası post-training RL'e harcanır; alan uzmanları, tek bir karma RL aşaması ve büyük ölçekli sentetik agent görevleri.

**Problem:** Açık modeller, özellikle agent görevlerinde kapalı modellerin gerisindeydi. Raporun cevabı iki parçalı: post-training'e çok daha fazla hesaplama ayırmak ve RL için çok sayıda zor, çeşitli agent görevi üretmek. Bu ölçekte RL'in kararlı kalması için GRPO'ya da düzeltmeler gerekir.

**Ne yaptılar:**
1. **Model.** V3.1-Terminus'a yalnızca DeepSeek Sparse Attention (DSA) eklenir; her token önceki token'ların yalnızca seçilmiş bir kısmına bakar, böylece uzun bağlam ucuzlar. Bu hat V3.2-Exp ile başladı.
2. **Uzman distillation.** Aynı V3.2 base checkpoint'inden alan uzmanları büyük ölçekli RL ile eğitilir: matematik, programlama, genel mantık, genel agent, agentic coding, agentic search; yazım ve genel soru-cevap da. Thinking ve non-thinking verisi farklı modellerden üretilir. Uzmanların verisiyle eğitilen model uzmanların az gerisinde kalır; sonraki RL bu farkı kapatır.
3. **Tek karma RL aşaması.** Reasoning, agent ve alignment birlikte, GRPO ile eğitilir. Reasoning ve agent görevlerinde reward üç parça: kural tabanlı sonuç doğruluğu, length penalty ve dil tutarlılığı reward'ı (cevabın tek bir dilde kalması). Genel görevlerde her prompt'un kendi rubric'ini kullanan bir generative reward model puan verir.
4. **GRPO'ya dört değişiklik.** (a) KL tahmini: modelin referans modelden uzaklaşmasını ölçen KL, K3 adlı bilinen bir formülle tahmin edilir; importance ratio ile düzeltilerek yansız (unbiased) yapılır. Matematikte KL cezası zayıf tutulur ya da hiç kullanılmaz. (b) [Off-policy](00_terimler.md#on-policy-ve-off-policy) sequence masking (off-policy: modelin eski bir hâliyle üretilmiş veri): trajectory'yi üreten eski model ile şimdiki model arasındaki fark bir δ eşiğini aşmışsa ve trajectory'nin advantage'ı negatifse, o trajectory kayba girmez. Fazla bayat ve kötü örnekler eğitimi bozmasın diye yapılır. (c) Keep Routing: MoE'de her token'ın hangi uzmana gittiği rollout sırasında kaydedilir ve eğitimde aynısı kullanılır. (d) Keep Sampling Mask: üretimde kullanılan top-p/top-k kesmesi (yalnızca en olası token'lar arasından seçme) eğitimde olasılık hesaplanırken de uygulanır. (c) ve (d), üretim ile eğitimin aynı olasılıkları görmesi içindir.
5. **Sentetik agent görevleri.** 24.667 code agent, 50.275 search agent, 4.417 genel agent (1.827 sentetik ortamda) ve 5.908 code interpreter görevi.
6. **Görev seçim kuralları.** Bir SWE ortamı ancak gold patch (doğru düzeltme) en az bir kırık testi düzeltiyor (F2P > 0) ve hiçbir geçen testi bozmuyorsa (P2F = 0) tutulur. Bir search örneği ancak ground truth doğruysa ve modelin bütün adayları yanlışsa tutulur. Bir genel agent görevi ancak 100 denemede en az biri başarılıysa (pass@100 > 0) tutulur. Yani görev ne imkânsız ne de kolay olmalıdır.
7. **Cold start prompt tabanlı.** Reasoning verisi ile tool call'lu non-reasoning agent verisi birleştirilir.
8. **V3.2-Speciale.** Yüksek hesaplamalı varyant. Yalnızca reasoning verisiyle, azaltılmış length penalty ile ve DeepSeekMath-V2'nin ispat verisi ve reward'ıyla eğitilir.

**Sonuç:** Yazarların raporuna göre V3.2'nin skorları: AIME 2025 93.1, HMMT Feb 2025 92.5 (Harvard-MIT lise matematik yarışması), LiveCodeBench 83.3, SWE-Verified 73.1, Terminal Bench 2.0 46.4, BrowseComp 51.4, τ²-Bench 80.3 (müşteri hizmeti senaryolarında tool kullanan agent). BrowseComp'ta bağlam yönetimi eklenince skor 51.4'ten 67.6'ya çıkar. Speciale'nin yarışma sonuçları: IMO 2025'te 42 puanın 35'i (uluslararası matematik olimpiyatı), IOI 2025'te 600'ün 492'si (uluslararası bilişim olimpiyatı), ICPC World Finals'ta 12 problemin 10'u (üniversite takımları programlama yarışması; altın). Ana ablation: RL yalnızca sentetik genel agent verisiyle yapılınca τ²-Bench, MCP-Mark ve MCP-Universe (MCP tool'larıyla yapılan agent görevleri; MCP, Model Context Protocol, tool'ları modele bağlayan ortak bir arayüzdür) belirgin artar. RL kod ve aramayla sınırlanınca bu benchmark'lar artmaz. Sentetik görevler zordur: V3.2-Exp onları ilk denemede %12, GPT-5-Thinking %62 oranında çözer.

**Bizim için:** "En az bir deneme çözebiliyor ama hepsi çözemiyor" kuralı (pass@k > 0, bütün adaylar doğru değil) RL soru seçimine birebir uyar. Small model'in hiç çözemediği soruları RL'den çıkarıp large model'in çözümleriyle SFT'ye ayırmak bunun doğal karşılığı.

## DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning (DeepSeek-AI, Kasım 2025) — [2511.22570](https://arxiv.org/abs/2511.22570)
**Tek cümlede:** İspatları puanlayan bir verifier model eğitilir; bu verifier, kendi ispatındaki hataları bulmaya zorlanan bir ispat üreticisinin reward'ı olur.

**Problem:** Matematikte RL çoğu zaman yalnızca son cevaba bakar. Ama doğru cevaba yanlış akıl yürütmeyle de varılabilir. İspat sorularında ise kontrol edilecek tek bir son cevap yoktur. Bu yüzden ispatın kendisini okuyup puanlayabilen bir model gerekir. Generator (ispat üreten model) ile verifier birbirini besleyen bir döngüde iyileşir; bu bir tür [self-play](00_terimler.md#self-play)'dir (modelin kendi ürettikleriyle kendini geliştirmesi).

**Ne yaptılar:**
1. **Başlangıç.** Base model DeepSeek-V3.2-Exp-Base.
2. **Verifier için cold-start verisi.** AoPS'tan (Art of Problem Solving forumu) 17.503 problem: olimpiyatlar, takım seçme sınavları ve 2010 sonrası ispat problemleri. Aday ispatlar V3.2-Exp-Thinking ile üretilir. Uzmanlar her ispatı 0, 0.5 ya da 1 ile puanlar.
3. **Verifier'ı eğitme.** Verifier önce bulduğu sorunların özetini, sonra bir puan yazar. Reward iki şeyin çarpımıdır. Biçim kapısı: istenen bölümler yazılmamışsa reward 0. Puan isabeti: 1 eksi verifier'ın puanı ile uzmanın puanı arasındaki fark. Örnek: uzman 1 demiş, verifier 0.5 demişse puan isabeti 0.5'tir.
4. **Meta-verifier.** Ayrı bir model verifier'ın analizini okur ve analizin ne kadar doğru ve gerekçeli olduğuna 0, 0.5 ya da 1 verir. Verifier'ın reward'ı bu puanla da çarpılır. Böylece verifier yalnızca doğru puanı tutturmakla kalmaz, doğru gerekçeyi de yazmak zorunda kalır.
5. **Generator'ı eğitme.** Generator GRPO ile, verifier'ın ispata verdiği puanı reward alarak eğitilir. Self-verification için generator ispattan sonra kendi ispatını da değerlendirir ve kendine bir puan verir. Toplam reward: biçim kapısı × (0.76 × verifier'ın ispata verdiği puan + 0.24 × öz değerlendirmenin isabeti). Öz değerlendirmenin isabeti, generator'ın kendine verdiği puanın verifier'ın puanına ne kadar yakın olduğu ile meta-verifier'ın bu değerlendirmeye verdiği puanın çarpımıdır. Yani model kötü bir ispatı "kötü" diye dürüstçe işaretlerse de ödül alır.
6. **İterasyonlar.** Her iterasyonda önce verifier, sonra generator eğitilir. İkinci iterasyondan itibaren verifier, iki yeteneği rejection fine-tuning ile (iyi çıktılarla yeniden SFT) birleştiren checkpoint'ten başlar.
7. **Otomatik etiketleme.** Her ispat için n bağımsız analiz üretilir. Hata bildiren analizler için m meta-verification yapılır. Çoğunluk hatayı onaylarsa etiket geçerli sayılır. Son iki iterasyonda insan etiketlemesinin yerini tamamen bu hat almıştır.
8. **Üretim sınırı** 128K token.

**Sonuç:** Yazarların raporuna göre meta-verification, verifier analizlerinin kalitesini 0.85'ten 0.96'ya çıkarır; yani analizlerdeki hatalı gerekçeler belirgin azalır. Yarışma sonuçları yüksek test-time hesaplamayla (cevap başına çok deneme ve kontrol) alınmıştır: IMO 2025'te 6 problemden 5'i (%83.3), CMO 2024'te %73.8 (Çin matematik olimpiyatı), Putnam 2024'te 120 puanın 118'i (ABD üniversite matematik yarışması). Bu dosyada bu rakamlar için önceki bir modelin skoru yok.

**Bizim için:** Reward'ı ikiye bölmek (cevabın kendisi + modelin kendi cevabını doğru değerlendirmesi) bizim submit'teki large model kontrolüne denk. Small model'e "submit etmeden önce sonucu kontrol et" davranışını ayrı bir reward terimiyle öğretmek düşünülebilir.

## Kimi K2 Thinking (Moonshot AI, Kasım 2025) — [blog](https://www.kimi.com/blog/kimi-k2-thinking)
**Tek cümlede:** K2'nin "thinking agent" sürümü; tool kullanırken adım adım düşünür ve insan müdahalesi olmadan 200–300 tool call'u art arda yürütür.

**Problem:** Zor görevlerde modelin hem uzun düşünmesi hem de çok sayıda tool çağrısı yapması gerekir. Çoğu model birkaç düzine adımdan sonra yolunu kaybeder. Ayrıca bu kadar büyük bir modeli uzun süre çalıştırmak pahalıdır, bu yüzden üretimin hızlanması gerekir.

**Ne yaptılar:**
1. **İki yönlü [test-time scaling](00_terimler.md#test-time-scaling).** Test-time scaling, cevap verirken daha çok hesaplama harcayarak daha iyi sonuç almaktır. K2 Thinking bunu iki şeyi birlikte büyüterek yapar: düşünce token'ları ve tool call adımları.
2. **Interleaved thinking.** Model her tool call'dan önce ve sonra düşünür; düşünce, eylem ve sonuç iç içedir. Bu sayede 200–300 ardışık tool call'u insan müdahalesi olmadan yürütebilir.
3. **Post-training'de QAT.** MoE bileşenlerine INT4 weight-only quantization uygulanır: yalnızca ağırlıklar 4 bitlik tam sayıya indirilir. Model bu hassasiyete eğitim sırasında alıştırılır (quantization-aware training). Bu, üretimi yaklaşık 2 kat hızlandırır. Bütün benchmark'lar INT4 hassasiyetinde raporlanır.
4. **Değerlendirme** 256K token bağlamla yapılmıştır.

**Sonuç:** Yazarların raporuna göre skorlar: HLE 44.9 (yalnızca metin soruları, tool'larla), BrowseComp 60.2, SWE-bench Verified 71.3, AIME 2025 94.5 (Python kullanınca 99.1), LiveCodeBench v6 83.1, Terminal-Bench 47.1. Karşılaştırma için aynı ailenin düşünmeyen sürümü K2-Instruct (aşağıdaki K2 girişi) SWE-bench Verified'da 65.8, AIME 2025'te 49.5, LiveCodeBench v6'da 53.7 almıştı. Yani düşünme en çok matematikte (yaklaşık 45 puan) ve yarışma kodunda (yaklaşık 30 puan) fark yaratır. Bu rakamlar iki farklı rapordan geldiği için değerlendirme ayarları birebir aynı olmayabilir.

**Kaynak notu:** Bu yalnızca bir blog yazısıdır ve RL ayrıntısı vermez. Algoritma ayrıntıları için K2 ve K2.5 raporlarına bakılmalı.

**Bizim için:** Quantization'ı eğitim sırasında uygulamak (QAT) rollout ile eğitim arasındaki farkı kapatır. MLX'te 4-bit model ile rollout alıp bf16 eğitiyorsak bu uyumsuzluğun (train–inference mismatch) farkında olmalıyız.

## Kimi-Dev: Agentless Training as Skill Prior for SWE-Agents (Moonshot AI, Eylül 2025) — [2509.23045](https://arxiv.org/abs/2509.23045)
**Tek cümlede:** Sabit iş akışlı (Agentless) kod düzeltme eğitimi, serbest çalışan SWE agent'ları için yeniden kullanılabilir bir ön beceridir ("skill prior"). ICLR 2026'da kabul edilmiş.

**Problem:** Yazılım hatalarını düzelten modeller iki şekilde kurulur. Agentless yaklaşımda iş akışı sabittir: önce hatanın yeri bulunur, sonra düzeltme yazılır. SWE-agent yaklaşımında model adımlarını kendisi seçer ve çok turlu çalışır. İkincisini RL ile sıfırdan eğitmek çok pahalıdır. Yazarlar, ucuz Agentless eğitiminin bu pahalı eğitime iyi bir başlangıç noktası olup olmadığını soruyor.

**Ne yaptılar:**
1. **[Mid-training](00_terimler.md#mid-training).** Ön-eğitim ile post-training arasında belirli bir alana odaklı ek ön-eğitimdir. Qwen2.5-72B-Base üzerine yaklaşık 150B token: yaklaşık 50B token Agentless biçiminde doğal diff patch'leri, yaklaşık 20B token PR commit paketleri, yaklaşık 20B token sentetik reasoning ve agent verisi (4 kat tekrarlanarak). SWE-bench Verified ile örtüşen repolar veriden çıkarılır; buna [decontamination](00_terimler.md#decontamination) denir (test sorularının eğitim verisine sızmasını önleme).
2. **Cold start SFT.** DeepSeek-R1'in SWE-Gym ve SWE-bench-extra (iki SWE eğitim veri seti) üzerinde ürettiği uzun reasoning trajectory'leriyle ([long CoT](00_terimler.md#cot-ve-long-cot): adım adım ve uzun düşünce zinciri).
3. **RL yalnızca code-edit aşamasında.** Hata yerini bulma becerisi cold-start modelinde olduğu gibi kalır. Algoritma k1.5 tarzı REINFORCE'tur (yüksek reward alan cevapların olasılığını artıran en basit policy gradient yöntemi). Baseline birden çok rollout'un ortalamasıdır. Reward yalnızca testlerden gelen 0/1 sonuçtur; biçim ya da process reward yoktur.
4. **Uyarlanabilir zorluk.** 1.200 problemle başlanır. 16 denemede hiç çözülemeyen (pass@16 = 0) problemler çıkarılır. Model güçlendikçe dışlanan yaklaşık 500 prompt geri eklenir. Son iterasyonlarda başarılı olan örnekler sonraki batch'lere de katılır.
5. **Ölçek.** İterasyon başına 1.024 problem × 10 rollout ve 5 eğitim adımı; bağlam 64K token.
6. **Test-time self-play.** Model iki rol oynar: BugFixer (düzeltme yazar) ve TestWriter (test yazar). Her örnek için 40 patch ve 40 test üretilir; patch'ler bu testlerle seçilir.
7. **SWE-agent'a uyarlama.** Agentless modelin üstüne 5.016 SWE-smith trajectory'siyle SFT yapılır.

**Sonuç:** Yazarların raporuna göre SWE-bench Verified'da (gerçek GitHub hatalarını düzeltme) %60.4 alınır. Self-play'in katkısı büyüktür: 1 patch × 1 test ile %48.0, 40 × 40 ile %60.4. 5 bin trajectory'lik SFT sonrasında SWE-agent olarak pass@1 %48.6, pass@10 %74.0. Ana ablation başlangıç noktasını (prior) karşılaştırır. RL'den geçmiş prior, hiç Agentless eğitimi görmemiş Base prior'ın en iyi pass@1'ine 2^23 (yaklaşık 8 milyon) SFT token'ıyla ulaşır; Base prior bunun için 1.5 × 2^28 (yaklaşık 400 milyon) token ister, yani yaklaşık 48 kat fazla. Yalnızca mid-training görmüş prior, uçtan uca RL'de 10 adım içinde %2'nin altına düşer. RL prior ise 300 adımdan sonra SFT prior'ı az farkla geçer.

**Bizim için:** Önce sabit bir alt beceriyi (ör. yalnızca "doğru SQL yaz" ya da "doğru değeri bul") RL ile güçlendirip sonra az miktarda tam agent trajectory'siyle SFT yapmak, tam agent RL'inden çok daha ucuz bir yol. pass@k = 0 soruları çıkarıp model güçlendikçe geri eklemek de basit bir curriculum.

## DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning (DeepSeek-AI, Nature, Eylül 2025) — [Nature 645, 633–638](https://www.nature.com/articles/s41586-025-09422-z) / [arXiv v2](https://arxiv.org/abs/2501.12948v2)
**Tek cümlede:** R1'in hakemli Nature sürümü; arXiv v2'nin (Ocak 2026) ek materyali RL verisini, hiperparametreleri, reward model eğitimini ve maliyeti ilk kez ayrıntılı verir.

**Problem:** Ocak 2025'teki ilk R1 raporu yöntemi anlatıyordu ama tekrar üretmek için gereken sayıların çoğunu vermiyordu. Bu sürüm o eksiği kapatır. Küçük bütçeli bir proje için değeri, büyük ölçekli bir RL koşusunun gerçek ayarlarını göstermesidir.

**Ne yaptılar:**
1. **R1-Zero'nun GRPO ayarları.** Learning rate 3e-6. KL katsayısı 0.001: modelin referans modelden uzaklaşmasına çok hafif bir ceza. Örnekleme sıcaklığı 1. Her soruya 16 cevap, her adımda 32 soru; yani adım başına 32 × 16 = 512 cevap. Maksimum cevap uzunluğu 8.2 bininci adıma kadar 32.768 token, sonra 65.536. Toplam 10.400 adım, yani verinin üzerinden 1.6 kez geçiş (epoch). Referans model her 400 adımda güncellenir. Reasoning'de nöral reward model (ne sonuca ne de ara adımlara puan veren) kullanılmaz; reward kurallarla hesaplanır.
2. **R1'in ilk RL aşaması.** Aynı ayarlar; clip oranı 10 (importance ratio için çok geniş bir izin) ve dil tutarlılığı reward'ı eklenir.
3. **R1'in ikinci RL aşaması.** Sıcaklık 0.7, 1.700 adım. Genel veri ve tercih (preference) reward'ları yalnızca son 400 adımda devreye girer.
4. **Reward model'ler.** Helpful RM 66.000 cevap çiftiyle eğitilir (batch 256, learning rate 6e-6, 1 epoch); iki cevaptan hangisinin daha yardımcı olduğunu öğrenir. Safety RM 106.000 prompt'la, pointwise eğitilir: her cevabı tek başına güvenli ya da güvensiz diye puanlar.
5. **RL verisi.** Matematik 26K, kod 17K (+8K hata düzeltme), STEM 22K, mantık 15K, genel 66K (+12.000 zararsızlık). İspat soruları çıkarılır, çünkü kural tabanlı kontrol edilemezler. Matematik ve STEM reward'ı ikilidir (doğru 1, yanlış 0).
6. **Rejection-sampling SFT.** Toplam 804.745 örnek: matematik 395.285, kod 211.129, STEM 10.124, mantık 10.395, genel 177.812. Ortalama uzunluk 5.355,3 token. Yalnızca doğru ve dil karışmamış cevaplar tutulur.

**Sonuç:** Yazarların raporuna göre AIME 2024'te (lise matematik olimpiyatı) pass@1, R1-Zero için 77.9, R1 için 79.8. Yani SFT'li dört aşamalı R1, yalnızca RL'li R1-Zero'yu az farkla geçer; asıl kazanç okunabilirliktir. Dil tutarlılığı reward'ı performansı hafifçe düşürür ama okunabilirlik için tutulur. R1'in eğitim maliyeti 294.000 dolar olarak bildirilmiştir.

**Kaynak notu:** 294.000 dolarlık maliyet, Nature makalesine dayanan haberlerden alınmıştır; base modelin (V3) maliyeti buna dahil değildir.

**Bizim için:** Büyük ölçekte bile RL verisi on binler, SFT verisi yüz binler mertebesindedir (yaklaşık 1:5–1:10). Küçük bütçede birkaç bin iyi seçilmiş RL sorusu makul bir başlangıç.

## Kimi K2: Open Agentic Intelligence (Moonshot AI, Temmuz 2025) — [2507.20534](https://arxiv.org/abs/2507.20534)
**Tek cümlede:** Büyük ölçekli sentetik tool kullanım verisi ve doğrulanabilir ile doğrulanamaz reward'ları birleştiren genel bir RL ile eğitilmiş 1T'lik agent modeli.

**Problem:** Agent davranışını öğretmek için çok sayıda gerçekçi tool kullanım örneği gerekir; bunları insanlarla toplamak pahalıdır. Ayrıca RL'de bazı görevlerin cevabı otomatik kontrol edilebilir (matematik, kod), bazılarınınki edilemez (yazım, sohbet). Model ikisinden de öğrenmelidir.

**Ne yaptılar:**
1. **Model.** 1T toplam, 32B aktif parametreli MoE. 15.5T token ön-eğitim, MuonClip optimizer ile.
2. **Tool kullanım verisi, üç aşamalı hat.** (a) Tool tanımları: GitHub'dan 3000'den fazla gerçek MCP tool'u ve bunlardan evrimle türetilmiş 20.000'den fazla sentetik tool. (b) Agent'lar ve görevler: her görevin açık bir rubric'i vardır. (c) Trajectory'ler: bir LLM judge (cevabı puanlayan başka bir model) yalnızca başarı ölçütlerini karşılayanları tutar. Kodlama ve SWE'de simülasyon yerine gerçek sandbox'lar kullanılır ve testlerin pass rate'i ground truth olur.
3. **Doğrulanabilir reward gym'i.** Kurallarla kontrol edilen görevler: matematik, STEM, mantık; karmaşık instruction following; faithfulness (cevabın verilen kaynağa sadık olması); kodlama ve SWE; güvenlik.
4. **Doğrulanamayan görevler için self-critique rubric reward.** Model kendi cevaplarını rubric'lerle ikişer ikişer karşılaştırır ve hangisinin iyi olduğuna karar verir. Bu critic'in güvenilir kalması için, doğru cevabı bilinen prompt'lardaki on-policy rollout'larla (modelin o anki hâlinin denemeleri) kalibre edilir.
5. **Algoritma (k1.5 üzerine).** Her örneğin bir maksimum token budget'ı vardır; aşan cevap kesilir ve cezalandırılır. Unutmayı azaltmak için PTX loss eklenir: RL'in yanında, elle seçilmiş yüksek kaliteli veride normal SFT kaybı da hesaplanır. Örnekleme sıcaklığı başta yüksektir (çok keşif), sonra azaltılır (temperature decay).

**Sonuç:** Yazarların raporuna göre düşünmeyen sürüm K2-Instruct'ın skorları: SWE-bench Verified 65.8 (çok denemeyle 71.6), Tau2-Bench 66.1 (müşteri hizmeti senaryolarında tool kullanan agent), ACEBench (En) 76.5 (tool kullanımı), LiveCodeBench v6 53.7, AIME 2025 49.5, GPQA-Diamond 75.1. Bu dosyada aynı ayarlarla önceki bir modelin skoru yok. Aynı modelin sonraki thinking sürümü (K2 Thinking) AIME 2025'te 94.5'e çıkmıştır; bu, buradaki matematik skorunun düşünmeden alındığını gösterir.

**Bizim için:** Sentetik görev başına rubric yazıp bir judge ile yalnızca başarılı trajectory'leri SFT'ye almak, experience log'dan "large model'in çözdüğü ve doğru çıkan" konuşmaları seçmenin genelleştirilmiş hâli. PTX benzeri bir karışım RL sırasında genel becerinin kaybını azaltır.

## Kimi-Researcher: End-to-End RL Training for Emerging Agentic Capabilities (Moonshot AI, Haziran 2025) — [blog](https://moonshotai.github.io/Kimi-Researcher/)
**Tek cümlede:** Arama, metin tabanlı tarayıcı ve kod tool'larıyla çalışan bir deep research agent'ı, büyük ölçüde uçtan uca [agentic RL](00_terimler.md#agentic-rl-ve-multi-turn) ile eğitildi.

**Problem:** Deep research agent'ları genelde sabit iş akışlarıyla ya da insan benzeri örneklerle SFT'lenerek kurulur. Bu yöntemler modelin kendi stratejisini keşfetmesine izin vermez. Uçtan uca RL'de model bütün çok turlu görevi (ara, oku, kod çalıştır, cevapla) tek bir reward'a göre öğrenir.

**Ne yaptılar:**
1. **Başlangıç modeli.** Moonshot'un iç k-serisi modellerinden biri.
2. **Algoritma ağırlıkla REINFORCE.** Veri katı biçimde on-policy'dir: yalnızca modelin o anki hâlinin ürettiği trajectory'lerle eğitilir. Tool call biçimini zorla düzelten yardımcılar kapalıdır; model biçimi kendisi doğru yazmayı öğrenir. [Entropy collapse](00_terimler.md#entropy-ve-entropy-collapse) (modelin hep aynı cevabı vermeye başlayıp keşfi bırakması) riskini azaltmak için bazı negatif örnekler atılır. Gamma-decay: doğru trajectory'nin reward'ı adım sayısıyla küçülür, böylece aynı doğru cevaba daha az adımda varan trajectory daha çok ödül alır.
3. **Reward sonuca bakar.** Cevap ground truth'a göre doğru mu. Geçersiz tool çağrısı ya da bağlam veya iterasyon sınırını aşmak cezalandırılır.
4. **Veri.** İki tür görev: belirli tool'ları kullanmayı gerektiren tool-centric görevler ve reasoning ağırlıklı görevler (matematik, kod, zor arama). Otomatik bir hat ground truth'u çıkarır. Pass@N filtresi yalnızca önemsiz olmayan soruları tutar, yani N denemede hep çözülen sorular atılır.
5. **Bağlam yönetimi ve hız.** Gereksiz dokümanlar bağlamdan atılır; böylece rollout 50 iterasyonun ötesine uzayabilir. Rollout tam asenkrondur ve tur düzeyinde partial rollout kullanılır (bitmeyen trajectory sonraki iterasyonda sürer); bu en az 1.5 kat hızlanma sağlar.

**Sonuç:** Yazarların raporuna göre HLE'de (uzmanların yazdığı çok zor sorular) pass@1 %8.6'dan %26.9'a çıkar; yani RL ile skor üç katından fazla artar. Pass@4 %40.17'dir. xbench-DeepSearch'te (deep research arama görevleri) pass@1 %69 (4 koşunun ortalaması). Ablation'da bağlam yönetimi yaklaşık %30 daha fazla iterasyona izin verir.

**Kaynak notu:** Kaynak bir blog yazısıdır, hakemli değildir; başlangıç modeli açıklanmamış bir iç modeldir.

**Bizim için:** "Geçersiz tool çağrısı ve budget aşımı cezası + kısa doğru trajectory'ye gamma bonusu", bizim 10 tool call'luk budget'ımıza doğrudan uyan, uygulaması kolay bir reward tasarımı.

## MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention (MiniMax, Haziran 2025) — [2506.13585](https://arxiv.org/abs/2506.13585)
**Tek cümlede:** Uzun düşünmeyi ucuzlatan hibrit (lightning) attention'lı açık bir reasoning modeli ve onu eğiten yeni RL algoritması CISPO; büyük ölçekli RL 512 H800 GPU ile yaklaşık üç haftada bitti.

**Problem:** Uzun düşünen modellerde normal attention'ın maliyeti cevap uzunluğunun karesiyle büyür. Bu, 80K token'lık düşünceleri çok pahalı yapar. Ayrıca PPO ve GRPO'daki clip, "Ama", "Bekle" gibi düşük olasılıklı ama önemli düşünme token'larını gradient'ten çıkarabilir. Bu token'lar modelin kendini düzeltmesini başlatır.

**Ne yaptılar:**
1. **Model ve mid-training.** MiniMax-Text-01 üzerine reasoning için 7.5T token ek ön-eğitim (continual pretraining). Model hibrit attention kullanır: lightning attention (maliyeti uzunlukla doğrusal büyüyen bir attention türü) normal attention'la karışık.
2. **Long-CoT SFT.** Verinin yaklaşık %60'ı matematik ve kod.
3. **RL verisi.** Yaklaşık 50K matematik sorusu: yalnızca 10 denemedeki başarı oranı 0'dan büyük ve 0.9'dan küçük olanlar tutulur; hiç çözülmeyenler ve çok kolaylar atılır. Yaklaşık 53K mantık sorusu (SynLogic, 41 görev türü). 30K yarışma programlama sorusu. Birkaç bin SWE örneği. 25K genel görev (GenRM, yani generative reward model ile puanlanan).
4. **Curriculum.** Önce kurallarla doğrulanan reasoning görevleri, sonra genel görevler kademeli olarak karıştırılır.
5. **CISPO.** PPO ve GRPO, importance ratio aralık dışına çıkınca token'ın güncellemesini keser. CISPO token'ı kesmez, yalnızca importance-sampling ağırlığını kırpar. Böylece düşük olasılıklı "düşünme" token'ları da gradient alır. KL cezası yoktur; ayarlanan tek clip değeri üst sınırdır (ε_high).
6. **Çıktı uzunluğu aşamalarla büyütülür:** 40K → 48K → 56K → 64K → 72K → 80K token.
7. **Üretim ile eğitim arasındaki fark.** Aynı token'ın olasılığı üretim motorunda ve eğitim kodunda aynı çıkmalıdır; çıkmazsa RL yanlış sinyalle güncellenir. Modelin son katmanını (LM head) FP32 hassasiyetine almak, iki taraftaki olasılıkların korelasyonunu yaklaşık 0.9'dan 0.99'a çıkarır.
8. **Tekrar döngüsüne karşı.** Art arda 3.000 token'ın her birinin olasılığı 0.99'u geçerse üretim durdurulur; model büyük ihtimalle aynı şeyi tekrarlıyordur.

**Sonuç:** Yazarların raporuna göre Qwen2.5-32B-base üzerindeki karşılaştırmada CISPO, DAPO'nun (clip-higher ve [dynamic sampling](00_terimler.md#dynamic-sampling) ekleyen bir GRPO türevi) performansına adımların yarısıyla ulaşır. M1-80k (80K token'a kadar düşünebilen sürüm): AIME 2024 86.0, SWE-bench Verified 56.0. M1-40k: 83.3 ve 55.6. Yani düşünme sınırını iki katına çıkarmak AIME'de 2.7, SWE'de 0.4 puan ekler. RL'in toplam maliyeti 534.700 dolarlık GPU kiralamasıdır.

**Bizim için:** "pass@k 0 ile 0.9 arası" filtresi en basit ve en etkili RL veri seçimi. Rollout ile eğitim arasındaki olasılık farkını ölçmek (MLX'te üretim ile eğitim aynı ağırlıkla mı) RL kararlılığı için ilk kontrol olmalı.

## DeepSeek-Prover-V2: Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition (DeepSeek-AI, Nisan 2025) — [2504.21801](https://arxiv.org/abs/2504.21801)
**Tek cümlede:** Büyük bir genel model ispatı alt hedeflere böler, küçük bir prover alt hedefleri çözer; bu veriyle 671B'lik model SFT ve RL ile eğitilir, sonra 7B'ye aktarılır.

**Problem:** Lean 4, ispatı bilgisayarın satır satır kontrol ettiği bir formel ispat dilidir. Bu yüzden reward kesindir: Lean ispatı ya kabul eder ya etmez. Ama başlangıç için yeterince formel ispat verisi yoktur. Genel modeller doğal dille akıl yürütmede iyidir, Lean ispatı yazmada zayıftır. Yazarlar bu iki beceriyi birleştirmek istiyor.

**Ne yaptılar:**
1. **Alt hedeflere bölme.** DeepSeek-V3 önce doğal dilde bir ispat taslağı yazar. Sonra bunu Lean'de `have` adımlarına çevirir; her adımın ispatı `sorry` ile boş bırakılır (`sorry`, Lean'de "bu kısmın ispatı sonra yazılacak" demektir). 7B'lik bir prover bu alt hedefleri tek tek çözer. Birleşen tam ispat, V3'ün doğal dildeki düşünce zincirine eklenir ve bir cold-start örneği olur.
2. **Curriculum.** Alt hedeflerden yeni teoremler türetilir; önceki alt hedefler bazen öncül olarak verilir, bazen verilmez. Böylece eğitim kümesi kolaydan zora doğru genişler.
3. **İki mod.** Önce non-CoT mod (düşünmeden doğrudan ispat) [expert iteration](00_terimler.md#expert-iteration) ile eğitilir: modelin çözdüğü ispatlar tekrar eğitim verisine girer ve döngü sürer. Sonra CoT mod (önce düşünüp sonra ispat) cold-start verisiyle kurulur ve RL ile iyileştirilir.
4. **SFT.** DeepSeek-V3-Base-671B üzerinde, sabit learning rate 5e-6, 16.384 token bağlam.
5. **RL.** GRPO; reward ikili: ispat doğru 1, yanlış 0. Eğitimin başında ayrıca bir consistency reward verilir: ispat, taslaktaki alt hedef yapısına uyuyorsa ödül. İterasyon başına 256 problem × 32 aday ispat, 32.768 token'a kadar.
6. **Küçük modele aktarım.** Prover-V1.5-Base-7B'nin bağlamı 4.096'dan 32.768 token'a uzatılır. 671B'nin RL rollout'larıyla fine-tune edilir, sonra aynı RL aşamasından geçer.

**Sonuç:** Yazarların raporuna göre miniF2F-test'te (olimpiyat düzeyi problemlerin Lean sürümleri) skorlar: 671B CoT, 32 denemede %82.4, 8.192 denemede %88.9. 7B CoT, 32 denemede %75.6, 8.192 denemede %82.0. 671B non-CoT, 32 denemede %73.8. Yani düşünerek ispat yazmak 32 denemede 8.6 puan kazandırır. 7B model 671B'nin yaklaşık 7 puan gerisinde kalır. PutnamBench'te (üniversite düzeyi Putnam problemlerinin Lean sürümleri) 671B 658 problemin 47'sini, 7B 11'ini çözer; zor problemlerde boyut farkı daha büyüktür.

**Bizim için:** "Büyük modelin rollout'larıyla SFT, sonra aynı RL" sırası 7B'de bile büyük modelin performansının çoğunu taşır. Bu, large model'in experience log'daki konuşmalarıyla small model'i SFT'leyip ardından kendi rollout'larıyla RL yapmanın doğrudan örneği.

## Inference-Time Scaling for Generalist Reward Modeling (DeepSeek-AI ve Tsinghua Üniversitesi, Nisan 2025) — [2504.02495](https://arxiv.org/abs/2504.02495)
**Tek cümlede:** Önce kendi değerlendirme ilkelerini, sonra eleştirisini yazan bir reward model; çok kez örneklenip oylandıkça daha isabetli olur.

**Problem:** Kural tabanlı kontrolü olmayan genel görevlerde (sohbet, yazım) reward'ı bir reward model verir. Klasik reward model'ler tek bir sayı üretir; onlara daha çok hesaplama vermek sonucu iyileştirmez. Yazarlar, cevap verirken daha çok örnekleme yaptıkça daha iyi karar veren bir reward model istiyor.

**Ne yaptılar:**
1. **Pointwise GRM.** Model önce bu soru için hangi ilkelere (principles) bakılacağını yazar, sonra cevapları eleştirir ve her cevaba 1–10 arası bir puan verir. Pointwise demek, her cevabın kendi puanını alması demektir; böylece tek bir cevap da birden çok cevap da puanlanabilir. Eğitim yönteminin adı Self-Principled Critique Tuning (SPCT).
2. **SPCT aşama 1, rejective fine-tuning (cold start).** Trajectory'ler iki tür prompt'la örneklenir: doğru cevabın ipucu verildiği ve verilmediği. Yanlış karar veren trajectory'ler atılır. Bütün örneklerin zaten doğru olduğu, yani çok kolay sorgular da atılır.
3. **SPCT aşama 2, kural tabanlı online RL.** GRPO ile; model en iyi cevabı seçerse +1, seçemezse −1 alır. Biçim reward'ı yoktur; onun yerine daha büyük bir KL katsayısı kullanılır, model başlangıçtaki biçimden çok uzaklaşmasın diye.
4. **Modeller.** Base model Gemma-2-27B. Ölçekleme deneyleri DeepSeek-V2-Lite, V2.5 ve V3 ile yapılır.
5. **Çıkarımda ölçekleme.** Aynı soru için k değerlendirme paralel üretilir ve puanlar toplanır (oylama). Ayrıca bir meta RM eğitilir: bir değerlendirmenin ilke ve eleştirisinin doğru olup olmadığını öğrenir (ikili cross-entropy ile, yani doğru/yanlış sınıflandırması). Meta RM, k değerlendirmenin en iyi yarısını (k/2) seçer, oylamaya yalnızca onlar girer. Örnekleme sıcaklığı 0.5.

**Sonuç:** Yazarların raporuna göre Reward Bench, PPE ve RMB (reward model'in iki ya da daha çok cevaptan iyisini seçip seçemediğini ölçen benchmark'lar) ortalamasında DeepSeek-GRM-27B tek denemeyle (greedy) 69.9, 32 değerlendirmenin oylamasıyla 71.0, meta RM ile 72.8 alır. Yani çıkarımda harcanan hesaplama yaklaşık 3 puan kazandırır. 32 örnekle oylayan 27B model, 671B'lik MoE modelle yaklaşık eşittir. Ablation: ilke üretimi çıkarılınca skor 69.9'dan 67.5'e düşer. Genel instruction verisi çıkarılınca RFT modeli 63.3'e iner. Uzun CoT (R1 tarzı) genel amaçlı reward modelde belirgin fayda sağlamaz.

**Bizim için:** Bizim large model kontrolümüz zaten bir GRM. "Çok kolay" örnekleri atıp yalnızca karar verilmesi zor SQL çiftleriyle küçük bir checker eğitmek ya da large model'i birkaç kez örnekleyip oylatmak kontrolün isabetini artırabilir.

## DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (DeepSeek-AI, Ocak 2025) — [2501.12948](https://arxiv.org/abs/2501.12948)
**Tek cümlede:** SFT olmadan doğrudan base model üzerinde yapılan RL'in (R1-Zero) uzun akıl yürütme, kendini doğrulama ve geri dönüp düzeltme davranışlarını ortaya çıkardığını gösterdiler; sonra okunabilir R1'i kurup küçük modellere aktardılar.

**Problem:** Akıl yürütmeyi öğretmek için genelde insanların yazdığı adım adım çözümlerle SFT yapılır; bu pahalıdır ve modeli insan çözümleriyle sınırlar. Soru şu: yalnızca "cevap doğru mu" reward'ıyla RL, akıl yürütmeyi kendi başına öğretebilir mi? İkinci soru: bu yetenek küçük modellere nasıl aktarılır?

**Ne yaptılar:**
1. **R1-Zero.** DeepSeek-V3-Base üzerinde GRPO. Reward yalnızca kurallarla hesaplanır: cevabın doğruluğu ve düşüncenin `<think>` etiketleri içinde yazılması (biçim). Bu modelde uzun düşünme kendiliğinden ortaya çıkar, ama metin okunması zordur ve diller karışır.
2. **R1'in dört aşaması.** (1) Cold-start SFT: binlerce okunabilir long-CoT örneği; R1-Zero çıktıları süzülür, V3 ve insanlar düzeltir. (2) Reasoning odaklı RL; buna dil tutarlılığı reward'ı eklenir. (3) RL checkpoint'inden rejection sampling ile yaklaşık 600k reasoning örneği, V3 hattından yaklaşık 200k non-reasoning örnek; toplam yaklaşık 800k örnekle SFT. (4) Bütün senaryolar için ikinci RL: reasoning'de kural tabanlı reward, genel veride preference reward model (insan tercihini taklit eden puanlayıcı).
3. **Küçük modellere distillation.** Aynı yaklaşık 800k örnekle Qwen2.5 ve Llama base modelleri yalnızca SFT ile eğitilir. RL aşaması yoktur.

**Sonuç:** Yazarların raporuna göre R1, AIME 2024'te (lise matematik olimpiyatı) pass@1 79.8 alır. Aktarılan küçük modellerin AIME 2024 / MATH-500 (lise ve üniversite düzeyi 500 matematik problemi) skorları: Qwen-1.5B 28.9 / 83.9, Qwen-7B 55.5 / 92.8, Qwen-14B 69.7 / 93.9, Qwen-32B 72.6 / 94.3, Llama-8B 50.4 / 89.1, Llama-70B 70.0 / 94.5. Yani 7B bile yalnızca SFT ile AIME'de yarıdan fazlasını çözer. Ana ablation: Qwen-32B-Base'e 10 bin adımdan fazla doğrudan RL yapıldığında (R1-Zero-Qwen-32B) AIME skoru 47.0'da kalır. Aynı boyuttaki, R1'den aktarılmış 32B ise 72.6'ya ulaşır; distillation RL'den 25.6 puan iyidir.

**Bizim için:** Küçük modelde "güçlü modelin doğru trajectory'leriyle SFT" kendi başına RL'den çok daha verimli. RL'i ancak bu distillation'dan sonra, ek kazanç için kullanmak bütçe açısından doğru sıra.

## Kimi k1.5: Scaling Reinforcement Learning with LLMs (Moonshot AI, Ocak 2025) — [2501.12599](https://arxiv.org/abs/2501.12599)
**Tek cümlede:** Value function, ağaç araması ya da process reward model gibi karmaşık parçalar olmadan, uzun bağlam ve sade bir RL algoritmasıyla multimodal reasoning RL'ini ölçeklediler; uzun düşünceyi kısa cevaplı modellere aktarmak için long2short yöntemleri önerdiler.

**Problem:** O dönem birçok çalışma reasoning RL'i için value function (her adımın gelecekteki değerini tahmin eden ayrı bir model), MCTS (Monte Carlo Tree Search, olası adımları ağaç gibi açıp arama) ya da process reward model (ara adımları puanlayan model) kullanıyordu. Bunlar pahalı ve kırılgandır. Ayrıca uzun düşünen modeller pratikte yavaş ve pahalıdır; aynı doğruluğun daha kısa cevaplarla alınması istenir.

**Ne yaptılar:**
1. **RL prompt seçimi.** Zorluk, bir SFT modelinin her prompt'u görece yüksek sıcaklıkta 10 kez cevaplamasındaki başarı oranıyla ölçülür. Akıl yürütmeden tahmin edilebilecek sorular çıkarılır: çoktan seçmeli, doğru/yanlış ve ispat soruları. Genel soru-cevapta model doğru cevabı düşünmeden (CoT olmadan) 8 denemede bulabiliyorsa prompt atılır. Bu, modelin akıl yürütmeden tahminle ödül almasını, yani reward hacking'i engeller.
2. **Long-CoT warmup SFT.** Doğrulanmış akıl yürütme yollarından oluşan küçük bir veriyle.
3. **Algoritma: online policy mirror descent'in bir türü.** Basitçe, her iterasyonda model reward'ı artıracak yönde güncellenir, ama bir önceki hâlinden fazla uzaklaşması kare bir ceza (l2 düzenlileştirme) ile engellenir. Baseline, aynı soruya üretilen k cevabın ortalama reward'ıdır. Value network yoktur.
4. **Length penalty.** Doğru cevaplar arasında kısa olanlar ödüllendirilir, uzun yanlış cevaplar cezalandırılır. Ceza, bir süre normal eğitim yapıldıktan sonra kademeli olarak devreye alınır (warmup) ve sonra sabit tutulur.
5. **Örnekleme stratejileri.** Curriculum sampling: kolay sorulardan zora doğru. Prioritized sampling: başarı oranı s olan bir problem, 1 − s ile orantılı olasılıkla seçilir. Örnek: model bir soruyu %90 çözüyorsa ağırlığı 0.1, %20 çözüyorsa 0.8 olur; zorlanılan sorular daha sık gelir.
6. **Partial rollout.** Sabit bir token budget'ında kesilen trajectory'ler bir replay buffer'da saklanır ve sonraki iterasyonda kaldığı yerden sürer.
7. **Long2short, dört yöntem.** (a) [Model merging](00_terimler.md#model-merging): uzun ve kısa düşünen modellerin ağırlıklarının ortalaması alınır. (b) Shortest rejection sampling: soru başına 8 cevap üretilir, en kısa doğru olan SFT'ye alınır. (c) [DPO](00_terimler.md#dpo-ve-preference-optimization) (Direct Preference Optimization: iyi ve kötü cevap çiftlerinden doğrudan öğrenme): en kısa doğru cevap iyi örnek, ondan 1.5 kattan uzun cevaplar kötü örnek olur. (d) Length penalty'li ve maksimum uzunluğu kısaltılmış ikinci bir RL fazı.

**Sonuç:** Yazarların raporuna göre uzun düşünen (long-CoT) model: AIME 2024 77.5, MATH 500 96.2, Codeforces'ta katılımcıların %94'ünden iyi, MathVista 74.9 (görsel matematik soruları). Kısa düşünen (short-CoT) model: AIME 60.8, MATH500 94.6, LiveCodeBench 47.3. Yani kısa model AIME'de uzun modelin 16.7 puan gerisinde, kolay MATH500'de ise yalnızca 1.6 puan gerisindedir. Long2short RL'li model AIME 2024'te ortalama 3.272 token'la 60.8 alır.

**Bizim için:** "Başarı oranına göre örnekleme (1 − s)" ve "modelin tool kullanmadan tahmin edebildiği soruları atma", küçük bütçeli RL için en ucuz iki veri seçimi tekniği. En kısa doğru trajectory'yi SFT'ye almak da tool call sayısını azaltmanın doğrudan yolu.

## DeepSeek-V3 Technical Report (DeepSeek-AI, Aralık 2024) — [2412.19437](https://arxiv.org/abs/2412.19437)
**Tek cümlede:** 671B toplam, 37B aktif parametreli MoE'nin post-training'i: R1 serisinden reasoning distillation içeren 1.5M örneklik SFT ve GRPO ile RL; gerekçe yazan (CoT'li) bir reward model ve self-rewarding.

**Problem:** Genel amaçlı bir modele R1 tarzı güçlü akıl yürütme kazandırmak isteniyor. Ama R1'in cevapları uzun, bazen dağınık ve aşırı düşünülmüş. Ayrıca kural tabanlı kontrolü olmayan görevlerde güvenilir bir reward gerekiyor.

**Ne yaptılar:**
1. **SFT verisi, 1.5M örnek.**
2. **Reasoning verisi** (matematik, yarışma kodu, mantık bulmacası) şirket içi bir R1 modeliyle üretilir. Her alan için SFT ve RL ile eğitilmiş uzman modeller veri üreticisi olur. Son veri rejection sampling ile seçilir. Her problemden iki tür kayıt çıkar: biri problem ve orijinal (kısa) cevap; diğeri modeli yansıtmaya ve doğrulamaya yönlendiren bir system prompt, problem ve R1'in cevabı.
3. **Non-reasoning verisi** (yaratıcı yazım, rol yapma, basit soru-cevap) DeepSeek-V2.5 ile üretilir ve insanlarca doğrulanır.
4. **SFT ayarları.** 2 epoch; learning rate kosinüs eğrisiyle 5e-6'dan 1e-6'ya iner. Packing kullanılır: birden çok kısa örnek tek bir uzun diziye yan yana konur. [Sample masking](00_terimler.md#loss-masking) ile her örnek yalnızca kendi token'larını görür, yan yana konan örnekler birbirini etkilemez.
5. **RL reward'ı.** Doğrulanabilir görevlerde kural tabanlı reward model: kutu içine yazılmış son cevap kontrol edilir ya da kod derleyicide testlerle çalıştırılır. Diğer görevlerde V3'ün SFT checkpoint'lerinden eğitilmiş, model tabanlı bir reward model kullanılır. Bu modelin tercih verisi yalnızca "hangisi iyi" kararını değil, kararın gerekçesini (CoT) de içerir; bu reward hacking'i azaltmak içindir.
6. **RL algoritması GRPO.** Ayrı bir critic (value) modeli yoktur; baseline, aynı soruya üretilen cevap grubunun ortalama reward'ıdır.

**Sonuç:** Yazarların raporuna göre R1 distillation'ının ablation'ı (DeepSeek-V2.5 üzerinde) doğruluğu belirgin artırır: LiveCodeBench-CoT 31.1 → 37.4 (yarışma programlama), MATH-500 74.6 → 83.2. Ancak ortalama cevap uzunluğu da artar: LiveCodeBench'te 718 → 783 token (yaklaşık %9), MATH-500'de 769 → 1510 token (yaklaşık iki katı). Yani distillation doğruluğu artırırken cevapları belirgin şekilde uzatır.

**Bizim için:** Alan uzmanı bir modelin rejection-sampled çıktılarıyla SFT, uzunluk maliyetiyle birlikte gelir. Bizim budget'lı agent'ımızda büyük modelin uzun trajectory'lerini olduğu gibi kopyalamak yerine kısa ve doğru olanları seçmek gerekir.
