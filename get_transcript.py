from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript('e9j2iEwJru0')
for entry in transcript:
    print(f"{entry['start']:.0f}s: {entry['text']}")
