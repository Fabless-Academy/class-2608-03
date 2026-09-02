# 1. Virtual Box  설치

- 아래 사이트에 들어가서 Download / 설치 진행!

Oracle VirtualBox

# 2. VM 생성

- ‘새로 만들기 ‘ 클릭
    - **VM Name :** VM_NextChip
    - VM Folder : 새로 생성해서 설정 (되도록 경로명 길지 않게 root로 부터 가까운곳 사용하기를 권장)
    - ISO Image : ubuntu-20.04.6-desktop-amd64.iso 선택
        - 선택 시 아래 OS/OS Distribution/OS Version 등 자동 선택
        - 중요!! : **Proceed with Unattended Installation** 체크 해제!
    - Spectify virtual hardware
        - Base Memory : 4GB 이상 여유있게
        - CPU : 8개 이상 여유있게
    - Specify virtual Hard Disk
        - 64GB 권장
- VM_NextChip 설정
    - 네트워크
        - 어댑터 2 - 네트워크 어댑터 활성화
            - Attached to : 어댑터에 브릿지
            - Name : 노트북의 유선 adaptor 선택
- 설정 완료 후 Summary 확인
    - 시스템 : 기본 메모리, 프로세서 확인
    - 저장소 : 하드 디스크 (64GB이상)
    - 네트워크 : 어댑터2 활성화 여부 확인
    
    !image.png
    

# 3. Ubuntu 20.04 설치

- VM 전원 켜기 : VM_NextChip 더블 클릭
- Install 화면
    - Install Ubuntu 선택

!image.png

- Keyoard Layout Continue
    - default로 continue 선택
        
        !image.png
        

- Update and other software
    - Normal Installation 선택 후 continue
        
        !image.png
        

- Installation type
    - Erasedisk and install ubuntu 선택 후 ‘Install Now’ 진행
        - continue 진행
        
        !image.png
        
        !image.png
        

- Where are you?
    - Seoul 선택 : apt-get repository 선택에 영향을 미치므로 꼭 Seoul 선택 후 continue
        
        !image.png
        

- Who are you
    - Your name : devuser
    - password : 본인이 선택
        
        !image.png
        
- 설치 진행
    - 진행 완료 popup 뜨면 ‘Restart Now’ 클릭
    
    !image.png
    
    - installation medium 제거 안내 나오면 머신 전원 끄고 미디어 꺼내기
        - 전원 끄기 : 파일 - 닫기 / 시스템 전원 끄기 선택 후 확인
            
            !image.png
            
        - 설정 - 저장소 카테고리 선택 - 저장소에서 ubuntu-20.04-desktop-amd64.iso 선택 - 속성 섹션에서 Optical Drive 옆 CD 모양 아이콘 클릭
            - ‘Remove Disk From Virtual Drive’ 선택
            
            !image.png
            
        - 확인 후 VM 다시 전원 켜기