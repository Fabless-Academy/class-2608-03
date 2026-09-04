# Ubuntu Install on VirtualBox

## 1. VirtualBox  설치

- 아래 사이트에 들어가서 Download / 설치 진행!

[Oracle VirtualBox](https://www.virtualbox.org/)

## 2. VM 생성

- `새로 만들기` 클릭
    - **VM Name :** VM_NextChip
    - VM Folder : default로 진행
    - ISO Image : ubuntu-20.04.6-desktop-amd64.iso 선택
        - 선택 시 아래 OS/OS Distribution/OS Version 등 자동 선택
        - 중요!! : **Proceed with Unattended Installation** 체크 해제!
    - Spectify virtual hardware
        - Base Memory : `4GB 이상` 여유있게
        - CPU : `8개 이상` 여유있게
    - Specify virtual Hard Disk
        - `64GB` 권장
- VM_NextChip 설정
    - 네트워크
        - `어댑터 2` - 네트워크 어댑터 활성화
            - Attached to : **어댑터에 브릿지**
            - Name : **노트북의 유선 adaptor** 선택
- 설정 완료 후 Summary 확인
    - 시스템 : 기본 메모리, 프로세서 확인
    - 저장소 : 하드 디스크 (64GB이상)
    - 네트워크 : 어댑터2 활성화 여부 확인

## 3. Ubuntu 20.04 설치

- VM 전원 켜기 : VM_NextChip 더블 클릭
- Install 화면
    - Install Ubuntu 선택

- Keyoard Layout Continue
    - default로 continue 선택

- Update and other software
    - Normal Installation 선택 후 continue

- Installation type
    - Erasedisk and install ubuntu 선택 후 ‘Install Now’ 진행
        - continue 진행

- Where are you?
    - Seoul 선택 : apt-get repository 선택에 영향을 미치므로 꼭 Seoul 선택 후 continue

- Who are you
    - Your name : devuser
    - password : 본인이 선택

- 설치 진행
    - 진행 완료 popup 뜨면 **Restart Now** 클릭

    <!-- - installation medium 제거 안내 나오면 머신 전원 끄고 미디어 꺼내기
        - 전원 끄기 : 파일 - 닫기 / 시스템 전원 끄기 선택 후 확인
        - 설정 - 저장소 카테고리 선택 -> 저장소에서 `ubuntu-20.04-desktop-amd64.iso` 선택 -> 속성 섹션에서 Optical Drive 옆 CD 모양 아이콘 클릭
            - `Remove Disk From Virtual Drive` 선택

        - 확인 후 VM 다시 전원 켜기 -->

## 4. Guest 확장 프로그램 설치

### Guest 확장 프로그램?

- Virtual Box의 Guest OS (현재는 Ubuntu)에서 VM을 편하게 사용할 수 있도록 해주는 프로그램
- **기능 :** 화면 해상도 자동 조정, Host OS - Guest OS 사이 공유 폴더, 클립 보드 공유

### 설치 방법

- 게스트 확장 CD 이미지 삽입
  - VM화면 메뉴 -> 장치 -> 게스트 확장 CD 이미지 삽입
- `build-essential` 패키지 설치
  
  ```bash
  sudo apt update
  sudo apt install build-essential
  ```

- 게스트 확장 프로그램 설치
  
  ```bash
  sudo /media/devuser/VBOX_GAs_7.?.?/VBoxLinuxAdditions.run
  ```

- 공유 폴더 설정
  - Windows `C:/share` folder 생성
  - VM화면 메뉴 -> 장치 -> 공유 폴더 -> 공유 폴더 설정
  - 박스 영역 내에서 마우스 오른쪽 버튼 클릭 -> 공유 폴더 추가
    - Folder Path : `C:/share` 선택
    - 자동 마운트 / Make Machine-permanent 선택
    - 확인

- 클립 보드 공유 설정
  - VM화면 메뉴 -> 장치 -> 공유 폴더 -> 클립 보드 공유 -> `양방향`

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

## 5. VS code install

### `sudo dpkg -i ~/res/vscode/code_1.35.1-1560349847_i386.deb`의 문제점

제시해주신 명령어로 설치할 경우 이전 두 방식(APT, Snap)과 몇 가지 치명적인 차이점 및 문제점이 발생합니다.

#### 1. 32비트(i386) 패키지 문제 (실행 불가)
`i386`은 **32비트 아키텍처용 패키지**를 의미합니다.

* Visual Studio Code는 **1.36 버전을 끝으로 32비트 Linux 지원을 중단**했습니다.
* Ubuntu 20.04(64비트) 환경에서 `i386.deb`를 그대로 설치하면 라이브러리 의존성 오류가 발생하거나 실행되지 않을 가능성이 매우 높습니다. 64비트 시스템에서는 `amd64.deb` 파일을 사용해야 합니다.

#### 2. 구버전 패키지 (2019년 출시 버전)

파일명의 `1.35.1`은 **2019년 6월에 출시된 매우 오래된 버전**입니다.

* 최신 VS Code 확장 프로그램(Extensions)과의 호환성이 떨어질 수 있습니다.
* 최신 보안 패치 및 기능 개선 사항이 적용되어 있지 않습니다.

#### 3. `dpkg -i` 직접 설치의 특성 (의존성 및 자동 업데이트)

* **의존성 자동 해결 불가:** `dpkg -i`는 필요한 관련 패키지(의존성)를 알아서 다운로드하여 설치해주지 않습니다. 만약 의존성이 부족하면 오류가 발생하며, 추가로 `sudo apt install -f` 명령어를 실행해야 부족한 패키지가 설치됩니다.
* **자동 업데이트 불가:** APT 저장소를 등록하고 설치한 경우에는 `sudo apt update && sudo apt upgrade` 시 VS Code도 함께 최신 버전으로 업데이트되지만, `.deb` 파일을 다운로드해 `dpkg`로 직접 설치한 경우 자동 업데이트가 되지 않아 새로운 버전이 나올 때마다 직접 `.deb`를 다시 받아서 설치해야 합니다.

---

Ubuntu 20.04.6 LTS 환경에서 Visual Studio Code를 설치하는 터미널 명령어와 앱 센터(GUI)를 통한 설치 방식 간의 차이점입니다.

### 1. VS Code 설치 명령어 (터미널)

공식 APT 저장소를 등록하여 설치하는 표준 방식을 권장합니다. 터미널(`Ctrl` + `Alt` + `T`)을 열고 아래 명령어를 순서대로 실행하세요.

```bash
# 1. 필요 패키지 설치
sudo apt update
sudo apt install -y software-properties-common apt-transport-https wget

# 2. Microsoft GPG 키 다운로드 및 등록
wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -

# 3. VS Code APT 저장소 추가
sudo add-apt-repository "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"

# 4. VS Code 설치
sudo apt update
sudo apt install -y code

```

---

### 2. 터미널(APT) vs App Center(Snap) 설치 차이점

Ubuntu 소프트웨어 센터(App Center)에서 검색하여 설치하는 VS Code는 기본적으로 **Snap** 패키지 형식을 사용하며, 터미널 명령어로 설치하는 방식은 **APT (.deb)** 패키지 형식입니다.

| 구분 | 터미널 설치 (APT / .deb) | App Center 설치 (Snap) |
| --- | --- | --- |
| **패키지 형식** | Debian 패키지 (`.deb`) | 격리된 컨테이너 패키지 (`Snap`) |
| **업데이트 방식** | `sudo apt update && sudo apt upgrade` 시 함께 업데이트 | 백그라운드에서 자동 업데이트 |
| **격리 및 권한** | 시스템 권한 및 경로에 제한 없이 접근 가능 | 샌드박스(Sandbox) 환경에서 격리되어 실행 |
| **속도 및 성능** | 프로그램 실행 및 반응 속도가 빠름 | 첫 실행 시 로딩 시간이 다소 길 수 있음 |
| **개발 환경 호환성** | Docker, C/C++ 컴파일러, Node.js 등 시스템 도구와 문제없이 연동 | 샌드박스 제약으로 인해 일부 외부 도구/터미널 연동 시 권한 에러가 발생할 수 있음 |

**추천:**
개발 시 Docker, C/C++ build tool, GPU 관련 SDK, C/C++ 디버거 등 시스템 리소스에 직접 접근해야 하는 작업이 많다면 **터미널(APT) 설치 방식**을 사용하는 것을 권장합니다.
