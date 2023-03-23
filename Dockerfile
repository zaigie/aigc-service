FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Shanghai

RUN mkdir /app
WORKDIR /app

# RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
RUN apt update && apt install make gcc g++ tzdata -y
# RUN python -m pip install --upgrade pip -i https://pypi.douban.com/simple
RUN python -m pip install --upgrade pip

COPY requirements.txt /app
RUN cd /app && pip install -r requirements.txt
RUN apt remove make gcc g++ -y

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN rm -rf /var/cache/apt/*
RUN rm -rf /root/.cache/
RUN find /usr/local/lib/python3.10/* -name *.pyc | xargs rm -rf -

COPY . /app

ENTRYPOINT ["bash", "start.sh"]

EXPOSE 8000
EXPOSE 9000
