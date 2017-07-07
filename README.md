# Video bounding boxes creator
Simple Qt5 app for tagging bounding boxes in video frames to create dataset for object detection

## Usage
pip install -r requirements.txt

python video_tagger.py

Output file is json of type:

[ [frame_number, [ [[top_left_x, top_left_y], [bottom_right_x, bottom_right_y]], ...]], ...]
