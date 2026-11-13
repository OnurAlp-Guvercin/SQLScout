# Bizim için çıkan reçete

**Durum:**
- Small model `Qwen3.5-0.8B`, yerelde MLX ile çalışıyor.
- Large model `qwen/qwen3.5-9b`, API'de; small model'le aynı aileden.
- Görev agentic Text-to-SQL; tool'lar `search_values`, `execute_sql`, `submit`. Benchmark BIRD.
- Kısıtlar: eğitim bir Mac'te yapılacak, API kotası sınırlı.

Literatürden çıkan ve bu kısıtlara uyan sıra aşağıda. Terimler [00_terimler.md](00_terimler.md)'de.

## 1. Veri temizliği
- **Ne:** Doğru SQL'i (gold) hata veren ya da boş sonuç dönen soruları at. `training/clean_bird.py` bunu yapıyor.
- **İsteğe bağlı:** Large model'in onayladığı bir cevap gold'la çelişiyorsa, soruyu "gold hatası adayı" olarak ayır.
- **Neden:** Gold yanlışsa model yanlış kalıbı öğrenir. Mistral Magistral'deki etiket hatası filtresi aynı fikre dayanıyor.

## 2. SFT (rejection sampling)
- **Ne:**
  1. Sistemi train sorularında koştur.
  2. Yalnızca hem doğru çıkan (`correct`) hem de large model'in onayladığı (`label = ok`) konuşmaları al.
  3. Small model'i bu konuşmalarla LoRA kullanarak birkaç epoch eğit.
- **Nasıl seçilir:**
  - Önce farklı soru sayısını artır. Text-to-SQL çalışmaları ~1 bin soruyla başlıyor; birkaç bin yeterli.
  - Kısa konuşmaları ve hata yapıp düzelen konuşmaları tut.
- **Kayıp:** Tool sonuçları (observation'lar) kayba girmez. `mlx_lm.lora --mask-prompt` yalnızca son assistant mesajını kayba sokuyor. Bu yüzden her assistant turu ayrı bir örnek olmalı.
- **Neden:** Küçük model RL'e biçimi bilerek başlamalı. Literatürde küçük modelde önce SFT, sonra RL, yalnızca RL'den açıkça iyi.

## 3. RL (GRPO ailesi)
- **Ne:**
  1. SFT'li modelle her train sorusuna N rollout at, örneğin 8.
  2. Pass rate'i 0 ve 1 olan soruları at, ortadakileri tut. Eğitim ilerledikçe kolaylaşan soruları havuzdan çıkar.
  3. GRPO ile eğit.
- **Reward:** Cevabın sonucu gold'un sonucuyla aynıysa 1, değilse 0. İstenirse küçük bir biçim terimi eklenir.
- **Kurallar:**
  - Observation'lar kayba girmez.
  - Kesilen ya da bozuk trajectory güncellemeden çıkarılır.
- **Dikkat:** Rollout'ları `mlx_lm.server` üretip eğitimi MLX kodu yaparsa, iki taraf aynı token'a farklı olasılık verebilir. Bu fark ölçülmeli (bkz. [importance sampling](00_terimler.md#importance-sampling)).

## 4. Ucuz alternatif ya da ara adım: DPO
- **Ne:** Experience log'da aynı sorunun doğru ve yanlış cevaplarından çiftler kur ve DPO ile eğit.
- **Neden:** Rollout gerekmediği için SFT kadar ucuz (ExCoT, Delta Learning).

## 5. Şimdilik ertelenenler
- **On-policy distillation:** Large model'in her token'a verdiği olasılıkları ister. Bunun OpenRouter API'sinden alınabildiğini doğrulamadık.
- **Multi-teacher:** Tek görevli bir agent için ayrı uzman eğitmenin kazancı literatüre göre küçük.

## Her aşamada
- **Tekrar koşu:** En az 3 tekrar.
- **Kontrol koşusu:** Örneğin aynı adım sayısında rastgele reward.
- **Neden:** Küçük farklar seed gürültüsü içinde kalabiliyor. Qwen modellerinde rastgele reward bile kazanç gösterebildi.
