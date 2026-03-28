# 🌅 Dawn Palette

> 전 세계 새벽 하늘의 색을 수집하고, 그날의 새벽이 어떤 색이었는지 기록합니다.

새벽을 그리워하는 마음으로 만든 프로젝트입니다.

## 미리보기

새벽 사진에서 대표 색상을 추출하고, 분위기를 자동 분류하여 웹 갤러리로 보여줍니다.

🔗 **[Dawn Palette 갤러리 링크](https://papa-drodr.github.io/Dawn-Palette/)**

- 🔥 **burning dawn** — 타오르는 새벽, 하늘을 물들이는 붉은 빛
- 💙 **blue hour** — 파란 시간, 밤과 낮 사이의 몽환적인 순간
- 🌟 **golden dawn** — 황금빛 새벽, 따스한 빛이 번져오는 순간
- 💜 **purple dawn** — 보랏빛 새벽, 신비로운 여명의 시작
- 🧊 **cool dawn** — 차가운 새벽, 맑고 푸른 여명
- 🌑 **deep night** — 아직 깊은 밤, 새벽을 기다리는 고요한 어둠
- 🎨 **pastel dawn** — 파스텔 새벽, 부드러운 색들이 어우러진 하늘

## 프로젝트 구조

```
dawn_palette/
├── collect_dawn.py        # Unsplash API로 새벽 사진 수집
├── extract_palette.py     # OpenCV + K-means로 색상 팔레트 추출
├── generate_gallery.py    # 웹 갤러리 생성 (index.html 작성)
├── requirements.txt
├── .env                   # API 키 (git에 포함하지 않음)
├── .env.example
├── data/
│   ├── photos/            # 수집된 새벽 사진
│   ├── metadata/          # 사진 메타데이터 (JSON)
│   └── palettes/          # 추출된 팔레트 이미지 + JSON
└── docs/                  # GitHub Pages 배포 폴더
    ├── index.html         # 갤러리 페이지 (자동 생성)
    ├── style.css          # 스타일시트
    └── photos/            # 웹용 사진 복사본
```

---

## 시작하기

### 1. 설치

```bash
pip install -r requirements.txt
```
---

### 2. Unsplash API 키 발급

1. [unsplash.com/join](https://unsplash.com/join)에서 회원가입
2. [unsplash.com/developers](https://unsplash.com/developers) → **Your apps** → **New Application**
3. 이용약관 동의, 앱 이름(`Dawn Palette`)과 설명 입력
4. 생성된 앱 페이지에서 **Access Key** 복사

---

### 3. API 키 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 발급받은 키를 입력합니다.

```
UNSPLASH_ACCESS_KEY=your_access_key_here
```

---

## 사용법

### Step 1. 새벽 사진 수집

```bash
# 기본 검색어로 10장 수집
python collect_dawn.py

# 특정 검색어로 수집
python collect_dawn.py --query "sunrise ocean" --count 20

# 다음 페이지 수집
python collect_dawn.py --query "dawn sky" --page 2

# 모든 기본 검색어로 한번에 수집
python collect_dawn.py --all
```

기본 검색어: `dawn sky`, `sunrise sky colors`, `early morning sky`, `twilight dawn`, `새벽 하늘`

### Step 2. 색상 팔레트 추출

```bash
# 수집된 사진 전체 분석
python extract_palette.py

# 단일 이미지 분석
python extract_palette.py --image data/photos/사진.jpg

# 추출 색상 수 변경 (기본값: 6)
python extract_palette.py --colors 8
```

### Step 3. 웹 갤러리 생성

```bash
python generate_gallery.py
```

`docs/` 폴더에 `index.html`이 생성되고, 사진이 `docs/photos/`로 복사됩니다.

로컬에서 확인하려면 `docs/index.html`을 브라우저로 열면 됩니다.

---

## 기술 스택

- **Python 3.10+**
- **OpenCV** — 이미지 처리, 하늘 영역 추출
- **scikit-learn** — K-means 클러스터링으로 대표 색상 추출
- **Unsplash API** — 새벽 사진 수집
- **GitHub Pages** — 갤러리 호스팅

---

## 주의사항

- **경로에 한글이 포함되면 OpenCV가 이미지를 읽지 못할 수 있습니다.** 프로젝트 폴더는 `C:\Projects\dawn_palette` 같은 영문 경로에 두는 것을 권장합니다.
- Unsplash 무료 플랜(Demo)은 시간당 50회 요청 제한이 있습니다.
- 수집된 사진의 저작권은 각 사진작가에게 있으며, [Unsplash 라이선스](https://unsplash.com/license)를 따릅니다.

---

## .gitignore

```
.env
data/
__pycache__/
```

`data/` 폴더는 용량이 크기 때문에 git에 포함하지 않습니다. 웹 갤러리에 필요한 사진은 `docs/photos/`에 복사되므로 `docs/`만 push하면 됩니다.

## 라이선스

MIT License