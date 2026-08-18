
```bash
# 자동 업데이트 기능 비활성화 (개발 환경에서만 추천)
sudo dpkg-reconfigure -plow unattended-upgrades
# -> 대화형 창이 뜨면 '아니오(No)'를 선택하세요.
```

```bash
sudo apt-mark hold libegl-mesa0 libgbm1 libgl1-mesa-dri libglapi-mesa libglx-mesa0 mesa-vulkan-drivers libgl1-amber-dri
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