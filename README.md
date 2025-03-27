# 🚀 CLOUD-BASED NEWS ARTICLE PROCESSING SYSTEM
A multi-cloud solution leveraging AWS AI services and Azure Cognitive Services for end-to-end news processing.

### 🔍 Extract text → 📄 Summarize → 💬 Analyze Sentiment → 🎙 Convert to Speech → ☁ Store in Cloud


## 🎯 How It Works
1️⃣ Upload an Image – The image is stored in AWS S3<br>
2️⃣ Text Extraction – AWS Textract extracts the text<br>
3️⃣ Summarization – AWS Bedrock generates a summary<br>
4️⃣ Sentiment Analysis – Azure Text Analytics analyzes sentiment<br>
5️⃣ Text-to-Speech – AWS Polly converts summary along with the sentiment into an MP3<br>
6️⃣ Cloud Storage – The MP3 file is stored in Azure Blob Storage<br>
🚀 Listen to the AI-generated audio summary!


## ☁️ Cloud Services
| AWS Services | Azure Services  |
|--------------|-----------------|
| S3 Storage   | Blob Storage    |
| Textract     | Text Analytics  |
| Polly        |                 |
| Bedrock      |                 |


## 🛠 Installation & Setup

### 🔹 Prerequisites
- AWS Account with required services enabled
- Azure Account with Cognitive Services
- Python 3.9+ environment

### 🔹 1. Clone the Repository
git clone https://github.com/<your-username>/<your-repository-name>.git<br>
cd <your-repository-name>

### 🔹 2. Install Dependencies
pip install -r requirements.txt

### 🔹 3. Set Up Environment Variables
### Add your AWS and Azure credentials:
AWS_ACCESS_KEY=your_aws_access_key<br>
AWS_SECRET_KEY=your_aws_secret_key<br>
AWS_REGION=your_aws_region<br>
S3_BUCKET_NAME=your_s3_bucket_name<br>

AZURE_TEXT_ANALYTICS_KEY=your_azure_key<br>
AZURE_TEXT_ANALYTICS_ENDPOINT=your_azure_endpoint<br>
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string<br>
AZURE_CONTAINER_NAME=your_azure_container_name<br>

### 🔹 4. Run the Application
python app.py

------------

Developed with ❤️ using AWS & Azure services...
