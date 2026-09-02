# 공유 폴더 & SDK setup

## 1. Guest 확장 프로그램 설치

## Guest 확장 프로그램?

- Virtual Box의 Guest OS (현재는 Ubuntu)에서 VM을 편하게 사용할 수 있도록 해주는 프로그램
- **기능 :** 화면 해상도 자동 조정, Host OS - Guest OS 사이 공유 폴더, 클립 보드 공유

## 설치 방법

- 게스트 확장 CD 이미지 삽입
  - VM화면 메뉴 - 장치 - 게스트 확장 CD 이미지 삽입
- apt-get repository update & build-essential 패키지 설치
  
  ```bash
  sudo apt-get update
  sudo apt-get install build-essential
  ```

- 게스트 확장 프로그램 설치
  
  ```bash
  sudo /media/devuser/VBOX_GAs_7.?.?/VBoxLinuxAdditions.run
  ```

- 공유 폴더 설정
  - VM화면 메뉴 - 장치 - 공유 폴더 - 공유 폴더 설정
  - 빨간 박스 영역 내에서 마우스 오른쪽 버튼 클릭 - 공유 폴더 추가
    - Folder Path : 윈도우에서 폴더 하나 만들어서 선택
    - 자동 마운트 / Make Machine-permanent 선택
    - 확인

- 클립 보드 공유 설정
  - VM화면 메뉴 - 장치 - 공유 폴더 - 클립 보드 공유 -양방향

- Ubuntu Power Off 후 다시 VM 전원 켜고 적용 내용 동작 확인
  - 게스트 확장 정상 동작 확인
    - 화면 크기 조절 확인
    - 공유 폴더 확인 : ls /media/sf_share 확인
      - Permission denied
        - 공유 폴더를 접근 할 권한이 없음
      - 공유 폴더 접근을 위해 현재 유저에 vboxsf 라는 group 추가
  
        ```jsx
        sudo usermod -aG vboxsf $USER
        groups $USER 
        ```
  
        - 명령 수행 후 Ubuntu 재부팅
  
        ```jsx
        shutdown -r now
        ```
  
    - 클립 보드 공유 확인 : windows에서 text 복사 - Ubuntu에서 붙여넣기 확인

## 2. SDK 설치

### Toolchain 설치

- 필요한 package 설치

    ```bash
    sudo apt install xz-utils bison flex git g++ unzip libssl-dev u-boot-tools cmake make
    
    ```

- Toolchain 설치
  - x86(64bits) - Linux 기반 시스템에서 ARM 64bit - Linux에서 동작할 프로그램용 컴파일러 설치
    - **gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu**

    ```bash
    wget https://developer.arm.com/-/media/Files/downloads/gnu-a/10.2-2020.11/binrel/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz 
    sudo cp gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz /opt
    cd /opt
    sudo tar Jxvf gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz
    
    echo export "PATH=/opt/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu/bin:\$PATH" >> ~/.bashrc
    source ~/.bashrc
    ```

### SDK 설치 및 빌드

- 공유에 아래 파일을 준비
  - **apache6-sr-linux_som_micro.tgz :** Apache6 SOM board SDK
  - **dl.tgz**
- apache6-sr-linux_som_micro.tgz 복사 및 압축 해제
  - 완료 시 ~/apache6-sr-linux_som_micro 에 SDK 압축 해제 됨

  ```bash
  cp /media/sf_share/apache6-sr-linux_som_micro.tgz .
  tar xvzf apache6-sr-linux_som_micro.tgz
  ```

  - dl.tgz 를 SDK 폴더 내 복사 및 압축 해제
  - dl.tgz
    - SDK 의 build-root 빌드 시 다운로드 받아야 할 내용을 미리 받아 압축해놓은 파일
    - 압축 해제 해 놓으면 build-root 빌드 시 따로 다운로드 받는 과정 생략 됨 (시간 오래 걸리는 작업)
  
  ```bash
  cp /media/sf_share/dl.tgz ./apache6-sr-linux_som_micro/buildroot
  tar xvzf dl.tgz
  ```

- Linux Kernel Build Option 조정
  - SystemV IPC 추가

    ```bash
    vim ~/apache6-sr-linux_som_micro/linux-kernel/arch/arm64/configs/apache6_sr_som_micro_defconfig
    ```

  - 제일 아래쪽에 아래 내용 추가

    ```bash
    CONFIG_SYSVIPC=y
    CONFIG_SYSVIPC_SYSCTL=y
    ```

- 환경 설정 및 빌드

    ```bash
    # 환경 설정
    ./nc_config.sh --som-micro
    
    # 빌드 실행 (실행 시간 오래 걸림)
    ./nc_build.sh
    ```

## Booting Micro SD 카드 만들기

- Micro SD 카드를 SD Reader에 장착 후 PC에 연결
  - 해당 Reader를 Virtual Machine에 passthrough로 연결
  - Linux에서 Micro SD카드가 어떤 장치로 인식되는지 확인
    - ex) /dev/sdc

- Micro SD카드에 build된 이미지 쓰기

    ```bash
    cd ./apaapache6-sr-linux_som_micro/scripts
    sudo ./mk-sd-card.sh /dev/sdc     # 참고 : 1.6GB 정도 write해야 함 (시간 오래 걸림)
    ```

- 완성 된 sd 보드에 장착 후 보드 전원 켜면 linux 정상 부팅 됨
  - ID : root / PW : root
