import os
import logging
import argparse


import numpy as np
from dotenv import load_dotenv
from PIL import Image
from moviepy import ImageClip, concatenate_videoclips


logging.basicConfig(
	level = logging.DEBUG,
	format = '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog='panorama_image_to_video',
		description='Creates a video from a panorama image'
	)
	parser.add_argument('input_image_filename')
	parser.add_argument('output_video_filename')
	parser.add_argument('-r', '--frame-rate', action='store', dest='frame_rate', type=int, default=30)
	parser.add_argument('-d', '--duration', action='store', dest='duration', type=int, default=10)
	command_line_arguments = parser.parse_args()
	logger.debug(f'input image filename: {command_line_arguments.input_image_filename}')
	logger.debug(f'output video filename: {command_line_arguments.output_video_filename}')

	load_dotenv()

	input_image = Image.open(command_line_arguments.input_image_filename)
	logger.debug(f'input image metadata: format: {input_image.format}, size: {input_image.size} px, mode: {input_image.mode}')
	image_chunk_size = input_image.height
	logger.debug(f'input image chunk size: {image_chunk_size} px; frame rate: {command_line_arguments.frame_rate} fps; duration: {command_line_arguments.duration} s')
	remaining_width = input_image.width - image_chunk_size
	if remaining_width > 0:
		# pan_per_frame = int(round((remaining_width / float(command_line_arguments.frame_rate)) / command_line_arguments.duration, 0))
		pan_per_frame = (remaining_width / float(command_line_arguments.frame_rate)) / command_line_arguments.duration
		logger.debug(f'pan per frame: {pan_per_frame} px')

		total_frame_count = int(round(remaining_width / pan_per_frame, 0))
		logger.debug(f'total frame count: {total_frame_count} frames')
		individual_frames = []
		for index in range(0, total_frame_count):
			pan = index * pan_per_frame
			frame = input_image.crop((pan, 0, input_image.height + pan, input_image.height))
			# logger.debug(f'frame dimensions: {frame.size} px; pan: {pan} px')
			individual_frames.append(frame)

		frame_duration = 1.0 / command_line_arguments.frame_rate
		individual_frames = [ ImageClip(np.array(frame), duration=frame_duration) for frame in individual_frames ]
		logger.debug(f'number of individual frames: {len(individual_frames)} frames; expected length: {len(individual_frames) / command_line_arguments.frame_rate} s')

		output_video = concatenate_videoclips(individual_frames)
		output_video.write_videofile(command_line_arguments.output_video_filename, fps=command_line_arguments.frame_rate, codec='mpeg4')
	else:
		raise Exception('This tool only supports landscape images having a greater width than height')
