# NVIDIA (Nemotron)

**Bu bölümde ne var:** NVIDIA'nın Nemotron ailesi ve araştırma ekiplerinin Aralık 2024 – Ekim 2026 arasındaki post-training çalışmaları. Bir kısmı büyük model raporları (Nemotron 3 Nano, Super, Ultra, 3.5), bir kısmı tek bir tekniği inceleyen kısa makaleler (PivotRL, GDPO, DLER, BroRL, ProRL...), bir kısmı da açık veri setleri. Girdiler yeniden eskiye sıralı.

**Bu bölümün ana dersleri:**
- NVIDIA'nın neredeyse her reçetesi aynı sırayı izliyor: önce güçlü bir SFT ya da distillation başlangıcı, sonra doğrulanabilir reward'la RL.
- RL verisi zorluğa göre seçiliyor: modelin her zaman çözdüğü ve hiç çözemediği sorular atılıyor, kalanlar kolaydan zora veriliyor.
- Tek bir görevde yapılan RL başka becerileri bozuyor; çözüm ya bütün görevleri birlikte eğitmek ya da ayrı uzmanları sonra on-policy distillation ile tek modelde birleştirmek.
- Reward'ın kendisi doğru olmalı: hatalı testler ve gevşek kısmi puanlar eğitimi bozuyor, sıkı binary reward çoğu zaman daha iyi.
- Küçük modelde ucuz numaralar işe yarıyor: çok turlu konuşmayı tek adımlara bölmek, uzunluk sınırı koymak, birden çok reward'ı ayrı normalize etmek, tool çıktısını loss'tan maskelemek.

**Makaleler:**
- Nemotron 3.5 Super and Lightning — iki MoE model; uzmanları ayrı eğitip tek modelde birleştiren reçete.
- Nemotron 3.5 Bolt E4B 4GB — Gemma tabanlı, SFT'siz yalnız RL ile eğitilmiş 4GB'lık yerel model.
- Priming Base Models for Agentic Post-Training — base model'i agentic işe hazırlayan mid-training aşaması.
- Nemotron 3 Ultra — 550B model; on'dan fazla uzmanı iki turda tek modele distill ediyor.
- Nemotron 3 Super — 120B model; 21 environment'ta birlikte RL, 96.5K Text-to-SQL kaydı.
- PivotRL — uzun agentic görevlerde yalnız kritik turlarda kısa RL.
- Nemotron-Cascade 2 — alan alan sıralı RL ve araya kendi checkpoint'lerinden distillation.
- Nemotron 3 Nano 4B — 9B modeli budayıp 4B'ye indirme, sonra SFT ve üç aşamalı RL.
- GDPO — birden çok reward'ı ayrı ayrı normalize eden GRPO çeşidi.
- Nemotron 3 Nano — 31.6B model; çok environment'lı RL ve Gauss curriculum.
- Nemotron-Cascade — alanları karıştırmadan sıralı RL.
- ToolOrchestra — başka modelleri ve tool'ları çağıran 8B "orchestrator", maliyet cezalı RL.
- DLER — doğruluğu bozmadan cevabı kısaltan length penalty reçetesi.
- QeRL — 4-bit quantize model üzerinde LoRA ile RL.
- BroRL — adım sayısı yerine soru başına rollout sayısını artırmak.
- RLP — RL'yi pretraining'e taşımak.
- Front-Loading Reasoning — reasoning verisi pretraining'de mi SFT'de mi verilmeli.
- RLBFF — reward model'i ikili ilkelerle eğitmek.
- Nemotron Nano 2 — 12B hibrit model; SFT, DPO, RLHF, model merging.
- Nemotron Post-Training Dataset sürümleri — açık SFT ve RL verileri.
- ProRL v2 — ProRL'yi 3,000+ adıma uzatmak.
- AceReason-Nemotron 1.1 — SFT ile RL'nin birlikte nasıl ölçeklendiği.
- ProRL — uzun RL'nin küçük modelde yeni beceri açtığı iddiası.
- NFT — yanlış cevaplardan da öğrenen supervised yöntem.
- AceReason-Nemotron — önce matematik, sonra kod RL'si.
- HelpSteer3-Preference — insan etiketli açık tercih verisi.
- Llama-Nemotron — reasoning'i açılıp kapanan 8B/49B/253B modeller.
- Nemotron-Research-Tool-N1 — tool calling için kural tabanlı binary reward'lı GRPO.
- AceMath-RL-Nemotron-7B — yalnız RL ile matematik modeli.
- AIMO-2 Winning Solution — matematik yarışmasını kazanan veri ve çözüm seçme yöntemi.
- Nemotron-CrossThink — RL'yi matematik dışı alanlara taşımak.
- OpenCodeReasoning — yarışma kodu için büyük distillation veri seti.
- AceMath — iki aşamalı matematik SFT'si ve matematik reward model'i.

---

## Nemotron 3.5 Super and Lightning: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Models for Agentic AI (NVIDIA, Ekim 2026) — [blog/teknik rapor](https://research.nvidia.com/labs/nemotron/Nemotron-3.5-Super-and-Lightning/)
**Tek cümlede:** İki model, önce daha büyük bir modelden bilgi alarak başlatılıyor; büyük olan Super, ayrı ayrı eğitilen uzman modellerin tek modelde birleştirildiği uzun bir reçeteden, küçük olan Lightning ise kısa bir "SFT + RLVR" reçetesinden geçiyor.

**Problem:** Agentic işler (kod düzelten, terminal kullanan, web'de arayan agent'lar) çok farklı beceriler istiyor. Hepsini tek bir RL koşusunda eğitmek zor: bir beceri gelişirken başka biri bozulabiliyor. Aynı zamanda NVIDIA az aktif parametreli, yani çalıştırması ucuz bir model istiyor.

