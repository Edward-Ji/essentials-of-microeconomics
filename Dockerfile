FROM python:3.9

WORKDIR /code

COPY ./essentials_of_microeconomics/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./essentials_of_microeconomics .

EXPOSE 7860

CMD ["shiny", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]
