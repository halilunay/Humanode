Otomasyonlu Sunucu Kurulum ve İzleme Sistemi Rehberi
Bu rehber, elinizde bulunan 4 sunucudan birini operatör sunucusu olarak kullanarak, diğer 3 sunucuyu otomasyonla nasıl kurup yöneteceğinizi anlatır. Rehberde, 2 sunucunun kullanıcı tanımlı (Telegram üzerinden bilgilendirme alacak) olduğu, 1 sunucunun ise henüz kullanıcı tanımlanmamış bir senaryo üzerinden ilerlenmektedir. Bu yapı, sisteminizi büyütmek, küçültmek, kullanıcı eklemek veya çıkarmak gibi durumlarda kolayca uyarlama yapmanızı sağlar.

Genel Senaryo
Sunucu Listesi:

Operatör Sunucusu (Merkez):
Bu sunucu üzerinden tüm diğer sunucuları otomatik kurar, yönetir ve izlersiniz. Ayrıca Prometheus, Grafana gibi izleme araçlarını burada barındırabilirsiniz.

Alt Sunucu 1 (Kullanıcısı Var):
Bu sunucuda USER_BOT_TOKEN ve USER_CHAT_ID ayarlı, yani bioauth inaktif olduğunda kullanıcıya Telegram üzerinden mesaj gider.

Alt Sunucu 2 (Kullanıcısı Var):
İkinci sunucu da benzer şekilde kendi kullanıcısına mesaj gönderebilir.

Alt Sunucu 3 (Kullanıcısı Yok):
Bu sunucuda kullanıcı tanımlanmamış, bu nedenle sessiz modda çalışır. Yani Telegram mesajı göndermez, fakat node_exporter ile metrik sağlar.

Daha Önce Nasıldı?
Eskiden manuel olarak tek tek kontrol yapıyordunuz. Bioauth inaktif mi, tünel kapalı mı, senkronizasyon geride mi? Tüm bunları elle incelemek zorundaydınız.

Şimdi Neler Değişiyor?
check_all.py scripti sayesinde bu kontroller otomatik yapılır ve Telegram’a mesaj atılır. setup_subnode.sh ile her alt sunucu otomatik kurulur. deploy_subnodes.sh ile tek komutla tüm alt sunucuları operatör sunucusundan yönetebilirsiniz.

Ana Dosyalar ve Görevleri
check_all.py:
Alt sunucularda çalışır, periyodik (her dakika) kontrol yapar. Bioauth, tünel, senkronizasyon, validator durumunu izler. Gerekirse kullanıcıya (varsa) veya operatöre Telegram mesajı gönderir. Kullanıcı tanımlı değilse sessiz kalır.

setup_subnode.sh:
Alt sunucuya göndereceğiniz kurulum scripti. Otomatik olarak paketleri, node_exporter’ı, check_all.py’yi ve servisleri ayarlar. Parametre olarak kullanıcı ve operatör bilgilerini alır, check_all.env dosyasıyla konfigüre eder.

deploy_subnodes.sh:
Operatör sunucusunda çalışır. subnodes.env içindeki alt sunucu IP’lerini ve belirlediğiniz kullanıcı/operatör bilgilerini kullanarak setup_subnode.sh’yi her sunucuya kopyalar ve çalıştırır. Tek komutla çoklu kurulum sağlar.

subnodes.env:
Alt sunucuların IP adreslerini tutar. Yeni sunucu eklerken, çıkarırken bu dosyayı güncellersiniz.

Adım Adım Kurulum ve Kullanım
GitHub’dan Dosyaları İndirin:
Tüm dosyalar (check_all.py, setup_subnode.sh, deploy_subnodes.sh, subnodes.env) bir GitHub reposunda bulunur. Operatör sunucusuna SSH ile bağlanın ve:

bash
Kodu kopyala
wget https://raw.githubusercontent.com/kullanici/humanode/main/subnodes.env
wget https://raw.githubusercontent.com/kullanici/humanode/main/deploy_subnodes.sh
chmod +x deploy_subnodes.sh
Böylece deploy_subnodes.sh dosyası çalışmaya hazır.

Dosya İçeriklerini Düzenleyin:

