FROM python:3.9

# workdir 경로 지정
WORKDIR /code

# 라이브러리, 모듈 설치 목록
COPY ./requirements.txt /code/requirements.txt

# requirements.txt에 적힌 라이브러리, 모듈 설치
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 이하 모든 소스코드 가져오기
COPY ./app /code/app

# 포트 노출
EXPOSE 6789

# FastAPI 실행 명령어. --reload: 코드 변경 시 서버 재시작, port는 6789
CMD ["uvicorn", "app.main:app", "--reload", "--proxy-headers", "--host", "0.0.0.0", "--port", "6789"]