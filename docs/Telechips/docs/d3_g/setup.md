
<!-- ```bash
# 자동 업데이트 기능 비활성화 (개발 환경에서만 추천)
sudo dpkg-reconfigure -plow unattended-upgrades
# -> 대화형 창이 뜨면 '아니오(No)'를 선택하세요.
```

```bash
sudo apt-mark hold libegl-mesa0 libgbm1 libgl1-mesa-dri libglapi-mesa libglx-mesa0 mesa-vulkan-drivers libgl1-amber-dri
``` -->

## Display Setup

`DashBoard` 실행시 출력을 보기 위해서 `QT_QPA_PLATFORM` 환경변수 값을 `wayland`로 만들어 주어야 한다.

* 아래 명령으로 `.bashrc`에 추가하고 export

  ```bash
  echo 'export QT_QPA_PLATFORM=wayland' >> ~/.bashrc
  source ~/.bashrc
  ```

## Network setup

* Wifi: GUI 환경에서 AP 선택하고 진행
* `eth0`, wired lan, 은 ip, `192.168.0.101`으로 고정
* `netplan`으로 수정:
  
  ```bash
  sudo vi /etc/netplan/99-default.yaml 
  ```
  
  ```bash
  # 수정전
  network:
    version: 2
    renderer: NetworkManager
    ethernets:
      eth0:
          dhcp4: true
          optional: true
  ```
  
  ```bash
  # 수정후
  network:
    version: 2
    renderer: NetworkManager
    ethernets:
      eth0:
        dhcp4: no
        addresses:
          - 192.168.0.101/24
          #      dhcp4: true
          #      optional: true
  ```
  
* apply `netplan`

  ```bash
  sudo netplan apply
  ```

---
## swap memory size 늘리기

```bash
sudo swapoff -a
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

echo '/swapfile none swap defaults 0 0' | sudo tee -a /etc/fstab
```

---
## 연결시 logon 상태를 기본값으로 변경

```bash
sudo sed -i 's/^#  AutomaticLoginEnable = true/AutomaticLoginEnable = true/' /etc/gdm3/custom.conf
sudo sed -i "s/^#  AutomaticLogin = .*/AutomaticLogin = $USER/" /etc/gdm3/custom.conf
```

---
## Silicon Labs CP210x USB to UART Bridge 인식문제

* D3-G board의 경우 장치 관리자에서 인식되지 않는다.
  - 이 경우 보드 문제로 오인할 수 있다. 반드시 FW를 download해서 확인해야 한다.
* AI-G / VCP-G에서는 인식된다.
