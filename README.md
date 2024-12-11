# Otomasyonlu Sunucu Kurulum ve İzleme Sistemi Rehberi

Bu rehber, elinizde bulunan 4 sunucudan birini operatör sunucusu olarak kullanarak, diğer 3 sunucuyu otomasyonla nasıl kurup yöneteceğinizi anlatır. Bu sistem, manuel kontrol süreçlerini otomasyona geçirerek zamandan tasarruf etmenizi ve hataları minimize etmenizi sağlar.

## Neden Bu Sistemi Kullanmalısınız?

- **Zamandan Tasarruf:** Tek bir komutla birden fazla sunucuyu kurabilir ve yönetebilirsiniz.
- **Hata Azaltma:** Manuel süreçlerde meydana gelebilecek insan hatalarını en aza indirir.
- **Kolay Ölçeklenebilirlik:** Yeni sunucu eklemek veya mevcut bir sunucuyu yapıdan çıkarmak kolaydır.
- **Otomatik İzleme:** Sistem durumunu otomatik olarak kontrol eder ve gerekli durumlarda Telegram üzerinden bilgilendirme yapar.
- **Modern Entegrasyonlar:** Prometheus ve Grafana gibi araçlarla entegrasyon sağlayarak metrikleri görselleştirebilirsiniz.

## Genel Senaryo

- **Sunucu Listesi:**
  1. **Operatör Sunucusu (Merkez):**  
     Bu sunucu üzerinden tüm diğer sunucuları otomatik kurar, yönetir ve izlersiniz. Ayrıca Prometheus, Grafana gibi izleme araçlarını burada barındırabilirsiniz.
  
  2. **Alt Sunucu 1 (Kullanıcısı Var):**  
     Bu sunucuda `USER_BOT_TOKEN` ve `USER_CHAT_ID` ayarlı, yani bioauth inaktif olduğunda kullanıcıya Telegram üzerinden mesaj gider.
  
  3. **Alt Sunucu 2 (Kullanıcısı Var):**  
     İkinci sunucu da benzer şekilde kendi kullanıcısına mesaj gönderebilir.
  
  4. **Alt Sunucu 3 (Kullanıcısı Yok):**  
     Bu sunucuda kullanıcı tanımlanmamış, bu nedenle sessiz modda çalışır. Yani Telegram mesajı göndermez, fakat node_exporter ile metrik sağlar.

- **Daha Önce Nasıldı?**  
  Eskiden manuel olarak tek tek kontrol yapıyordunuz. Örneğin, bioauth inaktif mi, tünel kapalı mı, senkronizasyon geride mi? Tüm bunları elle incelemek zorundaydınız. Her bir kontrol için farklı komutları çalıştırmak, raporları yorumlamak ve ardından düzeltici işlemleri uygulamak saatlerinizi alabiliyordu. Özellikle birden fazla sunucu varsa bu süreç daha da karmaşık ve zaman alıcı hale geliyordu.

- **Şimdi Neler Değişiyor?**  
  `check_all.py` scripti sayesinde bu kontroller otomatik yapılır ve Telegram’a mesaj atılır. `setup_subnode.sh` ile her alt sunucu otomatik kurulur. `deploy_subnodes.sh` ile tek komutla tüm alt sunucuları operatör sunucusundan yönetebilirsiniz.

## Ana Dosyalar ve Görevleri

- **check_all.py:**  
  Alt sunucularda çalışır, periyodik (her dakika) kontrol yapar. Bioauth, tünel, senkronizasyon, validator durumunu izler. Gerekirse kullanıcıya (varsa) veya operatöre Telegram mesajı gönderir. Kullanıcı tanımlı değilse sessiz kalır.

- **setup_subnode.sh:**  
  Alt sunucuya göndereceğiniz kurulum scripti. Otomatik olarak paketleri, `node_exporter`’ı, `check_all.py`’yi ve servisleri ayarlar. Parametre olarak kullanıcı ve operatör bilgilerini alır, `check_all.env` dosyasıyla konfigüre eder.

- **deploy_subnodes.sh:**  
  Operatör sunucusunda çalışır. `subnodes.env` içindeki alt sunucu IP’lerini ve belirlediğiniz kullanıcı/operatör bilgilerini kullanarak `setup_subnode.sh`’yi her sunucuya kopyalar ve çalıştırır. Tek komutla çoklu kurulum sağlar.

- **subnodes.env:**  
  Alt sunucuların IP adreslerini tutar. Yeni sunucu eklerken, çıkarırken bu dosyayı güncellersiniz. Örnek bir `subnodes.env` dosyası aşağıdaki gibi olabilir:

  ```
  # subnodes.env örnek içeriği
  NODE_1_IP=192.168.1.101
  NODE_2_IP=192.168.1.102
  NODE_3_IP=192.168.1.103

  # Kullanıcı bilgileri
  NODE_1_USER_CHAT_ID=123456789
  NODE_1_USER_BOT_TOKEN=abcdefg12345

  NODE_2_USER_CHAT_ID=987654321
  NODE_2_USER_BOT_TOKEN=hijklmn67890

  # Operatör bilgileri
  OPERATOR_CHAT_ID=1122334455
  OPERATOR_BOT_TOKEN=opertoken12345
  ```

