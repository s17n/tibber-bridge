FROM python:3

WORKDIR /Users/steffen/Projects/tibber-bridge

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./tibber-bridge.py" ]