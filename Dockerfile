FROM odoo:17

# Cài đặt các dependencies hệ thống cho OCR
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-vie \
        libtesseract-dev \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python cho AI Integration
RUN pip3 install --no-cache-dir \
    openai>=1.0.0 \
    google-generativeai>=0.3.0 \
    requests>=2.31.0 \
    pytesseract>=0.3.10 \
    Pillow>=10.0.0

USER odoo

