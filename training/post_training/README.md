# Post-training reçeteleri: literatür taraması

**Kapsam:** Kasım 2025 – Kasım 2026 öncelikli; boşluklar Kasım 2024 – Kasım 2025 ile dolduruldu. Yalnızca büyük laboratuvarların (DeepSeek, Kimi, MiniMax, Qwen, ByteDance, Zhipu, Tencent, Xiaomi, NVIDIA, Google, Meta, Microsoft, Mistral, Apple) ve tanınmış araştırma gruplarının (AI2, Stanford, Berkeley, Hugging Face, Thinking Machines...) çalışmaları.
**Tarama tarihi:** 13 Kasım 2026. 8 paralel tarama; her makale kendi sayfasından (arXiv, resmi teknik rapor, resmi blog ya da model kartı) açılıp doğrulandı.

**Okurken bil:**
- Rakamların hepsi yazarların kendi raporladığı değerler; hiçbiri bizim tarafımızdan yeniden üretilmedi. Bulunamayan rakam yazılmadı.
- Kaynağı zayıf olan girdiler (yalnızca blog ya da model kartı, kesik okunan uzun raporlar, kendi içinde tutarsız rakamlar) kendi girdisinde belirtildi. Örnekler: Qwen3.5'in teknik raporu yok (README ve model kartından); DeepSeek-V4'ün arXiv numarası gönderim tarihiyle uyuşmuyor; NVIDIA'nın mid-training makalesi ile Nemotron 3.5 raporu token sayılarında çelişiyor.
- Bazı makalelerin arXiv sayfasında kurum yazmıyor; grup, tanınmış yazarlardan çıkarıldı (girdide belirtildi).
- Birden çok bölüme giren 6 makale tek yerde anlatıldı; diğer bölümde yalnızca yönlendirme var.

## Nasıl okunur

1. Bilmediğin bir terim gördüğünde [Terimler sözlüğü](00_terimler.md)'ne bak; her bölüm terimin ilk geçtiği yerde oraya link verir.
2. Hızlı bakış için [Özet](01_ozet.md) ve [Bizim için çıkan reçete](03_bizim_recete.md) yeterli.
3. Bölümlerdeki her makale aynı düzende anlatılır: tek cümlede ne olduğu, çözdüğü problem, adım adım ne yaptıkları, sonuçlar ve bizim için ne anlama geldiği.

## İçindekiler

0. [Terimler sözlüğü](00_terimler.md)
1. [Özet: sorulara kısa cevaplar](01_ozet.md)
2. [Laboratuvarların reçeteleri nasıl ayrışıyor](02_laboratuvar_farklari.md)
3. [Bizim için çıkan reçete](03_bizim_recete.md)
4. [DeepSeek, Moonshot (Kimi), MiniMax](04_deepseek_kimi_minimax.md)
5. [Qwen (Alibaba)](05_qwen.md)
6. [ByteDance Seed, Zhipu, Tencent, Xiaomi, Meituan, Ant, Baidu, StepFun](06_bytedance_zhipu_tencent_digerleri.md)
7. [NVIDIA (Nemotron)](07_nvidia.md)
8. [Google DeepMind, Meta, Microsoft, Mistral, Apple](08_google_meta_microsoft_mistral_apple.md)
9. [Açık reçeteler (AI2, Stanford, Berkeley, Hugging Face, Thinking Machines ve diğerleri)](09_acik_receteler.md)
10. [Veri seçimi, zorluk, curriculum ve SFT↔RL etkileşimi (kesişen çalışmalar)](10_veri_secimi_curriculum.md)
11. [Agentic, tool-use ve Text-to-SQL post-training](11_agentic_text_to_sql.md)
