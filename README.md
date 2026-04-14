# 🧍 anime-standee-ar

OpenCV와 체스보드 패턴을 이용하여 **카메라 자세 추정(Camera Pose Estimation)** 을 수행하고, 계산된 자세 정보를 바탕으로 체스보드 위에 여러 캐릭터 이미지를 **세워진 스탠디(Standee) 형태의 AR** 로 렌더링하는 프로젝트입니다.

---

## ✨ 프로젝트 개요

이 프로젝트의 목표는 다음과 같습니다.

* 📐 체스보드 패턴을 기준으로 카메라 자세를 추정한다.
* 🖼️ 여러 캐릭터 이미지를 체스보드 위의 **수직 평면(vertical plane)** 으로 배치한다.
* 🎭 카메라 시점 변화에 따라 캐릭터 이미지가 함께 기울어지고 이동하도록 만든다.
* 📸 결과 화면을 저장하여 데모 이미지를 만든다.

---

## 📁 프로젝트 구조

```text
anime-standee-ar/
├─ assets/
│  ├─ Kento_Nanami.png
│  ├─ Megumi_Fushiguro.png
│  ├─ Satoru_Gojo.png
│  ├─ Toji_Fushiguro.png
│  ├─ Ryomen_Sukuna.png
│  └─ Ryomen_Sukuna2.png
├─ calib/
│  ├─ calibration_data.npz
│  └─ calibration_result.txt
├─ data/
│  └─ chessboard.avi
├─ results/
│  ├─ demo_front.png
│  ├─ demo_tilted.png
│  └─ demo_close.png
├─ pose_ar_stand.py
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🛠️ 구현 기능

### 1) 📐 카메라 자세 추정

`pose_ar_stand.py`

* 입력 영상(`data/chessboard.avi`) 또는 웹캠 영상을 읽음
* 체스보드 내부 코너 검출
* `cv.cornerSubPix()` 를 이용해 코너 위치 정밀화
* `cv.solvePnP()` 를 이용해 카메라 자세 추정
* `cv.Rodrigues()` 를 이용해 회전 행렬 계산
* 현재 카메라 위치 정보(`Camera XYZ`)를 화면에 표시

### 2) 🎭 캐릭터 스탠디 AR 렌더링

`pose_ar_stand.py`

* 각 캐릭터 이미지를 체스보드 위의 **수직 평면** 으로 정의
* `cv.projectPoints()` 를 이용해 3D 평면 꼭짓점을 2D 영상 좌표로 투영
* `cv.getPerspectiveTransform()` 과 `cv.warpPerspective()` 를 이용해 이미지를 원근에 맞게 변환
* 변환된 이미지를 원본 프레임에 합성하여 AR처럼 표시

### 3) 👥 멀티 캐릭터 배치

* 총 6개의 캐릭터를 두 그룹으로 배치
* 한 장면 안에서 여러 캐릭터가 동시에 보이도록 구현
* 각 캐릭터의 위치와 크기를 체스보드 칸 단위로 조절 가능

### 4) 📸 결과 저장

* `s` 키를 눌러 현재 결과 화면을 저장 가능
* 결과 이미지는 `results/` 폴더에 저장

---

## ▶️ 실행 방법

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 프로그램 실행

```bash
python pose_ar_stand.py
```

---

## ⚙️ 주요 설정값

### 입력 설정

```python
INPUT_SOURCE = "data/chessboard.avi"
CALIB_PATH = "calib/calibration_data.npz"
```

* `INPUT_SOURCE`
  * `"data/chessboard.avi"` : 미리 촬영한 영상 사용
  * `0` : 기본 웹캠 사용

### 체스보드 설정

```python
BOARD_PATTERN = (8, 6)
BOARD_CELL_SIZE = 0.025
```

* 체스보드 칸 개수: `9 x 7`
* 내부 코너 개수: `8 x 6`
* 한 칸 크기: `0.025 m`

### 캐릭터 배치 설정

각 캐릭터는 아래와 같은 방식으로 설정합니다.

```python
{
    "name": "Ryomen_Sukuna",
    "path": "assets/Ryomen_Sukuna.png",
    "anchor_x_cells": 1.9,
    "anchor_y_cells": 4.0,
    "height_cells": 4.0,
}
```

* `anchor_x_cells`, `anchor_y_cells`
  * 체스보드 칸 단위 기준 시작 위치
* `height_cells`
  * 캐릭터 높이
* `width_cells`
  * 이미지 비율에 따라 자동 계산

---

## 🧩 캐릭터 구성

### 그룹 1
* Kento Nanami
* Megumi Fushiguro
* Satoru Gojo

### 그룹 2
* Toji Fushiguro
* Ryomen Sukuna
* Ryomen Sukuna2

총 6개의 캐릭터를 체스보드 위에 동시에 배치했습니다.

---

## 🧠 구현 원리

이 프로젝트는 다음 순서로 동작합니다.

### 1. 캘리브레이션 결과 불러오기
이전 프로젝트(chessboard-lens-calibrator)에서 구한 `calibration_data.npz` 파일에서 다음 값을 불러옵니다.

* Camera Matrix `K`
* Distortion Coefficients `dist_coeff`

### 2. 체스보드 코너 검출
영상에서 체스보드 내부 코너를 찾습니다.

### 3. 카메라 자세 추정
검출한 2D 코너와 체스보드의 3D 기준점을 이용해 `cv.solvePnP()` 로 카메라 자세를 추정합니다.

### 4. 수직 평면 정의
각 캐릭터는 체스보드 위에 세워진 직사각형 평면으로 정의됩니다.

### 5. 원근 변환 및 합성
`cv.projectPoints()` 로 수직 평면의 꼭짓점을 영상 좌표로 투영한 뒤,  
`cv.getPerspectiveTransform()` 과 `cv.warpPerspective()` 를 이용해 캐릭터 이미지를 그 평면에 맞게 변환합니다.

### 6. 최종 렌더링
변환된 캐릭터 이미지를 프레임 위에 합성하여, 체스보드 위에 세워진 AR 스탠디처럼 보이게 만듭니다.

---

## 🖼️ 데모 이미지

아래 이미지는 카메라 자세 추정 결과를 이용해 6개의 캐릭터 스탠디를 체스보드 위에 렌더링한 예시입니다.

### 1) 정면

<img width="640" height="480" alt="multi_standee_preview_04" src="https://github.com/user-attachments/assets/b77fe278-dbdc-46f7-aff5-7cdf20ca7fb1" />

정면에 가까운 시점에서 6개의 캐릭터가 배치된 장면입니다.

### 2) 기울어진 시점

<img width="640" height="480" alt="multi_standee_preview_11" src="https://github.com/user-attachments/assets/03def949-59db-401b-8f91-df22ec9d9e9e" />

카메라가 기울어진 상태에서도 캐릭터 이미지가 체스보드 평면에 맞춰 함께 원근 변환되는 모습을 확인할 수 있습니다.

### 3) 더 강한 원근 변화

<img width="640" height="480" alt="multi_standee_preview_17" src="https://github.com/user-attachments/assets/85b8e2a8-dea2-4f00-a71e-4316407e3cc5" />

카메라 시점 변화가 더 커진 상황에서도 여러 캐릭터가 동시에 렌더링되는 예시입니다.

### 4) 멀어진 시점에서의 전체 장면

<img width="640" height="480" alt="multi_standee_preview_20" src="https://github.com/user-attachments/assets/46215488-6767-44aa-a517-4724c3d88e32" />

카메라가 더 멀어진 상태에서 전체 장면 구성이 어떻게 보이는지 확인할 수 있습니다.

---

## 🎮 조작 방법

* `ESC` : 종료
* `s` : 현재 프레임 저장
* `b` : 외곽선 표시 on/off

---

## 📊 결과 해석

* 체스보드가 정상적으로 검출되면 카메라 자세 추정이 가능했습니다.
* 추정된 자세를 이용해 캐릭터 이미지가 체스보드 위에 세워진 것처럼 렌더링되었습니다.
* 카메라 시점이 바뀌면 캐릭터도 함께 원근에 맞게 기울어져 보였습니다.
* 여러 캐릭터를 동시에 배치해도 한 장면 안에서 AR 구성이 가능함을 확인했습니다.

---

## ⚠️ 한계점

* 캐릭터 수가 많아질수록 렌더링 비용이 증가하여 속도가 느려졌습니다.
* 체스보드 검출이 불안정하면 캐릭터도 함께 흔들릴 수 있습니다.
* 캐릭터의 이미지 배경 제거 품질에 따라 결과의 자연스러움이 달라질 수 있습니다.
* 체스보드 기준 좌표계와 캐릭터 배치 좌표를 직접 조절해야 해서 초기 배치 튜닝이 필요합니다.

---

## 🔧 사용한 주요 OpenCV 함수

* `cv.VideoCapture()` : 카메라 또는 동영상 입력
* `cv.findChessboardCorners()` : 체스보드 코너 검출
* `cv.cornerSubPix()` : 코너 위치 정밀화
* `cv.solvePnP()` : 카메라 자세 추정
* `cv.Rodrigues()` : 회전 벡터 → 회전 행렬 변환
* `cv.projectPoints()` : 3D 점을 2D 영상 좌표로 투영
* `cv.getPerspectiveTransform()` : 원근 변환 행렬 계산
* `cv.warpPerspective()` : 캐릭터 이미지를 수직 평면에 맞게 변환
* `cv.imwrite()` : 결과 이미지 저장

---

## 📌 참고

이 프로젝트는 **카메라 캘리브레이션 결과를 재사용하여**, 체스보드 기반의 pose estimation과 image warping을 결합한 AR을 구현했습니다.

사용한 캐릭터 이미지의 저작권은 원저작권자에게 있습니다.