## Adım Adım Kurulum ve Kullanım

1. **GitHub’dan Dosyaları İndirin:**  
   Operatör sunucunuza SSH ile bağlanın ve:
   ```bash
   wget https://raw.githubusercontent.com/kullanici/humanode/main/subnodes.env
   wget https://raw.githubusercontent.com/kullanici/humanode/main/deploy_subnodes.sh
   chmod +x deploy_subnodes.sh
   ```

2. **Dosya İçeriklerini Düzenleyin:**
   - `subnodes.env` içine alt sunucuların IP adreslerini yazın.
   - `deploy_subnodes.sh` içinde her alt sunucu için `USER_BOT_TOKEN`, `USER_CHAT_ID`, `NODE_NAME` değerlerini belirleyin.
   - Kullanıcısı olan sunuculara geçerli token ve chat_id verin.
   - Kullanıcısız sunucularda bu değerleri boş bırakın.
   - `OPERATOR_BOT_TOKEN` ve `OPERATOR_CHAT_ID` sabit kalabilir.

3. **Kurulumu Başlatın:**
   ```bash
   ./deploy_subnodes.sh
   ```
   Bu komut:
   - `setup_subnode.sh`’yi GitHub’dan indirir.
   - Her alt sunucuya `setup_subnode.sh`’yi `scp` ile kopyalar.
   - `ssh` ile alt sunucuya bağlanıp `setup_subnode.sh` parametrelerle çalıştırır.
   - Sunucu otomatik paket kurulumlarını yapar, `check_all.py`’yi indirir, servisleri başlatır.

4. **Kontrol Edin:** Alt sunucuya bağlanarak:
   ```bash
   systemctl status check_all.timer
   systemctl status node_exporter
   ```
   Her şeyin çalıştığını doğrulayın.

## Telegram Mesajları

- Eğer kullanıcı tanımlıysa bioauth inaktif olduğunda kullanıcıya mesaj gelecek. Tünel kapalıysa operatöre mesaj gidecek.
- Kullanıcısı olmayan sunucular sessiz modda. Yani `USER_BOT_TOKEN` ve `USER_CHAT_ID` boş ise mesaj atmaz.

## Değişen Senaryolar ve Güncellemeler

- **Yeni Sunucu Ekleme:**
  `subnodes.env` dosyasına yeni sunucu IP’sini ekleyin, `deploy_subnodes.sh` içinde o sunucuya özel `USER_BOT_TOKEN`, `USER_CHAT_ID`, `NODE_NAME` değerlerini girin. Tekrar `./deploy_subnodes.sh` çalıştırın. Yeni sunucu otomatik kurulacaktır.

- **Kullanıcısı Olan Sunucuya Kullanıcı Ekleme / Silme:**
  Daha önce kullanıcısız bir sunucuya kullanıcı eklemek mi istiyorsunuz? `deploy_subnodes.sh` dosyasında o sunucunun `USER_BOT_TOKEN` ve `USER_CHAT_ID` değerlerini doldurun. Tekrar `./deploy_subnodes.sh` yapın, script alt sunucuda `check_all.env`’i günceller, artık mesaj atar. Kullanıcıyı kaldırmak isterseniz değerleri boş bırakın, aynı işlemi yapın, sunucu artık sessiz olur.

## Sorun Giderme

- `systemctl status check_all.service` veya `journalctl -u check_all.service -f` komutlarıyla logları inceleyin.
- Telegram mesajı gelmiyorsa token veya chat_id’yi test edin. `curl` ile Telegram API’ına test mesajı gönderebilirsiniz. Örnek bir komut:
  ```bash
  curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage \
       -d chat_id=<YOUR_CHAT_ID> \
       -d text="Test mesajı gönder"
  ```
- Eğer API bağlantısı kurulamazsa, sunucunuzun internet bağlantısını ve Telegram API erişimlerini doğrulayın.
- `setup_subnode.sh` ile ilgili hatalar için scripti manuel çalıştırarak daha detaylı hata bilgisi alabilirsiniz:
  ```bash
  bash /root/setup_subnode.sh --debug
  ```
- Prometheus veya Grafana entegrasyonlarında sorun yaşıyorsanız, Prometheus yapılandırma dosyasını (`prometheus.yml`) kontrol edin ve yeniden başlatmayı deneyin:
  ```bash
  systemctl restart prometheus
  ```
- Node exporter çalışmıyorsa ilgili servis durumunu kontrol edin:
  ```bash
  systemctl status node_exporter
  ```
  Gerekirse servisi yeniden başlatın:
  ```bash
  systemctl restart node_exporter
  ```
