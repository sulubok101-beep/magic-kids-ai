# Magic Kids AI

Streamlit tabanlı çocuklara uygun kısa hikâye ve Shorts üretim uygulaması.

## Özellikler
- 3 AI hediye kutusu konsepti üretir ve görsellerini oluşturur.
- Seçilen kutudan 3 farklı hikâye seçeneği çıkarır.
- Seçilen hikâye için 5 sahne ve her sahneye özgün AI görseli üretir.
- Tek parça Türkçe anlatım üretir.
- Özgün, basit prosedürel arka plan müziği besteler.
- Yazı ve altyazı kullanmadan 9:16 MP4 üretir.

## Yayınlama (Streamlit Community Cloud)
1. GitHub'da yeni `magic-kids-ai` deposu açın.
2. ZIP içindeki dosyaları depo köküne yükleyin.
3. https://share.streamlit.io adresinden Deploy an app seçin.
4. Repository: hesabınız/magic-kids-ai; branch: main; file: app.py
5. App settings → Secrets bölümüne:
   OPENAI_API_KEY = "kendi_api_anahtariniz"
6. Deploy edin.

## Maliyet ve gereksinimler
- Görsel üretimi için `gpt-image-1`, metin için `gpt-4.1-mini`, ses için `tts-1-hd` API kullanılır. API kullanımı ücretlidir ve ChatGPT aboneliğine dahil değildir.
- Her üretimde 3 kutu görseli + 3 hikâye afişi + 5 sahne görseli oluşturulabilir. Üretim maliyetini kontrol etmek için yalnızca seçilen aşamayı üretin; 11 görsel çağrısı olasıdır.
- Streamlit ücretsiz sunucusu büyük görsel/video işlemlerinde bellek ve süre sınırlarına takılabilir. Büyük ölçekli kullanım için güçlü bir sunucu gerekebilir.
- Arka plan müziği kodla oluşturulan özgün basit enstrümantal sestir; tam kapsamlı generative music modeli değildir.
- TTS `nova` sesini kullanır; sesin Türkçe telaffuz kalitesi test edilmelidir.
- İlk sürümde kutu açılış animasyonu web arayüzünde değil, seçim akışında durum mesajı olarak gösterilir. Video içindeki açılış sahnesi bir sonraki geliştirme adımıdır.
- Karakter tutarlılığı prompt ile desteklenir; ayrı görseller arasında kusursuz kimlik tutarlılığı garanti edilmez.
- Üretilen içerikleri çocuklara sunmadan önce yetişkin incelemesinden geçirin. Gerçek çocuk fotoğrafı/sesi yüklemeyin.