subnodes.env içine alt sunucuların IP adreslerini yazın.
deploy_subnodes.sh içinde her alt sunucu için USER_BOT_TOKEN, USER_CHAT_ID, NODE_NAME değerlerini belirleyin.
Kullanıcısı olan sunuculara geçerli token ve chat_id verin.
Kullanıcısız sunucularda bu değerleri boş bırakın.
OPERATOR_BOT_TOKEN ve OPERATOR_CHAT_ID sabit kalabilir.
Kurulum Başlatın:

bash
Kodu kopyala
./deploy_subnodes.sh
Bu komut:

setup_subnode.sh’yi GitHub’dan indirir.
Her alt sunucuya setup_subnode.sh’yi scp ile kopyalar.
ssh ile alt sunucuya bağlanıp setup_subnode.sh parametrelerle çalıştırır.
Sunucu otomatik paket kurulumlarını yapar, check_all.py’yi indirir, servisleri başlatır.
Kontrol Edin: Alt sunucuya bağlanarak:

bash
Kodu kopyala
systemctl status check_all.timer
systemctl status node_exporter
Her şeyin çalıştığını doğrulayın.

Telegram Mesajları:

Eğer kullanıcı tanımlıysa bioauth inaktif olduğunda kullanıcıya mesaj gelecek. Tünel kapalıysa operatöre mesaj gidecek.
Kullanıcısı olmayan sunucular sessiz modda. Yani USER_BOT_TOKEN ve USER_CHAT_ID boş ise mesaj atmaz.
Değişen Senaryolar ve Güncellemeler
Yeni Sunucu Ekleme: subnodes.env dosyasına yeni sunucu IP’sini ekleyin, deploy_subnodes.sh içinde o sunucuya özel USER_BOT_TOKEN, USER_CHAT_ID, NODE_NAME değerlerini girin. Tekrar ./deploy_subnodes.sh çalıştırın. Yeni sunucu otomatik kurulacaktır.

Kullanıcısı Olan Sunucuya Kullanıcı Ekleme / Silme: Daha önce kullanıcısız bir sunucuya kullanıcı eklemek mi istiyorsunuz? deploy_subnodes.sh dosyasında o sunucunun USER_BOT_TOKEN ve USER_CHAT_ID değerlerini doldurun. Tekrar ./deploy_subnodes.sh yapın, script alt sunucuda check_all.env’i günceller, artık mesaj atar.
Kullanıcıyı kaldırmak isterseniz değerleri boş bırakın, aynı işlemi yapın, sunucu artık sessiz olur.

Sorun Giderme:

systemctl status check_all.service veya journalctl -u check_all.service -f komutlarıyla logları inceleyin.
Telegram mesajı gelmiyorsa token veya chat_id’yi test edin. Curl ile Telegram API’ına test mesajı gönderebilirsiniz.
Paket hatası alırsanız setup_subnode.sh’yi alt sunucuda manuel bash /root/setup_subnode.sh ... parametreleriyle çalıştırıp hataya bakın.
Prometheus ve Grafana Kullanımı
Her alt sunucuda node_exporter :9100 portunda metrik sağlar.
Operatör sunucusunda Prometheus prometheus.yml dosyasına alt sunucuların :9100 portlarını ekleyin. Örneğin:
yaml
Kodu kopyala
scrape_configs:
  - job_name: 'nodes'
    static_configs:
      - targets:
        - '10.10.10.11:9100'
        - '10.10.10.12:9100'
        - '10.10.10.13:9100'
Prometheus’u yeniden başlatın.
Grafana’da Prometheus’u veri kaynağı olarak ekleyip node_exporter için hazır dashboard’ları yükleyin. CPU, RAM, disk gibi metrikleri görselleştirin.
Sonuç
Bu rehber, manuel kontrol yapan birinin setup_subnode.sh, deploy_subnodes.sh, check_all.py, subnodes.env dosyalarıyla otomasyona geçişini ve her değişikliğe kolay adapte olabilmesini sağlar. Bu sayede:

Tek komutla çoklu sunucu kurulumu,
Kullanıcı ekleme/çıkarma,
Sessiz mod (kullanıcısız) sunucuların varlığı,
Telegram üzerinden otomatik bildirimler,
Prometheus ve Grafana entegrasyonu
gibi özelliklerle operasyonlarınızı kolayca yönetebilirsiniz. README’yi rehber edinerek sisteminizi büyütüp küçültmeye, hataları gidermeye ve tamamen otomatikleştirmeye hazırsınız.
