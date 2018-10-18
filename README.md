# KLive
KLive는 라이브 방송을 제공하는 사이트 및 앱을 크롤링하는 python 코드이다.

- KODI addon
- PLEX plugin
- KLive Server + Android TV App

# 메뉴얼
https://soju6jan.github.io/klive


---
## 폴더구조
####  lib 폴더 내 파일은 공용파일이다. 직접 파일을 복사한 후 설치 해야한다.
  - KODI
  ```
    - plugin.video.KLive
        resoureces
          language
            Korean
            English
          lib  (lib 폴더 복사)
  ```

  - PLEX
  ```
    - KLive.bundle
        Contents
          Code (lib 폴더 내 파일 복사)
          esources
            English
  ```
  - Server
  ```
    - klive_server
        data
        lib  (lib 폴더 복사)
  ```


---
## 변경사항
#### 0.3.0 (2018-10-16)
  - custom 채널 설정 지원
  - Android TV 앱 연동
  -
#### 0.2.2 (2018-08-28)
  - 일부 OS에서 옥수수 안되는 문제 수정

#### 0.2.1 (2018-08-28)
  - KBS 수정

#### 0.1.4 (2018-04-01)
  - KODI / PLEX RADIO2 버그 수정

#### 0.1.3 (2018-03-28)
  - 일부 OS에서 m3u, xml 파일 쓰기가 안되는 문제 수정

#### 0.1.0 (2018-03-18)
  - First Release
