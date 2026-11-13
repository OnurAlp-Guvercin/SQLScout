# Agentic, tool-use ve Text-to-SQL post-training

**Bu bölümde ne var:** Tool kullanan modellerin post-training'i (ön eğitimden sonra modeli bir göreve göre eğitmek) üzerine 41 çalışma. Önce Text-to-SQL çalışmaları geliyor, çünkü bizim projeye en yakın olanlar onlar; sonra arama, kod ve web agent'ları gibi diğer [agentic ve multi-turn](00_terimler.md#agentic-rl-ve-multi-turn) (modelin birçok turda tool çağırıp sonucuna baktığı) çalışmalar. Her makale için ne yapıldığı, nasıl yapıldığı, sonucun ne anlama geldiği ve bizim projeye etkisi yazıyor.

Rakamlar yazarların bildirdiği gibidir; bulunamayan rakam yazılmadı. Her grupta makaleler yeniden eskiye sıralı.

**Bu bölümün ana dersleri:**
- Agent için [SFT](00_terimler.md#sft) (doğru örnek konuşmaları taklit ettirerek eğitmek) verisi küçük olabilir: büyük modelin ürettiği ve sonucu doğrulanmış 1K–10K trajectory yetiyor (SQL-Trail 1K, WebSailor ~2K, TRUST-SQL ~9K) ve kalite miktardan önemli (SQL-R1).
- SFT formatı ve tool kullanımını öğretiyor, asıl doğruluk ve genelleme kazancı ardından gelen [RL](00_terimler.md#rl-ve-rlvr)'den geliyor (TRUST-SQL: yalnız SFT 46.2, yalnız RL 59.9, SFT sonra RL 64.9) ve RL verisi de birkaç yüz ile birkaç bin soru arası olabiliyor (SkyRL-SQL 653, SQL-Trail ~1K).
- RL'e yalnızca modelin bazen çözdüğü sorular girmeli, çünkü hep ya da hiç çözülen soru öğrenme sinyali vermiyor (TRUST-SQL, SQL-Trail, KARL, Tongyi, rStar2).
- Basit bir [reward](00_terimler.md#reward) (doğru 1, çalışıyor 0.1) çoğunlukla yetiyor, ince kısmi puanlar bazen "tembellik" doğuruyor (Arctic, Databricks); adım düzeyi kredi ancak anlamlı birimlerde ve son cevap doğruysa işe yarıyor (FineStep, CAPER, TRUST-SQL).
- Tool çıktısını (observation) [loss'tan maskelemek](00_terimler.md#loss-masking), yani modelin kendi üretmediği metinden öğrenmesini engellemek, en net ölçülmüş kazançlardan biri (Search-R1: maske kaldırılınca 0.431'den 0.343'e).
- [Distillation](00_terimler.md#distillation) (büyük modelin bilgisini küçük modele aktarmak) için en sağlam yol büyük model trajectory'leriyle SFT ve ardından kısa bir on-policy aşama; küçük modelde düz on-policy distillation hatalı tool call'larda yanıltabiliyor (Two-Phase, SOD).

**Makaleler:**

*Text-to-SQL*
- SERL-SQL — sonucu gördükten sonra geriye bakan bir kopyayla token düzeyinde kredi
- Progress-SQL — ilk SQL'den son SQL'e ilerlemeyi ödüllendiren multi-turn reward
- CAPER — SQL'in her clause'unu puanlayan process reward model
- FineStep — her SQL adımına kurallarla verilen adım puanı
- ReViSQL — BIRD train'i temizleyip RL; veri temizliğinin büyük etkisi
- TRUST-SQL — şemayı tool'larla keşfeden 4B/8B agent, şema adımı için ayrı advantage
- SQL-Trail — ~1K SFT trajectory'si ve ~1K RL sorusuyla multi-turn agent
- MTIR-SQL — 4B, KL'siz ve bozuk rollout filtreli multi-turn GRPO
- Databricks RLVR — basit reward ile offline + online RL, BIRD test'te ilk sıra
- Arctic-Text2SQL-R1 — basit reward, veri filtresi ve güçlü SFT başlangıcı
- SkyRL-SQL — yalnızca 653 örnekle multi-turn RL (yalnızca blog)
- Reward-SQL — SQL'i CTE adımlarıyla yazdırıp her adımı puanlayan PRM
- SQL-R1 — tek turlu GRPO; cold start ve reward parçalarının etkisi
- Reasoning-SQL — SQL'e özgü kısmi reward'larla SFT'siz GRPO
- ExCoT — execution sonucundan kurulan çiftlerle iteratif DPO
- OmniSQL — 2.5M sentetik Text-to-SQL örneği (SynSQL-2.5M) ve SFT modelleri

*Diğer agentic çalışmalar*
- TACA — RL'de tool çağrılarının haksız yere cezalanmasını düzeltme
- ReOPD — ortamı çalıştırmadan, kayıtlı trajectory'lerle on-policy distillation
- Two-Phase Distillation — görev uzmanlarını önce SFT, sonra on-policy distillation ile birleştirme
- PACT — büyük model trajectory'lerini yalnızca loss'ta kullanma
- SOD — küçük agent'ta adım adım ağırlıklı on-policy distillation
- KARL — kurumsal arama agent'ı; distillation ile multi-task RL karşılaştırması
- SkyRL-Agent — uzun agent'lar için RL çerçevesi ve SWE agent'ı
- Tongyi DeepResearch — mid-training + SFT + RL ile açık deep-research agent'ı
- AEPO — ARPO'nun entropiye dayalı dallanmasını dengeleme
- AgentScaler — binlerce simüle tool ortamı ve SFT
- AgentGym-RL — eğitim boyunca tur sayısını büyüten multi-turn RL
- SimpleTIR — eylemsiz turları içeren trajectory'leri süzerek kararlı RL
- rStar2-Agent — 14B Python tool'lu RL; temiz doğru trajectory'leri seçme
- Chain-of-Agents — çok agent'lı sistemi tek modele distill edip RL
- Agent Lightning — var olan agent'ları kod değiştirmeden RL ile eğitme
- ARPO — tool sonrası kararsız noktalarda rollout'u dallandırma
- WebSailor — zor, belirsiz sentetik sorular ve kısa cold start ile web agent'ı
- Self-Challenging — agent'ın kendine görev yazıp çözdüğü RL
- WebDancer — dört aşamalı web agent reçetesi
- ZeroSearch — gerçek arama motoru yerine simüle arama ile RL
- RAGEN — multi-turn RL'in çöküşü ve önleme yolu
- ReTool — kod yorumlayıcılı SFT ve PPO
- ToRL — base modelden SFT'siz tool'lu RL
- SWEET-RL — referans çözümü gören critic ve tur düzeyinde DPO
- Search-R1 — arama tool'unu RL ile öğreten temel reçete

---

## Text-to-SQL

Bu gruptaki çalışmalar doğal dildeki bir soruyu SQL'e çeviren modelleri eğitiyor; birçoğu bizim gibi SQL'i çalıştırıp sonuca bakan multi-turn agent'lar. Çoğu [benchmark](00_terimler.md#benchmarklar) olarak BIRD ve Spider kullanıyor: BIRD dev 1,534 soruluk, gerçek ve kirli veritabanlarından oluşan Text-to-SQL değerlendirme seti; Spider daha temiz veritabanlı, daha kolay ve daha eski bir set; puan çoğunlukla EX (execution accuracy: üretilen sorgunun sonucu doğru SQL'in, yani gold SQL'in sonucuyla aynı mı).

### SERL-SQL: Selective Hindsight Distillation for Text-to-SQL Reinforcement Agentic Learning (Zhejiang University, Zhengzhou University, Ağustos 2026) — [2608.00485](https://arxiv.org/abs/2608.00485)

**Tek cümlede:** Multi-turn Text-to-SQL agent'ında reward'ı bütün token'lara eşit dağıtmak yerine, execution sonucunu gördükten sonra "hangi SQL kararı işe yaradı" diye geriye bakan bir model kopyasıyla token düzeyinde kredi veriyorlar.

**Problem:** [GRPO](00_terimler.md#grpo) (her soru için birkaç cevap üretip her cevabı grubun ortalamasına göre ödüllendiren RL yöntemi) bir trajectory'nin (modelin bir soru için yaptığı bütün adımlar) reward'ını o trajectory'nin bütün token'larına aynı ağırlıkla verir. Agent 5 tur boyunca SQL denediğinde, başarıyı hangi SQL kararının getirdiği bilinmez. Buna credit assignment (kredi dağıtımı) sorunu denir. Örnek: model önce yanlış tabloyu sorgulayıp sonra düzelterek doğru cevaba ulaştıysa, yanlış tablo seçimi de aynı ödülü alır.

**Ne yaptılar:**
1. Taban model Qwen2.5-Coder-Instruct 7B/14B/32B. Eğitim verisi yalnızca BIRD train.
2. Schema grounding: Veritabanındaki value'lar (hücre değerleri) önceden bir embedding index'ine konur (Qwen3-Embedding-0.6B). Sorudaki anahtar kelimelerle value aranır ve yalnızca ilgili tablo ve sütunlardan oluşan küçük bir şema çıkarılır. Örnek: soru "Fremont'taki okullar" diyorsa index 'Fremont' değerinin `schools.City` sütununda olduğunu bulur; modele bütün şema yerine bu kısım gösterilir.
3. [Rollout](00_terimler.md#rollout) (modelin bir soruyu baştan sona denemesi): think-act-observe döngüsü, yani düşün, SQL çalıştır, sonucu gör. Varsayılan en fazla 5 tur; soru başına 8 trajectory.
4. Reward: SQL geçerli ve doğruysa +1, geçerli ama yanlışsa 0, format bozuksa −1.
5. Hindsight modeli: Eğitilen modelin bir kopyası, trajectory'deki token'ları execution feedback'ini (hata mesajı, boş sonuç ya da sonuç tablosu) görerek yeniden puanlar. Yeni trajectory üretmez ve kendisi eğitilmez (gradient almaz). Kısaca "sonucu bilseydim bu token'ı ne kadar olası bulurdum?" sorusunu cevaplar.
6. Token ağırlığı: İki modelin aynı token'a verdiği log-prob farkından bir ağırlık çıkar. Ağırlık 0.8 ile 1.2 arasına kırpılır ve [advantage](00_terimler.md#advantage)'ın (cevabın grup ortalamasından ne kadar iyi olduğu) işaretine göre uygulanır. Yalnızca SQL ve tool-action token'larına uygulanır, düşünce metnine değil.
7. Decay: Bu ağırlığın katsayısı eğitim boyunca azaltılır. Başta hindsight sinyali yol gösterir, sonda yalnızca reward kalır.

**Sonuç:** Yazarların raporuna göre BIRD dev'de 7B 75.55, 14B 74.95, 32B 76.56; Spider test'te ~89–90. Karşılaştırma için bu bölümdeki diğer 7B sonuçları 60–69 arasında. Ablation (bir parçayı çıkarıp ne kadar düştüğüne bakmak), 14B'de 74.95 üzerinden:
- schema grounding olmadan 66.42 (en büyük düşüş, ~8.5 puan)
- hindsight olmadan 71.94 (~3 puan)
- kırpma olmadan 73.14
- seçici action mask'ı olmadan (ağırlık bütün token'lara uygulanınca) 73.43
- decay olmadan 73.61

Yani en büyük katkı value aramasından, ikinci büyük katkı hindsight'tan geliyor.

**Bizim için:** En büyük kazancın value aramasından gelmesi bizim `search_values` tool'unu doğruluyor. Hindsight fikri, büyük modelin final check gerekçesini token ağırlığı olarak kullanmaya ucuz bir yol gösteriyor.

### Progress-SQL: Improving Reinforcement Learning for Text-to-SQL via Progressive Rewards (East China Normal University, Haziran 2026) — [2606.06825](https://arxiv.org/abs/2606.06825)

**Tek cümlede:** Multi-turn RL'de reward'ı yalnızca son SQL'e değil, ilk SQL'den son SQL'e ne kadar ilerlendiğine veriyorlar.

**Problem:** Multi-turn Text-to-SQL'de model bir SQL yazar, feedback alır ve düzeltir. Yalnızca son SQL'e bakan reward, modelin turlar boyunca gerçekten düzelip düzelmediğini ödüllendirmez. Gereksiz yere çok tur kullanmayı da cezalandırmaz.

**Ne yaptılar:**
1. Taban Qwen2.5-Coder-7B/14B-Instruct. Veri: BIRD train, Spider train ve SynSQL-2.5M'den (OmniSQL'in sentetik seti, aşağıda) ~20K örnek.
2. RL: GRPO (verl kütüphanesiyle), soru başına 8 rollout, temperature 1.0, lr (learning rate, öğrenme hızı) 1e-6, en fazla 4 tur.
3. Reward dört parçadan oluşur:
   - İlerleme: İlk SQL'in ve son SQL'in gold SQL'e benzerliği ölçülür; reward ikisinin farkıdır. Benzerlik yapısal (sorgunun clause ağacı) ve sözcüksel (art arda gelen kelime çiftlerinin örtüşmesi) parçalardan oluşur (bu ayrıntı makaleden). İlerleme pozitif reward alır, yerinde saymak ceza alır.
   - Latency: Her ek turda 0.5 ile azalan bir reward; model ne kadar erken bitirirse o kadar çok alır.
   - Çalışabilirlik: SQL'in çalışır durumunu koruma, kazanma ya da kaybetme reward'ı.
   - Format reward'ı.
4. Eğitimde gold SQL ile karşılaştıran bir "Oracle-guided Diagnostic Tree" (gold'u bilen teşhis ağacı) clause düzeyinde hata feedback'i verir; ör. "WHERE koşulu yanlış". Değerlendirme tek turludur ve bu feedback yoktur.

**Sonuç:** Yazarların raporuna göre BIRD dev'de Vote@8 ile (8 cevap üretip en sık çıkan sonucu seçmek; bir tür [test-time scaling](00_terimler.md#test-time-scaling)) 7B 64.3 (taban model 52.3, +12.0), 14B 67.5 (taban 60.2, +7.3). Ablation (7B; tam yöntem 64.3; model boyu tablonun kendisinde yazmıyor, tam yöntem satırı 7B sonucuyla aynı):
- tek turlu RL: 61.2
- tur başına decay kaldırılınca: 47.5 (en büyük düşüş, tabanın da altında)
- yapısal hizalama olmadan: 61.6

**Bizim için:** Tur sayısını cezalandıran (decay) terim olmadan multi-turn reward çöküyor. Bizim RL reward'ımızda da bir tool-call maliyeti olmalı.

### CAPER: Clause-Aligned Process Supervision for Text-to-SQL (CUHK-Shenzhen, HKU, Haziran 2026) — [2606.03327](https://arxiv.org/abs/2606.03327)

**Tek cümlede:** SQL'in her clause'unu (SELECT, WHERE, GROUP BY...) ayrı puanlayan bir process reward model (PRM) eğitip GRPO'da sık (dense) reward olarak kullanıyorlar.

**Problem:** Yalnızca son sonuca bakan reward seyrektir (sparse): SQL'in neresinin yanlış olduğunu söylemez. Uzun bir SQL'de yalnızca WHERE yanlış olsa da bütün sorgu 0 alır. Token düzeyinde puan vermek ise anlamsız birimlere, tek tek kelime parçalarına not verir. CAPER puanı SQL'in anlamlı birimlerine, clause'lara verir. [PRM](00_terimler.md#reward-model-grm-ve-prm), cevabın her ara adımına puan veren bir reward model'dir.

**Ne yaptılar:**
1. Hatalı örnekler: Qwen3.5-9B rollout'lar üretir. Sonucu gold ile aynı olanlar başarılı, olmayanlar başarısız sayılır. Başarısız SQL'de gold'dan ilk sapan clause bulunur. Bu clause AST (SQL'in ağaç biçimi) düzenlemeleriyle gold'a doğru onarılır; onarım sonucu düzeltiyorsa hatanın kök nedeni o clause'dur.
2. Fault injection (hata enjeksiyonu): Başarılı SQL'lere, tipi koruyup sonucu değiştiren AST mutasyonları eklenir. Örnek: `WHERE year = 2020` yerine `WHERE year > 2020`. Böylece hatanın yeri tam bilinen yeni örnekler çıkar.
3. Veri boyutu: BIRD train, Spider dev ve SynSQL-5k'dan 90K+ clause etiketli tercih örneği; 82,081'i eğitim için.
4. PRM: CAPER-9B (Qwen3.5-9B tabanlı), margin ağırlıklı pairwise tercih loss'uyla eğitilir: doğru clause'un puanı yanlışınkinden belli bir farkla (margin) yüksek olmalı.
5. RL: Başlangıç modeli BIRD train + SynSQL-5k ile SFT edilmiş Qwen3.5-9B. Her clause sınırında reward verilir: format kapısı (format bozuksa 0) çarpı [yarısı PRM skoru + yarısı execution reward'ı]. Execution reward'ı yalnızca son clause'da eklenir.
6. Clause-level return-to-go: her clause'un değeri, kendisinden sonraki clause reward'larının toplamıdır. Grup normalizasyonu clause pozisyonuna göre yapılır; ör. bütün rollout'ların 2. clause'ları kendi aralarında karşılaştırılır. Batch 16, 8 rollout, lr 1e-6.

**Sonuç:** Yazarların raporuna göre BIRD dev'de P@1 (tek cevap doğru mu) / MV@8 (8 cevaptan çoğunluk oyu):
- yalnız SFT: 57.56 / 61.34
- yalnız son sonuca bakan (outcome) GRPO: 60.21 / 62.19
- CAPER: 63.56 / 69.61

CAPER outcome GRPO'ya göre P@1'de +3.35, MV@8'de +7.42. Token düzeyinde dense reward (57.36 / 60.49) seyrek GRPO'yu geçemiyor, SFT'nin bile biraz altında kalıyor. Fault injection olmadan PRM'in hata yerini bulma doğruluğu 84.53'ten 22.20'ye düşüyor; yani hata enjeksiyonu PRM'in çalışması için şart.

**Bizim için:** Bizim büyük modelimizle aynı boyda (9B) bir model PRM olabiliyor. Ama PRM verisi gold'a karşı AST mutasyonu gerektiriyor, ve dense reward clause gibi anlamlı birimlerde verilmeli, token düzeyinde değil.

### Every Step Counts / FineStep: Step-Level Credit Assignment for Tool-Integrated Text-to-SQL (Ant Group, Soochow University, USTC, Mayıs 2026) — [2605.04719](https://arxiv.org/abs/2605.04719)

**Tek cümlede:** SQL çalıştıran multi-turn agent'ta her tool call adımına, öğrenilmiş bir model kullanmadan, kurallarla hesaplanan bir adım puanı (process reward) ve adım düzeyinde advantage veriyorlar.

**Problem:** GRPO bir trajectory'nin bütün adımlarına aynı krediyi verir. 10 turluk bir konuşmada işe yarayan keşif sorgusu ile boşa giden tekrar sorgusu aynı ödülü alır. CAPER gibi bir PRM eğitmek pahalıdır; FineStep benzer işi basit kurallarla yapar.

**Ne yaptılar:**
1. Modeller Qwen3-4B-Instruct, Qwen3-8B ve Qwen3-30B-A3B ([MoE](00_terimler.md#moe): toplam 30B parametre, her token'da yalnızca 3B'si çalışır). Think-act-observe döngüsü, tek tool `sql_executor`, en fazla 10 tur.
2. Process reward (her adım için): Adımın SQL'i sözdizimi kontrolünden geçmiyorsa ya da önceki bir çağrıyı tekrarlıyorsa 0 (sert kısıt). Geçiyorsa 1 + örtüşme oranı. Örtüşme oranı = adımın sonucundaki hücrelerden gold sonuçta da olanların sayısı, bölü gold sonucun boyutu. Örnek: gold sonuç 4 hücre, keşif sorgusu bunların 2'sini döndürüyor; puan 1 + 2/4 = 1.5.
3. Outcome reward (son cevap): format için 0 ya da 1, artı execution eşleşmesi için 0 ya da 2.
4. Adım advantage'ı:
   - Outcome reward sondan geriye doğru her adımda 0.98 ile çarpılarak indirgenir (γ=0.98); sona yakın adımlar daha büyük pay alır.
   - Her adımın process değeri sonraki adımınkiyle yarı yarıya karıştırılarak yumuşatılır (β=0.5).
   - Son adım yalnızca outcome advantage'ı alır; önceki adımlar outcome ve process'in yarı yarıya karışımını alır (λ=0.5).
5. Ortamdan gelen feedback token'ları (SQL sonuçları) loss'tan maskelenir; model kendi üretmediği bu metinden öğrenmez.
6. Eğitim: verl, batch 128, group 8, lr 1e-6, 5 epoch.

**Sonuç:** Yazarların raporuna göre BIRD dev'de 4B 68.51 (düz GRPO 66.23, +2.28), 8B 68.06 (66.56, +1.50), 30B-A3B 69.23 (68.32, +0.91). Kazanç en çok zor sorularda (4B'de +6.21) ve en küçük modelde. Ablation (4B):
- outcome indirgemesi kaldırılınca −4.34
- process yumuşatma kaldırılınca −2.08
- yalnız outcome advantage'ı kullanılınca −1.82

**Bizim için:** Tekrar eden ve pre-check'ten geçmeyen çağrıya 0, gold sonuca kısmen yaklaşan keşif sorgusuna kısmi kredi. Bu, bizim `execute_sql` keşif adımlarımıza doğrudan uyan ve ek model gerektirmeyen bir process reward.

### ReViSQL / Human-Level Text-to-SQL via RL on Verified Data (University of Illinois, Daniel Kang grubu, Mart 2026, v4 Ağustos 2026) — [2603.20004](https://arxiv.org/abs/2603.20004)

**Tek cümlede:** Karmaşık pipeline'lar kurmak yerine temizlenmiş veride RLVR yapıyorlar; BIRD train'in hatalarını düzeltmenin tek başına büyük kazanç getirdiğini gösteriyorlar.

**Problem:** BIRD train'deki gold SQL'lerin, soruların ve ipuçlarının bir kısmı yanlış. [RLVR](00_terimler.md#rl-ve-rlvr) (reward'ı otomatik doğrulanabilen RL; burada SQL sonucu gold ile aynı mı) modeli gold'a göre ödüllendirdiği için, yanlış gold modele yanlış şeyi öğretir. Birçok sistem doğruluğu çok aşamalı, çok modelli pipeline'larla artırmaya çalışıyor; yazarlar asıl sorunun veride olduğunu savunuyor.

**Ne yaptılar:**
1. Veri temizliği: BIRD train'den 2.5K örnek bir LLM ve bir uzman tarafından en fazla 4 turda doğrulandı (v1'de adı BIRD-Verified, v4'te BIRD-Platinum). Örneklerin %61.1'inde hata bulundu: gold SQL'de %52.1, soruda %26.2, external knowledge'da (BIRD'ün soruyla verdiği ipucu, "evidence") %18.2.
2. Checklist: NULL, eşitlik (tie) ve eksik DISTINCT gibi hata türleri için bir kontrol listesi yayınlandı. Tie örneği: "en yüksek maaşlı çalışan" sorusunda iki kişi aynı maaşı alıyorsa `LIMIT 1` birini atar.
3. RL ayarı: CISPO loss (token'ları güncellemeden çıkarmak yerine [importance sampling](00_terimler.md#importance-sampling) ağırlığını kırpan bir GRPO varyantı), group size 16, [LoRA](00_terimler.md#lora) rank 32 (modelin tamamı yerine küçük ek matrisleri eğitmek), batch 64, lr 5e-5, en fazla 5 etkileşim turu, 85:15 train/validation ayrımı, eğitim servisi olarak Tinker.
4. Modeller Qwen3-235B-A22B ve Kimi-K2.6 (v1 özetinde daha hafif bir 30B model de var).
5. Reward shaping: Yalnızca sonuç eşleşmesine bakan reward'ın ~%32.8 false positive verdiği görüldü: sorgu yanlış ama bu veritabanında tesadüfen doğru sonucu veriyor. Örnek: `WHERE city = 'Paris'` yerine `WHERE id = 7` yazmak, Paris'in id'si 7 ise aynı sonucu verir. Bunun için VeriEQL ile eşdeğerlik kontrolü yapılır (iki sorgunun her veritabanında aynı sonucu verip vermediğini karşı örnek arayarak denetleyen bir araç); çürütülen sorgunun reward'ı β=0.2 ile düşürülür. Ayrıca evidence'ın her maddesi SQL'de açıkça kullanılmazsa küçük bir süreç cezası verilir (λ=0.1).

**Sonuç:** Yazarların raporuna göre:
- Temiz veriyle eğitilen Qwen3-235B, BIRD train ile eğitilen aynı modelden Arcwise-Plat'ta (makalede "BIRD'ün uzmanlarca doğrulanmış sürümü" diye tanımlanan değerlendirme seti) +11.0–16.1, Spider2'de (kurumsal ölçekte, çok daha zor bir Text-to-SQL seti) +11.8–14.0 puan daha iyi.
- Kimi-K2.6'da BIRD train ile eğitim doğruluğu düşürdü, temiz veri yükseltti.
- ReViSQL-BIRD-K2.6, Arcwise-Plat-Full'da greedy (temperature 0, tek cevap) 93.8; insan performansının yaklaşık değeri (insan proxy'si) 92.96. Yani insan seviyesinin biraz üstünde.
- Reward shaping +2.8–3.8 puan ekliyor.
- Kalan hataların %69'u soru belirsizliği: soru birden çok şekilde okunabiliyor.

**Kaynak notu:** Makalenin birden çok sürümü var (v1 Mart 2026, v4 Ağustos 2026). Temiz veri setinin adı (BIRD-Verified, BIRD-Platinum) ve model listesi sürümler arasında değişiyor.

**Bizim için:** BIRD train gold SQL'leri gürültülü. RL ya da SFT verisini seçmeden önce gold'u çalıştırıp boş ya da şüpheli olanları atmak (ya da büyük modelle kontrol etmek) en ucuz kazanç.

### TRUST-SQL: Tool-Integrated Multi-Turn RL for Text-to-SQL over Unknown Schemas (Meituan, BUPT, ICT/CAS, Mart 2026) — [2603.16448](https://arxiv.org/abs/2603.16448)

**Tek cümlede:** Şema modele önceden verilmiyor; 4B/8B agent şemayı tool'larla keşfediyor, gereken kısmı öneriyor, SQL yazıp onaylıyor; şema adımı için ayrı bir advantage "track"i kullanılıyor.

**Problem:** Gerçek veritabanlarında şema çok büyük olabilir ve bağlama sığmaz. Agent'ın hangi tabloların gerektiğini kendisinin bulması gerekir. Ama reward yalnızca son SQL'e verilirse, şema keşfinin iyi yapılıp yapılmadığı ayrıca ödüllendirilmez.

**Ne yaptılar:**
1. Modeller Qwen3-4B/8B; eğitim kütüphanesi SLIME.
2. SFT warm-up ([cold start](00_terimler.md#cold-start): RL'den önce formatı ve temel davranışı öğreten kısa SFT): SynSQL-2.5M'den orta ve üstü zorlukta 9,217 soru. Trajectory'ler GPT-4.1-mini, GPT-4o-mini ve DeepSeek-R1 ile üretilmiş. Yalnızca sonucu doğru ve formatı geçerli olanlar tutulmuş ([rejection sampling](00_terimler.md#rejection-sampling): çok örnek üretip yalnızca doğruları tutmak).
3. RL verisi: BIRD + Spider train'den 18,078 aday soru, her biri 8 kez rollout edilmiş. [Pass rate](00_terimler.md#pass-rate-ve-passk)'i (8 denemeden kaçının doğru olduğu) 6/8'in altında kalan 11,642 soru tutulmuş; yani model için kolay sorular atılmış.
4. Eylemler: explore_schema (şemaya bak), propose_schema (gereken tablo ve sütunları öner), generate_sql (SQL yaz), confirm_answer (cevabı onayla). execute_sql en fazla 30 satır döner. Eğitimde 10 tur budget.
5. Reward: doğru sonuç 1.0, çalışan ama yanlış 0.2, boş ya da hatalı 0. Protokole tam uyulursa +0.1 format. Şema reward'ı ikilidir (önerilen şema doğru mu) ve yalnızca execution reward'ı 1.0 ise sayılır.
6. Dual-Track GRPO: İki ayrı advantage hesaplanır. Şema track'i yalnızca Propose adımına kadar olan token'lara uygulanır, sonrası maskelenir. Tam track bütün trajectory'ye uygulanır. Loss = tam track + 0.25 × şema track.

**Sonuç:** Yazarların raporuna göre BIRD dev greedy / majority (çoğunluk oyu): 4B 64.9 / 67.2, 8B 65.8 / 67.7. Spider test 82.8 / 85.0 (4B). Ablation:
- Şema track ağırlığı 0.25 en iyi (ablation tablosunda 64.5). Reward'ları düz toplamak 58.7; yalnızca execution reward'ı 60.9; ağırlık 0.375 olunca model aşırı keşif yapıyor ve 54.2'ye düşüyor; şema reward'ı execution'a bağlanmazsa 52.7.
- Turn budget 10 en iyi; 12 kararsız.
- Eğitim sırası: yalnız RL 59.9 (model ilk turda her şeyi sorgulamayı öğreniyor), yalnız SFT 46.2, SFT sonra RL 64.9. Yani SFT'yi RL'den önce yapmak yalnız RL'e göre +5 puan.

**Bizim için:** 4B'de cold start SFT + pass rate filtresiyle seçilmiş RL verisi + 10 tur budget doğrudan bizim kurulumumuza uyuyor. Ara reward'lar ancak execution doğruysa sayılmalı.

### SQL-Trail: Multi-Turn RL with Interleaved Feedback for Text-to-SQL (AWS, Stanford, Ocak 2026) — [2601.17699](https://arxiv.org/abs/2601.17699)

**Tek cümlede:** ReAct döngüsünde (düşün, eylem yap, observation'a bak) SQL çalıştırıp sonuca bakarak düzelten bir agent'ı çok az veriyle önce SFT, sonra multi-turn RL ile eğitiyorlar.

**Problem:** Tek seferde SQL yazan model hatasını göremez; SQL'i çalıştırıp sonucu gören bir agent kendini düzeltebilir. Soru, bu davranışı az veri ve az hesapla öğretmenin mümkün olup olmadığı.

**Ne yaptılar:**
1. Modeller Qwen2.5-Coder 3B/7B/14B.
2. SFT verisi: Spider train'den 3,000 soru için Claude 3.7 Sonnet en fazla 10 turluk trajectory üretti. Final SQL'i doğru olan 1,000 tanesi (orta ve zor ağırlıklı) tutuldu. Batch 128, 2 epoch, lr 1e-5.
3. RL verisi (1,027 soru):
   - 2,800 SynSQL adayından pass@6 ile (6 denemeden kaçının doğru olduğu) "bazen çözülen" 700 dengeli soru.
   - 327 keşif sorusu: SFT sonrası başarısız 127, pass@6=0 olan 100 SynSQL ve pass@6=0 olan 100 çok zor Spider sorusu.
4. RL ayarı: GRPO, group 6, temperature 1.0, [KL](00_terimler.md#kl-penalty) yok (KL: modelin başlangıç modelinden çok uzaklaşmasını cezalandıran terim), [clip-higher](00_terimler.md#clip-ve-clip-higher) (iyi cevapların olasılığının bir adımda daha çok artmasına izin veren gevşek üst sınır), lr 1e-6, batch 128. En fazla 10 tur; tek tool SQL execution, sonuç sütun başlıklarıyla döner.
5. Reward (trajectory düzeyinde, toplam): 5 × execution doğruluğu + 2 × tur budget'ına uyma + şema Jaccard + bigram Jaccard + syntax + format. Tur eşiği zorluğa bağlı: kolay soruda 2, orta soruda 3 tur.
   - Şema Jaccard: kullanılan tablo/sütunların gold'dakilerle örtüşmesi. Örnek: gold `{orders, customers}`, model `{orders}`; ortak 1, toplam 2, puan 0.5.
   - Bigram Jaccard: art arda gelen kelime çiftlerinin gold SQL'dekilerle örtüşmesi.

**Sonuç:** Yazarların raporuna göre BIRD dev greedy / majority: 7B 60.1 / 64.2, 14B 63.6 / 66.7. Spider test 7B 86.0 / 87.6. Ablation:
- Kısmi reward'lar arasında en çok bigram benzerliği katkı veriyor.
- Tur reward'ı kaldırılınca etkileşim uzuyor ama doğruluk artmıyor.
- Multi-turn RL tek turlu RL'den iyi: 59.3'e karşı 56.3, +3 puan.
- SFT sonra RL en iyi sıra.

**Bizim için:** ~1K büyük model trajectory'si ile SFT ve pass@k ile seçilmiş ~1K RL sorusu yetiyor. Bu, Mac'te yapılabilir bir ölçek.

### MTIR-SQL: Multi-turn Tool-Integrated Reasoning RL for Text-to-SQL (Meituan, CASIA, PKU ve diğerleri, Ekim 2025) — [2510.25510](https://arxiv.org/abs/2510.25510)

**Tek cümlede:** 4B modeli SQL çalıştırma tool'uyla multi-turn GRPO ile eğitiyorlar; GRPO'ya bozuk rollout filtresi ekleyip KL'yi kaldırıyorlar.

**Problem:** Multi-turn RL'de bazı rollout'lar bozuk ya da düşük kaliteli olur ve eğitimi kararsızlaştırır. KL cezası da modeli başlangıç modeline bağlı tutarak keşfi sınırlayabilir. Yazarlar ikisini birden ele alan basit bir GRPO varyantı öneriyor.

**Ne yaptılar:**
1. Model Qwen3-4B. Veri: Spider + BIRD; boş sonuç dönen gold SQL'ler atılmış, çünkü reward sinyali vermiyor.
2. Tool SQL'i çalıştırır, sütun adlarını ve en fazla 10 satırı döner.
3. RL ayarı: en fazla 6 tur, girdi başına 5 örnek, temperature 0.6, en fazla 8192 token, batch 64, lr 1e-6, 8×A100 GPU, RL-Factory çerçevesi.
4. GRPO-Filter: KL yok; düşük kaliteli rollout'lar bir eşikle atılır.
5. Reward: format ±0.1, çalışabilirlik ±0.1, sonuç +1/−1.

**Sonuç:** Yazarların raporuna göre BIRD dev 64.4 (ablation tablolarında 63.1), Spider dev 84.6. Algoritma karşılaştırması: [PPO](00_terimler.md#ppo) (değer modeli, yani critic kullanan klasik RL yöntemi) 58.2, düz GRPO 60.3, GRPO-Filter 63.1; filtre düz GRPO'ya +2.8 puan ekliyor. Execution reward'ı olmadan 59.4, sonuç reward'ı olmadan 58.8. Daha çok tur genelde yardım ediyor, ama 6 turda kararsızlık başlıyor.

**Kaynak notu:** Makalede rakamlar tutarsız: ör. BIRD dev ana sonuçta 64.4, ablation tablolarında 63.1.

**Bizim için:** 4B ölçeğinde KL'siz GRPO + bozuk rollout filtresi + boş gold'ların atılması basit ve doğrudan uygulanabilir.

### A State-of-the-Art SQL Reasoning Model using RLVR (Databricks Mosaic Research, Eylül 2025) — [2509.21459](https://arxiv.org/abs/2509.21459)

**Tek cümlede:** Yalnızca BIRD train ve basit bir reward ile önce offline RL warm-up, sonra online RLVR yapıp BIRD test sıralamasında ilk sıraya çıkıyorlar.

**Problem:** Text-to-SQL'de en iyi sonuçlar çoğunlukla karmaşık pipeline'larla ve çok veriyle alınıyor. Yazarlar tek bir modelin, yalnızca BIRD train ve basit bir reward ile aynı seviyeye çıkıp çıkamayacağını deniyor.

**Ne yaptılar:**
1. Taban Qwen2.5-Coder-32B-Instruct; dev'de en iyi olduğu için seçilmiş. Prompt: OmniSQL'in prompt'u, değiştirilmiş bir veritabanı kodlaması (şemanın prompt'ta nasıl yazıldığı) ve reasoning isteyen bir talimat.
2. TAO (Databricks'in offline RL yöntemi): soru başına birkaç cevap örnekle, verifiable reward ile puanla, sonra bu sabit veriyle RL yap. Offline, yani model eğitim sırasında yeni cevap üretmiyor, önceden toplanmış cevaplardan öğreniyor ([on-policy ve off-policy](00_terimler.md#on-policy-ve-off-policy)). TAO kısa tutulmuş, çünkü fazla TAO sonraki online RL'in kazancını azaltıyor.
3. Online RL: GRPO tabanlı; zor problemlere odaklanma ve reward doygunluğunu önleme (model soruların çoğunu çözünce öğrenecek sinyal kalmaması) üzerine ayarlar.
4. Reward: BIRD execution eşleşmesi 0/1; sözdizimi geçersiz SQL −1.
5. Ayar bulguları: düşük lr ve düşük KL daha iyi; KL'yi tamamen kaldırmak belirgin zarar vermedi; reward shaping (ek ara reward'lar eklemek) kazanç getirmedi.
6. Çıkarımda 7 cevap üretilip ağırlıklı majority vote ile biri seçilir.

**Sonuç:** Yazarların raporuna göre BIRD dev'de taban model 64.80, yalnız TAO 67.40 (+2.6), TAO'dan sonra RLVR 70.80 (tabana göre +6.0). BIRD test'te (cevapları gizli tutulan resmi test seti; sıralama bunun üzerinden) 73.56; self-consistency (birden çok cevap üretip sonucu en sık çıkanı seçmek) ile 75.68.

**Bizim için:** Basit execution reward'ı + geçersiz SQL'e ceza yetiyor. Reward shaping'e emek harcamak yerine prompt ve taban model seçimine bakılmalı.

### Arctic-Text2SQL-R1: Simple Rewards, Strong Reasoning in Text-to-SQL (Snowflake AI Research, UMD, UCSD, Mayıs 2025) — [2505.20315](https://arxiv.org/abs/2505.20315)

**Tek cümlede:** Execution doğruluğuna dayanan basit bir reward ile GRPO; asıl farkı veri filtresinin ve güçlü bir SFT başlangıcının yarattığını gösteren bir "ne işe yaradı" çalışması.

**Problem:** Text-to-SQL RL'inde birçok karmaşık reward ve veri seçeneği deneniyor ama hangisinin gerçekten işe yaradığı belli değil. Yazarlar bu seçenekleri tek tek ölçüp en basit çalışan reçeteyi arıyor.

**Ne yaptılar:**
1. Başlangıç: OmniSQL'in SFT checkpoint'leri (Qwen2.5-Coder tabanlı; aşağıda).
2. Veri: BIRD train 8,017 (9,428'den), Spider train 6,972, Spider dev 985, Gretel-Synth 11,811 (sentetik bir Text-to-SQL seti).
   - Boş sonuç dönen ve 5 saniyeden uzun süren sorgular atılmış.
   - Gretel-Synth'te 10 örnekten en az birinin doğru çözdüğü sorular tutulmuş, yani hiç çözülemeyenler atılmış.
3. Online GRPO: temperature 0.8, soru başına 16 rollout, batch 256 (update 128), KL β=0.001, clip 0.2 (bir güncellemede bir token'ın olasılığının en fazla %20 değişmesine izin veren sınır).
4. Reward: sonuç doğruysa 1, SQL çalışıyorsa 0.1, değilse 0.
5. Biçim: model önce `<think>` içinde düşünür, sonra `<answer>` içinde SQL verir.

**Sonuç:** Yazarların raporuna göre BIRD dev / test: 7B 68.9 / 68.5, 14B 70.1 / 70.0, 32B 70.5 / 71.8. Başlangıç noktası OmniSQL-7B'nin BIRD dev'i 63.9 olduğu için (OmniSQL'e bakın), 7B'de RL +5.0 ekliyor. Ablation:
- Boş sonuçları filtrelemek yardım ediyor; filtresiz sentetik veri zarar veriyor.
- GRPO PPO'dan iyi (64.9'a karşı 63.0).
- Online RL, batch (toplu, offline) RL'den iyi.
- Daha ince (kısmi puan veren) reward'lar "tembel" davranış doğurmuş.
- Rollout sayısını değiştirmek belirgin fark yaratmamış.
- Yalnız BIRD ile eğitim diğer benchmark'larda 1.4 puan düşürmüş.
- LLM ile veri çoğaltma ve SynSQL-2.5M eklemek açık kazanç vermemiş.

**Bizim için:** Reward'ı "doğru 1, çalışıyor 0.1" gibi basit tut, boş sonuçlu ve yavaş örnekleri at, RL'i iyi bir SFT checkpoint'inden başlat.

### SkyRL-SQL (UC Berkeley NovaSky / Sky Computing Lab, Mayıs 2025) — [blog](https://novasky-ai.notion.site/skyrl-sql)

**Tek cümlede:** 7B modeli, veritabanını sorgulayıp sonuca bakarak SQL'i düzelten multi-turn RL ile yalnızca 653 eğitim örneğiyle eğitiyorlar.

**Problem:** OmniSQL gibi modeller milyonlarca örnekle SFT ediliyor. Yazarlar birkaç yüz soruyla yapılan multi-turn RL'in bu kadar veriyle eğitilmiş modellere yetişip yetişemeyeceğini deniyor.

**Ne yaptılar:**
1. Taban Qwen2.5-Coder-7B-Instruct.
2. Veri: 653 örnek. Hugging Face'teki veri setinde kaynak etiketi SynSQL ve Spider. Örneklerin nasıl seçildiği bulduğum kaynaklarda yazmıyor.
3. Altyapı VeRL + Search-R1 (aşağıda) üstüne kurulu.
4. Biçim: model `<think>` içinde düşünür, `<sql>` ile keşif sorgusu çalıştırır, sonuç `<observation>` içinde döner, son SQL `<solution>` içindedir.
5. Reward ikili: son SQL çalışıp gold ile aynı sonucu verirse 1, değilse 0.

**Sonuç:** Yazarların raporuna göre (blog):
- Spider'ın farklı sürümlerinde GPT-4o ve o4-mini'yi geçiyor; tabana göre ortalama +7.2, en iyi +9.2.
- 2.5M örnekle SFT edilmiş OmniSQL-7B'yi geçiyor.
- Aynı 653 örnekle multi-turn eğitim, %60 reward'a single-turn eğitimden 2.8 kat daha az adımda ulaşıyor.
- Değerlendirmede tur sayısı 1'den 5'e çıkınca ortalama +4.5.
- Görülen hata türleri: aşırı güven ve döngüye girme.

**Kaynak notu:** Kaynak yalnızca bir blog yazısı; makale yok. Örneklerin nasıl seçildiği bulduğum kaynaklarda yazmıyor.

**Bizim için:** Birkaç yüz iyi seçilmiş soru multi-turn RL için yetebiliyor. Döngü ve tekrar korumaları (bizdeki `MAX_REPEATS`) gerekli.

### Reward-SQL: Stepwise Execution-Aware Reasoning and Process-Supervised Rewards (Renmin University, HKUST-GZ, Tsinghua, Alibaba Cloud, Mayıs 2025, v3 Haziran 2026) — [2505.04671](https://arxiv.org/abs/2505.04671)

**Tek cümlede:** SQL'i adım adım CTE'lerle yazdırıp (Chain-of-CTEs, CoCTE) her adımı puanlayan bir PRM eğitiyorlar; PRM'i hem GRPO reward'ı hem de Best-of-N seçici (N cevaptan en yüksek puanlıyı seçen) olarak kullanıyorlar.

**Problem:** Tek parça yazılmış uzun bir SQL'in hangi kısmının yanlış olduğu anlaşılmaz. SQL küçük, ayrı çalıştırılabilir adımlara bölünürse her adım ayrı kontrol edilip puanlanabilir. CTE, `WITH` ile tanımlanan ara tablodur:

```sql
WITH ca_schools AS (SELECT * FROM schools WHERE state = 'CA')
SELECT COUNT(*) FROM ca_schools WHERE enrollment > 500;
```

Burada birinci adım (`ca_schools`) tek başına çalıştırılıp doğru okulları seçip seçmediğine bakılabilir.

**Ne yaptılar:**
1. Model Qwen3-8B.
2. Cold start verisi: DeepSeek-V3.1'e 5 örnek gösterilir (few-shot) ve BIRD ile Spider gold SQL'lerini CoCTE trajectory'lerine çevirmesi istenir. AST filtresinden (SQL'in yapısını kontrol) sonra 17,462 sorgudan 51,996 trajectory çıkar (%90.7 kabul). SFT: lr 1e-5, batch 64, 3 epoch.
3. PRM verisi: SFT modeli her BIRD train sorusu için 8 rollout üretir. MCTS (Monte Carlo Tree Search: bir ara adımdan devam eden birçok çözümü deneyip başarı oranına bakmak) ile her ara adıma, o adımdan devam edildiğinde execution'ın ne sıklıkla başarılı olduğu etiketlenir (~16K örnek). PRM Qwen2.5-Coder-7B üzerinde BCE ile (ikili sınıflandırma loss'u: adım iyi mi kötü mü) eğitilir.
4. RL: GRPO'da outcome + process (PRM) reward birlikte, KL ile. PRM eğitim boyunca değişmez (donuk).

**Sonuç:** Yazarların raporuna göre BIRD dev'de greedy 66.0; SFT 63.2, yalnız outcome GRPO 62.6. Yani process reward olmadan GRPO SFT'nin bile altında kalıyor, process reward ile +2.8. PRM@32 (32 cevap üretip PRM'in en beğendiğini seçmek) 70.3.
- Cold start verisini tek bir büyük modelden (DeepSeek, GPT-4 ya da Claude) üretmek benzer sonuç veriyor (PRM@8 67.6–68.9); üç modelin karışımı 70.0.
- CoCTE biçimi düz SQL'den (63.6) ve düz [CoT](00_terimler.md#cot-ve-long-cot)'tan (chain-of-thought: cevaptan önce düz metin düşünce, 64.2) iyi.

**Bizim için:** SFT trajectory'lerini birden çok büyük modelden karıştırmak tek modele göre kazanç veriyor. Bizim adımlarımız zaten çalıştırılabilir parçalar olduğu için adım düzeyinde PRM fikri uygulanabilir; ama ilk deneme kural tabanlı process reward (FineStep) olmalı.

### SQL-R1: Training Natural Language to SQL Reasoning Model by RL (IDEA Research, HKUST-GZ, Nisan 2025, NeurIPS 2025) — [2504.08600](https://arxiv.org/abs/2504.08600)

**Tek cümlede:** Tek turlu GRPO ile Text-to-SQL reasoning; cold start'ın ve reward parçalarının etkisini ablation'larla tek tek ölçüyorlar.

**Problem:** DeepSeek-R1 benzeri reasoning RL'inin Text-to-SQL'de nasıl kurulması gerektiği açık değil. İki soru öne çıkıyor: RL'den önce SFT gerekli mi, ve reward hangi parçalardan oluşmalı.

**Ne yaptılar:**
1. Modeller Qwen2.5-Coder 3B/7B/14B.
2. Cold start SFT: SynSQL-2.5M'den her zorluk seviyesinden 50K, toplam 200K örnek.
3. RL verisi: SynSQL-2.5M'den yalnızca "Complex" zorluk seviyesinden rastgele 5K soru.
4. GRPO: lr 3e-7, 8 rollout, en fazla 2048 token.
5. Reward dört parça: format ±1, çalışabilirlik ±2, sonuç ±3 ve uzunluk (en fazla 1).
6. Çıkarımda 8 aday üretilir ve self-consistency ile biri seçilir.

**Sonuç:** Yazarların raporuna göre BIRD dev 14B 67.1, 7B 66.6 (OmniSQL-7B'den başlayınca); Spider test 88.7 (7B). Cold start karşılaştırması (7B):
- SFT'siz, doğrudan RL: 63.1
- SynSQL-200K reasoning SFT'sinden sonra RL: 59.2 (SFT'sizden 3.9 puan kötü)
- OmniSQL-7B'den başlayınca: 66.6

Yani cold start her zaman gerekli değil; işe yarayıp yaramadığı veri kaynağına ve miktarına bağlı. Reward ablation'ı (63.1'den): format olmadan 60.4, çalışabilirlik olmadan 60.7, uzunluk olmadan 61.0; her parça 2–3 puan katkı veriyor.

**Bizim için:** Kötü bir SFT seti RL'i aşağı çekebiliyor; SFT verisinin kalitesi miktarından önemli.

### Reasoning-SQL: RL with SQL Tailored Partial Rewards (Google Cloud, Google DeepMind, Stanford, Mart 2025) — [2503.23157](https://arxiv.org/abs/2503.23157)

**Tek cümlede:** Seyrek execution reward'ını SQL'e özgü partial (kısmi) reward'larla destekleyen, SFT'siz GRPO.

**Problem:** Yalnızca "sonuç doğru mu" reward'ı seyrektir: zor sorularda model neredeyse hep 0 alır ve öğrenecek sinyal bulamaz. Kısmi doğruluğa da puan verilirse (ör. doğru tabloları seçmek), model daha erken öğrenmeye başlayabilir.

**Ne yaptılar:**
1. Modeller Qwen2.5-Coder 3B/7B/14B.
2. Veri: BIRD train'den hem Gemini-2.0-flash'ın hem GPT-4o'nun yanlış bulduğu örnekler atılınca 8,026 örnek.
3. GRPO: lr 1e-6, batch 32, 3 epoch, soru başına 6 cevap, 8×H100.
4. Reward parçaları ve ağırlıkları:
   - execution doğruluğu: 3
   - [LLM-as-judge](00_terimler.md#llm-as-judge-ve-rubric) (başka bir LLM'in cevabı değerlendirmesi): 2
   - syntax (SQL çalışıyor mu): 1
   - schema linking (kullanılan şema öğelerinin gold'dakilerle Jaccard örtüşmesi): 1
   - bigram benzerliği: 1
   - format: 1

   Schema linking örneği: gold `SELECT name FROM users WHERE age > 30` şu öğeleri kullanır: {users, users.name, users.age}. Model `SELECT name FROM users WHERE city = 'X'` yazarsa öğeleri {users, users.name, users.city} olur. Ortak 2, toplam 4 farklı öğe; puan 0.5.

**Sonuç:** Yazarların raporuna göre 14B model, CHASE-SQL pipeline'ı içinde (birden çok aday üretip aralarından seçen çok aşamalı bir Text-to-SQL sistemi) BIRD dev 72.29, test 72.78. 7B tabanda bütün reward'lar birlikte +6.77 iyileştiriyor, SFT ise +4.11. SFT modelleri Spider-DK (alan bilgisi gerektiren sorular) ve Spider-Syn (sütun adları yerine eş anlamlı kelimeler) üzerinde tabanın bile altında kalırken RL modeli genelleşiyor.

**Bizim için:** Partial reward'lar küçük modelde seyrek reward'ı yumuşatabilir. Ama Arctic ve Databricks'in bulgusuyla (ince reward tembellik doğuruyor, kazanç getirmiyor) birlikte okunmalı; önce yalnız execution reward'ı denenmeli.

### ExCoT: Optimizing Reasoning for Text-to-SQL with Execution Feedback (Snowflake, Mart 2025) — [2503.19988](https://arxiv.org/abs/2503.19988)

**Tek cümlede:** RL yerine, yalnızca execution doğruluğundan kurulan tercih çiftleriyle önce off-policy, sonra on-policy, iteratif DPO yapıyorlar; reward model ya da insan etiketi yok.

**Problem:** Online RL pahalı ve kararsız olabilir. Text-to-SQL'de bir cevabın doğru olup olmadığı SQL'i çalıştırarak bedavaya anlaşılır, bu yüzden doğru ve yanlış cevaplardan tercih çifti kurmak kolaydır. [DPO](00_terimler.md#dpo-ve-preference-optimization), aynı soruya verilmiş iyi (chosen) ve kötü (rejected) cevap çiftinden öğrenir: iyisinin olasılığını artırır, kötüsününkini azaltır. Eğitim sırasında rollout ya da ortam gerekmez. Soru, bunun RL kadar iyi sonuç verip vermediği.

**Ne yaptılar:**
1. Modeller LLaMA-3.1-70B ve Qwen2.5-Coder-32B base (önce genel talimat verisiyle eğitilmiş).
2. SFT: GPT-4o'ya gold SQL gösterilmeden soru başına 32'ye kadar CoT çözümü örneklenir. Sonucu gold ile eşleşenler tutulur (~5.6K BIRD, ~6.1K Spider). lr 1e-5, 2 epoch.
3. Off-policy DPO: Aynı soruda GPT-4o'nun doğru (chosen) ve yanlış (rejected) çözümleri eşlenir. Aralarında edit distance'ı (metin farkı) en büyük olan çiftler seçilir. lr 1e-6.
4. On-policy DPO: Modelin kendi 32 örneği execution ile doğrulanır. Bu kez edit distance'ı en küçük doğru/yanlış çiftler seçilir: neredeyse aynı iki cevaptan biri doğru, biri yanlış, fark tam hatanın olduğu yerde. Örnek: `WHERE year >= 2020` (doğru) ile `WHERE year > 2020` (yanlış). İki tur yapılır.

**Sonuç:** Yazarların raporuna göre BIRD dev (70B): SFT 58.14, off-policy DPO 66.30 (+8.16), on-policy DPO 68.51 (+2.21). BIRD test 68.53; Qwen-32B ile 68.25. Ablation:
- CoT'suz DPO yalnızca ~2.6 puan kazandırıyor; kazancın çoğu CoT ile DPO'nun birleşiminden geliyor.
- Off-policy turu atlanıp hep on-policy yapılınca 66.30–67.08.
- Turlar arttıkça geçerli çift havuzu küçülüyor; çift kurmak için aynı soruda hem doğru hem yanlış cevap gerekiyor.

**Bizim için:** Experience log'da aynı sorunun doğru ve yanlış cevapları zaten var. Online RL'den önce bunlardan DPO çiftleri kurmak Mac'te çok daha ucuz bir ilk adım.

### OmniSQL: Synthesizing High-quality Text-to-SQL Data at Scale (Renmin University, ByteDance, Mart 2025) — [2503.02240](https://arxiv.org/abs/2503.02240)

**Tek cümlede:** 16K+ sentetik veritabanında 2.5M örnek (SynSQL-2.5M) üretip yalnızca SFT ile 7B/14B/32B modeller eğitiyorlar; sonraki RL çalışmalarının çoğu bu veriyi ya da bu checkpoint'leri kullanıyor.

**Problem:** BIRD ve Spider train birkaç bin soru ve birkaç yüz veritabanı içerir; çeşitlilik az. Elle yeni Text-to-SQL verisi hazırlamak pahalı. Yazarlar büyük ölçekte, otomatik ve kaliteli veri üretmenin yolunu arıyor.

**Ne yaptılar:**
1. Veritabanı üretimi: Web tablolarından LLM ile veritabanı tasarlanır ve zenginleştirilir (16K+ veritabanı).
2. SQL üretimi: 4 zorluk seviyesinde SQL üretilir. Hatalı ya da zaman aşımına uğrayanlar atılır, şablon başına tek sorgu tutulur. ~5M'den ~2.5M kalır.
3. Soru üretimi: Her SQL için 9 farklı üslupta soru yazılır. Adaylar arasından anlamsal merkeze (bütün adayların ortalama anlamına) en yakını seçilir.
4. CoT üretimi: Her örnek için 8 CoT çözümü üretilir; execution sonucuna göre majority vote ile biri seçilir.
5. Eğitim: Qwen2.5-Coder-Instruct; SynSQL-2.5M + CoT eklenmiş Spider/BIRD train. Girdi: CREATE TABLE ifadeleri + açıklamalar + sütun başına 2 örnek değer + soruyla ilgili değerler + soru. Batch 512, 2 epoch, cosine lr takvimi, lr 2e-5 (7B).

**Sonuç:** Yazarların raporuna göre BIRD dev greedy / majority: 7B 63.9 / 66.1, 32B 64.5 / 67.0. Ablation (7B; taban model 50.9):
- yalnız SynSQL: 59.9 (+9.0)
- CoT eklenmiş Spider+BIRD: 59.6; CoT'suz 55.1, yani CoT tek başına +4.5
- tam karışım: 63.9 (+13.0)
- veri %20'den %100'e çıktıkça düzenli artış

**Bizim için:** Gold SQL'lere CoT eklemek tek başına +4.5 kazanç. SynSQL, BIRD dışı ek RL/SFT sorusu için hazır bir havuz; ama kullanıcı kararıyla BIRD dışı veri kullanılmıyor.

---

## Diğer agentic çalışmalar

Bu gruptaki çalışmalar SQL dışındaki görevlerde (matematik için kod çalıştırma, web arama, yazılım düzeltme, müşteri hizmetleri) tool kullanan agent'ları eğitiyor. Görev farklı olsa da reçeteler (cold start, loss masking, distillation, veri seçimi, çöküşü önleme) doğrudan bizim agent'ımıza taşınabiliyor.

### When Credit Turns Against Tools: Transition-Aware Credit Assignment in Agentic RL (Hong Kong Baptist University (Bo Han grubu), PKU, SJTU, Kasım 2026) — [2611.11330](https://arxiv.org/abs/2611.11330)

**Tek cümlede:** Multi-turn GRPO'da doğruluk önce artıp sonra düşerken tool başarısının da düştüğünü gösteriyor, nedenini credit assignment'ta bulup TACA adlı bir düzeltme öneriyorlar.

**Problem:** Agentic RL eğitiminde bir noktadan sonra model tool'u daha az ve daha kötü kullanmaya başlıyor, doğruluk da düşüyor. Yazarlara göre neden, reward'ın tool çağrılarına haksız yere ceza olarak yansıması.

**Ne yaptılar:**
1. Teşhis, üç neden:
   - Yanlış trajectory'lerde tur başına daha çok tool token'ı var. Bu yüzden tool çağrılarının toplam kredisi negatif oluyor; model kabaca "tool çağırmak kötü" sonucunu çıkarıyor.
   - Token-mean toplama (loss'u bütün token'ların ortalaması olarak almak) uzun trajectory'lere daha çok ağırlık veriyor; uzun olanların çoğu da yanlış.
   - Bir execution hatasından sonraki yeniden deneme çağrıları da son reward ile cezalanıyor.
2. Çözüm, TACA (Transition-Aware Credit Assignment):
   - Tool-call token'larının grup içindeki ortalama advantage'ı negatif olmayacak şekilde kaydırılır.
   - Aynı soruda tool'lu ve tool'suz cevap karşılaştırılır; "tool çağırayım mı" karar token'larının advantage'ı buna göre ayarlanır.
   - Önceki doğru trajectory'lerdeki tool çağrıları supervised replay ile tekrar öğretilir (likelihood loss: bu çağrıların olasılığını artıran SFT benzeri bir terim).

**Sonuç:** Yazarların raporuna göre (her satırda solda TACA'sız, sağda TACA'lı sonuç):
- Qwen2.5-1.5B-Instruct matematik: 28.63 → 33.24 (+4.61)
- 3B matematik: 39.90 → 43.51 (+3.61)
- TACO (programlama problemleri): 41.98 → 53.70
- WebShop (simüle bir alışveriş sitesinde istenen ürünü bulma): 56.8 → 67.2

Her bileşen ~2.7–3.0 puan katkı veriyor.

**Bizim için:** Küçük modelde RL sırasında `search_values`/`execute_sql` kullanımının düşmesi beklenen bir risk. Doğru trajectory'lerin tool çağrılarını replay etmek ucuz bir önlem.

### Multi-Turn On-Policy Distillation with Prefix Replay / ReOPD (Microsoft Research, University of Amsterdam, Temmuz 2026) — [2607.04763](https://arxiv.org/abs/2607.04763)

**Tek cümlede:** Agent'lar için on-policy distillation'ı ortama hiç gitmeden yapıyorlar: önek ve observation'lar büyük modelin kayıtlı trajectory'sinden, yalnızca denetlenen adımın eylemi küçük modelden geliyor.

**Problem:** [On-policy distillation (OPD)](00_terimler.md#on-policy-distillation-opd)'de küçük model kendi token'larını üretir, büyük model her token'a log-prob ile not verir, küçük model bu notlara göre güncellenir. Agent'larda bu pahalıdır: küçük modelin her rollout'u için ortamı (Python, arama motoru) gerçekten çalıştırmak gerekir. Yazarlar ortamı hiç çağırmadan aynı faydayı almanın yolunu arıyor.

**Ne yaptılar:**
1. Modeller: küçük model Qwen3-4B-Instruct-2507 (bir ayarda 8B). Büyük model 4B, 8B ya da 30B-A3B; önce SFT cold start + GRPO ile eğitilmiş. Burada "büyük" model aynı boyda da olabiliyor; fark, onun bu görevde daha iyi eğitilmiş olması.
2. Ortamlar: Python tool'lu matematik (ReTool cold start verisi, 6.4K DAPO prompt'u) ve Search-R1 arama ortamı.
3. Prefix replay: Büyük modelin kayıtlı bir trajectory'si bir adıma kadar alınır (önceki eylemler + observation'lar). Küçük model yalnızca o adımın eylemini üretir; büyük model bu eylemi token token puanlar. Ortam çağrılmaz.
4. "Prefix trap": Önek küçük modelin kendi davranışına benzedikçe büyük model güvenilmez geçmişlere düşüyor. Çözüm olarak erken adımlar daha sık örnekleniyor: t. adımın seçilme ağırlığı κ^t (κ=0.6), yani her sonraki adım bir öncekinin 0.6 katı sıklıkta seçiliyor.
5. Altyapı: Slime, 8×H100, ~3 saat.

**Sonuç:** Yazarların raporuna göre matematik ortalaması (4B büyük model ile): SFT 46.1, OPD 55.1, ReOPD 57.2; karşılaştırma olarak büyük modelin GRPO sonucu 55.5. Search'te ReOPD, OPD ile eşit (40.5'e karşı 40.6).
- Küçük model eğitiminde sıfır tool call; OPD'den en az 4 kat hızlı.
- Daha büyük ya da daha güçlü modellerin önekleri küçük modeli kötüleştiriyor.
- Büyük modelin kendi RL eğitimi sırasında topladığı rollout'lar bedavaya yeniden kullanılabiliyor.

**Bizim için:** Büyük modelin experience log'daki trajectory'leri, ortamı (SQLite) tekrar çalıştırmadan distillation'a girdi olabilir. Ama OPD için büyük modelin token log-prob'ları gerekiyor; API'den alınamıyorsa yerel model şart.

### Building Multi-Task Agentic LLMs via Two-Phase Distillation (Tsinghua University, Ant Group, Haziran 2026) — [2606.30044](https://arxiv.org/abs/2606.30044)

**Tek cümlede:** Her görev için ayrı RL ile eğitilmiş uzman modelleri (expert) tek modelde birleştirmenin yollarını karşılaştırıyorlar: off-policy SFT distillation, on-policy distillation, parametre birleştirme ve multi-task RL.

**Problem:** Bir görevde RL ile eğitilmiş model başka bir görevde iyi olmayabilir. Birden çok görevde iyi tek bir agent için ya hepsini birlikte RL ile eğitmek ya da ayrı uzmanları birleştirmek gerekir. Hangisinin en iyi olduğu açık değil.

**Ne yaptılar:**
1. Modeller Qwen3-8B ve Qwen3-30B-A3B-Thinking-2507 ([thinking mode](00_terimler.md#thinking-mode): cevaptan önce uzun düşünen sürüm).
2. Görevler: τ²-bench (simüle bir müşteriyle konuşup tool'larla işlem yapan müşteri hizmetleri agent'ı; airline ve telecom alanları; burada RL'den önce SFT yapılmış) ve GEM oyunları (sudoku, mastermind).
3. Faz 1, off-policy distillation ([birden çok modelden distillation](00_terimler.md#multi-teacher-distillation-mopd): birden çok uzman modelin bilgisini tek modele aktarma): Uzmanların kendi RL prompt'larında ürettiği rollout'lar birleştirilip SFT yapılır (8B'de görev başına 128×400 örnek).
4. Faz 2, on-policy distillation: Faz 1 modelinden başlanır. Model kendi rollout'unu üretir; her token için uzmana göre reverse-KL reward'ı alır. γ=0, yani her token yalnızca kendi puanını alır, sonraki token'ların puanı eklenmez. 16 prompt × 16 rollout, 10–30 adım.
   - Forward-KL (SFT'nin yaptığı): model uzmanın yapabildiği her şeyi kapsamaya çalışır; birden çok farklı strateji varsa aralarında bulanık bir ortalamaya düşebilir.
   - Reverse-KL (on-policy'nin yaptığı): model kendi ürettiği şeyin uzmanca da olası olmasını ister; tek bir iyi stratejiye odaklanır.

**Sonuç:** Yazarların raporuna göre iki fazlı model telecom'da RL uzmanını geçiyor: pass^4 (aynı görevi 4 denemenin dördünde de çözme oranı) 69.4'e karşı 67.8. Sudoku +7.3, mastermind +4.4.
- Yalnız off-policy distillation'da düşüş var; yazarlar bunu forward-KL'nin birçok davranış modunu ortalamasına bağlıyor.
- Yalnız on-policy (SFT modelinden başlatılınca) telecom'da 58.3'e düşüyor.
- Parametre birleştirme ([model merging](00_terimler.md#model-merging): averaging, task arithmetic, DARE gibi ağırlıkları ortalayan ya da farklarını toplayan yöntemler) çok kötü.
- Off-policy warm start'lı multi-task RL kararsız.

**Bizim için:** Birden çok kaynaktan (ör. büyük model ve kendi doğru rollout'larımız) gelen trajectory'leri tek SFT'de karıştırmak modları ortalayabilir. SFT'den sonra kısa bir on-policy aşaması bunu düzeltiyor.

### PACT: Privileged Trace Co-Training for Multi-Turn Tool-Use Agents (Georgia Tech, Ohio State, UPenn, Haziran 2026) — [2606.16215](https://arxiv.org/abs/2606.16215)

**Tek cümlede:** Büyük model trajectory'lerini rollout sırasında ipucu olarak vermeden, yalnızca optimizasyonda (RL'in yeniden puanlanması ve parça parça SFT) kullanıyorlar.

**Problem:** Büyük modelin doğru trajectory'leri değerli ama nasıl kullanılacağı açık değil. "Privileged trace", eğitimde var olan ama test sırasında olmayan bilgidir; burada büyük modelin doğru çözümü. Yazarlar bu bilgiyi küçük modelin rollout'larına karıştırmadan, yalnızca loss'ta kullanmayı deniyor.

**Ne yaptılar:**
1. Modeller Qwen3-1.7B/4B. Veri: FTRL eğitim prompt'larından 2,099 doğrulanmış örnek. Trajectory'ler çoğunlukla Qwen3-235B'den, kapsam için xLAM-32B'den de; hepsi execution ile doğrulanmış.
2. Rollout: Soru başına 8 rollout, yalnızca prompt ile (ipucu yok); temperature 1.0, en fazla 10 tur.
3. Yeniden puanlama: Aynı rollout'lar, büyük modelin trajectory'si önek olarak verilerek bir kez daha puanlanır (clipped GRPO benzeri bir amaçla).
4. Bileşen bazlı SFT: Yalnızca reasoning öneklerine ve tam tool-call span'lerine (bir tool çağrısının bütün metni) uygulanır. Tool observation'ları bağlamda kalır ama loss'tan maskelenir. Eğitim boyunca reasoning önekleri uzundan kısaya iner; tool-call ağırlığı 0.8'den 0.2'ye azaltılır.
5. Loss = RL + 0.1 × SFT. Prompt'ların %40'ında düz RL yapılır.
6. Reward: referans tool çağrılarıyla eşleşme (tool adı, argument key, argument value) + final cevap F1'i (cevap kelimelerinin referansla örtüşmesi). Advantage hem trajectory hem tur düzeyinde.
7. lr 1e-6, batch 256, 24 update.

**Sonuç:** Yazarların raporuna göre değerlendirme setlerinin ortalamasında Qwen3-4B 35.80 (önceki en iyi yöntem MatchTIR 32.66, +3.14), 1.7B 23.08 (20.96, +2.12). SFT, GRPO, SFT sonra MatchTIR ve on-policy self-distillation'ı geçiyor. SFT, trace-conditioned RL ile birleşince tek başına olduğundan daha çok yardım ediyor.

**Bizim için:** Büyük model trajectory'lerini ayrı bir SFT aşaması yerine RL loss'una küçük bir SFT terimi (0.1) olarak eklemek, 0.8B–4B'de SFT ile RL'i tek aşamada birleştirmenin bir yolu.

### SOD: Step-wise On-policy Distillation for Small Language Model Agents (Tencent LLM Department, Zhejiang University, USTC, NUS, Mayıs 2026) — [2605.07725](https://arxiv.org/abs/2605.07725)

**Tek cümlede:** 0.6B/1.7B tool kullanan agent'larda düz OPD'nin, hatalı tool call'ların sonraki adımlara yayılmasıyla bozulduğunu gösterip distillation gücünü adım adım ayarlıyorlar.

**Problem:** Küçük model bir adımda hatalı tool call yaparsa, sonraki adımlar o hatalı sonuç üzerinde ilerler. Büyük model böyle yabancı bir durumdaki adımlara yanıltıcı notlar verebilir. Düz OPD bütün adımlara aynı ağırlıkla bakar.

**Ne yaptılar:**
1. Modeller: küçük model Qwen3-0.6B/1.7B; büyük model GRPO ile eğitilmiş Qwen3-4B (ölçek testi için 14B).
2. Veri: 3K örneklik SFT warm start; ardından matematik, kod ve bilimden ~30K prompt; Python tool.
3. Sapma skoru: Her reasoning adımı için küçük ve büyük modelin log-prob farkından bir skor hesaplanır; küçük modelin büyük modelden ne kadar uzaklaştığını gösterir.
4. Adım ağırlığı: Ardışık adımların skor oranından hesaplanır (en fazla 1+δ). Sapması artan adıma daha az, toparlanan adıma daha çok ağırlık verilir. Örnek: model 3. adımda yoldan çıktıysa 4. adımdaki büyük model notuna daha az güvenilir; 5. adımda yola dönüyorsa o adım daha güçlü öğrenilir.
5. Loss = GRPO (seyrek outcome reward) + adım ağırlıklı OPD. 8×H20 GPU.

**Sonuç:** Yazarların raporuna göre 0.6B AIME25'te (AIME: Amerikan lise matematik yarışması soruları, burada 2025 sınavı) 26.13. 1.7B ortalama 42.98, düz OPD 36.27 (+6.71). SFT, GRPO ve self-distillation varyantlarını geçiyor. Ablation (1.7B):
- bütün adımlara eşit ağırlık: 34.70
- adım OPD'si olmadan: 25.39 (en büyük düşüş)
- GRPO olmadan: 40.78

**Bizim için:** 0.8B ölçeğinde düz OPD tool hatalarında yanıltıcı oluyor. Distillation sinyalini outcome reward'lı GRPO ile birleştirmek ve sapan adımlarda kısmak gerekiyor.

### KARL: Knowledge Agents via Reinforcement Learning (Databricks AI Research, Mart 2026) — [2603.05218](https://arxiv.org/abs/2603.05218)

**Tek cümlede:** Vector search (belgeleri embedding'e çevirip soruya anlamca en yakınları bulan arama) tool'lu bir kurumsal arama agent'ı; sentetik veri üretimini, off-policy RL'i ve multi-task RL'i, tek-görev uzmanlarını distill etmekle karşılaştırıyorlar.

**Problem:** Kurumsal belgelerde arama yapan agent'lar için hazır eğitim verisi yok. Ayrıca birden çok görevde iyi bir agent için uzmanları distill etmenin mi yoksa hepsini birlikte RL ile eğitmenin mi daha iyi olduğu bilinmiyor.

**Ne yaptılar:**
1. Model GLM 4.5 Air.
2. Veri üretimi:
   - Bir sentezleyici agent korpusu arayıp kaynaklı soru-cevap üretir; tekrarlar atılır.
   - Çözücü agent'ların hep ya da hiç çözemediği sorular atılır; belirsiz ya da yanlış cevaplı sorular da atılır.
   - Her iyileşen agent bir sonraki turun verisini üretir ([expert iteration](00_terimler.md#expert-iteration) benzeri bir döngü).
3. RL: OAPL; iteratif, büyük batch'li, off-policy bir yöntem, amaç fonksiyonu least-squares (kare hata) biçiminde. En fazla 3 iterasyon.
4. Context sıkıştırma: Bağlam belli bir eşiği aşınca model kendi geçmişini sıkıştırır; bu davranış da RL ile eğitilir.
5. Multi-task: BrowseComp-Plus (zor web arama sorularının sabit bir belge koleksiyonu üzerindeki sürümü) ve TREC-Biogen (biyomedikal sorulara kaynaklı cevap üretme) loss'ları token dengesiyle birleştirilir.

**Sonuç:** Yazarların raporuna göre KARL 58.9; paralel test-time compute ile (aynı soruya birden çok çözüm üretip birleştirmek) 68.1.
- RL ile eğitilen tek-görev uzmanlarını SFT ile tek modele distill etmek, in-distribution'da (eğitim görevlerine benzer sorularda) multi-task RL kadar iyi.
- Ama out-of-distribution'da (yeni tür sorularda) distill edilmiş model paralel test-time compute'tan neredeyse kazanç almıyor (59.4 → 59.6); multi-task RL ile eğitilen model artmaya devam ediyor.
- Context sıkıştırması kaldırılınca BrowseComp-Plus 0.570'ten 0.389'a düşüyor.

**Bizim için:** SFT distillation in-distribution için yeterli olabilir, ama genelleme ve self-consistency kazancı için RL aşaması gerekli. "Hep ya da hiç çözülen soruyu at" filtresi burada da var.

### SkyRL-Agent: Efficient RL Training for Multi-turn LLM Agent (UC Berkeley NovaSky, Anyscale, Kasım 2025) — [2511.16108](https://arxiv.org/abs/2511.16108)

**Tek cümlede:** Uzun multi-turn agent'lar için bir RL çerçevesi; bununla Qwen3-32B'den saf RL ile bir yazılım mühendisliği (SWE) agent'ı eğitiyorlar.

**Problem:** Yazılım hatası düzelten agent'lar onlarca adım çalışır; her rollout uzun ve pahalıdır. Böyle agent'ları RL ile verimli eğitmek için hem altyapı hem de doğru tool tasarımı gerekir.

**Ne yaptılar:**
1. Veri: R2E-Gym'den 4.5K görev (testleri olan gerçek kod deposu hata düzeltme görevleri).
2. RL ayarı: tam on-policy; görev başına 8 rollout. Leave-one-out advantage: bir rollout'un reward'ından diğer 7'sinin ortalaması çıkarılır; std ve uzunluk normalizasyonu yok. KL ve [entropy](00_terimler.md#entropy-ve-entropy-collapse) loss'u (entropy: modelin sıradaki token konusunda ne kadar kararsız olduğu) kapalı, lr 1e-6.
3. Sınırlar: 32K context ve 50 adım. Bu sınıra takılan trajectory'ler gradient'e girmez ama reward'ları korunur.
4. Tool tasarımı:
   - AST tabanlı bir kod arama tool'u; sonuçların sonunda sıradaki sorgu için ipucu.
   - Tool hatası, kalan adım/context budget'ı ve geçersiz tool call için kurtarma ipuçları.
   - Yalnızca bash tool'uyla çözülemeyen görevlerin oranı çok yüksek; tool tasarımı bu yüzden önemli.

**Sonuç:** Yazarların raporuna göre SWE-Bench Verified'da (gerçek GitHub hatalarını düzeltip testleri geçirme; insanlarca doğrulanmış görevler) 24.4'ten 39.4'e (+15.0). Maliyet 4,601 H100 saati, DeepSWE'nin (benzer bir açık SWE agent çalışması) yaklaşık yarısı. Async pipeline 1.55 kat hızlı.

**Bizim için:** Tool çıktısının sonuna eylem ipucu ve kalan budget eklemek (bizde `add_budget_note` ve `search_values` hatırlatması) RL'de de değerli. Sınıra takılan trajectory'leri loss'tan çıkarmak basit bir koruma.

### Tongyi DeepResearch Technical Report (Alibaba Tongyi Lab, Ekim 2025) — [2510.24701](https://arxiv.org/abs/2510.24701)

**Tek cümlede:** Qwen3-30B-A3B-Base'den başlayıp agentic mid-training + SFT + on-policy RL ile uçtan uca eğitilmiş açık bir deep-research (çok adımlı web araştırması yapan) agent.

**Problem:** Açık modeller uzun, çok adımlı web araştırması görevlerinde kapalı modellerin gerisinde. Yazarlar bütün eğitim zincirini, ön eğitim sonrasından RL'e kadar, agent davranışına göre kurmayı deniyor.

**Ne yaptılar:**
1. Agentic [mid-training](00_terimler.md#mid-training) (ön eğitim ile post-training arasında, büyük ölçekli ek eğitim): agent davranışı verisiyle (soru sentezi, planlama, karar eylemleri, ölçeklenmiş simüle ortamlardan function-calling) iki aşamalı continual pre-training; bağlam 32K'dan 128K'ya.
2. SFT cold start: Sentetik soru-cevaplardan açık modellerin ürettiği, rejection sampling ile süzülmüş trajectory'ler. ReAct ve context-management biçimleri. Önce 40K, sonra 128K bağlam.
3. RL: GRPO tabanlı, token-level policy gradient, clip-higher, tam on-policy.
   - Reward yalnızca 0/1 doğruluk. Format SFT'de öğrenildiği için format reward'ı yok.
   - Uzunluk sınırına takılıp cevap veremeyen negatifler loss'tan çıkarılıyor; filtresiz negatifler çöküşe yol açabiliyor.
4. Veri seçimi ([curriculum](00_terimler.md#curriculum): soruların zorluğunu eğitim boyunca ayarlamak):
   - SFT modelinin hep çözdüğü ya da hiç çözemediği sorular atılıyor.
   - Reward duraksayınca aktif set yenileniyor: çözülenler atılıyor, havuzdan daha zorları ekleniyor.
5. Ortam: Önce Wikipedia tabanlı offline simüle ortamda deneniyor; sonra önbellekli, hata olunca tekrar deneyen (retry'lı) gerçek sandbox'ta.
6. Son adımda aynı taban modelden eğitilmiş varyantlar model merging ile birleştiriliyor.

**Sonuç:** Yazarların raporuna göre:
- HLE (Humanity's Last Exam: uzman düzeyinde çok zor sorular): 32.9
- BrowseComp (internette bulunması çok zor bilgileri arama): 43.4
- GAIA (web ve tool gerektiren genel asistan görevleri): 70.9
- xbench-DeepSearch (derin arama görevleri): 75.0

Yazarlara göre agentic RL'in başarısı algoritmadan çok verinin kalitesine ve ortamın kararlılığına bağlı.

**Bizim için:** RL verisini sürekli "ne hep çözülen ne hiç çözülemeyen" sorulara göre tazelemek ve kesilmiş ya da bozuk negatifleri loss'tan çıkarmak, küçük modelde çöküşü önlemenin ucuz yolu.

### AEPO: Agentic Entropy-Balanced Policy Optimization (Renmin University, Kuaishou; ARPO ekibi, Ekim 2025) — [2510.14545](https://arxiv.org/abs/2510.14545)

**Tek cümlede:** ARPO'nun (aşağıda) entropiye göre dallanan rollout yönteminin iki sorununu düzeltiyorlar.

**Problem:** ARPO, tool sonucundan sonra modelin kararsızlaştığı (entropinin yükseldiği) noktalarda rollout'u dallandırır. Bunun iki sorunu var:
- Aynı trajectory'ler art arda dallanıyor ve rollout bütçesi birkaç yolda tükeniyor.
- Yüksek entropili token'ların gradient'i clip ile kesiliyor; yani tam öğrenilmesi gereken kararsız noktalar öğrenilmiyor.

**Ne yaptılar:**
1. Rollout bütçesi: Sorunun entropisi ile ortalama tool-call entropisi karşılaştırılır. Buna göre bütçenin ne kadarının baştan (global) üretilen örneklere, ne kadarının dallanmaya gideceği önceden belirlenir.
2. Art arda yüksek entropili dallanmaya ceza verilir.
3. Optimizasyon: Yüksek entropili token'larda clip teriminde stop-gradient kullanılır; değer kırpılır ama gradient (1+ε_h ölçeğinde) korunur.
4. Advantage, token'ın entropisine göre ölçeklenir.

**Sonuç:** Yazarların raporuna göre ~1K eğitim örneğiyle Qwen3-14B'nin Pass@1'i (tek denemede doğru oranı): GAIA 47.6, HLE 11.2, WebWalkerQA (web sitelerinde gezinerek bilgi bulma) 43.0. Karşılaştırma için ARPO makalesi aynı modelde GAIA'da 43.7 raporluyor (ayrı makalelerin rakamları). 14 veri setinde 7 RL baseline'ını geçiyor. Entropi daha kararlı; bazı baseline'ların yaklaşık yarısı kadar tool call yapıyor.

**Bizim için:** Tool sonucundan sonraki belirsiz token'lar en çok öğrenilecek yer. Ama bu yöntem dallanan rollout altyapısı istiyor; Mac ölçeğinde ikinci öncelik.

### AgentScaler: Towards General Agentic Intelligence via Environment Scaling (Alibaba Tongyi Lab, Eylül 2025) — [2509.13311](https://arxiv.org/abs/2509.13311)

**Tek cümlede:** Function-calling (tool çağırma) için binlerce simüle ortamı otomatik kuruyorlar; her ortamda tool'lar bir veritabanını okuyan ya da yazan Python kodu.

**Problem:** Tool kullanan agent eğitmek için çok çeşitli ve doğrulanabilir ortam gerekir. Gerçek API'lerle bunu ölçeklemek zor ve pahalı. Tool'lar bir veritabanı üzerinde çalışan kod olarak simüle edilirse, görevin başarılı olup olmadığı veritabanının son durumuna bakılarak doğrulanabilir.

**Ne yaptılar:**
1. Tool havuzu: ToolBench, API-Gen ve iç kaynaklardan 30K+ API.
2. Domain'ler: Parametre benzerliğinden bir tool bağımlılık grafiği kurulur. Louvain algoritması (bir grafiği sıkı bağlı topluluklara bölen yöntem) ile 1,000+ domain çıkarılır. Her domain'e bir veritabanı şeması verilir.
3. Görevler: Grafikte yürüyüşle bir tool dizisi ve başlangıç veritabanı durumu seçilir; simüle bir kullanıcı agent'la konuşur.
4. Üç filtre:
   - geçerlilik;
   - son veritabanı durumu gold ile eşleşiyor mu;
   - salt okuma görevlerinde tool çağrıları ve argument'ları birebir eşleşiyor mu.

   Tool hatası içeren ama sonunda hedefe ulaşan trajectory'ler tutulur.
5. İki aşamalı SFT: önce genel, sonra domain'e özgü. Loss yalnızca tool call'larda ve asistan cevaplarında; kullanıcı mesajı ve tool çıktısı maskeli.
6. Modeller Qwen3-4B/8B/30B-A3B. RL yok (ileriye bırakılmış).

**Sonuç:** Yazarların raporuna göre 30B-A3B, τ-bench, τ²-bench (müşteri hizmetleri senaryolarında tool kullanımı) ve ACEBench-en'de (İngilizce tool kullanımı benchmark'ı) 1T (1 trilyon) parametrenin altındaki açık modeller arasında en iyi. 4B, 30B sınıfı modellere yakın. ACEBench-zh'de (Çince sürüm) 4B 43.9'dan 65.6'ya çıkıyor (+21.7).

**Bizim için:** Hatadan kurtulup hedefe ulaşan trajectory'leri SFT'de tutmak (yalnızca kusursuz olanları değil) küçük modele hata düzeltmeyi öğretiyor. Salt okuma görevlerde, bizdeki gibi, son durum yerine sonuç eşleşmesi filtre olur.

### AgentGym-RL: Training LLM Agents for Long-Horizon Decision Making through Multi-Turn RL (Fudan University, ByteDance Seed, Shanghai Innovation Institute, Eylül 2025) — [2509.08755](https://arxiv.org/abs/2509.08755)

**Tek cümlede:** SFT'siz multi-turn RL için birleşik bir çerçeve ve etkileşim ufkunu (izin verilen tur sayısını) eğitim boyunca büyüten ScalingInter-RL yöntemi.

**Problem:** Uzun görevlerde agent'ı baştan çok turla eğitmek kararsız; az turla eğitmek ise bir tavana takılıyor. Yazarlar ikisinin arasını bulan bir takvim öneriyor.

**Ne yaptılar:**
1. Ortamlar: WebArena (gerçekçi web sitelerinde görev yapma), deep search, TextCraft (metin tabanlı eşya üretme oyunu), BabyAI (ızgara dünyada talimat izleme), SciWorld (metin tabanlı bilim deneyi simülasyonu).
2. Modeller Qwen2.5-3B/7B-Instruct. Algoritmalar: PPO, GRPO, RLOO ve REINFORCE++ (son ikisi critic kullanmayan, GRPO'ya benzer policy gradient yöntemleri).
3. Reward: bölüm sonunda 0 ile 1 arası görev tamamlama puanı.
4. ScalingInter-RL: Az turla başla; model bildiğini pekiştirir (exploitation). Sabit adım aralıklarıyla izin verilen en fazla tur sayısını artır; model yeni yollar dener (exploration). Bu, tur sayısı üzerinden bir curriculum.

**Sonuç:** Yazarların raporuna göre sabit kısa ufuk (5 tur) kararlı ama tavana takılıyor; sabit uzun ufuk (10 tur) başta yüksek reward veriyor sonra çöküyor. ScalingInter-7B:
- WebArena 26.00 (GPT-4o 16.00)
- deep search 38.25 (sabit ufuklu AgentGym-RL-7B 34.00, yani ufku büyütmek +4.25)
- BabyAI 96.67
- SciWorld 57.00

**Bizim için:** Tool-call budget'ı (bizde 10) RL'in başında küçük (ör. 4–5) tutup sonra büyütmek basit bir curriculum.

### SimpleTIR: End-to-End RL for Multi-Turn Tool-Integrated Reasoning (Nanyang Technological University, TikTok, Eylül 2025) — [2509.02479](https://arxiv.org/abs/2509.02479)

**Tek cümlede:** Multi-turn tool-integrated reasoning (TIR: modelin düşünürken kod çalıştırması) RL'inin kararsızlığının nedenini "void turn"lerde bulup bu turları içeren trajectory'leri eğitimden süzüyorlar.

**Problem:** Base modeli kod tool'uyla multi-turn RL ile eğitmek sık sık çöküyor. Tool çıktısı modelin kendi üretmediği metindir; dağılım kayması yaratır ve gradient patlamasına yol açar.

**Ne yaptılar:**
1. Model Qwen2.5-7B/32B base, zero RL (SFT olmadan doğrudan RL). Veri: Math3-5 (SimpleRL'in kullandığı, zorluk seviyesi 3–5 olan matematik soruları) ve DeepScaleR.
2. GRPO: 16 rollout, temperature 1.0, clip 0.2/0.28 (clip-higher), lr 1e-6, KL ve entropy terimi yok. Tool çıktısı loss'tan maskeli. Yalnızca son cevap reward'ı.
3. Aşamalı uzunluk: önce 16K token ve 5 tur; cevap uzunluğu doyunca 24K ve 10 tur.
4. Void turn filtresi: Ne kod bloğu ne de final cevap üreten tur, "void turn"dür; model bir şey yazmış ama hiçbir eylem yapmamıştır. Örnek: model "Şimdi hesaplayayım..." yazıp turu kod olmadan bitirir. Void turn içeren bütün trajectory'ler policy update'inden çıkarılır.

**Sonuç:** Yazarların raporuna göre 7B AIME24'te 22.1'den 50.5'e; 32B 59.9. Ablation (AIME24):
- saf multi-turn: 20.8
- düşük olasılıklı token filtresi: 23.3
- yüksek importance-ratio filtresi: 26.3
- void turn'de durdurup filtrelememe: 26.1
- tam SimpleTIR: 50.5

Yani diğer kararlılık çareleri birkaç puan getirirken void turn filtresi farkın çoğunu yaratıyor. SFT'siz eğitim daha çeşitli davranış veriyor: hata düzeltme oranı %38.0 (SFT ile başlayan ReTool'da %25.8).

**Bizim için:** Bizde "void turn" = okunamayan ya da tool call içermeyen tur. Bunları içeren trajectory'leri RL güncellemesinden çıkarmak tek satırlık, büyük etkili bir koruma.

### rStar2-Agent: Agentic Reasoning Technical Report (Microsoft Research, Ağustos 2025) — [2508.20722](https://arxiv.org/abs/2508.20722)

**Tek cümlede:** 14B modeli Python tool'uyla agentic RL ile eğitip bir haftada, 510 RL adımında AIME'de çok daha büyük modellere yetişiyorlar.

**Problem:** Kod tool'lu RL'de ortam gürültülüdür: model hatalı kod yazıp yine de doğru cevaba ulaşabilir. Yalnızca cevaba bakan reward bu kötü tool kullanımını da ödüllendirir. Yazarlar reward'ı değiştirmeden temiz tool kullanımını öğretmenin yolunu arıyor.

**Ne yaptılar:**
1. Model Qwen3-14B-Base.
2. Reasoning'siz SFT: ~165K function-calling (ToolACE, APIGen-MT, Glaive, Magicoder), 30K Tulu3 talimat, 27K sohbet. Amaç yalnızca format ve tool kullanımı.
3. RL verisi: 100K+ adaydan tamsayı cevaplı 42K matematik problemi; OpenMathReasoning'de Qwen3-32B'nin 16 denemede en az 2 kez doğru bulduğu sorular.
4. Üç aşama:
   - 1. aşama: 42K soru, en fazla 8K token
   - 2. aşama: 42K soru, 12K token
   - 3. aşama: 2. aşama politikasının 8/8 çözdüğü sorular atılmış 17.3K zor soru, 12K token (optimizer sıfırlanır)
5. GRPO-RoC (Resample-on-Correct): Her soru için 32 rollout üretilir ve 16'ya indirilir. Negatifler rastgele seçilir. Pozitifler arasından tool hatası ve format ihlali az olanlar tercih edilir. Böylece reward değişmeden "temiz" doğru cevaplar öğrenilir.
6. Reward yalnızca cevap. KL ve entropy yok, clip-higher 0.2/0.28, lr 1e-6, batch 512 prompt, 10–15 tur. 64 MI300X GPU.

**Sonuç:** Yazarların raporuna göre AIME24 80.6, AIME25 69.8. AIME24'ün aşamalara göre gelişimi: SFT sonrası 3.3, 1. aşama 72.1, 2. aşama 77.0, 3. aşama 80.6. RoC olmadan cevaplar daha kötü ve daha uzun. 510 adımdan sonra eğitim çöküyor.

**Bizim için:** Reward'ı bozmadan, doğru trajectory'ler arasından hatasız tool kullananları seçmek (RoC), küçük modelin gereksiz ya da hatalı `execute_sql` çağrılarını azaltmanın yolu. SFT'nin işi yalnızca formatı öğretmek olabilir.

### Chain-of-Agents: End-to-End Agent Foundation Models via Multi-Agent Distillation and Agentic RL (OPPO AI Agent Team, Ağustos 2025) — [2508.13167](https://arxiv.org/abs/2508.13167)

**Tek cümlede:** Çok agent'lı bir sistemin (OAgents) davranışını tek bir modele distill edip ardından agentic RL ile tool kullanımını iyileştiriyorlar; çıkan modele Agent Foundation Model (AFM) diyorlar.

**Problem:** Çok agent'lı sistemler (planlayıcı, arayıcı, kod yazıcı gibi ayrı LLM rolleri) güçlü ama pahalı ve yavaş. Aynı davranışı tek bir modelde, tek bir trajectory'de toplamak çıkarımı ucuzlatır.

**Ne yaptılar:**
1. Veri dönüşümü: OAgents'in her agent etkinleşmesi, reasoning durumu ve çıktısı tek bir "chain-of-agents" trajectory'sine çevrilir.
2. Filtre:
   - 5'ten az agent-tool etkileşimi olanlar atılır.
   - Yanlış ya da bozuk formatlılar atılır.
   - Reflection (kendi cevabını gözden geçirme) içermeyenler azaltılır.
   - Erken hatayı düzeltenler çoğaltılır.
3. SFT: 16,433 web trajectory'si (8,826 multi-hop QA, yani birkaç bilgiyi birleştirmeyi gerektiren sorular, ve 7,607 web) ve kod agent'ı için ~47K. Tool çıktıları loss'tan maskeli.
4. RL: DAPO (VeRL ile). DAPO, [dynamic sampling](00_terimler.md#dynamic-sampling) (bütün cevapları aynı reward'ı alan, sinyal vermeyen grupları atıp yenileriyle doldurmak) ve clip-higher kullanan bir GRPO varyantı.
   - Web: prompt başına 8 rollout, en fazla 24 adım / 32K token, Qwen2.5-72B judge ile ikili reward. Taban modelin pass rate'i 0.3'ü aşan sorular (kolaylar) atılır.
   - Kod: reward = doğruluk × format, en fazla 8 tool call. 7B'nin 8/8 çözdüğü sorular atılır.
5. Modeller Qwen2.5-3B/7B/32B-Instruct ve Qwen2.5-Coder-7B/32B.

**Sonuç:** Yazarların raporuna göre 32B web modeli GAIA 55.3, BrowseComp 11.1, HLE 18.0. Kod modeli LiveCodeBench v5 (yarışma programlama soruları) 47.9, AIME25 59.8. Çok agent'lı sisteme göre çıkarım maliyeti %84.6 düşük. 7B kod modelinde SFT ortalama +22.0, RL +20.8 puan kazandırıyor.

**Bizim için:** Bizim küçük model + büyük model + final check sistemimizin tamamının çıktısını (handoff dahil) tek bir küçük model trajectory'sine çevirip SFT verisi yapmak, bu çalışmanın Text-to-SQL karşılığı olur. Hata düzelten trajectory'leri çoğaltmak önemli.

### Agent Lightning: Train ANY AI Agents with Reinforcement Learning (Microsoft Research, Ağustos 2025) — [2508.03680](https://arxiv.org/abs/2508.03680)

**Tek cümlede:** Var olan agent'ları (LangChain, OpenAI Agents SDK, AutoGen ile yazılmış) neredeyse hiç kod değiştirmeden RL ile eğiten, agent'ın çalışmasını eğitimden ayıran bir çerçeve.

**Problem:** Her agent farklı bir framework'le yazılmış. RL kütüphaneleri ise genelde tek bir uzun konuşma dizisi bekliyor. Agent'ı RL'e uydurmak için çoğunlukla baştan yazmak gerekiyor.

**Ne yaptılar:**
1. Agent'ın çalışması bir MDP (Markov karar süreci: durum, eylem, reward zinciri) olarak modelleniyor. Her transition = (LLM girdisi, LLM çıktısı, reward).
2. LightningRL: Bölümün toplam reward'ı (return) transition'lara dağıtılıyor. Mevcut uygulamada her LLM çağrısına aynı değer, yani final return veriliyor. Böylece her çağrı ayrı bir tek turlu örnek gibi işleniyor. Tek turlu GRPO değiştirilmeden çalışıyor; masking ya da uzun dizileri birleştirme gerekmiyor.
3. Tool-call durumundan (ör. başarılı ya da hatalı) otomatik ara reward.
4. Deneyler Llama-3.2-3B-Instruct ile üç görevde:
   - Spider üzerinde LangChain ile Text-to-SQL: 3 agent var, 2'si eğitiliyor; reward final doğruluk.
   - MuSiQue (çok adımlı soru-cevap) üzerinde RAG: reward 0.9 F1 + 0.1 format.
   - Calc-X (hesap makinesi tool'lu matematik).

**Sonuç:** Yazarların raporuna göre üç görevde de reward eğrileri düzenli artıyor. Metinde sayısal sonuç verilmiyor.

**Kaynak notu:** Makale sonuçları yalnızca eğri olarak gösteriyor; bir taban yöntemle karşılaştırılabilecek doğruluk rakamı yok.

**Bizim için:** Her tool call'u aynı final reward ile ayrı bir tek turlu örnek gibi eğitmek, uzun konuşmayı tek dizi olarak işlemeye göre bellek açısından Mac'e daha uygun bir seçenek.

### ARPO: Agentic Reinforced Policy Optimization (Renmin University, Kuaishou, Temmuz 2025) — [2507.19849](https://arxiv.org/abs/2507.19849)

**Tek cümlede:** Tool çağrısından hemen sonra modelin token entropisinin sıçradığını gösterip rollout'u tam bu noktalarda dallandırıyorlar.

**Problem:** GRPO her rollout'u baştan sona bağımsız üretir. Ama asıl belirsizlik tool sonucu geldikten sonradır: model sonucu nasıl yorumlayacağına karar verir. Rollout bütçesini bu noktalarda daha çok alternatif denemeye harcamak daha verimli olabilir.

**Ne yaptılar:**
1. Gözlem: Tool sonucundan sonraki ilk 10–50 token'da entropi sıçrıyor.
2. Entropiye göre dallanma: Toplam M rollout'tan N'si baştan (global) üretilir. Kalan bütçe, entropi artışı bir eşiği aşan tool sonrası noktalarda kısmi dallanmaya harcanır: trajectory o noktadan kopyalanıp farklı devamlar üretilir. SQL'le bir örnek: sorgu sonucu boş geldi ve model kararsız; buradan birkaç farklı devam denenir (biri filtreyi gevşetir, biri değer arar).
3. Soft advantage attribution: Dalların ortak önekindeki token'ların advantage'ı, o önekten çıkan dallar hesaba katılarak verilir.
4. Cold start SFT: Tool-Star'ın 54K örneği + 0.8K STILL matematik. RL: reasoning için 10K Tool-Star, deep search için yalnızca 1K zor örnek.
5. Reward: doğruluk + format (iyi format ama sıfır doğruluk 0, bozuk format −1) + search ve Python'u birlikte doğru kullanırsa 0.1 bonus.

**Sonuç:** Yazarların raporuna göre (solda GRPO, sağda ARPO):
- Qwen2.5-7B ortalama: 56.5 → 58.3 (+1.8)
- Llama3.1-8B: 51.1 → 55.3 (+4.2)
- Qwen3-14B GAIA: 36.9 → 43.7 (+6.8)

GRPO'dan yüksek doğruluğa yaklaşık yarı tool call ile ulaşıyor. Ablation: entropi değeri 0.4'te en iyi; N=8 / M=16 en iyi.

**Bizim için:** RL verisi binlerce soru olmak zorunda değil (deep search'te 1K). Önce SFT ile tool formatı, sonra az sayıda zor soruyla RL.

### WebSailor: Navigating Super-human Reasoning for Web Agent (Alibaba Tongyi Lab, Temmuz 2025) — [2507.02592](https://arxiv.org/abs/2507.02592)

**Tek cümlede:** Belirsizliği yüksek, zor sentetik sorular (SailorFog-QA), kısa bir RFT cold start ve DUPO adlı RL yöntemiyle bir web agent'ı eğitiyorlar.

**Problem:** Mevcut web soru setleri çoğunlukla birkaç aramayla çözülüyor. Birçok adımda ipucu birleştirmeyi gerektiren, çok belirsiz sorular az. Bu tür sorular olmadan agent zor aramayı öğrenemiyor.

**Ne yaptılar:**
1. Soru üretimi: Wikidata'da nadir varlıklardan başlayan rastgele yürüyüşle bir bilgi grafiği kurulur. Bir alt graf seçilir ve tarih, isim gibi ayrıntılar bulanıklaştırılarak soru yazılır. Örnek bir bulanıklaştırma: "1952'de doğmuş" yerine "1950'lerin başında doğmuş".
2. Trajectory: QwQ-32B trajectory üretir. Uzun düşünceler atılır; başka bir model her adım için kısa, eyleme dönük bir düşünceyi yeniden yazar.
3. RFT cold start (rejection sampling fine-tuning: yalnızca doğru çıkan trajectory'lerle SFT): Yalnızca doğru, 32K token'dan kısa ve 5'ten fazla tool call içeren trajectory'ler; 2K'dan biraz fazla örnek. Observation token'ları loss'tan maskeli.
4. DUPO (RL):
   - Çok kolay sorular eğitimden önce atılır.
   - Eğitimde sıfır varyanslı gruplar (bütün rollout'ları aynı reward'ı alan, bu yüzden sinyal vermeyen gruplar) çıkarılır; batch, varyansı olan örneklerin kopyalarıyla doldurulur.
   - DAPO'nun dynamic sampling'inden (boşluğu yeni rollout üreterek doldurma) 2–3 kat hızlı.
5. Reward: 0.1 format + 0.9 LLM-judge cevap puanı.

**Sonuç:** Yazarların raporuna göre BrowseComp-en/zh (İngilizce ve Çince sürümleri), GAIA ve xbench'te açık agent'ları geçiyor. RFT cold start olmadan yakınsama daha düşük ve model daha az tool call yapıyor.

**Bizim için:** ~2K iyi süzülmüş büyük model trajectory'si cold start için yeterli. Büyük modelin uzun düşüncesini kısa, eyleme dönük düşünceye çevirmek küçük model için önemli.

### Self-Challenging Language Model Agents (Meta FAIR, UC Berkeley, Haziran 2025) — [2506.01716](https://arxiv.org/abs/2506.01716)

**Tek cümlede:** Agent önce tool'ları keşfedip kendine doğrulanabilir görevler yazıyor ([self-play](00_terimler.md#self-play) benzeri: model kendi görevini kendisi üretiyor), sonra bu görevlerde RL ile eğitiliyor.

**Problem:** Tool kullanan agent'lar için doğrulanabilir görev verisi az, elle yazmak da pahalı. Model görevleri kendisi üretebilirse veri sınırı kalkar.

**Ne yaptılar:**
1. Challenger rolü: Model "Code-as-Task" biçiminde bir görev yazar: talimat, doğrulama fonksiyonu (çözümün doğru olup olmadığını kontrol eden kod), örnek çözüm ve başarısız örnekler.
2. Kalite kontrolü: Kod çalıştırıcı yalnızca örnek çözümün doğrulamayı geçtiği ve başarısız örneklerin hiçbirinin geçmediği görevleri tutar. Böylece doğrulama ne bozuk ne de çok gevşek olur.
3. Executor rolü: Model bu görevleri çözer ve 0/1 doğrulama reward'ıyla eğitilir. Ana sonuçlarda yöntem rejection fine-tuning (yalnızca doğru çözümlerle SFT); DPO, PPO ve GRPO ablation'da.
4. İki ayar:
   - distillation: Llama-3.1-70B görev ve trajectory üretir, Llama-3.1-8B-Instruct eğitilir;
   - self-improvement: 8B kendi görevlerini kendisi üretir.

   Ayar başına 800 sentetik görev ve ~12K rollout.

**Sonuç:** Yazarların raporuna göre M3ToolEval (çok adımlı tool kullanımı görevleri) + τ-bench ortalama Pass@1: taban 12.0; distillation ile 32.2, self-improvement ile 23.5.
- Görevlerin ~beşte biri hâlâ hatalı (talimatta gerekli bilgi eksik).
- Kazanç ortama özgü; ortamlar arası ortak eğitim az fayda sağlıyor.
- Sentetik görevler gerçek görevlerin gerisinde.

**Bizim için:** BIRD veritabanlarından büyük modele doğrulanabilir yeni soru–SQL çiftleri ürettirmek (gold SQL'in kendisi doğrulayıcı) RL verisini çoğaltmanın bir yolu. Ama kullanıcı kararıyla BIRD train soruları yeterliyse buna ihtiyaç yok.

### WebDancer: Towards Autonomous Information Seeking Agency (Alibaba Tongyi Lab, Mayıs 2025) — [2505.22648](https://arxiv.org/abs/2505.22648)

**Tek cümlede:** Veri üretimi, trajectory örnekleme, SFT cold start ve DAPO RL'den oluşan dört aşamalı bir web agent reçetesi.

**Problem:** Web'de bilgi arayan agent'lar için hem zor soru hem de kaliteli trajectory verisi az. Yazarlar ikisini de üretip eğitimi aşamalara bölen tam bir reçete sunuyor.

**Ne yaptılar:**
1. Soru verisi: crawlQA (~60K; gezilen web sayfalarından üretilmiş) ve e2hQA (~40K; basit soruları adım adım zorlaştırarak, "easy to hard").
2. Trajectory: Rejection sampling ile (N=5, her soru için 5 deneme) search ve visit tool'larını kullanan ReAct trajectory'leri. Kısa CoT GPT-4o'dan, uzun CoT (reasoning modellerinin binlerce token'lık düşüncesi) QwQ-Plus'tan. Geçerlilik, doğruluk ve kalite (tekrar sınırı) filtresi uygulanır.
3. SFT: tool observation'ları loss'tan maskeli.
4. RL: DAPO; reward 0.1 format + 0.9 LLM-judge.

**Sonuç:** Yazarların raporuna göre GAIA'da QwQ-32B 51.5 (düz ReAct 37.8, +13.7), Qwen2.5-7B 31.0 (düz ReAct 18.4, +12.6). WebWalkerQA 47.9.
- Az veride filtrelenmiş veri filtresizden iyi.
- QwQ'da RL tek başına GAIA'da ~%5 Pass@3 (3 denemeden en az biri doğru).
- Uzun CoT küçük instruct modellere kötü aktarılıyor; geçersiz çıktı artıyor.

**Bizim için:** 0.8B–4B için büyük modelin kısa CoT'lu trajectory'leri seçilmeli; uzun reasoning trajectory'leri küçük modeli bozabilir.

### ZeroSearch: Incentivize the Search Capability of LLMs without Searching (Alibaba Tongyi Lab, Mayıs 2025) — [2505.04588](https://arxiv.org/abs/2505.04588)

**Tek cümlede:** RL'de gerçek arama motoru yerine SFT ile eğitilmiş bir LLM'i arama simülatörü olarak kullanıp belge gürültüsünü curriculum ile artırıyorlar.

**Problem:** Arama agent'ını RL ile eğitmek binlerce gerçek arama API çağrısı gerektirir. Bu pahalıdır ve gelen belgelerin kalitesi kontrol edilemez.

**Ne yaptılar:**
1. Simülatör: Gerçek arama trajectory'leri LLM-judge ile faydalı ya da gürültülü diye etiketlenir, bir LLM bunlarla SFT edilir. Prompt'taki bir anahtar kelime hangi tür belge (faydalı ya da gürültülü) üretileceğini seçer. Varsayılan simülatör Qwen2.5-14B-Instruct.
2. Curriculum rollout: Gürültülü belge olasılığı eğitim boyunca üstel bir takvimle artar. Önce model formatı öğrenir, sonra zor retrieval'ı (gürültü içinde doğru bilgiyi bulmayı).
3. Algoritmalar: REINFORCE (en iyi), GRPO ve PPO.
4. Reward: F1 (cevap kelimelerinin doğru cevapla örtüşmesi). EM (birebir eşleşme) uzun cevabı teşvik ettiği için kullanılmıyor. Format reward'ı yok.
5. Simüle belge token'ları loss'tan maskeli; maske kaldırılınca 36.07'den 34.53'e düşüyor.

**Sonuç:** Yazarların raporuna göre gerçek Google aramasıyla eğitilen Search-R1'i geçiyor: Qwen2.5-7B-Base'de 40.93'e karşı 39.51. Maliyet: 64K sorguda Google API ~$586.7, 14B simülatör ~$70.8; yani ~8 kat ucuz.

**Bizim için:** Ortam gürültüsünü (bizde `search_values`'ın döndürdüğü yanlış adaylar) eğitim boyunca artırmak bir curriculum seçeneği. Observation maskesi burada da ölçülmüş bir kazanç.

### RAGEN: Understanding Self-Evolution in LLM Agents via Multi-Turn RL (Northwestern, UW, Stanford, Microsoft, NYU ve diğerleri, Nisan 2025) — [2504.20073](https://arxiv.org/abs/2504.20073)

**Tek cümlede:** Multi-turn agent RL'in tipik çöküşünü ("Echo Trap": modelin tekrar eden, hep aynı kalıptaki reasoning'e kilitlenmesi) tanımlayıp kararlı bir varyant (StarPO-S) öneriyorlar.

**Problem:** Multi-turn RL'de reward bir süre artıp sonra çöküyor. Model çeşitliliğini kaybedip aynı düşünce kalıbını tekrarlıyor. Çöküşü neyin önlediği ve önceden nasıl fark edileceği bilinmiyor.

**Ne yaptılar:**
1. Modeller Qwen2.5-Instruct 0.5B (basit sembolik oyun ve bulmaca ortamları) ve 3B (WebShop).
2. StarPO-S:
   - Belirsizlik filtresi: Prompt'lar, tekrar rollout'larındaki reward std'sine (aynı soruya verilen cevapların reward'larının ne kadar farklı olduğu) göre sıralanır; yalnızca en belirsiz %25'i tutulur.
   - KL yok, clip-higher (0.2/0.28).
   - PPO critic'i bazı ayarlarda GRPO'dan daha düzgün sonuç veriyor.

**Sonuç:** Yazarların raporuna göre belirsizlik filtresi çöküşü geciktiriyor ya da önlüyor.
- Prompt başına 4 cevap en iyi.
- Turda 5–6 eylem en iyi; 7'de bozulma başlıyor.
- Sık ve taze rollout daha iyi genelleşiyor.
- Reasoning'e özgü reward olmadan multi-turn görevlerde reasoning eğitim boyunca kısalıyor.
- Erken uyarı işaretleri: reward std'sinin ve entropinin düşmesi (entropy collapse: modelin hep aynı cevabı vermeye başlaması). Gradient norm'undaki sıçrama ise geri dönülmez çöküşün işareti.

**Bizim için:** 0.8B'de çöküşü izlemek için reward std'si, entropi ve gradient norm'u loglanmalı. RL verisi reward varyansı yüksek sorulardan seçilmeli.

### ReTool: Reinforcement Learning for Strategic Tool Use in LLMs (ByteDance Seed, Nisan 2025) — [2504.11536](https://arxiv.org/abs/2504.11536)

**Tek cümlede:** Kod yorumlayıcıyı reasoning'in içine yerleştirip önce kod içeren SFT, sonra PPO ile tool kullanımını öğretiyorlar.

**Problem:** Metin tabanlı reasoning modelleri uzun hesaplarda hata yapar. Kodu çalıştırıp sonuç almak daha güvenilir; ama modelin kodu ne zaman ve nasıl çağıracağını öğrenmesi gerekir.

**Ne yaptılar:**
1. Modeller Qwen2.5-32B-Instruct (ayrıca DeepSeek-R1-Distill-Qwen-32B).
2. Cold start verisi: Metin tabanlı matematik reasoning verisinde (Open-Thoughts vb.; uzman + DeepSeek-R1 ile süzülmüş) elle yapılan hesap adımları, kod + yorumlayıcı çıktısıyla değiştirilir. Format ve cevap kontrolü yapılır. 2 epoch (veri boyutu verilmemiş).
3. RL: PPO (VeRL), lr 1e-6, en fazla 16,384 token, mini-batch 512, KL 0.
4. Reward: doğru +1, yanlış −1. Kodun çalışıp çalışmadığına reward verilmiyor; amaç [reward hacking](00_terimler.md#reward-hacking)'i (modelin asıl görevi değil, reward'ı kandıran bir kestirmeyi öğrenmesi) azaltmak.
5. Yorumlayıcı feedback token'ları loss'tan maskeli. Hız için KV-cache yeniden kullanımı ve async sandbox havuzu.

**Sonuç:** Yazarların raporuna göre AIME24/25'te 67.0 / 49.3, ~400 adımda. Metin tabanlı RL 1000+ adımda 40.0 / 36.7. Yalnız cold start 40.9. Yani tool'lu RL hem daha yüksek (AIME24'te +27 puan) hem daha az adımda. RL'den sonra:
- cevap uzunluğu ~%40 kısalıyor;
- cevapların ~%98'i kod içeriyor;
- kod daha erken çağrılıyor;
- hatadan sonra kendi kendini düzeltme ortaya çıkıyor.

**Bizim için:** Ara adım çalışabilirliğine reward vermemek (yalnızca final doğruluk) reward hacking'e karşı korunma. Observation maskesi standart.

### ToRL: Scaling Tool-Integrated RL (SJTU, SII, GAIR, Mart 2025) — [2503.23383](https://arxiv.org/abs/2503.23383)

**Tek cümlede:** Base modelden, SFT olmadan, doğrudan RL ile kod tool'u kullanmayı öğretiyorlar.

**Problem:** Tool kullanımı genelde önce SFT ile öğretilir; bu da modeli SFT verisindeki kalıplara bağlar. Yazarlar RL'in tool kullanımını sıfırdan keşfettirip keşfettiremeyeceğini deniyor.

**Ne yaptılar:**
1. Modeller Qwen2.5-Math-1.5B/7B base.
2. Veri: NuminaMATH, MATH ve DeepScaleR'dan ispat soruları ve doğrulaması belirsiz sorular atılınca 75,149 soru. LIMR (örnekleri öğrenmeye katkısına göre seçen bir yöntem) ile dengeli zorlukta 28,740 soru seçilmiş.
3. GRPO (veRL): rollout batch 128, soru başına 16 örnek, KL yok, temperature 1.
4. Tool kuralları: Cevap başına tool call sınırı C (varsayılan 1). Hata mesajı son satırına kısaltılır. Sandbox çıktısı loss'tan maskeli.
5. Reward: doğru +1, yanlış −1. Çalışmayan koda −0.5 cezası denenmiş ama kullanılmamış.

**Sonuç:** Yazarların raporuna göre ToRL-7B AIME24 43.3, AIME25 30.0, matematik setlerinin ortalaması 62.1. C=2 ortalamayı ~2 puan artırıyor ama adım süresi 237'den 288 saniyeye çıkıyor. Çalışabilirlik cezası yardım etmiyor; yazarlara göre aşırı basit kodu teşvik ediyor olabilir.

**Bizim için:** Tool hata mesajını kısaltmak ve hatalı tool call'a ayrı ceza koymamak. Zorluğu dengeli bir alt küme seçmek RL verisini 3'te 1'e indiriyor.

### SWEET-RL: Training Multi-Turn LLM Agents on Collaborative Reasoning Tasks (Meta FAIR, UC Berkeley, Mart 2025) — [2503.15478](https://arxiv.org/abs/2503.15478)

**Tek cümlede:** Multi-turn credit assignment için, eğitimde ayrıcalıklı bilgiyi (referans çözümü) gören bir critic (her eylemin ne kadar iyi olduğunu tahmin eden ayrı model) eğitip politikayı tur düzeyinde DPO ile güncelliyorlar.

**Problem:** Uzun bir konuşmanın sonunda gelen tek reward'dan hangi turun iyi, hangisinin kötü olduğu anlaşılmaz. Referans çözümü gören bir değerlendirici her turu daha doğru puanlayabilir; politika ise test sırasında bu bilgiyi göremez. Bu yüzden bilgi yalnızca critic'e verilir.

**Ne yaptılar:**
1. Ortam ColBench: agent simüle bir insanla en fazla 10 turda konuşup bir Python fonksiyonu (backend) ya da HTML sayfası (frontend) yazar.
2. Critic: Referans çözümü görür. Trajectory tercih çiftlerinde Bradley-Terry amacıyla (iki seçenekten hangisinin tercih edileceğini olasılıkla modelleyen yöntem) eğitilir ve tur düzeyinde advantage verir. Advantage, referans modele göre uzunlukla normalize edilmiş ortalama log-prob oranı olarak hesaplanır.
3. Politika: Yalnızca geçmişi görür. Her turda 16 aday eylem örneklenir ve critic ile sıralanır. Üst yarı chosen, alt yarı rejected olarak tur başına DPO yapılır.
4. Model Llama-3.1-8B-Instruct; 15K backend + 6K frontend offline trajectory.

**Sonuç:** Yazarların raporuna göre backend başarısı 40.4; multi-turn DPO 34.4, rejection fine-tuning 28.2, GPT-4o 40.4. Yani 8B model bu görevde GPT-4o'ya eşit. Critic'ten ayrıcalıklı bilgi çıkarılınca 31.2'ye düşüyor. Uzunluk normalizasyonu olmadan eğitim çöküyor (3.6).

**Bizim için:** Gold SQL'i gören bir critic (bizde büyük model ya da gold sonucu) her `execute_sql` turunu puanlayıp tur düzeyinde DPO çiftleri üretebilir. Bu, online RL'siz bir multi-turn yolu.

### Search-R1: Training LLMs to Reason and Leverage Search Engines with RL (UIUC Jiawei Han grubu, UMass Amherst, Google Cloud AI Research, Mart 2025) — [2503.09516](https://arxiv.org/abs/2503.09516)

**Tek cümlede:** Modelin reasoning sırasında arama motorunu çağırmasını yalnızca sonuç reward'ıyla RL ile öğreten temel reçete; SkyRL-SQL gibi sonraki çalışmalar bunun üstüne kurulu.

**Problem:** RAG (soruya göre belge getirip bağlama koymak) bir kez arar; model ne arayacağına ve ne zaman tekrar arayacağına kendisi karar veremez. Yazarlar modelin aramayı reasoning içinde kendi kararıyla kullanmayı RL ile öğrenip öğrenemeyeceğini soruyor.

**Ne yaptılar:**
1. Modeller Qwen2.5-3B/7B, base ve instruct. Veri NQ + HotpotQA train (NQ: gerçek arama sorgularından tek adımlı sorular; HotpotQA: iki belgeyi birleştirmeyi gerektiren çok adımlı sorular).
2. Arama: E5 retriever (embedding tabanlı belge arayıcı), en ilgili 3 pasaj; en fazla 4 tur.
3. Biçim: model `<search>` içinde sorgu yazar, sonuçlar `<information>` içinde döner, cevap `<answer>` içindedir.
4. RL: PPO (actor lr 1e-6, critic lr 1e-5, 500 adım, KL 0.001, clip 0.2) ve GRPO (soru başına 5 cevap). Batch 512, en fazla 4,096 token.
5. Reward yalnızca EM (cevap birebir doğru mu); format reward'ı yok.
6. Retrieve edilen token'lar policy gradient'ten ve KL'den maskeli.

**Sonuç:** Yazarların raporuna göre RAG'e göre göreli +%24 (7B) ve +%20 (3B). Maske kaldırılınca 7B base 0.431'den 0.343'e düşüyor (~9 puan).
- GRPO daha hızlı yakınsıyor ama uzun eğitimde çökebiliyor; PPO daha kararlı.
- Instruct model daha hızlı başlıyor ama base ile aynı yere varıyor.
- Cevap uzunluğu önce düşüp sonra artıyor.

**Bizim için:** Observation maskesi (bizde tool sonuçları) ölçülmüş en net kazançlardan; maske yoksa ~9 puan kayıp.
