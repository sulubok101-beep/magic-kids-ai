import json, re

def _json_response(client, prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    raw = response.output_text.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.I|re.M).strip()
    return json.loads(raw)

def generate_gift_boxes(client, age, style):
    prompt = f"""Türkçe çocuk içerikleri için üç birbirinden çok farklı, güvenli ve merak uyandırıcı hediye kutusu konsepti üret.
Yaş hedefi: {age}. Görsel tarz: {style}.
Her kutu ayrı bir fantastik dünya açmalı. Korku, tehlikeli davranış, şiddet, reklam, marka veya telifli karakter kullanma.
JSON array ver, tam 3 nesne: name, teaser, image_prompt.
image_prompt: yalnızca görsel tarifi; yazı, harf, logo, filigran içermeyen kare kompozisyon, kutu merkezde, kaliteli 3D animasyon film estetiği."""
    data = _json_response(client, prompt)
    return data[:3]

def generate_story_choices(client, box, age, style):
    prompt = f"""Seçilen kutu: {json.dumps(box, ensure_ascii=False)}.
Hedef yaş: {age}. Görsel tarz: {style}.
Bu kutunun içinden çıkan 3 farklı, özgün, çocuklara uygun kısa macera önerisi üret.
Her biri mutlu ve şaşırtıcı sonla bitsin; korkutma, tehlikeli taklit edilebilir eylem, şiddet, reklam veya telifli karakter olmasın.
JSON array, tam 3 nesne: title, description, lesson, poster_prompt, premise.
poster_prompt yazısız, logosuz, filigransız, kaliteli 3D animasyon film afişi görsel tarifi."""
    return _json_response(client, prompt)[:3]

def generate_storyboard(client, story, age, style, scene_count=5):
    prompt = f"""Şu hikâye fikrini 45 saniyelik Türkçe çocuk Shorts videosuna dönüştür.
Hikâye: {json.dumps(story, ensure_ascii=False)}
Hedef yaş: {age}; görsel stil: {style}; sahne sayısı: {scene_count}.
Tamamı güvenli, nazik, kapsayıcı, yaşa uygun olsun. Şaşırtıcı ve mutlu son olsun.
Tek bir anlatıcı sesiyle akıcı, doğal, kısa cümleli Türkçe metin yaz. Duraklama işaretlerini abartma.
Karakterlerin görünüşünü sabit tut. Her sahne için image_prompt yaz; her prompt aynı karakter tanımını tekrar içersin.
Görselde hiçbir yazı, altyazı, harf, sayı, logo veya filigran bulunmasın.
JSON nesnesi ver: narration (yaklaşık 85-105 kelime), mood (wonder/happy/adventure/calm), character_bible (karakterlerin ayrıntılı görünüşü), scenes (tam {scene_count} nesne: image_prompt, action_description).
"""
    data = _json_response(client, prompt)
    if len(data.get("scenes", [])) != scene_count:
        raise ValueError("Hikâye motoru beklenen sahne sayısını üretmedi. Yeniden deneyin.")
    return data
