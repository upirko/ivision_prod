import json

STREAMS = []

with open('streams_info.json', 'r') as stream_data:
    STREAMS = json.load(stream_data)    
