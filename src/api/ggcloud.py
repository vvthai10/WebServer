from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.api_core.client_options import ClientOptions

def transcribe_chirpRecognizer_LongAudio(project_id, gcs_uri) -> cloud_speech.BatchRecognizeResponse:
    """Transcribe an audio file using Chirp."""
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint="asia-southeast1-speech.googleapis.com",
        )
    )

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["vi-VN"],
        model="chirp",
    )

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)
    
    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{project_id}/locations/asia-southeast1/recognizers/chirp-recognizer",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )

    # Transcribes the audio into text
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=120)

    # Shown Transcript text on Terminal 
    # for result in response.results[gcs_uri].transcript.results:
    #     print(f"Transcript: {result.alternatives[0].transcript}")
    # return response.results[gcs_uri].transcript
    transcript_text = ""
    for result in response.results[gcs_uri].transcript.results:
        transcript_text += result.alternatives[0].transcript + " "

    return transcript_text.strip()