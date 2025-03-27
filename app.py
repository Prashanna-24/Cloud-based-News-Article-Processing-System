from flask import Flask, request, render_template, send_from_directory
import boto3
from azure.storage.blob import BlobServiceClient
import os
import json
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

app = Flask(__name__)

# AWS Configuration
AWS_ACCESS_KEY = 'PLACEHOLDER'
AWS_SECRET_KEY = 'PLACEHOLDER'
AWS_REGION = "PLACEHOLDER"
S3_BUCKET_NAME = "PLACEHOLDER"

# Azure Configuration
AZURE_TEXT_ANALYTICS_KEY = "PLACEHOLDER"
AZURE_TEXT_ANALYTICS_ENDPOINT = "PLACEHOLDER"
AZURE_STORAGE_CONNECTION_STRING = "PLACEHOLDER"
AZURE_CONTAINER_NAME = "PLACEHOLDER"

# Initialize AWS clients
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

textract = boto3.client(
    'textract',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

polly = boto3.client(
    'polly',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

bedrock = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# Initialize Azure clients
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
text_analytics_client = TextAnalyticsClient(
    endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT,
    credential=AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY)
)

def analyze_sentiment(text):
    # Authenticate client
    credential = AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY)
    client = TextAnalyticsClient(
        endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT, 
        credential=credential
    )
    
    # Analyze sentiment
    response = client.analyze_sentiment(
        documents=[text],
        show_opinion_mining=True
    )
    
    # Process results
    if response and not response[0].is_error:
        return {
            'sentiment': response[0].sentiment,
            'confidence': {
                'positive': response[0].confidence_scores.positive,
                'neutral': response[0].confidence_scores.neutral,
                'negative': response[0].confidence_scores.negative
            }
        }
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['image']
        if file:
            filename = file.filename
            file_path = os.path.join("uploads", filename)
            
            # Save file locally
            os.makedirs("uploads", exist_ok=True)
            file.save(file_path)

            # Upload to S3
            s3.upload_file(file_path, S3_BUCKET_NAME, filename)
            print(f"File '{filename}' uploaded to S3 bucket '{S3_BUCKET_NAME}'.")

            # Extract text with Textract
            response = textract.detect_document_text(
                Document={'S3Object': {'Bucket': S3_BUCKET_NAME, 'Name': filename}}
            )
            extracted_text = " ".join([item["Text"] for item in response["Blocks"] if item["BlockType"] == "LINE"])
            print(f"Text extracted from '{filename}': {extracted_text}")

            # Generate summary with Bedrock
            try:
                cohere_prompt = f"Summarize this news article: {extracted_text}"
                
                summary_response = bedrock.invoke_model(
                    modelId="cohere.command-text-v14",
                    body=json.dumps({
                        "prompt": cohere_prompt,
                        "max_tokens": 400,
                        "temperature": 0.5
                    })
                )
                response_body = json.loads(summary_response["body"].read().decode())
                
                if "message" in response_body and "blocked" in response_body["message"]:
                    summary = "Summary blocked by content filters"
                else:
                    summary = response_body["generations"][0]["text"]
                
                print(f"Cohere summary generated: {summary}")

            except Exception as e:
                print(f"Cohere error: {str(e)}")
                summary = "Summary generation failed"


            # Analyze sentiment with Azure Text Analytics
            try:
                sentiment_result = analyze_sentiment(summary)
                if sentiment_result:
                    # Get confidence scores and find maximum
                    confidences = sentiment_result['confidence']
                    max_key = max(confidences, key=lambda k: confidences[k])
                    max_value = confidences[max_key]
                    
                    # Build tone description
                    tone = f"This news has a {sentiment_result['sentiment']} tone. "
                    tone += f"Highest confidence is {max_key} at {max_value:.0%}. "
                    summary_with_tone = tone + "Here's the summary: " + summary
                else:
                    summary_with_tone = summary
            except Exception as e:
                print(f"Sentiment analysis error: {e}")
                summary_with_tone = summary

            # Polly
            polly_response = polly.synthesize_speech(
                Text=summary_with_tone,  # Updated text with sentiment
                OutputFormat='mp3',
                VoiceId='Joanna'
            )

            # Save and upload audio
            os.makedirs("output", exist_ok=True)
            audio_file_path = f"output/{filename}.mp3"
            with open(audio_file_path, "wb") as audio_file:
                audio_file.write(polly_response['AudioStream'].read())
            print(f"Audio file saved to '{audio_file_path}'.")

            # Upload to Azure Blob
            blob_client = blob_service_client.get_blob_client(
                container=AZURE_CONTAINER_NAME, 
                blob=f"{filename}.mp3"
            )
            with open(audio_file_path, "rb") as audio_file:
                blob_client.upload_blob(audio_file, overwrite=True)

            audio_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{filename}.mp3"
            print(f"Audio file '{filename}.mp3' uploaded to Azure Blob Storage.")

            return render_template(
                "index.html",
                text=summary,
                audio_url=audio_url,
                sentiment=sentiment_result
            )

    return render_template("index.html")

@app.route("/output/<filename>")
def serve_audio(filename):
    return send_from_directory("output", filename)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    app.run(debug=True, port=8080)