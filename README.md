2020 국민대학교 멋쟁이 사자처럼 교내 해커톤 프로젝트
[사자네 문방구]
-------------

### 프로젝트 시작 방법
1. GitHub Repository로부터 해당 프로젝트를 Clone한다.
   * 터미널을 연다.
   * 해당 프로젝트를 Clone할 위치로 이동한다.
   * *git clone https://github.com/pcjs156/LionStore.git* 명령어로 프로젝트를 Clone한다.
   
   
2. 터미널을 이용해 프로젝트를 Clone한 디렉토리로 이동한다. (windows의 경우 명령 프롬프트)
   * ex) *cd ~/workspace/LikeLion/LionStore*
   * *dir* 또는 *ls* 명령어로 확인했을 때 디렉토리/파일 목록에 manage.py가 있으면 됨


3. **venv**라는 이름의 가상환경을 생성한다(.gitignore 참조)
   * Windows : *python -m venv venv*
   * macOS / Linux : *python3 -m venv venv*


4. 가상환경을 activate한다
   * Windows : *venv\Scripts\activate.bat*
   * macOS / Linux : *source venv/bin/activate*

5. 필요한 패키지를 설치한다.
   * Windows : *pip install -r requirements*
   * macOS / Linux : *pip3 install -r requirements*
   
* * *

### 프로젝트 기여 방법
0. 작업하기 전 항상 GitHub Repository로부터 pull을 해옵니다.
   * *git pull origin master*

1. 기본적으로 각자 이름으로 된 branch를 생성하고, 필요할 경우 해당 branch에서 추가적으로 branch를 생성합니다.
   * branch 생성 : *git branch (branch 이름)*
   * branch 전환 : *git checkout (branch 브랜치 이름)*

2. 각자의 branch에서 작업이 끝나면, 따로 pull request를 하지 않고 master branch에 merge → push 합니다.
   1. master branch로 전환 : *git checkout master*
   2. 작업한 branch를 병합 : *git merge (병합할 branch 이름)*
   3. GitHub에 push : *git push*
   
3. 복구와 추적이 용이하도록 있으면 커밋을 작업 단위로 해주세요! (ex. 문구류 모델 생성)

4. 커밋 메시지는 작업 내역을 알 수 있게 정확히 적어주세요!

* * *
### 프로젝트 기여자
* youngjin2639
* se0983
* pcjs156
* yeahjin
* hyeonss33