**Ne yaptılar:**
1. **İki model seçtiler.** Super: 120B toplam, 12B aktif, görsel girdi alabiliyor. Lightning: 30B toplam, 3B aktif, yalnız metin.
   - İkisi de [MoE](00_terimler.md#moe) (mixture of experts): modelin içinde çok sayıda alt ağ ("uzman") var ve her token için yalnız birkaçı çalışıyor. "120B toplam, 12B aktif" şu demek: modelde 120 milyar parametre var, ama bir token işlenirken yalnız 12 milyarı kullanılıyor.
   - "Hybrid Mamba-Transformer": katmanların bir kısmı klasik Transformer attention'ı, bir kısmı Mamba. Mamba, metni sabit boyutlu bir durumla okuyan bir katmandır; uzun metinde attention'dan daha az bellek ve zaman harcar.
2. **Distillation ile başlattılar.** [Distillation](00_terimler.md#distillation): eğitilen model, büyük bir modelin çıktısını taklit ederek öğrenir. Burada 1T (bir trilyon) token boyunca büyük modelin logit'lerini taklit ettiler. Logit, modelin her konumda sözlükteki her token'a verdiği puandır; yalnız en yüksek puanlı 128 token kullanıldı (top-128). Super, Nemotron 3 Ultra Base'den; Lightning, Nemotron 3 Super Base'den başlatıldı.
3. **Super'a agentic SWE [mid-training](00_terimler.md#mid-training) yaptılar.** Mid-training, pretraining ile post-training arasında belirli bir alana yönelik ek eğitimdir. SWE (software engineering): yazılım mühendisliği görevleri. Lightning'de bu adım yok.
4. **[SFT](00_terimler.md#sft) yaptılar** (SFT: örnek cevapları birebir taklit ederek eğitim). Super'da iki aşama: önce geniş bir veri karışımı, sonra eksik kalan yetenekler için küçük ikinci bir aşama. Lightning'de tek aşama. Örnekler 524,288 token'lık dizilere paketlendi (packing: kısa örnekleri uç uca ekleyip tek uzun diziye koymak). Batch 32, learning rate 1e-5.
   - Reasoning verisini üreten büyük modelleri değiştirdiler: matematik ve fen için Kimi K3, matematik ispatı için DeepSeek V4 Pro, yarışma kodu için GLM-5.2.
   - 5,000 token'dan kısa reasoning cevapları attılar; yalnız uzun düşünme örnekleri kaldı.
5. **Ortak RL yaptılar.** [RLVR](00_terimler.md#rl-ve-rlvr): cevabı bir program tarafından kontrol edilebilen görevlerde RL. RLHF: insan tercihinden öğrenilmiş bir puanlayıcıyla RL. İkisi aynı koşuda.
   - Her environment kendi kontrolcüsüne gidiyor: ya bir verifier'a (doğru/yanlış diyen program) ya da bir [reward model](00_terimler.md#reward-model-grm-ve-prm)'e (cevabı puanlayan model).
   - Eğitimden önce her environment'ta modelin aldığı [reward](00_terimler.md#reward) ölçüldü (reward profiling).
   - Batch 8,192 prompt; her prompt için 16 [rollout](00_terimler.md#rollout) (rollout: modelin bir prompt'a ürettiği tam bir deneme). Üretim sınırı 80K token'dan 128K'ya çıkarıldı.
   - Finans agent environment'ında sentetik soruların zorluğu ölçüldü; zorluğa göre bir kısmı SFT havuzuna, bir kısmı RL havuzuna gitti.
6. **Uzman modeller eğittiler.** Ortak RL'nin 120. adımındaki checkpoint'ten beş ayrı kopya dallandı:
   - Agentic uzman: uçtan uca [GRPO](00_terimler.md#grpo) ile Terminal, SWE ve Search görevleri; adım başına 64 prompt × 16 rollout. GRPO: aynı prompt'a üretilen birkaç cevabı birbiriyle kıyaslayıp ortalamadan iyi olanları güçlendiren RL yöntemi.
   - Reasoning uzmanı: 25,600 örneklik bir [curriculum](00_terimler.md#curriculum) (soruların belirli bir sırayla verilmesi). Her 256 prompt'luk batch'in %90'ı fen, %5'i matematik, %5'i kod. Learning rate 4e-6; 80. adımdaki checkpoint seçildi.
   - Video uzmanı.
   - Görsel tool-use uzmanı: yalnız tool'suz çözülemeyen sorular tutuldu.
   - RLHF ile hizalama uzmanı.
7. **Uzmanları MOPD ile tek modelde birleştirdiler.** [MOPD](00_terimler.md#multi-teacher-distillation-mopd) (Multi-Teacher On-Policy Distillation): eğitilen model kendi cevabını üretir. Sorunun alanındaki uzman bu cevabın her token'ı için "bu token'ı ben ne kadar olası bulurdum" der (log-olasılık). [Advantage](00_terimler.md#advantage) (bir token'ın ne kadar güçlendirileceği) şöyle: uzmanın o token'a verdiği log-olasılıktan eğitilen modelinkini çıkar. Uzman token'ı daha olası buluyorsa token güçlenir, daha az olası buluyorsa zayıflar. Verifier gerekmez ve her token ayrı sinyal alır. Bu yaklaşımın tek-uzmanlı hâli [on-policy distillation](00_terimler.md#on-policy-distillation-opd)'dır.
   - 1. aşama: agentic, reasoning, RLHF ve görsel tool uzmanları sırayla %35, %25, %20, %15 ağırlıkla. Kalan %5 "self-anchor": eğitilen modelin donmuş bir kopyası, modelin kendinden fazla uzaklaşmaması için. Adım başına 512 prompt × 1 rollout, learning rate 2e-6, 30 adım.
   - 2. aşama: yavaş gelişen alanlar (chat, görsel), 1,024 prompt, 40 adım. Hedef yumuşatıldı: %20 uzman, %80 eğitilen modelin kendisi.
8. **[Decontamination](00_terimler.md#decontamination) yaptılar** (test sorularının eğitim verisine sızmasını temizlemek). Önce n-gram (ortak kelime dizileri) ve embedding benzerliğiyle aday buldular, sonra bir [LLM judge](00_terimler.md#llm-as-judge-ve-rubric) (yargıç model) karar verdi. 30 benchmark'a karşı 20,671 örnek çıkarıldı: verinin %0.09'u; 14,793'ü SFT'den, 5,878'i RL'den.

**Sonuç:** Yazarların raporuna göre:
- Super, SWE-bench Pro'da ([benchmark](00_terimler.md#benchmarklar): gerçek GitHub hatalarını düzeltme, zor sürüm) 51.78 alıyor ve kendisinden büyük Nemotron 3 Ultra'yı geçiyor. Bunu yaklaşık 4.6 kat daha az aktif parametreyle yapıyor.
- Mid-training'in etkisi: aynı SFT'den sonra DeepSWE'de (yazılım mühendisliği görevleri) [pass@1](00_terimler.md#pass-rate-ve-passk) (ilk denemede çözme oranı) 6.4'ten 10.4'e çıkıyor.
- MOPD'den önce bir agentic benchmark'ta rollout'ların %19.7'si sonsuz döngüye giriyordu. MOPD'den sonra sınırda kesilen cevap oranı %0.3. Yani birleştirme, uzun ve bitmeyen cevap sorununu neredeyse kaldırdı.
- SFT verisi: Kimi K3 verisiyle eğitim birden çok epoch boyunca gelişmeye devam etti; DeepSeek V4 Pro verisi tek geçişte doydu. Yazarlar bunu, daha yoğun reasoning'in küçük modele daha fazla tekrar gerektirmesine bağlıyor.

**Bizim için:** Küçük bir model için Lightning'in hafif yolu ("SFT + RLVR") yeterli görünüyor. Zorluğu ölçülen soruları SFT ve RL havuzlarına ayırmak ve kendi donmuş kopyasıyla dengelenmiş on-policy distillation, Text-to-SQL'de büyük modelden token düzeyinde sinyal almanın ucuz yolu.

---

## NVIDIA Nemotron 3.5 Bolt E4B 4GB (NVIDIA, Ekim 2026) — [blog](https://research.nvidia.com/labs/nemotron/NVIDIA-Nemotron-3.5-Bolt-E4B-4GB/)
**Tek cümlede:** Google'ın hazır küçük modeli Gemma4-E4B-it'in üzerine SFT yapmadan, doğrudan birçok environment'ta RL uygulayarak yerelde yaklaşık 4GB'a sığan bir konuşma agent'ı modeli yaptılar.

**Problem:** Yerel cihazlarda (telefon, dizüstü) çalışan agent'lar küçük bir model ister. Bu modelin tool çağırmayı, talimata uymayı ve kısa cevap vermeyi iyi yapması gerekir. Soru şu: hazır bir instruct modeli SFT'siz, yalnız RL ile bu yönlerde ne kadar geliştirebiliriz?

**Ne yaptılar:**
1. **Başlangıç modeli:** Gemma4-E4B-it (Google'ın talimat izleyen küçük modeli).
2. **RL yöntemi:** Sayfa yalnız RLVR ve RLHF'den söz ediyor. Eğitim NVIDIA'nın açık kütüphaneleri NeMo-RL (RL eğitim kodu) ve NeMo-Gym (RL environment'ları) ile yapıldı. SFT ya da on-policy distillation anılmıyor.
3. **Veri (environment'lar):**
   - Konuşmalı tool use ve function-calling (modelin bir fonksiyonu doğru argümanlarla çağırması).
   - Instruction following: SysBench (sistem mesajına uyma), InverseIFEval ve CFBench (karmaşık ya da alışılmışın tersine talimatlara uyma).
   - Instruction hierarchy: sistem talimatı ile kullanıcı talimatı çeliştiğinde hangisine uyulacağı.
   - Structured outputs (JSON gibi belirli biçimde çıktı), serbest biçim cevaplar ve güncellenmiş GenRM verisi. GenRM: cevabı metin yazarak değerlendiren reward model.
4. **İki mod birlikte:** Her örnek hem reasoning hem non-reasoning modda kullanıldı ([thinking mode](00_terimler.md#thinking-mode): modelin cevaptan önce düşünce yazması ya da yazmaması). Her batch'te non-reasoning örnekler reasoning örneklerin iki katı (2:1).
5. **Uzunluk kontrolü:** GenRM environment'ında length penalty (uzun cevaba ceza) artırıldı. Diğer environment'larda overlong filtering (sınırı aşan cevapları eğitimden çıkarmak) kapalı.
6. **Quantization:** Model Q4_K_M biçiminde 4 bit'e sıkıştırıldı. Sıkıştırmayı ayarlamak için kalibrasyon verisi olarak yaklaşık 1M token'lık RL rollout'u kullanıldı.

**Sonuç:** Yazarların raporuna göre:
- Önceki küçük model Nemotron 3 Nano 4B'den ortalamada yaklaşık %40 yüksek.
- BFCL-v3 (function calling doğruluğu): 68.5; Nano 4B 61.1. Yani tool çağırmada 7.4 puan önde.
- IHEval (instruction hierarchy'ye uyma): 84.8; Nano 4B 51.3. En büyük fark burada.
- Brevity Bench (adından anlaşıldığı kadarıyla kısa ve öz cevap verme): 82.5; Nano 4B 73.6.
- Reasoning açık karşılaştırmalarda %80'e kadar daha az çıktı token'ı.
- Zayıf nokta: RULER 64K'da (64K token'lık uzun bağlamda bilgi bulma) 87.0; Qwen 3.5 4B 95.1. Uzun bağlamda Qwen'in gerisinde.

**Kaynak notu:** Yalnız blog sayfası var; teknik rapor yok. Reçetenin ayrıntıları (algoritma, adım sayısı) sayfada verilmiyor.

**Bizim için:** Hazır bir instruct modelin üzerine SFT'siz, doğrudan çok environment'lı RL ile tool-calling'i belirgin artırmak 4B ölçeğinde mümkün görünüyor. Çıktı uzunluğunu RL'de cezalandırmak, yerelde çalışan modelin hızını doğrudan artırır.

---

## Priming Base Models for Agentic Post-Training: An Open Midtraining Recipe (NVIDIA, Ekim 2026) — [2610.22019](https://arxiv.org/abs/2610.22019)
**Tek cümlede:** Base model'i agentic işe hazırlamak için pretraining ile post-training arasına, gerçek yazılım geliştirme verisiyle ve az miktarda agent kaydıyla yapılan uzun bağlamlı bir mid-training aşaması koydular.

**Problem:** Pretraining verisi kısa bağlamlıdır ve neredeyse hiç agent etkileşimi (model tool çağırır, sonuç gelir, model devam eder) içermez. SFT verisi ise çoğunlukla sentetiktir. SFT'yi çok uzatmak da sonradan RL'nin kazancını azaltabiliyor. Yazarlar bu boşluğu dolduracak bir ara aşama arıyor.

**Ne yaptılar:**
1. **256K token bağlamla mid-training.** Veri, Nemotron 3.5 raporundaki Super karışımı:
   - Issue–PR çiftleri (bir hata kaydı ve onu düzelten kod değişikliği): %41
   - Bütün repository'ler: %20
   - Agent trace'leri (agent'ın adım adım kaydı): %10
   - Commit diff'leri: %3
   - Build ve CI log'ları: %1
   - Pretraining verisinden tekrar (replay; eski bilgiyi unutmamak için): %20
   - Long-context verisi: %5
2. **Agent trace'lerinde [loss masking](00_terimler.md#loss-masking).** Tool'un döndürdüğü cevaplar loss'a katılmadı; model yalnız kendi yazdığı turlardan öğrendi. Örnek: model bir komut yazar, terminal bir çıktı döndürür. Model komutu yazmayı öğrenir, terminal çıktısını ezberlemez.
3. **Doğal veri kendi biçiminde.** Issue, kod ve log'lar chat template'ine (sohbet biçimine) sokulmadan, olduğu gibi verildi.
4. **Decontamination.** Her kaynak SWE-bench ve Terminal-Bench'e karşı temizlendi.
5. **Değerlendirme yöntemi.** Bir checkpoint'i ölçmek için kısa ve sabit bir SFT koşusu önerdiler. Neden: base model üzerinde ölçülen ara metrikler, post-training sonrasındaki sonuçla güvenilir biçimde ilişkili değildi.

**Sonuç:** Yazarların raporuna göre (özetteki rakamlar; her karşılaştırma aynı SFT'den sonra, mid-training'siz ve mid-training'li):
- Lightning, 500B mid-training token'ı: SWE-bench Verified (gerçek GitHub hatalarını düzeltme) 60.7 → 64.5; SWE-bench Multilingual (başka programlama dilleri) 55.8 → 62.8; SWE-bench Pro (zor sürüm) 32.0 → 35.5.
- Super, 280B token: DeepSWE 11.7 → 15.7; SWE-bench Verified 72.9 → 74.3.
- Farklı agent harness'leri (agent'ı çalıştıran farklı çerçeveler) arasında sonuçlar daha tutarlı hâle geldi.

**Kaynak notu:** Rakamlar Nemotron 3.5 raporuyla tutarsız. O rapor, yayımlanan Lightning'de mid-training olmadığını ve yayımlanan Super'ın 65.4B token aldığını söylüyor. Bu makaledeki koşular yayımlanan modeller değil, araştırma koşuları olabilir.

**Bizim için:** Bizim ölçekte mid-training yapılamaz, ama iki ders taşınır. Agent trace'lerinde tool çıktısını (`execute_sql` sonucu) loss'tan maskelemek. Bir checkpoint'i kısa ve sabit bir SFT ile değerlendirme koşusuyla ölçmek.

---

## Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning (NVIDIA, Haziran 2026) — [2606.15007](https://arxiv.org/abs/2606.15007)
**Tek cümlede:** 550B'lik modelde SFT ve ortak RL'den sonra on'dan fazla alan uzmanı ayrı eğitildi, sonra bu uzmanlar iki tur MOPD ile tek modelde birleştirildi; birleşik model bazı alanlarda uzmanını bile geçti.

**Problem:** Tek bir ortak RL koşusu bütün alanları aynı anda iyileştirmekte zorlanıyor; bir alan gelişirken başka biri geriliyor. Ayrı uzmanlar her alanda daha iyi, ama tek bir modelde toplanmaları gerekiyor.

**Ne yaptılar:**
1. **Model:** 550B toplam, 55B aktif parametre (MoE).
2. **İki aşamalı SFT.**
   - 1. aşama: 294,912 token'lık paketler, batch 64, 204,800 örnek. Learning rate 1.5e-5'ten 1e-6'ya cosine eğrisiyle düşüyor.
   - 2. aşama: 515K token'a kadar uzun diziler, 19,200 örnek.
   - Veri örnekleri: matematik 1.8M tool'lu + 1.9M tool'suz; kod 1.2M Python + 1.0M C++ + 1.3M tool'lu Python; terminal yaklaşık 370K konuşma; güvenlik yaklaşık 135K. Kod verisi [rejection sampling](00_terimler.md#rejection-sampling) ile süzüldü (çok cevap üret, yalnız kontrolden geçenleri tut).
   - SWE trajectory'leri (agent'ın baştan sona kaydı) kural tabanlı bir analizciden geçti. Analizci şunlara baktı: çözüm eksiksiz teslim edilmiş mi, yasak git işlemi var mı, edit-test döngüsü (değiştir, test et, tekrar değiştir) sağlıklı mı.
3. **Birleşik RLVR (+RLHF).** Asenkron GRPO: rollout üretimi ile eğitim aynı anda, ayrı makinelerde yürüyor. Global batch 8,192, prompt başına 16 rollout, üretim sınırı 48K'dan 64K'ya.
   - Eğitimden önce reward profiling (her environment'ta başlangıç reward'ını ölçmek).
   - Gauss tabanlı veri karışımı ve curriculum: soruları, modelin o soruyu çözme oranı hedeflenen bir değere yakın olacak şekilde seçmek (ayrıntısı Nemotron 3 Nano girdisinde).
   - Reasoning effort (modelin ne kadar uzun düşüneceği) RL'de optimize ediliyor.
4. **On'dan fazla alan uzmanı.** Agentic görevlerin çoğunda PivotRL'e benzer tek-tur rollout kullanıldı (PivotRL kendi girdisinde). SWE uzmanının sırası: SFT → PivotRL → uçtan uca SWE-RL (binary reward: testler geçerse 1, geçmezse 0; 200 tura kadar).
5. **İki tur MOPD.** Uzmanların reverse KL tabanlı yoğun token advantage'ı: eğitilen modelin ürettiği her token için uzmanın ve modelin log-olasılık farkı. [PPO](00_terimler.md#ppo) tarzı [clipping](00_terimler.md#clip-ve-clip-higher): tek adımda modelin çok fazla değişmesini engelleyen sınır. IcePop token maskeleme: eğitimdeki ve üretimdeki olasılıkları çok farklı çıkan token'ları güncellemeden çıkarmak. Adım başına 1,024 prompt × 1 rollout, 192K token üretim. Prompt başına birden çok rollout ek fayda getirmedi.

**Sonuç:** Yazarların raporuna göre (RLVR sonrası → 1. MOPD → 2. MOPD):
- SWE-bench Verified (GitHub hatası düzeltme): 65.8 → 70.1 → 71.7. SWE uzmanının kendisi 72.5; birleşik model uzmana çok yaklaştı.
- Terminal Bench 2.0 (terminalde görev çözme): 44.5 → 50.8 → 54.0. Uzman 50.0; yani birleşik model uzmanını geçti.
- BrowseComp (web'de zor bilgi arama): 31.0 → 41.0 → 44.4.
- IFBench (talimata uyma): 78.4 → 80.0 → 81.7.
- MOPD warmup ablation'ı: warmup'sız GDPVal (meslek görevlerinden oluşan gerçek iş çıktıları) 35.3, warmup'lı 46.7. Isınma aşaması 11.4 puan fark yaratıyor.
- Logit matching (uzmanın en olası k token'ına ya da bütün sözlüğe olan dağılımını taklit etmek) yalnız örneklenen token'a bakan basit hedefi geçemedi; bazı agentic benchmark'larda geride kaldı.
- Medium-effort modu (daha kısa düşünme) yaklaşık 2.5 kat daha az token kullanıyor ve yaklaşık %7 doğruluk kaybediyor.

**Bizim için:** Farklı becerileri ayrı RL koşularında uzmanlaştırıp sonra tek modelde on-policy distillation ile birleştirmek, tek karışık RL koşusunun bozduğu yerleri onarıyor. Bizde büyük modelin yalnız örneklenen token'a verdiği log-olasılık yeterli; tam logit gerekmez.

---

## Nemotron 3 Super: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning (NVIDIA, Nisan 2026) — [2604.12374](https://arxiv.org/abs/2604.12374)
**Tek cümlede:** 120B'lik modelde iki aşamalı SFT ve çok aşamalı RL kullanıldı; agentic veri ve RL environment çeşitliliği önceki modele göre çok büyütüldü, SFT verisine 96.5K Text-to-SQL kaydı da girdi.

**Problem:** Bir önceki küçük model (Nano) yalnız 5 alanda tool-use konuşmasıyla eğitilmişti. Agentic işlerde iyi olmak için çok daha geniş veri ve environment gerekiyor. Ayrıca uzun girdili, kısa çıktılı görevler ile uzun reasoning görevlerini aynı SFT'de dengelemek zor.

**Ne yaptılar:**
1. **Model ve pretraining:** 120B toplam, 12B aktif; 25T token pretraining.
2. **İki aşamalı SFT.**
   - 1. aşama: loss token düzeyinde ortalanıyor (her token eşit ağırlık); 7M'den fazla örnek, learning rate 1e-5.
   - 2. aşama: loss konuşma başına ortalanıyor (her konuşma eşit ağırlık). Neden: token düzeyinde ortalamada uzun çıktılar baskın olur; kısa cevaplı görevler ezilir. Bu aşamada 1. aşama karışımının %85'i ve uzun bağlam verisi var.
   - Tek aşamalı SFT, uzun girdili ve kısa çıktılı görevlerde belirgin bozulma yaptı; iki aşama bu yüzden.
3. **Agentic veri.** 279,116 konuşmalı tool-use konuşması, 838 alanda (Nano'da 15,588 konuşma, 5 alan). Yaklaşık 1.5M genel tool-calling trajectory'si. 96.5K Text-to-SQL kaydı. Yaklaşık 15K CLI (komut satırı) görevi, yaklaşık 3K SWE görevi. LLM judge ile kalite kontrolü ve kod benchmark'larına karşı decontamination.
4. **Reasoning'i açıp kapama ve bütçe.** Reasoning-off modunu öğretmek için rastgele %3 örnekte reasoning silindi. 350 adımlık "yarı on-policy" SFT aşamasında reasoning'in %12'si rastgele uzunluklarda kesildi; model kısa düşünme bütçesinde de cevap vermeyi öğrensin diye.
5. **RLVR: 21 environment hep birlikte.** Tek environment'ta eğitim başka alanlarda bozulma yapıyordu.
   - SFT modelinin her zaman çözdüğü prompt'lar atıldı (öğretecek bir şey yok). Kalanlar zorluğa göre sıralandı.
   - Asenkron GRPO: eğitilen model, rollout'u üreten modelden en fazla bir adım ileride. Bu küçük farkı düzeltmek için maskeli [importance sampling](00_terimler.md#importance-sampling) kullanıldı (eski modelle üretilmiş örneği, yeni modele göre yeniden ağırlıklandırmak; farkı çok büyük olan token'lar maskelenir). Bu, tam [on-policy](00_terimler.md#on-policy-ve-off-policy) eğitimden biraz sapmak demek.
   - Adım başına 256 prompt × 16 cevap; üretim sınırı 49K'dan 64K'ya.
6. **SWE-RL ayrı aşama.** Konteynerde OpenHands agent'ı çalışıyor; testler geçerse reward 1 (binary). Farklı harness biçimleri kullanıldı.
7. **RLHF.** Qwen3-235B'den başlatılmış, ilkelere göre değerlendiren bir GenRM (metin yazarak puanlayan reward model).
8. **MTP healing.** MTP (multi-token prediction) modelin birden çok sonraki token'ı tahmin eden, hızlı üretim için kullanılan ek katmanıdır. Adından anlaşıldığı kadarıyla RL'den sonra bu katman yeniden ayarlanıyor; ayrıntısı bu dosyada yok.
9. **PivotRL** agentic görevlerde kullanıldı.

**Sonuç:** Yazarların raporuna göre:
- AIME25 (lise matematik olimpiyatı soruları, tool'suz): 90.21.
- LiveCodeBench v5 (yeni yarışma kodu soruları): 81.19.
- SWE-Bench (OpenHands ile, GitHub hatası düzeltme): 60.47.
- TauBench V2 (müşteri hizmeti gibi senaryolarda tool'lu konuşma) ortalaması: 61.15.
- Arena-Hard-V2 (zor sohbet soruları, yargıç modelle): 73.88.
- GPT-OSS-120B ile benzer doğruluk, 2.2 kata kadar daha yüksek throughput (saniyede üretilen token).
- Yazarlar ayrıntılı RL ablation rakamı vermiyor; "tek environment bozuyor" ve "tek aşamalı SFT bozuyor" bulguları sayısız.

**Bizim için:** SFT verisinde 96.5K Text-to-SQL kaydı ve çok sayıda tool-calling trajectory'si var; yani NVIDIA Text-to-SQL'i genel agentic becerinin bir parçası sayıyor. "Her zaman çözülen prompt'u at, kalanı zorluğa göre sırala" kuralı BIRD train RL verimize doğrudan uygulanabilir.

---

## PivotRL: High Accuracy Agentic Post-Training at Low Compute Cost (NVIDIA, Mart 2026) — [2603.21383](https://arxiv.org/abs/2603.21383)
**Tek cümlede:** Uzun agentic görevlerde uçtan uca RL yerine, hazır SFT trajectory'lerinin yalnız kritik ara turlarında kısa RL yaparak SFT'nin ucuzluğunu ve RL'nin genelleme gücünü birleştirdiler.

**Problem:** Uzun agentic görevlerde ([agentic RL](00_terimler.md#agentic-rl-ve-multi-turn): modelin birçok tur boyunca tool çağırıp sonuç gördüğü RL) iki seçenek var. SFT ucuz, ama modeli eğitim alanının dışında bozuyor. Uçtan uca RL ise genelleşiyor, ama her denemede görevi baştan sona oynatmak çok pahalı. Yazarlar ikisinin arasında bir yol arıyor.

**Ne yaptılar:**
1. **Başlangıç noktası:** Elde zaten var olan expert trajectory'leri (iyi bir agent'ın baştan sona çözüm kayıtları; SFT verisi).
2. **Pivot turlarını seçtiler.** Trajectory'nin her ara turunda, o ana kadarki geçmiş verildiğinde model birkaç eylem örnekliyor. Örneklenen eylemlerin sonuçları çok farklılaşıyorsa (bazıları işe yarıyor, bazıları yaramıyor) o tur bir "pivot"tur. Örnek: bir SQL görevinde şemayı okuma turu herkes için aynı sonucu verir, pivot değildir. Hangi JOIN'i yazacağına karar verilen tur ise bazı denemelerde doğru, bazılarında yanlış sonuç verir; pivot odur.
3. **RL'yi yalnız pivot turlarında yaptılar.** Model, geçmişi expert'ten alıp yalnız o turda kısa, on-policy bir rollout yapıyor. Bütün görevi baştan oynatmak gerekmiyor.
4. **Reward'ı esnek tuttular.** Expert'in yazdığı eylemle birebir aynı metni yazmak gerekmiyor; işlevsel olarak eşdeğer eylemler de ödül alıyor. Örnek: aynı sonucu veren iki farklı yazılmış komut ikisi de doğru sayılıyor.
5. **Gerekçe:** Yazarlar, bu kurulumun güçlü bir öğrenme sinyali verirken görevle ilgisiz eylemlerdeki davranışı büyük ölçüde koruduğunu teorik olarak savunuyor. SFT'nin alan dışı bozulmasının nedeni tam da bu ilgisiz davranışların değişmesi.
6. **Kullanım:** Nemotron 3 Super ve Ultra'da agentic programlama, search, terminal ve konuşmalı tool use'ta kullanıldı.

**Sonuç:** Yazarların raporuna göre:
- Aynı veriyle standart SFT'ye göre dört agentic alanda ortalama +4.17 puan alan içi (eğitildiği türden görevler) ve +10.04 puan alan dışı (eğitilmediği görevler) doğruluk. Yani asıl kazanç genellemede.
- SWE-Bench'te (GitHub hatası düzeltme) uçtan uca RL'ye yakın doğruluk, 4 kat daha az rollout turuyla.
- Nemotron 3 Super raporuna göre alan dışı ölçümde SFT −9.48 puan geriletirken PivotRL +0.21 ile yerinde kalıyor.

**Bizim için:** Experience log'daki çözülmüş trajectory'lerden yalnız belirsiz turlarda (hangi SQL'i deneyeceği ya da ne zaman submit edeceği) kısa rollout yapmak, Mac'te tam çok turlu RL'den çok daha ucuz. Eşdeğer SQL'i metinle değil sonuç eşleşmesiyle (result key) ödüllendirmek bu fikre birebir uyuyor.

---

## Nemotron-Cascade 2: Post-Training LLMs with Cascade RL and Multi-Domain On-Policy Distillation (NVIDIA, Mart 2026) — [2603.19220](https://arxiv.org/abs/2603.19220)
**Tek cümlede:** Bir SFT'den sonra RL'yi alan alan sırayla yaptılar (Cascade RL) ve araya, önceki aşamalarda bozulan becerileri geri getirmek için pipeline'ın kendi ara checkpoint'lerinden on-policy distillation koydular.

**Problem:** RL'yi alanlar arasında sırayla yapmak altyapıyı basitleştiriyor (her alanın cevap uzunluğu ve kontrol süresi farklı). Ama sonraki bir alanın RL'si önceki bir alanda kazanılanı bozabiliyor. Ayrı büyük uzman modeller eğitmek de pahalı.

**Ne yaptılar:**
1. **Başlangıç:** Nemotron-3-Nano-30B-A3B-Base (30B toplam, 3B aktif).
2. **Tek aşamalı büyük SFT.** 256K token'lık paketler, yaklaşık 1.5 epoch. Cevaplar çoğunlukla GPT-OSS-120B'den. Testi olan yerde yalnız doğru cevaplar tutuldu. Kod prompt'larının yaklaşık %24.2'si tekrar diye atıldı. Boyut örnekleri: matematik 1.8M tool'lu + 2.6M tool'suz; konuşmalı tool use 822K; terminal agent 490K.
3. **Sıralı RL aşamaları:**
   - IF-RL (talimata uyma): 128 prompt × 16 rollout, learning rate 3e-6, yaklaşık 180 adım.
   - Çoklu alan RL: %55 STEM çoktan seçmeli, %30 agentic tool calling, %15 structured output; yaklaşık 70 adım.
   - MOPD (aşağıda).
   - RLHF: GenRM ile, yaklaşık 30 adım.
   - Long-context RL.
   - Code RL: 3.5K zor prompt. GPT-OSS-120B'nin 8 denemenin 8'inde çözdüğü prompt'lar atıldı. Sıkı binary reward.
   - SWE RL.
4. **Bütün RL aşamalarında ortak ayarlar:**
   - Strictly on-policy GRPO: her batch o anki modelle üretiliyor ve bir kez kullanılıyor; bu yüzden importance ratio (yeni ve eski modelin olasılık oranı) hep 1.
   - [KL penalty](00_terimler.md#kl-penalty) yok (modeli başlangıç hâline yakın tutan ceza kullanılmıyor).
   - [Dynamic sampling](00_terimler.md#dynamic-sampling): bütün rollout'ları doğru ya da bütün rollout'ları yanlış olan prompt grupları atılıyor; çünkü GRPO'da bu gruplar sıfır sinyal verir.
   - Üretim sınırını aşan cevaba 0 reward.
5. **MOPD (kendi checkpoint'lerinden).** "Uzmanlar" ayrı büyük modeller değil, pipeline'ın kendi checkpoint'leri: matematik için SFT checkpoint'i, ayrıca RLHF checkpoint'i ve çoklu alan RL checkpoint'i. Eğitilen model cevap üretiyor; her örneklenen token için advantage = uzmanın log-olasılığı eksi modelin log-olasılığı. Importance ratio 0.5 ile 2.0 arasına kırpılıyor (truncated). 128 prompt × 4 rollout ya da 512 × 1 (ikisi benzer sonuç). Learning rate 2e-6; yaklaşık 40–50 adımda yakınsıyor.

**Sonuç:** Yazarların raporuna göre:
- Yalnız matematikle AIME25'te (lise matematik olimpiyatı): GRPO 25 adımda 89.9'dan 91.0'a çıkıyor; MOPD 30 adımda 92.0'a ulaşıyor. Benzer adımda MOPD daha yüksek.
- ArenaHard v2 Hard Prompt (zor sohbet soruları): RLHF 100 adımda 81.7; MOPD 52 adımda 85.5. Yarı adımda daha iyi.
- Final model: AIME 2025 92.4 (tool'lu 98.6), LiveCodeBench v6 (yeni yarışma kodu) 87.2, IFBench (talimata uyma) 82.9. IMO, IOI ve ICPC 2025'te (matematik, bilişim ve programlama olimpiyatları) altın madalya düzeyi.
- Agentless SWE verisi (agent döngüsü olmadan, doğrudan yama üretme) eklemek SWE-bench Verified'ı 48.9'dan 49.9'a çıkardı.
- Zayıf yanlar: GPQA (lisansüstü fen soruları), BFCL v4 (function calling) ve τ²-Bench'te (tool'lu müşteri hizmeti konuşması) Qwen3.5-35B-A3B'nin gerisinde.

**Bizim için:** "Uzman" için ayrı bir büyük model gerekmiyor. Kendi daha iyi checkpoint'imizden on-policy distillation, RL'nin bozduğu becerileri az adımda geri getiriyor ve GRPO'dan daha hızlı yakınsıyor.

---

## Nemotron 3 Nano 4B: A Compact Hybrid Model for Efficient Local AI (NVIDIA, Mart 2026) — [blog](https://huggingface.co/blog/nvidia/nemotron-3-nano-4b)
**Tek cümlede:** 9B'lik bir modeli budayarak 4B'ye indirdiler, budanmış modeli 9B'den distillation ile onardılar, sonra SFT ve üç aşamalı RLVR uyguladılar.

**Problem:** Yerel cihazlarda (ör. Jetson gibi küçük NVIDIA kartları) çalışacak küçük ama yetenekli bir model gerekiyor. Sıfırdan 4B eğitmek yerine var olan 9B modeli küçültmek daha ucuz.

**Ne yaptılar:**
1. **Budama (pruning) — Nemotron Elastic ile.** Nemotron Nano 9B v2 küçültüldü. Hangi boyutların budanacağını, modelle birlikte eğitilen bir router (seçici ağ) seçiyor. Sonuç:
   - Katman sayısı 56 → 42
   - Mamba head sayısı 128 → 96
   - FFN genişliği (her katmandaki ileri besleme ağı) 15680 → 12544
   - Embedding boyutu 4480 → 3136
2. **Distillation (onarma).** Budanan model, donmuş 9B modeli taklit ederek eğitildi.
   - 1. aşama: 63B token, 8K bağlam; verinin yaklaşık %70'i post-training, %30'u pretraining verisi.
   - 2. aşama: 150B token, 49K bağlam.
   - Toplam yaklaşık 213B token.
3. **İki aşamalı SFT.** 1. aşama: Nemotron-Post-Training-v3'ün alt kümeleri (matematik, kod, fen, chat, talimata uyma, agentic). 2. aşama: güvenlik için küçük bir koşu.
4. **Üç aşamalı RLVR** (NeMo-RL ile). Örneklerin yarısı reasoning, yarısı non-reasoning modda. KL penalty aşamadan aşamaya artırıldı; yani model giderek başlangıç hâline daha sıkı bağlandı.
   - (1) Tek turlu talimata uyma.
   - (2) NeMo-Gym'de tek ve çok turlu talimata uyma ve structured output (JSON, XML).
   - (3) Konuşmalı, çok turlu tool-calling veri setinin ön sürümü.
   - RL algoritmasının adı verilmiyor.

**Sonuç:** Yazarların raporuna göre:
- Kendi boyut sınıfında IFBench, IFEval (talimata uyma) ve Orak'ta (oyun agent'ı görevleri) en iyi olduğunu söylüyorlar.
- Q4_K_M GGUF (4 bit'e sıkıştırılmış biçim) modeli, BF16 (tam hassasiyet) modelin doğruluğunu medyan olarak %100 koruyor; yani sıkıştırma kayıpsız görünüyor.
- Jetson Orin Nano'da saniyede 18 token.

**Kaynak notu:** Yalnız blog var. Doğruluk tablosu görsel olarak verildiği için sayılar okunamadı; "en iyi" iddiası rakamsız aktarılıyor.

**Bizim için:** NVIDIA'nın 4B ölçeğindeki reçetesi "distillation + SFT + kısa, aşamalı RLVR": önce biçim ve talimata uyma, sonra çok turlu tool-calling. KL'yi giderek artırmak, küçük modelin önceki aşamalarda kazandığı biçim disiplinini korumanın basit bir yolu.

---

## GDPO: Group reward-Decoupled Normalization Policy Optimization for Multi-reward RL Optimization (NVIDIA, Ocak 2026) — [2601.05242](https://arxiv.org/abs/2601.05242)
**Tek cümlede:** Birden çok reward toplanıp GRPO ile normalize edilince farklı durumların aynı sinyale çöktüğünü gösterdiler ve her reward'ı önce ayrı normalize eden GDPO'yu önerdiler (NVIDIA tech report, ICML 2026).

**Problem:** Çoğu görevde tek reward yetmez: doğruluk, biçim, uzunluk gibi birkaç parça vardır. GRPO bunları toplayıp grup içinde normalize eder. Sorun: farklı başarı kombinasyonları aynı toplamı verir ve model aralarındaki farkı göremez. Örnek: biçim reward'ı 0/1, doğruluk reward'ı 0/1 olsun. "Biçim doğru, cevap yanlış" (1+0) ile "biçim yanlış, cevap doğru" (0+1) aynı toplamı, dolayısıyla aynı advantage'ı alır.

**Ne yaptılar:**
1. **GDPO formülü (kelimelerle):** Her reward parçası, aynı prompt'un rollout grubu içinde ayrı ayrı normalize ediliyor: o reward'dan grubun ortalaması çıkarılıyor, grubun standart sapmasına bölünüyor. Sonra bu normalize edilmiş parçalar toplanıyor. Toplam, bütün batch düzeyinde bir kez daha normalize ediliyor. Böylece seyrek görülen bir başarı (ör. grupta tek doğru cevap) kendi ölçeğinde büyük sinyal alıyor, sık görülen biçim başarısı onu ezmiyor.
2. **Tool calling deneyi** (ToolRL kurulumu):
   - Modeller: Qwen2.5-Instruct 1.5B ve 3B.
   - Veri: yaklaşık 4K örnek (2K ToolACE, 1K Hammer, 1K xLAM; hepsi function-calling veri setleri).
   - Reward: biçim reward'ı (0 ya da 1) + doğruluk reward'ı (−3 ile 3 arası).
   - 100 adım, prompt başına 4 rollout, batch 512, learning rate 1e-6.
3. **Matematik deneyi:** Uzunluk reward'ı + doğruluk reward'ı. Uzunluk reward'ını yalnız doğru cevaba vermek ("koşullu" uzunluk reward'ı), iki reward'ın ağırlığını elle ayarlamaktan daha güvenilir çıktı. Yani "kısa ol" ödülü ancak cevap doğruysa geçerli.
4. **Kod deneyi:** Üç reward'lı bir kurulum.

**Sonuç:** Yazarların raporuna göre:
- BFCL-v3 (function calling doğruluğu) ortalaması, 1.5B: GRPO 30.18 → GDPO 32.81. Biçim doğruluğu 76.33 → 80.66. 3B: 39.20 → 40.87. Kazanç küçük ama iki boyutta da tutarlı.
- DeepSeek-R1-1.5B ile AIME (lise matematik olimpiyatı): 23.1 → 29.4. Uzunluk sınırını aşan cevap oranı %10.8 → %6.5. Yani hem daha doğru hem daha kısa.
- Kodda pass rate korunurken uzunluk ihlali ve bug oranı düştü.

**Bizim için:** Bizim reward'ımız da çok parçalı olacak: doğru sonuç, geçerli tool call biçimi, az çağrı. Bunları toplamadan önce ayrı normalize etmek ve verimlilik reward'ını yalnız doğru cevaba bağlamak, 1.5B–3B'de ölçülmüş ucuz bir kazanç.

---

## Nemotron 3 Nano: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning (NVIDIA, Aralık 2025) — [2512.20848](https://arxiv.org/abs/2512.20848)
**Tek cümlede:** 31.6B'lik modelde SFT'den sonra bütün environment'larda aynı anda RLVR ve ardından RLHF yaptılar; Nemotron serisinde RL ilk kez bu ölçekte büyütüldü ve RL altyapısı (NeMo-RL, NeMo-Gym) açık kaynak verildi.

**Problem:** Önceki Nemotron'larda post-training çoğunlukla SFT'ye dayanıyordu. Agentic ve reasoning becerileri için RL'yi büyütmek istiyorlar, ama iki sorunla karşılaşıyorlar: tek environment'ta RL diğer becerileri bozuyor ve rastgele örneklenen sorular eğitimi kolay görevlere kaydırıyor.

**Ne yaptılar:**
1. **Model:** 31.6B toplam, yaklaşık 3.2B aktif. Eşlik eden white paper: [2512.20856](https://arxiv.org/abs/2512.20856).
2. **SFT.** Yaklaşık 18M örnek, dinamik örnekleme. Örneklerin %10'unda reasoning silindi (reasoning açık/kapalı kontrolünü öğretmek için); %3'ünde reasoning rastgele uzunluklarda kesildi (bütçe kontrolü). 13,000 adım, batch 64, learning rate 5e-5. Filtreler: yapısal kontroller, kendini tekrar eden reasoning'in atılması, LLM judge.
3. **Multi-environment RLVR** (bütün environment'lar aynı anda):
   - Matematik: DAPO 17K, SkyWorks 104K.
   - Kod: 22K.
   - STEM çoktan seçmeli: 135K.
   - Structured output: 9K (çıktı şemaya uyuyorsa 1, uymuyorsa 0).
   - Talimata uyma: 46K + 3K çok turlu.
   - Long-context soru–cevap: 12K.
   - Agentic tool use: Workplace Assistant (690 görev, 26 tool) ve yaklaşık 1K bankacılık görevi.
4. **RL ayarları.** Senkron GRPO (üretim ve eğitim sırayla). Maskeli importance sampling. MoE router donduruldu (hangi uzmanın seçileceğini belirleyen katman eğitilmedi). Overlong filtering (sınırı aşan cevaplar loss'tan çıkarıldı). Adım başına 128 prompt × 16 üretim; üretim sınırı 49K.
5. **Gauss curriculum.**
   - Önce SFT checkpoint'inin %100 çözdüğü prompt'lar atıldı.
   - Her prompt'un pass rate'i (modelin o soruyu çözme oranı) ölçüldü.
   - Prompt'lar, merkezi hedef bir pass rate olan bir Gauss (çan eğrisi) dağılımından örnekleniyor: pass rate'i hedefe yakın sorular daha sık seçiliyor.
   - Hedefin merkezi eğitim boyunca doğrusal olarak azalıyor. Basit bir örnek (rakamlar yalnız açıklama için): başta pass rate'i 0.8 civarı (kolay) sorular, sonra 0.5, en sonda 0.2 civarı (zor) sorular ağırlıkta.
   - İlerleme durunca görevler yeniden profilleniyor (pass rate'ler yeniden ölçülüyor).
6. **RLHF.** Qwen3-235B'den GRPO ile eğitilmiş bir GenRM (HelpSteer3 vb. veriyle).
   - Dairesel ikili karşılaştırma: N cevabın hepsini birbiriyle kıyaslamak N² karşılaştırma ister. Bunun yerine her cevap yalnız sıradakiyle kıyaslanıyor (1–2, 2–3, ..., N–1); N karşılaştırma yetiyor.
   - Grup içi sıfır ortalamalı uzunluk ödülü/cezası: grubun ortalamasından kısa cevaplar ödül, uzunlar ceza alıyor; toplamda grup reward'ı değişmiyor.

**Sonuç:** Yazarların raporuna göre:
- AIME25 (lise matematik olimpiyatı, tool'suz): 89.06.
- LiveCodeBench v6 (yeni yarışma kodu): 68.25.
- SWE-Bench (OpenHands ile, GitHub hatası düzeltme): 38.76.
- BFCL v4 (function calling): 53.76.
- TauBench V2 (tool'lu müşteri hizmeti konuşması) ortalaması: 49.04.
- Ablation'lar sayısal değil, yalnız sözel:
  - Curriculum'suz rastgele örnekleme eğitimi kolay görevlere kaydırıyor.
  - Tek environment'lı RL diğer benchmark'larda telafisi zor bozulma yapıyor.
  - RLVR, SFT'yi 3 ve 5 epoch uzatarak elde edilen checkpoint'lere eşit ya da onlardan üstün.
  - Uzunluk kontrolü, doğruluk kaybetmeden cevapları yaklaşık %30 kısalttı.

**Bizim için:** Kolaydan zora kayan, pass rate'e göre Gauss curriculum ve "%100 çözülen soruyu at" kuralı küçük bir BIRD RL havuzunda kolayca uygulanır. Biçim ve talimata uyma environment'ını Text-to-SQL ile birlikte tutmak, tek görevli RL'nin bozulmasını önler.

---

## Nemotron-Cascade: Scaling Cascaded Reinforcement Learning for General-Purpose Reasoning Models (NVIDIA, Aralık 2025) — [2512.13607](https://arxiv.org/abs/2512.13607)
**Tek cümlede:** İki aşamalı SFT'den sonra RL'yi alanları karıştırmadan sırayla yaptılar (RLHF → talimata uyma → matematik → kod → SWE) ve sonraki alanın RL'sinin öncekileri nadiren bozduğunu gösterdiler.

**Problem:** Farklı alanların cevap uzunluğu ve doğrulama süresi çok farklı. Örnek: matematik cevabı bir saniyede kontrol edilir, kod testleri dakikalar sürebilir. Hepsini aynı RL batch'inde karıştırmak altyapıyı karmaşıklaştırıyor. Sıralı RL bunu basitleştiriyor; soru, sıralı eğitimin önceki becerileri unutturup unutturmadığı.

**Ne yaptılar:**
1. **Başlangıç modelleri:** Qwen3-8B-Base ve Qwen3-14B-Base.
2. **İki aşamalı SFT.**
   - 1. aşama, 16K bağlam: 2.8M genel örnek (3.2B token), matematik 2.77M, kod 1.42M.
   - 2. aşama, 32K bağlam: yeni matematik ve kod, 310K tool calling konuşması, SWE verisi.
   - 9-gram decontamination (test sorularıyla 9 kelimelik ortak dizisi olan örnekleri atmak).
3. **Bütün RL aşamalarında ortak ayarlar:** Strictly on-policy GRPO. KL yok; bu durumda GRPO, grup içinde normalize edilmiş basit REINFORCE'a (en temel RL güncellemesi) iniyor. Loss token düzeyinde ortalanıyor.
4. **RL aşamaları sırayla:**
   - **RLHF ilk sırada,** çünkü cevap uzunluğunu ve tekrarı azaltıyor; sonraki aşamalar daha kısa cevaplarla başlıyor. RLHF verisinden matematik ve kod prompt'ları çıkarıldı; matematik eklemek AIME25'i %2 düşürmüştü.
   - **IF-RL (talimata uyma):** dinamik filtre, batch 128 prompt × 8 rollout, learning rate 2e-6.
   - **Math RL:** AceReason-Nemotron-7B'nin 16 denemede en az %75 çözdüğü problemler atıldı. Her epoch sonunda %100 ya da %0 doğrulu problemler havuzdan çıkarılıyor; zor olanlar %10, kolaylar %1 olasılıkla geri ekleniyor. Uzunluk curriculum'u (8B için): 24K → 32K → 40K token. Reward: doğruluk; dil karıştırana (ör. cevap ortasında Çince'ye geçene) −1.
   - **Code RL:** 7B'nin 8 denemenin 8'inde çözdüğü ya da DeepSeek-R1-0528'in 8 denemenin hiçbirinde çözemediği problemler atıldı; 9.8K kaldı. Bütün testler geçerse reward 1. Learning rate 4e-6, temperature 1.0.
   - **SWE RL.**

**Sonuç:** Yazarların raporuna göre:
- 14B-Thinking final: LiveCodeBench (yeni yarışma kodu) v5 77.5, v6 74.6; AIME25 (lise matematik olimpiyatı) 83.3; SWE-bench Verified (Agentless, agent döngüsüz) 43.1. SFT başlangıcı: LCB v5 66.1, AIME25 81.1. RL kod tarafında 11.4 puan, matematikte 2.2 puan ekledi.
- En büyük kod kazancı, beklenmedik biçimde RLHF aşamasından geldi: 8B'de LCB v5 +10.7.
- Math RL tek başına LCB'yi yaklaşık +2.2, ardından Code RL yaklaşık +3 artırdı.
- IF-RL, IFEval'i (talimata uyma) çok artırdı: 8B'de 45.5 → 83.3. Ama ArenaHard'ı (sohbet kalitesi) biraz düşürdü.
- Sonraki alanın RL'si önceki alanları nadiren bozdu.
- Kodda dil karıştırmaya −1 vermek doğruluğu düşürdü; bu yüzden kodda 0 verildi.
- Düşük temperature [entropiyi](00_terimler.md#entropy-ve-entropy-collapse) (modelin seçimlerindeki çeşitlilik) sabitledi ama kod doğruluğunu düşürdü.

**Bizim için:** RL'yi tek karışımda değil kısa, sıralı aşamalarda yapmak (önce biçim ve talimat, sonra SQL doğruluğu) ve her epoch'ta %0 ya da %100 doğrulu soruları havuzdan atıp küçük olasılıkla geri eklemek, sınırlı hesapla uygulanabilir bir reçete.

---

## ToolOrchestra: Elevating Intelligence via Efficient Model and Tool Orchestration (NVIDIA, Kasım 2025) — [2511.21689](https://arxiv.org/abs/2511.21689)
**Tek cümlede:** Qwen3-8B'den, görevi kendi başına değil başka modelleri ve tool'ları çağırarak çözen 8B'lik bir "Orchestrator" (yönetici model) eğittiler; reward doğruluğun yanında maliyeti ve süreyi de hesaba katıyor.

**Problem:** En güçlü modeller (ör. GPT-5) pahalı ve yavaş. Çoğu görevin her adımı en güçlü modeli gerektirmez. Küçük bir model, hangi adımda hangi tool'u ya da hangi büyük modeli çağıracağına karar verebilirse aynı doğruluğa çok daha ucuza ulaşılabilir.

**Ne yaptılar:**
1. **Model:** Qwen3-8B'den başlayan, uçtan uca RL ile eğitilen Orchestrator. Diğer modeller ve tool'lar onun için birer "araç".
2. **Algoritma:** GRPO.
3. **Üç parçalı reward:**
   - Sonucun doğruluğu: GPT-5 yargıç olarak doğru/yanlış diyor (binary).
   - Verimlilik: harcanan para ve geçen süre için ceza.
   - Tool tercihi: kullanıcının bir tercih vektörüyle (ör. "şu tool'u daha çok kullan, şunu az") ağırlıklandırılmış reward.
4. **Veri:**
   - ToolScale: 10 alanda sentetik kullanıcı–agent–tool environment'ları; 197 tool, yaklaşık 4K görev.
   - GeneralThought-430K: genel reasoning soruları.
5. **Ayarlar:** Learning rate 1e-6; girdi 24K, üretim 8K token; batch 16, rollout batch 8; en fazla 50 tur; 16 H100 GPU.
6. **Kararlılık için filtre:** Bütün rollout'ları aynı sonucu veren (homojen), biçimi bozuk ya da geçersiz çıktılı örnekler eğitimden süzülüyor.

**Sonuç:** Yazarların raporuna göre:
- HLE (Humanity's Last Exam: uzman düzeyinde çok zor sorular): 37.1. Yalnız GPT-5 kullanan kurulum: 35.1. Küçük orchestrator biraz daha yüksek.
- FRAMES (birden çok kaynaktan bilgi toplayarak cevaplanan sorular): 76.3.
- τ²-Bench (tool'lu müşteri hizmeti konuşması): 80.2.
- Maliyet: görev başına 9.2 sent; GPT-5 kurulumu 30.2 sent. Yani yaklaşık üçte bir maliyet.
- Süre: 8.2 dakika; GPT-5 kurulumu 19.8 dakika.
- Ablation tablosu yok; reward parçalarının ayrı katkısı ölçülmemiş.

**Bizim için:** Küçük modelin ne zaman büyük modele devredeceğini (handoff) maliyet cezalı bir reward ile RL'de öğrenmek mümkün. Bu, bizim small model → large model akışımıza doğrudan benziyor.

---

## DLER: Doing Length pEnalty Right - Incentivizing More Intelligence per Token via Reinforcement Learning (NVIDIA, Ekim 2025) — [2510.15110](https://arxiv.org/abs/2510.15110)
**Tek cümlede:** Uzunluk cezası eklenince doğruluğun düşmesinin nedeninin cezanın kendisi değil zayıf RL ayarları olduğunu savundular; basit bir "sınırı aşan cevaba 0" cezasını iyi bir RL reçetesiyle birleştirerek doğruluğu koruyup cevapları çok kısalttılar.

**Problem:** Reasoning modelleri gereğinden uzun düşünüyor; bu her token'ı pahalı kılıyor. Length penalty (uzun cevaba ceza) eklenince genellikle doğruluk düşüyor. Yaygın çözüm karmaşık ceza formülleri. Yazarlar ise sorunun optimizasyonda olduğunu düşünüyor.

**Ne yaptılar:**
1. **Modeller ve veri:** DeepSeek-R1-1.5B ve 7B; DeepScaleR veri seti (yaklaşık 40K matematik sorusu).
2. **Ceza:** 4,000 token'ı aşan cevaba 0 reward (truncation cezası). Doğru olsa bile.
3. **Batch düzeyinde reward normalizasyonu.** GRPO'da advantage, aynı prompt'un grubu içinde hesaplanır. Burada ise bütün batch'in ortalaması ve standart sapması kullanılıyor. Neden: ceza, gruplar içinde advantage'ı yanlı (çarpık) hâle getiriyor; batch düzeyi bunu azaltıyor.
4. **Clip-higher 0.28.** [Clip-higher](00_terimler.md#clip-ve-clip-higher): PPO'daki güncelleme sınırının üst kenarını gevşetmek; olasılığı düşük ama iyi token'lar daha hızlı güçlenebilsin diye.
5. **Dynamic sampling:** Bütün reward'ları 0 ya da bütün reward'ları pozitif olan gruplar atılıyor.
6. **Ayarlar:** Prompt başına 16 rollout, batch 512, learning rate 1e-6, KL katsayısı 0.0005.
7. **Difficulty-Aware DLER:** Kolay sorularda daha sıkı sınır (2,000 token). Kolay soruda uzun düşünmeye gerek yok.
8. **Update-selective merging** (bir [model merging](00_terimler.md#model-merging) türü: iki modelin ağırlıklarını birleştirmek). RL'nin değiştirdiği parametrelerden en büyük %25'lik güncelleme alınıyor, 0.7 ile çarpılıp base model'e ekleniyor. Diğer güncellemeler atılıyor.

**Sonuç:** Yazarların raporuna göre:
- DLER-R1-7B: AIME-24 (lise matematik olimpiyatı) 55.62; base 55.40. Doğruluk aynı. Ortalama cevap uzunluğu 7,747 → 2,405 token, yaklaşık %69 kısa.
- 1.5B: AIME-24 29.79 → 34.38; doğruluk 4.6 puan arttı. Cevaplar yaklaşık %77 kısa.
- Llama-3.1-Nemotron-Nano-8B'de merging, AIME-24'ü korurken (66.66'ya karşı 66.40) uzunluğu %46 kısalttı.

**Bizim için:** Yerel modelde her token pahalı. Bir token bütçesinin aşılmasını 0 reward saymak ve kolay sorularda bütçeyi daraltmak hem eğitim hem çalıştırma süresini kısaltır.

---

## QeRL: Beyond Efficiency -- Quantization-enhanced Reinforcement Learning for LLMs (NVIDIA ve MIT, HKU, Ekim 2025) — [2510.11696](https://arxiv.org/abs/2510.11696)
**Tek cümlede:** Base modelin ağırlıklarını 4 bit'e sıkıştırıp üzerine LoRA ile RL yaptılar; sıkıştırmanın getirdiği gürültünün yalnız bellek kazandırmadığını, modelin keşfini de artırdığını gösterdiler.

**Problem:** RL bellek ve zaman açısından çok pahalı: model hem rollout üretiyor hem eğitiliyor. Quantization (ağırlıkları daha az bit'le saklamak) belleği azaltır, ama genelde doğruluğu düşürdüğü düşünülür. Yazarlar quantization gürültüsünün RL'de faydalı olabileceğini öne sürüyor.

**Ne yaptılar:**
1. **NVFP4 + LoRA.** Base ağırlıklar NVFP4'e (NVIDIA'nın 4 bit'lik kayan nokta biçimi) sıkıştırıldı ve donduruldu. Üzerine [LoRA](00_terimler.md#lora) eğitildi (LoRA: modelin yanına eklenen küçük, eğitilebilir matrisler; ana ağırlıklar değişmez).
2. **Hızlı çekirdek.** Rollout üretimi ve prefill (prompt'un ilk okunması) için Marlin tabanlı bir GPU kernel'i (4 bit'lik matris çarpımını hızlı yapan kod) kullanıldı.
3. **Gürültü ve keşif.** Quantization'ın küçük hataları, modelin token dağılımını biraz düzleştiriyor; yani entropiyi (seçimlerdeki çeşitliliği) artırıyor. Daha çeşitli rollout'lar daha çok keşif demek.
4. **AQN (Adaptive Quantization Noise).** Her forward geçişte kanal düzeyinde ek gürültü ekleniyor. Gürültünün büyüklüğü eğitim boyunca üstel olarak azalıyor: başta çok keşif, sonra kararlılık. Gürültü RMSNorm ağırlıklarına (katman normalizasyonu parametreleri) katılıyor; ek parametre gerekmiyor.
5. **Veri ve algoritma:** Matematik (GSM8K, BigMath) üzerinde GRPO ve DAPO (GRPO'nun clip-higher ve dynamic sampling eklenmiş bir çeşidi).

**Sonuç:** Yazarların raporuna göre:
- Qwen2.5-7B-Instruct: GSM8K (ilkokul düzeyi kelime problemleri) 90.8, MATH 500 (lise yarışma matematiği) 77.4. Tam parametre fine-tuning'e yakın; 16-bit LoRA'nın ve QLoRA'nın (4 bit base + LoRA'nın klasik hâli) üstünde.
- Hız: rollout'ta 1.5 kattan fazla; QLoRA'ya göre uçtan uca yaklaşık 1.8 kat.
- Tek bir H100 GPU'da 32B modelle RL yapılabiliyor.
- 16-bit LoRA'nın çöktüğü learning rate'lerde kararlı kalıyor.
- Sınır: yalnız 3B–32B modellerde ve yalnız matematikte denendi.

**Bizim için:** Mac'te (MLX) quantize base + LoRA ile RL yapmak yalnız bellek kazancı değil, keşfi de artırabilir. NVFP4 kernel'i MLX'te olmadığı için bu bulgu doğrudan değil, ilke olarak taşınır.

---

## BroRL: Scaling Reinforcement Learning via Broadened Exploration (NVIDIA, Ekim 2025) — [2510.01180](https://arxiv.org/abs/2510.01180)
**Tek cümlede:** Uzun RL'nin bir noktada doyduğu 1.5B modelde, eğitimi daha da uzatmak yerine her prompt için rollout sayısını yüzlere çıkararak RL'yi yeniden ilerlettiler.

**Problem:** ProRL (bu dosyada ayrı girdi) 1.5B bir modeli 3K adım RL ile eğitti, ama bir noktadan sonra gelişme durdu. RL'yi büyütmenin iki yolu var: daha çok adım ya da adım başına daha çok deneme. Yazarlar ikincisini inceliyor.

**Ne yaptılar:**
1. **Başlangıç:** ProRLv2 checkpoint'i (Nemotron-Research-Reasoning-Qwen-1.5B). Bağlam 8K'dan 16K'ya.
2. **Rollout'u genişletme.** ProRL: adım başına 512 prompt × 16 rollout. BroRL: 128 prompt × 512 rollout. Yani daha az soru, her soruya çok daha fazla deneme.
3. **Learning rate:** Batch'in büyüme oranının kareköküyle ölçeklendi.
4. **Beş görev ailesi:** matematik, kod, fen, IFEval (talimata uyma), Reasoning Gym (mantık bulmacaları).
5. **RL ayarları:** PPO-clip; REINFORCE++ tarzı advantage normalizasyonu (advantage'ı batch düzeyinde normalize etmek); dynamic sampling; referans resetleri (ProRL girdisinde açıklanıyor); Clip-Higher.
6. **Teori (kelimelerle):** Bir RL adımında doğru token'ların toplam olasılığının nasıl değiştiğine bakıyorlar. Bu değişimin bir kısmı örneklenen rollout'lardan, bir kısmı örneklenmemiş olanlardan geliyor. Örneklenmemiş kısım negatif olabilir, yani doğru cevapların olasılığını düşürebilir. Rollout sayısı N büyüdükçe bu kısım küçülüyor. Basitçe: çok örnekle model neyi güçlendirdiğini daha doğru görüyor.

**Sonuç:** Yazarların raporuna göre (ProRL'nin doyduğu noktadan devam, +191 adım):
- Matematik 61.69 → 63.03, kod 52.00 → 54.20, Reasoning Gym 61.29 → 63.09.
- Aynı noktadan ProRL ile eğitime devam edilince skorlar düşmeye başladı.
- Dynamic sampling'in filtresinden geçen (sinyal veren) örneklerin oranı %62; ProRL'de %41. Yani çok rollout'la daha az örnek boşa gidiyor.
- Üretim throughput'u saniyede 72.4 örnek; ProRL'de 36.5. Çok rollout aynı prompt'tan paralel üretildiği için GPU daha verimli kullanılıyor.
- Sınırlar: kazançlar mutlak olarak küçük (1–2 puan). 16 ile 512 arasındaki N değerleri denenmedi.

**Bizim için:** Az soruyla RL'de adımı uzatmak doyuyorsa, soru başına daha çok rollout daha iyi sinyal verir. Ama Mac'te 512 rollout gerçekçi değil; ilke "zor soruda daha çok örnek" olarak alınmalı.

---

## RLP: Reinforcement as a Pretraining Objective (NVIDIA, Eylül 2025) — [2510.01265](https://arxiv.org/abs/2510.01265)
**Tek cümlede:** RL'yi pretraining'e taşıdılar: model sıradaki token'ı tahmin etmeden önce kısa bir "düşünce" yazıyor ve bu düşünce gerçek sıradaki token'ı ne kadar tahmin edilebilir kılıyorsa o kadar reward alıyor.

**Problem:** Normalde model düşünmeyi (reasoning) ancak post-training'de, RL ile öğreniyor. Pretraining ise yalnız sıradaki token'ı tahmin ediyor. Yazarlar düşünme alışkanlığının daha erken, pretraining sırasında ve doğrulayıcı (verifier) gerektirmeden kazandırılıp kazandırılamayacağını soruyor.

**Ne yaptılar:**
1. **Reward: information gain (bilgi kazancı).** Model metnin bir noktasında önce bir düşünce üretiyor, sonra sıradaki token'ı tahmin ediyor. Reward = düşünceyle birlikte gerçek sıradaki token'a verilen log-olasılık eksi düşüncesiz bir referans modelin verdiği log-olasılık. Örnek: metin "Fransa'nın başkenti" diye bitiyor, sıradaki gerçek token "Paris". Model "soru bir başkent, Fransa'nınki Paris" diye düşünürse "Paris" token'ı daha olası olur; reward pozitif.
2. **Referans: EMA modeli.** EMA (exponential moving average): eğitilen modelin ağırlıklarını yavaşça takip eden bir kopya. Decay 0.999, yani her adımda kopya yeni ağırlıklara yalnız binde bir yaklaşıyor.
3. **Verifier yok, sinyal yoğun.** Reward doğrudan gerçek metin üzerinde hesaplanıyor; doğru cevabı olan sorular gerekmiyor.
4. **Optimizasyon:** Grup göreli advantage (her bağlam için 16 düşünce, G = 16; GRPO'daki gibi kıyaslama). Clipped surrogate (PPO tarzı sınırlı güncelleme) yalnız düşünce token'larına uygulanıyor. Düz metin verisinde belge başına bir token konumu kullanılıyor.
5. **KL:** KL katsayısı β = 0 en iyi sonucu verdi.

**Sonuç:** Yazarların raporuna göre:
- Qwen3-1.7B-Base, benchmark ortalaması: 30.32 → 36.03 (yaklaşık %19 göreli artış). Aynı veriyle continued pretraining (CPT: normal sıradaki token tahminiyle eğitime devam) 30.85; yani kazancı veri değil yöntem getiriyor.
- Kazanç post-training'den sonra da kalıyor: aynı SFT+RLVR'dan sonra RLP'li model 42.51, base 39.34, CPT 39.90.
- Nemotron-Nano-12B-v2'de 250M token RLP ile 42.81 → 61.32.
- 170M token RLP, 6B token CPT'yi %5.3 geçiyor; yaklaşık 35 kat daha az veriyle.
- Düşünce uzunluğu yaklaşık 2,048 token'da doyuyor; daha uzun düşünce fayda getirmiyor.

**Bizim için:** Pretraining yapmayacağız. Ama kazancın SFT+RLVR'dan sonra da korunması, düşünme alışkanlığını erken kazandırmanın sonraki RL'yi güçlendirdiğini gösteriyor.

---

## Front-Loading Reasoning: The Synergy between Pretraining and Post-Training Data (NVIDIA, Eylül 2025) — [2510.03264](https://arxiv.org/abs/2510.03264)
**Tek cümlede:** Reasoning verisinin pretraining'de mi yoksa SFT'de mi verilmesi gerektiğini, 8B modelleri sıfırdan eğiterek ölçtüler; pretraining'de verilen reasoning verisinin kazancı post-training'den sonra da sürüyor.

**Problem:** Reasoning verisi (adım adım çözümler, uzun [CoT](00_terimler.md#cot-ve-long-cot); CoT: chain-of-thought, cevaptan önce yazılan düşünce zinciri) genelde yalnız SFT'de kullanılıyor. Aynı veriyi pretraining'e koymanın faydası belirsiz. Bunu ölçmek pahalı, çünkü modelleri sıfırdan eğitmek gerekiyor.

**Ne yaptılar:**
1. **Sıfırdan pretraining:** 8B hibrit modeller, 1T token.
2. **Pretraining karışımının %20'si reasoning verisi.** Üç çeşit:
   - Büyük ve çeşitli reasoning verisi.
   - Küçük ama yüksek kaliteli uzun CoT.
   - İkisi birlikte.
   - Karşılaştırma: reasoning verisi almayan baseline model.
3. **Post-training:** Bütün modellere SFT ve ardından GRPO tabanlı RLVR.

**Sonuç:** Yazarların raporuna göre:
- Pretraining'de reasoning verisi alan modeller SFT ve RL'den sonra da önde; uzman düzeyi benchmark'larda yaklaşık %19.
- "Asimetri": pretraining'de çeşitlilik ve ölçek, SFT'de kalite önemli.
- Baseline'ın SFT verisini ikiye katlamak yaklaşık %7 kazandırdı, ama aradaki farkı kapatamadı. Yani SFT'de daha çok veri, pretraining'deki eksikliği telafi etmiyor.
- Karışık kaliteli SFT verisini ikiye katlamak matematikte yaklaşık %5 düşürdü. Daha çok ama kötü veri zararlı.
- Pretraining'deki kaliteli veri hemen fayda göstermedi, ama SFT'den sonra yaklaşık %4 ek kazanç verdi. Etki gizli kalıp sonra ortaya çıkıyor.

**Bizim için:** SFT'de veri miktarını değil kalitesini artırmalıyız. Doğru ve temiz trajectory'lerden az sayıda örnek, karışık kaliteli çok sayıda örnekten iyidir.

---

## RLBFF: Binary Flexible Feedback to bridge between Human Feedback & Verifiable Rewards (NVIDIA, Eylül 2025) — [2509.21319](https://arxiv.org/abs/2509.21319)
**Tek cümlede:** İnsanların yazdığı geri bildirim metinlerinden "bilgi doğru mu", "kod okunur mu" gibi ikili ilkeler çıkarıp, reward model'i her ilkenin sağlanıp sağlanmadığına evet/hayır diyen bir model olarak eğittiler (ICLR 2026).

**Problem:** İki yaygın reward türünün ikisinin de zayıflığı var. İnsan tercihinden öğrenilen reward model'ler belirsiz: neden bir cevabı diğerine tercih ettiğini söylemez ve kolayca kandırılabilir. Doğrulanabilir reward'lar (RLVR) kesin, ama yalnız matematik ve kod gibi kontrol edilebilir görevlerde var. RLBFF bu ikisinin arasında bir yol arıyor.

**Ne yaptılar:**
1. **İlke çıkarma.** Doğal dildeki insan geri bildiriminden ilkeler çıkarılıyor. Örnek: "Cevap güzel ama tarih yanlış" → ilke "bilgi doğru mu", etiket "hayır".
2. **İlke bazında ikili etiket.** Her cevap için her ilkeye evet/hayır.
3. **Reward model'i entailment görevi olarak eğitme.** Entailment: "bu cevap şu ilkeyi sağlıyor mu?" sorusuna evet/hayır demek.
4. **Esneklik.** Kullanıcı çalışma anında hangi ilkeye odaklanılacağını seçebiliyor. Klasik Bradley-Terry reward model'inde bu mümkün değil. Bradley-Terry: her cevaba tek bir sayı veren ve iki cevaptan hangisinin daha iyi olduğunu bu sayıların farkından tahmin eden klasik reward model.
5. **Uygulama.** Qwen3-32B'yi RLBFF ile hizalamak için açık reçete ve veri yayımladılar.

**Sonuç:** Yazarların raporuna göre:
- Aynı veriyle Bradley-Terry'yi geçiyor. RM-Bench (reward model'in ince farkları ayırt edebilmesi) 86.2; JudgeBench (yargıç modelin zor sorularda doğru cevabı seçmesi) 81.4. 24 Eylül 2025'te liderlik tablosunda 1.
- Hizalanan Qwen3-32B, MT-Bench, WildBench ve Arena Hard v2'de (sohbet kalitesi; yargıç modelle puanlanıyor) o3-mini ve DeepSeek R1'e eşit ya da üstün. Çıkarım maliyeti onların %5'inden az.

**Bizim için:** Final check'teki büyük model kontrolü zaten ikili bir yargı (`correct`). Bunu açık ilkelere (doğru tablo, doğru filtre, doğru sütunlar) bölmek reward'ı daha açıklanabilir ve daha az gürültülü yapar.

---

## NVIDIA Nemotron Nano 2: An Accurate and Efficient Hybrid Mamba-Transformer Reasoning Model (NVIDIA, Ağustos 2025) — [2508.14444](https://arxiv.org/abs/2508.14444)
**Tek cümlede:** 12B'lik hibrit modeli SFT, talimat RL'si, tool calling için DPO, RLHF ve model merging ile post-train ettiler, sonra Minitron ile 9B'ye budayıp distillation ile onardılar.

**Problem:** Hem doğru hem hızlı bir reasoning modeli istiyorlar. Reasoning modelleri uzun çıktı ürettiği için hız önemli; Mamba-Transformer hibrit mimari bunu sağlıyor. Ayrıca farklı beceriler (tool calling, sohbet, reasoning) farklı eğitim yöntemleri istiyor.

**Ne yaptılar:**
1. **SFT, yaklaşık 80B token.** Örnek sayıları: çok dilli 5.0M, fen 2.0M, konuşma 1.5M, matematik 1.5M, kod 1.1M, tool-calling 400K, güvenlik 2K.
   - 1. aşama: bütün veri; prompt'ların yaklaşık %10'unda reasoning'i silinmiş cevap (reasoning açma/kapama için).
   - 2. aşama: tool-calling odaklı; packing kapalı. Packing (kısa örnekleri tek diziye eklemek) tool-call doğruluğunu düşürüyordu.
   - 3. aşama: long-context ve reasoning'i 1–2K token'a kesilmiş örnekler (bütçe kontrolü).
2. **IFEval RL:** LMSYS'ten (gerçek kullanıcı sohbetleri) 16K prompt; reward kural tabanlı bir verifier'dan (ör. "cevap 3 maddeli mi").
3. **DPO:** [DPO](00_terimler.md#dpo-ve-preference-optimization) (Direct Preference Optimization): iyi ve kötü cevap çiftlerinden, ayrı reward model olmadan öğrenme. WorkBench tool-calling görevlerinde iteratif ve on-policy: model cevap üretiyor, iyi ve kötü olanlar çift yapılıyor, model eğitiliyor, tekrar.
4. **RLHF:** HelpSteer3 bağlamlarında, Qwen tabanlı bir reward model ile GRPO.
5. **Model merging:** Reasoning'de güçlü bir RL checkpoint'i ile chat'te güçlü bir checkpoint arasında doğrusal interpolasyon (ağırlıkların ağırlıklı ortalaması). Yaklaşık 0.5 ağırlık iyi bir denge verdi.
6. **Budama ve distillation (Minitron).** 12B model 9B'ye budandı. Onarma: forward KL logit distillation (eğitilen model, büyük modelin bütün token dağılımını taklit ediyor). Distillation karışımında %70 post-training + %30 pretraining verisi en iyisiydi (matematik 58.5; diğer oranlarda 57.5 ve 57.2).

**Sonuç:** Yazarların raporuna göre:
- 12B hizalanmış model, Qwen3-8B'ye karşı: AIME-2025 (lise matematik olimpiyatı) 76.25 / 69.31; LiveCodeBench (yarışma kodu) 70.79 / 59.5; GPQA-D (lisansüstü fen, en zor alt küme) 64.48 / 59.61. Üçünde de belirgin önde.
- ArenaHard'da (sohbet kalitesi) geride: 74 / 78.4.
- 8K girdi / 16K çıktı ayarında 3–6 kat daha yüksek throughput.
- Bütçe: reasoning kısa bir bütçeyle kesilince model normalde cevabı uzatarak "telafi" etmeye çalışıyor. Kesilmiş reasoning örnekleriyle eğitim bu etkiyi kaldırdı.

**Bizim için:** Üç ucuz fikir: tool-calling SFT'sinde packing kullanmamak; ayrı checkpoint'leri (ör. SQL doğruluğu ve biçim disiplini) ağırlıklı ortalamayla birleştirmek; tool-calling için on-policy DPO.

---

## Nemotron Post-Training Dataset sürümleri (NVIDIA, Nisan–Ağustos 2025) — [HF: Llama-Nemotron](https://huggingface.co/datasets/nvidia/Llama-Nemotron-Post-Training-Dataset), [v1](https://huggingface.co/datasets/nvidia/Nemotron-Post-Training-Dataset-v1), [v2](https://huggingface.co/datasets/nvidia/Nemotron-Post-Training-Dataset-v2)
**Tek cümlede:** NVIDIA, modellerinin SFT (ve bir kısmı RL) verisini açık yayımladı; hepsi birden çok büyük modelin cevaplarından oluşan, süzülmüş sentetik veri.

**Problem:** Çoğu laboratuvar post-training verisini paylaşmıyor; bu yüzden reçeteleri tekrar etmek zor. NVIDIA kendi modellerinde kullandığı veriyi açık veriyor. Bu girdi bir makale değil, üç veri setinin kartlarından bir özet.

**Ne yaptılar:**
1. **Llama-Nemotron-Post-Training-Dataset (v1.1, Nisan 2025).** Llama-Nemotron Ultra, Super ve Nano 8B için.
   - SFT ve RL alt kümeleri var.
   - Dağılım tablosuna göre: matematik yaklaşık 22.1M, kod yaklaşık 10.1M, fen yaklaşık 709K, talimata uyma 56K, chat yaklaşık 40K, güvenlik yaklaşık 31K örnek.
   - Cevapları üreten modeller: Qwen-2.5-Math-7B-Instruct (19.8M), Qwen-2.5-Coder-32B (8.9M), DeepSeek-R1 (3.9M) ve diğerleri.
2. **Nemotron-Post-Training-Dataset-v1 (Temmuz 2025).** Llama-3.3-Nemotron-Super-49B-v1.5 için.
   - 25.7M örnek: stem 20.7M, matematik 2.0M, kod 1.9M, chat 747K, tool_calling 310K.
   - Cevaplar DeepSeek-R1-0528'den (24.6M) ve Qwen3-235B-A22B'den (1.06M).
3. **v2 (Ağustos 2025).** Nano-9B-v2 için. İspanyolca, Fransızca, Almanca, İtalyanca ve Japonca'ya yaklaşık 1M'er örnekle genişletme. Reasoning izleri İngilizce kaldı; yalnız soru ve cevap çevrildi.
4. **Ortak filtreler:** Prompt'lar tutarsızlık, kolayca tahmin edilen cevap (ör. çoktan seçmelide rastgele tutturulabilecek) ve sözdizimi hatasına göre süzüldü.
5. **İki mod:** Bazı prompt'lar için hem reasoning açık hem reasoning kapalı cevap var; model aynı soruda iki davranışı da görüyor.

**Sonuç:** Veri seti kartları performans rakamı vermiyor. Bu verilerle eğitilen modellerin sonuçları ilgili raporlarda (Llama-Nemotron, Nemotron Nano 2 girdileri).

**Bizim için:** Aynı prompt için reasoning açık ve kapalı iki cevap tutmak ve kolay tahmin edilen soruları atmak, experience log'dan SFT verisi seçerken uygulanabilecek basit filtreler.

---

## ProRL v2 / Scaling Up RL: Unlocking Diverse Reasoning in LLMs via Prolonged Training (NVIDIA, Temmuz–Ağustos 2025) — [blog](https://developer.nvidia.com/blog/scaling-llm-reinforcement-learning-with-prolonged-training-using-prorl-v2), [2507.12507](https://arxiv.org/abs/2507.12507)
**Tek cümlede:** ProRL'yi 1.5B'lik modelde 3,000'den fazla RL adımına uzattılar ve uzun RL'yi kararlı tutan üç bileşeni öne çıkardılar: KL kontrolü, clip oranı ve referans modelin düzenli sıfırlanması.

**Problem:** RL'yi çok uzun süre çalıştırmak genelde bir noktada bozuluyor: entropi çöküyor (model hep aynı cevabı üretmeye başlıyor) ya da model referanstan çok uzaklaşıp kararsızlaşıyor. Yazarlar binlerce adım boyunca öğrenmeye devam etmenin yolunu arıyor.

**Ne yaptılar:**
1. **Model:** DeepSeek-R1-Distill-Qwen-1.5B'den Nemotron-Research-Reasoning-Qwen-1.5B.
2. **RL algoritması:** PPO-Clip ve REINFORCE++ baseline'ı (advantage önce grup, sonra global batch düzeyinde normalize ediliyor).
3. **Clip-Higher:** Güncelleme sınırının alt kenarı 0.20, üst kenarı 0.28; üst kenar daha geniş, böylece düşük olasılıklı iyi token'lar daha hızlı güçlenebiliyor.
4. **Dynamic sampling:** Sinyal vermeyen (hepsi doğru ya da hepsi yanlış) gruplar atılıyor.
5. **KL penalty:** k2 tahminiyle hesaplanan ve üst sınırı olan bir KL cezası (k2: KL'yi örneklerden yaklaşık hesaplamanın bir yolu).
6. **Referans reset.** KL cezası modeli bir "referans" modele yakın tutar. Burada referans, her 200–500 adımda ya da KL aniden sıçradığında veya validation skoru durduğunda, o anki modelle değiştiriliyor. Optimizer durumu korunuyor. Basit bir benzetme: model ipe bağlı; ip belli aralıklarla modelin bulunduğu yere yeniden bağlanıyor. Böylece model hem kontrol altında kalıyor hem ilerleyebiliyor.
7. **Aralıklı cosine length penalty.** Uzunluk cezası açılıp kapanıyor. Örnek: 100 güncelleme açık, 500 kapalı.
8. **Bağlam:** ProRL v2 3K (3,000 adım) 8K bağlamla eğitildi; v1 2K (2,000 adım) 16K bağlamla eğitilmişti.

**Sonuç:** Yazarların raporuna göre:
- v2 3K, hem base modeli hem v1'i matematik, kod ve reasoning'de geçiyor.
- En büyük kazanç, base modelin hiç çözemediği görevlerde.
- Metinde tek sayı: matematikte ortalama çıktı uzunluğunda %17.54 düşüş. Yani daha kısa cevaplarla daha iyi sonuç.

**Kaynak notu:** Blog sonuçları çoğunlukla grafik olarak veriyor; sayısal karşılaştırma yok. Bileşenlerin listesi tech report'tan.

**Bizim için:** Uzun RL'de entropi çöküşüne karşı referans resetleri ve aralıklı length penalty, bizim gibi küçük bir modelde aynı soru havuzunda uzun süre RL yaparken bozulmayı geciktirebilir.

---

## AceReason-Nemotron 1.1: Advancing Math and Code Reasoning through SFT and RL Synergy (NVIDIA, Haziran 2025) — [2506.13284](https://arxiv.org/abs/2506.13284)
**Tek cümlede:** SFT ile RL'nin birlikte nasıl ölçeklendiğini sistematik olarak incelediler: SFT'de prompt sayısı mı cevap sayısı mı önemli, kaç epoch gerekli, daha güçlü SFT daha iyi RL getirir mi.

**Problem:** Pratikte "SFT'ye ne kadar veri koyalım, RL'yi nereden başlatalım" sorusunun net bir cevabı yok. SFT'de aynı soruya çok sayıda cevap mı, yoksa çok sayıda farklı soru mu daha değerli? RL temperature'ı nasıl seçilmeli? Yazarlar bunları kontrollü deneylerle ölçüyor.

**Ne yaptılar:**
1. **Başlangıç modeli:** Qwen2.5-Math-7B.
2. **SFT verisi:** 383K prompt (247K matematik, 136K kod); cevaplar DeepSeek-R1'den. 36K'dan 2.2M örneğe yedi farklı boyutta veri sürümü; prompt sayısı ve prompt başına cevap sayısı ayrı ayrı değiştirildi.
3. **RL:** On-policy GRPO, prompt başına 8 ya da 16 rollout, 128 prompt; KL yok.
4. **Uzunluk curriculum'u:** Matematikle 8K → 16K → 24K token; sonra yalnız kodla 24K → 32K; sonra yalnız matematikle 32K.
5. **Temperature kuralı.** Temperature'a göre ayarlanmış entropi yaklaşık 0.3 kalacak şekilde seçiliyor. Denemeler: 0.6 fazla sömürücü (model hep aynı cevabı veriyor, keşif az); 1.0 fazla keşif (cevaplar çok dağınık); 0.85 en iyi.
6. **Overlong filtering:** Sınırı aşan cevapları loss'tan çıkarmak 8K bağlamda yardımcı, 32K'da zararlı.

**Sonuç:** Yazarların raporuna göre:
- SFT ölçekleme: hem prompt sayısı hem cevap sayısı yardımcı, ama benzersiz prompt sayısının etkisi daha büyük. Regresyon katsayıları 4.831'e karşı 2.635; yani farklı soru eklemek, aynı soruya cevap eklemekten yaklaşık iki kat etkili. Performans 5–6 epoch'ta doyuyor.
- Daha güçlü SFT genelde daha iyi RL veriyor, ama aradaki fark RL'de daralıyor. AIME24'te iki SFT modeli arasındaki 6.6 puanlık fark, RL'den sonra 1.6'ya iniyor.
- 8K aşaması önce AIME25'i düşürüyor (48.4 → 44.6). Ama bu aşama atlanırsa final skoru daha düşük: 51.8'e karşı 56.7. Kısa bağlamla başlamak geçici bir kayıp, kalıcı bir kazanç.
- Final 7B, SFT'den sonra RL ile: AIME24 62.0 → 72.6; AIME25 48.4 → 64.8; LiveCodeBench v5 48.8 → 57.2.
- RL'nin pass@K kazancı (K denemeden en az birinin doğru olma oranı) AIME25'te K=8'de 8.3 puan, K=128'de yalnız 1.2 puan. Yani RL modele çoğunlukla zaten çözebildiği soruları daha sık doğru çözmeyi öğretiyor; çok denemede bulunabilen yeni çözümleri pek eklemiyor.

**Bizim için:** SFT verisi seçerken aynı soruya çok cevap yerine daha çok farklı soru tercih edilmeli. RL temperature'ını entropiye göre ayarlamak, sabit 0.7 kullanmaktan daha sağlam bir kural.

---

## ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models (NVIDIA, Mayıs 2025) — [2505.24864](https://arxiv.org/abs/2505.24864)
**Tek cümlede:** 1.5B'lik bir modelde 2,000'den fazla adım süren, çok alanlı uzun RL'nin, base modelde hiç bulunmayan reasoning stratejilerini açabildiğini savundular.

**Problem:** Bir tartışma var: RL modele yeni bir şey mi öğretiyor, yoksa yalnız zaten bildiği cevapları daha sık seçmesini mi sağlıyor? Kısa RL koşuları ikinci görüşü destekliyor. Yazarlar RL'yi çok uzatırsak ve çok alanlı yaparsak bunun değişip değişmediğini test ediyor.

**Ne yaptılar:**
1. **Model:** DeepSeek-R1-Distill-Qwen-1.5B.
2. **Veri:** Yaklaşık 136K doğrulanabilir problem.
   - Matematik 40K (reward binary: doğru ya da yanlış).
   - Kod 24K (reward: geçen testlerin oranı, 0 ile 1 arası sürekli).
   - STEM 25K.
   - Reasoning Gym bulmacaları 37K.
   - Talimata uyma 10K.
3. **Algoritma:** GRPO + DAPO bileşenleri.
   - Clip-higher: alt sınır ε_low 0.2, üst sınır ε_high 0.4.
   - Dynamic sampling: doğruluğu 0 ya da 1 olan prompt'lar atılıyor.
   - Referans modele KL penalty.
   - Validation skoru durunca referans model ve optimizer hard reset ediliyor (ikisi de o anki duruma sıfırlanıyor).
4. **Ayarlar:** Prompt başına 16 rollout (bir dönem 32), temperature 1.2, batch 256, mini-batch 64, learning rate 2e-6. Bağlam 8K; son yaklaşık 200 adım 16K.
5. **Maliyet:** Yaklaşık 16K H100 GPU saati, sekiz ardışık koşu.

**Sonuç:** Yazarların raporuna göre (base modele göre pass@1, ilk denemede çözme oranı):
- Matematik +15.7, kod +14.4, GPQA (lisansüstü fen) +25.9, IFEval (talimata uyma) +22.0, bulmacalar +54.8.
- Base modelin zayıf olduğu yerde RL kazancı daha büyük: base'in pass@128'i (128 denemede en az bir doğru) düşük olan görevlerde kazanç daha yüksek, yani negatif bir ilişki var.

**Kaynak notu:** Giriş bölümündeki bazı rakamlar sonuç tablosundakilerden farklı. Resmi bir ablation tablosu yok.

**Bizim için:** Base modelin pass@k'sı düşük olan sorular RL'den en çok kazanan sorular. Ama yaklaşık 16K GPU saati bizim bütçemizin çok üstünde; bu yüzden reçetenin ucuz parçaları (dynamic sampling, clip-higher) alınmalı.

---

## NFT: Bridging Supervised Learning and Reinforcement Learning in Math Reasoning (NVIDIA ve Tsinghua, Mayıs 2025) — [2505.18116](https://arxiv.org/abs/2505.18116)
**Tek cümlede:** Modelin yalnız doğru cevaplarından değil, yanlış cevaplarından da öğrenen bir supervised (denetimli) yöntem önerdiler (NFT: Negative-aware Fine-Tuning); katı on-policy durumda bunun GRPO'ya eşdeğer olduğunu gösterdiler.

**Problem:** En basit kendini geliştirme yöntemi RFT'dir (rejection sampling fine-tuning: model çok cevap üretir, yalnız doğru olanlarla SFT yapılır). Ucuz ve kararlıdır, ama yanlış cevaplardaki bilgiyi çöpe atar. RL ise yanlış cevapları da kullanır, ama daha karmaşıktır. Yazarlar yanlış cevapları supervised bir kayıpla kullanmanın yolunu arıyor.

**Ne yaptılar:**
1. **Negatif policy fikri (formül kelimelerle).** Bir soruda eski model bazen doğru, bazen yanlış cevap verir. Doğru cevap oranı r_q olsun (ör. 10 denemede 3 doğruysa r_q = 0.3). Eski modelin cevap dağılımı, iki parçanın karışımıdır: doğru cevap üreten bir "pozitif model" (oranı r_q) ve yanlış cevap üreten bir "negatif model" (oranı 1 − r_q). Yani negatif model = eski modelden pozitif modelin payı çıkarılıp kalanın (1 − r_q)'ya bölünmesi.
2. **Yanlış cevaplarla eğitim.** Negatif model bu formülle pozitif modele bağlı olduğu için, yanlış cevaplarda negatif modeli eğitmek doğrudan pozitif modeli (asıl kullanılacak modeli) iyileştiriyor. Ayrı bir negatif model saklamak gerekmiyor. Negatif oran ε ile kırpılıyor (çok uç değerlere gitmesin diye).
3. **Modeller ve veri:** Qwen2.5-Math-7B ve Qwen2.5-32B; DAPO-Math-17k veri seti.
4. **Ayarlar:** Adım başına 512 soru × 16 cevap, learning rate 1e-6, temperature 1.0, yaklaşık 320 rollout adımı.
5. **Teori:** Katı on-policy durumda NFT ile GRPO'nun eşdeğer olduğunu gösteriyorlar; yani bu, supervised ile RL arasında bir köprü.

**Sonuç:** Yazarların raporuna göre:
- 7B, altı matematik benchmark'ının ortalaması: base 31.6; [RFT](00_terimler.md#rejection-sampling) 48.3; GRPO 49.5; DAPO 51.2; NFT 51.7. NFT en yüksek, ama RL yöntemlerine çok yakın.
- 32B: RFT 52.8, DAPO 59.9, NFT 59.2. Burada DAPO biraz önde.
- 32B'de kazancın yaklaşık %80'i pozitif veriden (yani RFT'nin de yaptığı şeyden), yaklaşık %20'si negatif veriden.
- Zor sorulara daha yüksek ağırlık vermek (ağırlık = 1 − r_q; az çözülen soru daha çok sayılıyor) sabit ağırlıktan iyi.
- RFT'de entropi düşüyor (model daralıyor); NFT ve DAPO'da artıyor (keşif sürüyor).

**Bizim için:** Experience log'daki yanlış SQL'ler atılmak zorunda değil. Ama kazancın çoğu doğru trajectory'lerle RFT'den geliyor; bu yüzden ilk adım olarak RFT en ucuz ve en güvenli seçenek.

---

## AceReason-Nemotron: Advancing Math and Code Reasoning through Reinforcement Learning (NVIDIA, Mayıs 2025) — [2505.16400](https://arxiv.org/abs/2505.16400)
**Tek cümlede:** Distill edilmiş 7B ve 14B modellere önce yalnız matematik, sonra yalnız kod RL'si uyguladılar ve büyük ölçekli RL'nin küçük ve orta boy modellerde distillation'ı geçebildiğini gösterdiler.

**Problem:** O dönemde yaygın görüş şuydu: küçük modelde RL, büyük bir modelden distillation kadar iyi sonuç vermez (Llama-Nemotron girdisine bakın). Yazarlar doğru verilerle ve doğru ayarlarla RL'nin bu modellerde de belirgin kazanç getirip getirmediğini test ediyor.

**Ne yaptılar:**
1. **Modeller:** DeepSeek-R1-Distill-Qwen-7B ve 14B.
2. **RL ayarları:** GRPO, token düzeyinde loss. Strictly on-policy: her batch'le tek güncelleme. Batch başına 2 ya da 4 güncelleme denendiğinde yaklaşık 100. adımda entropi çöktü. KL ve entropi bonusu 0. Batch 128. Rollout: 8K aşamasında prompt başına 8, sonra 16.
3. **Reward:** Binary, kural tabanlı (matematikte cevap eşleşmesi, kodda testler).
4. **Matematik verisi, yaklaşık 49K** (DeepScaleR, NuminaMath).
   - 9-gram decontamination.
   - Çok parçalı sorular, çoktan seçmeliler ve ispat soruları atıldı (cevabı kesin kontrol edilemez).
   - DeepSeek-R1'in sürekli çözemediği sorular atıldı (muhtemelen bozuk ya da çok zor).
   - Çözümü 2K token'dan kısa olan sorular atıldı (fazla kolay).
   - Uzunluk curriculum'u: 8K → 16K → 24K → 32K. 24K aşamasında yaklaşık 2.2K zor prompt.
5. **Kod verisi, 8,520 problem.** Zayıf ya da yanlış testli problemler atıldı. DeepSeek-R1'in 8 denemenin hiçbirinde başaramadığı problemler atıldı. Uzunluk 24K → 32K. Her epoch kolay problemler süzülüyor.
6. **Neden ayrı aşamalar:** Kod doğrulaması çok yavaş: 1,024 örnek için kodda yaklaşık 552 saniye, matematikte 3.9 saniye.

**Sonuç:** Yazarların raporuna göre:
- 14B, distill başlangıçtan RL sonrasına: AIME24 69.7 → 78.6; AIME25 50.2 → 67.4; LiveCodeBench v5 53.1 → 61.1; v6 47.9 → 54.9.
- 7B: AIME25 53.6, LCB v5 51.8.
- Yalnız matematik RL'si kodu da artırdı: LCB v5'te 7B +6.8, 14B +5.8. Matematikte kazanılan reasoning koda geçiyor.
- 8K bağlamla başlamak, 16K ya da 24K ile başlamaktan iyi.
- Reward hataları: hatalı pozitif testler (yanlış kodun testi geçmesi) eğitimin ortasında ani bir düşüşe yol açtı; yanlış cevabın ödül alması [reward hacking](00_terimler.md#reward-hacking)'e kapı açıyor. Hatalı negatif testler (doğru kodun testten kalması) modelin alt-optimal bir noktada takılmasına yol açtı.
- Zor alt kümeyle eğitim AIME24'te 65.9; karşılaştırılan kurulum 63.3.

**Bizim için:** Reward'ın doğruluğu kritik: SQL'de sonuç karşılaştırması (result key) hatalı pozitif ya da negatif üretmemeli. Kısa bağlamla başlayıp uzatmak küçük modelde verimli.

---

## HelpSteer3-Preference: Open Human-Annotated Preference Data across Diverse Tasks and Languages (NVIDIA, Mayıs 2025) — [2505.11475](https://arxiv.org/abs/2505.11475)
**Tek cümlede:** STEM, kod ve çok dilli görevleri kapsayan, 40,000'den fazla insan etiketli tercih örneği içeren açık bir veri seti yayımladılar (CC-BY-4.0 lisansı); Nemotron'un reward model'lerinin temel verisi.

**Problem:** RLHF için iyi bir reward model gerekir; reward model de insanların "bu cevap şundan iyi" dediği tercih verisiyle eğitilir. Açık ve kaliteli tercih verisi az, özellikle STEM, kod ve İngilizce dışı dillerde.

**Ne yaptılar:**
1. **Veri:** İnsanların iki cevaptan hangisini tercih ettiğini işaretlediği örnekler (ikili tercih).
2. **Kullanım:** Bu veriyle iki tür reward model eğitiliyor:
   - Bradley-Terry reward model: her cevaba tek bir puan veriyor.
   - GenRM (generative reward model): cevabı metin yazarak değerlendirip sonra puan veriyor.
   - Bu reward model'lerle RLHF yapılarak model hizalanıyor.
3. **Sonraki kullanım:** Sonraki Nemotron 3 raporlarında GenRM'ler bu veriyle (ve lmarena, yani gerçek kullanıcı oylamalarının alt kümeleriyle) Qwen3-235B'den GRPO ile eğitiliyor.

**Sonuç:** Yazarların raporuna göre bu veriyle eğitilen reward model'ler RM-Bench'te (reward model'in ince farkları ayırt etmesi) 82.4, JudgeBench'te (yargıç modelin zor sorularda doğru cevabı seçmesi) 73.7 alıyor. Yazarlara göre bu, önceki en iyi sonuçların yaklaşık 10 puan üstü.

**Bizim için:** Final check'te büyük model zaten bir yargıç. Ayrı bir reward model eğitmek yerine doğrulanabilir sonuç (result key) reward'ı birincil, büyük model yargısı ikincil sinyal olarak kalmalı.

---

## Llama-Nemotron: Efficient Reasoning Models (NVIDIA, Mayıs 2025) — [2505.00949](https://arxiv.org/abs/2505.00949)
**Tek cümlede:** Llama tabanlı üç reasoning modeli (Nano 8B, Super 49B, Ultra 253B) mimari arama, distillation, SFT ve RL ile eğittiler; kullanıcı "detailed thinking on/off" sistem talimatıyla reasoning'i açıp kapatabiliyor.

**Problem:** Reasoning modelleri güçlü ama pahalı: her soruda uzun düşünüyorlar. Kullanıcı basit sorularda düşünmeyi kapatabilmeli. Ayrıca büyük modelleri daha hızlı çalışacak şekilde küçültmek ve hangi boyutta RL'nin işe yaradığını bulmak gerekiyor.

**Ne yaptılar:**
1. **Mimari ve başlangıç.** NAS (neural architecture search: hızlı çalışacak katman yapısını otomatik aramak) ile mimari seçildi. Ardından distillation ve continued pretraining.
2. **SFT verisi, 33.0M örnek.**
   - Reasoning açık yaklaşık 3.2M: matematik 2.23M, kod 0.99M, fen 0.71M. Reasoning izleri DeepSeek-R1'den.
   - Reasoning kapalı yaklaşık 29.8M: cevaplar Llama ve Qwen modellerinden.
   - Her prompt iki moda da eşlendi: aynı soru için hem düşünceli hem düşüncesiz cevap.
   - Matematikte beklenen cevapla eşleşmeyen çözümler atıldı. Decontamination yapıldı.
3. **Nano için üç aşamalı SFT.** (1) Yalnız reasoning verisi, learning rate 1e-4, 4 epoch. (2) Reasoning'siz veri eklendi. (3) Chat, talimata uyma ve tool-calling.
4. **Büyük ölçekli reasoning RL, yalnız Ultra'da.**
   - GRPO; adım başına 72 prompt × 16 cevap; temperature 1; batch 576.
   - Reward: doğruluk (Llama-3.3-70B yargıç olarak) + biçim.
   - LN-Super'in 8 denemede en az %75 çözdüğü prompt'lar atıldı.
   - Batch'ler pass rate üzerinde kolaydan zora kayan Gauss hedefle kuruldu (Nemotron 3 Nano girdisindeki yöntemin ilk hâli).
   - Maliyet: yaklaşık 140K H100 saati.
5. **IF RL (talimata uyma):** RLOO (REINFORCE Leave-One-Out: her cevabın baseline'ı, aynı prompt'un diğer cevaplarının ortalama reward'ı), 120 adımdan az.
6. **Tercih optimizasyonu.** RPO (Reward-aware Preference Optimization), NVIDIA'nın [DPO](00_terimler.md#dpo-ve-preference-optimization) benzeri yöntemi: iyi ve kötü cevap çiftlerinden öğrenirken reward farkının büyüklüğünü de hesaba katıyor.
   - Super: iki tur online RPO (her turda modelin kendi yeni cevaplarıyla). Arena Hard (sohbet kalitesi) 69.1 → 88.1.
   - Nano: iki tur offline RPO (hazır cevap çiftleriyle).
   - Ultra: GRPO.
7. **Model merging** yalnız Super'da.

**Sonuç:** Yazarların raporuna göre:
- Ultra'da RL: GPQA-D (lisansüstü fen, zor alt küme) 66.4 → 76.0; AIME25 (lise matematik olimpiyatı) 60.4 → 72.5.
- Ön deneylerde küçük modellerde RL, distillation'dan daha kötü sonuç verdi. Bu yüzden reasoning RL yalnız Ultra'ya uygulandı.
- Daha güçlü bir SFT checkpoint'i her zaman daha iyi RL getirmedi; RL daha erken bir checkpoint'ten başlatıldı.
- Nano'da RPO sonrası AIME25-I 51.6 → 47.1'e düştü; sohbet için yapılan tercih eğitimi matematiği biraz bozdu.

**Bizim için:** 2025 başındaki NVIDIA bulgusu "küçük modelde önce distillation (SFT), RL değil" idi. Aynı ekibin sonraki işleri (AceReason, ProRL, Cascade) küçük modelde de RL'nin işe yaradığını gösterdi, ama hep iyi bir SFT ya da distillation başlangıcıyla.

---

## Nemotron-Research-Tool-N1: Exploring Tool-Using Language Models with Reinforced Reasoning (NVIDIA, Nisan 2025) — [2505.00024](https://arxiv.org/abs/2505.00024)
**Tek cümlede:** Tool calling'i, modele hazır reasoning izi vermeden, yalnız biçimin ve çağrının doğruluğunu ödüllendiren kural tabanlı bir binary reward ile GRPO kullanarak eğittiler (ortak yazarlar Penn State ve UW).

**Problem:** Tool calling genelde büyük modellerden distill edilmiş trajectory'lerle SFT ile öğretilir. Bu, modelin örnekleri taklit etmesini sağlar ama kendi akıl yürütmesini geliştirmez. Yazarlar yalnız sonucu kontrol eden basit bir reward'ın, SFT verisi olmadan da tool calling'i öğretip öğretemeyeceğini soruyor.

**Ne yaptılar:**
1. **Modeller:** Qwen2.5-7B-Instruct ve 14B-Instruct.
2. **Veri:** ToolACE ve xLAM'ın (function-calling veri setleri) alt kümeleri.
   - xLAM: 60K tek turlu örnek.
   - ToolACE: 8,183 tek turlu örnek ve çok turlu konuşmalardan 1,470 tek adımlık örnek.
   - Çok turlu trajectory'ler tek adımlık tahminlere bölündü: önceki adımlar bağlam olarak veriliyor, model yalnız sıradaki çağrıyı tahmin ediyor. Örnek: 3 adımlı bir konuşma, 3 ayrı eğitim örneği olur.
3. **Filtre:** Aday tool listesinde olmayan bir tool'u çağıran, JSON'u bozuk ya da biçimi tutarsız örnekler atıldı.
4. **Reward (binary).** 1 almak için hepsi gerekli: `<think>` ve `<tool_call>` etiketleri var; tool adı doğru; bütün argüman anahtar–değer çiftleri eşleşiyor (argüman sırası önemsiz). Aksi hâlde 0.
5. **Ayarlar:** Batch 1024, learning rate 1e-6, temperature 0.7, prompt başına 5 rollout, KL 1e-3, 7 epoch.

**Sonuç:** Yazarların raporuna göre:
- BFCL (Berkeley Function Calling Leaderboard: fonksiyon çağırma doğruluğu) genel skor: 14B 85.97, 7B 84.82. GPT-4o 83.97. Yani 7B bile GPT-4o'nun biraz üstünde.
- Aynı 5,518 distill trajectory'siyle karşılaştırma: reasoning'siz SFT 81.47; reasoning'li SFT 82.71; SFT → RL 83.17; saf RL 83.24. Önce SFT sonra RL, doğrudan RL'yi güvenilir biçimde geçmedi.
- Binary reward kısmi puanlı reward'lardan iyi: 84.82'ye karşı 83.74 ve 82.58. Kısmi puan (ör. tool adı doğruysa yarım puan) modeli yarım doğru çağrılara razı ediyor.
- Reasoning biçim şartını (`<think>` etiketi zorunluluğu) kaldırmak BFCL Live alt kümesini 80.38'den 76.24'e düşürdü.

**Bizim için:** Kısmi puan yerine sıkı binary reward ve çok turlu konuşmayı tek adımlık örneklere bölmek, bizim üç tool'lu (`search_values`, `execute_sql`, `submit`) akışta küçük modelle RL'yi çok ucuzlatır.

---

## AceMath-RL-Nemotron-7B: Training Math Reasoning Model with Reinforcement Learning (NVIDIA, Nisan 2025) — [blog](https://research.nvidia.com/labs/adlr/acemath_rl)
**Tek cümlede:** Distill edilmiş 7B bir modeli yalnız RL ile, yalnız matematik verisinde eğittiler; AceReason-Nemotron'un öncüsü.

**Problem:** Distill edilmiş bir reasoning modelinin üzerine RL'nin ne kadar ekleyebileceği ve RL'nin kararlı nasıl tutulacağı belirsiz. Ayrıca model geliştikçe soruların çoğu kolaylaşıyor ve sinyal vermiyor.

**Ne yaptılar:**
1. **Model:** DeepSeek-R1-Distill-Qwen-7B.
2. **Algoritma:** On-policy GRPO. Off-policy koşular (aynı rollout'larla birden çok güncelleme) yaklaşık 150 adımda entropi çöküşü ve KL patlaması yaptı; bu yüzden on-policy seçildi.
3. **Veri:** Yaklaşık 46K matematik prompt'u. 3. aşamada pass rate'e göre yaklaşık 2.2K zor probleme indirildi.
4. **Uzunluk aşamaları** (parantez içinde adım sayısı): 8K (2,500) → 16K (430) → 24K (350) → 32K (330). Prompt başına rollout 8'den 16'ya.
5. **Diğer ayarlar:** 1. aşamada temperature 0.6, batch 128, KL 0.001. 4. aşamada KL 0, temperature 0.8'den 1.0'a.

**Sonuç:** Yazarların raporuna göre:
- AIME24 (lise matematik olimpiyatı) 55.5 → 69.0; AIME25 39.2 → 53.6.
- LiveCodeBench (yarışma kodu) 37.6 → 44.4. Yalnız matematik RL'si koda da geçti.
- Eğitim doğruluğu %90'ı geçince soruların yaklaşık %70'i GRPO sinyali vermiyordu (hepsi doğru çözülüyordu). En zor alt kümeyle eğitmek en iyi sonucu verdi.

**Bizim için:** Model kolay soruları çözmeye başlayınca havuzu zor sorulara daraltmak gerekir. Aksi hâlde batch'in çoğu sıfır advantage'la boşa gider.

---

## AIMO-2 Winning Solution: Building State-of-the-Art Mathematical Reasoning Models with OpenMathReasoning dataset (NVIDIA, Nisan 2025) — [2504.16891](https://arxiv.org/abs/2504.16891)
**Tek cümlede:** AIMO-2 (Kaggle'daki yapay zekâ matematik olimpiyatı yarışması) birincisi çözüm: büyük bir matematik veri seti, kod çalıştırarak çözen modeller ve birden çok çözüm arasından en iyisini seçen bir yöntem.

**Problem:** Yarışma matematiği için hem çok sayıda kaliteli problem hem de iki tür çözüm gerekiyor: düz metin reasoning ve hesaplamayı Python koduna yaptıran tool'lu reasoning. Ayrıca yarışmada bir soruya birden çok çözüm üretilip doğru olanın seçilmesi gerekiyor.

**Ne yaptılar:**
1. **Problem toplama (540K problem).** AoPS (Art of Problem Solving) forumlarından Qwen2.5-32B-Instruct ile problemler çıkarıldı. Çoktan seçmeli, evet/hayır ve geçersiz problemler atıldı. İspat soruları cevabı olan sorulara çevrildi. Decontamination yapıldı.
2. **CoT çözümleri (3.2M).** DeepSeek-R1 ve QwQ-32B ile problem başına 32'ye kadar aday üretildi; yalnız beklenen cevaba ulaşanlar tutuldu.
3. **TIR çözümleri (1.7M).** TIR (tool-integrated reasoning): model düşünürken Python kodu yazar, kod çalıştırılır, sonuç düşünceye geri eklenir.
   - Önce LIMO-Qwen-32B ile yaklaşık 15K örnek üretildi. Yalnız yeni ve anlamlı kod bloğu içeren, en fazla iki kod bloklu çözümler tutuldu.
   - Sonra bu veriyle ara modeller eğitildi, onlarla tekrar çözüm üretilip süzüldü. Bu döngü [expert iteration](00_terimler.md#expert-iteration)'a benziyor (model üretir, iyiler seçilir, model onlarla eğitilir, tekrar).
   - Prompt'ta kod çağrı bütçesi verildi (1 ile 8 arası); bütçeyi aşan çözümler atıldı.
4. **SFT.** Qwen2.5 1.5B'den 32B'ye; 5.5M karışık örnek, 6 epoch. 2.2M zor problemle ikinci bir tur CoT'u artırdı, TIR'ı biraz düşürdü.
5. **GenSelect.** Model birden çok aday çözümü okuyup en iyisini seçiyor (generative selection). Bu bir [test-time scaling](00_terimler.md#test-time-scaling) yöntemi: çalıştırma sırasında daha çok hesap harcayıp doğruluğu artırmak.
6. **Kaggle modeli:** CoT ve TIR checkpoint'lerinin doğrusal birleşimi (0.3 CoT + 0.7 TIR).

**Sonuç:** Yazarların raporuna göre:
- 32B, Comp-Math-24-25'te (2024–25 yarışma matematiği soruları): CoT 76.5; TIR 78.4; TIR + GenSelect 93.3. Seçim yöntemi tek başına yaklaşık 15 puan ekliyor.
- 1.5B'de TIR, CoT'tan kötü: 52.0'a karşı 61.6. Neden: küçük model TIR çözümlerinin %40.31'ini bitiremiyor; CoT'ta bu oran %12.23.
- Birleştirilmiş model, maj@16'da (16 çözümün çoğunluk oyu) 69.1; yalnız TIR 66.8, yalnız CoT 62.9. Birleşim ikisinden de iyi.
- Kaggle'da 50 sorudan 34'ünü çözerek birinci.

**Bizim için:** Küçük model tool'lu uzun trajectory'leri bitiremeyebilir. Tool çağrı bütçesini prompt'ta vermek ve bütçeyi aşan trajectory'leri SFT verisinden atmak, bizim 10 çağrılık budget'ımızla birebir örtüşüyor.

---

## Nemotron-CrossThink: Scaling Self-Learning beyond Math Reasoning (NVIDIA, Nisan 2025) — [2504.13941](https://arxiv.org/abs/2504.13941)
**Tek cümlede:** RL'yi matematik dışındaki alanlara taşımak için çok alanlı soru–cevap verisini şablonlarla, doğrulanabilirlik filtresiyle ve karışım oranı seçimiyle hazırlayıp doğrudan base modele GRPO uyguladılar.

**Problem:** RLVR genelde matematik ve kodla sınırlı, çünkü orada cevap kesin kontrol edilebiliyor. Genel reasoning soruları (fen, hukuk, ekonomi) çoğu zaman serbest metin cevaplı ve kontrolü zor. Yazarlar bu soruları kontrol edilebilir biçime sokup RL'de kullanmanın yolunu arıyor.

**Ne yaptılar:**
1. **Modeller:** Qwen2.5-7B ve 32B base (SFT yapılmamış).
2. **Veri, yaklaşık 588.6K örnek.**
   - Genel reasoning: MMLU train 99.8K, sentetik CrossThink-QA 192.9K, Natural Reasoning 100K.
   - Matematik: NuminaMath 87.4K, sentetik 100K, MATH 8.5K.
3. **Filtre (doğrulanabilirlik):** Doğru cevabı şıklarda olmayan çoktan seçmeli sorular; şıklarından bazıları eksik kalanlar; cevabı 10 kelimeden uzun açık uçlu sorular; cevapsız matematik soruları atıldı. Kalan her sorunun cevabı kısa ve kontrol edilebilir.
4. **Reward:** 1, yalnız cevap doğru ve biçim (`<think>` etiketi, cevap `\boxed{}` içinde) birlikte sağlanıyorsa.
5. **GRPO ayarları:** 128 prompt × 8 rollout, learning rate 1e-6, KL 0.001, bağlam 5,000 token, 650 adım. Koşu başına yaklaşık 48 GPU saati.
6. **Blend (karışım) denemeleri:** Genel reasoning ile matematiğin farklı oranları karşılaştırıldı.

**Sonuç:** Yazarların raporuna göre:
- En iyi karışım genel reasoning ağırlıklı (2:1) blend: ortalama 58.12. Yalnız matematik 57.82, yalnız genel reasoning 53.30, base 44.75.
- Base'e göre: MATH-500 (lise yarışma matematiği) +30.1; MMLU-Pro (çok alanlı zor bilgi soruları) +12.8; GPQA-D (lisansüstü fen) +11.3.
- Doğru cevaplarda yalnız matematikle eğitilen modele göre yaklaşık %28 daha az token.
- Ablation: soruları yalnız açık uçlu biçime çevirmek +1.21; kısa cevap etiketi +1.20.
- Zorluk filtresi: 32B'yi eğitirken yalnız 7B'nin zero-shot (örneksiz, ilk denemede) çözemediği soruları tutmak 65.84 → 67.99.

**Bizim için:** "Daha küçük bir modelin çözemediği soruları tut" türünden ucuz bir zorluk filtresi ve kısa, kesin doğrulanabilir cevaplar (bizde sonuç tablosu) RL verisini daha verimli yapar.

---

## OpenCodeReasoning: Advancing Data Distillation for Competitive Coding (NVIDIA, Nisan 2025) — [2504.01943](https://arxiv.org/abs/2504.01943)
**Tek cümlede:** Yarışma kodlaması için SFT ile distillation yapmaya yarayan büyük bir veri seti (OCR) kurdular ve veri ölçeğinin ve filtrelemenin etkisini ölçtüler.

**Problem:** Küçük modellere yarışma kodu öğretmenin en ucuz yolu, büyük bir reasoning modelinin çözümlerinden SFT. Ama hangi çözümler tutulmalı: yalnız testleri geçenler mi, hepsi mi? Ve veri büyüdükçe kazanç sürüyor mu?

**Ne yaptılar:**
1. **Veri üretimi:** 28,904 benzersiz soru için DeepSeek-R1'den 736,712 Python çözümü (temperature 0.6, 16K token sınırı).
2. **Filtre:** Yalnız iyi biçimli reasoning'i olan ve kodu Tree Sitter ile (kodu sözdizimine göre ayrıştıran bir araç) ayrıştırılabilen çözümler tutuldu. Testlere göre doğruluk filtresi uygulanmadı (aşağıda neden).
3. **SFT:** Qwen2.5 7B, 14B ve 32B; 3 epoch, learning rate 5e-5, batch 256, 32K bağlam.

**Sonuç:** Yazarların raporuna göre:
- LiveCodeBench (yeni yarışma kodu soruları): 7B 51.3, 14B 59.4, 32B 61.8. Çözümleri üreten DeepSeek-R1: 65.6. 32B, büyük modele 3.8 puan yaklaşıyor.
- Veri 25K'dan 736K örneğe çıkarken performans artmaya devam etti; en çok yeni ve zor sorular eklendikçe.
- Test çalıştırmaya göre filtreleme zarar verdi (14B): filtresiz 54.1; yalnız testi geçen çözümler 47.0; yalnız testi geçmeyenler 52.3. Şaşırtıcı biçimde yanlış çözümler bile doğrulara indirgemekten iyi.
- Yazarlar bu yüzden çözüm doğruluğu yerine soru çeşitliliğini öne aldı.

**Bizim için:** Uzun reasoning SFT'sinde yalnız doğru cevaplara indirmek her zaman iyi değil. Ama bu bulgu büyük modelin uzun reasoning izleri içindir; bizim kısa tool trajectory'lerimizde yanlış SQL'i öğretmek riskli olduğundan önce küçük bir karşılaştırmayla doğrulanmalı.

---

## AceMath: Advancing Frontier Math Reasoning with Post-Training and Reward Modeling (NVIDIA, Aralık 2024) — [2412.15084](https://arxiv.org/abs/2412.15084)
**Tek cümlede:** Matematik için önce genel, sonra matematiğe özel iki aşamalı bir SFT ve çözümleri puanlayan ayrı bir matematik reward model'i (AceMath-RM) geliştirdiler.

**Problem:** Matematik modelleri genelde doğrudan matematik verisiyle eğitiliyor. Yazarlar genel bir SFT'nin önce gelip gelmemesi gerektiğini ve verinin hacmi mi kalitesi mi daha önemli olduğunu soruyor. Ayrıca birden çok çözüm arasından doğrusunu seçmek için iyi bir reward model gerekiyor.

**Ne yaptılar:**
1. **Genel SFT:** Yaklaşık 3M örnek, iki aşamada; cevaplar GPT-4o-mini'den.
2. **Matematik SFT verisi:**
   - 1.3M açık prompt + yaklaşık 1M sentetik prompt.
   - Çapraz kontrol: Qwen2.5-Math-72B-Instruct bir cevap, GPT-4o-mini iki cevap üretti; yalnız cevapları uyuşan örnekler tutuldu (yaklaşık 800K çapraz kontrollü örnek).
   - Çok uzun prompt ya da cevaplar ve kendini tekrar eden çıktılar atıldı.
   - Decontamination: 13-gram (13 kelimelik ortak dizi) ve LCS (longest common subsequence: en uzun ortak alt dizi) ile.
   - Son karışım yaklaşık 1.6M örnek (1.29B token).
3. **Reward model (AceMath-RM):** Yaklaşık 356K problem; her problem için 14 farklı modelden 6 cevap. Model, doğru ve yanlış çözümleri ayırt etmeyi öğreniyor.

**Sonuç:** Yazarların raporuna göre:
- 7 matematik benchmark'ının ortalaması: 1.5B 59.99, 7B 67.17, 72B 71.84. Karşılaştırma, aynı boydaki Qwen2.5-Math-Instruct: 56.97 / 63.29 / 68.16. Her boyutta 3–4 puan önde.
- Ablation'lar:
  - Genel SFT'yi atlamak yaklaşık 1 puan düşürdü.
  - Sentetik prompt'ları kaldırmak 7B'de 64.19 → 62.53.
  - 500K düşük kaliteli sentetik prompt eklemek sonucu 62.95'te bıraktı; seçilmiş sentetik veriyle alınan 64.19'un altında. Filtre hacimden önemli.
  - 2.3M örneğin tamamıyla eğitmek, seçilmiş 1.6M'den biraz kötü.

**Bizim için:** İki farklı modelin aynı cevaba ulaştığı örnekleri tutmak (çapraz kontrol) ve hacim yerine seçilmiş daha az veri, bizim için doğrudan bir kural: small model ile large model'in aynı sonucu bulduğu trajectory'leri SFT'ye almak.
