FROM python

WORKDIR /project23362

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0"]