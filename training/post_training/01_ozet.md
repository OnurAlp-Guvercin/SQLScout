# Özet: sorulara kısa cevaplar

Bu dosya, literatürün yedi soruya verdiği cevabı toplar. Her soruda önce kısa cevap, sonra nedeni, sonra kanıtlar var. Kanıtlardaki rakamlar yazarların raporladığı değerlerdir; ayrıntısı ilgili bölümde. Terimlerin anlamı [00_terimler.md](00_terimler.md)'de.

## 1. SFT verisi nasıl seçiliyor?

**Kısa cevap:** Yalnızca doğru olduğu kontrol edilmiş cevaplar tutuluyor, kolay sorular atılıyor ve önce soru çeşitliliği artırılıyor.

**Kurallar:**
1. **Yalnızca doğrulanmış örnek.** Neredeyse her laboratuvar [rejection sampling](00_terimler.md#rejection-sampling) yapıyor. Büyük model bir soruya birkaç cevap üretiyor. Yalnızca bir testle, verifier'la ya da doğru cevapla karşılaştırılıp doğru çıkanlar SFT verisine giriyor. DeepSeek, Kimi, Qwen, NVIDIA ve Text-to-SQL çalışmalarının hepsi böyle.
2. **Kolay soru atılıyor.** Model zaten çözebildiği sorudan bir şey öğrenmez.
   - Llama 4, SFT verisinin yarısını "kolay" diye attı.
   - Phi-4, modelin tam sınırındaki soruları seçiyor; bunlara "teachable" (öğretilebilir) diyor.
   - Qwen, düşünmeden (CoT olmadan) çözülebilen soruları atıyor.
3. **Önce farklı soru, sonra aynı soruya çok cevap.** Farklı soru sayısını artırmak, aynı soruya çok cevap üretmekten daha çok kazandırıyor (NVIDIA AceReason 1.1, OpenThoughts). Aynı soruya birden çok doğru cevap eklemek ucuz bir büyütme yolu, ama ikinci sırada.
4. **Küçük model, en güçlü modelin uzun düşüncelerinden kötü öğreniyor.** 3B ve altındaki modeller için kısa ve modele "tanıdık" gelen cevaplar daha iyi. "Tanıdık", küçük modelin kendisinin de üretebileceği türden bir metin demek. Aynı aileden bir büyük model daha iyi aktarıyor. Agent'larda uzun düşünme izleri küçük modeli bozuyor (Alibaba WebDancer).
5. **Az ama iyi veri işe yarıyor, ama küçük modelde etkisi azalıyor.** s1 (1.000 örnek) ve LIMO (800 örnek) büyük modellerde güçlü sonuç verdi. LIMO'da aynı etki 3B modelde zayıf kaldı. Az veriyi birkaç epoch eğitmek, çok veriyi bir kez geçmekten iyi.
6. **Agent'ta gerçek, baştan sona trajectory'ler değerli.** Hata yapıp sonra düzelen trajectory'leri tutmak yararlı. Birden çok büyük modelin trajectory'lerini karıştırmak tek modelden iyi çıktı (Reward-SQL). Ama hiç ayırt etmeden karıştırmak bazen zarar veriyor.

## 2. SFT ve RL veri setlerinin büyüklüğü ne kadar farklı?

**Kısa cevap:** SFT verisi RL verisinden 10 ile 1.000 kat büyük. Küçük ölçekte ikisi de birkaç bin, hatta yüzler mertebesinde olabiliyor.

**Neden:** SFT modele biçimi ve bilgiyi örnekle öğretir; çok örnek gerekir. RL ise modelin zaten yapabildiğini güçlendirir; her soruya birçok [rollout](00_terimler.md#rollout) atıldığı için az soru yeter.

**Kanıtlar:**
- **Büyük laboratuvarlar:** DeepSeek-R1'de ~805 bin SFT örneğine karşı ~146 bin RL sorusu var. NVIDIA'da SFT 7–33 milyon örneğe çıkıyor. Qwen3'ün reasoning RL'i yalnızca 3.995 soruyla yapıldı. Phi-4-reasoning ~6 bin soruyla ve yalnızca 90 RL adımıyla eğitildi.
- **Text-to-SQL:** SQL-Trail ~1 bin SFT ve ~1 bin RL örneği kullandı. SkyRL-SQL yalnızca 653 RL örneğiyle eğitildi. TRUST-SQL 9 bin SFT ve 11,6 bin RL örneği kullandı.
- **Tek örnek:** "1-shot RLVR" çalışmasında tek bir soruyla RL bile Qwen modellerinde kazanç verdi. Ama "Spurious Rewards" çalışmasına göre Qwen'de rastgele reward bile kazanç gösterebiliyor. Bu yüzden her RL deneyinin yanında bir kontrol koşusu gerekiyor.
- **RL az bilgi öğretiyor:** Thinking Machines'in deneyinde RL için çok küçük bir [LoRA](00_terimler.md#lora) (rank 1) bile yetti. Bu, RL'in her rollout'tan çok az bilgi aldığını gösteriyor.

## 3. RL verisinin zorluğu ve kademeli (curriculum) RL

**Kısa cevap:** RL'e yalnızca modelin bazen çözüp bazen çözemediği sorular girmeli. Sabit bir "kolaydan zora" sırası pek işe yaramıyor; modelin o anki başarısına göre değişen bir sıra işe yarıyor.

**Neden:** [GRPO](00_terimler.md#grpo) bir sorunun rollout'larını birbiriyle karşılaştırır. Hepsi doğru ya da hepsi yanlışsa karşılaştıracak fark kalmaz ve o sorudan hiçbir şey öğrenilmez. Bu yüzden hep çözülen ve hiç çözülemeyen sorular boşa hesaplanır.

**Kanıtlar:**
1. **Ortak kural "çözülebilir ama hep çözülmüyor".** [Pass rate](00_terimler.md#pass-rate-ve-passk)'i 0 ya da 1 olan sorular atılıyor; buna [dynamic sampling](00_terimler.md#dynamic-sampling) deniyor. ByteDance'in DAPO'sunda bu tek başına +8 puan getirdi.
   - MiniMax-M1, 10 denemede başarısı 0 ile 0,9 arasında olan soruları tutuyor.
   - Light-R1 0,25–0,625 aralığını, Phi-4 0,2–0,8 aralığını kullanıyor.
   - Kesişen çalışmalara göre en değerli sorular pass rate'i ~0,5 olanlar.
2. **Kolaylaşan soru havuzdan çıkıyor.** Model eğitildikçe bazı sorular kolaylaşır. Meta ScaleRL ve POLARIS, pass rate'i 0,9'u geçen soruyu kalıcı olarak çıkarıyor. Xiaomi MiMo ise çok kolay soruların küçük bir kısmını (%10) unutmamak için geri katıyor.
3. **Sabit sıra değil, uyarlanır curriculum.** Önceden belirlenmiş bir kolaydan zora sırası çoğu deneyde işe yaramadı. Modelin o anki başarısına bakıp zorluğu seçen yöntemler işe yaradı (AdaRFT, Self-Evolving Curriculum). Zorluk, rollout atmadan modelin geçmiş sonuçlarından da tahmin edilebiliyor; bu rollout süresini yaklaşık yarıya indiriyor (GRESO). Öte yandan JustRL hiç curriculum kullanmadan düz GRPO ile de iyi sonuç aldı.
4. **Kademe çoğu zaman alanla ve uzunlukla kuruluyor.**
   - NVIDIA AceReason önce yalnızca matematik, sonra yalnızca kodla RL yapıyor.
   - DeepSeek ve Kimi önce reasoning, sonra agent görevleriyle RL yapıyor.
   - Cevap uzunluğu ya da tur sayısı küçük başlayıp büyüyor: Mistral Magistral'de 16 bin token'dan 32 bin'e, NVIDIA'da 8 bin'den yukarı.
5. **Hiç çözülemeyen soruya ipucu.** Meta CWM ve Baidu ERNIE 5, çözülemeyen soruya kısmi çözüm ekliyor ve ipucunu zamanla kaldırıyor. LUFFY ve ReLIFT gibi yöntemler bu sorularda doğru çözümü SFT olarak veriyor.

## 4. Veri seçme teknikleri

**Kısa cevap:** En çok kullanılan teknik pass rate filtresi. Onu etiket hatası filtresi ve "tool olmadan da çözülüyorsa at" filtresi izliyor.

1. **Pass rate filtresi:** Her soruya eğitilen modelle (ya da daha küçük bir modelle) N rollout atılır, pass rate'e göre seçilir (3. soru).
2. **Etiket hatası filtresi:** Model bir soruya birçok cevap üretir. Çoğunluğun verdiği cevap veri setindeki "doğru cevap"la çelişiyorsa, sorunun etiketi büyük ihtimalle hatalıdır ve soru atılır (Mistral Magistral, Meta CoT-Self-Instruct). Meta'nın deneyinde böyle filtrelenmiş 2,9 bin soru, filtrelenmemiş 10 bin sorudan daha iyi sonuç verdi.
3. **"Tool olmadan da çözülüyorsa at":** Tool kullanmayı öğretmek için, tool'suz da çözülebilen sorular atılır. Bunun için tool'lu ve tool'suz pass rate karşılaştırılır (StepFun, Xiaomi, Meituan). Qwen'in START çalışması bunun tersini seçiyor: modelin tek başına çözemeyip tool'la çözdüğü sorular.
4. **Uzlaşma:** İki farklı büyük model aynı cevaba ulaştıysa örnek tutulur (NVIDIA AceMath).
5. **SFT ve RL soruları ayrı tutuluyor:** Aynı soru iki aşamada da kullanılmıyor (Qwen3-Coder-Next). Bir çalışma kolay soruları SFT'ye, zor soruları RL'e ayırmayı öneriyor (DeReason).
6. **BIRD'e özgü:** ReViSQL, BIRD train örneklerinin %61'inin düzeltme gerektirdiğini raporluyor. Bu bizim ölçtüğümüz bir rakam değil. Doğru SQL'i boş sonuç dönen soruların atılması öneriliyor; `training/clean_bird.py` bunu yapıyor.

## 5. SFT ile RL nasıl birleşiyor? Distillation nerede?

**Kısa cevap:** Küçük modelde önce SFT ya da [distillation](00_terimler.md#distillation), sonra RL. SFT kısa tutuluyor. Küçük modeli eğitmenin en verimli yolu [on-policy distillation](00_terimler.md#on-policy-distillation-opd).

1. **Küçük modelde yalnızca RL yetmiyor.** Küçük model biçimi kendi başına bulamıyor; RL'de hiç doğru cevap üretemeyince reward hep 0 kalıyor.
   - Mistral'in küçük modelinde SFT+RL 62,8 aldı, yalnızca RL 51,9 aldı (AIME 2025: lise matematik olimpiyatı soruları).
   - DeepSeek-R1'de 32B modele distillation 72,6, doğrudan RL 47,0 verdi.
   - Microsoft Phi-4-mini'de aşamalı distillation AIME puanını 10'dan 30'a, sonra 43'e çıkardı.
2. **SFT kısa olmalı.** SFT biçimi oturtacak kadar olmalı. Uzun ve ağır bir SFT, sonraki RL'in çıkabileceği tavanı düşürebiliyor. Öte yandan yalnızca biçim öğreten çok hafif bir SFT de düşürüyor (Xiaomi MiMo-7B). Doğru miktar deneyle bulunuyor.
3. **Soru başına seçim en iyi sonucu veriyor.** Model bir soruyu bazen çözebiliyorsa o soru RL ile eğitiliyor. Hiç çözemiyorsa doğru çözüm SFT olarak veriliyor (HPT, ReLIFT, LUFFY).
4. **RL yeni yetenek açmıyor.** "Does RL Really Incentivize..." çalışmasına göre RL, modelin zaten bazen çözebildiğini daha sık çözdürüyor. Modelin hiç çözemediğini öğretmek için distillation gerekiyor.
5. **On-policy distillation en verimli yol.**
   - Qwen3'te 8B modelde RL'in ~1/10 GPU saatiyle RL'i geçti: AIME 2024'te 74,4'e karşı 67,6.
   - Thinking Machines'e göre aynı sonuca SFT'den 9–30 kat daha ucuza ulaşıyor.
   - Yaygın sıra: önce büyük modelin cevaplarıyla SFT, sonra on-policy distillation, sonra RL.
   - Tool kullanan küçük agent'ta düz on-policy distillation tool hatalarıyla bozuluyor. Bunun için GRPO ile birleştirilmesi ya da adım adım ağırlıklandırılması öneriliyor (Tencent SOD).
6. **Ucuz ara adım: DPO.** [DPO](00_terimler.md#dpo-ve-preference-optimization) aynı sorunun iyi ve kötü cevaplarından çiftlerle eğitir; rollout gerekmez. Örnekler:
   - Doğru ve yanlış SQL çiftleri (ExCoT).
   - Büyük modelin cevabı iyi, küçük modelinki kötü olarak (Delta Learning).

## 6. Multi-teacher ve multi-expert reçeteler

**Kısa cevap:** 2026'da büyük laboratuvarlar her alan için ayrı bir uzman model eğitip hepsini tek modelde birleştiriyor. Ama karşılaştırmalı çalışmalar farkın küçük olduğunu gösteriyor. Tek görevli bir agent için gerekli değil.

1. **Nasıl yapılıyor:** Her alan için (matematik, kod, agent, arama...) ayrı bir uzman SFT ve RL ile eğitiliyor. Sonra tek bir model, her soruda o alanın uzmanından on-policy distillation ile öğreniyor. Buna [multi-teacher distillation](00_terimler.md#multi-teacher-distillation-mopd) deniyor. DeepSeek-V4, Kimi K3, Xiaomi MiMo, Zhipu GLM-5, NVIDIA Nemotron ve Qwen3.5 böyle yapıyor.
2. **Neden:** Bütün alanlarda tek seferde RL yapmak alanları birbirine karıştırıyor; bir alanda gelişen model başka bir alanda geriliyor. NVIDIA'ya göre uzmanlardan distillation, RL'in bozduğu yetenekleri birkaç on adımda geri getiriyor.
3. **Ama fark küçük:** Kesişen bir karşılaştırmada üç yolun arasındaki fark ortalamada en fazla 1,4 puan çıktı: [model merging](00_terimler.md#model-merging), karışık RL ve multi-teacher distillation. En ucuzu tek bir karışık RL.
4. **Model merging:** Ağırlıkların ortalamasını almak çok ucuz ve küçük bir kazanç verebiliyor (Qwen3 Embedding 0.6B'de ~+2 puan). Agent görevlerinde ise kötü sonuç verdi.
5. **Birden çok büyük modelden SFT verisi:** NVIDIA'nın veri setleri birden çok büyük modelin cevaplarını içeriyor. Her kaynakla ayrı eğitip birleştirmek ya da adım adım en iyi kaynağı seçmek, hepsini düz karıştırmaktan daha iyi.

## 7. Reward ve algoritma

**Kısa cevap:** Reward basit ve ikili (doğru 1, yanlış 0). Algoritma GRPO ailesinden. Agent'ta tool sonuçları kayba girmiyor.

1. **Reward basit olmalı.**
   - NVIDIA Tool-N1'de kısmi puanlı reward, basit doğru/yanlış reward'ından kötü çıktı.
   - Text-to-SQL'de "doğruysa 1, yalnızca çalışıyorsa 0,1" yetiyor (Snowflake Arctic-Text2SQL-R1, Databricks). Ayrıntılı ara puanlar modeli tembelleştirebiliyor.
   - Yardımcı puanlar ancak son cevap doğruysa veriliyor (TRUST-SQL).
   - Tek bir ikili reward kaçış yolu da açabilir. Qwen3Guard'da model güvenlik reward'ını yükseltmek için her şeyi reddetmeyi öğrendi; buna [reward hacking](00_terimler.md#reward-hacking) deniyor. Çözüm ayrı bir ceza terimi oldu.
2. **Algoritma GRPO ailesi.** Çoğu reçete GRPO'yu birkaç düzeltmeyle kullanıyor:
   - DAPO'nun düzeltmeleri: [clip-higher](00_terimler.md#clip-ve-clip-higher), dynamic sampling, token düzeyinde kayıp, aşırı uzun cevaba yumuşak ceza.
   - Qwen GSPO'yu, MiniMax CISPO'yu kullanıyor.
   - [KL cezası](00_terimler.md#kl-penalty) çoğunlukla kapalı ya da çok küçük. NVIDIA ProRL uzun eğitimde KL'i kullanıyor ve başlangıç modelini ara ara güncelliyor.
   - Birden çok reward varsa her biri ayrı ölçekleniyor (NVIDIA GDPO).
3. **Agent'a özgü kurallar:**
   - Tool sonuçları (observation'lar) kayıptan çıkarılıyor; buna [loss masking](00_terimler.md#loss-masking) deniyor. Search-R1'de bu kaldırılınca ~9 puan düştü.
   - Kesilen ya da bozuk trajectory'ler cezalandırılmıyor, güncellemeden çıkarılıyor (SimpleTIR, DeepSWE, Tongyi).
   - Geçersiz tool call'a ve tur sınırını aşmaya ceza veriliyor (Qwen3-Coder-Next).
   - RL sırasında modelin tool kullanımı düşebiliyor; izlenmesi gerekiyor (TACA).
4. **İzlenmesi gerekenler:**
   - Eğitim kodu ile inference sunucusu aynı token'a farklı olasılık verebiliyor ve bu RL'i bozabiliyor. Ant'in IcePop'u bu token'ları maskeliyor; [importance sampling](00_terimler.md#importance-sampling)'e bakın.
   - Modelin hep aynı cevabı vermeye kayması ([entropy collapse](00_terimler.md#entropy-ve-entropy-collapse)) izlenmeli.
   - Uzunluk cezası keşfi öldürebiliyor (JustRL).
