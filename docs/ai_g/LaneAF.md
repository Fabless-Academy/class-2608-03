

---

## CULane dataset

**CULane**은 자율주행 차선 감지(Lane Detection) 연구에서 가장 널리 쓰이는 대규모 벤치마크 데이터셋입니다. 홍콩중문대학교(CUHK) 연구진이 CVPR 2018 논문(SCNN)을 통해 공개했으며, 복잡한 도심 및 고속도로 환경의 실전 데이터를 담고 있습니다.

[Spatial As Deep: Spatial CNN for Traffic Scene Understanding](https://arxiv.org/pdf/1712.06080)

**주요 특징**

* **대규모 데이터**: 베이징 도심을 주행하는 차량의 블랙캠으로 수집된 총 **133,247개 프레임** (Train 88,880 / Val 9,675 / Test 34,692)으로 구성됩니다.
* **픽셀 단위 수동 라벨링**: 각 차선이 점(Point) 목록 형태의 폴리라인(Polyline) 구조로 정밀하게 주석 처리되어 있습니다.
* **9가지 다채로운 시나리오**: 단순 맑은 날씨 외에 모델 한계를 시험하는 난이도 높은 9개 카테고리로 시험 데이터를 분류합니다.

| 시나리오 구분 | 설명 |
| --- | --- |
| **Normal** | 맑고 혼잡하지 않은 일반 도로 |
| **Crowded** | 교통량이 많아 차량에 의해 차선이 가려진 상태 |
| **Night** | 야간 저조도 환경 |
| **No Line** | 차선 마모 또는 도로 공사 등으로 차선 구분이 모호한 경우 |
| **Shadow** | 건물, 가로수 등에 의한 짙은 그림자 |
| **Arrow / Dazzle** | 노면 화살표 표시 interference / 역광 및 눈부심 |
| **Curve / Crossroad** | 급커브 구간 / 차선이 끊기는 교차로 영역 |

---

**평가 방식 (Evaluation Metric)**

모델 예측 차선을 일정 두께(16픽셀)로 확장한 라인 영역과 정답(Ground Truth) 라인 간의 IoU(Intersection over Union)를 계산합니다.

* IoU가 **0.5 이상**일 때 올바르게 감지한 것으로 판단(True Positive)합니다.
* 최종 성능은 정밀도(Precision)와 재현율(Recall)을 종합한 **$F_1$-score** 조화평균 수치로 평가합니다.