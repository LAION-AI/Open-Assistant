FROM postgres:15

# install unzip
RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/*

# download aws cli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip -q awscliv2.zip
RUN ./aws/install

COPY ./backup_pg_to_s3.sh .
