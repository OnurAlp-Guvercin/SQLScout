# ByteDance Seed, Zhipu, Tencent, Xiaomi, Meituan, Ant, Baidu, StepFun

**Bu bölümde ne var:** Çin'deki büyük laboratuvarların (ByteDance Seed, Zhipu, Tencent, Xiaomi, Meituan, Ant Group, Baidu, StepFun) post-training raporları, yeniden eskiye sıralı. Post-training, önceden eğitilmiş bir modeli [SFT](00_terimler.md#sft) (örnek cevaplarla doğrudan eğitme) ve [RL](00_terimler.md#rl-ve-rlvr) (modelin denemelerini puanlayıp iyi denemeleri güçlendirme) ile kullanılabilir hale getirme aşamasıdır. Her girişte bir raporun reçetesi, rakamları ve bizim projeye ne söylediği var.

**Kaynak notu:** Bütün rakamlar yazarların kendi raporlarından alındı. Bir rakam bulunamadıysa yazılmadı. ByteDance'in Seed2.0 Model Card'ı ([2607.00248](https://arxiv.org/abs/2607.00248), Haziran 2026) bulundu ama özetinde post-training reçetesi yok, bu yüzden listeye alınmadı.

**Bu bölümün ana dersleri:**
- Büyük modellerde ortak kalıp şu: ortak bir SFT, alan başına ayrı RL ile uzman modeller, sonra bu uzmanları tek modelde toplamak.
- RL verisi, modelin "bazen çözdüğü" sorulardan oluşmalı; hep çözülen ya da hiç çözülemeyen sorular öğrenme sinyali vermiyor.
- Cevabı kesin kontrol eden bir doğrulayıcı (testler, Lean, gerçek çalıştırma) RL'in en değerli parçası; zayıf bir doğrulayıcı bütün eğitimi bozabiliyor.
- Güçlü bir SFT'den başlayan RL'in tavanı daha yüksek; yalnızca formatı öğreten hafif bir SFT yetmiyor.
- Büyük model hazırsa, küçük modelin kendi denemelerini büyük modelin her token'da puanlaması (on-policy distillation) çok uzman eğitmenin en ucuz karşılığı.

**Makaleler:**
- MiMo-V2.6 — Xiaomi'nin tek büyük agentic RL koşusu ve Qwen3.5-9B'ye distill edilmiş açık model.
- Hunyuan-A13B — Tencent'in dört aşamalı post-training'i; hızlı ve yavaş düşünme modu.
- Ling and Ring 2.6 — Ant'ın uzman eğit, sonra distill et pipeline'ı ve KPop token maskesi.
- Scaling Reasoning Tokens via RL and Parallel Thinking — competitive programming'de doğrulama ısınması ve paralel düşünme.
- Beyond Length Scaling (Mix-GRM) — göreve göre farklı biçimde düşünen 8B reward model.
- GLM-5 — sıralı RL aşamaları ve unutmaya karşı cross-stage distillation.
- Step 3.5 Flash — alan uzmanları, tek modelde birleştirme ve MIS-PO algoritması.
- ERNIE 5.0 — çok kipli RL; entropi önlemleri ve ipucuyla öğrenme.
- LongCat-Flash-Thinking-2601 — 10,000'den fazla otomatik ortam ve bilerek gürültü eklenmiş agentic RL.
- MiMo-V2-Flash — çok uzmanlı on-policy distillation (MOPD).
- Seed-Prover 1.5 — Lean'de tool kullanan agentic RL ile ispat.
- DRIVE — competitive programming RL'inde veri seçimi ve zor sorulara odaklanan curriculum.
- Ling 2.0 — DFT, Evo-CoT, LPO ve Group Arena Reward yöntemleri.
- Ring-1T — trilyon parametrede RL; IcePop ve C3PO++.
- LongCat-Flash-Thinking — alan uzmanlarını ağırlık birleştirmeyle toplama.
- GLM-4.5 — uzmanları self-distillation ile birleştirme; agentic RL kuralları.
- Seed-Prover — Lean geri bildirimiyle ispatını düzelten model.
- GLM-4.1V-Thinking ve GLM-4.5V — görsel-dil modelinde curriculum sampling'li RL.
- Truncated Proximal Policy Optimization (T-PPO) — rollout bitmeden PPO güncellemesi.
- MiMo-VL — görsel modelde RLVR ve RLHF'yi tek on-policy koşuda birleştirme.
- Seed-Coder — verisini büyük ölçüde LLM'lerin seçtiği 8B kod modeli.
- Hunyuan-TurboS — soruya göre kısa ya da uzun düşünme; iki aşamalı GRPO.
- MiMo — 7B reasoning modeli; base'den RL ile SFT'den RL karşılaştırması.
- VAPO — value modelli PPO'yu uzun CoT'de kararlı çalıştırma.
- Seed1.5-Thinking — 200B MoE reasoning modeli ve LLM verifier'lar.
- DAPO — GRPO'ya dört düzeltme getiren açık kaynak RL sistemi.

---

## MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement (Xiaomi, Ekim 2026) — [2610.11959](https://arxiv.org/abs/2610.11959)
**Tek cümlede:** Xiaomi, iki büyük modeli kısa bir SFT'den sonra tek ve çok büyük bir agentic RL koşusuyla eğitti; aynı reçeteyi Qwen3.5-9B üzerinde açık bir modelle de gösterdi.

**Problem:** Agent görevlerinde (kod düzeltme, terminalde iş yapma) model uzun bir tool çağrısı zinciri kurar. Böyle görevlerde RL'i büyütmek zordur. Tek bir deneme uzun sürer, reward çoğu zaman yalnızca "testler geçti mi" diye ikili gelir ve model reward'ı hileyle kazanmanın yollarını bulur. Yazarlar RL compute'unu artırınca modelin iyileşmeye devam edip etmediğini görmek istedi.

**Ne yaptılar:**
1. **Modeller.** MiMo-V2.6-Pro 1.02T toplam, 42B aktif parametreli; Flash 310B toplam, 15B aktif. İkisi de [MoE](00_terimler.md#moe): model birçok "uzman" alt ağdan oluşur ve her token için yalnızca birkaçı çalışır. "Aktif" parametre, bir token'da gerçekten kullanılan kısımdır.
2. **Kısa SFT, sonra tek bir karışık [agentic RL](00_terimler.md#agentic-rl-ve-multi-turn) koşusu.** Agentic RL'de model çok adımlı bir görevde tool çağırır, sonunda görevin sonucu puanlanır. Görev karışımı: kod %68, genel tool use %12, tasarım %13, context following (bağlamdaki talimata uyma) %3, siber güvenlik %4.
3. **RL compute'unu üç eksende büyütme.** Büyük batch, çok sayıda agent ortamı ve uzun görevlerde daha doğru reward veren "groupwise" değerlendirme (aynı görevin denemelerini birlikte değerlendirme). Her RL adımında 1,568 prompt × 16 [rollout](00_terimler.md#rollout) var. Rollout, modelin bir prompt için ürettiği tek bir denemedir; bizde bir sorunun tool çağrılarıyla baştan sona çözümü. Bu, adım başına yaklaşık 25K trajectory ve 2.7–3.7B token eder.
4. **Algoritma: [GRPO](00_terimler.md#grpo).** GRPO aynı prompt için bir grup deneme üretir. Grubun ortalamasından iyi olan denemeleri güçlendirir, kötüleri zayıflatır. Ayrı bir değer modeli gerekmez. Ayarlar:
   - Prompt-mean loss: loss önce her prompt'un kendi denemeleri içinde ortalanıyor.
   - Asenkron partial rollout, staleness 4: rollout'lar eğitimle eşzamanlı üretiliyor ve bir deneme en fazla 4 güncelleme eski bir modelden gelebiliyor. Bu biraz [off-policy](00_terimler.md#on-policy-ve-off-policy) bir eğitim demek: denemeyi üreten model ile eğitilen model tam aynı değil.
   - lr (learning rate, öğrenme hızı) 3e-6.
   - [Importance sampling](00_terimler.md#importance-sampling) oranının kırpılması: eski ve yeni modelin bir token'a verdiği olasılıkların oranı, eski modelden gelen veriyi düzeltmek için kullanılır. Bu oran [clip](00_terimler.md#clip-ve-clip-higher)leniyor, yani bir aralıkla sınırlanıyor. Aralık [0.2, 5.0] ile başlıyor, sonra [entropy](00_terimler.md#entropy-ve-entropy-collapse)'ye (modelin seçimlerindeki belirsizlik) göre ayarlanıyor.
   - MoE router (her token'ı hangi uzmana yollayacağını seçen parça) RL boyunca dondurulmuş.
   - [Dynamic sampling](00_terimler.md#dynamic-sampling): bütün denemeleri geçen ya da bütün denemeleri kalan gruplar atılıyor. Grupta fark yoksa öğrenecek bir şey de yok.
5. **[Reward](00_terimler.md#reward) tasarımı.** Temel reward ikili test reward'ı: testler geçerse 1, geçmezse 0. Üstüne şunlar ekleniyor:
   - GRS: [pass rate](00_terimler.md#pass-rate-ve-passk)'i (denemelerin geçme oranı) yüksek görevlerde ikili reward, çözüm ve davranış [rubric](00_terimler.md#llm-as-judge-ve-rubric) puanlarıyla çarpılıyor. Rubric, bir değerlendiricinin maddelere göre verdiği puandır. Yani görev kolaysa "geçti" yetmiyor; nasıl geçtiğine de bakılıyor.
   - GAR: geçen trajectory'leri bir grader (değerlendirici model) kaliteye göre sıralıyor. Pozitif [advantage](00_terimler.md#advantage) daha kaliteli olanlara kaydırılıyor. Advantage, bir denemenin grubun ortalamasından ne kadar iyi olduğudur; güncellemenin yönünü ve gücünü belirler. Hile tespit edilen denemenin reward'ı 0.
   - Uzunluk cezası: gruptaki bir referansa göre fazla uzun deneme cezalanıyor.
   - Format ve tool-call hatalarına segment düzeyinde ceza: bütün deneme değil, hatanın olduğu parça cezalanıyor.
6. **[Reward hacking](00_terimler.md#reward-hacking)'e karşı önlemler.** Reward hacking, modelin görevi çözmeden reward'ı kazanmasıdır (ör. testleri değiştirmek). Ortam temizlendi (git geçmişi ve build artifact'ları), ağ izole edildi ve ortamdaki açıkları bilerek arayan ayrı bir "hack agent" çalıştırıldı.
7. **9B model.** Qwen3.5-9B, MiMo'nun ürettiği 77.4B token'lık veriyle SFT'den geçti; bu token'ların 27.2B'si loss'a giriyor, gerisi [loss-masking](00_terimler.md#loss-masking) ile dışarıda kalıyor. Bu bir [distillation](00_terimler.md#distillation): büyük modelin çıktılarıyla küçük modeli eğitmek. Sonra yayımlanan ~7K görevle alan başına GRPO yapıldı. Model, ortamlar ve RL kodu açık.

**Sonuç:** Yazarların raporuna göre:
- DeepSWE v1.1 (yazılım mühendisliği görevlerinden oluşan bir agent testi; bu dosyadaki testlerin kısa açıklamaları için bkz. [benchmarklar](00_terimler.md#benchmarklar)) RL boyunca Pro'da 58.4'ten 72.6'ya, Flash'ta 48.7'den 65.7'ye çıktı. RL iki modelde de 14–17 puan ekledi.
- GAR ablation'ı (Flash, yalnızca kod görevleri): online grader olmadan tur sayısı ve cevap uzunluğu hızla büyüdü, pass rate kazancı durdu. GAR açıkken kazanç sürdü ve daha az hileli çözüm çıktı. Yani yalnız "geçti mi" diye bakan reward modeli uzun ve hileli çözümlere itiyor.
- 9B model (temel → SFT → RL): SWE-bench Verified (gerçek GitHub hatalarını kod değişikliğiyle düzeltme; testlerle kontrol edilir) 60.0 → 61.1 → 66.2; Terminal Bench 2.1 (terminalde komutlarla görev bitirme) 27.0 → 37.1 → 52.8. SWE-bench'te SFT yalnızca 1.1 puan, RL 5.1 puan ekledi; Terminal Bench'te RL'in katkısı daha da büyük.
- RL, raporlanan 11 değerlendirmenin hepsinde SFT'yi geçti.
- Grader'ın maliyeti RL bütçesinin %12.7'si.

**Bizim için:** 9B'lik model için de kalıp aynı: önce büyük modelin trajectory'leriyle SFT, sonra az sayıda (binlerce) doğrulanabilir görevle GRPO. Doğru cevaplar arasında "temiz" olanı ödüllendirmek (ör. gereksiz `execute_sql` sayısı az olanı) uzunluk ve tur şişmesini engelliyor.

## Hunyuan-A13B Technical Report (Tencent, Eylül 2026; model Haziran 2025'te çıktı) — [2609.27284](https://arxiv.org/abs/2609.27284)
**Tek cümlede:** Tencent, 80B toplam / 13B aktif bir MoE modelini dört aşamalı post-training ile hem hızlı hem yavaş düşünebilen bir modele çevirdi.

**Problem:** Bir model kolay soruya kısa cevap vermeli, zor soruda uzun düşünmeli. Ayrıca RL verisinin kalitesi kritik. Yanlış etiketli sorular ya da tahminle doğru bilinebilen sorular modele yanlış şey öğretir.

**Ne yaptılar:**
1. **Dört aşama sırayla:** reasoning SFT → reasoning RL → all-scenarios SFT (her tür görev) → all-scenarios RL. Model iki [thinking mode](00_terimler.md#thinking-mode) arasında geçebiliyor: `/no_think` ile hızlı, `/think` ile yavaş (önce uzun düşünerek) cevap.
2. **Reasoning SFT verisi.** Yalnızca doğrulanmış soru–cevap çiftleri tutuldu. Veri [rejection sampling](00_terimler.md#rejection-sampling) ile kuruldu: çok sayıda cevap üretilir, kontrolden geçemeyenler atılır. Kontrol alana göre değişiyor:
   - Matematikte generative [reward model](00_terimler.md#reward-model-grm-ve-prm) (karar vermeden önce gerekçe yazan değerlendirici model) ve otomatik doğrulama.
   - Kodda critic model ve sandbox (kodu güvenli bir ortamda gerçekten çalıştırma).
   - Mantıkta sentetik bulmacalar (cevabı bilinen, üretilmiş bulmacalar).
   - Fende birim ve sayıyı kontrol eden bir LLM verifier.
3. **Reasoning RL.** GRPO, [KL penalty](00_terimler.md#kl-penalty) yok (modelin başlangıç modelinden uzaklaşmasını cezalandıran terim kullanılmadı). 150K prompt. Bu prompt'lar SFT modelinin "kararsız" olduğu, yani bazen çözüp bazen çözemediği sorulardan seçildi. Oran matematik:kod:mantık:fen = 2:2:1:1. SFT verisiyle örtüşme ~%10.
4. **Tahminle kazanılan reward'ı engelleme.** Çoktan seçmeli, doğru/yanlış ve ispat soruları çıkarıldı. Örnek: dört şıklı bir soruda rastgele seçim dörtte bir doğru çıkar; model düşünmeden reward kazanır. İspatın doğruluğu ise otomatik kontrol edilemez.
5. **[Curriculum](00_terimler.md#curriculum)** (eğitimi kolaydan zora sıralama): önce 24K, sonra 32K context. Sampling temperature 0.6–0.8.
6. **Agent verisi.** All-scenarios SFT'deki agent verisi beş rollü bir motorla üretildi: user, planner, tool, agent, checker. 30'dan fazla sistem talimatı tipi ve 20,000 format kombinasyonu var.
7. **Agent reward'ı** iki parçanın toplamı: format (0 ya da 1) ve tool, parametre ve değer tutarlılığı (doğru tool doğru argümanlarla mı çağrıldı).

**Sonuç:** Yazarların raporuna göre yavaş modda AIME2024 (Amerikan lise matematik olimpiyatı elemesi soruları) 87.3, BFCL v3 (Berkeley Function Calling Leaderboard: tool/fonksiyon çağırma doğruluğu) 78.3, ZebraLogic (mantık bulmacaları) 84.7. Hızlı modda AIME2024 30.6. Yani zor matematikte düşünmeden cevap vermek skoru 87.3'ten 30.6'ya düşürüyor; uzun düşünme bu sorularda belirleyici.

**Kaynak notu:** Raporda post-training aşamalarının katkısını ayıran ablation yok; hangi aşamanın ne kadar kazandırdığı bilinmiyor. Rapor Eylül 2026 tarihli, model ise Haziran 2025'te çıktı.

**Bizim için:** RL prompt'larını SFT modelinin "bazen çözdüğü" sorulardan seçmek ve tahminle geçilebilecek soruları atmak, BIRD train'den RL kümesi kurarken doğrudan uygulanabilir. Tool çağrısına format + argüman reward'ı da bizim `execute_sql`/`submit` çağrılarına uyar.

## Ling and Ring 2.6 Technical Report (Ant Group / Inclusion AI, Haziran 2026) — [2606.15079](https://arxiv.org/abs/2606.15079)
**Tek cümlede:** Ant Group iki model ailesini (hızlı Ling-2.6 ve derin düşünen Ring-2.6) alan uzmanları eğitip tek modele distill ederek kurdu ve agentic RL için KPop adlı yeni bir token maskesi önerdi.

**Problem:** Ling-2.0 temeli mimari bir geçişle yükseltildi ve büyük ölçekli agentic post-training yapıldı. İki ayrı ihtiyaç var: hızlı ve az token harcayan cevap (Ling-2.6) ile derin düşünme ve agentic iş akışları (Ring-2.6). Agentic RL'de eğitim ve inference motorlarının olasılık farkını yöneten IcePop'un (Ring-1T girişinde anlatılıyor) düşük olasılıklı token'ları gereğinden fazla maskelediğini düşündüler.

**Ne yaptılar:**
1. **Pipeline:** [cold-start](00_terimler.md#cold-start) SFT (RL'den önce modele temel davranışı öğreten başlangıç SFT'si) → alan başına uzman SFT → her uzmana RL → uzmanları tek modele distillation.
2. **SFT verisinin zorluğu** modelin pass rate'ine göre ayarlandı.
3. **Ling'in reasoning RL'i: Evo-CoT reward'ı.** [CoT](00_terimler.md#cot-ve-long-cot), modelin cevaptan önce yazdığı adım adım düşünme metnidir. Reward parçaları:
   - doğru cevaba +1;
   - cevapta açık bir reasoning işareti varsa −0.5 (Ling hızlı cevap için tasarlandı);
   - zorluğa bağlı bir uzunluk terimi: doğru cevapta pozitif, yanlış cevapta en fazla 0;
   - anlamsal tekrara ceza (tekrarı bir LLM değerlendiriyor).
   Veri düzeyinde de her soru için en kısa doğru aday tutuldu. Bu, cevapları ortalama 200–300 token kısalttı.
4. **Agentic RL.** Algoritma GSPO: GRPO'ya benzer ama kırpmayı token yerine bütün dizi düzeyinde yapar. Tool-call trajectory'si için process reward var (yalnız sonuç değil, ara adımlar da puanlanıyor). Tekrar cezası zlib sıkıştırma oranıyla hesaplanıyor: tekrarlı metin çok iyi sıkışır, yüksek sıkışma tekrarı gösterir.
5. **Dynamic Pass Rating ile curriculum.** Görevlerin zorluğu sabit bir geçmiş pass rate'e göre değil, eğitim sırasındaki davranışa göre belirleniyor. Eğitimin başında çözülen ya da hep yüksek pass rate'li görevler kolay sayılıyor. Çözülemeyen ya da sonucu dalgalanan görevler zor sayılıp öne alınıyor. Böylece eğitim, modelin o anki sınırındaki görevlere yoğunlaşıyor.
6. **Ring'in SWE verisi.** ~300K PR–issue çifti süzüldü. Pass rate'i 0.1–0.9 arasında olanlar tutuldu; yani neredeyse hep çözülen ve neredeyse hiç çözülemeyenler atıldı. Çeşitlilik için repo başına en fazla 3 örnek alındı. Sonuç: 1,550 repodan ~2,500 örnek.
7. **Agent arayüzü** üç tool: `execute_bash`, `search_replace`, `task_done`. Eğitimde bir görev 200 tura kadar sürebiliyor.
8. **KPop.** Eğitim motoru ile inference motoru aynı token'a biraz farklı olasılık verebilir. IcePop bu farkı her token'a aynı sabit oran aralığıyla sınırlıyor. KPop bunun yerine her token için ikili bir KL farkı ölçüyor: kelime dağarcığını "örneklenen token" ve "geri kalan her şey" diye iki olaya bölüyor ve iki motorun bu iki olaya verdiği olasılıkları karşılaştırıyor. Fark her iki yönde de φ eşiğinin altındaysa token eğitimde kalıyor; aşarsa gradient'ten çıkarılıyor. Bütün mekanizmayı tek bir sayı (φ) yönetiyor.

**Sonuç:** Yazarların raporuna göre:
- KPop, SWE-bench Verified'da çözme oranını 70.8'den 76.28'e çıkardı (3 koşu ortalaması); yaklaşık 5.5 puanlık bir kazanç.
- LM head'i (modelin son, token olasılıklarını üreten katmanı) eğitimde ve inference'ta FP32 hassasiyette tutmak reward'da ~+2 puan getirdi. Yani iki motorun sayısal farkını azaltmak tek başına ölçülebilir bir kazanç.
- Trajectory'lerin ~%0.2'sinde hile görüldü.
- Ring-2.6-1T: AIME26 (2026 Amerikan matematik olimpiyatı elemesi) 95.78, SWE-bench Verified 74.00.
- Ling-2.6-1T token verimliliğinde Ling-2.0-1T'nin ~4 katı: aynı işi yaklaşık dörtte bir token'la yapıyor.

**Kaynak notu:** Raporda 70.8'lik koşunun hangi yöntemle yapıldığı (IcePop mu, başka bir ayar mı) yazılmıyor; bu yüzden KPop'un tam olarak neye karşı 5.5 puan kazandırdığı belirsiz. φ'nin değeri de raporlanmamış.

**Bizim için:** RL kümesinde pass rate'i 0.1–0.9 arasında olan soruları tutmak ve veritabanı başına soru sayısını sınırlamak (repo başına 3 kuralının BIRD karşılığı: `db_id` başına sınır) küçük ama çeşitli bir RL kümesi verir. Üç tool'lu sade bir arayüz bizimkiyle aynı yapıda.

## Scaling Reasoning Tokens via RL and Parallel Thinking: Evidence From Competitive Programming (ByteDance Seed, Nisan 2026) — [2604.01302](https://arxiv.org/abs/2604.01302)
**Tek cümlede:** ByteDance Seed, competitive programming'de modelin düşünmeye harcadığı token sayısını RL ve test anında paralel düşünmeyle büyüttü ve doğruluğun bu sayıyla düzenli arttığını gösterdi.

**Problem:** Daha uzun düşünen model daha mı iyi çözer, ve bu nasıl büyütülür? Competitive programming (algoritma yarışması problemleri) iyi bir deney alanı, çünkü cevap testlerle kesin kontrol edilir. Ayrıca çözüm üretmek kadar çözümün doğru olup olmadığını anlamak da önemli: model test anında kendi çözümlerini seçecekse iyi bir doğrulayıcı olmalı.

**Ne yaptılar:**
1. **Başlangıç.** Temel model Seed-OSS-36B-Base. ~6K trajectory'lik cold-start SFT.
2. **RL.** ~10K competitive programming problemiyle asenkron GRPO; en fazla 1 adım off-policy (denemeyi üreten model, eğitilen modelden en fazla bir güncelleme eski). Adım başına 16 problem × 32 rollout, 90K context.
3. **Reward ikili:** bütün testler geçerse +1. Uzunluk sınırını aşan cevap yanlış sayılıyor.
4. **Verification RL warmup.** Önce model, ~160K aday çözümün doğru olup olmadığını tahmin etmeye RL ile eğitiliyor. Bu adayların etiketi kodlar gerçekten çalıştırılarak bulundu. Asıl generation RL (çözüm üretme) bu checkpoint'ten başlıyor. Fikir: önce "bu çözüm doğru mu" sorusunu öğren, sonra çözmeyi öğren.
5. **Randomized clipping.** Uzunluk sınırı sabit değil; her seferinde 60K ile 90K arasından rastgele (uniform) bir sınır çekiliyor. Örnek: bir denemede sınır 72K, sonrakinde 85K olabilir.
6. **Paralel düşünme.** Bu bir [test-time scaling](00_terimler.md#test-time-scaling) yöntemi: test anında daha çok hesap harcayıp doğruluğu artırmak. N thread × M tur çalışıyor; her thread her turda çözüm üretiyor, doğruluyor ve düzeltiyor. Pipeline'ın tamamı uçtan uca RL ile eğitildi. Her turun kendi reward'ı var. γ=0 seçildi: bir turun reward'ına sonraki turların sonucu eklenmiyor. GRPO grupları tur bazında kuruluyor; aynı turdaki denemeler kendi aralarında karşılaştırılıyor.

**Sonuç:** Yazarların raporuna göre:
- Doğruluk, ortalama üretilen token sayısıyla yaklaşık log-lineer arttı: token sayısı her katlandığında doğruluk yaklaşık sabit bir miktar artıyor.
- Verification warmup ile generation RL'in ulaştığı tavan ~0.33'ten ~0.38'e çıktı. Doğrulama precision'ı ("doğru" dediği çözümlerin gerçekten doğru olma oranı) 0.78'den 0.89'a yükseldi.
- Tam sistem (16 × 16) AetherCode'un (zor competitive programming problemlerinden oluşan test) 456 zor probleminde ~0.61'e ulaştı; GPT-5-high ~0.46. Parçaları ayrı ayrı eğitilen pipeline ~0.60'ta kaldı; uçtan uca eğitim yalnızca küçük bir fark yarattı.
- Doğrulamayı 1 yerine 8 kez yapmak (V=1'den V=8'e) skoru 0.43'ten 0.48'e taşıdı. Yazarlara göre asıl darboğaz verifier'ın kalitesi.
- Maliyet: ortalama ~100K token uzunluğunda bir RL adımı 256 A100 GPU'da ~4 saat sürüyor.

**Bizim için:** Küçük modeli önce "bu SQL sonucu doğru mu" kararına RL ile ısıtmak, generation RL'in başlangıç noktasını yükseltebilir. Bu, bizim large model kontrolünü (final check) zamanla küçük modelin kendisine öğretmenin bir yolu. Uzun bağlam pahalı olduğundan budget'ı kısa tutmak gerekir.

## Beyond Length Scaling: Synergizing Breadth and Depth for Generative Reward Models (Tencent Hunyuan, MBZUAI, CityU HK, Mart 2026) — [2603.01571](https://arxiv.org/abs/2603.01571)
**Tek cümlede:** Yazarlar, göreve göre farklı biçimde düşünen 8B'lik bir generative reward model (Mix-GRM) eğitti: öznel tercihlerde geniş, objektif doğrulukta derin düşünme.

**Problem:** Generative reward model (GRM), bir cevabı puanlamadan önce gerekçe yazan bir LLM'dir. GRM'leri iyileştirmenin yaygın yolu gerekçeyi uzatmaktır. Yazarlar uzunluktan çok gerekçenin biçiminin önemli olduğunu savundu. "Hangi cevap daha yardımcı" gibi öznel sorularda birçok farklı ölçütü taramak gerekir. "Bu çözüm doğru mu" gibi objektif sorularda ise problemi kendin çözüp derinlemesine kontrol etmek gerekir.

**Ne yaptılar:**
1. **Gerekçeleri birimlere bölme.** Gerekçeler "Principle–Judgment–Verdict" birimlerine çevrildi: bir ilke (ör. "cevap soruyu doğrudan karşılıyor mu"), o ilkeye göre bir yargı ve bir karar.
2. **Breadth-CoT (B-CoT, genişlik).** Birden çok bağımsız gerekçe örnekleniyor. İlkeler birleştirilip tekrarlar atılıyor; az geçen ilkeler de atılıyor. Sonuç, birçok açıdan bakan tek bir gerekçe.
3. **Depth-CoT (D-CoT, derinlik).** Önce sorunun çözüm izi üretiliyor; değerlendirici problemi kendisi çözüyor. Sonra bu ize dayanarak en fazla üç ilke yeniden değerlendiriliyor.
4. **Veri.** Temel model Qwen3-8B-Base. Gerekçe sentezi DeepSeek-V3 ile (temperature 0.8). Toplam ~30K örnek: 9K SFT ve 21K RLVR. RLVR (RL with verifiable rewards), reward'ı otomatik kontrol edilebilen RL'dir; burada kontrol, kararın etiketle eşleşmesi. Kaynak veri setleri: HelpSteer3, Code-Preference, Math-DPO, WildGuard, OffsetBias.
5. **RLVR ayarları.** GRPO; karar etiketle eşleşirse +1, eşleşmezse −1. 100 adım, lr 1e-6, batch 128, prompt başına 8 rollout, KL katsayısı 0.001.

**Sonuç:** Yazarların raporuna göre:
- Beş testin ortalamasında Mix-GRM SFT sonrası 75.1, RLVR sonrası 79.4. Karşılaştırma modeli Base-GRM 73.3 → 76.9. Mix-GRM iki aşamada da yaklaşık 2 puan önde.
- Açık kaynak reward model'leri ortalama %8.2 geçti.
- MATH (yarışma matematiği problemleri) best-of-10 yeniden sıralama: bir modelin 10 cevabından GRM'in en iyi bulduğu seçiliyor. Mix-GRM ile doğruluk %43.2, RM-R1 ile %37.7.
- Ablation: tercih alanında yalnızca genişlik +1.1, yalnızca derinlik −2.3 getirdi; doğruluk alanında durum tersine. Yani göreve uymayan düşünme biçimi zarar veriyor.
- Görev ile CoT tipinin eşleşme oranı (model göreve uygun tipi seçiyor mu) SFT'den sonra %73, RLVR'dan sonra %95. RL, modele hangi görevde nasıl düşüneceğini öğretti.
- Etiketle çelişen örnekleri süzmemek zarar vermedi (70.1'e karşı 69.8; fark önemsiz).

**Bizim için:** Large model kontrolünü (final check) zamanla küçük bir yerel verifier'a taşımak istersek, ~9K SFT + ~21K RLVR ve 100 adımlık bir bütçe 8B ölçeğinde yetiyor. Doğruluk kararı için "önce kendi çözüm izini üret, sonra karar ver" (D-CoT) bizim SQL kontrolüne uygun.

## GLM-5: from Vibe Coding to Agentic Engineering (Zhipu AI & Tsinghua, Şubat 2026) — [2602.15763](https://arxiv.org/abs/2602.15763)
**Tek cümlede:** Zhipu, 744B toplam / 40B aktif bir MoE modelini dört ardışık aşamayla eğitti ve sonda, önceki aşamalarda unutulan becerileri ucuz bir on-policy distillation ile geri kazandı.

**Problem:** RL aşamaları art arda yapılınca (önce reasoning, sonra agent, sonra genel) model yeni beceriyi öğrenirken eskisini unutabilir. Ayrıca agentic RL'i büyük ölçekte kararlı çalıştırmak zor: inference ile eğitim ayrı makinelerde çalışınca olasılıklar ayrışır, sandbox'lar çöker, eski trajectory'ler eğitimi bozar.

**Ne yaptılar:**
1. **Aşamalar:** SFT → Reasoning RL → Agentic RL → General RL → sonda on-policy cross-stage distillation.
2. **SFT.** Üç kategori: genel sohbet, reasoning, kod ve agent. Context 202,752 token'a kadar. Trajectory'lerdeki hatalı parçalar veride tutuluyor ama loss'tan maskeleniyor: model hatayı ve sonrasını görüyor, ama hatayı üretmeyi öğrenmiyor.
3. **Reasoning RL.** GRPO + IcePop, KL yok, tamamen [on-policy](00_terimler.md#on-policy-ve-off-policy) (her deneme o anki modelden). Ayarlar:
   - IcePop'a benzer bir maske: eğitim ve inference motorlarının bir token'a verdiği olasılık oranı 1/β ile β arasında değilse token sıfırlanıyor. β=2, yani [0.5, 2] dışındaki token'lar atılıyor.
   - ε_low=0.2, ε_high=0.28: güncelleme oranının alt ve üst kırpma sınırları. Üst sınırın daha geniş olması (clip-higher) az olası ama iyi token'ların daha hızlı güçlenmesine izin verir.
   - Group ve batch boyutu 32.
   - Matematik, fen, kod ve tool-integrated reasoning (düşünürken tool kullanma) yaklaşık eşit karıştırıldı.
   - Zorluk filtresi: GLM-4.7'nin nadiren çözdüğü ama daha güçlü büyük modellerin çözebildiği problemler tutuldu. Yani hem zor hem çözülebilir sorular.
   - Reward, alan başına judge'lardan gelen ikili sonuç.
4. **Agentic RL.** Tamamen asenkron: inference ve training ayrı GPU'larda. Kararlılık için:
   - token-in-token-out gateway (model ile ortam arasında metin yerine token'ların taşınması, böylece tokenizer farkı oluşmuyor);
   - çift yönlü importance sampling kırpması;
   - çok eski trajectory'lerin atılması;
   - sandbox çöktüğü için yarım kalan örneklerin eğitimden çıkarılması.
   Ortamlar: 9 dilde 10,000'den fazla doğrulanabilir SWE ortamı, binlerce terminal ortamı ve çok adımlı arama soruları.
5. **Cross-stage distillation.** Önceki aşamaların son checkpoint'leri büyük model rolünde. Eğitilen model kendi cevabını üretiyor. Her token için advantage yerine şu kullanılıyor: önceki checkpoint'in o token'a verdiği olasılık ile eğitilen modelin verdiği olasılığın log oranı. Bu değer sabit tutuluyor (stop-gradient, yani üzerinden gradient akmıyor). Advantage artık grup ortalamasından değil bu farktan geldiği için prompt başına tek deneme yetiyor: group size 1, batch 1024.

**Sonuç:** Yazarların raporuna göre:
- Arama görevlerinde bağlamda yalnızca son 5 turu tutmak BrowseComp'u (web'de bulunması zor bilgileri arama testi) 55.3'ten 62.0'a çıkardı. Karma bir bağlam stratejisi en büyük bütçede 75.9'a ulaştı. Yani eski turları atmak, bağlamı doldurmaktan daha iyi.
- Non-deterministic top-k operatörleri (DSA indexer'da, aynı girdiye her seferinde aynı sonucu vermeyen işlemler) RL'de performans çöküşüne yol açtı. Deterministik `torch.topk` kullanmak gerekli oldu.

**Bizim için:** Ardışık RL aşamalarında unutmayı önlemek için ucuz bir çözüm, önceki checkpoint'i referans alıp tek örnekle on-policy distillation yapmak. "Sandbox hatasından düşen örneği eğitimden çıkar" kuralı `execute_sql` zaman aşımları için de geçerli.

## Step 3.5 Flash: Open Frontier-Level Intelligence with 11B Active Parameters (StepFun, Şubat 2026) — [2602.10604](https://arxiv.org/abs/2602.10604)
**Tek cümlede:** StepFun, 196B toplam / 11B aktif bir modelde önce alan başına uzmanlar kurdu, sonra onları tek modelde topladı ve RL için MIS-PO adlı bir algoritma önerdi.

**Problem:** Tek bir modelin matematik, kod, tool use, uzun context ve insan tercihi gibi çok farklı alanlarda iyi olması gerekiyor. Hepsini tek RL koşusunda eğitmek alanların birbirini bozmasına yol açabilir. Ayrıca büyük MoE modellerde RL, eğitim ve inference farkı yüzünden gürültülü ve kararsız olabiliyor.

**Ne yaptılar:**
1. **SFT.** 9 alanda 871K örnek (7.23B token). En çok örnek genel alanda (314,495) ve tool use'ta (114,507). Zorluğa göre filtrelendi ve alanlar dengelendi.
2. **İkinci SFT aşaması.** ~30K uzman düzeyi kimya trajectory'si ve sentetik aritmetik görevleri 3 epoch eğitildi.
3. **Tool verisi.** Gerçek ortamlarda "örnekle → çalıştır → doğrula" döngüsü ve rejection sampling ile 100K'dan fazla trajectory üretildi.
4. **Arama verisi filtresi.** DeepSeek-R1'in tool kullanmadan çözebildiği sorular atıldı. Böylece kalan sorular gerçekten arama gerektiriyor.
5. **Uzmanlar ve birleştirme.** Ortak SFT temelinden alan başına RL ile uzmanlar kuruldu (matematik, kod, STEM, tool use, uzun context, insan tercihi, agentic reasoning). Bunlar self-distillation (uzmanların çıktılarıyla tek modeli eğitme) ve ölçekli RL ile tek modelde birleştirildi.
6. **MIS-PO algoritması.** Normalde eski modelden gelen veri, importance ağırlığıyla (iki modelin olasılık oranı) çarpılarak düzeltilir. MIS-PO bunun yerine ikili bir maske kullanıyor: örnek ya tam ağırlıkla giriyor ya hiç girmiyor. İki koşul var: token düzeyinde oran [0.5, 2] içinde olmalı; trajectory düzeyinde oranların geometrik ortalaması [0.996, 1.001] içinde olmalı. Dışındaysa örnek eğitime girmiyor.
7. **RL ayarları.** Algoritma [PPO](00_terimler.md#ppo) tarzı: bir actor (eğitilen model) ve bir critic (her durumun beklenen reward'ını tahmin eden value modeli) var. Rollout boyutları: reasoning 256 prompt × 16, insan tercihi 512 × 8, tool use 128 × 8. Max uzunluk 128K. Actor lr 2e-6, critic lr 5e-6. γ=λ=1: advantage hesaplanırken gelecekteki bütün reward'lar indirimsiz sayılıyor. Uzunluk sınırında kesilen cevaplara 0 reward yerine critic'in value tahmini veriliyor; yani "bitmedi" diye cezalandırılmıyor.
8. **Reward kaynakları.**
   - Kural tabanlı checker'lar.
   - STEM için model tabanlı verifier.
   - İnsan tercihi için pairwise GenRM: iki cevabı karşılaştırıp hangisinin iyi olduğuna karar veren generative reward model.
   - MetaRM: doğru cevaba mantık hatalı bir yoldan ulaşan denemeyi cezalandırıyor.
   - Agent görevlerinde rubric'e dayalı reward.

**Sonuç:** Yazarların raporuna göre:
- Model tabanlı STEM verifier'la eğitim, kural tabanlı math-verify kütüphanesiyle eğitimi 450 adımda ortalama %2.0 geçti.
- MetaRM, GenRM'i %0.5–3 iyileştirdi.
- MIS-PO, PPO'ya göre daha az gradient gürültüsü ve daha yavaş entropi düşüşü gösterdi. Entropi çok hızlı düşerse model erkenden tek bir cevaba kilitlenir; yavaş düşüş, keşfin sürdüğünü gösterir.
- MoE'de GSPO ~200. iterasyonda platoya girdi; MIS-PO öğrenmeye devam etti.
- Tamamen asenkron agentic RL ~10 kat verim getirdi ve ~20 adım staleness'ta (denemeler 20 güncelleme eski modelden gelse bile) kararlı kaldı.
- IMO-AnswerBench (olimpiyat düzeyi, kısa cevaplı matematik problemleri) 85.4; LiveCodeBench-v6 (yakın zamanda yayımlanmış competitive programming problemleri) 86.4; τ²-Bench (simüle bir müşteriye tool'larla hizmet veren agent testi) 88.2.

**Bizim için:** "Tool'suz çözülebilen soruyu at" filtresi bizde "şemaya bakıp tek seferde doğru SQL yazılabilen soruyu agentic RL'den çıkar" demek; böylece RL, tool kullanımının gerçekten gerektiği sorulara harcanır.

## ERNIE 5.0 Technical Report (Baidu, Şubat 2026) — [2602.04705](https://arxiv.org/abs/2602.04705)
**Tek cümlede:** Baidu, trilyon parametreli ve metin, görüntü gibi birden çok kipi hem anlayan hem üreten bir modeli, reasoning, agent ve talimat takibini birleştiren çok aşamalı bir RL ile eğitti.

**Problem:** Çok farklı görevleri tek RL'de eğitirken üç sorun çıkıyor. Kısa (kolay) cevaplar önce bittiği için asenkron sistemde eğitime daha sık giriyor ve eğitim kolay sorulara kayıyor. Entropi erken çöküyor; model keşfi bırakıp tek bir cevaba kilitleniyor. Zor sorularda hiç doğru deneme çıkmadığı için reward hep 0 ve öğrenme olmuyor.

**Ne yaptılar:**
1. **Genel yapı.** ERNIE 4.5'teki gibi önce SFT, sonra reasoning, agent ve talimat takibini birleştiren çok aşamalı unified multimodal RL (UM-RL).
2. **Unbiased Replay Buffer.** Rollout, RL süresinin %90'ından fazlasını alıyor. Asenkron havuzda her iterasyona bir veri grubu atanıyor ve yalnızca o grubun rollout'ları eğitime giriyor. Böylece önce biten kısa cevaplar sıranın önüne geçemiyor ve zorluk yanlılığı oluşmuyor.
3. **[Entropy collapse](00_terimler.md#entropy-ve-entropy-collapse)'e karşı iki önlem.**
   - MISC: IcePop'a benzer, token düzeyinde bir maskeleme. Yazarlar GSPO'nun dizi düzeyindeki kırpmasının düşük entropili cevapları budadığını ve erken çöküşe yol açtığını gözlemledi; bu yüzden token düzeyine indiler.
   - WPSM: ortalama doğruluğu bir τ eşiğini geçen (yani kolaylaşmış) sorularda, entropisi bir η eşiğinin altındaki rollout'ların ağırlığı α katsayısıyla küçültülüyor. Böylece gradient, zaten çözülen sorulardaki emin cevaplar yerine zor sorulara kayıyor.
4. **Hint-based learning (AHRL).** Reward'ı seyrek olan zor sorularda, doğru reasoning'in başından bir kısmı ipucu olarak prompt'a ekleniyor. İpucunun oranı eğitim ilerledikçe üstel olarak azalıyor. Azalma hızı, sorunun SFT modelindeki başlangıç pass rate'ine bağlı: başta pass rate'i düşük olan sorular ipucunu daha uzun süre tutuyor, kolay olanlar çabuk bırakıyor. Yani zor bir soru önce çözümün başı verilerek soruluyor; model ilerledikçe ipucu kısalıyor ve giderek sıfıra yaklaşıyor.

**Sonuç:** Yazarların raporuna göre AIME 2025 89.06, LiveCodeBench v6 76.21. Talimat takibi testleri MultiChallenge (çok turlu sohbette zor talimatlara uyma) 65.98 ve Multi-IF (çok turlu, çok dilli talimat takibi) 85.56; bu ikisinde listedeki en iyi model.

**Kaynak notu:** RL eklemeleri (replay buffer, MISC, WPSM, AHRL) için sayısal ablation yok, yalnızca grafikler var. Bu yüzden her parçanın ne kadar kazandırdığı rakamla bilinmiyor.

**Bizim için:** Küçük modelin hiç çözemediği BIRD sorularında, gold SQL'in bir parçasını (ör. doğru tablo ya da `search_values` ile bulunan değer) ipucu olarak verip ipucunu zamanla azaltmak, sıfır reward'lı soruları atmak yerine onları öğrenilebilir hale getirir.

## LongCat-Flash-Thinking-2601 Technical Report (Meituan, Ocak 2026) — [2601.16725](https://arxiv.org/abs/2601.16725)
**Tek cümlede:** Meituan, 560B / ~27B aktif modeli otomatik üretilmiş 10,000'den fazla ortamda agentic RL ile eğitti ve ortama bilerek gürültü ekleyerek modeli gerçek dünyadaki hatalara dayanıklı hale getirdi.

**Problem:** Agentic RL için çok sayıda ve çeşitli ortam gerekir; bunları elle kurmak pahalıdır. Ayrıca gerçek dünyada kullanıcı talimatları belirsizdir ve tool'lar hata verir. Temiz ortamda eğitilen agent bu durumlarda dağılabilir.

**Ne yaptılar:**
1. **Otomatik ortamlar.** 20'den fazla alanda 10,000'den fazla ortam, alan başına 60'tan fazla tool'dan oluşan tool graph'larından (tool'ların birbirine nasıl bağlandığını gösteren graf) otomatik üretildi. Tool şemasından çalıştırılabilir tool'a geçişte başarı %95'ten fazla. Her görevde bir açıklama, bir kullanıcı profili ve bir değerlendirme rubric'i var.
2. **Cold start verisi.**
   - Genel thinking verisi perplexity ağırlıklı K-Center-Greedy ile 210K örneğe indirildi. K-Center-Greedy, her adımda seçilmişlere en uzak örneği ekleyerek veri uzayını en iyi kaplayan küçük bir alt küme seçer. Perplexity ağırlığı, modelin şaşırdığı örneklere öncelik verir.
   - Agentic trajectory'ler doğruluğa göre süzüldü.
   - 15K'lık bir özetleme kümesi ~%3 kazandırdı.
3. **RL algoritması.** GSPO. Reward ağırlıkla outcome reward (yalnızca sonucun puanı); uzun trajectory'lere hafif ceza.
4. **Curriculum.** Görevler pass rate'e ve gerektirdiği agentic beceriye göre sıralanıyor.
5. **Rollout bütçesinin dağıtımı.** Heap tabanlı greedy bir yöntemle yapılıyor. Geçmiş pass rate'i düşük görevlerin oversampling katsayısı artıyor; yani zor görevler daha sık deneniyor.
6. **Gürültü curriculum'u.** Belirsiz kullanıcı talimatları, tool hataları ya da kısmi sonuçlar ortama bilerek ekleniyor. Gürültünün zorluğu eğitim boyunca giderek artıyor. Örnek: bir arama tool'u ara sıra boş ya da eksik sonuç döner.
7. **Bağlam yönetimi.** Bağlam 80K token'ı geçince özetleniyor.

**Sonuç:** Yazarların raporuna göre:
- Gürültü ablation'ı (cold start → gürültüsüz RL → gürültülü RL): Tau2Bench-Noise (τ²-Bench'in gürültü eklenmiş sürümü) 58.8 → 62.2 → 67.1; VitaBench-Noise (gerçek hayattan agent görevlerinin gürültülü sürümü) 6.3 → 13.3 → 20.5. Gürültülü RL, gürültüsüz RL'in üstüne 5–7 puan daha ekledi.
- Temiz Tau2Bench de 87.1'den 88.2'ye çıktı; yani gürültü eğitimi temiz ortamdaki başarıyı düşürmedi.
- Bağlam yönetimi BrowseComp'u 55.8'den 73.1'e taşıdı.
- DORA adlı asenkron RL sistemi senkron eğitime göre 2–4 kat hızlı.

**Bizim için:** RL sırasında `execute_sql`'e ara sıra yapay hata ya da boş sonuç eklemek, küçük modelin gerçek hatalardan sonra toparlanmasını öğretebilir. Az örnekli SFT için K-Center-Greedy gibi çeşitlilik odaklı seçim, experience log'dan alt küme seçerken kullanılabilir.

## MiMo-V2-Flash Technical Report (Xiaomi, Ocak 2026) — [2601.02780](https://arxiv.org/abs/2601.02780)
**Tek cümlede:** Xiaomi, 309B / 15B aktif modeli alan uzmanlarından tek modele "çok uzmanlı on-policy distillation" (MOPD) ile topladı ve eğitilen model çoğu alanda uzmanı yakaladı ya da geçti.

**Problem:** Alan başına uzman eğitmek kolay; zor olan bu uzmanları tek modelde birleştirmek. Uzmanların cevaplarıyla düz SFT yapınca eğitilen model kendi hatalarını hiç görmez. RL ise yalnızca deneme sonunda tek bir puan verir, sinyali seyrektir.

**Ne yaptılar:**
1. **Üç aşama:** genel SFT → alan başına RL ya da SFT ile eğitilmiş uzman büyük modeller → [MOPD](00_terimler.md#multi-teacher-distillation-mopd).
2. **SFT.** Milyonlarca örnek, thinking ve non-thinking. lr cosine schedule ile 5e-5'ten 5e-6'ya iniyor. Batch 128.
3. **Agentic uzman verisi.**
   - Code Agent: 90K (gerçek ortam + gerçek prompt) ve 30K (gerçek ortam + sentetik prompt).
   - Search Agent: 150K.
   - General Agent: 50K.
   Kod agent RL'i ~120K ortamda çalıştı; 8 dilde ortam kurulum başarısı %70.
4. **MOPD.** Bu bir [on-policy distillation](00_terimler.md#on-policy-distillation-opd): eğitilen model kendi rollout'larını üretir, büyük model bu rollout'un her token'ını puanlar. Burada büyük model rolünde, prompt'un alanına göre ilgili uzman var. Her token'ın advantage'ı iki parçanın toplamı:
   - Uzmanın o token'a verdiği olasılık ile eğitilen modelin verdiği olasılığın log oranı (sabit tutuluyor, stop-gradient). Uzman o token'ı eğitilen modelden daha olası buluyorsa pozitif, daha az olası buluyorsa negatif. Bu, reverse-KL'den gelen yoğun, token düzeyi bir sinyal.
   - α katsayısıyla çarpılmış, GRPO tipi bir outcome reward advantage'ı (cevabın doğru olup olmadığından gelen).
   Importance ağırlıkları [ε_low, ε_high] aralığında kırpılıyor.

**Sonuç:** Yazarların raporuna göre MOPD öncesi → sonrası (parantezde en iyi uzman modelin skoru):
- AIME 2025: 89.3 → 94.1 (93.9)
- LiveCodeBench: 77.5 → 83.2 (82.6)
- SWE-Bench Verified: 67.8 → 73.4 (74.2)
- Tau2-Bench: 75.9 → 80.3 (79.6)

Yani tek model, dört testin üçünde kendi uzmanını geçti; SWE-Bench'te uzmanın 0.8 puan gerisinde kaldı. Bir kayıp da var: Arena-Hard'ın (zor kullanıcı istekleri; bir LLM judge cevabı referans bir modelle karşılaştırır) yaratıcı yazım kısmı 90.1'den 86.2'ye düştü.

**Bizim için:** On-policy distillation bizde doğrudan kurulabilir: 0.8B modelin kendi trajectory'leri üzerinde 9B modelden token log-prob'ları alınıp küçük bir outcome reward ile birleştirilir. Bu, seyrek reward'lı RL'den çok daha yoğun sinyal verir. Kısıt: API'den token log-prob alınabilmesi gerekir.

## Seed-Prover 1.5: Mastering Undergraduate-Level Theorem Proving via Learning from Experience (ByteDance Seed, Aralık 2025) — [2512.17260](https://arxiv.org/abs/2512.17260)
**Tek cümlede:** ByteDance Seed, Lean'de formal ispat yazan modeli, ispat doğrulayıcısı ve arama tool'larıyla etkileşen bir agent olarak büyük ölçekli agentic RL ile eğitti.

**Problem:** Lean, ispatı bilgisayarın adım adım kontrol ettiği formal bir matematik dilidir; ispat ya geçer ya geçmez, hile yapmak çok zordur. Ama tek seferde tam ispat yazmak zordur. İnsan bir matematikçi gibi model de ara sonuçları denemeli, kütüphanede lemma aramalı, hatadan öğrenip düzeltmelidir. Yazarlar bunu tool'lu bir agent döngüsüne çevirip RL ile öğretmek istedi.

**Ne yaptılar:**
1. **Başlangıç.** Seed-Prover 1.0'dan başlandı. Tool çağırma kalıplarını öğretmek için şirket içi sentetik verilerle cold-start SFT yapıldı.
2. **Tool'lar.** Lean doğrulayıcısı (ispatı kontrol eder), Mathlib araması (Lean'in matematik kütüphanesinde lemma bulma) ve Python.
3. **RL algoritması.** VAPO tabanlı (PPO tarzı kırpmalı; VAPO bu dosyanın sonlarında ayrı bir girişte anlatılıyor). ReTool tarzı tool-integrated RL: model düşünürken tool çağırıyor ve RL bu davranışı da eğitiyor.
4. **RL verisi.** Açık veri setleri (BigMath, NuminaMath, Lean Workbook vb.) ve formal dile çevrilmiş ders kitapları.
5. **Zorluk filtresi.** Pass@4×8 ile, yani 4×8 denemelik hafif bir inference ile her problem test edildi ([pass@k](00_terimler.md#pass-rate-ve-passk): k denemeden en az birinin başarılı olma oranı). 3'ten fazla kez ispatlanan (fazla kolay) örnekler ve SFT modelinin hiç ispatlayamadıkları (şimdilik imkânsız) çıkarıldı.
6. **Üç görev biçimi.** Doğrudan ispat; doğal dilde bir taslakla ispat; önceki başarısız denemelerin özetiyle ispat. Üçüncüsü, modelin kendi hatalarından öğrenmesini görev haline getiriyor.
7. **Reward ve bütçe.** Lean ispatı doğrularsa +1, doğrulamazsa −1. Trajectory başına bütçe 64K token ve 28 tool call. İspatlanan lemma'lar bağlamda tutulup sonraki adımlarda tekrar kullanılıyor.

**Sonuç:** Yazarların raporuna göre:
- 1,200 RL adımında eğitim doğruluğu ~%50'den ~%90'a çıktı. Aynı sürede ortalama tool call sayısı ~15'ten ~10'a, uzunluk ~28K'dan ~17K token'a düştü. Yani model hem daha çok çözdü hem daha az adım harcadı.
- PutnamBench (Putnam üniversite matematik yarışması problemlerinin Lean'e çevrilmiş hali) 660 problemin 580'i (%87.9).
- Fate-H (formal soyut cebir ispat testi, zor seviye) %80.
- Putnam 2025'te 12 sorunun 11'i.

**Bizim için:** "Önceki başarısız denemenin özetiyle tekrar çöz" görev biçimi, bizim handoff ve final check notlarını eğitim görevine çevirmenin örneği. RL ilerledikçe tool call sayısının kendiliğinden azalması, budget'ı 10'da tutmanın öğrenilebilir olduğunu gösteriyor.

## DRIVE: Data Curation Best Practices for Reinforcement Learning with Verifiable Reward in Competitive Code Generation (Tencent Hunyuan, Kasım 2025) — [2511.06307](https://arxiv.org/abs/2511.06307)
**Tek cümlede:** Tencent Hunyuan, competitive programming RLVR'ında hangi verinin ne sırayla verilmesi gerektiğini sistematik inceledi ve zor sorulara odaklanan iki aşamalı bir RL curriculum'u önerdi.

**Problem:** RL'de algoritmalar çok konuşulur ama veri seçimi daha az incelenir. Hangi SFT verisi RL'e iyi bir başlangıç verir? RL'de kolay sorular mı, zor sorular mı, hangi sırayla? Kolay sorularda bütün denemeler doğru çıkar ve sinyal sulanır; çok zor sorularda hepsi yanlış çıkar ve yine sinyal olmaz.

**Ne yaptılar:**
1. **Temel model** Qwen2.5-32B-Instruct.
2. **SFT verisi.** DeepSeek-R1-0528'den distill edilmiş 1.27M prompt. Küçük bir sınıflandırıcı problemleri kolay, orta ve zor diye etiketliyor. Zor problemler veride iki kez tekrarlanıyor ("Twice Hard"). SFT 3 epoch, lr 1e-5, batch 512, 32K context.
3. **RL aşama 1: entropi genişletme.** ~9K tekdüze, orta zorlukta prompt; prompt başına 8 rollout, 24K uzunluk, 32 adım. Amaç modelin entropisini artırmak, yani daha çeşitli denemeler üretmesini sağlamak; ayrıca tekrarı ve uzunluk sınırında kesilmeyi azaltmak.
4. **RL aşama 2: hard-focus curriculum.** Zorluk, 8 rollout'luk başlangıç doğruluğuyla ölçülüyor. 3 faz var ve her fazda yalnızca en zor problemler kalıyor: 72 → 50 → 25 problem. Prompt başına 64–80 rollout, 32K uzunluk. Pass rate'i hâlâ düşük olan problemler bir sonraki faza taşınıyor. Az sayıda zor soruda çok sayıda deneme, nadir doğru denemeyi yakalama şansını artırıyor.

**Sonuç:** Yazarların raporuna göre:
- SFT → son RL: LiveCodeBench v6 0.549 → 0.703; Codeforces (yarışma sitesinin problemleri) 0.115 → 0.182.
- Yalnızca 9K'lık orta zorluk kümesiyle RL, Codeforces'ta 0.102'de kaldı; bu SFT'nin 0.115'inin bile altında. Zor odaklı ikinci aşama olmadan RL bu testte işe yaramadı.
- Aşama 1 olmadan yalnızca aşama 2: LeetCode'da 0.550; tam yöntem 0.653. Entropi genişletme adımı ~10 puan kazandırıyor.
- 109 zor örnek eklemek bütün testleri yükseltti. Yazarlara göre "zor örnekler işe yarar reward sinyali verir, kolay örnekler sinyali sulandırır."
- SFT'de Twice Hard en iyi seçenekti.

**Bizim için:** Küçük bir RL bütçesinde önce orta zorlukta geniş bir kümeyle kısa bir RL, sonra az sayıda zor soruda çok rollout'lu ikinci bir aşama BIRD'e uyarlanabilir. SFT'de zor soruları iki kez göstermek bedava bir kazanç.

## Every Activation Boosted: Scaling General Reasoner to 1 Trillion Open Language Foundation — Ling 2.0 (Ant Group / Inclusion AI, Ekim 2025) — [2510.22115](https://arxiv.org/abs/2510.22115)
**Tek cümlede:** Ant Group, 16B'den 1T'ye uzanan Ling 2.0 instruct serisinde üç post-training yöntemi (DFT, Evo-CoT, LPO) ve insan tercihi için Group Arena Reward önerdi.

**Problem:** Bir model hem anında cevap vermeli hem gerektiğinde derin düşünmeli; ikisini aynı veride karıştırmak modeli kararsız bırakabilir. Ayrıca token düzeyindeki kırpma uzun reasoning'de gürültülü olabiliyor. Açık uçlu sorularda (ör. yazı) doğru cevap olmadığı için reward vermek de zor.

**Ne yaptılar:**
1. **DFT (Decoupled Fine-Tuning).** SFT verisi iki ayrı sistem prompt'uyla eğitiliyor: biri anında cevap, biri derin reasoning için. Reasoning, genel ve sektörel alanlar (finans, sağlık, tedarik zinciri) dengeleniyor.
2. **ApexEval ile checkpoint seçimi.** SFT checkpoint'lerinden, RL'e en çok yer bırakanı seçmek için kullanılıyor. Yani en yüksek skorlu değil, RL ile en çok gelişebilecek olan checkpoint aranıyor.
3. **Evo-CoT.** RL anında cevap modundan başlıyor ve reasoning gerektikçe uzuyor. Reward parçaları:
   - doğruluk +1;
   - zorluğa bağlı bir uzunluk katsayısı: kolay soruda kısalık, zor soruda uzun reasoning ödüllendiriliyor;
   - reasoning işaretine −0.5;
   - görev reward'ları (kod testleri vb.).
4. **LPO.** Importance sampling ve kırpma token yerine cümle düzeyinde yapılıyor; kırpma aralığı ε = 0.03. Bir cümle tek bir birim gibi değerlendiriliyor; böylece tek tek token'ların gürültüsü azalıyor.
5. **Group Arena Reward (GAR).** Aynı modelin bir prompt'a verdiği cevaplar round-robin bir turnuvada ikişer ikişer karşılaştırılıyor; her maçı generative reward model yönetiyor. Bir cevabın toplam galibiyet sayısı onun reward'ı. Örnek: 4 cevap varsa her biri diğer 3'üyle eşleşir; 3 maçı da kazanan en yüksek reward'ı alır. Bu bir [preference optimization](00_terimler.md#dpo-ve-preference-optimization) biçimi: mutlak puan yerine karşılaştırmalı tercihle öğrenme.

**Sonuç:** Yazarların raporuna göre:
- Evo-CoT benzer ya da daha iyi performansa %25 daha az eğitim token'ıyla ulaştı.
- LPO, GRPO ve GSPO'ya göre daha düzgün reward eğrileri verdi; karmaşık reasoning'de yaklaşık %10 kazanç bildirildi.
- GAR, açık uçlu değerlendirmelerde %2–10 daha yüksek tutarlılık verdi.

**Bizim için:** RL'e başlamadan önce SFT checkpoint'ini "RL'e ne kadar alan bırakıyor" ölçüsüyle seçmek (ör. pass@k yüksek ama pass@1 düşük olan checkpoint) bizim küçük bütçemizde önemli bir karar.

## Every Step Evolves: Scaling Reinforcement Learning for Trillion-Scale Thinking Model — Ring-1T (Ant Group / Inclusion AI, Ekim 2025) — [2510.18855](https://arxiv.org/abs/2510.18855)
**Tek cümlede:** Ant Group, 1T / ~50B aktif bir thinking modelini RL ile eğitti ve bu ölçekte RL'i kararlı ve hızlı tutmak için IcePop ile C3PO++'ı önerdi.

**Problem:** RL'de rollout'u bir inference motoru (hızlı üretim için), güncellemeyi bir eğitim motoru yapar. İkisi aynı token'a sayısal olarak biraz farklı olasılık verir. MoE'de ve uzun rollout'larda bu fark birikir ve eğitimi bozabilir. Ayrıca çok uzun bir rollout bütün batch'i bekletir.

**Ne yaptılar:**
1. **Aşamalar.** Ling-1T-base'den: Long-CoT SFT → reasoning RL (RLVR) → genel RL.
2. **SFT verisi.** Açık kaynak, uzman yazımı ve LLM sentezi. Tam eşleşmeyle tekilleştirme, zararlı içerik filtresi ve hash ile tam string eşleşmesine dayanan benchmark [decontamination](00_terimler.md#decontamination) (test sorularının eğitim verisinden temizlenmesi). Karışım: matematik %46, STEM %26, kod %20, diğer %8. SFT 3 epoch, lr 2e-4, 64K packing (kısa örnekler tek bir uzun diziye paketleniyor).
3. **RLVR verisi.**
   - Matematik.
   - Kod: test case'leri doğrulanmış.
   - Fen: çoktan seçmeli sorular açık uçluya çevrildi (tahminle kazanılmasın diye), pass rate filtresi uygulandı.
   - Mantık bulmacaları: çözülebilir oldukları kontrol edildi.
   - Genel veri.
   Her örnek hem LLM hem kural tabanlı puanlanabiliyor; dynamic sampling için metadata tutuluyor.
4. **Reasoning RL ayarları.** lr 2e-6, KL 0, temperature 1.0, adım başına 480 prompt × 8 rollout, max 65,536 token.
5. **Genel RL ayarları.** GRPO, lr 3e-6, 80 prompt × 8 rollout, 32K.
6. **IcePop.** Her token için eğitim motorunun ve inference motorunun verdiği olasılıkların oranı hesaplanıyor. Oran [0.5, 5] aralığının dışındaysa token gradient'ten çıkarılıyor. Örnek: inference motoru bir token'a 0.10, eğitim motoru 0.60 verdiyse oran 6; bu token atılıyor. Bu, token'ların ~%0.1–0.2'sini etkiliyor.
7. **C3PO++.** Her adım için bir token bütçesi var. Bütçe dolunca o ana kadar biten rollout'lar eğitime giriyor. Bitmeyenler yarıda bırakılıp bir sonraki modelle devam ettiriliyor. Böylece en uzun rollout bütün batch'i bekletmiyor.

**Sonuç:** Yazarların raporuna göre:
- AIME 2025 93.40; HMMT 2025 (Harvard-MIT matematik turnuvası) 86.72; Codeforces rating (yarışma sitesinin insanlarla aynı ölçekteki puanı) 2088; IMO 2025'te gümüş madalya düzeyi.
- Ring-mini-2.0'da IcePop, AIME25'te TIS'i (truncated importance sampling: oranı atmak yerine üstten sınırlayan yöntem) geçti ve temel skoru (%63) %14'ten fazla artırdı.
- Daha dar aralık [0.5, 2] eğitimi bozdu; çok fazla token atmak da zararlı.
- C3PO++ rollout'ta ~2.5 kat, uçtan uca ~1.5 kat hız sağladı.

**Bizim için:** MLX'te eğitip `mlx_lm.server` ile rollout ürettiğimizde iki motorun olasılıkları farklı olabilir; IcePop tipi bir token maskesi (oran [0.5, 5] dışındaysa at) ucuz bir güvenlik önlemi.

## Introducing LongCat-Flash-Thinking: A Technical Report (Meituan, Eylül 2025) — [2509.18883](https://arxiv.org/abs/2509.18883)
**Tek cümlede:** Meituan, 560B / ~27B aktif reasoning modelini long CoT cold start ve büyük ölçekli RL ile eğitti; alan uzmanlarını ayrı ayrı RL'leyip ağırlıklarını birleştirerek tek modelde topladı.

**Problem:** Farklı alanları (STEM, kod, agent) tek RL koşusunda eğitmek hem yavaş hem çatışmalı. Ayrıca agentic veride her soru tool gerektirmez; tool'un işe yaramadığı sorular modele gereksiz tool kullanmayı öğretir. Reward'ın doğruluğu da kritik: kural eşleşmesi doğru cevapları kaçırabilir.

**Ne yaptılar:**
1. **[Mid-training](00_terimler.md#mid-training).** Pre-training ile post-training arasında, belirli bir veri türüyle yapılan ek eğitim. Burada mid-training'e reasoning ağırlıklı STEM ve kod verisi karıştırıldı. Küçük bir modelde bu oranı artırmak AIME-24'ü %27.7 artırdı.
2. **SFT verisi.** [LLM-as-judge](00_terimler.md#llm-as-judge-ve-rubric) (bir LLM'in cevabı değerlendirmesi), model oylamasıyla cevap doğrulama (birden çok model aynı cevabı buluyor mu) ve zorluk filtresiyle süzüldü; rejection sampling ile kuruldu.
3. **Agentic veri seçimi.** Yalnızca tool'un açıkça yardım ettiği sorular tutuldu. Ölçüt: aynı sorunun tool'lu ve tool'suz pass rate'i arasındaki fark. Fark büyükse soru tutuluyor.
4. **RL: değiştirilmiş GRPO.**
   - KL yok.
   - Sabit bir normalizer'la token-level loss: loss, cevap uzunluğuna göre değil sabit bir sayıya bölünüyor; uzun cevaplar yüzünden ağırlık kaymıyor.
   - Pozitif ve negatif advantage için farklı (asimetrik) kırpma sınırları.
   - Motor farkı için truncated importance sampling (oranı üstten sınırlama).
   - Hepsi doğru ya da hepsi yanlış prompt'lar eğitim sırasında atılıyor.
   - Staleness sınırlı ve bir replay buffer var.
   - Puanlama hatası olan ya da uzunluk sınırında kesilen örnekler maskeleniyor.
   - STEM için reasoning yapan bir generative reward model kullanıldı.
5. **Uzmanlar ve [model merging](00_terimler.md#model-merging).** Alan başına ayrı uzmanlar eğitildi (STEM 64K, agentic 48K context). Her uzmanın task vector'ü (uzman ağırlıkları eksi başlangıç ağırlıkları) normalize edildi. Sonra DARE tarzı seyreltme (task vector'deki değerlerin çoğu rastgele sıfırlanıp kalanlar büyütülüyor) ve işaret budamasıyla (uzmanların ters yöne çektiği ağırlıklarda çatışmayı ayıklama) birleştirildi. Sonda genel bir PPO aşaması var.

**Sonuç:** Yazarların raporuna göre:
- Reasoning yapan GenRM, insan etiketli bir kümede %98.8 doğruluk verdi. Reasoning'siz GenRM %94.0, kural eşleşmesi %80.9. Yani düz kural, her beş cevaptan birini yanlış puanlıyor.
- Tool kullanınca AIME-25'te token sayısı 19,653'ten 6,965'e indi (~%64.5 azalma); doğruluk korundu.
- AIME-25 90.6; MiniF2F (olimpiyat problemlerinin formal ispat diline çevrilmiş hali) 67.6.
- RL compute'u pre-training compute'unun ~%20'si.

**Bizim için:** "Tool'lu ve tool'suz pass rate farkı" agentic SFT/RL verisi seçmek için doğrudan ölçüt: BIRD'de base'in (tool'suz tek SQL) çözemediği ama agentic sistemin çözdüğü sorular en değerli eğitim verisi.

## GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models (Zhipu AI & Tsinghua, Ağustos 2025) — [2508.06471](https://arxiv.org/abs/2508.06471)
**Tek cümlede:** Zhipu, reasoning, agent ve genel sohbet için ayrı uzmanlar eğitip bunları self-distillation ile tek bir hibrit reasoning modelinde birleştirdi ve agentic RL için birkaç basit kural koydu.

**Problem:** Tek bir model hem matematik çözmeli, hem tool kullanan bir agent olmalı, hem de iyi sohbet etmeli. Bu becerileri ayrı ayrı RL ile geliştirip tek modelde toplamanın pratik bir yolu gerekiyor. Ayrıca reasoning RL'de uzunluk, zorluk ve temperature gibi ayarların ne zaman ve nasıl değişeceği belirsiz.

**Ne yaptılar:**
1. **İki aşama.** (1) Reasoning, agent ve genel sohbet için ayrı uzmanlar; her biri cold-start SFT + RL. (2) Self-distillation: uzmanların çıktılarıyla tek bir hibrit reasoning modeli eğitiliyor. RL altyapısı slime (Megatron eğitim + SGLang inference).
2. **Genel SFT.** Milyonlarca örnek, 128K'ya kadar context.
3. **Rejection sampling'de dört filtre.** Bozuk ya da kesik örnekler atılıyor; objektif cevaplarda doğruluk kontrol ediliyor; öznel cevaplarda reward model puanı kullanılıyor; agent örneklerinde tool-call protokolü ve görevin son durumu kontrol ediliyor.
4. **Prompt seçimi.** Cevap uzunluğuna göre en alttaki %50 prompt'u (kısa cevaplı, muhtemelen kolay olanları) atmak, verinin yarısıyla matematik ve fende %2–4 kazandırdı. Zor prompt başına 4 cevap üretmek %1–2 ekledi.
5. **Agentic veri pipeline'ı.** Tool ve framework toplama → görev sentezi → trajectory üretimi (çok turlu görevlerde kullanıcıyı bir LLM simüle ediyor) → birden çok judge agent'ın başarılı dediği trajectory'leri tutma.
6. **Reasoning RL.**
   - KL'siz GRPO.
   - İki aşamalı zorluk curriculum'u: ikinci aşamada yalnızca cevabı doğrulanmış ve modelin henüz hiç çözemediği problemler.
   - Doğrudan 64K uzunlukta tek aşama. Kısa uzunluklarla başlayıp aşamalı büyütmek, modelin cevap uzunluğunu geri dönülmez şekilde düşürdü.
   - Reward platoya girince temperature artırılıyor; seçilen değer, doğrulama kümesinde en fazla %1 düşüş veren en yüksek temperature.
   - Kodda token-ağırlıklı ortalama loss (her token aynı ağırlıkta).
7. **Agentic RL kuralları.** Yalnızca modelin ürettiği token'lar optimize ediliyor; tool çıktıları loss'tan maskeli. Bozuk bir tool call'a 0 reward veriliyor ve trajectory orada durduruluyor.
8. **Yinelemeli distillation.** Bu bir [expert iteration](00_terimler.md#expert-iteration) döngüsü: RL'den çıkan iyi trajectory'ler cold-start verisinin yerini alıyor, sonra daha zor görevlerle tekrar RL yapılıyor.
9. **Fonksiyon çağırma.** Adım bazında kural tabanlı RL: format doğru ve çağrı beklenenle tam eşleşiyorsa reward 1.

**Sonuç:** Yazarların raporuna göre:
- TAU-bench (simüle bir müşteriyle tool kullanarak iş bitiren agent testi) 70.1; BFCL V3 77.8; SWE-bench Verified 64.2; AIME 24 91.0.
- BrowseComp doğruluğu, etkileşim turu sayısı arttıkça düzgün biçimde yükseldi.
- Fende yalnızca uzmanların doğruladığı çoktan seçmeli sorularla eğitmek, karışık kaliteli veriyle eğitmekten iyi sonuç verdi.

**Bizim için:** Bozuk tool call'da trajectory'yi 0 reward'la kesmek, yalnızca model token'larında loss hesaplamak (tool çıktısı maskeli) ve RL çıktılarını yeni SFT verisi yapıp tekrar RL'lemek, bizim döngüye doğrudan uyan üç kural.

## Seed-Prover: Deep and Broad Reasoning for Automated Theorem Proving (ByteDance Seed, Temmuz 2025) — [2507.23726](https://arxiv.org/abs/2507.23726)
**Tek cümlede:** ByteDance Seed, Lean'de lemma lemma tam ispat yazan ve ispatını Lean'in geri bildirimiyle düzelten bir modeli RL ile eğitti.

**Problem:** LLM'ler matematik sorularını RL ile iyi çözmeye başladı, ama ispat yazmakta zorlanıyorlar. Doğal dilde yazılmış bir ispatın doğru olup olmadığını otomatik ve kesin olarak kontrol etmek zor; bu yüzden RL için net bir sinyal yok. Lean gibi formal bir dilde ise ispatı bilgisayar kontrol eder ve sinyal nettir.

**Ne yaptılar:**
1. **Lemma tarzı tam ispat.** Model ispatı önce ara lemma'lara bölüyor, sonra her lemma'yı ve ana teoremi ispatlıyor.
2. **Geri bildirimle düzeltme döngüsü.** Model ispatını yinelemeli olarak düzeltiyor. Elindeki üç kaynak: Lean'in hata mesajları, daha önce ispatlanmış lemma'lar ve kendi yazdığı özetler. Eğitim bu döngüyü öğretmeye dayanıyor.
3. **Reward.** Asıl sinyal Lean'in formal doğrulaması: ispat geçer ya da geçmez. Bu ikili ve hilesi zor bir reward.
4. **Test anında üç strateji.** IMO düzeyindeki problemler için hem derin (bir ispatı uzun süre düzeltme) hem geniş (birçok farklı yol deneme) arama yapan üç inference stratejisi tasarlandı.
5. **Seed-Geometry.** Lean'in geometri desteği zayıf olduğu için ayrı bir geometri reasoning motoru kuruldu.

**Sonuç:** Yazarların raporuna göre:
- Formal dile çevrilmiş geçmiş IMO (Uluslararası Matematik Olimpiyatı) problemlerinin %78.1'i ispatlandı.
- MiniF2F doygun: testteki problemlerin neredeyse hepsi çözülüyor.
- PutnamBench'te %50'den fazla; yazarlara göre önceki en iyi sonucu büyük farkla geçiyor. (Aynı ekibin 1.5 sürümü yukarıda %87.9'a çıkıyor.)
- Seed-Geometry ile birlikte IMO 2025'in 6 probleminden 5'i tam ispatlandı.

**Kaynak notu:** Bu giriş raporun özetine dayanıyor. Özette ayrıntılı RL hiperparametresi, reward'ın tam tanımı ve üç test stratejisinin adları yok.

**Bizim için:** Kesin bir doğrulayıcı (bizde gerçek çalıştırma ve result key karşılaştırması) varken "hata notuyla düzelt" döngüsünü RL'in ana konusu yapmak, `execute_sql` hata notlarından öğrenmenin karşılığı.

## GLM-4.1V-Thinking and GLM-4.5V: Towards Versatile Multimodal Reasoning with Scalable Reinforcement Learning (Zhipu AI & Tsinghua, Temmuz 2025; v6 Ocak 2026) — [2507.01006](https://arxiv.org/abs/2507.01006)
**Tek cümlede:** Zhipu, görsel-dil modellerini long CoT cold-start SFT ve ardından zorluğa göre örnekleme yapan bir RL (RLCS) ile eğitti.

**Problem:** Görsel-dil modelleri (görüntü ve metni birlikte işleyen modeller) çok farklı görevlerle karşılaşır: grafik okuma, geometri, video, belge. RL'de her görev aynı zorlukta değildir. Çok kolay ve çok zor örnekler sinyal vermez. Ayrıca her alanın cevabını kontrol eden ayrı bir verifier gerekir ve biri bile zayıfsa sorun çıkabilir.

**Ne yaptılar:**
1. **Cold-start SFT.** 32K sıra uzunluğu, global batch 32. Cevaplar `<think>` ve `<answer>` etiketleriyle; doğrulanabilir görevlerde son cevap özel kutu işaretleri arasında, böylece otomatik okunabiliyor.
2. **Cold-start verisinin temizliği.** Dil karışımı (ör. İngilizce cevabın ortasında Çince) ve gereksiz tekrar içeren cevaplar atıldı. Kısa CoT SFT bilerek yapılmadı. Cold-start verisi, RL checkpoint'lerinden alınan örneklerle tazelendi.
3. **RLCS (Reinforcement Learning with Curriculum Sampling).**
   - Offline zorluk: birden çok modelin pass@k'sı ve insan etiketleriyle her örneğe bir zorluk derecesi veriliyor.
   - Online zorluk: eğitim sırasında her rollout'un pass@k'sına göre güncelleniyor.
   - Her iterasyonda çok kolay ve çok zor örneklerin ağırlığı azaltılıyor, orta zorluk öne çıkarılıyor.
4. **Ratio-EMA dynamic sampling.** Batch'te doğru ve yanlış denemelerin en dengeli olduğu alt küme tutuluyor.
5. **Kesilen reasoning.** Reasoning uzunluk sınırında kesilirse `</think>` zorla eklenip modelden cevap alınıyor.
6. **Kaldırılan parçalar.** KL yok. Entropi loss'u (entropiyi yüksek tutmak için eklenen terim) yok, çünkü bozuk çıktıya yol açtı. top-p 1 (örnekleme kısıtlanmıyor). Loss örnek başına hesaplanıyor.
7. **Verifier'lar.** Her alanın kendi verifier'ı var.

**Sonuç:** Yazarların raporuna göre:
- RL, GLM-4.5V'de SFT modeline göre %10.6'ya kadar kazanç verdi.
- Tek bir alandaki zayıf bir verifier, bütün alanlarda eğitimi çökertebildi.
- Daha güçlü bir cold-start checkpoint'i, RL sonunda daha iyi sonucu garanti etmedi: 1,000 ve 2,000 adımlık cold start'lar RL sonunda neredeyse aynı skora geldi.
- GLM-4.1V-9B-Thinking, 29 testte kendisinden 8 kat büyük Qwen2.5-VL-72B'yi geçti.

**Bizim için:** Online pass rate'e göre örnekleme ağırlığı (orta zorluğu öne çıkar) ve "cold start'ı uzun tutmak gerekmez" bulgusu, küçük compute'ta SFT'yi kısa tutup bütçeyi RL'e ayırmayı destekliyor. Verifier (result key) hatasız olmalı.

## Truncated Proximal Policy Optimization (ByteDance Seed, Haziran 2025) — [2506.15050](https://arxiv.org/abs/2506.15050)
**Tek cümlede:** ByteDance Seed, uzun CoT'li PPO'da rollout'ların bitmesini beklemeden kısmen üretilmiş cevaplar üzerinde de güncelleme yapan T-PPO'yu önerdi.

**Problem:** PPO'da her güncellemeden önce bütün rollout'ların bitmesi beklenir. Uzun CoT'de cevapların uzunlukları çok farklıdır: çoğu erken biter, birkaçı çok uzun sürer. GPU'lar en uzun cevabı beklerken boş durur. Bu, eğitimi yavaşlatır.

**Ne yaptılar:**
1. **Pencereli üretim.** Her adımda her cevap en fazla bir pencere uzunluğu (burada 8K token) kadar ilerletiliyor. Bitmeyen cevap sonraki adımda kaldığı yerden devam ediyor.
2. **Extended GAE.** GAE, advantage'ı her adımdaki reward ve value tahminlerinden hesaplayan standart yöntemdir. Cevap bitmediğinde son reward henüz bilinmez; Extended GAE, advantage'ı cevabın yalnızca üretilmiş kısmı için value modelinin tahminleriyle hesaplıyor.
3. **İki modelin ayrı eğitimi.** Policy, yalnızca o adımda üretilen token'larla güncelleniyor. Value modeli ise yalnızca biten dizilerin bütün token'larıyla, gerçek sonuç kullanılarak (Monte Carlo) eğitiliyor. İkisi bağımsız ama eşzamanlı.
4. **Ayarlar.** Qwen2.5-32B Base. Policy lr 1e-6, critic lr 2e-6. 512 prompt × 16 örnek. λ=0.95. Kırpma sınırları ε_low=0.2, ε_high=0.28. KL yok. Max uzunluk 24K, pencere 8K.

**Sonuç:** Yazarların raporuna göre:
- AIME 2024 avg@32 (soru başına 32 denemenin ortalama doğruluğu) 62. Karşılaştırma: VAPO 60, DAPO 50.
- Eğitim verimliliği 2.5 kata kadar arttı. PPO-EWMA ~11,200 adımda yakınsarken T-PPO ~6,720 adımda yakınsadı; yaklaşık %40 daha az adım.

**Bizim için:** Bizim trajectory'lerimiz kısa olduğu için T-PPO'nun asıl kazancı bize az yansır. Genel ders şu: rollout zamanı RL'in darboğazıdır ve Mac'te en pahalı kısım da budur.

## MiMo-VL Technical Report (Xiaomi, Haziran 2025) — [2506.03569](https://arxiv.org/abs/2506.03569)
**Tek cümlede:** Xiaomi, 7B'lik görsel-dil modeli MiMo-VL'i SFT'den sonra, doğrulanabilir görevlerle insan tercihini tek bir on-policy RL koşusunda birleştiren MORL ile eğitti.

**Problem:** Görsel modelden hem doğrulanabilir işler (görsel reasoning, grounding yani görüntüde bir nesnenin yerini bulma, sayma) hem de insanlara hoş gelen cevaplar bekleniyor. Bunlar genelde ayrı aşamalarda eğitilir: RLVR ve RLHF (insan tercihlerinden öğrenilmiş bir reward model'le RL). Yazarlar ikisini tek koşuda yapmak istedi.

**Ne yaptılar:**
1. **Mixed On-policy RL (MORL).** RLVR (görsel reasoning, grounding, sayma) ve RLHF aynı koşuda.
2. **Görsel reasoning RL kümesi.** 80K problem. MiMo-VL-7B'nin rollout pass rate'i %90'ı geçen (fazla kolay) sorular atıldı. Görüntüye bakmadan çözülebilen sorular da atıldı; bunlar görsel beceri öğretmez. Daha zor problemler için MiMo-7B'nin metin matematik verisi eklendi.
3. **Algoritma.** GRPO'nun tamamen on-policy bir çeşidi. Her rollout'tan sonra tek bir güncelleme yapılıyor; bu yüzden clipped surrogate (eski ve yeni modelin oranını kırpan PPO terimi) yok. KL yok. Dynamic sampling, kolay veri filtresi ve yeniden örnekleme var.
4. **Reward-as-a-Service.** Bir router, görev tipine göre doğru reward fonksiyonunu seçiyor. Bütün reward'lar [0, 1] aralığına normalize ediliyor. Format reward'ı yok.

**Sonuç:** Yazarların raporuna göre:
- On-policy RL, veri arttıkça iyileşmeye devam etti; vanilla GRPO yaklaşık 20,000 örnekte platoya girdi.
- MORL, SFT modeline 22'den fazla Elo ekledi. Elo, modellerin ikili karşılaştırmalarından hesaplanan bir puandır; fark büyüdükçe kazanma olasılığı artar.
- Alanlar birbirini etkiledi: reasoning görevleri CoT'u uzatırken grounding ve sayma görevleri kısalttı. Yazarlar bu çatışmayı çözemediklerini söylüyor.

**Bizim için:** "Soru, tool kullanmadan (ya da görüntü olmadan) çözülebiliyorsa at" filtresi BIRD'de "şemayı görmeden çözülebilen soruyu at" olarak işe yarar. Tamamen on-policy, tek güncellemeli GRPO küçük batch'te de kararlı bir seçenek.

## Seed-Coder: Let the Code Model Curate Data for Itself (ByteDance Seed, Haziran 2025) — [2506.03524](https://arxiv.org/abs/2506.03524)
**Tek cümlede:** ByteDance Seed, 8B'lik kod modellerinin (base, instruct, reasoning) verisini seçme ve düzeltme işini büyük ölçüde LLM'lerin kendisine bıraktı.

**Problem:** Kod verisini elle kurallarla süzmek pahalıdır ve iyi örnekleri kaçırır. Yazarlar veriyi bir modelin puanlamasını, test etmesini ve düzeltmesini istedi. Ayrıca zor örnekler değerlidir ama ilk denemede çoğu hatalıdır; bunları atmak yerine kurtarmak istediler.

**Ne yaptılar:**
1. **Instruct verisi.** ~3M instruction–response çifti.
   - Tree-sitter (kodu ayrıştıran bir araç) ile sözdizimi hatalı cevaplar atıldı.
   - Bir model her örneğe doğruluk ve zorluk puanı verdi; zorluğu 3/10'un altındakiler atıldı.
   - Model kendi çözümü için test yazıyor, sandbox'ta çalıştırıyor ve başarısız olanları yinelemeli düzeltiyor. Böylece zor ama ilk denemede yanlış örnekler kurtarılıyor.
2. **SFT.** 3 epoch, lr 2e-5, zorluğa duyarlı örnekleme.
3. **[DPO](00_terimler.md#dpo-ve-preference-optimization).** Sandbox test sonuçlarıyla etiketlenmiş ~20K on-policy tercih çifti. DPO, "bu cevap şundan iyi" çiftleriyle, ayrı bir reward model eğitmeden modeli iyi cevaba yaklaştırır. Burada testi geçen cevap "iyi", geçmeyen "kötü".
4. **Reasoning modeli.** Önce base modelden binlerce long CoT örneğiyle ısınma. Sonra verl kütüphanesinde DAPO tarzı GRPO: batch 128, lr 1e-6, temperature 0.6, KL yok, clip 0.28, token-level loss, aşırı uzun cevaplar filtreli.
5. **Curriculum.** Doğruluğu %87.5'in üstündeki problemler atıldı. Uzunluk aşamalı büyütüldü: önce 16K'da 16 örnekle 90 adım, sonra 32K'da 32 örnekle 160 adım.

**Sonuç:** Yazarların raporuna göre instruct modeli LiveCodeBench'te (Ekim 2024 – Şubat 2025 arası problemler) %24.7 ile ~8B modeller arasında en iyisi. NaturalCodeBench'te (gerçek kullanıcıların kod istekleri) 49.6; daha büyük Qwen2.5-Coder-14B-Instruct 46.4'te kaldı.

**Bizim için:** "Model kendi SQL'ini çalıştırıp hatayı düzeltir, düzeltilmiş trajectory SFT verisi olur" döngüsü experience log'la hazır elimizde. Toplam 250 adımlık RL, küçük bir modelde az adımla iş görüldüğünü gösteriyor.

## Hunyuan-TurboS: Advancing Large Language Models through Mamba-Transformer Synergy and Adaptive Chain-of-Thought (Tencent, Mayıs 2025) — [2505.15431](https://arxiv.org/abs/2505.15431)
**Tek cümlede:** Tencent, Transformer–Mamba2–MoE hibriti bir modeli soruya göre kısa ya da uzun düşünmeyi seçecek şekilde eğitti ve iki aşamalı GRPO kullandı.

**Problem:** Uzun düşünen modeller kolay sorularda da uzun düşünür ve token israf eder. İdeal model soru kolaysa kısa, zorsa uzun düşünmeli. Ayrıca önce reasoning, sonra genel talimatlar üzerinde RL yapınca ilk aşamada öğrenilen beceri unutulabilir.

**Ne yaptılar:**
1. **Model.** 560B toplam / 56B aktif. Transformer katmanlarının yanında Mamba2 katmanları var; Mamba2, uzun dizileri attention'dan daha ucuz işleyen bir katman türü.
2. **SFT.** 13 konuda ~3M örnek.
3. **Adaptive long-short CoT verisi.** Kısa CoT modeli doğru cevap verdiyse cevap olduğu gibi tutuluyor. Yanlış verdiyse soru ve yanlış cevap Hunyuan-T1'e (uzun düşünen model) veriliyor; T1 doğruya ulaşana kadar reasoning'i sürdürüyor. Sonuç kısa CoT biçimine çevrilip veriye ekleniyor.
4. **Multi-round deliberation learning.** Raporun özetine göre yinelemeli iyileştirme için çok turlu bir aşama; ayrıntısı özette yok.
5. **RL reward'ları.** Zorluğa uyarlanan reward: zor prompt'ta uzun, kolay prompt'ta kısa CoT ödüllendiriliyor. Sıkıştırma reward'ı: aynı doğruluktaki yollardan kısası ödüllendiriliyor.
6. **GRPO aşama I.** ~300K reasoning prompt'u (kod:matematik:mantık ve fen = 2:2:1), küçük KL.
7. **GRPO aşama II.** 12 alanda ~160K genel talimat ve aşama I'in reasoning verisinden %10. Unutmaya karşı daha büyük KL.
8. **Ortak ayarlar.** Token-level loss. Yalnızca pozitif advantage'lı örneklere best-of-N loss (en iyi denemeleri ayrıca güçlendirme). Hep çözülen ya da hiç çözülemeyen prompt'lar atılıyor.

**Sonuç:** Yazarların raporuna göre LMSYS Arena'da (insanların iki modelin cevabını karşılaştırıp oy verdiği sıralama) 1356 puanla ilk 7'de. 23 testte ortalama %77.9. Ortalama çıktı 1,207.8 token; DeepSeek-R1 2,283.5 token. Yani yaklaşık yarı token'la çalışıyor.

**Kaynak notu:** Bileşenler (adaptive CoT, iki reward, iki aşamalı GRPO) için sayısal ablation yok; her parçanın katkısı bilinmiyor. Deliberation learning'in nasıl çalıştığı özette anlatılmıyor.

**Bizim için:** İkinci RL aşamasında ilk aşamanın verisinden %10 tutmak unutmaya karşı basit bir önlem. Kolay soruda kısa çözümü ödüllendirmek, bizde kolay soruda az tool call'la `submit`'i ödüllendirmek demek.

## MiMo: Unlocking the Reasoning Potential of Language Model — From Pretraining to Posttraining (Xiaomi, Mayıs 2025) — [2505.07608](https://arxiv.org/abs/2505.07608)
**Tek cümlede:** Xiaomi, reasoning için 25T token'la pre-train edilmiş 7B bir modeli SFT ve 130K doğrulanabilir problemle RL'den geçirdi ve RL'in base'den mi yoksa SFT'den mi başlaması gerektiğini karşılaştırdı.

**Problem:** Küçük bir modelin büyük modeller kadar iyi reasoning yapıp yapamayacağı soruluyor. Bir de pratik soru var: RL'e doğrudan base modelden başlamak (RL-Zero) mı, önce SFT yapıp sonra RL mi daha iyi? Ayrıca reward'ın hack'lenmesi küçük modellerde de görülüyor.

**Ne yaptılar:**
1. **SFT.** ~500K örnek. Benchmark'larla 16-gram örtüşmesi olanlar (16 kelimelik bir dizisi test sorusunda geçenler) decontamination ile atıldı. Soru başına en fazla 8 cevap. lr 3e-5, batch 128, 32K packing.
2. **RL verisi: ~100K matematik.** İspat ve çoktan seçmeli sorular atıldı. N-gram tekilleştirme ve decontamination yapıldı. SFT modeli 16 rollout'ta %90'dan fazla çözüyorsa soru atıldı; bu, kolay problemlerin yarısını eledi.
3. **RL verisi: ~30K kod.** Test case'i olmayan ya da altın çözümü testleri geçemeyen problemler atıldı; 16 denemenin 16'sında çözülenler de atıldı.
4. **Reward.** Yalnızca kural tabanlı doğruluk; format ya da uzunluk reward'ı yok.
5. **Kod için test-difficulty-driven reward.** Testler pass rate'e göre zorluk seviyelerine ayrılıyor ve kısmi puan veriliyor. Bu, IOI'nin (Uluslararası Bilgisayar Olimpiyatı) alt görev puanlamasına benziyor: bütün testleri geçmeyen ama kolay testleri geçen çözüm de bir miktar puan alıyor.
6. **Algoritma.** KL'siz GRPO. Dynamic sampling (pass rate'i 0 ya da 1 olan prompt'lar atılıyor). Clip-higher (üst kırpma sınırını genişletme).
7. **Easy data re-sampling.** Tamamen çözülen problemler bir "kolay havuz"a alınıyor. Her rollout %10 olasılıkla bu havuzdan çekiliyor. Böylece kolay sorular tamamen unutulmuyor.
8. **Ayarlar.** Batch 512, lr 1e-6, max uzunluk 32K (sonra 48K'ya çıkarıldı).

**Sonuç:** Yazarların raporuna göre:
- RL-Zero → SFT'den başlayan RL: AIME 2024 56.4 → 68.2; AIME 2025 46.3 → 55.4; LiveCodeBench v5 49.1 → 57.8. SFT'den başlamak üç testte de 8–12 puan önde.
- Base'den RL daha hızlı büyüyor, ama SFT'den başlayan RL'in tavanı daha yüksek.
- Yalnızca formata hizalayan hafif bir SFT, ~500 adımdan sonra RL-Zero'nun da gerisine düştü.
- 2000–2500. adımlarda kod iyileşirken matematik dalgalandı. Sebep: model matematik reward'ını hack'liyordu; test tabanlı kod verifier'ını kandırmak ise zordu.
- Sonraki bir checkpoint (48K bütçe) AIME 2024'te 80.1'e ulaştı.

**Bizim için:** 7B'de bile güçlü bir SFT, RL tavanını yükseltiyor; yalnızca formatı öğreten SFT yetmiyor. Kolay soruları tamamen atmak yerine %10 oranında geri çekmek kararlılık için iyi bir ayar. SQL'de kısmi reward (ör. sütun ya da satır kümesi örtüşmesi) IOI tarzı kısmi puanın karşılığı olabilir, ama hack'lenmeye açık olabileceği unutulmamalı.

## VAPO: Efficient and Reliable Reinforcement Learning for Advanced Reasoning Tasks (ByteDance Seed, Nisan 2025) — [2504.05118](https://arxiv.org/abs/2504.05118)
**Tek cümlede:** ByteDance Seed, value modeli kullanan PPO'yu (actor-critic) uzun CoT'de kararlı hale getirip GRPO ve DAPO gibi value-free yöntemlerin önüne geçirdi.

**Problem:** PPO'da bir value modeli (critic) her token'dan sonra beklenen reward'ı tahmin eder; advantage bu tahminlerden hesaplanır. Teoride bu, grup ortalamasından daha ince bir sinyal verir. Ama uzun CoT'de üç sorun çıkıyor: value modeli başta yanlı tahmin yapıyor (value bias); cevap uzunlukları çok farklı olduğu için tek bir ayar herkese uymuyor; reward yalnızca sonda ve seyrek geliyor.

**Ne yaptılar:**
1. **Value-pretraining.** RL'den önce value modeli, sabit bir politikanın (ör. SFT modeli) rollout'larının gerçek sonuçlarıyla (Monte Carlo return) ısıtılıyor. Böylece RL başladığında value tahminleri anlamlı.
2. **Decoupled GAE.** GAE'deki λ, advantage hesaplanırken ne kadar uzağa bakıldığını ayarlar. Value modeli için λ=1.0 (bütün gelecek reward'lar), policy için ayrı bir λ kullanılıyor.
3. **Length-adaptive GAE.** Policy'nin λ'sı cevap uzunluğuna göre seçiliyor: λ = 1 − 1/(α × uzunluk), α = 0.05. Cevap uzadıkça λ 1'e yaklaşıyor. Örnek: 100 token'lık cevapta λ = 0.8, 1,000 token'lık cevapta λ = 0.98.
4. **Token-level loss** ve **clip-higher** (alt sınır 0.2, üst sınır 0.28).
5. **Doğru örneklere NLL loss.** Doğru cevaplara μ = 0.1 ağırlıklı ek bir dil modeli loss'u ekleniyor; bu, RL'in içine küçük bir SFT terimi koymak gibi.
6. **Group sampling.** 512 prompt × 16 deneme. Actor lr 1e-6, critic lr 2e-6.

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-32B'de AIME24 60.4 (~5,000 adımda). DAPO'yu ve DeepSeek-R1-Zero-Qwen-32B'yi 10 puandan fazla geçti. 3 koşuda da eğitim çökmedi.
- Ablation (AIME24, her satırda bir parça çıkarılıyor):
  - vanilla PPO: 5
  - value-pretraining olmadan: 11
  - decoupled GAE olmadan: 33
  - length-adaptive GAE olmadan: 45
  - pozitif örnek LM loss'u olmadan: 54
  - tam yöntem: 60
  En büyük etki value-pretraining'in: o olmadan skor 60'tan 11'e düşüyor.

**Bizim için:** Value modeli ayrıca bellek demek; 0.8B–4B'de critic'siz GRPO daha uygun. Ama "doğru örneklere küçük bir NLL loss eklemek" (RL + SFT karışımı) bize de ucuz ve faydalı bir ekleme.

## Seed1.5-Thinking: Advancing Superb Reasoning Models with Reinforcement Learning (ByteDance Seed, Nisan 2025) — [2504.13914](https://arxiv.org/abs/2504.13914)
**Tek cümlede:** ByteDance Seed, 200B / 20B aktif bir MoE reasoning modelini long CoT SFT'den sonra VAPO ve DAPO tabanlı RL ile, hem doğrulanabilir hem doğrulanamaz veriyle eğitti.

**Problem:** RL'de matematik ve kod gibi cevabı kontrol edilebilen veri kolay puanlanır. Yazı gibi doğrulanamaz görevlerde ise kesin bir doğru yoktur. Ayrıca cevabı kontrol eden verifier'ın kendisi hata yaparsa model yanlış şeyi öğrenir. Yazarlar ikisini aynı RL'de birleştirmek ve verifier'ı güçlendirmek istedi.

**Ne yaptılar:**
1. **CoT SFT.** ~400K örnek: 300K doğrulanabilir, 100K doğrulanamaz. Az sayıda insan yazımı cold-start örneğinden başlanıp Seed-Verifier ile rejection sampling yapıldı. 32K, 2 epoch, lr 2e-5'ten 2e-6'ya.
2. **RL verisi.** ~100K STEM problemi (%80'den fazlası matematik); unit test'li competitive programming; 22 görev tipinden ~10K mantık bulmacası (bulmacaların zorluğu modelin performansına göre ayarlanıyor).
3. **Veri temizliği.**
   - Kötü tanımlı sorular atıldı.
   - Model bir soruda tutarlı olarak referanstan farklı cevap veriyorsa, referans cevap bir insan uzmana kontrol ettirildi.
   - Çoktan seçmeli sorular boşluk doldurmaya çevrildi (tahminle kazanılmasın diye).
   - Doğrulanamaz veride, SFT modelinin cevapları arasında reward varyansı düşük olan prompt'lar atıldı: bütün cevaplar aynı puanı alıyorsa soru sinyal vermez.
   - RL sırasında doğruluğu 0 ya da 1 olan prompt'lar atılıyor.
4. **Reward modelleri.**
   - Seed-Verifier: cevabı referansla karşılaştıran LLM judge.
   - Seed-Thinking-Verifier: karar vermeden önce adım adım düşünen verifier.
   - Doğrulanamaz görevler için pairwise generative RM (iki cevabı karşılaştırır).
5. **Online data distribution adaptation.** Eğitim sırasında alanların veri oranı ayarlanıyor; böylece alanlar birbirini bozmuyor.

**Sonuç:** Yazarların raporuna göre:
- AIME 2024 86.7; AIME 2025 74.0; GPQA (lisansüstü düzeyde, internette kolayca bulunamayan fen soruları) 77.3; Codeforces pass@8 (8 denemeden en az birinin doğru olma oranı) 55.0.
- Zor bir kümede Seed-Thinking-Verifier %99.3, Seed-Verifier %82.7 doğruluk verdi. Düşünen verifier, düşünmeyenin hatalarının neredeyse hepsini kapatıyor.

**Bizim için:** "SFT örnekleri arasında reward'ı hep aynı çıkan prompt'u at" kuralı, RL öncesi ucuz bir filtre: küçük model 8 denemede hep aynı sonucu buluyorsa o soru RL'e sinyal vermez.

## DAPO: An Open-Source LLM Reinforcement Learning System at Scale (ByteDance Seed & Tsinghua AIR, Mart 2025) — [2503.14476](https://arxiv.org/abs/2503.14476)
**Tek cümlede:** ByteDance Seed ve Tsinghua, Qwen2.5-32B base üzerinde GRPO'yu dört basit teknikle güçlendiren açık kaynak bir RLVR sistemi (verl tabanlı kod, veri ve algoritma) yayımladı.

**Problem:** Büyük reasoning modellerinin RL reçeteleri çoğunlukla açık değil. Naif GRPO'yu uzun CoT'de çalıştırınca entropi çöküyor (model hep aynı cevabı vermeye başlıyor), birçok batch sinyal vermiyor ve uzun cevaplar gürültü yaratıyor. Yazarlar bu sorunları tek tek çözen ve tekrar üretilebilen bir sistem sunmak istedi.

**Ne yaptılar:**
1. **Clip-Higher.** PPO/GRPO'da bir token'ın olasılığının tek güncellemede ne kadar değişebileceği bir aralıkla sınırlanır. Simetrik sınır (±0.2) düşük olasılıklı token'ların büyümesini çok kısıtlar; model keşfi bırakır. DAPO alt sınırı 0.2'de tutup üst sınırı 0.28'e açıyor. Örnek: olasılığı 0.01 olan iyi bir token tek adımda en fazla 0.012 yerine 0.0128'e çıkabiliyor.
2. **Dynamic Sampling.** Bütün denemeleri doğru ya da bütün denemeleri yanlış olan prompt'lar atılıyor. Batch, sonuçları karışık prompt'larla dolana kadar örneklemeye devam ediliyor. Böylece her batch'teki her prompt gerçekten sinyal veriyor.
3. **Token-level policy gradient loss.** GRPO'da loss önce her cevap içinde ortalanır; uzun bir cevaptaki her token az ağırlık alır. Token-level loss bütün token'ları eşit sayıyor. Böylece uzun ve tekrarlı kötü cevaplar yeterince cezalanıyor.
4. **Overlong reward shaping.** Beklenen uzunluk 16,384 token. Ondan sonra 4,096 token'lık yumuşak bir ceza bölgesi var; bu bölgede ceza uzunlukla artıyor. Max 20,480 token. Kesilen örnekleri eğitimde maskelemek (overlong filtering) de denendi.
5. **Diğer ayarlar.** KL yok. Veri DAPO-Math-17K; cevaplar kural tabanlı kontrol kolay olsun diye tam sayıya çevrildi. lr 1e-6 (20 adım warmup), 512 prompt × 16 rollout, mini-batch 512.

**Sonuç:** Yazarların raporuna göre AIME 2024'te 50; DeepSeek-R1-Zero-Qwen-32B'nin 47'sini, onun eğitim adımlarının ~%50'siyle geçti. Kümülatif ablation (AIME24 avg@32, her satır bir öncekinin üstüne bir teknik ekliyor):
- naif GRPO: 30
- + overlong filtering: 36
- + clip-higher: 38
- + soft overlong punishment: 41
- + token-level loss: 42
- + dynamic sampling: 50

Toplamda 20 puanlık kazancın 8 puanı tek başına dynamic sampling'den geliyor.

**Bizim için:** Dynamic sampling tek başına en büyük kazancı (+8) veriyor ve uygulaması kolay: her soru için birkaç rollout al, hepsi doğru ya da hepsi yanlışsa batch'e koyma. Cevabı otomatik kontrol edilebilir biçime çevirme fikri bizde zaten var (result key).

---

## Ortak bakış: çoklu uzman, birleştirme ve distillation reçeteleri (bu bölümdeki raporlardan)
Bu laboratuvarların 2025 sonundan beri büyük modellerde izlediği kalıp neredeyse aynı. Önce ortak bir SFT temeli kuruluyor. Sonra her alan için ayrı RL ile uzman modeller eğitiliyor. En sonda bu uzmanlar tek modelde toplanıyor. Toplama yöntemi rapora göre değişiyor:

- **Self-distillation ile birleştirme.** Uzmanların ürettiği cevaplarla tek bir model eğitiliyor.
  - GLM-4.5: reasoning, agent ve genel sohbet uzmanları tek bir hibrit modelde.
  - Step 3.5 Flash: yedi alan uzmanının rejection sampling'den geçmiş trajectory'leri, mid-training checkpoint'inden başlayan bir modele veriliyor.
  - Ling/Ring 2.6: uzman SFT + uzman RL, sonra distillation.
- **Multi-teacher on-policy distillation.** Eğitilen model kendi rollout'larını üretiyor; büyük modeller her token'ı puanlıyor.
  - MiMo-V2-Flash (MOPD): ilgili alanın uzmanından token düzeyinde log oranı + outcome reward.
  - GLM-5 (cross-stage distillation): önceki SFT/RL checkpoint'leri referans; prompt başına tek deneme (group size 1).
- **Ağırlık birleştirme (model merging).** LongCat-Flash-Thinking: alan uzmanlarının task vector'leri (başlangıçtan farkları) normalize ediliyor, DARE tarzı seyreltme ve işaret budamasıyla birleştiriliyor; sonra genel bir PPO aşaması.
- **Expert iteration / yinelemeli distillation.** Modelin başarılı çıktıları yeni eğitim verisi oluyor, sonra tekrar eğitiliyor.
  - GLM-4.5 agentic RL: RL çıktıları yeni cold-start verisi oluyor, sonra daha zor görevlerle tekrar RL.
  - LongCat-Flash-Thinking'in formal reasoning'i: Lean'de doğrulanan ispatlar veriye ekleniyor.
  - Seed-Coder: model kendi çözümünü sandbox'ta test edip düzeltiyor.
- **Reward model eğitimi.**
  - Seed1.5-Thinking: Seed-Verifier ve düşünerek karar veren Seed-Thinking-Verifier.
  - LongCat-Flash-Thinking: reasoning yapan GenRM (%98.8 doğruluk).
  - Step 3.5 Flash: pairwise GenRM + MetaRM.
  - Tencent Mix-GRM: 8B GRM, SFT + RLVR.
- **Preference optimization.**
  - Seed-Coder: sandbox'la etiketlenmiş ~20K on-policy çiftle DPO.
  - Ling 2.0: Group Arena Reward (round-robin, ikili karşılaştırmalı turnuva).
  - MiMo-VL: Bradley-Terry reward model'li RLHF (ikili tercihlerden puan öğrenen reward model), RLVR ile aynı on-policy koşuda.
- **Reasoning için mid-training.**
  - MiMo-7B: 25T token, üç aşamalı veri karışımı.
  - LongCat-Flash-Thinking: mid-training'e reasoning verisi eklemek küçük modelde AIME-24'ü %27.7 artırdı.
  - LongCat-Flash-Thinking-2601: agentic mid-training verisi.
  - MiMo-V2.6: agent odaklı mid-training; reward hacking'e karşı hizalama örnekleri dahil.
- **[Self-play](00_terimler.md#self-play)** (modelin kendine karşı oynayarak ya da kendi görevlerini üreterek öğrenmesi): Bu laboratuvarlardan doğrulanabilen bir self-play post-training raporu bulunamadı.

**Bizim için:** Bu reçetelerin hepsi büyük ölçekte birden çok uzman eğitmeyi gerektiriyor. Bizim için gerçekçi karşılığı şu: uzman zaten var (large model, 9B). Bu yüzden MOPD tarzı on-policy distillation (küçük modelin trajectory'si + large model'in log-prob'ları + outcome reward), çoklu uzman eğitiminin en ucuz biçimi.
