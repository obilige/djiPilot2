# pilot2 develop project
- dji pilot2 sample을 python, nginx, redis 등을 이용해 리팩토링한 개인 작업물입니다.
- Drone + Smart Agriculture Team 드론 솔루션입니다.

### 1. Pilot2?
- DJI에서 개발한 드론 컨트롤러 시스템
- Mavic3, RTK300 등의 기종 구매 시, 컨트롤러에 탑재
- pilot2 프로그램을 이용해 DJI에서 제공하는 기능을 자사 솔루션에 붙일 수 있음

###  2. Outline
- 관제시스템 개발
- 여러 대의 드론을 하나의 시스템에서 통제, 관찰할 수 있도록 만들 예정
- 디렉토리: 
    1. backend(python, 개발)
    2. frontend(vue, 샘플)
    3. oss(minio, docker hub)
    4. livestreaming(ome, docker hub)
    5. database(postgreSQL, docker hub)
    6. redis(redis, docker hub)
    7. reverseProxy(nginx, docker hub)
- 구성:
    ```text
    Drone --------------+-------------> pilot2 with js-bridge+
    pilot2 cloud <-------------------------------------------|  
    |                   |                                    |
    nginx:8756 ---------+-----> frontend:8080 ---------------+
                        |       http:// & ws://              | ws://
                        |-----> backend:6789                 | E 8
                        |                                    | M 0
                        +-----> postgres:5432                | Q 8
                        +-----> minio:9000                   | X 3
                        +-----> ome:1935, 3333, 3478         | :
                        +-----> redis:5432                   |
    --------------------|------------------------------------+
    ```

### 3. SKill 기대효과
- python으로 backend service 개발
- websocket, mqtt, oss 이용한 cloud + 장비 통신
- livestreaming MQTT - WebRTC 구현
- nginx로 reverseProxy 구현
- PostgreSQL로 json 기반 DB 구현 및 활용
- redis로 in-memory DB 사용해보기
- docker로 컨테이너 구현 -> k8s로 오케스트레이션 사용해보기

### 4. Function
- pilot2 login: 클라우드 통한 관제 웹페이지 - 컨트롤러 연동
- livestreaming: 드론에서 촬영한 영상 실시간 라이브스트리밍
- wayline file: 경로파일 업로드/다운로드, 클라우드로 내려받은 경로파일로 드론 날아가게 만들기
- situation awareness: 두 대 이상의 드론이 지정된 경로에 있는 경우 서로 정보 공유

### 5. 추후계획
- k8s: 쿠버네티스로 도커 컨테이너 관리해보기(case study for learning k8s)
- deep learning: oss에 저장된 사진들 deep-learning 훈련에 사용해보기