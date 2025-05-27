ARG BUILD_FROM
FROM $BUILD_FROM

# Install required packages
RUN apk add --no-cache python3 py3-pip

# Install Python dependencies
RUN pip3 install --no-cache-dir flask pyyaml requests

# Copy data
COPY run.sh app.py /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]