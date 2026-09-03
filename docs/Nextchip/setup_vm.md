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
