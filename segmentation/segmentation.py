import time
import cv2
import matplotlib.pyplot as plt
import importlib
import os

import dicomHandler
import wspMultithreshold
import plotGraph

def main(image_folder, algorithm, dimension, q):
    input_dir = image_folder
    current_date =  time.strftime("%Y-%m-%d-%H-%M-%S")
    output_dir = input_dir + f"-{current_date}-{algorithm}-d{dimension}-q{q}"
    os.mkdir(output_dir)

    for file in os.listdir(image_folder):
        dcm_path = image_folder + '/' + file

        dicom_image, pixel_array = dicomHandler.read_dicom_image(dcm_path)

        hu_image = dicomHandler.transform_to_hu(dicom_image, pixel_array)

        hist, bin_edges, best_thresholds, img_thres = wspMultithreshold.wspMultithreshold(hu_image, algorithm, dimension, q)

        high_intensity = wspMultithreshold.get_high_intensity_pixels(img_thres)

        pixel_array = dicomHandler.transform_to_pixel_array(dicom_image, high_intensity)

        #hard_tissue = wspMultithreshold.get_largest_region(pixel_array)

        dicomHandler.save_dicom(dicom_image, pixel_array,f'{output_dir}/{file}')


if __name__ == '__main__':
    image = "../../Database/2EFVJVCN"
    algorithm = 'FFA'
    dimension = 2
    q = 1

    main(image, algorithm, dimension, q)