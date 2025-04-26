import cv2

#read video just to be sure that the video is read correctly nothing important here
def read_video(video_path):
    cap = cv2.VideoCapture(video_path) #read video
    frames = [] #store frames
    while True:
        ret, frame = cap.read() #read frame
        if not ret:
            break #if no frame, break
        frames.append(frame) #store frame
    return frames #return frames   


# save video function to be sure that the video is saved correctly  nothing important here
def save_video(ouput_video_frames,output_video_path):
    fourcc = cv2.VideoWriter.fourcc(*'XVID') #codec
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0])) # 0 is the frame rate, 1 is the size of the frame
    for frame in ouput_video_frames: # so we loop through the frames and write them to the video
        out.write(frame)
    out.release()