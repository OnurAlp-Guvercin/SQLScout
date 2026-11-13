# Laboratuvarların reçeteleri nasıl ayrışıyor

Bütün laboratuvarlar aynı parçaları kullanıyor: SFT, RL, distillation. Farkları; parçaların sırasında, veri miktarında ve küçük modelleri nasıl eğittiklerinde. Her laboratuvarın ayrıntısı kendi bölümünde, terimler [00_terimler.md](00_terimler.md)'de.

## DeepSeek
- **Sıra (R1):**
  1. Küçük bir [cold start](00_terimler.md#cold-start) SFT.
  2. Reasoning RL.
  3. RL'li modelden [rejection sampling](00_terimler.md#rejection-sampling) ile büyük bir SFT verisi (~805 bin örnek).
  4. Genel RL.
- **2025 sonu ve 2026 (V3.2, V4):** Her alan için ayrı bir uzman RL ile eğitiliyor. Sonra uzmanlar distillation ile tek modelde birleştiriliyor.
- **Ayırt edici:** Küçük modelleri RL ile değil, büyük modelin cevaplarıyla distillation yaparak eğitiyor. Cevabı puanlarken önce gerekçe yazan bir reward model kullanıyor (GRM).

## Qwen
- **Sıra (Qwen3):**
  1. Uzun düşünme için cold start.
  2. Az sayıda zor soruyla reasoning RL (3.995 soru).
  3. Düşünen ve düşünmeyen modu tek modelde birleştirme ("thinking mode fusion").
  4. Genel RL.
- **Küçük modeller:** RL yapılmıyor. Büyük modelden önce düz distillation, sonra [on-policy distillation](00_terimler.md#on-policy-distillation-opd) ile öğreniyorlar ("strong-to-weak distillation").
- **Ayırt edici:** RL verisi çok küçük ve "öğrenilebilir ama zor" sorulardan seçiliyor. Kendi RL algoritmaları var (GSPO). 2026'da onlar da alan uzmanlarını distill ediyor.

## NVIDIA
- **Sıra:**
  1. Çok büyük bir SFT: milyonlarca örnek, birden çok büyük modelden.
  2. Alan alan sıralı RL: önce matematik, sonra kod ("Cascade").
  3. Uzun süreli RL (ProRL).
  4. 2026'da uzmanlardan [multi-teacher distillation](00_terimler.md#multi-teacher-distillation-mopd).
- **Ayırt edici:** Veri setlerini açık yayımlıyor. Tamamen on-policy GRPO ve doğru/yanlış reward kullanıyor. Zorluğu soruların pass rate'ine göre kademeli artırıyor.

## Google, Meta, Microsoft, Mistral
- **Google (Gemma):** Ağırlıklı olarak büyük modelden distillation, ardından RL.
- **Meta (Llama 4):**
  1. Hafif bir SFT; kolay örneklerin yarısı atılıyor.
  2. Zor sorularla online RL.
  3. Hafif bir DPO.
- **Microsoft (Phi):** Modelin sınırındaki ("teachable") sorularla SFT, ardından çok kısa bir RL (~6 bin soru, 90 adım). Küçük modellerde aşamalı distillation.
- **Mistral (Magistral):** Büyük modelde SFT'siz, saf RL. Küçük modelde SFT+RL; çünkü küçük model saf RL'de geride kaldı.
- **Ayırt edici:** Meta, RL'e daha çok hesap verildikçe sonucun nasıl arttığını ölçtü (ScaleRL).

## ByteDance, Zhipu, Xiaomi ve diğer Çin laboratuvarları
- **ByteDance:** GRPO'yu kararlı hale getiren düzeltmeleri yayımladı (DAPO, VAPO). Bunlar bugün birçok reçetenin standardı.
- **Zhipu (GLM-4.5):** Alan uzmanları ayrı eğitiliyor, sonra tek modelde birleştiriliyor.
- **Xiaomi (MiMo):** Reasoning için özel pretraining, ardından RL. Uzmanlardan multi-teacher on-policy distillation (MOPD).
- **Ant:** Eğitim ve inference motorlarının olasılık farkını düzelten IcePop.

## Açık gruplar (AI2, Berkeley, Stanford, Hugging Face)
- **AI2 (Tülu 3, OLMo):** SFT → DPO → RLVR. "RLVR" terimi Tülu 3'ten geliyor.
- **Stanford s1 ve LIMO:** Çok az ama iyi seçilmiş veriyle (1.000 ve 800 örnek) SFT.
- **Berkeley (DeepScaleR, DeepCoder):** Zaten distill edilmiş küçük bir modelde, cevap uzunluğu kademeli artan RL.
- **Ayırt edici:** Az veri, kontrol koşuları ve açık veri reçeteleri (OpenThoughts).
